#!/usr/bin/env python3
"""
Quick Audio Fix for Runic Lands

This script automatically fixes all menu section files by trimming
them to contain only the actual musical notes, removing silence.
"""

import os
import wave
import struct
import numpy as np
import shutil
from pathlib import Path

# Audio directory path
AUDIO_DIR = "../assets/audio"

def print_header(text):
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)

def process_audio_file(filename):
    """Process a single audio file by trimming silence."""
    file_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False

    # Create backup
    backup_path = f"{file_path}.backup"
    if not os.path.exists(backup_path):
        try:
            shutil.copy2(file_path, backup_path)
            print(f"Created backup: {backup_path}")
        except Exception as e:
            print(f"Error creating backup for {filename}: {e}")
            return False

    try:
        # Open the WAV file
        with wave.open(file_path, 'rb') as wav:
            # Get properties
            n_channels = wav.getnchannels()
            sampwidth = wav.getsampwidth()
            framerate = wav.getframerate()
            n_frames = wav.getnframes()

            # Read all frames
            frames = wav.readframes(n_frames)

            # Convert to numpy array
            if sampwidth == 2:  # 16-bit audio
                fmt = f"<{n_frames * n_channels}h"  # Use little-endian
                data = struct.unpack(fmt, frames)
                data = np.array(data, dtype=np.int16)
            elif sampwidth == 1:  # 8-bit audio (unsigned)
                fmt = f"<{n_frames * n_channels}B"
                data = struct.unpack(fmt, frames)
                data = np.array(data, dtype=np.uint8)
                # Convert to signed int16 for processing consistency
                data = data.astype(np.int16) - 128
            else:
                print(f"Unsupported sample width {sampwidth} for {filename}. Skipping.")
                return False

            # Handle stereo/mono for processing
            if n_channels == 2:
                data_proc = data.reshape(-1, 2)
                # Use absolute max of both channels for better detection
                mono_for_rms = np.maximum(np.abs(data_proc[:, 0]), np.abs(data_proc[:, 1])).astype(np.float64)
            else:  # Mono
                data_proc = data
                mono_for_rms = np.abs(data_proc).astype(np.float64)

            # --- EXTREMELY AGGRESSIVE Silence Detection ---
            # First, find the absolute maximum value to calibrate
            abs_max = np.max(mono_for_rms)
            
            # Set an extremely aggressive threshold - just 0.5% of maximum 
            threshold = abs_max * 0.005  # Ultra-low threshold to catch very quiet notes
            
            # Find where audio is above threshold
            audio_mask = mono_for_rms > threshold
            
            # Identify the start and potential end of actual notes
            if np.any(audio_mask):
                # Find first non-silent frame
                first_audio_frame = np.argmax(audio_mask)
                
                # Find last frame that exceeds threshold within first 2 seconds
                # (focusing on just the initial notes)
                max_search_frame = min(n_frames, first_audio_frame + int(framerate * 2.0))
                last_audio_frame = max_search_frame - 1
                for i in range(first_audio_frame, max_search_frame):
                    if audio_mask[i]:
                        last_audio_frame = i
                
                # Add a small buffer (30ms) at the end to catch note tails
                last_audio_frame = min(n_frames - 1, last_audio_frame + int(framerate * 0.03))
                
                # Ensure we have at least 100ms of audio
                min_duration = int(framerate * 0.1)
                if last_audio_frame - first_audio_frame < min_duration:
                    last_audio_frame = min(n_frames - 1, first_audio_frame + min_duration)
                
                # Extract only the frames with actual audio
                actual_audio_segment = data_proc[first_audio_frame:last_audio_frame+1]
                
                # Calculate the actual duration 
                actual_duration_sec = len(actual_audio_segment) / framerate
                print(f"  Detected actual audio: {actual_duration_sec:.2f} seconds (frames {first_audio_frame} to {last_audio_frame})")
                
                # Write the trimmed file
                with wave.open(file_path, 'wb') as out_wav:
                    out_wav.setnchannels(n_channels)
                    out_wav.setsampwidth(sampwidth)
                    out_wav.setframerate(framerate)
                    
                    # Convert back to bytes
                    if n_channels == 2:
                        audio_bytes = actual_audio_segment.tobytes()
                    else:
                        if sampwidth == 2:
                            audio_bytes = actual_audio_segment.astype(np.int16).tobytes()
                        else:  # 8-bit audio
                            audio_bytes = (actual_audio_segment.astype(np.int8) + 128).astype(np.uint8).tobytes()
                    
                    out_wav.writeframes(audio_bytes)
                
                print(f"Fixed {filename} - Trimmed to {actual_duration_sec:.2f} seconds")
                return True
            else:
                print(f"  Warning: No audio detected above threshold in {filename}. Skipping fix.")
                return False

    except wave.Error as e:
        print(f"Error processing {filename} (likely not a valid WAV file): {e}")
        return False
    except Exception as e:
        print(f"Unexpected error processing {filename}: {e}")
        return False

