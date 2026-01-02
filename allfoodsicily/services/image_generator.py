"""Nano Banana Pro (Gemini 3 Pro Image) integration for image generation."""

import base64
import logging
from typing import Optional
from io import BytesIO
from PIL import Image

from google import genai
from google.genai import types
from config.settings import settings
from utils.retry import retry_api_call

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Nano Banana Pro image generator."""
    
    def __init__(self):
        """Initialize Gemini client for image generation."""
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_IMAGE_MODEL
        logger.info(f"Initialized image generator with model: {self.model}")
    
    @retry_api_call(max_attempts=3)
    def generate_image(
        self,
        prompt: str,
        aspect_ratio: Optional[str] = None,
        image_size: Optional[str] = None
    ) -> tuple[bytes, str]:
        """Generate image from text prompt.
        
        Args:
            prompt: Text prompt for image generation
            aspect_ratio: Aspect ratio (default from settings)
            image_size: Image size (default from settings)
            
        Returns:
            Tuple of (image_bytes, mime_type)
        """
        logger.info("Generating image with Nano Banana Pro")
        logger.debug(f"Prompt: {prompt[:100]}...")
        
        aspect_ratio = aspect_ratio or settings.IMAGE_ASPECT_RATIO
        image_size = image_size or settings.IMAGE_SIZE
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE'],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=image_size
                    )
                )
            )
            
            # Extract image from response
            for part in response.parts:
                if part.inline_data:
                    # Get image data
                    image_data = part.inline_data.data
                    mime_type = part.inline_data.mime_type
                    
                    # Convert to bytes if needed
                    if isinstance(image_data, str):
                        # Base64 encoded
                        image_bytes = base64.b64decode(image_data)
                    else:
                        image_bytes = image_data
                    
                    logger.info(f"Generated image: {len(image_bytes)} bytes, {mime_type}")
                    return image_bytes, mime_type
            
            raise ValueError("No image data found in response")
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise
    
    def generate_image_base64(
        self,
        prompt: str,
        aspect_ratio: Optional[str] = None,
        image_size: Optional[str] = None
    ) -> tuple[str, str]:
        """Generate image and return as base64 string.
        
        Args:
            prompt: Text prompt for image generation
            aspect_ratio: Aspect ratio (default from settings)
            image_size: Image size (default from settings)
            
        Returns:
            Tuple of (base64_string, mime_type)
        """
        image_bytes, mime_type = self.generate_image(prompt, aspect_ratio, image_size)
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        return base64_string, mime_type
    
    def save_image(
        self,
        image_bytes: bytes,
        filepath: str,
        mime_type: str = "image/png"
    ) -> None:
        """Save image bytes to file.
        
        Args:
            image_bytes: Image data as bytes
            filepath: Path to save image
            mime_type: MIME type of image
        """
        try:
            # Determine format from mime type
            if "jpeg" in mime_type or "jpg" in mime_type:
                format = "JPEG"
            elif "png" in mime_type:
                format = "PNG"
            else:
                format = "PNG"  # Default
            
            # Open image and save
            image = Image.open(BytesIO(image_bytes))
            image.save(filepath, format=format)
            logger.info(f"Saved image to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            raise

