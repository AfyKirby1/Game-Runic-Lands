"""
Asset Generator Utilities
This module provides functions to generate game assets programmatically.
"""

import os
import numpy as np
from PIL import Image
from scipy.io import wavfile
from typing import Dict, Tuple, List

# Color palette based on documentation
COLORS = {
    "skin_base": (224, 176, 136, 255),  # #E0B088
    "skin_shadow": (198, 156, 123, 255),  # #C69C7B
    "hair_base": (74, 74, 74, 255),  # #4A4A4A
    "hair_shadow": (51, 51, 51, 255),  # #333333
    "shirt_base": (139, 69, 19, 255),  # #8B4513
    "shirt_shadow": (101, 67, 33, 255),  # #654321
    "pants_base": (105, 105, 105, 255),  # #696969
    "pants_shadow": (74, 74, 74, 255),  # #4A4A4A
    "boots_base": (139, 69, 19, 255),  # #8B4513
    "boots_shadow": (101, 67, 33, 255),  # #654321
    "metal": (192, 192, 192, 255),  # #C0C0C0
    "metal_shadow": (128, 128, 128, 255),  # #808080
}

# Audio sample rate
SAMPLE_RATE = 44100  # 44.1 kHz

def ensure_directory(path: str):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)

# Sprite Generation Functions
def generate_base_character(output_dir: str = "assets/sprites/characters/player/png"):
    """Generate the base character sprite with layered approach"""
    ensure_directory(output_dir)
    
    # Base sprite size
    width, height = 32, 32
    
    # Create images for different layers
    base_body = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    base_clothing = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    combined = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    # Head
    for x in range(12, 20):
        for y in range(4, 6):
            base_clothing.putpixel((x, y), COLORS["hair_base"])
        for y in range(6, 8):
            base_clothing.putpixel((x, y), COLORS["hair_shadow"])
    
    # Face
    for x in range(12, 20):
        for y in range(8, 12):
            base_body.putpixel((x, y), COLORS["skin_base"])
    
    # Torso
    for x in range(10, 22):
        for y in range(12, 16):
            base_clothing.putpixel((x, y), COLORS["shirt_base"])
        for y in range(16, 20):
            base_clothing.putpixel((x, y), COLORS["shirt_shadow"])
    
    # Arms
    for x in range(8, 10):  # Left arm
        for y in range(12, 24):
            base_clothing.putpixel((x, y), COLORS["shirt_base"])
            
    for x in range(22, 24):  # Right arm
        for y in range(12, 24):
            base_clothing.putpixel((x, y), COLORS["shirt_base"])
    
    # Hands
    for x in range(8, 10):  # Left hand
        for y in range(24, 28):
            base_body.putpixel((x, y), COLORS["skin_base"])
            
    for x in range(22, 24):  # Right hand
        for y in range(24, 28):
            base_body.putpixel((x, y), COLORS["skin_base"])
    
    # Legs
    for x in range(12, 16):  # Left leg
        for y in range(20, 28):
            base_clothing.putpixel((x, y), COLORS["pants_base"])
            
    for x in range(16, 20):  # Right leg
        for y in range(20, 28):
            base_clothing.putpixel((x, y), COLORS["pants_base"])
    
    # Feet
    for x in range(12, 16):  # Left foot
        for y in range(28, 32):
            base_clothing.putpixel((x, y), COLORS["boots_base"])
            
    for x in range(16, 20):  # Right foot
        for y in range(28, 32):
            base_clothing.putpixel((x, y), COLORS["boots_base"])
    
    # Combine layers
    combined = Image.alpha_composite(combined, base_body)
    combined = Image.alpha_composite(combined, base_clothing)
    
    # Save the images
    base_body.save(f"{output_dir}/base_body.png")
    base_clothing.save(f"{output_dir}/base_clothing.png")
    combined.save(f"{output_dir}/base_wanderer.png")
    
    return combined

def generate_idle_animation(base_sprite: Image.Image, output_dir: str = "assets/sprites/characters/player/png"):
    """Generate idle animation frames for the character"""
    width, height = base_sprite.size
    
    # Create the sprite sheet with idle animation frames (4 frames)
    sprite_sheet = Image.new("RGBA", (width * 4, height), (0, 0, 0, 0))
    
    # Create 4 slightly different frames for idle animation
    frames = []
    frames.append(base_sprite)  # Frame 1: Original
    
    # Frame 2: Subtle breathing (shoulders slightly up)
    frame2 = base_sprite.copy()
    for x in range(10, 22):
        for y in range(12, 16):
            if y > 12 and frame2.getpixel((x, y))[3] > 0:
                pixel = frame2.getpixel((x, y-1))
                frame2.putpixel((x, y-1), pixel)
    frames.append(frame2)
    
    # Frame 3: Same as frame 1
    frames.append(base_sprite.copy())
    
    # Frame 4: Subtle breathing (shoulders slightly down)
    frame4 = base_sprite.copy()
    for x in range(10, 22):
        for y in range(15, 19):
            if y < 18 and frame4.getpixel((x, y))[3] > 0:
                pixel = frame4.getpixel((x, y+1))
                frame4.putpixel((x, y+1), pixel)
    frames.append(frame4)
    
    # Combine frames into sprite sheet
    for i, frame in enumerate(frames):
        sprite_sheet.paste(frame, (i * width, 0))
    
    # Save the sprite sheet
    sprite_sheet.save(f"{output_dir}/base_wanderer_idle.png")
    
    return sprite_sheet

