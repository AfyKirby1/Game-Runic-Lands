#!/usr/bin/env python3
"""
Menu Music Generator for Runic Lands

This script generates new menu music sections using synthesized notes.
Each section will have a unique melody while maintaining a consistent theme.
"""

import numpy as np
import wave
import os
from pathlib import Path

# Audio settings
SAMPLE_RATE = 44100  # Standard CD quality
DURATION = 2.0  # Each section will be 2 seconds long
AMPLITUDE = 0.3  # Volume level (0.0 to 1.0)
CROSSFADE_DURATION = 0.1  # 100ms crossfade at start/end

# Note frequencies (A4 = 440Hz and related notes)
NOTES = {
    'A4': 440.0,
    'B4': 493.88,
    'C5': 523.25,
    'D5': 587.33,
    'E5': 659.25,
    'F5': 698.46,
    'G5': 783.99,
    'A5': 880.0
}

def generate_sine_wave(frequency, duration, amplitude=1.0, sample_rate=44100):
    """Generate a sine wave for a musical note."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave

def apply_envelope(wave, attack=0.02, decay=0.1, sustain=0.8, release=0.15):
    """Apply ADSR envelope to a wave."""
    total_length = len(wave)
    attack_length = int(attack * total_length)
    decay_length = int(decay * total_length)
    release_length = int(release * total_length)
    
    envelope = np.ones(total_length)
    # Attack (smoother curve using square root)
    envelope[:attack_length] = np.sqrt(np.linspace(0, 1, attack_length))
    # Decay (exponential curve)
    decay_curve = np.exp(-3 * np.linspace(0, 1, decay_length))
    decay_curve = decay_curve * (1 - sustain) + sustain
    envelope[attack_length:attack_length+decay_length] = decay_curve
    # Sustain
    envelope[attack_length+decay_length:-release_length] = sustain
    # Release (exponential fade)
    release_curve = np.exp(-3 * np.linspace(0, 1, release_length))
    envelope[-release_length:] = sustain * release_curve
    
    return wave * envelope

def apply_section_envelope(wave, crossfade_samples):
    """Apply smooth fade in/out for the entire section."""
    fade_in = np.sqrt(np.linspace(0, 1, crossfade_samples))
    fade_out = np.sqrt(np.linspace(1, 0, crossfade_samples))
    
    # Apply fade in
    wave[:crossfade_samples] *= fade_in
    # Apply fade out
    wave[-crossfade_samples:] *= fade_out
    
    return wave

def create_note(frequency, duration, amplitude=AMPLITUDE):
    """Create a musical note with envelope."""
    wave = generate_sine_wave(frequency, duration, amplitude)
    return apply_envelope(wave)

def create_section(notes, note_duration=0.22):  # Slightly shorter notes for better spacing
    """Create a section of music with the given notes."""
    waves = []
    num_notes = len(notes)
    if num_notes == 0:
        # Return silence if no notes are provided
        return np.zeros(int(DURATION * SAMPLE_RATE))

    # Calculate usable duration, excluding crossfade time at start/end
    usable_duration = DURATION - (2 * CROSSFADE_DURATION)
    if usable_duration <= 0:
        raise ValueError("Crossfade duration cannot exceed half the total duration.")

    # Total time strictly occupied by the notes themselves
    total_notes_duration = num_notes * note_duration

    # Check if notes fit within the usable duration
    if total_notes_duration > usable_duration:
        # If notes are too long, adjust note_duration proportionally
        original_note_duration = note_duration
        note_duration = usable_duration / num_notes
        print(f"Warning: Original note duration ({original_note_duration:.3f}s) too long for usable section duration ({usable_duration:.3f}s). Adjusted note duration to {note_duration:.3f}s.")
        total_notes_duration = usable_duration # Reset total note time based on new duration
        total_gap_time = 0 # No time left for gaps
    else:
        # Calculate total time available for gaps between notes
        total_gap_time = usable_duration - total_notes_duration

    # Calculate the duration and sample count for each individual gap
    num_gaps = num_notes - 1
    gap_duration = total_gap_time / num_gaps if num_gaps > 0 else 0
    # Ensure gap samples isn't negative (shouldn't happen with check above, but safety first)
    gap_samples = max(0, int(gap_duration * SAMPLE_RATE))

    # Generate notes and append gaps
    for i, note in enumerate(notes):
        # Create the note using the potentially adjusted duration
        wave = create_note(NOTES[note], note_duration)
        waves.append(wave)

        # Add calculated gap (except after last note)
        if i < num_notes - 1:
            if gap_samples > 0:
                gap = np.zeros(gap_samples)
                waves.append(gap)

    # Combine all waves (notes and calculated gaps)
    combined = np.concatenate(waves)

    # Ensure exact total duration by padding or truncating
    desired_length = int(DURATION * SAMPLE_RATE)
    current_length = len(combined)

    if current_length < desired_length:
        # Pad with silence at the end if needed
        padding = np.zeros(desired_length - current_length)
        combined = np.concatenate([combined, padding])
    elif current_length > desired_length:
        # Truncate if slightly too long (should be rare with calculations above)
        combined = combined[:desired_length]

    # Apply section-wide envelope for smooth start/end transitions
    crossfade_samples = int(CROSSFADE_DURATION * SAMPLE_RATE)
    combined = apply_section_envelope(combined, crossfade_samples)

    return combined

def save_wave_file(data, filename, sample_rate=SAMPLE_RATE):
    """Save audio data as a WAV file."""
    try:
        # Normalize to prevent clipping
        max_val = np.max(np.abs(data))
        if max_val > 0:
            data = data / max_val * 0.95  # Leave a little headroom
        
        # Scale to 16-bit range and convert to integer
        scaled = np.int16(data * 32767)
        
        # Make sure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # If file exists, try to remove it first
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as e:
                print(f"Warning: Could not remove existing file {filename}: {e}")
        
        # Write the new file
        wav_file = wave.open(filename, 'wb')
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(scaled.tobytes())
        wav_file.close()
        
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

def main():
    try:
        # Create audio directory if it doesn't exist
        script_dir = Path(__file__).resolve().parent
        audio_dir = script_dir.parent / "assets" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Define melodies for each section
        sections = {
            # Original sections
            'menu_section1.wav': ['C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B4', 'C5'],  # Ascending
            'menu_section2.wav': ['C5', 'E5', 'G5', 'C5', 'E5', 'G5', 'B4', 'C5'],  # Arpeggios
            'menu_section3.wav': ['A5', 'G5', 'F5', 'E5', 'D5', 'C5', 'B4', 'A4'],  # Descending
            'menu_section4.wav': ['C5', 'B4', 'C5', 'E5', 'G5', 'E5', 'C5', 'B4'],  # Melodic
            'menu_section5.wav': ['E5', 'C5', 'D5', 'B4', 'C5', 'A4', 'B4', 'C5'],  # Complex
            
            # New sections
            'menu_section6.wav': ['C5', 'E5', 'G5', 'C5', 'B4', 'G5', 'E5', 'C5'],  # Descending arpeggio
            'menu_section7.wav': ['E5', 'D5', 'C5', 'B4', 'C5', 'D5', 'E5', 'F5'],  # Wave pattern
            'menu_section8.wav': ['G5', 'E5', 'C5', 'G5', 'F5', 'D5', 'B4', 'G5'],  # Cascading
            'menu_section9.wav': ['A4', 'C5', 'E5', 'A5', 'E5', 'C5', 'B4', 'A4'],  # Mountain
            'menu_section10.wav': ['D5', 'G5', 'F5', 'D5', 'E5', 'C5', 'B4', 'G5']  # Wandering
        }
        
        print("\n=== Generating Menu Music Sections ===\n")
        
        success_count = 0
        for filename, notes in sections.items():
            filepath = audio_dir / filename
            try:
                # Create the audio data
                audio_data = create_section(notes)
                # Save to file
                if save_wave_file(audio_data, str(filepath)):
                    print(f"Created {filename} with notes: {', '.join(notes)}")
                    success_count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        
        print(f"\nSuccessfully generated {success_count} of {len(sections)} audio files.")
        if success_count == len(sections):
            print("All menu music sections have been generated!")
            print("Each section is exactly 2 seconds long with 8 distinct notes.")
            print("Files include 100ms crossfades for smooth transitions.")
            print("The files have been saved in the assets/audio directory.")
        else:
            print("Warning: Some files could not be generated. Please check the errors above.")
        
        return 0 if success_count == len(sections) else 1
    
    except Exception as e:
        print(f"\nError: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 