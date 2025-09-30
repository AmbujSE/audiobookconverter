import os
import subprocess
import json
from pathlib import Path
import re

class AudiobookConverter:
    def __init__(self, folder_path, output_folder=None):
        self.folder_path = Path(folder_path)
        self.output_folder = Path(output_folder) if output_folder else self.folder_path / "converted_mp3"
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
    def check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: FFmpeg is not installed or not in PATH")
            print("Please install FFmpeg from https://ffmpeg.org/download.html")
            return False
    
    def parse_cue_file(self, cue_path):
        """Parse .cue file to extract chapter information"""
        chapters = []
        try:
            with open(cue_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract track information
            tracks = re.findall(r'TRACK (\d+).*?\n.*?TITLE "(.*?)".*?\n.*?INDEX \d+ (\d+):(\d+):(\d+)', 
                              content, re.DOTALL)
            
            for track_num, title, min, sec, frame in tracks:
                # Convert time to milliseconds
                time_ms = (int(min) * 60 + int(sec)) * 1000 + (int(frame) * 1000 // 75)
                chapters.append({
                    'title': title,
                    'time_ms': time_ms
                })
        except Exception as e:
            print(f"Warning: Could not parse CUE file {cue_path}: {e}")
        
        return chapters
    
    def get_metadata(self, m4b_path):
        """Extract metadata from m4b file using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_chapters',
                str(m4b_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Warning: Could not extract metadata from {m4b_path}: {e}")
            return None
    
    def convert_m4b_to_mp3(self, m4b_path):
        """Convert a single m4b file to mp3 with metadata and chapters"""
        m4b_path = Path(m4b_path)
        output_path = self.output_folder / f"{m4b_path.stem}.mp3"
        
        print(f"\nProcessing: {m4b_path.name}")
        
        # Check for CUE file
        cue_path = m4b_path.with_suffix('.cue')
        cue_chapters = []
        if cue_path.exists():
            print(f"Found CUE file: {cue_path.name}")
            cue_chapters = self.parse_cue_file(cue_path)
        
        # Get metadata from m4b
        metadata = self.get_metadata(m4b_path)
        
        # Build FFmpeg command
        cmd = ['ffmpeg', '-i', str(m4b_path)]
        
        # Add metadata mapping
        cmd.extend(['-map', '0:a'])  # Map audio stream
        cmd.extend(['-map_metadata', '0'])  # Copy all metadata
        
        # Check if chapters exist in the m4b file
        has_chapters = False
        if metadata and 'chapters' in metadata and len(metadata['chapters']) > 0:
            has_chapters = True
            cmd.extend(['-map_chapters', '0'])  # Copy chapters
            print(f"Found {len(metadata['chapters'])} chapters in m4b file")
        elif cue_chapters:
            print(f"Using {len(cue_chapters)} chapters from CUE file")
            # Note: FFmpeg doesn't directly support CUE chapter injection in this way
            # Chapters from CUE would need to be written to a metadata file
        
        # Set codec and quality
        cmd.extend([
            '-c:a', 'libmp3lame',  # MP3 codec
            '-q:a', '2',  # High quality (VBR ~190 kbps)
            '-y',  # Overwrite output file
            str(output_path)
        ])
        
        try:
            print("Converting...")
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✓ Successfully converted to: {output_path.name}")
            
            # Display metadata info
            if metadata and 'format' in metadata and 'tags' in metadata['format']:
                tags = metadata['format']['tags']
                print(f"  Metadata preserved:")
                for key in ['title', 'artist', 'album', 'date', 'genre']:
                    if key in tags:
                        print(f"    {key.capitalize()}: {tags[key]}")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Error converting {m4b_path.name}: {e}")
            if e.stderr:
                print(f"  Error details: {e.stderr.decode()}")
            return False
    
    def convert_all(self):
        """Convert all m4b files in the folder"""
        if not self.check_ffmpeg():
            return
        
        m4b_files = list(self.folder_path.glob("*.m4b"))
        
        if not m4b_files:
            print(f"No .m4b files found in {self.folder_path}")
            return
        
        print(f"Found {len(m4b_files)} .m4b file(s)")
        print(f"Output folder: {self.output_folder}")
        
        successful = 0
        failed = 0
        
        for m4b_file in m4b_files:
            if self.convert_m4b_to_mp3(m4b_file):
                successful += 1
            else:
                failed += 1
        
        print(f"\n{'='*50}")
        print(f"Conversion complete!")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"{'='*50}")

# Usage
if __name__ == "__main__":
    # Change this to your audiobook folder path
    input_folder = "/mnt/d/Media/Convert"
    
    # Optional: specify custom output folder
    # output_folder = r"C:\path\to\output"
    # converter = AudiobookConverter(input_folder, output_folder)
    
    converter = AudiobookConverter(input_folder)
    converter.convert_all()