"""
Runic Lands - Main Game Module

Entry point for the game that initializes systems and runs the main loop.
Uses the refactored architecture with separate managers for state, assets, and configuration.
"""

import pygame
import sys
import random
import time

from src.systems.state_manager import StateManager, GameState
from src.assets.asset_manager import AssetManager
from src.config.config_manager import ConfigManager
from src.systems.synapstex import SynapstexGraphics, RenderLayer, BlendMode, ParticleType

class RunicLands:
    """
    Main game class that initializes systems and manages the game loop.
    Acts as a coordinator between various game systems.
    """
    
    def __init__(self):
        """Initialize game systems and setup the initial state"""
        # Initialize Pygame
        pygame.init()
        
        # Set up managers in the correct order:
        # 1. Config manager first to load settings
        self.config = ConfigManager()
        
        # 2. Get display settings from config
        resolution = self.config.get_resolution()
        fullscreen = self.config.get_fullscreen()
        vsync = self.config.get_vsync()
        
        # 3. Initialize graphics system with config settings
        self.graphics = SynapstexGraphics(
            screen_size=resolution,
            fullscreen=fullscreen,
            vsync=vsync
        )
        
        # 4. Initialize asset manager
        self.assets = AssetManager()
        
        # 5. Initialize state manager
        self.state_manager = StateManager()
        
        # Set up game clock
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        self.last_update = pygame.time.get_ticks()
        
        # Track total game time
        self.total_time = 0
        
        # Register state handlers
        self._register_state_handlers()
        
        # Preload essential assets
        self._preload_assets()
    
    def _register_state_handlers(self):
        """Register event, update, and draw handlers for each game state"""
        # Main Menu
        self.state_manager.register_event_handler(GameState.MAIN_MENU, self._handle_main_menu_events)
        self.state_manager.register_update_handler(GameState.MAIN_MENU, self._update_main_menu)
        self.state_manager.register_draw_handler(GameState.MAIN_MENU, self._draw_main_menu)
        
        # Single Player
        self.state_manager.register_event_handler(GameState.SINGLE_PLAYER, self._handle_game_events)
        self.state_manager.register_update_handler(GameState.SINGLE_PLAYER, self._update_game)
        self.state_manager.register_draw_handler(GameState.SINGLE_PLAYER, self._draw_game)
        
        # Paused State
        self.state_manager.register_event_handler(GameState.PAUSED, self._handle_paused_events)
        self.state_manager.register_update_handler(GameState.PAUSED, self._update_paused)
        self.state_manager.register_draw_handler(GameState.PAUSED, self._draw_paused)
        
        # TODO: Add handlers for other states as they are implemented
    
    def _preload_assets(self):
        """Preload essential game assets"""
        # Default sprites
        sprites = {
            'player': 'assets/sprites/player.png',
            'tiles': 'assets/sprites/tiles.png',
            'items': 'assets/sprites/items.png',
            'ui': 'assets/sprites/ui.png'
        }
        
        # Sound effects
        sounds = {
            'menu_click': 'assets/audio/click.wav',
            'attack': 'assets/audio/attack.wav'
        }
        
        # Preload assets
        self.assets.preload_assets(sprites, sounds)
        
        # Start menu music
        self.assets.play_music('menu_theme', 'assets/audio/menu_theme.wav', loop=True,
                             volume=self.config.get('audio', 'master_volume', 0.7) * 
                                   self.config.get('audio', 'music_volume', 0.5))
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_update) / 1000.0  # Convert to seconds
            self.last_update = current_time
            
            # Update total game time
            self.total_time += dt
            
            # Process events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            
            # Handle events for current state
            self.state_manager.handle_events(events)
            
            # Update current state
            self.state_manager.update(dt)
            
            # Check if we should quit
            if self.state_manager.current_state == GameState.QUIT:
                running = False
            
            # Draw current state
            self.state_manager.draw(self.graphics.screen)
            
            # Update display
            pygame.display.flip()
            
            # Maintain frame rate
            self.clock.tick(self.target_fps)
        
        # Cleanup and exit
        self._cleanup()
        pygame.quit()
        sys.exit()
    
    def _cleanup(self):
        """Perform cleanup operations before exiting"""
        # Save configuration
        self.config.save_config()
        
        # Clean up assets
        self.assets.cleanup()
        
        # Clean up graphics resources
        self.graphics.cleanup()

    # ========== Main Menu State Handlers ==========
    
    def _handle_main_menu_events(self, event):
        """Handle events for the main menu state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameState.QUIT)
                return True
            elif event.key == pygame.K_RETURN:
                self.state_manager.change_state(GameState.SINGLE_PLAYER)
                return True
            elif event.key == pygame.K_o:
                self.state_manager.change_state(GameState.OPTIONS, push_to_stack=True)
                return True
        return False
    
    def _update_main_menu(self, dt):
        """Update logic for the main menu state"""
        # Main menu animation updates would go here
        pass
    
    def _draw_main_menu(self, screen):
        """Draw the main menu state"""
        # Clear screen
        screen.fill((20, 20, 40))
        
        # Draw title
        title = "Runic Lands"
        title_font = self.assets.get_default_font(72)
        title_text = title_font.render(title, True, (255, 255, 255))
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 100))
        
        # Draw menu options
        menu_font = self.assets.get_default_font(36)
        menu_items = [
            ("Play", GameState.SINGLE_PLAYER),
            ("Options", GameState.OPTIONS),
            ("Quit", GameState.QUIT)
        ]
        
        for i, (text, state) in enumerate(menu_items):
            y_pos = 300 + i * 60
            item_text = menu_font.render(text, True, (255, 255, 255))
            screen.blit(item_text, (screen.get_width() // 2 - item_text.get_width() // 2, y_pos))
    
    # ========== Game State Handlers ==========
    
    def _handle_game_events(self, event):
        """Handle events for the game state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameState.PAUSED, push_to_stack=True)
                return True
        return False
    
    def _update_game(self, dt):
        """Update logic for the game state"""
        # Game update logic would go here
        pass
    
    def _draw_game(self, screen):
        """Draw the game state"""
        # Clear screen
        screen.fill((34, 139, 34))  # Green background
        
        # Game rendering would go here
        
        # Draw temporary placeholder text
        font = self.assets.get_default_font(36)
        text = font.render("Game Screen - Press ESC for Menu", True, (255, 255, 255))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 
                         screen.get_height() // 2 - text.get_height() // 2))

    # ========== Paused State Handlers ==========
    
    def _handle_paused_events(self, event):
        """Handle events for the paused state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to the previous game state (pop from stack)
                self.state_manager.pop_state()
                return True
            elif event.key == pygame.K_q:
                # Quit to main menu
                self.state_manager.change_state(GameState.MAIN_MENU)
                return True
            elif event.key == pygame.K_o:
                # Go to options
                self.state_manager.change_state(GameState.OPTIONS, push_to_stack=True)
                return True
        return False
    
    def _update_paused(self, dt):
        """Update logic for the paused state"""
        # Nothing to update while paused
        pass
    
    def _draw_paused(self, screen):
        """Draw the paused state"""
        # First draw the game screen underneath
        self._draw_game(screen)
        
        # Then draw a semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Draw pause menu
        title_font = self.assets.get_default_font(72)
        option_font = self.assets.get_default_font(36)
        
        # Title
        title = "PAUSED"
        title_text = title_font.render(title, True, (255, 255, 255))
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 100))
        
        # Menu options
        pause_options = [
            "Resume (ESC)",
            "Options (O)",
            "Quit to Menu (Q)"
        ]
        
        for i, text in enumerate(pause_options):
            y_pos = 300 + i * 60
            option_text = option_font.render(text, True, (255, 255, 255))
            screen.blit(option_text, (screen.get_width() // 2 - option_text.get_width() // 2, y_pos))

if __name__ == "__main__":
    game = RunicLands()
    game.run() 