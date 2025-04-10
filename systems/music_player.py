import pygame
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class MusicPlayerSystem:
    """A system for browsing and playing music tracks in-game"""
    
    def __init__(self, options_system):
        """Initialize the music player with a reference to the options system"""
        self.options = options_system
        self.tracks = []  # List of all available tracks
        self.menu_tracks = []  # Menu sections
        self.game_tracks = []  # Game sections
        self.current_index = 0  # Currently selected track index
        self.playing = False  # Is a track currently playing
        self.active = False  # Is the music player UI active
        self.previous_track = None  # Track that was playing before entering player
        self.font = None
        self.initialize_font()
        self.scan_music_files()
        
    def initialize_font(self):
        """Initialize the font for rendering track names"""
        try:
            self.font = pygame.font.Font('assets/fonts/runic.ttf', 20)
            if not self.font:
                self.font = pygame.font.SysFont('Arial', 18)
        except:
            self.font = pygame.font.SysFont('Arial', 18)
    
    def scan_music_files(self):
        """Scan for all available music files"""
        self.tracks = []
        self.menu_tracks = []
        self.game_tracks = []
        
        # Check for menu section tracks
        menu_base_path = "assets/audio/"
        for i in range(1, 11):
            file_path = f"{menu_base_path}menu_section{i}.wav"
            if os.path.exists(file_path):
                track = {
                    'path': file_path,
                    'name': f"Menu Section {i}",
                    'description': self._get_menu_section_description(i),
                    'type': 'menu'
                }
                self.tracks.append(track)
                self.menu_tracks.append(track)
        
        # Check for game section tracks
        game_base_path = "assets/audio/game/"
        for i in range(1, 11):
            file_path = f"{game_base_path}game_section{i}.wav"
            if os.path.exists(file_path):
                track = {
                    'path': file_path,
                    'name': f"Game Section {i}",
                    'description': self._get_game_section_description(i),
                    'type': 'game'
                }
                self.tracks.append(track)
                self.game_tracks.append(track)
        
        # Add any other sound effects we might want to include
        sfx_paths = {
            'Menu Click': f"{menu_base_path}menu_click.wav",
            'Menu Select': f"{menu_base_path}menu_select.wav",
            'Attack Sound': f"{menu_base_path}attack.wav"
        }
        
        for name, path in sfx_paths.items():
            if os.path.exists(path):
                track = {
                    'path': path,
                    'name': name,
                    'description': f"Sound effect: {name}",
                    'type': 'sfx'
                }
                self.tracks.append(track)
    
    def _get_menu_section_description(self, section_num):
        """Get a description for a menu section by number"""
        descriptions = {
            1: "Heroic Intro - Ascending scale",
            2: "Calm Town-like Section - Arpeggio pattern",
            3: "Energetic Battle-like Section - Descending scale",
            4: "Resolving Passage - Melodic pattern with C5 focus",
            5: "Misty Woods Intro - Complex melody with varied intervals",
            6: "Descending Arpeggio - C5-based descending pattern",
            7: "Wave Pattern - Smooth up/down melodic movement",
            8: "Cascading - Pattern with wide intervals", 
            9: "Mountain - Melody that rises then falls",
            10: "Wandering - Melody with varied intervals"
        }
        return descriptions.get(section_num, f"Menu Section {section_num}")

    def _get_game_section_description(self, section_num):
        """Get a description for a game section by number"""
        descriptions = {
            1: "Forest Exploration - Peaceful C4-based melody",
            2: "Village Theme - Bright, E4-based melody",
            3: "Ancient Ruins - Mysterious A-minor theme",
            4: "Cave Discovery - Deep, resonant G-minor melody",
            5: "Mountain Path - Bold, adventurous D-theme",
            6: "Ocean Journey - Flowing F-major pattern",
            7: "Dark Forest - Tense B-minor theme",
            8: "Approaching Storm - Dynamic E-minor progression",
            9: "Victory Fanfare - Triumphant C-major ascent",
            10: "Quest Completion - Resolved G-major theme"
        }
        return descriptions.get(section_num, f"Game Section {section_num}")
    
    def activate(self):
        """Activate the music player UI"""
        if not self.active:
            # Store currently playing track
            self.previous_track = self.options.current_track
            
            # Store current end event and disable it
            self.previous_end_event = pygame.mixer.music.get_endevent()
            pygame.mixer.music.set_endevent()  # Disable end events
            
            # Completely stop all music and clear any queues
            pygame.mixer.music.stop()
            self.options.stop_music()
            self.options.next_track = None
            self.options.music_queue = []
            self.playing = False
            
            # Wait a brief moment to ensure playback has fully stopped
            pygame.time.wait(50)
            
            # Double check that music is stopped
            if pygame.mixer.music.get_busy():
                logger.warning("Music still playing after stop command, forcing stop again")
                pygame.mixer.music.stop()
            
            # Activate the player UI
            self.active = True
            
            # Reset selection to first track
            self.current_index = 0
            
            # Refresh track list
            self.scan_music_files()
            
            logger.info("Music player activated - all music stopped")
            return True
        return False
    
    def deactivate(self):
        """Deactivate the music player and restore previous music"""
        if self.active:
            # Stop any playing track
            if self.playing:
                pygame.mixer.music.stop()
                self.options.stop_music()
                self.playing = False
            
            # Restore the previous end event
            if hasattr(self, 'previous_end_event'):
                pygame.mixer.music.set_endevent(self.previous_end_event)
            else:
                # Default back to the event from the options system
                pygame.mixer.music.set_endevent(self.options.music_end_event)
            
            # Restore previous music if any
            if self.previous_track:
                logger.info(f"Restoring previous music: {self.previous_track}")
                if self.previous_track.startswith("game_section"):
                    self.options.queue_game_music()
                else:
                    self.options.queue_section_music()
            
            # Deactivate the player UI
            self.active = False
            logger.info("Music player deactivated")
            return True
        return False
    
    def play_selected_track(self):
        """Play the currently selected track"""
        if self.current_index < len(self.tracks):
            # Get the selected track
            track = self.tracks[self.current_index]
            
            # Make sure any currently playing music is stopped
            pygame.mixer.music.stop()
            self.options.stop_music()
            
            # Play the selected track
            if track['type'] == 'sfx':
                # For sound effects, just play them once
                self.options.play_sound(os.path.basename(track['path']).split('.')[0])
                self.playing = False
            else:
                # For music tracks, loop them
                try:
                    # Directly load and play music for better control
                    pygame.mixer.music.load(track['path'])
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    self.options.current_track = os.path.basename(track['path'])
                    self.playing = True
                    
                    # Make sure volume is set correctly
                    effective_volume = 0.0 if self.options.audio.get('is_muted', False) else (
                        self.options.audio.get('music_volume', 0.5) * self.options.audio.get('master_volume', 0.7))
                    pygame.mixer.music.set_volume(effective_volume)
                except Exception as e:
                    logger.error(f"Error playing track: {e}")
                    self.playing = False
                    return False
                
            logger.info(f"Playing track: {track['name']}")
            return True
        return False
    
    def stop_playback(self):
        """Stop the currently playing track"""
        if self.playing:
            pygame.mixer.music.stop()
            self.options.stop_music()
            self.playing = False
            logger.info("Stopped music playback")
            return True
        return False
    
    def toggle_playback(self):
        """Toggle play/pause of the currently selected track"""
        if self.playing:
            return self.stop_playback()
        else:
            return self.play_selected_track()
    
    def next_track(self):
        """Select the next track"""
        if len(self.tracks) > 0:
            self.current_index = (self.current_index + 1) % len(self.tracks)
            logger.info(f"Selected track: {self.tracks[self.current_index]['name']}")
            return True
        return False
    
    def previous_track(self):
        """Select the previous track"""
        if len(self.tracks) > 0:
            self.current_index = (self.current_index - 1) % len(self.tracks)
            logger.info(f"Selected track: {self.tracks[self.current_index]['name']}")
            return True
        return False
    
    def render(self, screen, position=(100, 100), width=600, height=400):
        """Render the music player UI at the given position"""
        if not self.active:
            return
            
        # Draw background
        bg_rect = pygame.Rect(position[0], position[1], width, height)
        pygame.draw.rect(screen, (40, 40, 60), bg_rect)
        pygame.draw.rect(screen, (100, 100, 120), bg_rect, 3)
        
        # Draw title
        title_text = self.font.render("RUNIC LANDS MUSIC PLAYER", True, (220, 220, 240))
        screen.blit(title_text, (position[0] + 20, position[1] + 20))
        
        # Draw divider
        pygame.draw.line(screen, (100, 100, 120), 
                         (position[0] + 10, position[1] + 50),
                         (position[0] + width - 10, position[1] + 50), 2)
        
        # Draw track list
        if len(self.tracks) == 0:
            no_tracks_text = self.font.render("No music tracks found", True, (200, 200, 200))
            screen.blit(no_tracks_text, (position[0] + 20, position[1] + 70))
        else:
            # Calculate visible tracks (5 tracks visible at once)
            start_index = max(0, self.current_index - 2)
            end_index = min(len(self.tracks), start_index + 5)
            
            # Draw each visible track
            y_offset = 70
            for i in range(start_index, end_index):
                track = self.tracks[i]
                
                # Highlight selected track
                if i == self.current_index:
                    select_rect = pygame.Rect(position[0] + 10, position[1] + y_offset - 5, width - 20, 30)
                    pygame.draw.rect(screen, (60, 60, 100), select_rect)
                    pygame.draw.rect(screen, (120, 120, 180), select_rect, 1)
                    
                    # Show play/pause indicator
                    if self.playing and self.options.current_track == os.path.basename(track['path']):
                        status = "■ PLAYING"
                        status_color = (180, 255, 180)
                    else:
                        status = "▶ PLAY"
                        status_color = (220, 220, 240)
                        
                    status_text = self.font.render(status, True, status_color)
                    screen.blit(status_text, (position[0] + width - 120, position[1] + y_offset))
                
                # Draw track name with type indicator
                type_color = {
                    'menu': (180, 220, 255),
                    'game': (255, 220, 180),
                    'sfx': (220, 180, 255)
                }.get(track['type'], (200, 200, 200))
                
                track_text = self.font.render(track['name'], True, type_color)
                screen.blit(track_text, (position[0] + 20, position[1] + y_offset))
                
                y_offset += 30
            
            # Draw selected track description
            if self.current_index < len(self.tracks):
                selected_track = self.tracks[self.current_index]
                
                # Draw divider
                pygame.draw.line(screen, (100, 100, 120), 
                                (position[0] + 10, position[1] + height - 70),
                                (position[0] + width - 10, position[1] + height - 70), 2)
                
                # Draw track details
                details_text = self.font.render(selected_track['description'], True, (220, 220, 220))
                screen.blit(details_text, (position[0] + 20, position[1] + height - 50))
                
                # Draw file path
                path_text = self.font.render(selected_track['path'], True, (180, 180, 180))
                screen.blit(path_text, (position[0] + 20, position[1] + height - 25))
        
        # Draw controls
        controls_text = self.font.render("↑/↓: Select Track   Space: Play/Pause   Esc: Close", True, (200, 200, 200))
        screen.blit(controls_text, (position[0] + 20, position[1] + height - 100))
    
    def handle_event(self, event):
        """Handle input events for the music player"""
        if not self.active:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.deactivate()
                return True
            elif event.key == pygame.K_UP:
                self.previous_track()
                return True
            elif event.key == pygame.K_DOWN:
                self.next_track()
                return True
            elif event.key == pygame.K_SPACE:
                self.toggle_playback()
                return True
                
        return False 