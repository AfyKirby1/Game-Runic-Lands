#!/usr/bin/env python3
"""
Unified Audio Manager for Runic Lands - FIXED VERSION
Consolidates audio generation, checking, and fixing functionality
"""

import os
import sys
import json
import wave
import numpy as np
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse

# Audio directory path - get project root first
project_root = Path(__file__).parent.parent
AUDIO_DIR = project_root / "assets" / "audio"

class AudioManager:
    """
    Manages all audio-related tasks for the Runic Lands project.

    This class handles the generation, validation, analysis, and backup of
    all audio assets, including sound effects and music.
    """
    
    def __init__(self, audio_dir: Path = None):
        """
        Initializes the AudioManager.

        Args:
            audio_dir (Path, optional): The path to the main audio directory.
                                        If None, a default path is used.
                                        Defaults to None.
        """
        self.audio_dir = audio_dir or AUDIO_DIR
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Required audio files
        self.required_files = {
            "menu_click.wav": "Menu click sound effect",
            "menu_select.wav": "Menu select sound effect", 
            "attack.wav": "Player attack sound effect",
            "menu_theme.wav": "Main menu music (fallback)",
        }
        
        # Menu music sections
        self.menu_sections = {f"menu_section{i}.wav": f"Menu music section {i}" 
                             for i in range(1, 11)}
        
        # Game music sections  
        self.game_sections = {f"game_section{i}.wav": f"Game music section {i}"
                             for i in range(1, 11)}
        
        self.required_files.update(self.menu_sections)
        self.required_files.update(self.game_sections)

    def print_header(self, title: str):
        """
        Prints a formatted header to the console.

        Args:
            title (str): The title to display.
        """
        print(f"\n{'='*50}")
        print(f" {title}")
        print(f"{'='*50}")

    def check_files(self) -> Dict[str, bool]:
        """
        Checks for the existence of all required audio files.

        Returns:
            Dict[str, bool]: A dictionary mapping filenames to a boolean
                             indicating if the file exists.
        """
        self.print_header("Checking Audio Files")
        
        status = {}
        missing_files = []
        
        for filename, description in self.required_files.items():
            if filename.startswith("menu_section"):
                path = self.audio_dir / "menu" / filename
            elif filename.startswith("game_section"):
                path = self.audio_dir / "game" / filename
            else:
                path = self.audio_dir / filename
            exists = path.exists()
            status[filename] = exists
            
            if exists:
                print(f"✓ {filename}: Found ({description})")
            else:
                print(f"✗ {filename}: MISSING ({description})")
                missing_files.append(filename)
        
        if missing_files:
            print(f"\n⚠️  {len(missing_files)} files are missing")
        else:
            print(f"\n✅ All {len(self.required_files)} audio files found!")
            
        return status

    def analyze_files(self) -> Dict[str, Dict]:
        """
        Analyzes the properties of all existing required audio files.

        This reads each audio file to extract metadata like duration,
        sample rate, channels, and file size.

        Returns:
            Dict[str, Dict]: A dictionary where keys are filenames and
                             values are dictionaries of audio properties.
        """
        self.print_header("Analyzing Audio Files")
        
        analyses = {}
        
        for filename in self.required_files.keys():
            if filename.startswith("menu_section"):
                path = self.audio_dir / "menu" / filename
            elif filename.startswith("game_section"):
                path = self.audio_dir / "game" / filename
            else:
                path = self.audio_dir / filename
            if not path.exists():
                continue
                
            try:
                with wave.open(str(path), 'rb') as w:
                    frames = w.getnframes()
                    rate = w.getframerate()
                    channels = w.getnchannels()
                    sampwidth = w.getsampwidth()
                    duration = frames / rate
                    
                    analyses[filename] = {
                        'duration': duration,
                        'frames': frames,
                        'rate': rate,
                        'channels': channels,
                        'sampwidth': sampwidth,
                        'size_bytes': path.stat().st_size
                    }
                    
                    print(f"📊 {filename}:")
                    print(f"   Duration: {duration:.2f}s")
                    print(f"   Rate: {rate} Hz")
                    print(f"   Channels: {channels}")
                    print(f"   Size: {path.stat().st_size} bytes")
                    
            except Exception as e:
                print(f"❌ Error analyzing {filename}: {e}")
                
        return analyses

    def generate_menu_music(self, force: bool = False) -> bool:
        """
        Generates all 10 sections of the main menu music.

        Each section is a unique melodic pattern. These are saved in the
        'assets/audio/menu' directory.

        Args:
            force (bool, optional): If True, existing files will be
                                    overwritten. Defaults to False.

        Returns:
            bool: True if all sections were generated successfully,
                  False otherwise.
        """
        self.print_header("Generating Menu Music")
        
        # Create menu subdirectory
        menu_dir = self.audio_dir / "menu"
        menu_dir.mkdir(exist_ok=True)
        
        # Musical note frequencies (in Hz)
        notes = {
            'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
            'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25,
            'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99
        }
        
        # Define musical sections with different note patterns
        sections = {
            "menu_section1.wav": ['C4', 'E4', 'G4', 'C5', 'G4', 'E4', 'C4', 'G4'],  # Heroic
            "menu_section2.wav": ['F4', 'A4', 'C5', 'F4', 'A4', 'C5', 'A4', 'F4'],  # Calm
            "menu_section3.wav": ['G4', 'B4', 'D5', 'G5', 'D5', 'B4', 'G4', 'D5'],  # Energetic
            "menu_section4.wav": ['A4', 'C5', 'E5', 'A4', 'E5', 'C5', 'A4', 'C5'],  # Resolving
            "menu_section5.wav": ['D4', 'F4', 'A4', 'D5', 'A4', 'F4', 'D4', 'A4'],  # Misty
            "menu_section6.wav": ['E4', 'G4', 'B4', 'E5', 'B4', 'G4', 'E4', 'B4'],  # Descending
            "menu_section7.wav": ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5'],  # Wave
            "menu_section8.wav": ['C5', 'B4', 'A4', 'G4', 'F4', 'E4', 'D4', 'C4'],  # Cascading
            "menu_section9.wav": ['G4', 'G4', 'A4', 'A4', 'B4', 'B4', 'C5', 'C5'],  # Mountain
            "menu_section10.wav": ['F4', 'G4', 'A4', 'F4', 'G4', 'A4', 'G4', 'F4'], # Wandering
        }
        
        success_count = 0
        
        for filename, note_sequence in sections.items():
            filepath = menu_dir / filename
            
            if filepath.exists() and not force:
                print(f"⏭️  Skipping {filename} (already exists)")
                success_count += 1
                continue
                
            try:
                # Create the audio data
                audio_data = self._create_musical_section(note_sequence, notes)
                
                # Save to file
                if self._save_wave_file(audio_data, filepath):
                    print(f"✅ Created {filename} with notes: {', '.join(note_sequence)}")
                    success_count += 1
                else:
                    print(f"❌ Failed to save {filename}")
                    
            except Exception as e:
                print(f"❌ Error creating {filename}: {e}")
        
        print(f"\n📊 Generated {success_count}/{len(sections)} menu music files")
        return success_count == len(sections)

    def generate_game_music(self, force: bool = False) -> bool:
        """
        Generates all 10 sections of the in-game music.

        These sections are more atmospheric than the menu music and are saved
        in the 'assets/audio/game' directory.

        Args:
            force (bool, optional): If True, existing files will be
                                    overwritten. Defaults to False.

        Returns:
            bool: True if all sections were generated successfully,
                  False otherwise.
        """
        self.print_header("Generating Game Music")
        
        # Create game subdirectory
        game_dir = self.audio_dir / "game"
        game_dir.mkdir(exist_ok=True)
        
        # Game music uses different patterns - more atmospheric
        notes = {
            'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61,
            'G3': 196.00, 'A3': 220.00, 'B3': 246.94, 'C4': 261.63,
            'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00
        }
        
        # Game sections - more atmospheric and longer patterns
        sections = {
            "game_section1.wav": ['C3', 'G3', 'C4', 'E4', 'G3', 'C3', 'E4', 'C4'],
            "game_section2.wav": ['D3', 'A3', 'D4', 'F4', 'A3', 'D3', 'F4', 'D4'],
            "game_section3.wav": ['E3', 'B3', 'E4', 'G4', 'B3', 'E3', 'G4', 'E4'],
            "game_section4.wav": ['F3', 'C4', 'F4', 'A3', 'C4', 'F3', 'A3', 'F4'],
            "game_section5.wav": ['G3', 'D4', 'G4', 'B3', 'D4', 'G3', 'B3', 'G4'],
            "game_section6.wav": ['A3', 'E4', 'A3', 'C4', 'E4', 'A3', 'C4', 'E4'],
            "game_section7.wav": ['B3', 'F4', 'B3', 'D4', 'F4', 'B3', 'D4', 'F4'],
            "game_section8.wav": ['C4', 'G3', 'C4', 'E3', 'G3', 'C4', 'E3', 'G3'],
            "game_section9.wav": ['D4', 'A3', 'D4', 'F3', 'A3', 'D4', 'F3', 'A3'],
            "game_section10.wav": ['E4', 'B3', 'E4', 'G3', 'B3', 'E4', 'G3', 'B3'],
        }
        
        success_count = 0
        
        for filename, note_sequence in sections.items():
            filepath = game_dir / filename
            
            if filepath.exists() and not force:
                print(f"⏭️  Skipping {filename} (already exists)")
                success_count += 1
                continue
                
            try:
                # Create the audio data  
                audio_data = self._create_musical_section(note_sequence, notes, duration=3.0)
                
                # Save to file
                if self._save_wave_file(audio_data, filepath):
                    print(f"✅ Created {filename} with notes: {', '.join(note_sequence)}")
                    success_count += 1
                else:
                    print(f"❌ Failed to save {filename}")
                    
            except Exception as e:
                print(f"❌ Error creating {filename}: {e}")
        
        print(f"\n📊 Generated {success_count}/{len(sections)} game music files")
        return success_count == len(sections)

    def generate_sound_effects(self, force: bool = False) -> bool:
        """
        Generates the basic sound effects for the game.

        This includes sounds for menu interactions and combat.

        Args:
            force (bool, optional): If True, existing files will be
                                    overwritten. Defaults to False.

        Returns:
            bool: True if all sound effects were generated successfully,
                  False otherwise.
        """
        self.print_header("Generating Sound Effects")
        
        effects = {
            'menu_click.wav': self._create_click_sound,
            'menu_select.wav': self._create_select_sound,
            'attack.wav': self._create_attack_sound,
        }
        
        success_count = 0
        
        for filename, generator_func in effects.items():
            filepath = self.audio_dir / filename
            
            if filepath.exists() and not force:
                print(f"⏭️  Skipping {filename} (already exists)")
                success_count += 1
                continue
                
            try:
                audio_data = generator_func()
                if self._save_wave_file(audio_data, filepath):
                    print(f"✅ Generated {filename}")
                    success_count += 1
                else:
                    print(f"❌ Failed to save {filename}")
                    
            except Exception as e:
                print(f"❌ Error generating {filename}: {e}")
        
        print(f"\n📊 Generated {success_count}/{len(effects)} sound effects")
        return success_count == len(effects)

    def _create_musical_section(self, note_sequence: List[str], notes: Dict[str, float], 
                               duration: float = 2.0) -> np.ndarray:
        """
        Creates a NumPy array of audio data from a sequence of musical notes.

        Args:
            note_sequence (List[str]): A list of note names (e.g., ['C4', 'E4']).
            notes (Dict[str, float]): A dictionary mapping note names to frequencies.
            duration (float, optional): The total duration of the audio clip in seconds.
                                        Defaults to 2.0.

        Returns:
            np.ndarray: A 1D NumPy array containing the generated audio waveform.
        """
        sample_rate = 44100
        total_samples = int(sample_rate * duration)
        audio_data = np.zeros(total_samples)
        
        note_duration = duration / len(note_sequence)
        samples_per_note = int(sample_rate * note_duration)
        
        for i, note in enumerate(note_sequence):
            if note in notes:
                freq = notes[note]
                start_sample = i * samples_per_note
                end_sample = min(start_sample + samples_per_note, total_samples)
                
                # Generate note samples
                t = np.linspace(0, note_duration, end_sample - start_sample, False)
                note_wave = np.sin(2 * np.pi * freq * t) * 0.3
                
                # Add some harmonics for richer sound
                note_wave += np.sin(2 * np.pi * freq * 2 * t) * 0.1
                note_wave += np.sin(2 * np.pi * freq * 0.5 * t) * 0.05
                
                # Apply envelope (fade in/out)
                envelope = np.ones_like(note_wave)
                fade_samples = len(note_wave) // 10
                if fade_samples > 0:
                    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
                    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
                
                note_wave *= envelope
                audio_data[start_sample:end_sample] += note_wave
        
        return audio_data

    def _create_click_sound(self) -> np.ndarray:
        """
        Generates a short, high-frequency click sound.

        Returns:
            np.ndarray: A 1D NumPy array of the click sound waveform.
        """
        sample_rate = 44100
        duration = 0.1
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Quick click with high frequency
        click = np.sin(2 * np.pi * 1200 * t) * 0.5
        click += np.sin(2 * np.pi * 2400 * t) * 0.2
        
        # Apply quick fade out
        fade = np.exp(-20 * t)
        return click * fade

    def _create_select_sound(self) -> np.ndarray:
        """
        Generates a rising tone sound for selection confirmation.

        Returns:
            np.ndarray: A 1D NumPy array of the selection sound waveform.
        """
        sample_rate = 44100
        duration = 0.2
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Rising tone
        freq_start = 440
        freq_end = 880
        freq = freq_start + (freq_end - freq_start) * t / duration
        
        select = np.sin(2 * np.pi * freq * t) * 0.4
        
        # Apply envelope
        envelope = np.exp(-3 * t)
        return select * envelope

    def _create_attack_sound(self) -> np.ndarray:
        """
        Generates a 'swish' sound for a player attack.

        This is created using filtered white noise.

        Returns:
            np.ndarray: A 1D NumPy array of the attack sound waveform.
        """
        sample_rate = 44100
        duration = 0.3
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Sword swish sound - noise with filtering
        noise = np.random.normal(0, 0.3, len(t))
        
        # Apply frequency filtering (simple low-pass)
        for i in range(1, len(noise)):
            noise[i] = 0.7 * noise[i] + 0.3 * noise[i-1]
        
        # Apply envelope for swish effect
        envelope = np.exp(-5 * t) * (1 - t/duration)
        return noise * envelope

    def _save_wave_file(self, audio_data: np.ndarray, filepath: Path, 
                       sample_rate: int = 44100) -> bool:
        """
        Saves a NumPy array of audio data to a .wav file.

        Args:
            audio_data (np.ndarray): The audio waveform to save.
            filepath (Path): The path to the output .wav file.
            sample_rate (int, optional): The sample rate of the audio.
                                         Defaults to 44100.

        Returns:
            bool: True if the file was saved successfully, False otherwise.
        """
        try:
            # Convert to 16-bit PCM
            audio_16bit = np.int16(audio_data * 32767)
            
            with wave.open(str(filepath), 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_16bit.tobytes())
            
            return True
            
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
            return False

    def backup_files(self) -> bool:
        """
        Creates a backup of all existing required audio files.

        Backups are stored in the 'assets/audio/backups' directory with a
        '.backup' extension.

        Returns:
            bool: True if at least one file was backed up, False otherwise.
        """
        self.print_header("Creating Backups")
        
        backup_dir = self.audio_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        backed_up = 0
        
        for filename in self.required_files.keys():
            source = self.audio_dir / filename
            backup = backup_dir / f"{filename}.backup"
            
            if source.exists() and not backup.exists():
                try:
                    shutil.copy2(source, backup)
                    print(f"📦 Backed up {filename}")
                    backed_up += 1
                except Exception as e:
                    print(f"❌ Failed to backup {filename}: {e}")
        
        print(f"\n📊 Created {backed_up} backups")
        return backed_up > 0

    def restore_backups(self) -> bool:
        """
        Restores all audio files from the backup directory.

        This overwrites existing audio files with their backed-up versions.

        Returns:
            bool: True if at least one file was restored, False otherwise.
        """
        self.print_header("Restoring from Backups")
        
        backup_dir = self.audio_dir / "backups"
        if not backup_dir.exists():
            print("❌ No backup directory found")
            return False
        
        restored = 0
        
        for backup_file in backup_dir.glob("*.backup"):
            original_name = backup_file.stem  # Remove .backup extension
            original_path = self.audio_dir / original_name
            
            try:
                shutil.copy2(backup_file, original_path)
                print(f"📥 Restored {original_name}")
                restored += 1
            except Exception as e:
                print(f"❌ Failed to restore {original_name}: {e}")
        
        print(f"\n📊 Restored {restored} files")
        return restored > 0

    def generate_all_missing(self, force: bool = False) -> bool:
        """
        A convenience method to generate all missing audio files at once.

        This calls the individual generator methods for sound effects, menu
        music, and game music.

        Args:
            force (bool, optional): If True, existing files will be
                                    overwritten. Defaults to False.

        Returns:
            bool: True if all generation steps were successful, False otherwise.
        """
        self.print_header("Generating All Missing Audio")
        
        success = True
        success &= self.generate_sound_effects(force)
        success &= self.generate_menu_music(force) 
        success &= self.generate_game_music(force)
        
        return success

