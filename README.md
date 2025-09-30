# Audiobook Converter

A Python script to convert M4B audiobook files to high-quality MP3 format while preserving metadata and chapter information.

## Features

- Converts M4B audiobook files to MP3 format
- Preserves original metadata (title, artist, album, etc.)
- Maintains chapter information from the source file
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

## Example Output

```
Found 1 .m4b file(s)
Output folder: /path/to/output/converted_mp3

Processing: Pride and Prejudice (Unabridged).m4b
Found 8 chapters in m4b file
Converting...
✓ Successfully converted to: Pride and Prejudice (Unabridged).mp3
  Metadata preserved:
    Title: Pride and Prejudice (Unabridged)
    Artist: Jane Austen & Lulu Raczka
    Album: Pride and Prejudice (Unabridged)

==================================================
Conversion complete!
Successful: 1
Failed: 0
==================================================
```

## License

This project is open source and available under the MIT License.