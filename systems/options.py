import pygame
import json
import os
from typing import Dict, Any, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
CONFIG_FILE = "config.json"

# List of common resolutions
AVAILABLE_RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 720),  # 720p
    (1366, 768),  # Common laptop
    (1600, 900),
    (1920, 1080), # 1080p
    (2560, 1440)  # 1440p
]

DEFAULT_KEYBINDS = {
    'player1': {
        'up': pygame.K_w,
        'down': pygame.K_s,
        'left': pygame.K_a,
        'right': pygame.K_d,
        'attack': pygame.K_SPACE,
        'inventory': pygame.K_i,
        'run': pygame.K_LCTRL  # Added run keybind for player 1
    },
    'player2': {
        'up': pygame.K_UP,
        'down': pygame.K_DOWN,
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'attack': pygame.K_RCTRL,
        'inventory': pygame.K_RSHIFT,
        'run': pygame.K_RCTRL  # Added run keybind for player 2
    }
}

DEFAULT_AUDIO = {
    'master_volume': 0.7,
    'music_volume': 0.5,
    'sfx_volume': 0.8,
    'is_muted': False
}

DEFAULT_VIDEO = {
    'fullscreen': False,
    'resolution': (800, 600),
    'vsync': True,
    'gui_scale': 1.0,  # Added GUI scale
    'particles_enabled': True  # Add particles toggle
}

