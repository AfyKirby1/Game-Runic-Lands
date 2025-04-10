#!/usr/bin/env python3

"""
Audio File Fixer for Runic Lands

This script analyzes audio files, detects silence, and creates improved versions
with better audio content distribution without long silent parts.
"""

import os
import sys
import wave
import struct
import array
import numpy as np
from pathlib import Path
import shutil

# Path to audio directory
AUDIO_DIR = "../assets/audio"

def print_header(text):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def analyze_audio_content(filename):
    """
    Analyze an audio file to detect silence and actual content.
    Returns details about the audio content.
    """
    file_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        return None

    try:
        with wave.open(file_path, 'rb') as wav:
            # Get basic properties
            n_channels = wav.getnchannels()
            sampwidth = wav.getsampwidth()
            framerate = wav.getframerate()
            n_frames = wav.getnframes()
            duration = n_frames / framerate
            
            # Read all frames
            frames = wav.readframes(n_frames)
            
            # Convert to numpy array for analysis
            if sampwidth == 2:  # 16-bit audio
                fmt = f"{n_frames * n_channels}h"
                data = struct.unpack(fmt, frames)
                data = np.array(data, dtype=np.int16)
            elif sampwidth == 4:  # 32-bit audio
                fmt = f"{n_frames * n_channels}i"
                data = struct.unpack(fmt, frames)
                data = np.array(data, dtype=np.int32)
            else:  # 8-bit audio or other
                data = np.frombuffer(frames, dtype=np.uint8)
                data = data.astype(np.int16) - 128  # Convert to signed
            
            # If stereo, average channels
            if n_channels == 2:
                data = data.reshape(-1, 2)
                data = np.mean(data, axis=1)
            
            # Calculate absolute values for amplitude analysis
            abs_data = np.abs(data)
            
            # Detect silent parts (threshold at 1% of max amplitude)
            threshold = max(0.01 * np.max(abs_data), 100)  # At least 100 to avoid background noise
            silent_mask = abs_data < threshold
            
            # Calculate silence percentage
            silence_percent = 100 * np.sum(silent_mask) / len(data)
            
            # Find contiguous segments of audio
            segments = []
            is_silent = True
            segment_start = 0
            
            for i in range(len(silent_mask)):
                if is_silent and not silent_mask[i]:
                    # Transition: silence -> sound
                    segment_start = i
                    is_silent = False
                elif not is_silent and silent_mask[i]:
                    # Transition: sound -> silence
                    if i - segment_start > framerate * 0.1:  # At least 100ms
                        segments.append((segment_start, i))
                    is_silent = True
            
            # Handle the case where the file ends with sound
            if not is_silent:
                segments.append((segment_start, len(silent_mask)))
            
            # Convert to seconds
            segments_sec = [(s[0]/framerate, s[1]/framerate) for s in segments]
            
            return {
                'filename': filename,
                'duration': duration,
                'silence_percent': silence_percent,
                'segments': segments,
                'segments_sec': segments_sec,
                'properties': {
                    'channels': n_channels,
                    'sampwidth': sampwidth,
                    'framerate': framerate,
                    'n_frames': n_frames
                },
                'data': data,
                'silent_mask': silent_mask
            }
    except Exception as e:
        print(f"Error analyzing {filename}: {e}")
        return None

