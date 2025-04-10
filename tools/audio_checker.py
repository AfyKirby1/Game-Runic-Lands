#!/usr/bin/env python3

"""
Audio File Checker and Repair Utility for Runic Lands

This script helps analyze and fix issues with audio files for the Runic Lands game.
It checks for missing section files, analyzes file durations, and can create 
missing files if needed.
"""

import os
import sys
import shutil
import wave
from pathlib import Path

# Path to audio directory - modify as needed
AUDIO_DIR = "../assets/audio"

def print_header(text):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_file_existence():
    """Check if all required audio files exist."""
    print_header("Checking Required Audio Files")
    
    # Define required files
    required_files = {
        "menu_theme.wav": "Main menu music (fallback)",
        "menu_section1.wav": "Menu music - Heroic Intro",
        "menu_section2.wav": "Menu music - Calm Town Section",
        "menu_section3.wav": "Menu music - Energetic Battle Section",
        "menu_section4.wav": "Menu music - Resolving Passage",
        "menu_section5.wav": "Menu music - Misty Woods Intro",
        "menu_section6.wav": "Menu music - Descending Arpeggio",
        "menu_section7.wav": "Menu music - Wave Pattern",
        "menu_section8.wav": "Menu music - Cascading",
        "menu_section9.wav": "Menu music - Mountain",
        "menu_section10.wav": "Menu music - Wandering",
        "menu_click.wav": "Menu click sound effect",
        "attack.wav": "Player attack sound effect"
    }
    
    # Check each file
    missing_files = []
    for filename, description in required_files.items():
        path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(path):
            print(f"✓ {filename}: Found ({description})")
        else:
            print(f"✗ {filename}: MISSING ({description})")
            missing_files.append(filename)
    
    return missing_files

def analyze_audio_files():
    """Analyze audio file properties."""
    print_header("Audio File Analysis")
    
    # Get all WAV files in the audio directory
    audio_path = Path(AUDIO_DIR)
    all_files = list(audio_path.glob("*.wav"))
    
    if not all_files:
        print("No .wav files found in the audio directory.")
        return
    
    # Print file sizes
    print("\nFile sizes:")
    for file_path in all_files:
        size_bytes = file_path.stat().st_size
        size_kb = size_bytes / 1024
        print(f"  {file_path.name}: {size_kb:.2f} KB")
    
    # Analyze durations
    print("\nFile durations:")
    for file_path in all_files:
        try:
            with wave.open(str(file_path), 'rb') as w:
                # Calculate duration
                frames = w.getnframes()
                rate = w.getframerate()
                channels = w.getnchannels()
                sampwidth = w.getsampwidth()
                duration = frames / rate
                
                print(f"  {file_path.name}: {duration:.2f} seconds "
                      f"({frames} frames @ {rate} Hz, {channels} channels, "
                      f"{sampwidth*8}-bit)")
        except Exception as e:
            print(f"  {file_path.name}: ERROR - {str(e)}")

def create_missing_section_files():
    """Create missing menu section files by copying existing ones."""
    print_header("Creating Missing Section Files")
    
    # Check for the basis file to copy from
    base_files = ["menu_section1.wav", "menu_theme.wav"]
    base_file = None
    
    for filename in base_files:
        path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(path):
            base_file = path
            print(f"Using {filename} as the base file for missing sections")
            break
    
    if not base_file:
        print("No suitable base file found. Cannot create missing sections.")
        return False
    
    # Create missing section files
    created_count = 0
    for i in range(1, 6):
        section_file = os.path.join(AUDIO_DIR, f"menu_section{i}.wav")
        if not os.path.exists(section_file):
            try:
                shutil.copy2(base_file, section_file)
                print(f"Created missing file: {section_file}")
                created_count += 1
            except Exception as e:
                print(f"Error creating {section_file}: {e}")
    
    if created_count > 0:
        print(f"\nCreated {created_count} missing section files")
    else:
        print("\nNo missing section files needed to be created")
    
    return created_count > 0

def fix_audio_permissions():
    """Fix permissions on audio files."""
    print_header("Fixing File Permissions")
    
    audio_path = Path(AUDIO_DIR)
    all_files = list(audio_path.glob("*.wav"))
    
    fixed_count = 0
    for file_path in all_files:
        try:
            os.chmod(file_path, 0o644)  # rw-r--r--
            print(f"Fixed permissions for {file_path.name}")
            fixed_count += 1
        except Exception as e:
            print(f"Error fixing permissions for {file_path.name}: {e}")
    
    print(f"\nFixed permissions for {fixed_count} files")
    return fixed_count > 0

def verify_menu_sections():
    """Verify that menu sections have consistent properties."""
    print_header("Verifying Menu Section Consistency")
    
    section_files = []
    for i in range(1, 6):
        path = os.path.join(AUDIO_DIR, f"menu_section{i}.wav")
        if os.path.exists(path):
            section_files.append(path)
    
    if len(section_files) < 2:
        print("Not enough section files to compare consistency.")
        return False
    
    # Extract properties from the first file as reference
    try:
        with wave.open(section_files[0], 'rb') as w:
            ref_rate = w.getframerate()
            ref_channels = w.getnchannels()
            ref_sampwidth = w.getsampwidth()
            
        print(f"Reference format: {ref_rate} Hz, {ref_channels} channels, {ref_sampwidth*8}-bit")
        
        # Check other files against the reference
        inconsistent = False
        for file_path in section_files[1:]:
            with wave.open(file_path, 'rb') as w:
                rate = w.getframerate()
                channels = w.getnchannels()
                sampwidth = w.getsampwidth()
                
                if rate != ref_rate or channels != ref_channels or sampwidth != ref_sampwidth:
                    print(f"WARNING: {os.path.basename(file_path)} has inconsistent format: "
                          f"{rate} Hz, {channels} channels, {sampwidth*8}-bit")
                    inconsistent = True
                else:
                    print(f"✓ {os.path.basename(file_path)}: Format is consistent")
        
        return not inconsistent
    except Exception as e:
        print(f"Error verifying section consistency: {e}")
        return False

def main():
    print("\nRunic Lands Audio Checker and Repair Utility")
    print("--------------------------------------------")
    
    # Ensure audio directory exists
    if not os.path.exists(AUDIO_DIR):
        print(f"Error: Audio directory not found: {AUDIO_DIR}")
        print("Please run this script from the tools directory or adjust the AUDIO_DIR path.")
        return 1
    
    # Check file existence
    missing_files = check_file_existence()
    
    # Create missing files if needed
    if missing_files and any(f.startswith("menu_section") for f in missing_files):
        if input("\nWould you like to create missing menu section files? (y/n): ").lower() == 'y':
            create_missing_section_files()
    
    # Analyze audio files
    analyze_audio_files()
    
    # Verify menu section consistency
    if any(os.path.exists(os.path.join(AUDIO_DIR, f"menu_section{i}.wav")) for i in range(1, 6)):
        verify_menu_sections()
    
    # Fix permissions if on Unix
    if sys.platform != "win32" and input("\nWould you like to fix file permissions? (y/n): ").lower() == 'y':
        fix_audio_permissions()
    
    print("\nAudio analysis complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 