def generate_walking_animation(base_sprite: Image.Image, output_dir: str = "assets/sprites/characters/player/png"):
    """Generate walking animation frames for the character"""
    width, height = base_sprite.size
    
    # Create walking animation (4 frames)
    walk_sheet = Image.new("RGBA", (width * 4, height), (0, 0, 0, 0))
    frames = []
    
    # Frame 1: Left foot forward, right foot back
    frame1 = base_sprite.copy()
    # Clear leg area
    for x in range(12, 20):
        for y in range(20, 32):
            frame1.putpixel((x, y), (0, 0, 0, 0))
    
    # Left leg forward
    for x in range(12, 16):
        for y in range(20, 26):
            frame1.putpixel((x, y), COLORS["pants_base"])
        for y in range(26, 30):
            frame1.putpixel((x, y), COLORS["boots_base"])
    
    # Right leg back
    for x in range(16, 20):
        for y in range(22, 28):
            frame1.putpixel((x, y), COLORS["pants_base"])
        for y in range(28, 32):
            frame1.putpixel((x, y), COLORS["boots_base"])
    
    frames.append(frame1)
    
    # Frame 2: Neutral stance (use base character with slight modification)
    frame2 = base_sprite.copy()
    # Slight head bob (1px up)
    head_area = frame2.crop((12, 4, 20, 12))
    frame2.paste((0, 0, 0, 0), (12, 4, 20, 12))
    frame2.paste(head_area, (12, 3), head_area)
    frames.append(frame2)
    
    # Frame 3: Right foot forward, left foot back
    frame3 = base_sprite.copy()
    # Clear leg area
    for x in range(12, 20):
        for y in range(20, 32):
            frame3.putpixel((x, y), (0, 0, 0, 0))
    
    # Left leg back
    for x in range(12, 16):
        for y in range(22, 28):
            frame3.putpixel((x, y), COLORS["pants_base"])
        for y in range(28, 32):
            frame3.putpixel((x, y), COLORS["boots_base"])
    
    # Right leg forward
    for x in range(16, 20):
        for y in range(20, 26):
            frame3.putpixel((x, y), COLORS["pants_base"])
        for y in range(26, 30):
            frame3.putpixel((x, y), COLORS["boots_base"])
    
    frames.append(frame3)
    
    # Frame 4: Similar to frame 2 but head bob down
    frame4 = base_sprite.copy()
    # Slight head bob (1px down)
    head_area = frame4.crop((12, 4, 20, 12))
    frame4.paste((0, 0, 0, 0), (12, 4, 20, 12))
    frame4.paste(head_area, (12, 5), head_area)
    frames.append(frame4)
    
    # Combine frames into sprite sheet
    for i, frame in enumerate(frames):
        walk_sheet.paste(frame, (i * width, 0))
    
    # Save the sprite sheet
    walk_sheet.save(f"{output_dir}/base_wanderer_walk.png")
    
    return walk_sheet