def create_variations():
    """Create variations of menu_section1.wav if other section files don't exist."""
    # Find existing section files
    section_files = []
    for i in range(1, 6):
        filename = f"menu_section{i}.wav"
        file_path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(file_path):
            section_files.append(filename)

    # If we don't have all 5 section files, create missing ones from menu_section1.wav
    if len(section_files) < 5 and "menu_section1.wav" in section_files:
        print("\nCreating missing section files...")

        # Load the first section file
        file_path = os.path.join(AUDIO_DIR, "menu_section1.wav")
        with wave.open(file_path, 'rb') as wav:
            n_channels = wav.getnchannels()
            sampwidth = wav.getsampwidth()
            framerate = wav.getframerate()
            n_frames = wav.getnframes()
            frames = wav.readframes(n_frames)

            # Convert to numpy array
            if sampwidth == 2:  # 16-bit audio
                fmt = f"<{n_frames * n_channels}h"
                data = struct.unpack(fmt, frames)
                data = np.array(data, dtype=np.int16)
                if n_channels == 2:
                    data = data.reshape(-1, 2)
            else:  # Assume 8-bit audio
                data = np.frombuffer(frames, dtype=np.uint8)
                data = data.astype(np.int16) - 128  # Convert to signed
                if n_channels == 2:
                    data = data.reshape(-1, 2)

            # Create variations for missing files
            for i in range(2, 6):
                filename = f"menu_section{i}.wav"
                file_path = os.path.join(AUDIO_DIR, filename)

                if not os.path.exists(file_path):
                    # Create a variation based on index
                    variation_type = (i - 1) % 3

                    if variation_type == 0:
                        # Pitch shift (increase) by modifying playback rate
                        new_data = data.copy()
                        if n_channels == 2:
                            # Process each channel
                            for channel in range(2):
                                # Apply envelope
                                envelope = np.linspace(0.7, 1.0, len(new_data))
                                new_data[:, channel] = new_data[:, channel] * envelope
                        else:
                            # Apply envelope
                            envelope = np.linspace(0.7, 1.0, len(new_data))
                            new_data = new_data * envelope

                    elif variation_type == 1:
                        # Reverse the audio
                        new_data = np.flip(data, axis=0)

                    else:
                        # Apply a filter (e.g., volume envelope)
                        new_data = data.copy()
                        if n_channels == 2:
                            # Process each channel
                            for channel in range(2):
                                # Apply envelope
                                envelope = np.linspace(1.0, 0.7, len(new_data))
                                new_data[:, channel] = new_data[:, channel] * envelope
                        else:
                            # Apply envelope
                            envelope = np.linspace(1.0, 0.7, len(new_data))
                            new_data = new_data * envelope

                    # Write the new file
                    with wave.open(file_path, 'wb') as out_wav:
                        out_wav.setnchannels(n_channels)
                        out_wav.setsampwidth(sampwidth)
                        out_wav.setframerate(framerate)

                        # Convert back to bytes
                        if sampwidth == 2:
                            audio_bytes = new_data.astype(np.int16).tobytes()
                        else:
                            new_data = new_data.astype(np.int8) + 128  # Convert back to unsigned
                            audio_bytes = new_data.tobytes()

                        out_wav.writeframes(audio_bytes)

                    print(f"Created {filename} as a variation of menu_section1.wav")

        return True

    return False

def main():
    """Main function to fix audio files automatically."""
    print_header("Runic Lands Quick Audio Fixer")

    # Check if audio directory exists
    if not os.path.exists(AUDIO_DIR):
        print(f"Error: Audio directory not found: {AUDIO_DIR}")
        print("Make sure you're running this script from the tools directory")
        return 1

    # Process menu section files
    fixed_count = 0
    processed_files = set()  # Keep track of files already processed

    # First pass: Process existing files
    for i in range(1, 6):
        filename = f"menu_section{i}.wav"
        file_path = os.path.join(AUDIO_DIR, filename)

        if os.path.exists(file_path):
            print(f"\nProcessing {filename}...")
            if process_audio_file(filename):
                fixed_count += 1
                processed_files.add(filename)
        else:
            print(f"\n{filename} not found. Will try to create it...")

    # Create variations if needed (using the original logic)
    created_new_files = create_variations()  # Keep the original variation logic

    # Second pass: Process newly created files ONLY IF they weren't just processed
    if created_new_files:
        print("\nProcessing newly created variation files...")
        for i in range(2, 6):
            filename = f"menu_section{i}.wav"
            file_path = os.path.join(AUDIO_DIR, filename)

            # Check if it exists and wasn't processed in the first pass
            if os.path.exists(file_path) and filename not in processed_files:
                print(f"\nProcessing newly created {filename}...")
                if process_audio_file(filename):
                    fixed_count += 1
                    processed_files.add(filename)  # Mark as processed

    print_header("Audio Fixing Complete")
    # Report count based on successful processing attempts
    print(f"Attempted to fix/create {len(processed_files)} audio files")
    print("The menu music files should now be trimmed to their actual content length.")
    print("Please test the game again.")

    return 0

if __name__ == "__main__":
    main() 