def create_fixed_audio_file(original, output_filename, keepframes=None):
    """
    Create a fixed audio file by removing or shortening silences.
    If keepframes is provided, it should be a list of frame ranges to keep.
    """
    try:
        # Create backup of original file
        backup_path = os.path.join(AUDIO_DIR, f"{original['filename']}.backup")
        original_path = os.path.join(AUDIO_DIR, original['filename'])
        
        if not os.path.exists(backup_path):
            shutil.copy2(original_path, backup_path)
            print(f"Created backup: {backup_path}")
        
        # Get original properties
        properties = original['properties']
        
        # If we're just shortening silences
        if keepframes:
            # Create new audio data array
            new_data = np.array([], dtype=original['data'].dtype)
            
            # Add each segment
            for start, end in keepframes:
                segment_data = original['data'][start:end]
                new_data = np.append(new_data, segment_data)
            
            # Create a new WAV file
            output_path = os.path.join(AUDIO_DIR, output_filename)
            with wave.open(output_path, 'wb') as wav:
                wav.setnchannels(properties['channels'])
                wav.setsampwidth(properties['sampwidth'])
                wav.setframerate(properties['framerate'])
                
                # Convert numpy array to bytes
                if properties['sampwidth'] == 2:  # 16-bit audio
                    audio_bytes = new_data.astype(np.int16).tobytes()
                elif properties['sampwidth'] == 4:  # 32-bit audio
                    audio_bytes = new_data.astype(np.int32).tobytes()
                else:  # 8-bit audio
                    new_data = new_data.astype(np.int8) + 128  # Convert back to unsigned
                    audio_bytes = new_data.tobytes()
                
                wav.writeframes(audio_bytes)
            
            print(f"Created fixed audio file: {output_path} with {len(new_data)} frames")
            return output_path
        
        # For more complex processing, we'd implement additional methods here
        return None
    
    except Exception as e:
        print(f"Error creating fixed audio file: {e}")
        return None

def duplicate_audio_content(original, output_filename, repeat_count=1):
    """
    Create a new audio file by duplicating the audio content to fill the duration.
    """
    try:
        # Create backup of original file
        backup_path = os.path.join(AUDIO_DIR, f"{original['filename']}.backup")
        original_path = os.path.join(AUDIO_DIR, original['filename'])
        
        if not os.path.exists(backup_path):
            shutil.copy2(original_path, backup_path)
            print(f"Created backup: {backup_path}")
        
        # Get original properties
        properties = original['properties']
        
        # Find the non-silent part of the audio
        silent_mask = original['silent_mask']
        if np.all(silent_mask):
            print(f"No audio content found in {original['filename']}")
            return None
        
        # Find the first non-silent segment
        segments = original['segments']
        if not segments:
            print(f"No segments found in {original['filename']}")
            return None
        
        # Get the longest segment
        longest_segment = max(segments, key=lambda s: s[1] - s[0])
        content_start, content_end = longest_segment
        content_data = original['data'][content_start:content_end]
        
        # Create new audio data by repeating the content
        new_data = np.array([], dtype=original['data'].dtype)
        for _ in range(repeat_count):
            new_data = np.append(new_data, content_data)
        
        # Ensure we don't exceed the original length
        if len(new_data) > len(original['data']):
            new_data = new_data[:len(original['data'])]
        
        # If we're shorter than original, pad with last few frames repeated
        if len(new_data) < len(original['data']):
            padding_needed = len(original['data']) - len(new_data)
            # Use the last 100ms of the content data as padding pattern
            padding_pattern = content_data[-min(len(content_data), int(properties['framerate'] * 0.1)):]
            while len(new_data) < len(original['data']):
                padding_to_add = min(padding_needed, len(padding_pattern))
                new_data = np.append(new_data, padding_pattern[:padding_to_add])
                padding_needed -= padding_to_add
        
        # Create a new WAV file
        output_path = os.path.join(AUDIO_DIR, output_filename)
        with wave.open(output_path, 'wb') as wav:
            wav.setnchannels(properties['channels'])
            wav.setsampwidth(properties['sampwidth'])
            wav.setframerate(properties['framerate'])
            
            # Convert numpy array to bytes
            if properties['sampwidth'] == 2:  # 16-bit audio
                audio_bytes = new_data.astype(np.int16).tobytes()
            elif properties['sampwidth'] == 4:  # 32-bit audio
                audio_bytes = new_data.astype(np.int32).tobytes()
            else:  # 8-bit audio
                new_data = new_data.astype(np.int8) + 128  # Convert back to unsigned
                audio_bytes = new_data.tobytes()
            
            wav.writeframes(audio_bytes)
        
        print(f"Created improved audio file: {output_path}")
        print(f"  - Original audio content: {(content_end - content_start) / properties['framerate']:.2f} seconds")
        print(f"  - New file duration: {len(new_data) / properties['framerate']:.2f} seconds")
        
        return output_path
    
    except Exception as e:
        print(f"Error creating improved audio file: {e}")
        return None