def main():
    """
    The main command-line interface for the AudioManager script.

    Provides arguments to check, analyze, generate, backup, and restore
    audio files for the Runic Lands project.
    """
    parser = argparse.ArgumentParser(description="Runic Lands Audio Manager")
    parser.add_argument("--check", action="store_true", help="Check which files exist")
    parser.add_argument("--analyze", action="store_true", help="Analyze audio file properties")
    parser.add_argument("--generate-menu", action="store_true", help="Generate menu music")
    parser.add_argument("--generate-game", action="store_true", help="Generate game music")
    parser.add_argument("--generate-sfx", action="store_true", help="Generate sound effects")
    parser.add_argument("--generate-all", action="store_true", help="Generate all missing audio")
    parser.add_argument("--backup", action="store_true", help="Backup existing files")
    parser.add_argument("--restore", action="store_true", help="Restore from backups")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--audio-dir", type=Path, help="Audio directory path")
    
    args = parser.parse_args()
    
    # Initialize audio manager
    audio_manager = AudioManager(args.audio_dir)
    
    print("🎵 Runic Lands Audio Manager")
    print("="*50)
    
    if args.check or not any(vars(args).values()):
        audio_manager.check_files()
    
    if args.analyze:
        audio_manager.analyze_files()
    
    if args.backup:
        audio_manager.backup_files()
    
    if args.restore:
        audio_manager.restore_backups()
    
    if args.generate_menu or args.generate_all:
        audio_manager.generate_menu_music(args.force)
    
    if args.generate_game or args.generate_all:
        audio_manager.generate_game_music(args.force)
    
    if args.generate_sfx or args.generate_all:
        audio_manager.generate_sound_effects(args.force)
    
    if args.generate_all:
        audio_manager.generate_all_missing(args.force)
    
    print("\n✅ Audio management complete!")

if __name__ == "__main__":
    main() 