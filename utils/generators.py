"""
Asset Generator Utilities
This module provides functions to generate game assets programmatically.
"""

import os
import numpy as np
from PIL import Image
from scipy.io import wavfile
from typing import Dict, Tuple, List

# Enhanced color palettes with more human-like options
COLORS = {
    # Skin tones (more realistic variety)
    "skin_pale": (255, 220, 177, 255),
    "skin_light": (255, 206, 158, 255),
    "skin_medium": (224, 176, 136, 255),
    "skin_tan": (192, 152, 118, 255),
    "skin_dark": (160, 128, 96, 255),
    "skin_very_dark": (128, 96, 64, 255),
    
    # Hair colors (more variety)
    "hair_black": (45, 45, 45, 255),
    "hair_brown": (101, 67, 33, 255),
    "hair_blonde": (255, 220, 177, 255),
    "hair_red": (139, 69, 19, 255),
    "hair_gray": (128, 128, 128, 255),
    "hair_white": (200, 200, 200, 255),
    
    # Clothing colors (expanded palette)
    "clothing_red": (220, 20, 60, 255),
    "clothing_blue": (30, 144, 255, 255),
    "clothing_green": (34, 139, 34, 255),
    "clothing_purple": (128, 0, 128, 255),
    "clothing_yellow": (255, 215, 0, 255),
    "clothing_orange": (255, 140, 0, 255),
    "clothing_brown": (139, 69, 19, 255),
    "clothing_gray": (128, 128, 128, 255),
    "clothing_black": (45, 45, 45, 255),
    "clothing_white": (240, 240, 240, 255),
    
    # Eye colors
    "eye_brown": (101, 67, 33, 255),
    "eye_blue": (135, 206, 235, 255),
    "eye_green": (34, 139, 34, 255),
    "eye_hazel": (160, 82, 45, 255),
    "eye_gray": (128, 128, 128, 255),
    
    # Shadow variants
    "skin_shadow": (198, 156, 123, 255),
    "hair_shadow": (51, 51, 51, 255),
    "clothing_shadow": (101, 67, 33, 255),
    "eye_shadow": (85, 51, 17, 255),
    
    # Metal colors
    "metal": (192, 192, 192, 255),
    "metal_shadow": (128, 128, 128, 255),
}

# Character customization settings
CHARACTER_SETTINGS = {
    "skin_tone": "skin_medium",
    "hair_color": "hair_brown", 
    "shirt_color": "clothing_brown",
    "pants_color": "clothing_gray",
    "shoes_color": "clothing_black",
    "eye_color": "eye_brown",
    "hair_style": "medium",  # short, medium, long, bald, beard
    "gender": "male",  # male, female, non_binary
    "age": "adult"  # young, adult, elderly
}

# Audio sample rate
SAMPLE_RATE = 44100  # 44.1 kHz

def ensure_directory(path: str):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)

