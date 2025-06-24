import pygame
import sys
from enum import Enum, auto

# Standard imports assuming main.py is the entry point
# and ui_elements.py is in the root directory
from ui_elements import Button, Slider, Label, ToggleButton
from systems.options import OptionsSystem, AVAILABLE_RESOLUTIONS
from systems.music_player import MusicPlayerSystem  # Import the music player system

class OptionsMenuState(Enum):
    MAIN = auto()
    VIDEO = auto()
    AUDIO = auto()
    CONTROLS = auto()
    REBIND = auto()
    MUSIC_PLAYER = auto()  # Add music player state

class OptionsMenu:
    def __init__(self, screen_size, options_system: OptionsSystem):
        self.screen_size = screen_size
        self.options = options_system
        self.state = OptionsMenuState.MAIN
        self.font = pygame.font.Font(None, 32) # Slightly smaller default font
        self.title_font = pygame.font.Font(None, 48)
        self.colors = {
            'background': (20, 30, 40),
            'button': (70, 70, 200),
            'button_hover': (100, 100, 255),
            'button_text': (255, 255, 255),
            'title': (200, 200, 255),
            'text': (220, 220, 220),
            'slider_bg': (50, 50, 100),
            'slider_handle': (100, 100, 255)
        }
        
        # UI Elements
        self.elements = {}
        self.rebind_info = None # Store player/action for rebinding
        
        # Initialize Music Player System
        self.music_player = MusicPlayerSystem(options_system)
        
        self._setup_ui()

    def resize(self, new_screen_size):
        """Recalculate UI layout based on new screen size."""
        print(f"DEBUG: OptionsMenu resizing to {new_screen_size}") # DEBUG LOG
        self.screen_size = new_screen_size
        self._setup_ui() # Re-run the UI setup with the new size

    def _setup_ui(self):
        self.elements = {}
        screen_w, screen_h = self.screen_size
        center_x = screen_w // 2
        
        # Use relative positioning for Y coordinates
        title_y = int(screen_h * 0.15) # Title closer to top
        start_y = int(screen_h * 0.30) # First button below title
        spacing = int(screen_h * 0.08) # Spacing based on height
        button_height = max(35, int(screen_h * 0.05)) # Button height scales slightly
        button_width = 220 # Keep button width fixed for now

        # --- Main Options --- 
        self.elements[OptionsMenuState.MAIN] = [
            Label("Options", center_x, title_y, self.title_font, self.colors['title']),
            Button("Video", center_x - button_width/2, start_y, button_width, button_height, self.font, self.colors, action=OptionsMenuState.VIDEO),
            Button("Audio", center_x - button_width/2, start_y + spacing, button_width, button_height, self.font, self.colors, action=OptionsMenuState.AUDIO),
            Button("Controls", center_x - button_width/2, start_y + spacing*2, button_width, button_height, self.font, self.colors, action=OptionsMenuState.CONTROLS),
            Button("Music Player", center_x - button_width/2, start_y + spacing*3, button_width, button_height, self.font, self.colors, action=OptionsMenuState.MUSIC_PLAYER),
            Button("Back", center_x - button_width/2, start_y + spacing*4, button_width, button_height, self.font, self.colors, action='back', tag='back_button')
        ]

        # --- Video Options --- 
        video_y = int(screen_h * 0.25) # Start Y for video options
        video_spacing = int(screen_h * 0.09) # Spacing for video options
        video_title_y = int(screen_h * 0.15)
        label_col_x = center_x - 150 # Label column X
        control_col_x = center_x + 0    # Control column X
        control_width = 250
        small_button_height = max(30, int(screen_h * 0.04)) # Smaller height for < > buttons
        toggle_width = 100
        slider_width = control_width - 80
        slider_height = 20

        current_res_text = f"{self.options.video['resolution'][0]} x {self.options.video['resolution'][1]}"
        current_gui_scale_text = f"{self.options.video['gui_scale']:.1f}"

        self.elements[OptionsMenuState.VIDEO] = [
            Label("Video Settings", center_x, video_title_y, self.title_font, self.colors['title']),

            # Resolution Controls
            Label("Resolution:", label_col_x, video_y, self.font, self.colors['text'], align='right'),
            Button("<", control_col_x - 100, video_y - small_button_height // 2, 30, small_button_height, self.font, self.colors, action='res_prev'),
            Label(current_res_text, control_col_x + 25, video_y, self.font, self.colors['text'], align='center', tag='resolution_label'),
            Button(">", control_col_x + 150, video_y - small_button_height // 2, 30, small_button_height, self.font, self.colors, action='res_next'),

            # Fullscreen Toggle
            Label("Fullscreen:", label_col_x, video_y + video_spacing, self.font, self.colors['text'], align='right'),
            ToggleButton(self.options.video['fullscreen'], control_col_x, video_y + video_spacing - button_height // 2, toggle_width, button_height, self.font, self.colors, action='toggle_fullscreen', tag='fullscreen_toggle'),

            # VSync Toggle
            Label("VSync:", label_col_x, video_y + video_spacing * 2, self.font, self.colors['text'], align='right'),
            ToggleButton(self.options.video['vsync'], control_col_x, video_y + video_spacing * 2 - button_height // 2, toggle_width, button_height, self.font, self.colors, action='toggle_vsync', tag='vsync_toggle'),

            # Particles Toggle
            Label("Particles:", label_col_x, video_y + video_spacing * 3, self.font, self.colors['text'], align='right'),
            ToggleButton(self.options.video['particles_enabled'], control_col_x, video_y + video_spacing * 3 - button_height // 2, toggle_width, button_height, self.font, self.colors, action='toggle_particles', tag='particles_toggle'),

            # GUI Scale Slider
            Label("GUI Scale:", label_col_x, video_y + video_spacing * 4, self.font, self.colors['text'], align='right'),
            Slider(control_col_x, video_y + video_spacing * 4, slider_width, slider_height, 0.5, 2.5, self.options.video['gui_scale'], self.colors, action='set_gui_scale', step=0.1, tag='gui_scale_slider'),
            Label(current_gui_scale_text, control_col_x + slider_width + 40, video_y + video_spacing * 4, self.font, self.colors['text'], tag='gui_scale_label'),

            # Back Button
            Button("Back", center_x - button_width // 2, video_y + video_spacing * 5, button_width, button_height, self.font, self.colors, action='back')
        ]
        
        # --- Audio Options --- 
        audio_y = int(screen_h * 0.25)
        audio_spacing = int(screen_h * 0.09)
        audio_title_y = int(screen_h * 0.15)
        self.elements[OptionsMenuState.AUDIO] = [
            Label("Audio Settings", center_x, audio_title_y, self.title_font, self.colors['title']),
            # Use same layout constants as Video for consistency
            Label("Master Volume:", label_col_x, audio_y, self.font, self.colors['text'], align='right'),
            Slider(control_col_x, audio_y, slider_width, slider_height, 0, 1, self.options.audio['master_volume'], self.colors, action='set_master_volume'),
            Label(f"{self.options.audio['master_volume']:.0%}", control_col_x + slider_width + 40, audio_y, self.font, self.colors['text'], tag='master_volume_label'),
            
            Label("Music Volume:", label_col_x, audio_y + audio_spacing, self.font, self.colors['text'], align='right'),
            Slider(control_col_x, audio_y + audio_spacing, slider_width, slider_height, 0, 1, self.options.audio['music_volume'], self.colors, action='set_music_volume'),
            Label(f"{self.options.audio['music_volume']:.0%}", control_col_x + slider_width + 40, audio_y + audio_spacing, self.font, self.colors['text'], tag='music_volume_label'),
            
            Label("SFX Volume:", label_col_x, audio_y + audio_spacing*2, self.font, self.colors['text'], align='right'),
            Slider(control_col_x, audio_y + audio_spacing*2, slider_width, slider_height, 0, 1, self.options.audio['sfx_volume'], self.colors, action='set_sfx_volume'),
            Label(f"{self.options.audio['sfx_volume']:.0%}", control_col_x + slider_width + 40, audio_y + audio_spacing*2, self.font, self.colors['text'], tag='sfx_volume_label'),

            Label("Mute Music:", label_col_x, audio_y + audio_spacing*3, self.font, self.colors['text'], align='right'),
            ToggleButton(self.options.audio['is_muted'], control_col_x, audio_y + audio_spacing*3 - button_height // 2, toggle_width, button_height, self.font, self.colors, action='toggle_mute'),

            Button("Music Player", center_x - button_width // 2, audio_y + audio_spacing*4, button_width, button_height, self.font, self.colors, action=OptionsMenuState.MUSIC_PLAYER),
            Button("Back", center_x - button_width // 2, audio_y + audio_spacing*5, button_width, button_height, self.font, self.colors, action='back')
        ]

        # --- Controls Options --- 
        controls_title_y = int(screen_h * 0.15)
        controls_start_y = int(screen_h * 0.25)
        controls_spacing = int(screen_h * 0.06) # Tighter spacing for controls
        controls_button_height = max(30, int(screen_h * 0.04))
        col1_x = center_x - 250
        col2_x = center_x + 50
        col_width = 200
        self.elements[OptionsMenuState.CONTROLS] = [
            Label("Controls Settings", center_x, controls_title_y, self.title_font, self.colors['title'])
        ]
        
        row = 0
        for player in ['player1', 'player2']:
            self.elements[OptionsMenuState.CONTROLS].append(
                Label(f"Player {player[-1]}", col1_x + col_width / 2 if player == 'player1' else col2_x + col_width / 2, 
                      controls_start_y - 20, self.font, self.colors['text']) # Player label above binds
            )
            current_col_x = col1_x if player == 'player1' else col2_x
            current_y = controls_start_y
            for action in self.options.keybinds[player]:
                key_name = pygame.key.name(self.options.get_keybind(player, action) or 0)
                self.elements[OptionsMenuState.CONTROLS].extend([
                    Label(f"{action.capitalize()}:", current_col_x - 10, current_y, self.font, self.colors['text'], align='right'),
                    Button(key_name, current_col_x + 10, current_y - controls_button_height // 2, col_width - 20, controls_button_height, 
                           self.font, self.colors, action=('rebind', player, action), tag=(player, action))
                ])
                current_y += controls_spacing
            # This logic assumes controls fit in one column per player layout
            
        # Position back button below controls
        back_button_y = controls_start_y + len(self.options.keybinds['player1']) * controls_spacing + 20
        self.elements[OptionsMenuState.CONTROLS].append(
             Button("Back", center_x - button_width // 2, back_button_y, button_width, button_height, self.font, self.colors, action='back')
        )
        
        # --- Rebind State --- 
        # Calculate center Y for the rebind prompt
        center_y_pos = screen_h // 2
        self.elements[OptionsMenuState.REBIND] = [
            Label("Press any key to rebind...", center_x, center_y_pos + 50, self.font, self.colors['text'], tag='rebind_prompt')
            # We will draw the action being rebound separately
        ]

    def handle_input(self, events):
        # For video toggle buttons
        self._update_video_toggle_buttons()
        self._update_gui_scale_slider_label()
        
        # For audio menu, update all slider labels and toggle buttons
        self._update_audio_slider_labels()
        self._update_audio_toggle_buttons()
        
        # If music player is active, handle its input
        if self.state == OptionsMenuState.MUSIC_PLAYER and self.music_player.active:
            for event in events:
                if self.music_player.handle_event(event):
                    # If music player handled the event, check if it deactivated itself
                    if not self.music_player.active:
                        # Music player was deactivated (probably Escape key), return to audio menu
                        self.state = OptionsMenuState.AUDIO
                        return None
                    return self.state
            return self.state
        
        # Handle rebinding state first
        if self.state == OptionsMenuState.REBIND and self.rebind_info:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    player, action = self.rebind_info
                    self.options.set_keybind(player, action, event.key)
                    self._update_control_button_text(player, action, pygame.key.name(event.key))
                    self.state = OptionsMenuState.CONTROLS
                    self.rebind_info = None
                    self.options.play_sound('menu_click')
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Cancel rebinding on mouse click
                    self.state = OptionsMenuState.CONTROLS
                    self.rebind_info = None
                    return None
            return None
        
        # Handle user input
        for event in events:
            # Handle sliders in audio menu
            if self.state == OptionsMenuState.AUDIO:
                for elem in self.elements[OptionsMenuState.AUDIO]:
                    if isinstance(elem, Slider):
                        if elem.handle_event(event):
                            # Process slider change
                            if elem.action == 'set_master_volume':
                                self.options.audio['master_volume'] = elem.value
                                self.options.set_volume('master_volume', elem.value)
                            elif elem.action == 'set_music_volume':
                                self.options.audio['music_volume'] = elem.value
                                self.options.set_volume('music_volume', elem.value)
                            elif elem.action == 'set_sfx_volume':
                                self.options.audio['sfx_volume'] = elem.value
                                self.options.set_volume('sfx_volume', elem.value)
                            
                            # Update audio slider labels after any audio change
                            self._update_audio_slider_labels()
                            return self.state
                    
                    # Handle toggle buttons (mute)
                    elif isinstance(elem, ToggleButton) and elem.action == 'toggle_mute':
                        if elem.handle_event(event):
                            self.options.audio['is_muted'] = elem.is_on
                            # Immediately apply mute setting
                            if pygame.mixer.music.get_busy():
                                volume = 0.0 if self.options.audio['is_muted'] else (
                                    self.options.audio['master_volume'] * self.options.audio['music_volume'])
                                pygame.mixer.music.set_volume(volume)
                            return self.state

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == OptionsMenuState.MAIN:
                        print("DEBUG: ESC pressed in main options - returning exit_options") # Debug print
                        self.options.save_settings()
                        self.state = OptionsMenuState.MAIN  # Reset state before returning
                        return 'exit_options'
                    else:
                        self.state = OptionsMenuState.MAIN
                        return None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                for element in self.elements.get(self.state, []):
                    if isinstance(element, Button) and element.collidepoint(pygame.mouse.get_pos()):
                        action = element.action
                        print(f"DEBUG: Button clicked - action: {action}, tag: {element.tag}")  # Debug print
                        
                        # Handle back button action FIRST
                        if action == 'back':
                            self.options.play_sound('menu_click')
                            # If we're in any sub-menu, go back to main
                            if self.state != OptionsMenuState.MAIN:
                                # If we're in the music player, deactivate it
                                if self.state == OptionsMenuState.MUSIC_PLAYER:
                                    self.music_player.deactivate()
                                self.state = OptionsMenuState.MAIN
                            else:
                                # If we're in main, exit options
                                self.options.save_settings()
                                return 'exit_options'

                        # Play sound AFTER handling back action
                        self.options.play_sound('menu_click')
                        
                        # Handle rebind action
                        if isinstance(action, tuple) and action[0] == 'rebind':
                            _, player, key_action = action
                            self.rebind_info = (player, key_action)
                            self.state = OptionsMenuState.REBIND
                            return None
                        
                        # Handle other button actions
                        if isinstance(action, OptionsMenuState):
                            self.options.play_sound('menu_click')
                            self.state = action
                            # If entering the music player, activate it
                            if self.state == OptionsMenuState.MUSIC_PLAYER:
                                # First completely stop all music
                                pygame.mixer.music.stop()
                                self.options.next_track = None
                                self.options.music_queue = []
                                # Now activate the music player
                                self.music_player.activate()
                            return self.state
                        elif action == 'toggle_fullscreen':
                            self.options.toggle_fullscreen()
                        elif action == 'toggle_vsync':
                            self.options.toggle_vsync()
                        elif action == 'res_prev':
                            self.options.cycle_resolution(-1)
                            self._update_resolution_label()
                        elif action == 'res_next':
                            self.options.cycle_resolution(1)
                            self._update_resolution_label()
                        elif action == 'set_master_volume':
                            for elem in self.elements[OptionsMenuState.AUDIO]:
                                if isinstance(elem, Slider) and elem.action == action:
                                    self.options.set_volume('master_volume', elem.value)
                                    break
                        elif action == 'set_music_volume':
                            for elem in self.elements[OptionsMenuState.AUDIO]:
                                if isinstance(elem, Slider) and elem.action == action:
                                    self.options.set_volume('music_volume', elem.value)
                                    break
                        elif action == 'set_sfx_volume':
                            for elem in self.elements[OptionsMenuState.AUDIO]:
                                if isinstance(elem, Slider) and elem.action == action:
                                    self.options.set_volume('sfx_volume', elem.value)
                                    break
                        elif action == 'toggle_mute':
                            self.options.toggle_mute()
                        elif action == 'set_gui_scale':
                            for elem in self.elements[OptionsMenuState.VIDEO]:
                                if isinstance(elem, Slider) and elem.action == 'set_gui_scale':
                                    self.options.set_gui_scale(elem.value)
                                    self._update_gui_scale_slider_label()
                                    break
                        elif action == 'toggle_particles':
                            self.options.toggle_particles()
                        # Already handled above when checking if action is an OptionsMenuState
                        # No need to handle MUSIC_PLAYER again here
                        break

            elif event.type == pygame.MOUSEMOTION:
                for element in self.elements.get(self.state, []):
                    if isinstance(element, Slider):
                        if element.handle_event(event):
                            action = element.action
                            if action == 'set_master_volume':
                                self.options.set_volume('master_volume', element.value)
                            elif action == 'set_music_volume':
                                self.options.set_volume('music_volume', element.value)
                            elif action == 'set_sfx_volume':
                                self.options.set_volume('sfx_volume', element.value)
                            elif action == 'set_gui_scale':
                                self.options.set_gui_scale(element.value)
                                self._update_gui_scale_slider_label()
                    elif hasattr(element, 'is_hovered'):
                        element.is_hovered = element.collidepoint(pygame.mouse.get_pos())

        return None

    def _update_resolution_label(self):
        res_text = f"{self.options.video['resolution'][0]} x {self.options.video['resolution'][1]}"
        for elem in self.elements[OptionsMenuState.VIDEO]:
            if isinstance(elem, Label) and elem.tag == 'resolution_label':
                elem.set_text(res_text)
                break
                
    def _update_video_toggle_buttons(self):
         for elem in self.elements[OptionsMenuState.VIDEO]:
            if isinstance(elem, ToggleButton):
                 if elem.action == 'toggle_fullscreen': elem.is_on = self.options.video['fullscreen']
                 elif elem.action == 'toggle_vsync': elem.is_on = self.options.video['vsync']
                 elif elem.action == 'toggle_particles': elem.is_on = self.options.video['particles_enabled']
                 
    def _update_gui_scale_slider_label(self):
         scale_text = f"{self.options.video['gui_scale']:.1f}"
         for elem in self.elements[OptionsMenuState.VIDEO]:
             if isinstance(elem, Label) and elem.tag == 'gui_scale_label':
                 elem.set_text(scale_text)
             elif isinstance(elem, Slider) and elem.action == 'set_gui_scale':
                 elem.set_value(self.options.video['gui_scale'])

    def _update_audio_slider_labels(self):
         for elem in self.elements[OptionsMenuState.AUDIO]:
             if isinstance(elem, Label):
                if elem.tag == 'master_volume_label': elem.set_text(f"{self.options.audio['master_volume']:.0%}")
                elif elem.tag == 'music_volume_label': elem.set_text(f"{self.options.audio['music_volume']:.0%}")
                elif elem.tag == 'sfx_volume_label': elem.set_text(f"{self.options.audio['sfx_volume']:.0%}")
             elif isinstance(elem, Slider):
                if elem.action == 'set_master_volume': elem.set_value(self.options.audio['master_volume'])
                elif elem.action == 'set_music_volume': elem.set_value(self.options.audio['music_volume'])
                elif elem.action == 'set_sfx_volume': elem.set_value(self.options.audio['sfx_volume'])
                
    def _update_audio_toggle_buttons(self):
        for elem in self.elements[OptionsMenuState.AUDIO]:
            if isinstance(elem, ToggleButton) and elem.action == 'toggle_mute':
                elem.is_on = self.options.audio['is_muted']

    def _update_control_button_text(self, player, action, key_name):
         for elem in self.elements.get(OptionsMenuState.CONTROLS, []):
             if isinstance(elem, Button) and elem.tag == (player, action):
                 elem.set_text(key_name)
                 break
                 
    def _update_all_control_button_text(self):
         for elem in self.elements.get(OptionsMenuState.CONTROLS, []):
             if isinstance(elem, Button) and isinstance(elem.tag, tuple): # Control buttons have tuple tags
                 player, action = elem.tag
                 key_name = pygame.key.name(self.options.get_keybind(player, action) or 0)
                 elem.set_text(key_name)

    def draw(self, screen):
        """Draw the options menu"""
        # Fill background
        screen.fill(self.colors['background'])
        
        # Special handling for music player state
        if self.state == OptionsMenuState.MUSIC_PLAYER:
            player_width = min(800, self.screen_size[0] - 100)
            player_height = min(500, self.screen_size[1] - 100)
            player_x = (self.screen_size[0] - player_width) // 2
            player_y = (self.screen_size[1] - player_height) // 2
            self.music_player.render(screen, (player_x, player_y), player_width, player_height)
            return
        
        # Draw current state elements
        current_elements = self.elements.get(self.state, [])
        
        # Special handling for rebind state
        if self.state == OptionsMenuState.REBIND and self.rebind_info:
            player, action = self.rebind_info
            # Draw centered prompt
            center_x = self.screen_size[0] // 2
            center_y = self.screen_size[1] // 2
            
            # Draw action being rebound
            action_text = f"Press a key to bind for {player}'s {action}..."
            action_label = Label(action_text, center_x, center_y - 50, 
                               self.font, self.colors['title'])
            action_label.draw(screen)
            
            # Draw escape hint
            escape_text = "Click anywhere to cancel"
            escape_label = Label(escape_text, center_x, center_y + 50,
                               self.font, self.colors['text'])
            escape_label.draw(screen)
            return
        
        # Draw all other elements
        for element in current_elements:
            element.draw(screen)