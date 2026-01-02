# Configurazione Modelli Gemini

## Dove sono configurati

I modelli Gemini sono configurati in **`config/settings.py`** alle righe 40-45:

```python
# Gemini models
GEMINI_TEXT_MODEL: str = "gemini-2.5-flash"
GEMINI_IMAGE_MODEL: str = "gemini-3-pro-image-preview"
```

## Modelli Attuali

### 1. Modello Testo (`GEMINI_TEXT_MODEL`)
- **Attuale**: `gemini-2.5-flash`
- **Usato per**: 
  - Analisi contenuti e selezione topic
  - Generazione articoli (500-800 parole)
  - Generazione prompt per immagini

**Modelli disponibili:**
- `gemini-2.5-flash` ⚡ (veloce, economico) - **ATTUALE**
- `gemini-2.5-pro` 🧠 (più potente, più costoso)
- `gemini-2.0-flash` (versione precedente)

### 2. Modello Immagini (`GEMINI_IMAGE_MODEL`)
- **Attuale**: `gemini-3-pro-image-preview` (Nano Banana Pro)
- **Usato per**: Generazione immagini 2K per articoli

**Modelli disponibili:**
- `gemini-3-pro-image-preview` 🎨 (Nano Banana Pro - alta qualità, 4K) - **ATTUALE**
- `gemini-2.5-flash-image` ⚡ (più veloce, risoluzione minore)

## Come Modificare i Modelli

### Opzione 1: Modifica diretta in `config/settings.py`

```python
# Per testi più potenti
GEMINI_TEXT_MODEL: str = "gemini-2.5-pro"

# Per immagini più veloci (ma qualità minore)
GEMINI_IMAGE_MODEL: str = "gemini-2.5-flash-image"
```

### Opzione 2: Variabili ambiente nel `.env`

Aggiungi al file `.env`:

```env
GEMINI_TEXT_MODEL=gemini-2.5-pro
GEMINI_IMAGE_MODEL=gemini-2.5-flash-image
```

## Confronto Modelli

### Testi

| Modello | Velocità | Qualità | Costo | Uso Consigliato |
|---------|----------|---------|-------|-----------------|
| `gemini-2.5-flash` | ⚡⚡⚡ | ⭐⭐⭐ | 💰 | Analisi e articoli standard |
| `gemini-2.5-pro` | ⚡⚡ | ⭐⭐⭐⭐ | 💰💰 | Articoli complessi, analisi approfondite |

### Immagini

| Modello | Velocità | Qualità | Risoluzione | Costo |
|---------|----------|---------|-------------|-------|
| `gemini-3-pro-image-preview` | ⚡⚡ | ⭐⭐⭐⭐⭐ | Fino a 4K | 💰💰 |
| `gemini-2.5-flash-image` | ⚡⚡⚡ | ⭐⭐⭐ | 1K | 💰 |

## Impostazioni Immagini

Anche le impostazioni delle immagini sono configurabili in `config/settings.py`:

```python
IMAGE_ASPECT_RATIO: str = "16:9"  # Formato: 1:1, 16:9, 4:3, etc.
IMAGE_SIZE: str = "2K"            # Risoluzione: 1K, 2K, 4K (solo per gemini-3-pro-image-preview)
```

## Dove vengono usati

- **`services/gemini_client.py`**: Usa `GEMINI_TEXT_MODEL` per analisi e generazione testi
- **`services/image_generator.py`**: Usa `GEMINI_IMAGE_MODEL` per generazione immagini

## Raccomandazioni

- **Per produzione**: Mantieni `gemini-2.5-flash` per testi (veloce ed economico)
- **Per qualità massima**: Usa `gemini-2.5-pro` per testi e `gemini-3-pro-image-preview` per immagini
- **Per risparmiare**: Usa `gemini-2.5-flash-image` per immagini (ma qualità inferiore)

