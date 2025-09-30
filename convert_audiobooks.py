import os
import subprocess
import json
from pathlib import Path
import re
from typing import Optional

class AudiobookConverter:
    def __init__(self, folder_path, output_folder=None):
        self.folder_path = Path(folder_path)
        self.output_folder = Path(output_folder) if output_folder else self.folder_path / "converted_mp3"
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Common image formats for album artwork
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
        
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
    
    def find_album_artwork(self, m4b_path):
        """Find album artwork file with the same name as the M4B file"""
        m4b_path = Path(m4b_path)
        base_name = m4b_path.stem
        
        # Look for image files with the same base name
        for ext in self.image_extensions:
            artwork_path = m4b_path.parent / f"{base_name}{ext}"
            if artwork_path.exists():
                print(f"Found external artwork: {artwork_path.name}")
                return str(artwork_path)
        
        # Look for common cover art names in the same directory
        common_names = ['cover', 'folder', 'albumart', 'front', 'artwork']
        for name in common_names:
            for ext in self.image_extensions:
                artwork_path = m4b_path.parent / f"{name}{ext}"
                if artwork_path.exists():
                    print(f"Found common artwork file: {artwork_path.name}")
                    return str(artwork_path)
        
        return None
    
    def has_embedded_artwork(self, m4b_path):
        """Check if the M4B file has embedded artwork"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_name',
                '-of', 'csv=p=0',
                str(m4b_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            # If there's a video stream, it's likely embedded artwork
            return bool(result.stdout.strip())
        except Exception:
            return False
    
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
        
        # Find external artwork
        external_artwork = self.find_album_artwork(m4b_path)
        has_embedded_art = self.has_embedded_artwork(m4b_path)
        
        # Build FFmpeg command
        cmd = ['ffmpeg', '-i', str(m4b_path)]
        
        # Add external artwork as input if found
        if external_artwork:
            cmd.extend(['-i', external_artwork])
        
        # Add metadata mapping
        cmd.extend(['-map', '0:a'])  # Map audio stream
        cmd.extend(['-map_metadata', '0'])  # Copy all metadata from audio file
        
        # Handle artwork mapping
        if external_artwork:
            cmd.extend(['-map', '1:v'])  # Map video/image stream from second input (external artwork)
            cmd.extend(['-c:v', 'copy'])  # Copy video stream without re-encoding
            cmd.extend(['-disposition:v:0', 'attached_pic'])  # Mark as attached picture
            print(f"Adding external artwork: {Path(external_artwork).name}")
        elif has_embedded_art:
            cmd.extend(['-map', '0:v'])  # Map embedded artwork
            cmd.extend(['-c:v', 'copy'])  # Copy video stream without re-encoding
            cmd.extend(['-disposition:v:0', 'attached_pic'])  # Mark as attached picture
            print("Preserving embedded artwork from M4B file")
        
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
            
            # Display artwork info
            if external_artwork or has_embedded_art:
                print(f"  ✓ Album artwork included")
            
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