"""This module defines the menu system for the game."""

import pygame
import sys
from enum import Enum, auto

class GameState(Enum):
    """Enumeration for the different states of the game."""
    MAIN_MENU = auto()
    OPTIONS = auto()
    SINGLE_PLAYER = auto()
    LOCAL_COOP = auto()
    QUIT = auto()

class MenuItem:
    """Represents a single item in the menu."""
    def __init__(self, text, action, position, size=(200, 50)):
        """Initializes a MenuItem object.

        Args:
            text (str): The text to display on the menu item.
            action: The action to perform when the item is selected.
            position (Tuple[int, int]): The position of the menu item.
            size (Tuple[int, int], optional): The size of the menu item.
                Defaults to (200, 50).
        """
        self.text = text
        self.action = action
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.is_hovered = False
        
    def draw(self, screen, font):
        """Draws the menu item on the screen.

        Args:
            screen (pygame.Surface): The surface to draw the item on.
            font (pygame.font.Font): The font to use for the item's text.
        """
        # Button colors
        button_color = (100, 100, 255) if self.is_hovered else (70, 70, 200)
        text_color = (255, 255, 255)
        
        # Draw button
        pygame.draw.rect(screen, button_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)
        
        # Draw text
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class MenuSystem:
    """Manages the main menu and its interactions."""
    def __init__(self, screen_size, options_system=None):
        """Initializes the MenuSystem.

        Args:
            screen_size (Tuple[int, int]): The size of the screen.
            options_system (any, optional): A reference to the options system. Defaults to None.
        """
        self.screen_size = screen_size
        self.state = GameState.MAIN_MENU
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.options = options_system  # Keep reference to options system
        self.setup_main_menu()
        
        # Don't start music here - let the game handle it initially
        
    def reset(self):
        """Resets the menu system to its initial state."""
        self.state = GameState.MAIN_MENU
        # Rebuild menu layout in case screen size changed
        self.setup_main_menu()
        
        # Restart menu music when returning to menu
        if hasattr(self, 'options') and self.options:
            self.start_menu_music()
            
        return self.state
    
    def start_menu_music(self):
        """Starts the menu music."""
        if hasattr(self, 'options') and self.options:
            # First stop any currently playing music to ensure clean start
            self.options.stop_music()
            
            # Try the sectioned approach with improved error handling
            try:
                print("Starting menu music with section approach...")
                # This will analyze music files and provide diagnostics
                result = self.options.queue_section_music()
                if result:
                    print("Menu music started successfully with section playback.")
                    return True
                else:
                    print("Section playback failed, falling back to standard playback.")
                    # Explicit fallback to standard theme
                    self.options.play_music('assets/audio/menu_theme.wav')
                    return True
            except Exception as e:
                # Fallback to standard playback
                print(f"Error using sectioned playback: {e}")
                self.options.play_music('assets/audio/menu_theme.wav')
                return True
        return False
    
    def resize(self, new_screen_size):
        """Resizes the menu to fit a new screen size.

        Args:
            new_screen_size (Tuple[int, int]): The new size of the screen.
        """
        self.screen_size = new_screen_size
        self.setup_main_menu()  # Recalculate menu item positions
        
    def setup_main_menu(self):
        """Sets up the layout of the main menu."""
        # Use exact center of screen width for better positioning
        button_width = 200
        button_height = 50
        
        # Center position in screen
        center_x = self.screen_size[0] // 2 - button_width // 2
        
        # Position buttons in the middle third of the screen
        # This makes the layout work better at different aspect ratios
        title_y = self.screen_size[1] * 0.25  # Title at 25% of screen height
        start_y = self.screen_size[1] * 0.45  # Start buttons near middle (45%)
        
        # Button spacing proportional to screen height (but with a minimum)
        button_spacing = max(60, int(self.screen_size[1] * 0.08))
        
        self.menu_items = [
            MenuItem("Single Player", GameState.SINGLE_PLAYER, 
                    (center_x, int(start_y)),
                    (button_width, button_height)),
            MenuItem("Local Co-op", GameState.LOCAL_COOP,
                    (center_x, int(start_y + button_spacing)),
                    (button_width, button_height)),
            MenuItem("Options", GameState.OPTIONS,
                    (center_x, int(start_y + button_spacing * 2)),
                    (button_width, button_height)),
            MenuItem("Quit", GameState.QUIT,
                    (center_x, int(start_y + button_spacing * 3)),
                    (button_width, button_height))
        ]
    
    def handle_input(self, events):
        """Handles user input for the menu.

        Args:
            events (list): A list of Pygame events.

        Returns:
            GameState: The current game state.
        """
        mouse_pos = pygame.mouse.get_pos()
        
        for item in self.menu_items:
            item.is_hovered = item.rect.collidepoint(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for item in self.menu_items:
                    if item.is_hovered:
                        self.state = item.action
                        return item.action
        
        return self.state
    
    def draw(self, screen):
        """Draws the menu on the screen.

        Args:
            screen (pygame.Surface): The surface to draw the menu on.
        """
        # Fill background with a dark color
        screen.fill((20, 20, 40))
        
        # Draw title
        title_text = "Runic Lands"
        title_surface = self.title_font.render(title_text, True, (255, 215, 0))
        
        # Calculate title position using the same formula as in setup_main_menu
        title_y = self.screen_size[1] * 0.25  # Title at 25% of screen height
        title_rect = title_surface.get_rect(
            center=(self.screen_size[0] // 2, int(title_y))
        )
        screen.blit(title_surface, title_rect)
        
        # Draw menu items
        for item in self.menu_items:
            item.draw(screen, self.font)
            
        # Draw version number - position in bottom left, proportional to screen size
        version_text = "v0.1"
        version_font = pygame.font.Font(None, max(18, int(self.screen_size[1] * 0.03)))  # Scale font with screen
        version_surface = version_font.render(version_text, True, (150, 150, 150))
        
        # Place version in bottom left with padding proportional to screen size
        padding_x = max(10, int(self.screen_size[0] * 0.01))
        padding_y = max(10, int(self.screen_size[1] * 0.02))
        version_pos = (padding_x, self.screen_size[1] - version_surface.get_height() - padding_y)
        screen.blit(version_surface, version_pos)
        
        # pygame.display.flip() # Removed redundant flip 