# Sprite Generation Functions
def generate_base_character(output_dir: str = "assets/sprites/characters/player/png", custom_settings: Dict = None):
    """Generate the base character sprite with enhanced human-like features and customizable colors"""
    ensure_directory(output_dir)
    
    # Use custom settings or defaults
    settings = custom_settings if custom_settings else CHARACTER_SETTINGS
    
    # Base sprite size
    width, height = 32, 32
    
    # Create images for different layers
    base_body = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    base_clothing = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    combined = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    # Get colors based on settings
    skin_color = COLORS[settings["skin_tone"]]
    hair_color = COLORS[settings["hair_color"]]
    shirt_color = COLORS[settings["shirt_color"]]
    pants_color = COLORS[settings["pants_color"]]
    shoes_color = COLORS[settings["shoes_color"]]
    eye_color = COLORS[settings["eye_color"]]
    
    # Enhanced Head with more human-like features
    head_x, head_y = 12, 4
    head_width, head_height = 8, 10
    
    # Draw head with more oval shape
    for dx in range(head_width):
        for dy in range(head_height):
            px, py = head_x + dx, head_y + dy
            if 0 <= px < width and 0 <= py < height:
                # Create more oval shape
                center_x, center_y = head_x + head_width // 2, head_y + head_height // 2
                dist_x = abs(dx - head_width // 2) / (head_width // 2)
                dist_y = abs(dy - head_height // 2) / (head_height // 2)
                
                if dist_x * dist_x + dist_y * dist_y <= 1.0:
                    base_body.putpixel((px, py), skin_color)
    
    # Draw hair based on style
    draw_hair(base_clothing, hair_color, settings["hair_style"], head_x, head_y, head_width, head_height)
    
    # Draw eyes
    draw_eyes(base_body, eye_color, head_x, head_y, head_width)
    
    # Draw nose (small triangle)
    for dx in range(2):
        for dy in range(2):
            px, py = head_x + 3 + dx, head_y + 6 + dy
            if 0 <= px < width and 0 <= py < height:
                if dx + dy <= 1:  # Triangle shape
                    base_body.putpixel((px, py), COLORS["skin_shadow"])
    
    # Draw mouth
    for dx in range(3):
        px, py = head_x + 3 + dx, head_y + 8
        if 0 <= px < width and 0 <= py < height:
            base_body.putpixel((px, py), COLORS["skin_shadow"])
    
    # Enhanced Torso with better proportions
    torso_x, torso_y = 10, 12
    torso_width, torso_height = 12, 8
    
    for dx in range(torso_width):
        for dy in range(torso_height):
            px, py = torso_x + dx, torso_y + dy
            if 0 <= px < width and 0 <= py < height:
                base_clothing.putpixel((px, py), shirt_color)
    
    # Torso shadow
    for dx in range(torso_width):
        for dy in range(2):
            px, py = torso_x + dx, torso_y + dy + torso_height
            if 0 <= px < width and 0 <= py < height:
                base_clothing.putpixel((px, py), COLORS["clothing_shadow"])
    
    # Enhanced Arms with better proportions
    arm_width, arm_height = 2, 12
    
    # Left arm
    for dx in range(arm_width):
        for dy in range(arm_height):
            px, py = torso_x - arm_width + dx, torso_y + dy
            if 0 <= px < width and 0 <= py < height:
                base_clothing.putpixel((px, py), shirt_color)
    
    # Right arm
    for dx in range(arm_width):
        for dy in range(arm_height):
            px, py = torso_x + torso_width + dx, torso_y + dy
            if 0 <= px < width and 0 <= py < height:
                base_clothing.putpixel((px, py), shirt_color)
    
    # Enhanced Hands
    hand_width, hand_height = 2, 4
    
    # Left hand
    for dx in range(hand_width):
        for dy in range(hand_height):
            px, py = torso_x - hand_width + dx, torso_y + arm_height + dy
            if 0 <= px < width and 0 <= py < height:
                base_body.putpixel((px, py), skin_color)
    
    # Right hand
    for dx in range(hand_width):
        for dy in range(hand_height):
            px, py = torso_x + torso_width + dx, torso_y + arm_height + dy
            if 0 <= px < width and 0 <= py < height:
                base_body.putpixel((px, py), skin_color)
    
    # Enhanced Legs with better proportions
    leg_x, leg_y = 12, 20
    leg_width, leg_height = 4, 8
    
    # Left leg
    for dx in range(leg_width):
        for dy in range(leg_height):
            px, py = leg_x + dx, leg_y + dy
            if 0 <= px < width and 0 <= py < height:
                base_clothing.putpixel((px, py), pants_color)
    
    # Right leg
    for dx in range(leg_width):
        for dy in range(leg_height):
            px, py = leg_x + leg_width + dx, leg_y + dy
            if 0 <= px < width and 0 <= py < height:
                base_clothing.putpixel((px, py), pants_color)
    
    # Leg shadows
    for dx in range(leg_width * 2):
        for dy in range(2):
            px, py = leg_x + dx, leg_y + dy + leg_height
            if 0 <= px < width and 0 <= py < height:
                base_clothing.putpixel((px, py), COLORS["clothing_shadow"])
    
    # Enhanced Feet
    foot_width, foot_height = 4, 4
    
    # Left foot
    for dx in range(foot_width):
        for dy in range(foot_height):
            px, py = leg_x + dx, leg_y + dy + leg_height
            if 0 <= px < width and 0 <= py < height:
                base_clothing.putpixel((px, py), shoes_color)
    
    # Right foot
    for dx in range(foot_width):
        for dy in range(foot_height):
            px, py = leg_x + foot_width + dx, leg_y + dy + leg_height
            if 0 <= px < width and 0 <= py < height:
                base_clothing.putpixel((px, py), shoes_color)
    
    # Combine layers
    combined = Image.alpha_composite(combined, base_body)
    combined = Image.alpha_composite(combined, base_clothing)
    
    # Save the images
    base_body.save(f"{output_dir}/base_body.png")
    base_clothing.save(f"{output_dir}/base_clothing.png")
    combined.save(f"{output_dir}/base_wanderer.png")
    
    # Save character settings
    settings_file = f"{output_dir}/character_settings.txt"
    with open(settings_file, 'w') as f:
        for key, value in settings.items():
            f.write(f"{key}: {value}\n")
    
    return combined

def draw_hair(img: Image.Image, hair_color: Tuple, hair_style: str, x: int, y: int, head_width: int, head_height: int):
    """Draw hair based on style"""
    if hair_style == "bald":
        return
    
    # Hair base
    for dx in range(head_width + 2):
        for dy in range(3):
            px, py = x + dx - 1, y + dy
            if 0 <= px < img.width and 0 <= py < img.height:
                img.putpixel((px, py), hair_color)
    
    # Hair shadow
    for dx in range(head_width + 2):
        for dy in range(2):
            px, py = x + dx - 1, y + dy + 3
            if 0 <= px < img.width and 0 <= py < img.height:
                img.putpixel((px, py), COLORS["hair_shadow"])
    
    # Long hair
    if hair_style == "long":
        for dx in range(head_width + 2):
            for dy in range(4):
                px, py = x + dx - 1, y + dy + head_height
                if 0 <= px < img.width and 0 <= py < img.height:
                    img.putpixel((px, py), hair_color)
    
    # Beard
    if hair_style == "beard":
        for dx in range(4):
            for dy in range(3):
                px, py = x + 2 + dx, y + head_height - 2 + dy
                if 0 <= px < img.width and 0 <= py < img.height:
                    img.putpixel((px, py), hair_color)

def draw_eyes(img: Image.Image, eye_color: Tuple, x: int, y: int, head_width: int):
    """Draw eyes with color"""
    # Left eye
    for dx in range(2):
        for dy in range(2):
            px, py = x + dx, y + dy
            if 0 <= px < img.width and 0 <= py < img.height:
                img.putpixel((px, py), eye_color)
    
    # Right eye
    for dx in range(2):
        for dy in range(2):
            px, py = x + head_width - 2 + dx, y + dy
            if 0 <= px < img.width and 0 <= py < img.height:
                img.putpixel((px, py), eye_color)

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
            frame1.putpixel((x, y), COLORS["clothing_gray"])  # Default pants color
        for y in range(26, 30):
            frame1.putpixel((x, y), COLORS["clothing_black"])  # Default boots color
    
    # Right leg back
    for x in range(16, 20):
        for y in range(22, 28):
            frame1.putpixel((x, y), COLORS["clothing_gray"])  # Default pants color
        for y in range(28, 32):
            frame1.putpixel((x, y), COLORS["clothing_black"])  # Default boots color
    
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
            frame3.putpixel((x, y), COLORS["clothing_gray"])  # Default pants color
        for y in range(28, 32):
            frame3.putpixel((x, y), COLORS["clothing_black"])  # Default boots color
    
    # Right leg forward
    for x in range(16, 20):
        for y in range(20, 26):
            frame3.putpixel((x, y), COLORS["clothing_gray"])  # Default pants color
        for y in range(26, 30):
            frame3.putpixel((x, y), COLORS["clothing_black"])  # Default boots color
    
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
            frame1.putpixel((x, y), COLORS["clothing_brown"])  # Default shirt color
    for x in range(22, 24):
        for y in range(4, 8):
            frame1.putpixel((x, y), COLORS["skin_medium"])  # Default skin color
    
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
            frame2.putpixel((x, y), COLORS["clothing_brown"])  # Default shirt color
    for x in range(26, 28):
        for y in range(12, 14):
            frame2.putpixel((x, y), COLORS["skin_medium"])  # Default skin color
    
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
            frame3.putpixel((x, y), COLORS["clothing_brown"])  # Default shirt color
    for x in range(26, 28):
        for y in range(16, 18):
            frame3.putpixel((x, y), COLORS["skin_medium"])  # Default skin color
    
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
            frame4.putpixel((x, y), COLORS["clothing_brown"])  # Default shirt color
    for x in range(22, 24):
        for y in range(24, 28):
            frame4.putpixel((x, y), COLORS["skin_medium"])  # Default skin color
    
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

def generate_custom_character(skin_tone: str = "skin_medium", hair_color: str = "hair_brown", 
                            shirt_color: str = "clothing_brown", pants_color: str = "clothing_gray", 
                            shoes_color: str = "clothing_black", eye_color: str = "eye_brown",
                            hair_style: str = "medium", gender: str = "male", age: str = "adult",
                            output_dir: str = "assets/sprites/characters/player/png"):
    """Generate a custom character with specified appearance settings"""
    custom_settings = {
        "skin_tone": skin_tone,
        "hair_color": hair_color,
        "shirt_color": shirt_color,
        "pants_color": pants_color,
        "shoes_color": shoes_color,
        "eye_color": eye_color,
        "hair_style": hair_style,
        "gender": gender,
        "age": age
    }
    
    print(f"🎨 Generating custom character with settings:")
    for key, value in custom_settings.items():
        print(f"   {key}: {value}")
    
    base_sprite = generate_base_character(output_dir, custom_settings)
    generate_idle_animation(base_sprite, output_dir)
    generate_walking_animation(base_sprite, output_dir)
    generate_attack_animation(base_sprite, output_dir)
    
    print("✅ Custom character generated successfully!")
    return base_sprite

def generate_random_character(output_dir: str = "assets/sprites/characters/player/png"):
    """Generate a random character with random appearance settings"""
    import random
    
    skin_tones = ["skin_pale", "skin_light", "skin_medium", "skin_tan", "skin_dark", "skin_very_dark"]
    hair_colors = ["hair_black", "hair_brown", "hair_blonde", "hair_red", "hair_gray", "hair_white"]
    clothing_colors = ["clothing_red", "clothing_blue", "clothing_green", "clothing_purple", 
                      "clothing_yellow", "clothing_orange", "clothing_brown", "clothing_gray", 
                      "clothing_black", "clothing_white"]
    eye_colors = ["eye_brown", "eye_blue", "eye_green", "eye_hazel", "eye_gray"]
    hair_styles = ["short", "medium", "long", "bald", "beard"]
    genders = ["male", "female", "non_binary"]
    ages = ["young", "adult", "elderly"]
    
    random_settings = {
        "skin_tone": random.choice(skin_tones),
        "hair_color": random.choice(hair_colors),
        "shirt_color": random.choice(clothing_colors),
        "pants_color": random.choice(clothing_colors),
        "shoes_color": random.choice(clothing_colors),
        "eye_color": random.choice(eye_colors),
        "hair_style": random.choice(hair_styles),
        "gender": random.choice(genders),
        "age": random.choice(ages)
    }
    
    print(f"🎲 Generating random character with settings:")
    for key, value in random_settings.items():
        print(f"   {key}: {value}")
    
    base_sprite = generate_base_character(output_dir, random_settings)
    generate_idle_animation(base_sprite, output_dir)
    generate_walking_animation(base_sprite, output_dir)
    generate_attack_animation(base_sprite, output_dir)
    
    print("✅ Random character generated successfully!")
    return base_sprite

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