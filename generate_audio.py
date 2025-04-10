import numpy as np
from scipy.io import wavfile
import os

# Create audio directory if it doesn't exist
os.makedirs("assets/audio", exist_ok=True)

# Sample rate
sample_rate = 44100  # 44.1 kHz

# Generate menu_select.wav (short beep)
def generate_menu_select():
    duration = 0.1  # 100 ms
    # Generate a higher frequency beep
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    note = np.sin(2 * np.pi * 880 * t) * 0.5  # A5 note
    
    # Apply fade out
    fade_out = np.linspace(1.0, 0.0, int(sample_rate * duration))
    note = note * fade_out
    
    # Convert to 16-bit PCM
    audio = np.int16(note * 32767)
    
    # Save as WAV
    wavfile.write("assets/audio/menu_select.wav", sample_rate, audio)
    print("Generated menu_select.wav")

# Generate menu_click.wav (click sound)
def generate_menu_click():
    duration = 0.15  # 150 ms
    # Generate a click-like sound
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # First part - higher pitch
    note1 = np.sin(2 * np.pi * 1200 * t) * 0.7
    # Second part - lower resonance
    note2 = np.sin(2 * np.pi * 600 * t) * 0.3
    
    note = note1 + note2
    
    # Apply quick fade out
    fade_out = np.exp(-5 * t)
    note = note * fade_out
    
    # Convert to 16-bit PCM
    audio = np.int16(note * 32767)
    
    # Save as WAV
    wavfile.write("assets/audio/menu_click.wav", sample_rate, audio)
    print("Generated menu_click.wav")

# Generate attack.wav (swoosh sound)
def generate_attack():
    duration = 0.3  # 300 ms
    # Generate a swoosh-like sound
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a frequency sweep (from high to low)
    freqs = np.linspace(1200, 400, int(sample_rate * duration))
    note = 0.6 * np.sin(2 * np.pi * np.cumsum(freqs) / sample_rate)
    
    # Add some noise for texture
    noise = np.random.normal(0, 0.2, int(sample_rate * duration))
    note = note + noise
    
    # Apply envelope
    attack = np.linspace(0, 1, int(sample_rate * 0.05))  # 50ms attack
    decay = np.linspace(1, 0, int(sample_rate * 0.25))   # 250ms decay
    envelope = np.concatenate((attack, decay))
    
    # Make sure envelope has same length as note
    if len(envelope) < len(note):
        envelope = np.pad(envelope, (0, len(note) - len(envelope)), mode='constant')
    else:
        envelope = envelope[:len(note)]
    
    # Apply envelope to note
    note = note * envelope
    
    # Convert to 16-bit PCM
    audio = np.int16(note * 32767)
    
    # Save as WAV
    wavfile.write("assets/audio/attack.wav", sample_rate, audio)
    print("Generated attack.wav")

# Generate simple background music
def generate_background_music(filename, duration=10.0, base_freq=220):
    # Create a simple looping melody
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Base melody using pentatonic scale
    scale = [0, 2, 4, 7, 9]  # Pentatonic scale intervals
    sequence = []
    
    # Create a simple sequence
    for i in range(int(duration * 2)):  # 2 notes per second
        note_idx = (i % len(scale))
        semitones = scale[note_idx]
        freq = base_freq * (2 ** (semitones / 12))
        sequence.append(freq)
    
    # Generate the waveform
    signal = np.zeros(int(sample_rate * duration))
    
    note_duration = 0.5  # half second per note
    for i, freq in enumerate(sequence):
        start_idx = int(i * note_duration * sample_rate)
        end_idx = int((i + 1) * note_duration * sample_rate)
        if end_idx > len(signal):
            break
            
        t_note = np.linspace(0, note_duration, end_idx - start_idx, False)
        # Main tone
        note = 0.4 * np.sin(2 * np.pi * freq * t_note)
        # Add some harmonics
        note += 0.2 * np.sin(2 * np.pi * freq * 2 * t_note)  # octave
        note += 0.1 * np.sin(2 * np.pi * freq * 3 * t_note)  # fifth above octave
        
        # Apply envelope
        env_attack = int(0.1 * (end_idx - start_idx))
        env_release = int(0.3 * (end_idx - start_idx))
        env = np.ones(end_idx - start_idx)
        env[:env_attack] = np.linspace(0, 1, env_attack)
        env[-env_release:] = np.linspace(1, 0, env_release)
        
        note = note * env
        signal[start_idx:end_idx] += note
    
    # Add a simple bass line
    for i in range(int(duration)):
        start_idx = int(i * sample_rate)
        end_idx = int((i + 1) * sample_rate)
        
        # Make sure we don't go out of bounds
        if end_idx > len(signal):
            end_idx = len(signal)
            
        t_bass = np.linspace(0, 1, end_idx - start_idx, False)
        bass_freq = base_freq / 2
        bass = 0.3 * np.sin(2 * np.pi * bass_freq * t_bass)
        
        # Create the envelope with the right length
        env_length = end_idx - start_idx
        attack_len = int(0.1 * env_length)
        sustain_len = int(0.2 * env_length)
        release_len = env_length - attack_len - sustain_len
        
        env = np.concatenate([
            np.linspace(0, 1, attack_len),
            np.ones(sustain_len),
            np.linspace(1, 0, release_len)
        ])
        
        # Apply envelope and add to signal
        signal[start_idx:end_idx] += bass * env
    
    # Normalize the signal
    signal = signal / np.max(np.abs(signal))
    
    # Convert to 16-bit PCM
    audio = np.int16(signal * 32767)
    
    # Save as WAV
    wavfile.write(f"assets/audio/{filename}", sample_rate, audio)
    print(f"Generated {filename}")

# Generate only the game theme since other files were created successfully
# generate_menu_select()
# generate_menu_click()
# generate_attack()
# generate_background_music("menu_theme.wav", duration=5.0, base_freq=220)  # A3
generate_background_music("game_theme.wav", duration=8.0, base_freq=196)  # G3

print("All audio files generated successfully!") 