def generate_attack_animation(base_sprite: Image.Image, output_dir: str = "assets/sprites/characters/player/png"):
    """Generate attack animation frames for the character"""
    width, height = base_sprite.size
    
    # Create attack animation (4 frames)
    attack_sheet = Image.new("RGBA", (width * 4, height), (0, 0, 0, 0))
    frames = []
    
    # Frame 1: Wind-up
    frame1 = base_sprite.copy()
    # Clear right arm area
    for x in range(22, 24):
        for y in range(12, 28):
            frame1.putpixel((x, y), (0, 0, 0, 0))
    # Raised arm (wind up)
    for x in range(22, 24):
        for y in range(8, 20):
            frame1.putpixel((x, y), COLORS["shirt_base"])
    for x in range(22, 24):
        for y in range(4, 8):
            frame1.putpixel((x, y), COLORS["skin_base"])
    
    # Add a simple sword (raised)
    for x in range(24, 26):
        for y in range(2, 7):
            frame1.putpixel((x, y), COLORS["metal"])
    
    frames.append(frame1)
    
    # Frame 2: Attack motion
    frame2 = base_sprite.copy()
    # Clear right arm area
    for x in range(22, 24):
        for y in range(12, 28):
            frame2.putpixel((x, y), (0, 0, 0, 0))
    # Extended arm (attack)
    for x in range(22, 26):
        for y in range(12, 14):
            frame2.putpixel((x, y), COLORS["shirt_base"])
    for x in range(26, 28):
        for y in range(12, 14):
            frame2.putpixel((x, y), COLORS["skin_base"])
    
    # Add sword (extended)
    for x in range(28, 32):
        for y in range(12, 14):
            frame2.putpixel((x, y), COLORS["metal"])
    
    frames.append(frame2)
    
    # Frame 3: Follow-through
    frame3 = base_sprite.copy()
    # Clear right arm area
    for x in range(22, 24):
        for y in range(12, 28):
            frame3.putpixel((x, y), (0, 0, 0, 0))
    # Follow through arm position
    for x in range(22, 26):
        for y in range(16, 18):
            frame3.putpixel((x, y), COLORS["shirt_base"])
    for x in range(26, 28):
        for y in range(16, 18):
            frame3.putpixel((x, y), COLORS["skin_base"])
    
    # Add sword (follow through)
    for x in range(28, 32):
        for y in range(18, 20):
            frame3.putpixel((x, y), COLORS["metal"])
    
    frames.append(frame3)
    
    # Frame 4: Recovery
    frame4 = base_sprite.copy()
    # Slightly modified arm position
    for x in range(22, 24):
        for y in range(16, 24):
            frame4.putpixel((x, y), COLORS["shirt_base"])
    for x in range(22, 24):
        for y in range(24, 28):
            frame4.putpixel((x, y), COLORS["skin_base"])
    
    frames.append(frame4)
    
    # Combine frames into sprite sheet
    for i, frame in enumerate(frames):
        attack_sheet.paste(frame, (i * width, 0))
    
    # Save the sprite sheet
    attack_sheet.save(f"{output_dir}/base_wanderer_attack.png")
    
    return attack_sheet

# Audio Generation Functions
def generate_menu_select_sound(output_dir: str = "assets/audio"):
    """Generate a menu selection sound effect"""
    ensure_directory(output_dir)
    
    duration = 0.1  # 100 ms
    # Generate a higher frequency beep
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    note = np.sin(2 * np.pi * 880 * t) * 0.5  # A5 note
    
    # Apply fade out
    fade_out = np.linspace(1.0, 0.0, int(SAMPLE_RATE * duration))
    note = note * fade_out
    
    # Convert to 16-bit PCM
    audio = np.int16(note * 32767)
    
    # Save as WAV
    wavfile.write(f"{output_dir}/menu_select.wav", SAMPLE_RATE, audio)

def generate_menu_click_sound(output_dir: str = "assets/audio"):
    """Generate a menu click sound effect"""
    ensure_directory(output_dir)
    
    duration = 0.15  # 150 ms
    # Generate a click-like sound
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
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
    wavfile.write(f"{output_dir}/menu_click.wav", SAMPLE_RATE, audio)

def generate_attack_sound(output_dir: str = "assets/audio"):
    """Generate an attack sound effect"""
    ensure_directory(output_dir)
    
    duration = 0.3  # 300 ms
    # Generate a swoosh-like sound
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # Create a frequency sweep (from high to low)
    freqs = np.linspace(1200, 400, int(SAMPLE_RATE * duration))
    note = 0.6 * np.sin(2 * np.pi * np.cumsum(freqs) / SAMPLE_RATE)
    
    # Add some noise for texture
    noise = np.random.normal(0, 0.2, int(SAMPLE_RATE * duration))
    note = note + noise
    
    # Apply envelope
    attack = np.linspace(0, 1, int(SAMPLE_RATE * 0.05))  # 50ms attack
    decay = np.linspace(1, 0, int(SAMPLE_RATE * 0.25))   # 250ms decay
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
    wavfile.write(f"{output_dir}/attack.wav", SAMPLE_RATE, audio)

def generate_background_music(filename: str, duration: float = 10.0, base_freq: float = 220, output_dir: str = "assets/audio"):
    """Generate background music"""
    ensure_directory(output_dir)
    
    # Create a simple looping melody
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
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
    signal = np.zeros(int(SAMPLE_RATE * duration))
    
    note_duration = 0.5  # half second per note
    for i, freq in enumerate(sequence):
        start_idx = int(i * note_duration * SAMPLE_RATE)
        end_idx = int((i + 1) * note_duration * SAMPLE_RATE)
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
        start_idx = int(i * SAMPLE_RATE)
        end_idx = int((i + 1) * SAMPLE_RATE)
        
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
    wavfile.write(f"{output_dir}/{filename}", SAMPLE_RATE, audio)

def generate_all_game_assets():
    """Generate all game assets at once"""
    print("Generating character sprites...")
    base_sprite = generate_base_character()
    generate_idle_animation(base_sprite)
    generate_walking_animation(base_sprite)
    generate_attack_animation(base_sprite)
    
    print("Generating audio assets...")
    generate_menu_select_sound()
    generate_menu_click_sound()
    generate_attack_sound()
    generate_background_music("menu_theme.wav", duration=5.0, base_freq=220)  # A3
    generate_background_music("game_theme.wav", duration=8.0, base_freq=196)  # G3
    
    print("All game assets generated successfully!") 