class OptionsSystem:
    """
    Manages game settings including keybindings, audio, and video.

    This class handles loading, saving, and applying all user-configurable
    settings. It provides methods to interact with video, audio, and input
    configurations, ensuring a persistent state between game sessions.
    """
    
    def __init__(self):
        """
        Initializes the OptionsSystem.

        Sets up default values, initializes Pygame mixer, and loads settings
        from the configuration file if it exists.
        """
        self.logger = logging.getLogger(__name__)
        self.settings_file = Path("settings.json")
        self.default_settings = {
            'screen_size': (800, 600),
            'fps': 60,
            'volume': 0.5,
            'fullscreen': False,
            'vsync': True
        }
        self.settings = self.default_settings.copy()
        self.keybinds = DEFAULT_KEYBINDS.copy()
        self.audio = DEFAULT_AUDIO.copy()
        self.video = DEFAULT_VIDEO.copy()  # Add missing video settings
        self.sounds = {}
        self.music_queue = []
        self.current_track = None
        self.next_track = None
        self.music_end_event = pygame.USEREVENT + 1
        self.music_player_active = False  # Flag to track if music player is controlling playback
        self.video_change_callback = None  # Initialize callback to prevent AttributeError
        self.fullscreen_callback = None  # Initialize fullscreen callback to prevent AttributeError
        pygame.mixer.music.set_endevent(self.music_end_event)
        self.initialize()

    def initialize(self):
        """
        Initializes the options system by loading settings from a file.

        If loading fails, it resets to default settings and creates the
        settings file.
        """
        try:
            self.load_settings()
            self.logger.info("Options system initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing options system: {e}")
            self.settings = self.default_settings.copy()
            self.save_settings()

    def load_settings(self):
        """
        Loads game settings from the settings JSON file.

        This method reads `settings.json` and populates the system's
        configuration. It handles nested structures for keybinds, audio, and
        video. If the file doesn't exist or an error occurs, it falls back
        to default settings.
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded_data = json.load(f)
                    loaded_settings = {k: v for k, v in loaded_data.items() if k not in ['keybinds', 'audio', 'video']}
                    loaded_keybinds = loaded_data.get('keybinds', {})
                    loaded_audio = loaded_data.get('audio', {})
                    loaded_video = loaded_data.get('video', {})

                    # Convert screen_size from list to tuple
                    if 'screen_size' in loaded_settings:
                        loaded_settings['screen_size'] = tuple(loaded_settings['screen_size'])
                    self.settings.update(loaded_settings)

                    # Update keybinds from loaded data
                    # Deep update to handle nested player dictionaries
                    for player, binds in loaded_keybinds.items():
                        if player in self.keybinds:
                            self.keybinds[player].update(binds)
                        else:
                            self.keybinds[player] = binds

                    # Update audio settings
                    self.audio.update(loaded_audio)
                    
                    # Update video settings
                    self.video.update(loaded_video)

                self.logger.info("Settings loaded successfully")
            else:
                self.logger.info("No settings file found, using defaults")
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            self.settings = self.default_settings.copy()

    def save_settings(self):
        """
        Saves the current game settings to the settings JSON file.

        This method serializes all current settings, including keybinds, audio,
        and video configurations, into `settings.json` for persistence.
        """
        try:
            # Combine settings, keybinds, audio, and video for saving
            data_to_save = self.settings.copy()
            data_to_save['keybinds'] = self.keybinds
            data_to_save['audio'] = self.audio
            data_to_save['video'] = self.video
            with open(self.settings_file, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            self.logger.info("Settings saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Gets the current screen size setting.

        Returns:
            Tuple[int, int]: The current screen size as a (width, height) tuple.
        """
        return self.settings['screen_size']

    def set_screen_size(self, width: int, height: int):
        """
        Sets the screen size setting.

        Args:
            width (int): The new screen width in pixels.
            height (int): The new screen height in pixels.
        """
        self.settings['screen_size'] = (width, height)
        self.save_settings()

    def get_fps(self) -> int:
        """
        Gets the current target frames per second (FPS) setting.

        Returns:
            int: The current FPS target.
        """
        return self.settings['fps']

    def set_fps(self, fps: int):
        """
        Sets the target frames per second (FPS) setting.

        Args:
            fps (int): The new FPS target.
        """
        self.settings['fps'] = fps
        self.save_settings()

    def get_volume(self) -> float:
        """
        Gets the current master volume setting.

        Returns:
            float: The current volume level (0.0 to 1.0).
        """
        return self.settings['volume']

    def set_volume(self, volume: float):
        """
        Sets the master volume setting.

        Args:
            volume (float): The new volume level (clamped between 0.0 and 1.0).
        """
        self.settings['volume'] = max(0.0, min(1.0, volume))
        self.save_settings()

    def get_fullscreen(self) -> bool:
        """
        Gets the current fullscreen mode setting.

        Returns:
            bool: True if fullscreen is enabled, False otherwise.
        """
        return self.settings['fullscreen']

    def set_fullscreen(self, fullscreen: bool):
        """
        Sets the fullscreen mode.

        Args:
            fullscreen (bool): The desired fullscreen state.
        """
        self.settings['fullscreen'] = fullscreen
        self.save_settings()

    def get_vsync(self) -> bool:
        """
        Gets the current VSync setting.

        Returns:
            bool: True if VSync is enabled, False otherwise.
        """
        return self.settings['vsync']
    
    def get_setting(self, key: str):
        """
        Gets a generic setting value by its key.

        Args:
            key (str): The key of the setting to retrieve.

        Returns:
            Any: The value of the setting, or None if the key does not exist.
        """
        return self.settings.get(key)

    def set_vsync(self, vsync: bool):
        """
        Sets the VSync setting.

        Args:
            vsync (bool): The desired VSync state.
        """
        self.settings['vsync'] = vsync
        self.save_settings()

    def reset_to_defaults(self):
        """
        Resets all settings to their default values and saves them.
        """
        self.settings = self.default_settings.copy()
        self.save_settings()
        self.logger.info("Settings reset to defaults")

    def _load_sound_effects(self):
        """
        Loads all defined sound effects into memory.

        This internal method populates the `self.sounds` dictionary. If a
        sound file is missing, it attempts to generate a fallback sound.
        """
        sound_files = {
            'menu_click': 'assets/audio/menu_click.wav',
            'menu_select': 'assets/audio/menu_select.wav',
            'attack': 'assets/audio/attack.wav'
        }
        
        # Load each sound file
        for name, path in sound_files.items():
            try:
                sound = pygame.mixer.Sound(path)
                self.sounds[name] = sound
                print(f"Loaded sound: {path}")
            except Exception as e:
                print(f"Could not load sound: {path} - Error: {e}")
                # Try to generate missing sounds
                if name == 'menu_click':
                    try:
                        self._generate_click_sound()
                        sound = pygame.mixer.Sound('assets/audio/menu_click.wav')
                        self.sounds[name] = sound
                        print(f"Generated and loaded sound: {path}")
                    except Exception as e2:
                        print(f"Could not generate sound: {name} - Error: {e2}")
    
    def _generate_click_sound(self):
        """
        Generates a simple click sound if the primary sound file is missing.

        This method uses NumPy and SciPy to create a synthetic sound wave,
        providing a fallback to prevent crashes when audio assets are not found.

        Raises:
            Exception: Propagates exceptions from audio generation libraries.
        """
        try:
            import numpy as np
            from scipy.io import wavfile
            from pathlib import Path
            
            # Ensure audio directory exists
            Path("assets/audio").mkdir(exist_ok=True)
            
            # Sample rate
            sample_rate = 44100  # 44.1 kHz
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
        except Exception as e:
            print(f"Error generating click sound: {e}")
            raise
    
    def play_sound(self, sound_name: str):
        """
        Plays a pre-loaded sound effect by its name.

        Args:
            sound_name (str): The name (key) of the sound effect to play.
        """
        if sound_name in self.sounds:
            # Apply master volume adjustment
            volume = self.audio['sfx_volume'] * self.audio['master_volume']
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()
    
    def _get_enhanced_version(self, music_file: str) -> str:
        """
        Checks for an enhanced version of a music file.

        (Note: This functionality is currently disabled and returns the original path.)

        Args:
            music_file (str): The path to the music file.

        Returns:
            str: The path to the enhanced music file, or the original path.
        """
        try:
            # Just return the original file - enhanced versions were removed
            print(f"Using music file: {music_file}")
            return music_file
        except Exception as e:
            print(f"Error checking for enhanced version: {e}")
            return music_file

    def play_music(self, music_file: str, loop: bool = True, queue: bool = False) -> bool:
        """
        Plays a music file, with options for looping and queuing.

        This is the primary method for controlling music playback. It handles
        loading, playing, and queuing tracks, and applies the current volume
        settings.

        Args:
            music_file (str): The path to the music file to be played.
            loop (bool, optional): If True, the music will loop indefinitely. Defaults to True.
            queue (bool, optional): If True, the music will be added to the
                                  queue instead of playing immediately. Defaults to False.

        Returns:
            bool: True if the music was played or queued successfully, False otherwise.
        """
        if not music_file:
            return False
            
        if not pygame.mixer.get_init():
            return False
            
        # Check for enhanced version of the music file
        enhanced_file = self._get_enhanced_version(music_file)
        if enhanced_file:
            music_file = enhanced_file
            print(f"Using enhanced music: {music_file}")
            
        # Track timing for debugging
        request_time = pygame.time.get_ticks()
        print(f"DEBUG: Music request - {music_file} at {request_time} ms")
        
        try:
            print(f"Using music file: {music_file}")
            
            # Check if file exists
            if not os.path.exists(music_file):
                print(f"ERROR: Music file not found: {music_file}")
                return False
                
            load_start = pygame.time.get_ticks()
            # Only attempt direct load if not queuing
            if not queue:
                if pygame.mixer.music.get_busy() and not loop:
                    pygame.mixer.music.stop()
                pygame.mixer.music.load(music_file)
                
                # Register end event for music
                pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
                
                load_time = pygame.time.get_ticks() - load_start
                print(f"DEBUG: Music file loaded in {load_time} ms")
                
                # Save current track info
                self.current_track = os.path.basename(music_file)
                
                play_start = pygame.time.get_ticks()
                loop_count = -1 if loop else 0  # -1 means loop indefinitely
                pygame.mixer.music.play(loop_count)
                play_time = pygame.time.get_ticks() - play_start
                
                print(f"DEBUG: Music started - {os.path.basename(music_file)} in {play_time} ms")
                print(f"DEBUG: Total music setup time: {pygame.time.get_ticks() - request_time} ms")
                
                # Apply volume (consider mute status)
                effective_volume = 0.0 if self.audio.get('is_muted', False) else (
                    self.audio.get('music_volume', 0.5) * self.audio.get('master_volume', 0.7))
                pygame.mixer.music.set_volume(effective_volume)
                
                return True
            else:
                # Try to queue music
                if pygame.mixer.music.get_busy():
                    print(f"Queuing next section: {os.path.basename(music_file)}")
                    pygame.mixer.music.queue(music_file)
                    return True
                else:
                    # If not currently playing, start playing
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
                    self.current_track = os.path.basename(music_file)
                    pygame.mixer.music.play(0)  # Don't loop, music will be queued
                    effective_volume = 0.0 if self.audio.get('is_muted', False) else (
                        self.audio.get('music_volume', 0.5) * self.audio.get('master_volume', 0.7))
                    pygame.mixer.music.set_volume(effective_volume)
                    return True
        except Exception as e:
            print(f"Error playing music: {e}")
            return False

    def handle_music_event(self, event: pygame.event.Event):
        """
        Handles music-related Pygame events, primarily for seamless track transitions.

        This method should be called from the main game loop to process events.
        It checks for the music end event and plays the next track in the queue.

        Args:
            event (pygame.event.Event): The Pygame event to process.
        """
        
        # If music player is active, don't handle automatic music events
        if getattr(self, 'music_player_active', False):
            return False
        
        # Music has ended, play the next track in the queue
        if hasattr(self, 'music_queue') and self.music_queue:
            next_track = self.music_queue.pop(0)
            
            try:
                # Play the next track without looping
                pygame.mixer.music.load(next_track)
                pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
                pygame.mixer.music.play(0)  # No loop, we'll queue the next one
                
                # Update tracking
                self.current_track = os.path.basename(next_track)
                
                # Apply volume
                effective_volume = 0.0 if self.audio.get('is_muted', False) else (
                    self.audio.get('music_volume', 0.5) * self.audio.get('master_volume', 0.7))
                pygame.mixer.music.set_volume(effective_volume)
                
                return True
            except Exception as e:
                print(f"ERROR: Failed to play next track: {e}")
                return False
        else:
            # Queue is empty, restart the appropriate music sequence
            print(f"DEBUG: Music sequence completed, restarting seamless loop")
            
            # Check if current track is a game section or menu section
            is_game_section = False
            if hasattr(self, 'current_track') and self.current_track:
                is_game_section = self.current_track.startswith("game_section")
                
            if is_game_section:
                return self.queue_game_music()
            else:
                return self.start_seamless_menu_music()

    def _rebuild_section_queue(self, current_track: str = None):
        """
        Rebuilds the music queue for menu sections to ensure continuous playback.

        Args:
            current_track (str, optional): The filename of the track that just
                                           finished, used to determine the next
                                           track in sequence. Defaults to None.
        """
        # Clear existing queue
        self.music_queue = []
        
        # Get all available section files
        base_path = "assets/audio/"
        all_sections = [
            f"{base_path}menu_section1.wav",
            f"{base_path}menu_section2.wav",
            f"{base_path}menu_section3.wav",
            f"{base_path}menu_section4.wav",
            f"{base_path}menu_section5.wav",
            f"{base_path}menu_section6.wav",
            f"{base_path}menu_section7.wav",
            f"{base_path}menu_section8.wav",
            f"{base_path}menu_section9.wav",
            f"{base_path}menu_section10.wav",
        ]
        
        # Find existing sections
        existing_sections = [s for s in all_sections if os.path.exists(s)]
        if not existing_sections:
            print("ERROR: No section files found!")
            return
            
        # Find current position in sequence
        current_index = 0
        if current_track:
            try:
                current_path = f"{base_path}{current_track}"
                current_index = existing_sections.index(current_path)
            except ValueError:
                # If current track not found, start from the beginning
                current_index = 0
                
        # Queue all tracks starting from the next one
        next_index = (current_index + 1) % len(existing_sections)
        for i in range(len(existing_sections)):
            idx = (next_index + i) % len(existing_sections)
            self.music_queue.append(existing_sections[idx])
            
        print(f"DEBUG: Rebuilt queue with {len(existing_sections)} sections starting after {current_track}")
    
    def _rebuild_game_section_queue(self, current_track: str = None):
        """
        Rebuilds the music queue for in-game sections.

        Args:
            current_track (str, optional): The filename of the track that just
                                           finished. Defaults to None.
        """
        # Clear existing queue
        self.music_queue = []
        
        # Get all available game section files
        base_path = "assets/audio/game/"
        all_sections = [
            f"{base_path}game_section1.wav",
            f"{base_path}game_section2.wav",
            f"{base_path}game_section3.wav",
            f"{base_path}game_section4.wav",
            f"{base_path}game_section5.wav",
            f"{base_path}game_section6.wav",
            f"{base_path}game_section7.wav",
            f"{base_path}game_section8.wav",
            f"{base_path}game_section9.wav",
            f"{base_path}game_section10.wav",
        ]
        
        # Find existing sections
        existing_sections = [s for s in all_sections if os.path.exists(s)]
        if not existing_sections:
            print("ERROR: No game section files found!")
            return
            
        # Find current position in sequence
        current_index = 0
        if current_track:
            try:
                current_path = f"{base_path}{current_track}"
                current_index = existing_sections.index(current_path)
            except ValueError:
                # If current track not found, start from the beginning
                current_index = 0
                
        # Queue all tracks starting from the next one
        next_index = (current_index + 1) % len(existing_sections)
        for i in range(len(existing_sections)):
            idx = (next_index + i) % len(existing_sections)
            self.music_queue.append(existing_sections[idx])
            
        print(f"DEBUG: Rebuilt game queue with {len(existing_sections)} sections starting after {current_track}")
    
    def _play_next_track_now(self):
        """
        Immediately plays the next track in the music queue.

        This is a low-level method designed to minimize delay between tracks
        for seamless playback.
        """
        print(f"DEBUG: Playing next track immediately at {pygame.time.get_ticks()} ms")
        
        # If we have a next track ready, play it right away
        if len(self.music_queue) > 0:
            next_track = self.music_queue.pop(0)
            load_start = pygame.time.get_ticks()
            print(f"DEBUG: Starting immediate playback of {os.path.basename(next_track)}")
            
            # Directly load and play to minimize delay
            try:
                # Immediate load
                pygame.mixer.music.load(next_track)
                
                # Start playing right away
                pygame.mixer.music.play(0)  # No loop - we'll queue the next one
                load_end = pygame.time.get_ticks()
                print(f"DEBUG: Immediate playback loaded and started in {load_end - load_start} ms")
                
                # Update tracking
                self.current_track = os.path.basename(next_track)
                
                # Queue up the next track IMMEDIATELY to prevent gaps
                if len(self.music_queue) > 0:
                    queue_start = pygame.time.get_ticks()
                    pygame.mixer.music.queue(self.music_queue[0])
                    self.next_track = os.path.basename(self.music_queue[0])
                    queue_end = pygame.time.get_ticks()
                    print(f"DEBUG: Next track queued in {queue_end - queue_start} ms - {self.next_track}")
                
                return True
            except Exception as e:
                print(f"Error in immediate playback: {e}")
                # Try standard playback as fallback
                self.play_music(next_track, loop=False)
                return True
                
        # If we have no queue but know what track was playing, rebuild and try again
        elif getattr(self, 'current_track', None) is not None:
            print(f"DEBUG: Empty queue, rebuilding from {self.current_track}")
            
            # Check if this is a game section
            is_game_section = self.current_track.startswith("game_section")
            
            # Rebuild the appropriate queue
            if is_game_section:
                self._rebuild_game_section_queue(self.current_track)
            else:
                self._rebuild_section_queue(self.current_track)
                
            if len(self.music_queue) > 0:
                return self._play_next_track_now()  # Recursive call with populated queue
            
        # Absolute fallback - restart the sequence from the beginning
        print(f"DEBUG: No queue info available, restarting sequence from beginning")
        
        # Check if we were playing game music
        is_game_section = False
        if hasattr(self, 'current_track') and self.current_track:
            is_game_section = self.current_track.startswith("game_section")
            
        # Start appropriate sequence
        if is_game_section:
            # Start game music sequence
            print("DEBUG: Starting game music sequence from beginning")
            return self._immediate_play_game_sequence()
        else:
            # Start menu music sequence
            return self._immediate_play_sequence()
    
    def _immediate_play_sequence(self):
        """
        Immediately starts playing the menu music sequence from the beginning.

        This method is optimized for fast startup of the menu music loop.
        """
        print(f"DEBUG: Starting immediate sequence at {pygame.time.get_ticks()} ms")
        
        # Clear existing queue and state
        self.next_track = None
        self.music_queue = []
        
        # Define section paths and check which ones exist
        base_path = "assets/audio/"
        all_sections = [
            f"{base_path}menu_section1.wav",  # Heroic Intro
            f"{base_path}menu_section2.wav",  # Calm Town-like Section
            f"{base_path}menu_section3.wav",  # Energetic Battle-like Section
            f"{base_path}menu_section4.wav",  # Resolving Passage
            f"{base_path}menu_section5.wav",  # Misty Woods Intro
            f"{base_path}menu_section6.wav",
            f"{base_path}menu_section7.wav",
            f"{base_path}menu_section8.wav",
            f"{base_path}menu_section9.wav",
            f"{base_path}menu_section10.wav",
        ]
        
        # Check which section files actually exist
        existing_sections = []
        for section in all_sections:
            if os.path.exists(section):
                existing_sections.append(section)
            else:
                print(f"WARNING: Missing music file: {section}")
        
        # If we have no section files, log error and return
        if len(existing_sections) == 0:
            print("ERROR: No section files found.")
            return False
        
        # Timing info for debugging
        load_start = pygame.time.get_ticks()
        
        # Start with the first existing section
        first_section = existing_sections[0]
        print(f"DEBUG: Starting sequence with {os.path.basename(first_section)}")
        
        try:
            # Direct loading and playing for faster response
            pygame.mixer.music.load(first_section)
            pygame.mixer.music.play(0)  # No loop - we'll queue the next track
            
            # Update current track
            self.current_track = os.path.basename(first_section)
            
            # Apply volume
            effective_volume = 0.0 if self.audio.get('is_muted', False) else (
                self.audio.get('music_volume', 0.5) * self.audio.get('master_volume', 0.7))
            pygame.mixer.music.set_volume(effective_volume)
            
            load_end = pygame.time.get_ticks()
            print(f"DEBUG: First section loaded and started in {load_end - load_start} ms")
            
            # If only one section exists, we're done (it will loop automatically)
            if len(existing_sections) == 1:
                print(f"DEBUG: Only one section exists, looping it automatically")
                return True
                
            # Queue the next section immediately
            queue_start = pygame.time.get_ticks()
            next_section = existing_sections[1] if len(existing_sections) > 1 else existing_sections[0]
            pygame.mixer.music.queue(next_section)
            self.next_track = os.path.basename(next_section)
            
            queue_end = pygame.time.get_ticks()
            print(f"DEBUG: Next section queued in {queue_end - queue_start} ms")
            
            # Build the complete queue for all remaining sections
            for i in range(2, len(existing_sections)):
                self.music_queue.append(existing_sections[i])
                
            # Always add the first section to the end to ensure looping
            self.music_queue.append(existing_sections[0])
            
            # For even more resilience, add another complete cycle
            for section in existing_sections:
                self.music_queue.append(section)
                
            print(f"DEBUG: Built complete music loop with {len(self.music_queue) + 2} sections")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to start section sequence: {e}")
            # Try fallback method
            try:
                # Use standard play_music as fallback
                self.play_music(first_section, loop=(len(existing_sections) == 1))
                
                # If we have more than one section, queue the rest
                if len(existing_sections) > 1:
                    for i in range(1, len(existing_sections)):
                        self.music_queue.append(existing_sections[i])
                    # Add the first section to create a loop
                    self.music_queue.append(existing_sections[0])
                    
                return True
            except Exception as e2:
                print(f"CRITICAL: Both section playback methods failed: {e2}")
                return False
    
    def _immediate_play_game_sequence(self):
        """
        Immediately starts playing the in-game music sequence from the beginning.
        """
        print(f"DEBUG: Starting immediate game sequence at {pygame.time.get_ticks()} ms")
        
        # Clear existing queue and state
        self.next_track = None
        self.music_queue = []
        
        # Define game section paths and check which ones exist
        base_path = "assets/audio/game/"
        all_sections = [
            f"{base_path}game_section1.wav",  # Forest Exploration
            f"{base_path}game_section2.wav",  # Village Theme
            f"{base_path}game_section3.wav",  # Ancient Ruins
            f"{base_path}game_section4.wav",  # Cave Discovery
            f"{base_path}game_section5.wav",  # Mountain Path
            f"{base_path}game_section6.wav",  # Ocean Journey
            f"{base_path}game_section7.wav",  # Dark Forest
            f"{base_path}game_section8.wav",  # Approaching Storm
            f"{base_path}game_section9.wav",  # Victory Fanfare
            f"{base_path}game_section10.wav", # Quest Completion
        ]
        
        # Check which section files actually exist
        existing_sections = []
        for section in all_sections:
            if os.path.exists(section):
                existing_sections.append(section)
            else:
                print(f"WARNING: Missing game music file: {section}")
        
        # If we have no section files, return error
        if len(existing_sections) == 0:
            print("ERROR: No game section files found.")
            return False
        
        # Timing info for debugging
        load_start = pygame.time.get_ticks()
        
        # Start with the first existing section
        first_section = existing_sections[0]
        print(f"DEBUG: Starting game sequence with {os.path.basename(first_section)}")
        
        try:
            # Direct loading and playing for faster response
            pygame.mixer.music.load(first_section)
            pygame.mixer.music.play(0)  # No loop - we'll queue the next track
            
            # Update current track
            self.current_track = os.path.basename(first_section)
            
            # Apply volume
            effective_volume = 0.0 if self.audio.get('is_muted', False) else (
                self.audio.get('music_volume', 0.5) * self.audio.get('master_volume', 0.7))
            pygame.mixer.music.set_volume(effective_volume)
            
            load_end = pygame.time.get_ticks()
            print(f"DEBUG: First game section loaded and started in {load_end - load_start} ms")
            
            # If only one section exists, we're done (it will loop automatically)
            if len(existing_sections) == 1:
                print(f"DEBUG: Only one game section exists, looping it automatically")
                return True
                
            # Queue the next section immediately
            queue_start = pygame.time.get_ticks()
            next_section = existing_sections[1] if len(existing_sections) > 1 else existing_sections[0]
            pygame.mixer.music.queue(next_section)
            self.next_track = os.path.basename(next_section)
            
            queue_end = pygame.time.get_ticks()
            print(f"DEBUG: Next game section queued in {queue_end - queue_start} ms")
            
            # Build the complete queue for all remaining sections
            for i in range(2, len(existing_sections)):
                self.music_queue.append(existing_sections[i])
                
            # Always add the first section to the end to ensure looping
            self.music_queue.append(existing_sections[0])
            
            # For even more resilience, add another complete cycle
            for section in existing_sections:
                self.music_queue.append(section)
                
            print(f"DEBUG: Built complete game music loop with {len(self.music_queue) + 2} sections")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to start game section sequence: {e}")
            # Try fallback method
            try:
                # Use standard play_music as fallback
                self.play_music(first_section, loop=(len(existing_sections) == 1))
                
                # If we have more than one section, queue the rest
                if len(existing_sections) > 1:
                    for i in range(1, len(existing_sections)):
                        self.music_queue.append(existing_sections[i])
                    # Add the first section to create a loop
                    self.music_queue.append(existing_sections[0])
                    
                return True
            except Exception as e2:
                print(f"CRITICAL: Both game section playback methods failed: {e2}")
                return False
    
    def _fallback_to_theme(self, theme_file: str):
        """
        Provides a fallback to play a standard theme if sections are missing.
        (Currently logs an error and returns False).

        Args:
            theme_file (str): The path to the fallback theme file.

        Returns:
            bool: Always returns False.
        """
        print(f"ERROR: Music section files missing. Unable to play theme: {theme_file}")
        return False

    def queue_section_music(self):
        """
        Queues all available menu music sections to play in a seamless loop.

        This method intelligently determines a starting track and queues the
        rest to create a continuous, non-repetitive music experience.
        """
        try:
            # Clear any existing queue
            self.next_track = None
            self.music_queue = []
            
            # Create a seamless sequence of all sections
            base_path = "assets/audio/"
            
            # Define all menu sections
            all_menu_sections = [
                f"{base_path}menu_section1.wav",
                f"{base_path}menu_section2.wav",
                f"{base_path}menu_section3.wav",
                f"{base_path}menu_section4.wav",
                f"{base_path}menu_section5.wav",
                f"{base_path}menu_section6.wav",
                f"{base_path}menu_section7.wav",
                f"{base_path}menu_section8.wav",
                f"{base_path}menu_section9.wav",
                f"{base_path}menu_section10.wav",
            ]
            
            # Get existing sections
            existing_sections = [s for s in all_menu_sections if os.path.exists(s)]
            
            if not existing_sections:
                print("ERROR: No menu sections available")
                return False
            
            # Determine starting section based on time of day if datetime is available
            try:
                import datetime
                current_hour = datetime.datetime.now().hour
                if 18 <= current_hour or current_hour <= 6:  # Evening/night (6PM-6AM)
                    first_section_name = "menu_section5.wav"  # Start with misty woods at night
                else:
                    first_section_name = "menu_section1.wav"  # Start with heroic intro during day
                
                # Make sure the chosen section exists, otherwise use first available
                first_section = f"{base_path}{first_section_name}"
                if not os.path.exists(first_section):
                    first_section = existing_sections[0]
            except (ImportError, IndexError):
                # Fallback if datetime not available or no sections found
                if existing_sections:
                    first_section = existing_sections[0]
                else:
                    print("ERROR: No menu sections available")
                    return False
            
            # Start with the determined first section
            print(f"Starting menu music with section: {os.path.basename(first_section)}")
            pygame.mixer.music.load(first_section)
            pygame.mixer.music.play(0)  # No loop - we'll queue the next track
            
            # Update current track
            self.current_track = os.path.basename(first_section)
            
            # Apply volume
            effective_volume = 0.0 if self.audio.get('is_muted', False) else (
                self.audio.get('music_volume', 0.5) * self.audio.get('master_volume', 0.7))
            pygame.mixer.music.set_volume(effective_volume)
            
            # If only one section exists, we're done (it will loop automatically)
            if len(existing_sections) == 1:
                print(f"Only one menu section exists, looping it")
                pygame.mixer.music.play(-1)  # Loop indefinitely
                return True
            
            # Queue all remaining sections in order
            current_index = existing_sections.index(first_section)
            for i in range(1, len(existing_sections)):
                next_index = (current_index + i) % len(existing_sections)
                next_section = existing_sections[next_index]
                print(f"Queueing next section: {os.path.basename(next_section)}")
                pygame.mixer.music.queue(next_section)
            
            # Set up the event for when a track ends
            pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
            
            return True
            
        except Exception as e:
            print(f"Error in queue_section_music: {e}")
            return False

    def queue_game_music(self):
        """
        Queues all available in-game music sections for seamless playback.
        """
        try:
            # First, analyze music files to identify potential issues
            game_sections_available = self._analyze_game_music_files()
            
            # If no game sections found, return false
            if not game_sections_available:
                print("ERROR: No game music sections found")
                return False

            # Clear any existing queue
            self.next_track = None
            self.music_queue = []
            
            # Create a seamless sequence of all game sections
            base_path = "assets/audio/game/"
            
            # Define all game sections
            all_game_sections = [
                f"{base_path}game_section1.wav",  # Forest Exploration
                f"{base_path}game_section2.wav",  # Village Theme
                f"{base_path}game_section3.wav",  # Ancient Ruins
                f"{base_path}game_section4.wav",  # Cave Discovery
                f"{base_path}game_section5.wav",  # Mountain Path
                f"{base_path}game_section6.wav",  # Ocean Journey
                f"{base_path}game_section7.wav",  # Dark Forest
                f"{base_path}game_section8.wav",  # Approaching Storm
                f"{base_path}game_section9.wav",  # Victory Fanfare
                f"{base_path}game_section10.wav", # Quest Completion
            ]
            
            # Get existing sections
            existing_sections = [s for s in all_game_sections if os.path.exists(s)]
            
            # Determine starting section based on game context or use first available
            # For now, we'll just use the first available section
            first_section = existing_sections[0]
                
            # Start with the first section
            print(f"Starting game music with section: {os.path.basename(first_section)}")
            self.play_music(first_section, loop=False)
            
            # Queue the next sections
            if len(existing_sections) > 1:
                next_section = existing_sections[1]
                pygame.mixer.music.queue(next_section)
                self.next_track = os.path.basename(next_section)
                print(f"Queued next section: {self.next_track}")
                
                # Add remaining sections to our queue
                for i in range(2, len(existing_sections)):
                    self.music_queue.append(existing_sections[i])
                
                # Add a complete extra cycle for resilience
                for section in existing_sections:
                    self.music_queue.append(section)
                    
                print(f"Built complete game music loop with {len(existing_sections)} sections")
                return True
            else:
                # Only one section exists, loop it
                print(f"Only one game section exists, looping it")
                pygame.mixer.music.play(-1)  # Loop indefinitely
                return True
                
        except Exception as e:
            print(f"Error in queue_game_music: {e}")
            return False

    def stop_music(self):
        """
        Stops the currently playing music and clears the queue.
        """
        if pygame.mixer and pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            print(f"DEBUG: Music stopped - {getattr(self, 'current_track', 'unknown')}")
            self.current_track = None
            # Clear the queue
            self.music_queue = []
            self.next_track = None
    
    def set_fullscreen_callback(self, callback: callable):
        """
        Sets a callback function to be executed when fullscreen is toggled.

        Args:
            callback (callable): The function to call. It should handle the
                                 re-initialization of the display surface.
        """
        self.fullscreen_callback = callback
    
    def toggle_fullscreen(self):
        """
        Toggles the fullscreen mode and triggers the video change callback.
        """
        self.video['fullscreen'] = not self.video['fullscreen']
        self.save_settings()
        self.trigger_video_change()
        logger.info(f"Fullscreen toggled: {self.video['fullscreen']}")
    
    def set_resolution(self, width: int, height: int):
        """
        Sets the screen resolution and triggers the video change callback.

        Args:
            width (int): The new screen width in pixels.
            height (int): The new screen height in pixels.
        """
        self.video['resolution'] = (width, height)
        self.save_settings()
        self.trigger_video_change()
    
    def cycle_resolution(self, direction: int = 1):
        """
        Cycles through the list of available screen resolutions.

        Args:
            direction (int, optional): The direction to cycle. 1 for next,
                                     -1 for previous. Defaults to 1.
        """
        current_res = tuple(self.video['resolution']) # Ensure tuple for comparison
        try:
            current_index = AVAILABLE_RESOLUTIONS.index(current_res)
        except ValueError:
            current_index = 0 # Default to first if current not found
            
        new_index = (current_index + direction) % len(AVAILABLE_RESOLUTIONS)
        self.video['resolution'] = AVAILABLE_RESOLUTIONS[new_index]
        self.save_settings()
        self.trigger_video_change()
        logger.info(f"Resolution changed to: {self.video['resolution']}")
    
    def set_gui_scale(self, scale: float):
        """
        Sets the scale factor for GUI elements.

        Args:
            scale (float): The new GUI scale factor (e.g., 1.0 for default).
        """
        # Add validation/clamping if needed (e.g., 0.5 to 3.0)
        self.video['gui_scale'] = float(scale)
        self.save_settings()
        # Note: Applying GUI scale might require UI elements to be recreated or redrawn.
        # This might need a separate callback or signal.
        logger.info(f"GUI Scale set to: {self.video['gui_scale']}")
            
    def toggle_vsync(self):
        """
        Toggles the vertical sync (VSync) setting.
        """
        self.video['vsync'] = not self.video['vsync']
        self.save_settings()
        # VSync toggle might also require display reinitialization
        self.trigger_video_change()
        logger.info(f"VSync toggled: {self.video['vsync']}")
            
    def toggle_particles(self):
        """
        Toggles the particle effects setting.
        """
        self.video['particles_enabled'] = not self.video['particles_enabled']
        self.save_settings()
        # No need to reinitialize display, just update the setting
        if self.video_change_callback:
            self.video_change_callback()  # Call without passing video - the callback can access it if needed
        logger.info(f"Particles toggled: {self.video['particles_enabled']}")
            
    def set_volume(self, volume_type: str, value: float):
        """
        Sets the volume for a specific audio channel (e.g., music, sfx).

        Args:
            volume_type (str): The audio channel key (e.g., 'master_volume', 'music_volume').
            value (float): The new volume level (0.0 to 1.0).
        """
        if volume_type in self.audio:
            # Clamp value to valid range
            value = max(0.0, min(1.0, value))
            self.audio[volume_type] = value
            self.save_settings()
            
            # If changing music volume, update current playback
            if volume_type in ('music_volume', 'master_volume') and pygame.mixer.music.get_busy():
                effective_volume = self.audio['music_volume'] * self.audio['master_volume']
                if self.audio.get('is_muted', False):
                    effective_volume = 0
                pygame.mixer.music.set_volume(effective_volume)
                print(f"DEBUG: Music volume changed - {volume_type}={value:.2f}, effective={effective_volume:.2f}")
    
    def get_keybind(self, player: str, action: str) -> int:
        """
        Retrieves the keybinding for a specific player and action.

        Args:
            player (str): The player identifier (e.g., 'player1').
            action (str): The action identifier (e.g., 'up', 'attack').

        Returns:
            int: The Pygame key code for the action, or None if not found.
        """
        if player in self.keybinds and action in self.keybinds[player]:
            return self.keybinds[player][action]
        return None
    
    def set_keybind(self, player: str, action: str, key: int):
        """
        Sets the keybinding for a specific player and action.

        Args:
            player (str): The player identifier (e.g., 'player1').
            action (str): The action identifier (e.g., 'up').
            key (int): The new Pygame key code to assign.
        """
        if player in self.keybinds and action in self.keybinds[player]:
            self.keybinds[player][action] = key
            self.save_settings()
    
    def apply_audio_settings(self):
        """
        Applies the current audio settings to the Pygame mixer.

        This is typically called after changing volume or mute status.
        """
        if pygame.mixer.get_init():
            try:
                volume = 0.0 if self.audio['is_muted'] else self.audio["music_volume"]
                pygame.mixer.music.set_volume(volume)
                logger.debug(f"Applied music volume: {volume}")
            except pygame.error as e:
                logger.error(f"Error setting music volume: {e}")
        else:
             logger.warning("Mixer not initialized, cannot apply audio settings.")

    def set_music_volume(self, volume: float):
        """
        Sets the dedicated music volume level.

        Args:
            volume (float): The new music volume (0.0 to 1.0).
        """
        self.audio["music_volume"] = max(0.0, min(1.0, volume))
        self.apply_audio_settings()

    def set_sound_volume(self, volume: float):
        """
        Sets the dedicated sound effects (SFX) volume level.

        Args:
            volume (float): The new SFX volume (0.0 to 1.0).
        """
        self.audio["sfx_volume"] = max(0.0, min(1.0, volume))
        # Applying sound volume immediately isn't straightforward
        # as individual sounds use this value when played.

    def toggle_mute(self):
        """
        Toggles the global mute state for all audio.
        """
        self.audio['is_muted'] = not self.audio.get('is_muted', False) # Use .get for safety
        self.apply_audio_settings()
        logger.info(f"Audio {'muted' if self.audio['is_muted'] else 'unmuted'}.")

    def play_sound(self, sound_name: str):
        """
        Plays a sound effect by name, respecting mute and volume settings.

        Args:
            sound_name (str): The name of the sound file (without extension)
                              located in `assets/audio/`.
        """
        if pygame.mixer.get_init() and not self.audio.get('is_muted', False):
            try:
                # Load sound from assets (assuming a helper function or manager exists)
                # For now, we'll simulate loading
                sound_path = f"assets/audio/{sound_name}.wav"
                if os.path.exists(sound_path):
                    sound = pygame.mixer.Sound(sound_path)
                    volume = self.audio["sfx_volume"]
                    sound.set_volume(volume)
                    sound.play()
                    logger.debug(f"Playing sound: {sound_name} at volume: {volume}")
                else:
                    logger.warning(f"Sound file not found: {sound_path}")
            except pygame.error as e:
                logger.error(f"Error playing sound {sound_name}: {e}")
            except FileNotFoundError:
                logger.warning(f"Sound file not found: assets/audio/{sound_name}.wav")
        elif self.audio.get('is_muted', False):
             logger.debug(f"Sound {sound_name} not played because audio is muted.")

    def get_keybind(self, player: str, action: str) -> int:
        """
        Retrieves the keybinding for a specific player and action.

        Args:
            player (str): The player identifier (e.g., 'player1').
            action (str): The action identifier (e.g., 'up').

        Returns:
            int: The Pygame key code, or None if not found.
        """
        return self.keybinds.get(player, {}).get(action, None)

    def set_keybind(self, player: str, action: str, key: int):
        """
        Sets the keybinding for a specific player and action and saves it.

        Args:
            player (str): The player identifier (e.g., 'player1').
            action (str): The action identifier (e.g., 'up').
            key (int): The new Pygame key code.
        """
        if player in self.keybinds and action in self.keybinds[player]:
            self.keybinds[player][action] = key
            self.save_settings()

    def set_video_change_callback(self, callback: callable):
        """
        Registers a callback function to be called when video settings change.

        Args:
            callback (callable): The function to execute on video setting changes.
        """
        self.video_change_callback = callback
        
    def trigger_video_change(self):
         """
         Executes the registered video change callback, if it exists.

         This is called internally when settings like resolution or fullscreen
         mode are changed.
         """
         if self.video_change_callback:
             self.video_change_callback()
         else:
             logger.warning("Video change triggered, but no callback is set.")

    def _analyze_music_files(self):
        """
        Performs a diagnostic analysis of all music files.

        This method checks for the existence, size, and duration of menu,
        game, and theme music files, printing a report to the console. It helps
        in debugging missing or corrupt audio assets.
        """
        print("\n=== MUSIC FILE ANALYSIS ===")
        
        # ===== Analyze Menu Music Files =====
        # Get all menu section files
        base_path = "assets/audio/"
        menu_sections = [
            f"{base_path}menu_section1.wav",
            f"{base_path}menu_section2.wav",
            f"{base_path}menu_section3.wav",
            f"{base_path}menu_section4.wav",
            f"{base_path}menu_section5.wav",
            f"{base_path}menu_section6.wav",
            f"{base_path}menu_section7.wav",
            f"{base_path}menu_section8.wav",
            f"{base_path}menu_section9.wav",
            f"{base_path}menu_section10.wav",
        ]
        
        # Check which menu files exist
        print("\nMenu Music File existence check:")
        for section in menu_sections:
            status = "EXISTS" if os.path.exists(section) else "MISSING"
            print(f"  {section}: {status}")
        
        # Check menu file sizes
        print("\nMenu Music File size analysis:")
        for section in menu_sections:
            if os.path.exists(section):
                size_bytes = os.path.getsize(section)
                size_kb = size_bytes / 1024
                print(f"  {section}: {size_bytes} bytes ({size_kb:.2f} KB)")
                
                # Check if sizes are significantly different
                if section != menu_sections[0] and os.path.exists(menu_sections[0]):
                    first_size = os.path.getsize(menu_sections[0])
                    diff_pct = abs(size_bytes - first_size) / first_size * 100
                    if diff_pct > 5:  # More than 5% difference
                        print(f"    WARNING: Size differs from first section by {diff_pct:.1f}%")
        
        # ===== Analyze Game Music Files =====
        # Get all game section files
        game_base_path = "assets/audio/game/"
        game_sections = [
            f"{game_base_path}game_section1.wav",
            f"{game_base_path}game_section2.wav",
            f"{game_base_path}game_section3.wav",
            f"{game_base_path}game_section4.wav",
            f"{game_base_path}game_section5.wav",
            f"{game_base_path}game_section6.wav",
            f"{game_base_path}game_section7.wav",
            f"{game_base_path}game_section8.wav",
            f"{game_base_path}game_section9.wav",
            f"{game_base_path}game_section10.wav",
        ]
        
        # Check if game directory exists
        game_dir = "assets/audio/game"
        if not os.path.exists(game_dir):
            print(f"\nGAME MUSIC WARNING: Directory {game_dir} does not exist!")
        else:
            # Check which game files exist
            print("\nGame Music File existence check:")
            for section in game_sections:
                status = "EXISTS" if os.path.exists(section) else "MISSING"
                print(f"  {section}: {status}")
            
            # Check game file sizes
            print("\nGame Music File size analysis:")
            for section in game_sections:
                if os.path.exists(section):
                    size_bytes = os.path.getsize(section)
                    size_kb = size_bytes / 1024
                    print(f"  {section}: {size_bytes} bytes ({size_kb:.2f} KB)")
        
        # ===== Analyze Combined Theme Files =====
        # Check main theme files
        theme_files = [
            f"{base_path}menu_theme.wav",
            f"{base_path}enhanced_menu_theme.wav",
            f"{base_path}game_theme.wav",
            f"{base_path}enhanced_game_theme.wav",
        ]
        
        print("\nTheme File existence check:")
        for file in theme_files:
            status = "EXISTS" if os.path.exists(file) else "MISSING"
            print(f"  {file}: {status}")
        
        # Try to analyze actual durations if wave module is available
        try:
            import wave
            print("\nDuration analysis:")
            
            # Analyze menu sections durations
            print("  Menu Music Sections:")
            for section in menu_sections:
                if os.path.exists(section):
                    try:
                        with wave.open(section, 'rb') as w:
                            # Calculate duration in seconds
                            frames = w.getnframes()
                            rate = w.getframerate()
                            duration = frames / rate
                            print(f"    {section}: {duration:.2f} seconds ({frames} frames @ {rate} Hz)")
                    except Exception as e:
                        print(f"    {section}: ERROR analyzing - {e}")
            
            # Analyze game sections durations
            print("  Game Music Sections:")
            for section in game_sections:
                if os.path.exists(section):
                    try:
                        with wave.open(section, 'rb') as w:
                            # Calculate duration in seconds
                            frames = w.getnframes()
                            rate = w.getframerate()
                            duration = frames / rate
                            print(f"    {section}: {duration:.2f} seconds ({frames} frames @ {rate} Hz)")
                    except Exception as e:
                        print(f"    {section}: ERROR analyzing - {e}")
            
            # Analyze theme files durations
            print("  Theme Files:")
            for file in theme_files:
                if os.path.exists(file):
                    try:
                        with wave.open(file, 'rb') as w:
                            # Calculate duration in seconds
                            frames = w.getnframes()
                            rate = w.getframerate()
                            duration = frames / rate
                            print(f"    {file}: {duration:.2f} seconds ({frames} frames @ {rate} Hz)")
                    except Exception as e:
                        print(f"    {file}: ERROR analyzing - {e}")
                        
        except ImportError:
            print("\nCould not analyze durations (wave module not available)")
            
        print("\n=== END ANALYSIS ===\n")
        
        # Return True to make it usable in chains of conditions
        return True 

    def _analyze_game_music_files(self):
        """
        Performs a diagnostic analysis of in-game music files.

        Returns:
            bool: True if at least one game music section file exists, False otherwise.
        """
        print("\n=== GAME MUSIC FILE ANALYSIS ===\n")
        
        # Define game section paths and check which ones exist
        base_path = "assets/audio/game/"
        all_game_sections = [
            f"{base_path}game_section1.wav",  # Forest Exploration
            f"{base_path}game_section2.wav",  # Village Theme
            f"{base_path}game_section3.wav",  # Ancient Ruins
            f"{base_path}game_section4.wav",  # Cave Discovery
            f"{base_path}game_section5.wav",  # Mountain Path
            f"{base_path}game_section6.wav",  # Ocean Journey
            f"{base_path}game_section7.wav",  # Dark Forest
            f"{base_path}game_section8.wav",  # Approaching Storm
            f"{base_path}game_section9.wav",  # Victory Fanfare
            f"{base_path}game_section10.wav", # Quest Completion
        ]
        
        # Check if game directory exists
        game_dir = "assets/audio/game"
        if not os.path.exists(game_dir):
            print(f"WARNING: Game music directory does not exist: {game_dir}")
            print("Game sections will not be available.")
            return False
            
        # Check which files exist
        print("File existence check:")
        for section in all_game_sections:
            status = "EXISTS" if os.path.exists(section) else "MISSING"
            print(f"  {section}: {status}")
        
        # Count existing sections
        existing_sections = [s for s in all_game_sections if os.path.exists(s)]
        print(f"\nFound {len(existing_sections)} of {len(all_game_sections)} game music sections")
        
        # Check fallback theme files
        fallback_paths = [
            "assets/audio/game_theme.wav",
            "assets/audio/enhanced_game_theme.wav"
        ]
        
        print("\nFallback theme check:")
        for path in fallback_paths:
            status = "EXISTS" if os.path.exists(path) else "MISSING"
            print(f"  {path}: {status}")
            
        # Try to analyze actual durations if wave module is available
        try:
            import wave
            print("\nDuration analysis:")
            for section in existing_sections:
                try:
                    with wave.open(section, 'rb') as w:
                        # Calculate duration in seconds
                        frames = w.getnframes()
                        rate = w.getframerate()
                        duration = frames / rate
                        print(f"  {section}: {duration:.2f} seconds ({frames} frames @ {rate} Hz)")
                except Exception as e:
                    print(f"  {section}: ERROR analyzing - {e}")
                    
            # Check fallback themes
            for path in fallback_paths:
                if os.path.exists(path):
                    try:
                        with wave.open(path, 'rb') as w:
                            frames = w.getnframes()
                            rate = w.getframerate()
                            duration = frames / rate
                            print(f"  {path}: {duration:.2f} seconds ({frames} frames @ {rate} Hz)")
                    except Exception as e:
                        print(f"  {path}: ERROR analyzing - {e}")
        except ImportError:
            print("\nCould not analyze durations (wave module not available)")
            
        print("\n=== END GAME MUSIC ANALYSIS ===\n")
        return len(existing_sections) > 0 

    def _analyze_menu_music_files(self):
        """
        Performs a diagnostic analysis of menu music files.

        Returns:
            bool: True if at least one menu music section file exists, False otherwise.
        """
        print("\n=== MENU MUSIC FILE ANALYSIS ===\n")
        
        # Define menu section paths and check which ones exist
        base_path = "assets/audio/"
        all_menu_sections = [
            f"{base_path}menu_section1.wav",  # Heroic Intro
            f"{base_path}menu_section2.wav",  # Calm Town-like Section
            f"{base_path}menu_section3.wav",  # Energetic Battle-like Section
            f"{base_path}menu_section4.wav",  # Resolving Passage
            f"{base_path}menu_section5.wav",  # Misty Woods Intro
            f"{base_path}menu_section6.wav",
            f"{base_path}menu_section7.wav",
            f"{base_path}menu_section8.wav",
            f"{base_path}menu_section9.wav",
            f"{base_path}menu_section10.wav",
        ]
        
        # Check which files exist
        print("File existence check:")
        existing_sections = []
        for section in all_menu_sections:
            status = "EXISTS" if os.path.exists(section) else "MISSING"
            print(f"  {section}: {status}")
            if os.path.exists(section):
                existing_sections.append(section)
        
        # Count existing sections
        print(f"\nFound {len(existing_sections)} of {len(all_menu_sections)} menu music sections")
        
        # Check fallback theme files
        fallback_paths = [
            "assets/audio/menu_theme.wav",
            "assets.audio/enhanced_menu_theme.wav"
        ]
        
        print("\nFallback theme check:")
        for path in fallback_paths:
            status = "EXISTS" if os.path.exists(path) else "MISSING"
            print(f"  {path}: {status}")
            
        # Try to analyze actual durations if wave module is available
        try:
            import wave
            print("\nDuration analysis:")
            for section in existing_sections:
                try:
                    with wave.open(section, 'rb') as w:
                        # Calculate duration in seconds
                        frames = w.getnframes()
                        rate = w.getframerate()
                        duration = frames / rate
                        print(f"  {section}: {duration:.2f} seconds ({frames} frames @ {rate} Hz)")
                except Exception as e:
                    print(f"  {section}: ERROR analyzing - {e}")
                    
            # Check fallback themes
            for path in fallback_paths:
                if os.path.exists(path):
                    try:
                        with wave.open(path, 'rb') as w:
                            frames = w.getnframes()
                            rate = w.getframerate()
                            duration = frames / rate
                            print(f"  {path}: {duration:.2f} seconds ({frames} frames @ {rate} Hz)")
                    except Exception as e:
                        print(f"  {path}: ERROR analyzing - {e}")
        except ImportError:
            print("\nCould not analyze durations (wave module not available)")
            
        print("\n=== END MENU MUSIC ANALYSIS ===\n")
        return len(existing_sections) > 0 

    def start_seamless_menu_music(self):
        """
        Starts a seamless, looping playback of all available menu music sections.

        This method is the recommended way to start menu music. It handles
        stopping previous tracks, building a resilient queue, and starting
        playback.
        """
        try:
            # Clear any existing queue and state
            self.next_track = None
            self.music_queue = []
            
            # Stop any currently playing music
            pygame.mixer.music.stop()
            
            # Define all menu sections in proper order
            base_path = "assets/audio/"
            all_menu_sections = [
                f"{base_path}menu_section1.wav",   # Heroic Intro
                f"{base_path}menu_section2.wav",   # Calm Town-like Section  
                f"{base_path}menu_section3.wav",   # Energetic Battle-like Section
                f"{base_path}menu_section4.wav",   # Mystical Bridge
                f"{base_path}menu_section5.wav",   # Misty Woods Intro
                f"{base_path}menu_section6.wav",   # Descending Arpeggio
                f"{base_path}menu_section7.wav",   # Wave Pattern
                f"{base_path}menu_section8.wav",   # Cascading
                f"{base_path}menu_section9.wav",   # Mountain
                f"{base_path}menu_section10.wav",  # Wandering
            ]
            
            # Filter to only existing sections
            existing_sections = [s for s in all_menu_sections if os.path.exists(s)]
            
            if not existing_sections:
                print("ERROR: No menu sections available for seamless playback")
                return False
            
            print(f"Found {len(existing_sections)} menu sections for seamless playback")
            
            # Start with the first section
            first_section = existing_sections[0]
            print(f"Starting seamless menu music loop with {len(existing_sections)} sections")
            
            # Load and play the first section
            pygame.mixer.music.load(first_section)
            pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
            pygame.mixer.music.play(0)  # Play once, no loop
            
            # Update tracking
            self.current_track = os.path.basename(first_section)
            
            # Apply volume
            effective_volume = 0.0 if self.audio.get('is_muted', False) else (
                self.audio.get('music_volume', 0.5) * self.audio.get('master_volume', 0.7))
            pygame.mixer.music.set_volume(effective_volume)
            
            # Build complete queue for seamless looping
            # Add all remaining sections to the queue
            for i in range(1, len(existing_sections)):
                self.music_queue.append(existing_sections[i])
            
            # Add the first section back to the end to create a seamless loop
            self.music_queue.append(existing_sections[0])
            
            # Add another complete cycle for extra resilience
            for section in existing_sections:
                self.music_queue.append(section)
            
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to start seamless menu music: {e}")
            return False