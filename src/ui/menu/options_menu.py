"""
Options Menu UI Component for Runic Lands
Provides user interface for changing game settings
"""

import pygame
from enum import Enum, auto
from typing import Tuple, Dict, List, Callable, Optional

class OptionsMenuState(Enum):
    """States for the options menu navigation"""
    MAIN = auto()
    CONTROLS = auto()
    AUDIO = auto()
    VIDEO = auto()
    BACK = auto()

class Slider:
    """UI Slider component for adjusting numeric values"""
    
    def __init__(self, x: int, y: int, width: int, height: int, value: float = 0.5,
                 min_value: float = 0.0, max_value: float = 1.0):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_size = (height * 1.5, height * 1.5)
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.active = False
        self.handle_rect = self._calculate_handle_rect()
        
    def _calculate_handle_rect(self) -> pygame.Rect:
        """Calculate the position of the slider handle based on current value"""
        value_range = self.max_value - self.min_value
        position = (self.value - self.min_value) / value_range if value_range > 0 else 0
        handle_x = self.rect.x + (self.rect.width * position) - (self.handle_size[0] / 2)
        handle_y = self.rect.y + (self.rect.height / 2) - (self.handle_size[1] / 2)
        return pygame.Rect(handle_x, handle_y, *self.handle_size)
        
    def handle_event(self, event) -> bool:
        """Process mouse events for slider interaction"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if handle was clicked
            if self.handle_rect.collidepoint(event.pos):
                self.active = True
                return True
            # Check if track was clicked
            elif self.rect.collidepoint(event.pos):
                self._update_value_from_pos(event.pos[0])
                self.handle_rect = self._calculate_handle_rect()
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active:
                self.active = False
                return True
                
        elif event.type == pygame.MOUSEMOTION and self.active:
            self._update_value_from_pos(event.pos[0])
            self.handle_rect = self._calculate_handle_rect()
            return True
            
        return False
        
    def _update_value_from_pos(self, x_pos: int):
        """Calculate slider value based on mouse X position"""
        relative_x = max(self.rect.left, min(x_pos, self.rect.right)) - self.rect.left
        percentage = relative_x / self.rect.width
        self.value = self.min_value + percentage * (self.max_value - self.min_value)
        
    def draw(self, surface: pygame.Surface):
        """Draw the slider on the provided surface"""
        # Draw track
        track_color = (80, 80, 100)
        pygame.draw.rect(surface, track_color, self.rect, border_radius=self.rect.height // 2)
        
        # Draw filled portion
        value_range = self.max_value - self.min_value
        fill_width = int((self.value - self.min_value) / value_range * self.rect.width) if value_range > 0 else 0
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        fill_color = (100, 100, 200)
        if fill_width > 0:
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=self.rect.height // 2)
        
        # Draw handle
        handle_color = (150, 150, 255) if self.active else (120, 120, 220)
        pygame.draw.ellipse(surface, handle_color, self.handle_rect)
        # Add a border to the handle
        pygame.draw.ellipse(surface, (200, 200, 255), self.handle_rect, 2)

class ScrollBar:
    """Scrollbar for navigating content taller than the viewport"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 content_height: int, viewport_height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.content_height = max(content_height, viewport_height)
        self.viewport_height = viewport_height
        self.scroll_pos = 0  # Current scroll position
        self.active = False  # Whether handle is being dragged
        self.handle_rect = self._calculate_handle_rect()
        
    def _calculate_handle_rect(self) -> pygame.Rect:
        """Calculate handle rect based on content/viewport ratio and scroll position"""
        # Handle height is proportional to viewport/content ratio
        handle_height = max(20, int(self.rect.height * self.viewport_height / self.content_height))
        
        # Calculate handle position based on scroll position
        max_scroll = max(0, self.content_height - self.viewport_height)
        scroll_percentage = self.scroll_pos / max_scroll if max_scroll > 0 else 0
        max_handle_pos = self.rect.height - handle_height
        handle_pos = int(scroll_percentage * max_handle_pos)
        
        return pygame.Rect(self.rect.x, self.rect.y + handle_pos, self.rect.width, handle_height)
        
    def handle_event(self, event) -> bool:
        """Process mouse events for scrollbar interaction"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if handle was clicked
            if self.handle_rect.collidepoint(event.pos):
                self.active = True
                # Store offset from handle top to mouse
                self.drag_offset = event.pos[1] - self.handle_rect.y
                return True
            # Check if track was clicked
            elif self.rect.collidepoint(event.pos):
                # Jump to position
                self._update_scroll_from_pos(event.pos[1], 0)
                self.handle_rect = self._calculate_handle_rect()
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active:
                self.active = False
                return True
                
        elif event.type == pygame.MOUSEMOTION and self.active:
            self._update_scroll_from_pos(event.pos[1], self.drag_offset)
            self.handle_rect = self._calculate_handle_rect()
            return True
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            # Mouse wheel scrolling
            if self.rect.collidepoint(event.pos) or True:  # Allow scrolling anywhere
                scroll_amount = 30  # Pixels to scroll per wheel click
                if event.button == 4:  # Scroll up
                    self.scroll_pos = max(0, self.scroll_pos - scroll_amount)
                else:  # Scroll down
                    max_scroll = max(0, self.content_height - self.viewport_height)
                    self.scroll_pos = min(max_scroll, self.scroll_pos + scroll_amount)
                self.handle_rect = self._calculate_handle_rect()
                return True
                
        return False
        
    def _update_scroll_from_pos(self, y_pos: int, offset: int):
        """Calculate scroll position based on mouse Y position"""
        # Adjust position by drag offset
        handle_pos = y_pos - self.rect.y - offset
        
        # Calculate percentage
        max_handle_pos = self.rect.height - self.handle_rect.height
        percentage = handle_pos / max_handle_pos if max_handle_pos > 0 else 0
        percentage = max(0, min(1, percentage))
        
        # Set scroll position
        max_scroll = max(0, self.content_height - self.viewport_height)
        self.scroll_pos = int(percentage * max_scroll)
        
    def get_scroll_offset(self) -> int:
        """Get the current scroll offset for viewport rendering"""
        return self.scroll_pos
        
    def draw(self, surface: pygame.Surface):
        """Draw the scrollbar on the provided surface"""
        # Draw track
        track_color = (60, 60, 80)
        pygame.draw.rect(surface, track_color, self.rect, border_radius=self.rect.width // 2)
        
        # Draw handle
        handle_color = (150, 150, 255) if self.active else (120, 120, 220)
        pygame.draw.rect(surface, handle_color, self.handle_rect, 
                       border_radius=self.rect.width // 2)

class OptionsMenu:
    """
    Options menu interface for adjusting game settings
    Uses ConfigManager for handling configuration values
    """
    
    def __init__(self, screen_size: Tuple[int, int], config_manager, asset_manager, graphics_engine):
        """
        Initialize the options menu
        
        Args:
            screen_size: Tuple of (width, height) for the screen
            config_manager: ConfigManager instance for accessing settings
            asset_manager: AssetManager instance for loading UI assets
            graphics_engine: SynapstexGraphics instance for display updates
        """
        self.screen_size = screen_size
        self.config = config_manager
        self.assets = asset_manager
        self.graphics = graphics_engine
        self.state = OptionsMenuState.MAIN
        
        # Get fonts
        self.font = self.assets.get_default_font(36)
        self.small_font = self.assets.get_default_font(24)
        
        # Flag for awaiting keybind input
        self.waiting_for_key = False
        self.current_binding = None
        
        # Create audio sliders
        center_x = self.screen_size[0] // 2 - 100
        self.sliders = {
            'master': Slider(center_x, 200, 200, 20, 
                            value=self.config.get('audio', 'master_volume', 0.7)),
            'music': Slider(center_x, 250, 200, 20, 
                          value=self.config.get('audio', 'music_volume', 0.5)),
            'sfx': Slider(center_x, 300, 200, 20, 
                        value=self.config.get('audio', 'sfx_volume', 0.8))
        }
        
        # Calculate content height for controls menu
        player_count = 2  # Number of players with controls
        controls_per_player = 6  # Number of configurable controls per player
        self.controls_content_height = 40 + (controls_per_player * 40 + 40) * player_count
        self.controls_viewport_height = 400
        
        # Create scrollbar for controls menu
        scrollbar_x = self.screen_size[0] - 30
        scrollbar_y = 150
        scrollbar_height = self.controls_viewport_height
        self.controls_scrollbar = ScrollBar(scrollbar_x, scrollbar_y, 20, scrollbar_height,
                                          self.controls_content_height, self.controls_viewport_height)
        
        # Available video resolutions
        self.resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1920, 1080)
        ]
        
        # Current resolution index
        self.current_resolution_index = 0
        current_res = self.config.get_resolution()
        for i, res in enumerate(self.resolutions):
            if res == current_res:
                self.current_resolution_index = i
                break
    
    def handle_input(self, events) -> Optional[OptionsMenuState]:
        """Process input events and return state changes"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.waiting_for_key:
                    if event.key != pygame.K_ESCAPE:  # ESC cancels rebinding
                        player, action = self.current_binding
                        self.config.set_keybind(player, action, event.key)
                        self._play_sound('menu_click')
                    self.waiting_for_key = False
                    self.current_binding = None
                    return self.state
                elif event.key == pygame.K_ESCAPE:
                    # If in a submenu, go back to main options menu
                    if self.state in [OptionsMenuState.CONTROLS, 
                                      OptionsMenuState.AUDIO, 
                                      OptionsMenuState.VIDEO]:
                        self.state = OptionsMenuState.MAIN
                        self._play_sound('menu_click')
                        return self.state
                    # If already in main menu, return to game
                    else:
                        return OptionsMenuState.BACK
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == OptionsMenuState.MAIN:
                    result = self.handle_main_menu_click(event.pos)
                    if result:
                        return result
                elif self.state == OptionsMenuState.CONTROLS:
                    # Handle scrollbar first
                    if self.controls_scrollbar.handle_event(event):
                        pass  # Scrollbar handled the event
                    elif self.handle_controls_click(event.pos):
                        return self.state
                elif self.state == OptionsMenuState.AUDIO:
                    if self.handle_audio_click(event.pos):
                        return self.state
                elif self.state == OptionsMenuState.VIDEO:
                    if self.handle_video_click(event.pos):
                        return self.state
                        
            # Handle slider dragging in audio menu
            if self.state == OptionsMenuState.AUDIO:
                for slider_name, slider in self.sliders.items():
                    if slider.handle_event(event):
                        volume_type = f"{slider_name}_volume"
                        self.config.set('audio', volume_type, slider.value)
                        # Update audio immediately
                        if slider_name == 'master' or slider_name == 'music':
                            self.assets.set_music_volume(
                                self.config.get('audio', 'master_volume', 0.7) * 
                                self.config.get('audio', 'music_volume', 0.5)
                            )
            
            # Handle scrollbar dragging in controls menu
            if self.state == OptionsMenuState.CONTROLS:
                self.controls_scrollbar.handle_event(event)
                        
        return self.state
    
    def _play_sound(self, sound_name: str):
        """Play a sound effect"""
        self.assets.play_sound(sound_name, 
                             self.config.get('audio', 'master_volume', 0.7) * 
                             self.config.get('audio', 'sfx_volume', 0.8))
        
    def handle_main_menu_click(self, pos) -> Optional[OptionsMenuState]:
        """Handle mouse clicks in the main options menu"""
        buttons = [
            (pygame.Rect(300, 200, 200, 40), OptionsMenuState.CONTROLS),
            (pygame.Rect(300, 260, 200, 40), OptionsMenuState.AUDIO),
            (pygame.Rect(300, 320, 200, 40), OptionsMenuState.VIDEO),
            (pygame.Rect(300, 380, 200, 40), OptionsMenuState.BACK)
        ]
        
        for rect, state in buttons:
            if rect.collidepoint(pos):
                self._play_sound('menu_click')
                self.state = state
                return state
        return None
    
    def handle_controls_click(self, pos) -> bool:
        """Handle mouse clicks in the controls configuration menu"""
        scroll_offset = self.controls_scrollbar.get_scroll_offset()
        adjusted_y = pos[1] + scroll_offset
        
        # Control binding buttons
        y_start = 150 - scroll_offset
        player_spacing = 40
        control_spacing = 40
        
        # Check player 1 keybinds
        for i, action in enumerate(['up', 'down', 'left', 'right', 'attack', 'inventory']):
            y = y_start + i * control_spacing
            rect = pygame.Rect(450, y, 150, 30)
            if rect.collidepoint(pos[0], adjusted_y):
                self.waiting_for_key = True
                self.current_binding = ('player1', action)
                self._play_sound('menu_click')
                return True
                
        # Check player 2 keybinds
        y_start += 6 * control_spacing + player_spacing
        for i, action in enumerate(['up', 'down', 'left', 'right', 'attack', 'inventory']):
            y = y_start + i * control_spacing
            rect = pygame.Rect(450, y, 150, 30)
            if rect.collidepoint(pos[0], adjusted_y):
                self.waiting_for_key = True
                self.current_binding = ('player2', action)
                self._play_sound('menu_click')
                return True
        
        # Back button (fixed position, not affected by scrolling)
        back_rect = pygame.Rect(300, 500, 200, 40)
        if back_rect.collidepoint(pos):
            self.state = OptionsMenuState.MAIN
            self._play_sound('menu_click')
            return True
            
        return False
    
    def handle_audio_click(self, pos) -> bool:
        """Handle mouse clicks in the audio settings menu"""
        # Sliders are handled separately
        
        # Back button
        back_rect = pygame.Rect(300, 400, 200, 40)
        if back_rect.collidepoint(pos):
            self.state = OptionsMenuState.MAIN
            self._play_sound('menu_click')
            return True
            
        return False
    
    def handle_video_click(self, pos) -> bool:
        """Handle mouse clicks in the video settings menu"""
        # Fullscreen toggle button
        fullscreen_rect = pygame.Rect(300, 200, 200, 40)
        if fullscreen_rect.collidepoint(pos):
            fullscreen = not self.config.get_fullscreen()
            self.config.set('video', 'fullscreen', fullscreen)
            self.graphics.set_fullscreen(fullscreen)
            self._play_sound('menu_click')
            return True
            
        # VSync toggle button
        vsync_rect = pygame.Rect(300, 250, 200, 40)
        if vsync_rect.collidepoint(pos):
            vsync = not self.config.get_vsync()
            self.config.set('video', 'vsync', vsync)
            self.graphics.set_vsync(vsync)
            self._play_sound('menu_click')
            return True
            
        # Resolution buttons
        res_prev_rect = pygame.Rect(270, 300, 30, 30)
        res_next_rect = pygame.Rect(500, 300, 30, 30)
        
        if res_prev_rect.collidepoint(pos):
            self.current_resolution_index = (self.current_resolution_index - 1) % len(self.resolutions)
            new_res = self.resolutions[self.current_resolution_index]
            self.config.set('video', 'resolution', new_res)
            self._play_sound('menu_click')
            return True
            
        if res_next_rect.collidepoint(pos):
            self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
            new_res = self.resolutions[self.current_resolution_index]
            self.config.set('video', 'resolution', new_res)
            self._play_sound('menu_click')
            return True
            
        # Apply resolution button
        apply_rect = pygame.Rect(300, 350, 200, 40)
        if apply_rect.collidepoint(pos):
            current_res = self.resolutions[self.current_resolution_index]
            self.graphics.set_screen_resolution(*current_res)
            self._play_sound('menu_click')
            return True
            
        # Back button
        back_rect = pygame.Rect(300, 430, 200, 40)
        if back_rect.collidepoint(pos):
            self.state = OptionsMenuState.MAIN
            self._play_sound('menu_click')
            return True
            
        return False
        
    def draw(self, screen: pygame.Surface):
        """Draw the options menu to the screen"""
        # Clear screen
        screen.fill((20, 20, 40))
        
        # Draw header
        header_text = "Options"
        header = self.font.render(header_text, True, (255, 255, 255))
        screen.blit(header, (self.screen_size[0] // 2 - header.get_width() // 2, 50))
        
        if self.state == OptionsMenuState.MAIN:
            self.draw_main_menu(screen)
        elif self.state == OptionsMenuState.CONTROLS:
            self.draw_controls_menu(screen)
        elif self.state == OptionsMenuState.AUDIO:
            self.draw_audio_menu(screen)
        elif self.state == OptionsMenuState.VIDEO:
            self.draw_video_menu(screen)
        
        # Draw "Press any key" prompt if waiting for keybind
        if self.waiting_for_key:
            overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            prompt = self.font.render("Press a key...", True, (255, 255, 255))
            prompt_rect = prompt.get_rect(center=(self.screen_size[0]//2, self.screen_size[1]//2))
            screen.blit(prompt, prompt_rect)
            
            cancel = self.small_font.render("(Escape to cancel)", True, (200, 200, 200))
            cancel_rect = cancel.get_rect(center=(self.screen_size[0]//2, self.screen_size[1]//2 + 40))
            screen.blit(cancel, cancel_rect)
        
    def draw_main_menu(self, screen: pygame.Surface):
        """Draw the main options menu"""
        menu_items = [
            ("Controls", OptionsMenuState.CONTROLS),
            ("Audio", OptionsMenuState.AUDIO),
            ("Video", OptionsMenuState.VIDEO),
            ("Back", OptionsMenuState.BACK)
        ]
        
        for i, (text, state) in enumerate(menu_items):
            rect = pygame.Rect(300, 200 + i * 60, 200, 40)
            # Highlight if mouse is over button
            mouse_pos = pygame.mouse.get_pos()
            is_hover = (mouse_pos[0] >= rect.x and mouse_pos[0] <= rect.right and 
                       mouse_pos[1] >= rect.y and mouse_pos[1] <= rect.bottom)
            color = (100, 100, 200) if is_hover else (70, 70, 140)
            
            pygame.draw.rect(screen, color, rect)
            item_text = self.font.render(text, True, (255, 255, 255))
            screen.blit(item_text, (rect.centerx - item_text.get_width() // 2, 
                                   rect.centery - item_text.get_height() // 2))
        
    def draw_controls_menu(self, screen: pygame.Surface):
        """Draw the controls configuration menu"""
        # Create viewport for scrolling
        viewport = pygame.Surface((self.screen_size[0], self.controls_viewport_height), pygame.SRCALPHA)
        viewport.fill((0, 0, 0, 0))
        
        # Get current scroll offset
        scroll_offset = self.controls_scrollbar.get_scroll_offset()
        
        # Render title
        title = self.font.render("Controls", True, (255, 255, 255))
        screen.blit(title, (self.screen_size[0] // 2 - title.get_width() // 2, 100))
        
        # Player 1 header
        p1_text = self.font.render("Player 1", True, (200, 200, 255))
        viewport.blit(p1_text, (200, 100 - scroll_offset))
        
        # Player 1 controls
        controls = ['up', 'down', 'left', 'right', 'attack', 'inventory']
        labels = ['Up', 'Down', 'Left', 'Right', 'Attack', 'Inventory']
        
        for i, (control, label) in enumerate(zip(controls, labels)):
            y = 150 + i * 40 - scroll_offset
            
            # Draw label
            label_text = self.small_font.render(label, True, (255, 255, 255))
            viewport.blit(label_text, (280 - label_text.get_width(), y + 5))
            
            # Draw key binding
            key = self.config.get_keybind('player1', control)
            key_name = pygame.key.name(key).upper()
            
            # Draw button
            button_rect = pygame.Rect(450, y, 150, 30)
            button_color = (80, 80, 160)
            pygame.draw.rect(viewport, button_color, button_rect, border_radius=5)
            
            # Draw key name
            key_text = self.small_font.render(key_name, True, (255, 255, 255))
            viewport.blit(key_text, (button_rect.centerx - key_text.get_width() // 2, 
                                   button_rect.centery - key_text.get_height() // 2))
        
        # Player 2 header
        p2_text = self.font.render("Player 2", True, (200, 200, 255))
        viewport.blit(p2_text, (200, 390 - scroll_offset))
        
        # Player 2 controls
        for i, (control, label) in enumerate(zip(controls, labels)):
            y = 440 + i * 40 - scroll_offset
            
            # Draw label
            label_text = self.small_font.render(label, True, (255, 255, 255))
            viewport.blit(label_text, (280 - label_text.get_width(), y + 5))
            
            # Draw key binding
            key = self.config.get_keybind('player2', control)
            key_name = pygame.key.name(key).upper()
            
            # Draw button
            button_rect = pygame.Rect(450, y, 150, 30)
            button_color = (80, 80, 160)
            pygame.draw.rect(viewport, button_color, button_rect, border_radius=5)
            
            # Draw key name
            key_text = self.small_font.render(key_name, True, (255, 255, 255))
            viewport.blit(key_text, (button_rect.centerx - key_text.get_width() // 2, 
                                   button_rect.centery - key_text.get_height() // 2))
        
        # Blit viewport to screen
        screen.blit(viewport, (0, 150))
        
        # Draw scrollbar
        self.controls_scrollbar.draw(screen)
        
        # Draw back button (below viewport)
        back_rect = pygame.Rect(300, 500, 200, 40)
        # Highlight if mouse is over button
        mouse_pos = pygame.mouse.get_pos()
        is_hover = (mouse_pos[0] >= back_rect.x and mouse_pos[0] <= back_rect.right and 
                   mouse_pos[1] >= back_rect.y and mouse_pos[1] <= back_rect.bottom)
        back_color = (100, 100, 200) if is_hover else (70, 70, 140)
        
        pygame.draw.rect(screen, back_color, back_rect)
        back_text = self.font.render("Back", True, (255, 255, 255))
        screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, 
                               back_rect.centery - back_text.get_height() // 2))
        
    def draw_audio_menu(self, screen: pygame.Surface):
        """Draw the audio settings menu"""
        # Render title
        title = self.font.render("Audio Settings", True, (255, 255, 255))
        screen.blit(title, (self.screen_size[0] // 2 - title.get_width() // 2, 100))
        
        # Draw volume sliders
        pygame.draw.rect(screen, (40, 40, 60), (250, 180, 300, 180), border_radius=10)
        
        # Master volume
        label = self.small_font.render("Master Volume", True, (255, 255, 255))
        screen.blit(label, (200, 200))
        self.sliders['master'].draw(screen)
        value_text = self.small_font.render(f"{int(self.sliders['master'].value * 100)}%", 
                                          True, (255, 255, 255))
        screen.blit(value_text, (530, 200))
        
        # Music volume
        label = self.small_font.render("Music Volume", True, (255, 255, 255))
        screen.blit(label, (200, 250))
        self.sliders['music'].draw(screen)
        value_text = self.small_font.render(f"{int(self.sliders['music'].value * 100)}%", 
                                          True, (255, 255, 255))
        screen.blit(value_text, (530, 250))
        
        # SFX volume
        label = self.small_font.render("Effects Volume", True, (255, 255, 255))
        screen.blit(label, (200, 300))
        self.sliders['sfx'].draw(screen)
        value_text = self.small_font.render(f"{int(self.sliders['sfx'].value * 100)}%", 
                                          True, (255, 255, 255))
        screen.blit(value_text, (530, 300))
        
        # Back button
        back_rect = pygame.Rect(300, 400, 200, 40)
        # Highlight if mouse is over button
        mouse_pos = pygame.mouse.get_pos()
        is_hover = (mouse_pos[0] >= back_rect.x and mouse_pos[0] <= back_rect.right and 
                   mouse_pos[1] >= back_rect.y and mouse_pos[1] <= back_rect.bottom)
        back_color = (100, 100, 200) if is_hover else (70, 70, 140)
        
        pygame.draw.rect(screen, back_color, back_rect)
        back_text = self.font.render("Back", True, (255, 255, 255))
        screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, 
                               back_rect.centery - back_text.get_height() // 2))
        
    def draw_video_menu(self, screen: pygame.Surface):
        """Draw the video settings menu"""
        # Render title
        title = self.font.render("Video Settings", True, (255, 255, 255))
        screen.blit(title, (self.screen_size[0] // 2 - title.get_width() // 2, 100))
        
        # Draw settings panel
        pygame.draw.rect(screen, (40, 40, 60), (250, 180, 300, 220), border_radius=10)
        
        # Draw fullscreen toggle
        fullscreen_rect = pygame.Rect(300, 200, 200, 40)
        fullscreen = self.config.get_fullscreen()
        fullscreen_state = "ON" if fullscreen else "OFF"
        fullscreen_color = (100, 160, 100) if fullscreen else (160, 100, 100)
        
        pygame.draw.rect(screen, fullscreen_color, fullscreen_rect)
        fullscreen_text = self.font.render(f"Fullscreen: {fullscreen_state}", True, (255, 255, 255))
        screen.blit(fullscreen_text, (fullscreen_rect.centerx - fullscreen_text.get_width() // 2, 
                                    fullscreen_rect.centery - fullscreen_text.get_height() // 2))
        
        # Draw vsync toggle
        vsync_rect = pygame.Rect(300, 250, 200, 40)
        vsync = self.config.get_vsync()
        vsync_state = "ON" if vsync else "OFF"
        vsync_color = (100, 160, 100) if vsync else (160, 100, 100)
        
        pygame.draw.rect(screen, vsync_color, vsync_rect)
        vsync_text = self.font.render(f"V-Sync: {vsync_state}", True, (255, 255, 255))
        screen.blit(vsync_text, (vsync_rect.centerx - vsync_text.get_width() // 2, 
                               vsync_rect.centery - vsync_text.get_height() // 2))
        
        # Draw resolution selector
        res_text = self.small_font.render("Resolution:", True, (255, 255, 255))
        screen.blit(res_text, (self.screen_size[0] // 2 - res_text.get_width() // 2, 300))
        
        # Current resolution
        current_res = self.resolutions[self.current_resolution_index]
        res_value = self.font.render(f"{current_res[0]} x {current_res[1]}", True, (255, 255, 255))
        screen.blit(res_value, (self.screen_size[0] // 2 - res_value.get_width() // 2, 320))
        
        # Navigation buttons for resolution
        prev_rect = pygame.Rect(270, 320, 30, 30)
        next_rect = pygame.Rect(500, 320, 30, 30)
        
        pygame.draw.rect(screen, (70, 70, 140), prev_rect)
        pygame.draw.rect(screen, (70, 70, 140), next_rect)
        
        prev_text = self.font.render("<", True, (255, 255, 255))
        next_text = self.font.render(">", True, (255, 255, 255))
        
        screen.blit(prev_text, (prev_rect.centerx - prev_text.get_width() // 2, 
                               prev_rect.centery - prev_text.get_height() // 2))
        screen.blit(next_text, (next_rect.centerx - next_text.get_width() // 2, 
                               next_rect.centery - next_text.get_height() // 2))
        
        # Apply resolution button
        apply_rect = pygame.Rect(300, 350, 200, 40)
        apply_color = (100, 100, 160)
        
        pygame.draw.rect(screen, apply_color, apply_rect)
        apply_text = self.font.render("Apply", True, (255, 255, 255))
        screen.blit(apply_text, (apply_rect.centerx - apply_text.get_width() // 2, 
                                apply_rect.centery - apply_text.get_height() // 2))
        
        # Draw restart notice
        note_text = self.small_font.render("* Some settings require restart", True, (255, 200, 200))
        screen.blit(note_text, (self.screen_size[0] // 2 - note_text.get_width() // 2, 395))
        
        # Back button
        back_rect = pygame.Rect(300, 430, 200, 40)
        # Highlight if mouse is over button
        mouse_pos = pygame.mouse.get_pos()
        is_hover = (mouse_pos[0] >= back_rect.x and mouse_pos[0] <= back_rect.right and 
                   mouse_pos[1] >= back_rect.y and mouse_pos[1] <= back_rect.bottom)
        back_color = (100, 100, 200) if is_hover else (70, 70, 140)
        
        pygame.draw.rect(screen, back_color, back_rect)
        back_text = self.font.render("Back", True, (255, 255, 255))
        screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, 
                               back_rect.centery - back_text.get_height() // 2)) 