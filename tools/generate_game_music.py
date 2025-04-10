import numpy as np
import wave
import struct
import math
import os
from pathlib import Path
import shutil

# Audio settings
SAMPLE_RATE = 44100  # CD quality
DURATION = 8.0  # 8 seconds per section (longer than menu music)
AMPLITUDE = 0.3  # Volume level (0.0 to 1.0)
CROSSFADE_DURATION = 0.15  # 150ms crossfade (slightly longer than menu music)

# Musical note frequencies (A4 = 440Hz standard pitch)
NOTES = {
    'A3': 220.00,  # Lower octave for more atmospheric sounds
    'B3': 246.94,
    'C4': 261.63,
    'D4': 293.66,
    'E4': 329.63,
    'F4': 349.23,
    'G4': 392.00,
    'A4': 440.00,
    'B4': 493.88,
    'C5': 523.25,
    'D5': 587.33,
    'E5': 659.25,
    'F5': 698.46,
    'G5': 783.99,
    'A5': 880.00
}

def apply_envelope(wave, attack=0.02, decay=0.1, sustain=0.8, release=0.15):
    """Apply ADSR envelope to shape the sound"""
    samples = len(wave)
    # Convert ratios to sample counts
    attack_samples = int(samples * attack)
    decay_samples = int(samples * decay)
    release_samples = int(samples * release)
    sustain_level = sustain
    
    # Create envelope
    envelope = np.ones(samples)
    
    # Attack phase - exponential curve for smoother onset
    if attack_samples > 0:
        attack_curve = np.linspace(0, 1, attack_samples)**0.5  # Square root for more natural attack
        envelope[:attack_samples] = attack_curve
    
    # Decay phase
    if decay_samples > 0:
        decay_curve = np.linspace(1, sustain_level, decay_samples)
        envelope[attack_samples:attack_samples + decay_samples] = decay_curve
    
    # Sustain phase is already set by the ones array
    sustain_start = attack_samples + decay_samples
    sustain_end = samples - release_samples
    envelope[sustain_start:sustain_end] = sustain_level
    
    # Release phase
    if release_samples > 0:
        release_curve = np.linspace(sustain_level, 0, release_samples)
        envelope[sustain_end:] = release_curve
    
    # Apply envelope
    return wave * envelope

def apply_section_envelope(wave):
    """Apply a gentle fade in/out to the entire section for seamless transitions"""
    samples = len(wave)
    crossfade_samples = int(CROSSFADE_DURATION * SAMPLE_RATE)
    
    # Create a full envelope with crossfades at start and end
    envelope = np.ones(samples)
    
    # Start crossfade using square root curve for natural fade
    if crossfade_samples > 0:
        fade_in = np.linspace(0, 1, crossfade_samples)**0.5
        envelope[:crossfade_samples] = fade_in
    
    # End crossfade
    if crossfade_samples > 0:
        fade_out = np.linspace(1, 0, crossfade_samples)**0.5
        envelope[-crossfade_samples:] = fade_out
    
    # Apply envelope
    return wave * envelope

