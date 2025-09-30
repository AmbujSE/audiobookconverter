# Audiobook Converter

A Python script to convert M4B audiobook files to high-quality MP3 format while preserving metadata and chapter information.

## Features

- Converts M4B audiobook files to MP3 format
- Preserves original metadata (title, artist, album, etc.)
- Maintains chapter information from the source file
- **Automatic album artwork embedding** from external image files or M4B metadata
- Supports CUE file parsing for additional chapter data
- High-quality audio output (VBR ~190 kbps)
- Batch processing of multiple files

## Prerequisites

- Python 3.x
- FFmpeg installed and available in PATH

### Installing FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install -y ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

**macOS:**
```bash
brew install ffmpeg
```

## Usage

1. Update the `input_folder` path in the script to point to your M4B files
2. Run the converter:

```bash
python convert_audiobooks.py
```

The script will:
- Find all `.m4b` files in the specified folder
- Automatically detect and embed album artwork (see Artwork section below)
- Create a `converted_mp3` subfolder for output
- Convert each file while preserving metadata and chapters
- Display conversion progress and results

## Configuration

Edit the `input_folder` variable in `convert_audiobooks.py`:

```python
# For Windows (when running in WSL)
input_folder = "/mnt/d/Media/Convert"

# For Linux/macOS
input_folder = "/path/to/your/audiobooks"

# For Windows (native)
input_folder = r"D:\Media\Convert"
```

## Album Artwork

The converter automatically handles album artwork in multiple ways:

### External Image Files
Place an image file with the same name as your M4B file:
```
MyBook.m4b
MyBook.jpg     ← Will be embedded as album art
```

### Supported Image Formats
- `.jpg` / `.jpeg`
- `.png` 
- `.bmp`
- `.gif`
- `.tiff`
- `.webp`

### Common Cover Art Names
If no matching image is found, the script looks for common cover art filenames:
- `cover.jpg`
- `folder.jpg` 
- `albumart.jpg`
- `front.jpg`
- `artwork.jpg`

### Embedded Artwork
If your M4B file already contains embedded artwork, it will be preserved in the MP3 output.

## Example Output

```
Found 1 .m4b file(s)
Output folder: /path/to/output/converted_mp3

Processing: The Man Who Mistook His Wife for a Hat.m4b
Found CUE file: The Man Who Mistook His Wife for a Hat.cue
Found external artwork: The Man Who Mistook His Wife for a Hat.jpg
Adding external artwork: The Man Who Mistook His Wife for a Hat.jpg
Found 29 chapters in m4b file
Converting...
✓ Successfully converted to: The Man Who Mistook His Wife for a Hat.mp3
  Metadata preserved:
    Title: The Man Who Mistook His Wife for a Hat
    Artist: Oliver Sacks
    Album: The Man Who Mistook His Wife for a Hat
    Date: 2018
  ✓ Album artwork included

==================================================
Conversion complete!
Successful: 1
Failed: 0
==================================================
```

## License

This project is open source and available under the MIT License.