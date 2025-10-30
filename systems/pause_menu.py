import pygame
from pygame import Surface, Rect
from systems.menu import GameState 

class PauseMenu:
    """
    A pause menu that can be displayed over the game screen.

    This class handles the creation, rendering, and input handling for the
    in-game pause menu, allowing the player to resume, access options,
    or quit to the main menu.
    """
    def __init__(self, screen_width: int, screen_height: int):
        """
        Initializes the PauseMenu.

        Args:
            screen_width (int): The width of the screen.
            screen_height (int): The height of the screen.
        """
        self.screen_size = (screen_width, screen_height)
        self.width = 300
        self.height = 400
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (screen_width // 2, screen_height // 2)
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.background_color = (10, 10, 30, 200) # Semi-transparent dark blue
        self.border_color = (150, 150, 200)
        self.text_color = (230, 230, 255)
        self.highlight_color = (100, 100, 255)
        self.button_color = (70, 70, 180)
        
        self.is_visible = False
        self.selected_option = 0
        self._setup_options()
        
    def resize(self, new_screen_size):
        """
        Recalculates menu position and option layout on screen resize.

        Args:
            new_screen_size (Tuple[int, int]): The new screen dimensions.
        """
        self.screen_size = new_screen_size
        # Recenter the menu rectangle
        self.rect.center = (new_screen_size[0] // 2, new_screen_size[1] // 2)
        # Recalculate option positions
        self._setup_options()
        print(f"DEBUG: PauseMenu resized to {new_screen_size}")
        
    def _setup_options(self):
        """
        Sets up the menu options and their rectangles relative to the menu rect.

        This internal method defines the text, action, and position for each
        button in the pause menu.
        """
        self.options = [
            {"text": "Resume", "action": "resume"},
            {"text": "Options", "action": "options"},
            {"text": "Save Game", "action": "save_game"},
            {"text": "Load Game", "action": "load_game"}, # Placeholder
            {"text": "Quit to Menu", "action": "quit"}
        ]
        
        button_width = self.width - 40
        button_height = 40
        start_y = self.rect.top + 80 # Start below title
        spacing = 55
        
        for i, option in enumerate(self.options):
            option['rect'] = pygame.Rect(
                self.rect.left + 20,
                start_y + i * spacing,
                button_width,
                button_height
            )
        
    def toggle(self):
        """
        Toggles the visibility of the pause menu.

        Returns:
            bool: The new visibility state of the menu.
        """
        self.is_visible = not self.is_visible
        if self.is_visible:
            # Always reset selection to top when opening
            self.selected_option = 0
        return self.is_visible
        
    def handle_input(self, event):
        """
        Handles a single event for the pause menu.

        This method processes keyboard and mouse inputs to navigate the menu
        and trigger actions.

        Args:
            event (pygame.event.Event): The event to handle.

        Returns:
            Optional[str]: An action string if an action is triggered, otherwise None.
        """
        if not self.is_visible:
            return None
                    
        if event.type == pygame.KEYDOWN:
            # Do NOT handle ESC here - let main game loop handle it
            # to prevent conflicts and event loops
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                return None  # Just change selection, no action
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                return None  # Just change selection, no action
            elif event.key == pygame.K_RETURN:
                # Return the action corresponding to selected option
                action = self.options[self.selected_option]["action"]
                
                # Only reset selection when NOT resuming (since menu will be hidden)
                if action != "resume":
                    self.selected_option = 0
                    
                return action
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if any button was clicked
            mouse_pos = pygame.mouse.get_pos()
            for i, option in enumerate(self.options):
                if option['rect'].collidepoint(mouse_pos):
                    action = option["action"]
                    
                    # Only reset selection when NOT resuming (since menu will be hidden)
                    if action != "resume":
                        self.selected_option = 0
                        
                    return action
                    
        elif event.type == pygame.MOUSEMOTION:
            # Update selected option based on mouse position
            mouse_pos = pygame.mouse.get_pos()
            for i, option in enumerate(self.options):
                if option['rect'].collidepoint(mouse_pos):
                    self.selected_option = i
                    break
        
        return None
        
    def draw(self, screen: Surface):
        """
        Draws the pause menu on the given surface.

        Args:
            screen (pygame.Surface): The screen surface to draw on.
        """
        if not self.is_visible:
            return
            
        # Draw semi-transparent background
        pygame.draw.rect(screen, self.background_color, self.rect, border_radius=10)
        
        # Draw title
        title_text = self.title_font.render("Paused", True, self.highlight_color)
        title_rect = title_text.get_rect(center=(self.rect.centerx, self.rect.top + 50))
        screen.blit(title_text, title_rect)
        
        # Draw menu options
        for i, option in enumerate(self.options):
            # Draw button background when hovered
            if i == self.selected_option:
                pygame.draw.rect(screen, self.highlight_color, option['rect'], border_radius=5)
                pygame.draw.rect(screen, self.button_color, option['rect'], 1, border_radius=5)
            
            # Draw text centered in the button
            text = self.font.render(option["text"], True, self.text_color)
            
            # Center text in the button
            center_x = option['rect'].centerx
            center_y = option['rect'].centery
            text_rect = text.get_rect(center=(center_x, center_y))
            
            screen.blit(text, text_rect) 