def create_section(notes, note_duration=0.9, pattern_type='melodic'):
    """
    Create a section of audio based on notes and pattern type
    
    Parameters:
    - notes: List of note names to play
    - note_duration: Base duration of each note (in seconds)
    - pattern_type: Pattern style ('melodic', 'atmospheric', 'rhythmic')
    """
    # Initialize audio data
    total_samples = int(SAMPLE_RATE * DURATION)
    audio_data = np.zeros(total_samples)
    
    num_notes = len(notes)
    samples_per_note = int(SAMPLE_RATE * note_duration)
    
    # Different spacing based on pattern type
    if pattern_type == 'melodic':
        # Regular melodic pattern
        note_spacing = (total_samples - samples_per_note) // (num_notes - 1) if num_notes > 1 else 0
    elif pattern_type == 'atmospheric':
        # Overlapping notes for atmospheric feel
        note_spacing = int((total_samples - samples_per_note) // (num_notes * 0.7)) if num_notes > 1 else 0
    elif pattern_type == 'rhythmic':
        # More defined spacing for rhythmic feel
        note_spacing = int((total_samples - samples_per_note) // (num_notes * 1.2)) if num_notes > 1 else 0
    else:
        # Default spacing
        note_spacing = (total_samples - samples_per_note) // num_notes if num_notes > 0 else 0
    
    # Generate audio for each note
    for i, note in enumerate(notes):
        if note in NOTES:
            frequency = NOTES[note]
            # Calculate note start position
            start_pos = i * note_spacing
            
            # Ensure we don't go beyond the buffer
            if start_pos >= total_samples:
                break
                
            # Create time array for this note
            t = np.linspace(0, note_duration, samples_per_note, False)
            
            # Generate the note (sine wave)
            note_data = AMPLITUDE * np.sin(2 * np.pi * frequency * t)
            
            # Apply ADSR envelope to the note
            note_data = apply_envelope(
                note_data, 
                attack=0.03,     # 30ms attack
                decay=0.15,      # 150ms decay
                sustain=0.65,    # 65% sustain level
                release=0.25     # 250ms release
            )
            
            # Add the note to the audio data at the calculated position
            end_pos = min(start_pos + samples_per_note, total_samples)
            actual_note_samples = end_pos - start_pos
            audio_data[start_pos:end_pos] += note_data[:actual_note_samples]
    
    # Apply crossfade envelope to the entire section
    audio_data = apply_section_envelope(audio_data)
    
    # Normalize to prevent clipping
    max_amplitude = np.max(np.abs(audio_data))
    if max_amplitude > 0:
        # Leave some headroom (90% of maximum)
        audio_data = audio_data * 0.9 / max_amplitude
    
    return audio_data

def save_wave_file(filename, audio_data, notes=None):
    """Save audio data as a WAV file"""
    try:
        # First try to remove file if it exists and is not in use
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"Removed existing file: {filename}")
            except Exception as e:
                print(f"Warning: Could not remove existing file {filename}: {e}")
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Normalize data to 16-bit range and convert to integer
        audio_int = np.int16(audio_data * 32767)
        
        # Open the WAV file
        with wave.open(filename, 'w') as wav_file:
            # Set parameters
            nchannels = 1  # Mono
            sampwidth = 2  # 2 bytes (16 bits)
            framerate = SAMPLE_RATE
            nframes = len(audio_data)
            
            # Set WAV file parameters
            wav_file.setparams((nchannels, sampwidth, framerate, nframes, 'NONE', 'not compressed'))
            
            # Write audio data
            wav_file.writeframes(audio_int.tobytes())
        
        if notes:
            print(f"Created {os.path.basename(filename)} with notes: {', '.join(notes)}")
        else:
            print(f"Created {os.path.basename(filename)}")
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

def main():
    try:
        # Create audio directory if it doesn't exist
        script_dir = Path(__file__).resolve().parent
        audio_dir = script_dir.parent / "assets" / "audio"
        game_audio_dir = audio_dir / "game"
        game_audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Define melodies for each section with appropriate themes for adventure game
        sections = {
            # Exploration themes (peaceful, adventurous)
            'game_section1.wav': ['C4', 'E4', 'G4', 'C5', 'B4', 'G4', 'E4', 'C4'],  # Forest Exploration
            'game_section2.wav': ['E4', 'G4', 'B4', 'C5', 'D5', 'B4', 'G4', 'E4'],  # Village Theme
            
            # Mystery/Discovery themes
            'game_section3.wav': ['A3', 'E4', 'A4', 'C5', 'B4', 'A4', 'E4', 'A3'],  # Ancient Ruins
            'game_section4.wav': ['G3', 'B3', 'D4', 'G4', 'F4', 'D4', 'B3', 'G3'],  # Cave Discovery
            
            # Adventure/Journey themes
            'game_section5.wav': ['D4', 'A4', 'D5', 'C5', 'A4', 'F4', 'E4', 'D4'],  # Mountain Path
            'game_section6.wav': ['F4', 'A4', 'C5', 'F5', 'E5', 'C5', 'A4', 'F4'],  # Ocean Journey
            
            # Tension/Mystery themes
            'game_section7.wav': ['B3', 'D4', 'F4', 'A4', 'G4', 'F4', 'D4', 'B3'],  # Dark Forest
            'game_section8.wav': ['E4', 'G4', 'C5', 'B4', 'A4', 'G4', 'F4', 'E4'],  # Approaching Storm
            
            # Triumph/Resolution themes
            'game_section9.wav': ['C4', 'E4', 'G4', 'C5', 'E5', 'G5', 'E5', 'C5'],  # Victory Fanfare
            'game_section10.wav': ['G3', 'B3', 'D4', 'G4', 'B4', 'D5', 'B4', 'G4']  # Quest Completion
        }
        
        # Pattern types for different musical feels
        patterns = {
            'game_section1.wav': 'melodic',     # Regular melodic pattern
            'game_section2.wav': 'melodic',
            'game_section3.wav': 'atmospheric', # Overlapping notes for ambient feel
            'game_section4.wav': 'atmospheric',
            'game_section5.wav': 'melodic',
            'game_section6.wav': 'melodic',
            'game_section7.wav': 'atmospheric',
            'game_section8.wav': 'atmospheric',
            'game_section9.wav': 'rhythmic',    # Distinct notes for triumph themes
            'game_section10.wav': 'rhythmic'
        }
        
        print("\n=== Generating Game Music Sections ===\n")
        
        success_count = 0
        total_sections = len(sections)
        
        for filename, notes in sections.items():
            # Get the pattern type for this section
            pattern = patterns.get(filename, 'melodic')
            
            # Set note duration based on pattern type
            if pattern == 'atmospheric':
                note_duration = 1.2    # Longer notes for atmospheric sections
            elif pattern == 'rhythmic':
                note_duration = 0.7    # Shorter notes for rhythmic sections
            else:
                note_duration = 0.9    # Default for melodic sections
                
            # Generate audio data
            audio_data = create_section(notes, note_duration=note_duration, pattern_type=pattern)
            
            # Save to WAV file
            full_path = game_audio_dir / filename
            if save_wave_file(str(full_path), audio_data, notes):
                success_count += 1
        
        # Display summary
        print(f"\nSuccessfully generated {success_count} of {total_sections} audio files.")
        if success_count == total_sections:
            print("All game music sections have been generated!")
            print(f"Each section is exactly {DURATION} seconds long with various musical patterns.")
            print(f"Files include {CROSSFADE_DURATION*1000}ms crossfades for smooth transitions.")
            print(f"The files have been saved in the {game_audio_dir} directory.")
        else:
            print(f"Warning: {total_sections - success_count} files could not be generated.")
            print("Check the error messages above for details.")
            
        # Create a combined game theme from all sections
        print("\nCreating combined game theme from all sections...")
        
        # First check if all sections were created successfully
        if success_count == total_sections:
            try:
                # Combined audio data will be 10 sections long
                combined_length = int(SAMPLE_RATE * DURATION * total_sections)
                combined_audio = np.zeros(combined_length)
                
                # Add each section to the combined audio
                for i, filename in enumerate(sections.keys()):
                    file_path = game_audio_dir / filename
                    with wave.open(str(file_path), 'rb') as wav_file:
                        # Read audio data
                        n_frames = wav_file.getnframes()
                        frame_data = wav_file.readframes(n_frames)
                        
                        # Convert to numpy array
                        section_audio = np.frombuffer(frame_data, dtype=np.int16) / 32767.0
                        
                        # Calculate position in combined audio
                        start_pos = i * int(SAMPLE_RATE * DURATION)
                        end_pos = start_pos + len(section_audio)
                        
                        # Add to combined audio
                        combined_audio[start_pos:end_pos] += section_audio
                
                # Normalize combined audio
                max_amplitude = np.max(np.abs(combined_audio))
                if max_amplitude > 0:
                    combined_audio = combined_audio * 0.9 / max_amplitude
                
                # Save combined audio as game_theme.wav
                combined_path = audio_dir / "game_theme.wav"
                if save_wave_file(str(combined_path), combined_audio, notes=None):
                    print(f"Successfully created combined game theme: {combined_path}")
                    
                    # Also create enhanced_game_theme.wav as a copy for compatibility
                    enhanced_path = audio_dir / "enhanced_game_theme.wav"
                    shutil.copy(str(combined_path), str(enhanced_path))
                    print(f"Created enhanced game theme copy: {enhanced_path}")
            except Exception as e:
                print(f"Error creating combined game theme: {e}")
        
        return success_count == total_sections
    
    except Exception as e:
        print(f"Error in main function: {e}")
        return False

if __name__ == "__main__":
    main() 