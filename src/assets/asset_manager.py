"""
Asset Manager for Runic Lands
Handles loading and caching game assets like images, sounds, and music
"""

import pygame
import os
from typing import Dict, Optional, Tuple

class AssetManager:
    """Centralized system for loading and managing game assets"""
    
    def __init__(self):
        """Initialize asset caches"""
        self.sprites: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, Dict[int, pygame.font.Font]] = {}
        self.current_music: Optional[str] = None
        
        # Track asset paths for potential reloading
        self._sprite_paths: Dict[str, str] = {}
        self._sound_paths: Dict[str, str] = {}
        self._font_paths: Dict[str, str] = {}
        
    def load_sprite(self, name: str, path: str) -> pygame.Surface:
        """Load a sprite from a file, or return cached version if already loaded"""
        if name in self.sprites:
            return self.sprites[name]
            
        try:
            sprite = pygame.image.load(path).convert_alpha()
            self.sprites[name] = sprite
            self._sprite_paths[name] = path
            return sprite
        except Exception as e:
            print(f"Error loading sprite '{name}' from '{path}': {e}")
            # Return a placeholder texture for missing sprites
            placeholder = pygame.Surface((32, 32), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255))  # Magenta for missing textures
            return placeholder
            
    def load_sound(self, name: str, path: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound effect from a file, or return cached version if already loaded"""
        if name in self.sounds:
            return self.sounds[name]
            
        if not pygame.mixer.get_init():
            return None
            
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
            self._sound_paths[name] = path
            return sound
        except Exception as e:
            print(f"Error loading sound '{name}' from '{path}': {e}")
            return None
            
    def load_font(self, name: str, path: str, size: int) -> pygame.font.Font:
        """Load a font at a specific size, or return cached version if already loaded"""
        # Check if font family exists in cache
        if name in self.fonts:
            # Check if this size is cached
            if size in self.fonts[name]:
                return self.fonts[name][size]
        else:
            # Initialize font family dictionary
            self.fonts[name] = {}
            self._font_paths[name] = path
        
        try:
            # Load font at requested size
            if os.path.exists(path):
                font = pygame.font.Font(path, size)
            else:
                # Use system font if file doesn't exist
                font = pygame.font.SysFont(name, size)
                
            self.fonts[name][size] = font
            return font
        except Exception as e:
            print(f"Error loading font '{name}' size {size} from '{path}': {e}")
            # Return default font as fallback
            return pygame.font.Font(None, size)
    
    def get_default_font(self, size: int) -> pygame.font.Font:
        """Get the default system font at the specified size"""
        return pygame.font.Font(None, size)
    
    def play_music(self, name: str, path: str, loop: bool = True, volume: float = 1.0):
        """Play music from a file with optional looping"""
        if self.current_music == name:
            return  # Already playing this track
            
        if not pygame.mixer.get_init():
            return
            
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self.current_music = name
        except Exception as e:
            print(f"Error playing music '{name}' from '{path}': {e}")
    
    def stop_music(self):
        """Stop currently playing music"""
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.current_music = None
    
    def set_music_volume(self, volume: float):
        """Set the volume for music playback (0.0 to 1.0)"""
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
    
    def play_sound(self, name: str, volume: float = 1.0) -> bool:
        """Play a previously loaded sound effect with specified volume"""
        if name in self.sounds and pygame.mixer.get_init():
            self.sounds[name].set_volume(volume)
            self.sounds[name].play()
            return True
        return False
    
    def preload_assets(self, sprite_list: Dict[str, str], sound_list: Dict[str, str]):
        """Preload multiple assets at once"""
        for name, path in sprite_list.items():
            self.load_sprite(name, path)
            
        for name, path in sound_list.items():
            self.load_sound(name, path)
    
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a previously loaded sprite by name"""
        return self.sprites.get(name)
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get a previously loaded sound by name"""
        return self.sounds.get(name)
    
    def cleanup(self):
        """Release all asset resources"""
        self.sprites.clear()
        self.sounds.clear()
        self.fonts.clear()
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop() 