def restore_original_files():
    """Restore original files from backups."""
    print_header("Restoring Original Files")
    
    restored = 0
    for filename in os.listdir(AUDIO_DIR):
        if filename.endswith('.backup'):
            original_name = filename[:-7]  # Remove .backup
            backup_path = os.path.join(AUDIO_DIR, filename)
            original_path = os.path.join(AUDIO_DIR, original_name)
            
            try:
                shutil.copy2(backup_path, original_path)
                print(f"Restored {original_name} from backup")
                restored += 1
            except Exception as e:
                print(f"Error restoring {original_name}: {e}")
    
    print(f"\nRestored {restored} files from backups")
    return restored

def improve_menu_sections():
    """
    Analyze and improve all menu section files.
    This will create new files with better audio content.
    """
    print_header("Improving Menu Section Files")
    
    # Analyze all section files
    section_files = []
    for i in range(1, 6):
        filename = f"menu_section{i}.wav"
        file_path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(file_path):
            section_files.append(filename)
    
    if not section_files:
        print("No menu section files found to improve.")
        return False
    
    # Analyze each file
    analyses = {}
    for filename in section_files:
        print(f"Analyzing {filename}...")
        analysis = analyze_audio_content(filename)
        if analysis:
            analyses[filename] = analysis
            print(f"  Duration: {analysis['duration']:.2f} seconds")
            print(f"  Silence: {analysis['silence_percent']:.1f}%")
            print(f"  Audio segments: {len(analysis['segments'])}")
            if analysis['segments_sec']:
                print("  Audio content at:")
                for i, (start, end) in enumerate(analysis['segments_sec'][:5]):
                    print(f"    {i+1}. {start:.2f}s - {end:.2f}s ({end-start:.2f}s)")
                if len(analysis['segments_sec']) > 5:
                    print(f"    ... and {len(analysis['segments_sec']) - 5} more segments")
    
    # Check if we found excessive silence
    files_to_improve = []
    for filename, analysis in analyses.items():
        if analysis['silence_percent'] > 50:  # If more than 50% is silence
            files_to_improve.append(filename)
    
    # Improve files with excessive silence
    if files_to_improve:
        print(f"\nImproving {len(files_to_improve)} files with excessive silence...")
        for filename in files_to_improve:
            print(f"\nImproving {filename}...")
            # Create an improved version by duplicating content
            duplicate_audio_content(analyses[filename], filename, repeat_count=3)
    else:
        print("\nNo files need improvement based on silence percentage.")
    
    # Create unique variations if all files are the same
    if len(section_files) >= 2:
        # Check if all files have the same content
        first_file = section_files[0]
        all_same = True
        
        for filename in section_files[1:]:
            if not all_same:
                break
                
            # Compare file sizes first (quick check)
            if os.path.getsize(os.path.join(AUDIO_DIR, first_file)) != os.path.getsize(os.path.join(AUDIO_DIR, filename)):
                all_same = False
                break
            
            # If sizes match, check the actual content
            with open(os.path.join(AUDIO_DIR, first_file), 'rb') as f1, open(os.path.join(AUDIO_DIR, filename), 'rb') as f2:
                if f1.read() != f2.read():
                    all_same = False
                    break
        
        if all_same and first_file in analyses:
            print("\nAll section files have identical content. Creating variations...")
            
            # Get the audio content
            analysis = analyses[first_file]
            
            # Create variations with different start points and speeds
            for i, filename in enumerate(section_files):
                if i == 0:
                    # Keep the first file as is
                    continue
                    
                # For each variation, modify the audio differently
                variation_type = i % 3
                if variation_type == 1:
                    # Speed up the audio slightly (pitch increase)
                    modified_data = analysis['data'][::2]  # Skip every other sample
                    output_path = os.path.join(AUDIO_DIR, filename)
                    
                    # Create a new WAV file
                    with wave.open(output_path, 'wb') as wav:
                        wav.setnchannels(analysis['properties']['channels'])
                        wav.setsampwidth(analysis['properties']['sampwidth'])
                        wav.setframerate(analysis['properties']['framerate'])
                        
                        # Convert numpy array to bytes and ensure same length
                        modified_data = np.resize(modified_data, len(analysis['data']))
                        if analysis['properties']['sampwidth'] == 2:
                            audio_bytes = modified_data.astype(np.int16).tobytes()
                        else:
                            audio_bytes = modified_data.astype(np.int8).tobytes()
                        
                        wav.writeframes(audio_bytes)
                    
                    print(f"Created variation {filename} (speed modified)")
                    
                elif variation_type == 2:
                    # Reverse the audio
                    modified_data = np.flip(analysis['data'])
                    output_path = os.path.join(AUDIO_DIR, filename)
                    
                    # Create a new WAV file
                    with wave.open(output_path, 'wb') as wav:
                        wav.setnchannels(analysis['properties']['channels'])
                        wav.setsampwidth(analysis['properties']['sampwidth'])
                        wav.setframerate(analysis['properties']['framerate'])
                        
                        if analysis['properties']['sampwidth'] == 2:
                            audio_bytes = modified_data.astype(np.int16).tobytes()
                        else:
                            audio_bytes = modified_data.astype(np.int8).tobytes()
                        
                        wav.writeframes(audio_bytes)
                    
                    print(f"Created variation {filename} (reversed)")
                    
                else:
                    # Apply volume envelope
                    envelope = np.linspace(0.5, 1.0, len(analysis['data']))
                    modified_data = analysis['data'] * envelope
                    output_path = os.path.join(AUDIO_DIR, filename)
                    
                    # Create a new WAV file
                    with wave.open(output_path, 'wb') as wav:
                        wav.setnchannels(analysis['properties']['channels'])
                        wav.setsampwidth(analysis['properties']['sampwidth'])
                        wav.setframerate(analysis['properties']['framerate'])
                        
                        if analysis['properties']['sampwidth'] == 2:
                            audio_bytes = modified_data.astype(np.int16).tobytes()
                        else:
                            audio_bytes = modified_data.astype(np.int8).tobytes()
                        
                        wav.writeframes(audio_bytes)
                    
                    print(f"Created variation {filename} (volume envelope)")
    
    return True

def main():
    print("\nRunic Lands Audio File Fixer")
    print("----------------------------")
    
    # Ensure audio directory exists
    if not os.path.exists(AUDIO_DIR):
        print(f"Error: Audio directory not found: {AUDIO_DIR}")
        print("Please run this script from the tools directory or adjust the AUDIO_DIR path.")
        return 1
    
    print("\nThis tool will analyze and fix audio files for better playback.")
    print("It will create backups of original files before modifying them.")
    
    # Offer to restore original files if backups exist
    backup_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith('.backup')]
    if backup_files:
        print(f"\nFound {len(backup_files)} backup files from previous runs.")
        if input("Would you like to restore original files from backups? (y/n): ").lower() == 'y':
            restore_original_files()
            if input("\nExit after restoration? (y/n): ").lower() == 'y':
                return 0
    
    # Improve menu section files
    if input("\nAnalyze and improve menu section files? (y/n): ").lower() == 'y':
        improve_menu_sections()
    
    print("\nAudio file fixing completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 