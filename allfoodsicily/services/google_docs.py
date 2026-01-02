"""Google Docs API integration for saving articles."""

import os
import logging
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from io import BytesIO

from config.settings import settings
from models.schemas import Article, GoogleDocInfo
from utils.retry import retry_api_call

logger = logging.getLogger(__name__)

# Scopes required for Google Docs and Drive
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]


class GoogleDocsService:
    """Google Docs and Drive service."""
    
    def __init__(self):
        """Initialize Google Docs service with OAuth2."""
        self.creds = self._get_credentials()
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        logger.info("Initialized Google Docs service")
    
    def _get_credentials(self) -> Credentials:
        """Get credentials - prefer Service Account, fallback to OAuth2.
        
        Returns:
            Valid credentials
        """
        # Try Service Account first (preferito per automazioni)
        service_account_path = Path(settings.GOOGLE_SERVICE_ACCOUNT_FILE)
        if service_account_path.exists():
            logger.info(f"Using Service Account: {service_account_path}")
            try:
                creds = service_account.Credentials.from_service_account_file(
                    str(service_account_path),
                    scopes=SCOPES
                )
                logger.info("Service Account credentials loaded successfully")
                return creds
            except Exception as e:
                logger.error(f"Error loading Service Account: {str(e)}")
                raise
        
        # Fallback to OAuth2
        logger.info("Service Account not found, using OAuth2")
        creds = None
        token_path = Path(settings.GOOGLE_TOKEN_FILE)
        credentials_path = Path(settings.GOOGLE_CREDENTIALS_FILE)
        
        # Load existing token
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                if not credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {credentials_path}\n"
                        "Please download from Google Cloud Console and save as credentials.json\n"
                        "OR use Service Account by saving service_account.json"
                    )
                
                logger.info("Requesting new credentials")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    @retry_api_call(max_attempts=3)
    def create_document(
        self,
        article: Article,
        image_base64: Optional[str] = None,
        image_mime_type: Optional[str] = None
    ) -> GoogleDocInfo:
        """Create a Google Doc with article content.
        
        Args:
            article: Article to save
            image_base64: Base64 encoded image (optional)
            image_mime_type: MIME type of image (optional)
            
        Returns:
            GoogleDocInfo with document details
        """
        logger.info(f"Creating Google Doc for article: {article.title}")
        
        # Generate document title
        date_str = datetime.now().strftime("%Y-%m-%d")
        doc_title = f"{date_str} - {article.title}"
        
        try:
            # Create empty document
            doc = self.docs_service.documents().create(
                body={'title': doc_title}
            ).execute()
            
            doc_id = doc.get('documentId')
            logger.info(f"Created document with ID: {doc_id}")
            
            # Prepare content
            requests = []
            
            # Add title (already in document title, but add as heading)
            requests.append({
                'insertText': {
                    'location': {'index': 1},
                    'text': article.title + '\n'
                }
            })
            
            # Format title as heading
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': len(article.title) + 1
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_1'
                    },
                    'fields': 'namedStyleType'
                }
            })
            
            # Convert markdown to plain text (simplified)
            # In production, use a proper markdown parser
            content_text = self._markdown_to_text(article.content)
            
            # Add article content
            current_index = len(article.title) + 2
            requests.append({
                'insertText': {
                    'location': {'index': current_index},
                    'text': content_text + '\n\n'
                }
            })
            
            # Add image if provided
            if image_base64:
                # Upload image to Drive first
                image_file_id = self._upload_image_to_drive(
                    image_base64,
                    image_mime_type or "image/png",
                    f"{article.title}_image"
                )
                
                if image_file_id:
                    # Insert image into document
                    image_index = current_index + len(content_text) + 2
                    requests.append({
                        'insertInlineImage': {
                            'location': {'index': image_index},
                            'uri': f'https://drive.google.com/uc?id={image_file_id}'
                        }
                    })
            
            # Add sources section
            sources_text = "\n\n---\n\n**Fonti:**\n"
            for source_url in article.topic.fonti:
                sources_text += f"- {source_url}\n"
            
            final_index = current_index + len(content_text) + 2
            if image_base64:
                final_index += 1  # Account for image
            
            requests.append({
                'insertText': {
                    'location': {'index': final_index},
                    'text': sources_text
                }
            })
            
            # Execute batch update
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            # Move to folder
            folder_id = self._get_or_create_folder()
            if folder_id:
                self._move_to_folder(doc_id, folder_id)
            
            # Get document URL
            doc_url = f"https://docs.google.com/document/d/{doc_id}"
            
            logger.info(f"Document created successfully: {doc_url}")
            
            return GoogleDocInfo(
                doc_id=doc_id,
                doc_url=doc_url,
                title=doc_title
            )
            
        except HttpError as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    def _markdown_to_text(self, markdown: str) -> str:
        """Convert markdown to plain text (simplified).
        
        Args:
            markdown: Markdown content
            
        Returns:
            Plain text content
        """
        # Simple markdown to text conversion
        # Remove markdown headers
        lines = markdown.split('\n')
        text_lines = []
        
        for line in lines:
            # Remove markdown headers
            line = line.lstrip('#').strip()
            # Remove markdown bold/italic
            line = line.replace('**', '').replace('*', '')
            # Remove markdown links (keep text)
            if '[' in line and '](' in line:
                # Simple link extraction
                import re
                line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
            
            text_lines.append(line)
        
        return '\n'.join(text_lines)
    
    def _upload_image_to_drive(
        self,
        image_base64: str,
        mime_type: str,
        filename: str
    ) -> Optional[str]:
        """Upload image to Google Drive.
        
        Args:
            image_base64: Base64 encoded image
            mime_type: MIME type
            filename: Filename for image
            
        Returns:
            File ID or None if error
        """
        try:
            import base64
            image_bytes = base64.b64decode(image_base64)
            
            file_metadata = {
                'name': filename,
                'mimeType': mime_type
            }
            
            media = MediaIoBaseUpload(
                BytesIO(image_bytes),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"Uploaded image to Drive: {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            return None
    
    def _get_or_create_folder(self) -> Optional[str]:
        """Get or create the monthly folder for drafts.
        
        Returns:
            Folder ID or None if error
        """
        try:
            month_name = datetime.now().strftime("%B")  # Full month name
            folder_name = f"AllFoodSicily/Bozze/{month_name}"
            
            # Check if folder exists
            query = f"name='{month_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            if folders:
                return folders[0]['id']
            
            # Create folder if not exists
            # First, get or create parent folder
            parent_folder_id = self._get_or_create_parent_folder()
            
            file_metadata = {
                'name': month_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id] if parent_folder_id else []
            }
            
            folder = self.drive_service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            logger.info(f"Created folder: {month_name}")
            return folder.get('id')
            
        except Exception as e:
            logger.error(f"Error getting/creating folder: {str(e)}")
            return None
    
    def _get_or_create_parent_folder(self) -> Optional[str]:
        """Get or create parent folder structure.
        
        Returns:
            Parent folder ID or None
        """
        # For simplicity, use the configured folder ID if available
        if settings.GOOGLE_DOCS_FOLDER_ID:
            return settings.GOOGLE_DOCS_FOLDER_ID
        
        # Otherwise, create in root (simplified)
        return None
    
    def _move_to_folder(self, file_id: str, folder_id: str) -> None:
        """Move file to folder.
        
        Args:
            file_id: File ID to move
            folder_id: Destination folder ID
        """
        try:
            # Get current parents
            file = self.drive_service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()
            
            previous_parents = ",".join(file.get('parents', []))
            
            # Move file
            self.drive_service.files().update(
                fileId=file_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            logger.info(f"Moved file {file_id} to folder {folder_id}")
            
        except Exception as e:
            logger.warning(f"Error moving file to folder: {str(e)}")

