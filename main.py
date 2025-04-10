import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
import time
import random
import os # Added os import
import math

# Ensure the project root directory is on the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    # Optional: Log the path addition for debugging
    print(f"DEBUG: Added to sys.path: {project_root}") # Uncommented for verification

# Now imports should work regardless of execution method
import pygame
from enum import Enum, auto
from entities.player import Player
from systems.combat import CombatSystem
from systems.world import World
from systems.menu import MenuSystem, GameState
from systems.options import OptionsSystem
from systems.options_menu import OptionsMenu, OptionsMenuState
from systems.inventory import InventoryUI, create_example_items, Item, ItemType
from systems.synapstex import SynapstexGraphics, RenderLayer, BlendMode, ParticleType
from systems.pause_menu import PauseMenu
from systems.save_manager import SaveManager, SaveCorruptionError, VersionMismatchError

# Set up logging
def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_filename = log_dir / f"game_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    crash_filename = log_dir / f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG) # Set root logger to lowest level

    # File Handler (logs everything DEBUG and above)
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console Handler (logs INFO and above to console)
    console_handler = logging.StreamHandler(sys.stdout) 
    console_handler.setLevel(logging.INFO) # Log INFO and higher to console
    console_formatter = logging.Formatter('%(levelname)s: %(name)s: %(message)s') # Simpler format for console
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Set up global exception handler
    def handle_exception(exc_type, exc_value, exc_traceback):
        # Log the exception first
        logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Format the traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = "".join(tb_lines)
        
        # Save detailed crash report
        try:
            with open(crash_filename, 'w', encoding='utf-8') as f:
                f.write(f"Crash Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=\n" * 40)
                f.write("CRASH REPORT\n")
                f.write("=\n" * 40)
                f.write(tb_text)
            logger.info(f"Crash report saved to {crash_filename}")
        except Exception as write_error:
            logger.error(f"Failed to write crash report: {write_error}")
            
        # Also print traceback to stderr for immediate visibility
        print("\n--- UNHANDLED EXCEPTION --- ", file=sys.stderr)
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
        print("-------------------------", file=sys.stderr)
        print(f"Crash report also saved to: {crash_filename}", file=sys.stderr)

    sys.excepthook = handle_exception
    
    logger.info(f"Logging initialized. Log file: {log_filename}")
    return logger

class Game:
    def __init__(self):
        try:
            # Initialize Pygame FIRST
            pygame.init()
            
            # Set up logging immediately after pygame init
            self.logger = setup_logging()
            self.logger.info("Pygame initialized, setting up logger.")
            
            # Initialize Options System (needed for settings)
            self.options = OptionsSystem()
            self.logger.info("Options system initialized.")

            # Get screen settings from options
            self.screen_size = tuple(self.options.video.get('resolution', (800, 600)))
            fullscreen = self.options.video.get('fullscreen', False)
            vsync = self.options.video.get('vsync', True)
            self.logger.info(f"Screen settings: {self.screen_size}, Fullscreen: {fullscreen}, VSync: {vsync}")

            # Initialize display
            display_flags = 0
            if fullscreen:
                display_flags = pygame.FULLSCREEN  # Use pygame's constant
            if vsync:
                display_flags |= pygame.DOUBLEBUF  # Add DOUBLEBUF with OR operation
            
            # Debug the actual values we're using
            self.logger.debug(f"Using flags: {display_flags} (pygame.FULLSCREEN={pygame.FULLSCREEN}, pygame.DOUBLEBUF={pygame.DOUBLEBUF})")
            self.screen = pygame.display.set_mode(self.screen_size, display_flags)
            # Update screen_size again in case set_mode adjusted it (e.g., fullscreen)
            self.screen_size = self.screen.get_size()
            pygame.display.set_caption("Runic Lands")
            self.logger.info(f"Display initialized to: {self.screen_size}, Flags: {self.screen.get_flags()}")
            
            # Initialize graphics system (AFTER display setup)
            self.graphics = SynapstexGraphics(self.screen_size, fullscreen=fullscreen, vsync=vsync)
            self.graphics.particle_system.set_screen_size(*self.screen_size) # Set particle screen size
            
            # Initialize particle system based on settings
            particles_enabled = self.options.video.get('particles_enabled', True)
            if particles_enabled:
                self.graphics.particle_system.enable()
            else:
                self.graphics.particle_system.disable()
            self.logger.info(f"Graphics engine initialized, particles {'enabled' if particles_enabled else 'disabled'}.")

            # Initialize other core systems (AFTER display and graphics)
            self.menu = MenuSystem(self.screen_size, self.options)
            self.options_menu = OptionsMenu(self.screen_size, self.options)
            self.save_manager = SaveManager()
            self.pause_menu = PauseMenu(*self.screen_size) # Ensure PauseMenu also takes screen size
            # Immediately resize UI elements to match the actual initial screen size
            self.menu.resize(self.screen_size) if hasattr(self.menu, 'resize') else None
            self.options_menu.resize(self.screen_size)
            self.pause_menu.resize(self.screen_size) if hasattr(self.pause_menu, 'resize') else None
            self.logger.info("UI Systems (Menu, Options, Pause, Save) initialized and resized.")
            
            # Initialize game state variables
            self.game_mode = GameState.MAIN_MENU
            self._previous_mode = GameState.MAIN_MENU
            self._from_pause_menu = False
            self.world = None
            self.combat = None
            self.players = []
            self.inventory_ui = None # InventoryUI is created later
            self.logger.info("Game state variables initialized.")
            
            # Initialize time tracking
            self.last_update = pygame.time.get_ticks()
            self.last_time = time.time()
            self.play_time = 0
            self.clock = pygame.time.Clock()
            self.target_fps = 60
            # Initialize FPS tracking variables
            self.fps_counter = 0
            self.fps_timer = time.time()
            self.current_fps = 0
            self.logger.info("Time tracking initialized.")
            
            # Set the video change callback to handle screen resizing
            self.options.set_video_change_callback(self.apply_video_settings)
            self.logger.info("Video settings change callback set.")
            
            # Cache common UI elements
            self._cache_ui_elements()
            self.logger.info("UI elements cached.")
            
            # Start menu music by initiating the queue system through MenuSystem
            if self.menu and hasattr(self.menu, 'start_menu_music'):
                self.menu.start_menu_music()
                self.logger.info("Menu music started.")
                
            # Continue with game initialization
            self.logger.info("Game initialized successfully")
            
        except Exception as e:
            # Log the error even if it happens during init
            # Note: logger might not be fully set up if error is very early
            if hasattr(self, 'logger'):
                self.logger.error(f"CRITICAL ERROR during game initialization: {e}", exc_info=True)
            else:
                # Fallback print if logger failed
                print(f"CRITICAL ERROR during game initialization (logging not ready): {e}")
                traceback.print_exc()
            
            # Attempt graceful shutdown
            try:
                if pygame.get_init():
                    pygame.quit()
            except Exception:
                pass # Ignore errors during shutdown after a critical init failure
                
            # Exit immediately after critical init failure
            sys.exit(1)
        
    def _cache_ui_elements(self):
        """Cache commonly used UI elements"""
        self._ui_cache = {}
        
        # Create and cache the control hints background
        hints_bg = self.graphics.create_rounded_rect(
            (200, 60), 10, (0, 0, 0), 150
        )
        self.graphics.cache_surface('hints_bg', hints_bg)
        
        # Create and cache the inventory background overlay
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.graphics.cache_surface('inventory_overlay', overlay)
    
    def init_single_player(self):
        self.logger.info("Initializing single-player mode...")
        try:
            # Clear existing render layers
            self.logger.debug("Clearing render layers...")
            for layer in RenderLayer:
                self.graphics.clear_layer(layer)
            self.logger.debug("Render layers cleared.")
                
            # Create a new world or load existing if needed
            self.logger.debug("Creating world...")
            self.world = World(seed=random.randint(0, 999999)) 
            self.logger.debug(f"World created with seed: {self.world.seed}")
            self.combat = CombatSystem()
            self.logger.debug("Combat system initialized.")
            
            # Get the spawn point closest to the center for single player
            spawn = self.world.get_centered_spawn()
            self.logger.debug(f"Using centered spawn point: {spawn}")
            
            controls = {
                'up': self.options.get_keybind('player1', 'up'),
                'down': self.options.get_keybind('player1', 'down'),
                'left': self.options.get_keybind('player1', 'left'),
                'right': self.options.get_keybind('player1', 'right'),
                'attack': self.options.get_keybind('player1', 'attack'),
                'inventory': self.options.get_keybind('player1', 'inventory'),
                'run': self.options.get_keybind('player1', 'run')  # Added run keybind
            }
            self.logger.debug("Player controls retrieved.")
            
            self.players = [Player(*spawn, (255, 0, 0), controls, self.world)]
            self.logger.debug("Player entity created.")
            self.game_mode = GameState.SINGLE_PLAYER
            
            # Set up inventory UI for the player
            self.inventory_ui = InventoryUI(self.players[0].inventory, self.screen_size)
            self.logger.debug("Inventory UI initialized.")
            
            # Add world and player to render layers
            self.graphics.add_to_layer(RenderLayer.TERRAIN, self.world)
            self.graphics.add_to_layer(RenderLayer.ENTITIES, self.players[0])
            self.logger.debug("World and player added to render layers.")
            
            # Switch to game music using the new section-based approach
            if pygame.mixer.get_init():
                self.options.queue_game_music()
            
            self.logger.info("Single-player mode initialized successfully.")
            
        except Exception as e:
            self.logger.error(f"CRITICAL ERROR during single-player initialization: {e}", exc_info=True)
            # Attempt to return to main menu gracefully
            self.return_to_menu()
    
    def init_local_coop(self):
        # Clear existing render layers
        for layer in RenderLayer:
            self.graphics.clear_layer(layer)
            
        self.world = World(seed=random.randint(0, 999999))  # Use random seed for world generation
        self.combat = CombatSystem()
        spawn1, spawn2 = self.world.spawn_points
        
        p1_controls = {
            'up': self.options.get_keybind('player1', 'up'),
            'down': self.options.get_keybind('player1', 'down'),
            'left': self.options.get_keybind('player1', 'left'),
            'right': self.options.get_keybind('player1', 'right'),
            'attack': self.options.get_keybind('player1', 'attack'),
            'inventory': self.options.get_keybind('player1', 'inventory'),
            'run': self.options.get_keybind('player1', 'run')  # Added run keybind
        }
        p2_controls = {
            'up': self.options.get_keybind('player2', 'up'),
            'down': self.options.get_keybind('player2', 'down'),
            'left': self.options.get_keybind('player2', 'left'),
            'right': self.options.get_keybind('player2', 'right'),
            'attack': self.options.get_keybind('player2', 'attack'),
            'inventory': self.options.get_keybind('player2', 'inventory'),
            'run': self.options.get_keybind('player2', 'run')  # Added run keybind
        }
        
        self.players = [
            Player(*spawn1, (255, 0, 0), p1_controls, self.world),
            Player(*spawn2, (0, 0, 255), p2_controls, self.world)
        ]
        self.game_mode = GameState.LOCAL_COOP
        
        # Set up inventory UI for player 1
        self.inventory_ui = InventoryUI(self.players[0].inventory, self.screen_size)
        
        # Add world and players to render layers
        self.graphics.add_to_layer(RenderLayer.TERRAIN, self.world)
        for player in self.players:
            self.graphics.add_to_layer(RenderLayer.ENTITIES, player)
        
        # Switch to game music using the new section-based approach
        if pygame.mixer.get_init():
            self.options.queue_game_music()
    
    def return_to_menu(self):
        """Return to the main menu from game"""
        # Set game mode to main menu FIRST
        self.game_mode = GameState.MAIN_MENU
        self.logger.debug("Setting game mode to MAIN_MENU")
        
        # Clear existing particles when returning to menu
        if hasattr(self.graphics, 'particle_system'):
            self.graphics.particle_system.particles.clear()
            # Temporarily disable particles during transition
            self.graphics.particle_system.disable()
            
        # Clear existing render layers
        for layer in RenderLayer:
            self.graphics.clear_layer(layer)
            
        self.camera_x = 0
        self.camera_y = 0
        
        # Reset game state
        self.world = None
        self.combat = None
        self.players = []
        self.inventory_ui = None
        
        # Reset menu state - use the newly added reset method
        self.menu.reset()  # This will set menu.state to MAIN_MENU
        self.pause_menu.is_visible = False
        
        # Reset time tracking
        self.play_time = 0
        self.last_time = time.time()
        self.last_update = pygame.time.get_ticks()
        
        # Re-enable particles after cleanup if they were enabled in settings
        if hasattr(self.graphics, 'particle_system'):
            if self.options.video.get('particles_enabled', True):
                self.graphics.particle_system.enable()
        
        # The reset method in MenuSystem will handle playing the menu music
        self.logger.debug("Successfully returned to main menu")
    
    def handle_input(self):
        try:
            # Get all events except music events (those are handled directly in the main loop)
            events = pygame.event.get()
            processed_events = []
            
            # Store keyboard state for movement
            keys = pygame.key.get_pressed()
            
            # First pass: handle critical events (quit, inventory/pause toggle)
            for event in events:
                # Check for music end events - these should already be handled in the main loop
                if hasattr(self.options, 'music_end_event') and event.type == self.options.music_end_event:
                    # If any music events made it here, handle them as a backup
                    print(f"DEBUG: Backup music handling in handle_input at {pygame.time.get_ticks()} ms")
                    self.options.handle_music_event(event)
                    processed_events.append(event)
                    continue
                
                # Always handle quit events
                if event.type == pygame.QUIT:
                    self.logger.debug("Quit event received")
                    pygame.quit()
                    sys.exit()
                
                # Toggle particle system with 'P' key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    if hasattr(self.graphics, 'particle_system'):
                        if self.graphics.particle_system.disabled:
                            self.graphics.particle_system.enable()
                            self.logger.debug("Particle system enabled with P key")
                        else:
                            self.graphics.particle_system.disable()
                            self.logger.debug("Particle system disabled with P key")
                        processed_events.append(event)
                        continue
                
                # Spacebar shows debug info for main menu
                if self.game_mode == GameState.MAIN_MENU and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    particle_status = "DISABLED" if (hasattr(self.graphics, 'particle_system') and self.graphics.particle_system.disabled) else "ENABLED"
                    particle_setting = "ENABLED" if self.options.video.get('particles_enabled', True) else "DISABLED"
                    self.logger.info(f"DEBUG - Particles: System: {particle_status}, Setting: {particle_setting}, Count: {len(self.graphics.particle_system.particles) if hasattr(self.graphics, 'particle_system') else 0}")
                    processed_events.append(event)
                    continue  # Skip further processing
                
                # Handle ESC key: Priority -> Inventory > Pause > Options > Quit
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.logger.debug(f"ESC key pressed. Game mode: {self.game_mode}, Inventory visible: {self.inventory_ui.visible if self.inventory_ui else False}, Pause menu visible: {self.pause_menu.is_visible}, Options menu active: {self.game_mode == GameState.OPTIONS}")
                    
                    # 1. Close Inventory if open
                    if self.inventory_ui and self.inventory_ui.visible:
                        self.logger.debug("ESC: Closing inventory.")
                        self.inventory_ui.visible = False # Directly set visibility
                        self.options.play_sound('menu_close') # Sound for closing
                        processed_events.append(event)
                        continue
                    
                    # 2. Handle Options Menu ESC (if inventory is not open)
                    if self.game_mode == GameState.OPTIONS:
                        self.logger.debug("ESC: Closing options menu.")
                        self.options.save_settings()
                        self.options.play_sound('menu_close') # Sound for closing
                        if self._from_pause_menu:
                            self.game_mode = self._previous_mode
                            self.pause_menu.is_visible = True
                            self._from_pause_menu = False
                        else:
                            self.game_mode = GameState.MAIN_MENU
                            self.menu.state = GameState.MAIN_MENU
                        processed_events.append(event)
                        continue
                    
                    # 3. Toggle Pause Menu (if playing and inventory/options not open)
                    if self.game_mode not in [GameState.MAIN_MENU, GameState.OPTIONS]:
                        is_opening = not self.pause_menu.is_visible
                        self.pause_menu.is_visible = is_opening
                        self.logger.debug(f"ESC: {'Opening' if is_opening else 'Closing'} pause menu.")
                        self.options.play_sound('menu_open' if is_opening else 'menu_close')
                        processed_events.append(event)
                        continue
                    
                    # 4. Quit from Main Menu (if nothing else was open)
                    if self.game_mode == GameState.MAIN_MENU:
                        self.logger.debug("ESC: Quitting from main menu.")
                        pygame.quit()
                        sys.exit()
                    
                # Handle Inventory toggle key ('I' or configured key)
                if self.game_mode not in [GameState.MAIN_MENU, GameState.OPTIONS] and not self.pause_menu.is_visible:
                    if event.type == pygame.KEYDOWN and self.players and self.inventory_ui:
                        # --- DEBUG LOG --- #
                        expected_inv_key = self.players[0].controls.get('inventory')
                        self.logger.debug(f"KEYDOWN Event: key={event.key} (pygame code), Expected Inventory Key: {expected_inv_key} (pygame code)")
                        # --- END DEBUG --- #
                        
                        # Check against the specific keybind for player 1's inventory
                        if event.key == expected_inv_key:
                            is_opening = not self.inventory_ui.visible
                            self.inventory_ui.toggle_visibility()
                            self.logger.debug(f"Inventory key pressed: {'Opening' if is_opening else 'Closing'} inventory.")
                            self.options.play_sound('menu_open' if is_opening else 'menu_close')
                            processed_events.append(event)
                            continue # Mark as processed
            
            # Remove processed events before passing to other handlers
            remaining_events = [e for e in events if e not in processed_events]
            
            # Second pass: handle game state-specific input
            if self.game_mode == GameState.MAIN_MENU:
                # Handle main menu input
                new_state = self.menu.handle_input(remaining_events)
                if new_state != GameState.MAIN_MENU:
                    # Clear any main menu particles before transitioning
                    if hasattr(self.graphics, 'particle_system'):
                        self.graphics.particle_system.particles.clear()
                        
                    if new_state == GameState.SINGLE_PLAYER:
                        self.init_single_player()
                    elif new_state == GameState.LOCAL_COOP:
                        self.init_local_coop()
                    elif new_state == GameState.OPTIONS:
                        self.options_menu.state = OptionsMenuState.MAIN
                        self.game_mode = GameState.OPTIONS
                        self._from_pause_menu = False
                    elif new_state == GameState.QUIT:
                        pygame.quit()
                        sys.exit()
            
            elif self.game_mode == GameState.OPTIONS:
                # Handle options menu input
                result = self.options_menu.handle_input(remaining_events)
                self.logger.debug(f"OptionsMenu handle_input result: {result}") # DEBUG LOG
                
                # Check if the options menu signaled to exit
                if result == 'exit_options':
                    self.logger.debug("Exiting options menu.")
                    # Save settings before transitioning
                    self.options.save_settings()
                    
                    # Transition back to the previous state (main menu or paused game)
                    if self._from_pause_menu:
                        self.game_mode = self._previous_mode
                        self.pause_menu.is_visible = True # Re-show pause menu
                        self._from_pause_menu = False
                        self.logger.debug(f"Returning to paused game mode: {self.game_mode}")
                    else:
                        self.game_mode = GameState.MAIN_MENU
                        self.menu.state = GameState.MAIN_MENU  # Also update menu state
                        self.logger.debug("Returning to main menu.")
                    
                    # Reset options menu state
                    self.options_menu = None  # Force recreation of options menu
                    self.options_menu = OptionsMenu(self.screen_size, self.options)  # Recreate options menu
                    return
                
                # Handle ESC key in options menu
                for event in remaining_events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        # Save settings before transitioning
                        self.options.save_settings()
                        
                        if self._from_pause_menu:
                            self.game_mode = self._previous_mode
                            self.pause_menu.is_visible = True
                            self._from_pause_menu = False
                        else:
                            self.game_mode = GameState.MAIN_MENU
                            self.menu.state = GameState.MAIN_MENU  # Also update menu state
                        
                        # Reset options menu state
                        self.options_menu = None  # Force recreation of options menu
                        self.options_menu = OptionsMenu(self.screen_size, self.options)  # Recreate options menu
                        return
            
            elif self.game_mode not in [GameState.MAIN_MENU, GameState.OPTIONS]:
                # Handle pause menu if visible
                if self.pause_menu.is_visible:
                    for event in remaining_events:
                        action = self.pause_menu.handle_input(event)
                        if action:
                            self.logger.debug(f"Pause menu action: {action}")
                            if action == "resume":
                                self.pause_menu.is_visible = False
                                self.options.play_sound('menu_click')
                            elif action == "quit":
                                self.pause_menu.is_visible = False
                                self.return_to_menu()
                                return
                            elif action == "save_game":
                                self.save_current_game()
                            elif action == "load_game":
                                self.load_game()
                            elif action == "options":
                                self._previous_mode = self.game_mode
                                self._from_pause_menu = True
                                self.options_menu.state = OptionsMenuState.MAIN
                                self.game_mode = GameState.OPTIONS
                                self.pause_menu.is_visible = False
                            break
                
                # Handle inventory UI if visible and pause menu is not
                elif self.inventory_ui and self.inventory_ui.visible:
                    for event in remaining_events:
                        if self.inventory_ui.handle_event(event):
                            break
                
                # Handle gameplay input if not paused or in inventory
                else:
                    # Handle special keys
                    for event in remaining_events:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_p:
                                if hasattr(self.graphics.particle_system, 'disabled'):
                                    self.graphics.particle_system.disabled = not self.graphics.particle_system.disabled
                                    self.logger.debug(f"Particles {'disabled' if self.graphics.particle_system.disabled else 'enabled'}")
                            elif self.players and self.inventory_ui and event.key == self.players[0].controls.get('inventory'):
                                self.logger.debug("Opening inventory")
                                self.inventory_ui.toggle_visibility()
                                self.options.play_sound('menu_click')
                    
                    # Handle player movement
                    if self.players:
                        for player in self.players:
                            player.move(keys)
                    
                    # Handle combat for respective game modes
                    if not self.players:
                        # No players available, likely during a transition between game states
                        # Skip combat checks
                        pass
                    elif self.game_mode == GameState.LOCAL_COOP and len(self.players) > 1:
                        if keys[self.players[0].controls['attack']]:
                            if self.combat.handle_attack(self.players[0], self.players[1]):
                                self.options.play_sound('attack')
                        if keys[self.players[1].controls['attack']]:
                            if self.combat.handle_attack(self.players[1], self.players[0]):
                                self.options.play_sound('attack')
                    elif self.game_mode == GameState.SINGLE_PLAYER:
                        if keys[self.players[0].controls['attack']]:
                            self.options.play_sound('attack')

        except Exception as e:
            self.logger.error(f"Error in handle_input: {e}", exc_info=True)
            raise
    
    def update(self):
        # Calculate delta time
        now = pygame.time.get_ticks()
        dt = (now - self.last_update) / 1000.0
        self.last_update = now
        
        # Track FPS
        self.fps_counter += 1
        if now - self.fps_timer >= 1000:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_timer = now
            self.logger.debug(f"FPS: {self.current_fps}")
        
        if self.game_mode == GameState.MAIN_MENU:
            # Emit main menu particles if they're enabled
            if hasattr(self.graphics, 'particle_system'):
                try:
                    # Update existing particles
                    self.graphics.particle_system.update(dt)
                    
                    # Force enable particles for the main menu if they're explicitly enabled in settings
                    if self.options.video.get('particles_enabled', True) and self.graphics.particle_system.disabled:
                        self.graphics.particle_system.enable()
                        self.logger.debug("Force-enabled particles for main menu")
                    
                    emit_chance = 0.05
                    
                    # Stars - more dynamic patterns with occasional bursts
                    emit_chance = 0.05
                    
                    # Every ~10 seconds, create a small cluster of stars in one area
                    star_burst_interval = 10.0
                    if hasattr(self, 'last_star_burst_time'):
                        time_since_burst = now / 1000.0 - self.last_star_burst_time
                        if time_since_burst > star_burst_interval:
                            # Create a cluster of 3-7 stars in a small area
                            self.last_star_burst_time = now / 1000.0
                            cluster_x = random.uniform(0, self.screen_size[0])
                            cluster_y = random.uniform(0, self.screen_size[1] * 0.6)
                            cluster_size = random.randint(3, 7)
                            
                            # More varied star colors
                            star_colors = [
                                (220, 225, 255, 160),  # Blue-white
                                (255, 240, 220, 160),  # Yellowish-white
                                (255, 210, 180, 160),  # Orange-tinted
                                (220, 220, 255, 160),  # Light blue
                                (255, 255, 255, 160),  # Pure white
                            ]
                            
                            for _ in range(cluster_size):
                                # Emit stars in the cluster area with slight variation
                                self.graphics.particle_system.emit(
                                    x=cluster_x + random.uniform(-30, 30),
                                    y=cluster_y + random.uniform(-20, 20),
                                    particle_type=ParticleType.STAR,
                                    count=1,
                                    color=random.choice(star_colors),
                                    size_range=(1.0, 3.0),
                                    lifetime_range=(5.0, 10.0),
                                    use_world_space=False
                                )
                    else:
                        self.last_star_burst_time = now / 1000.0
                    
                    # Occasional "shooting star" effect (~every 15 seconds)
                    meteor_interval = 15.0
                    if hasattr(self, 'last_meteor_time'):
                        time_since_meteor = now / 1000.0 - self.last_meteor_time
                        if time_since_meteor > meteor_interval:
                            self.last_meteor_time = now / 1000.0
                            
                            # Start position (off one edge of the screen)
                            start_x = random.uniform(-50, self.screen_size[0] + 50)
                            start_y = random.uniform(-50, 50)  # Near top
                            
                            # Create meteor trail with 5-8 small stars
                            trail_length = random.randint(5, 8)
                            direction_x = random.uniform(-2.0, 2.0)
                            direction_y = random.uniform(0.5, 1.5)  # Always move downward
                            
                            # Normalize direction vector
                            magnitude = (direction_x**2 + direction_y**2)**0.5
                            if magnitude > 0:
                                direction_x /= magnitude
                                direction_y /= magnitude
                                
                            meteor_color = (255, 250, 230, 180)  # Warm white with higher alpha
                            
                            for i in range(trail_length):
                                # Stars get smaller along the trail
                                size_factor = 1.0 - (i / trail_length * 0.7)
                                lifetime_factor = 1.0 - (i / trail_length * 0.5)
                                
                                self.graphics.particle_system.emit(
                                    x=start_x + direction_x * i * 15,
                                    y=start_y + direction_y * i * 15,
                                    particle_type=ParticleType.STAR,
                                    count=1,
                                    color=meteor_color,
                                    size_range=(2.0 * size_factor, 3.5 * size_factor),
                                    lifetime_range=(1.5 * lifetime_factor, 3.0 * lifetime_factor),
                                    use_world_space=False
                                )
                    else:
                        self.last_meteor_time = now / 1000.0
                    
                    # Regular star emission
                    if random.random() < emit_chance:
                        # More varied star colors
                        star_colors = [
                            (220, 225, 255, 160),  # Blue-white
                            (255, 240, 220, 160),  # Yellowish-white
                            (255, 210, 180, 160),  # Orange-tinted
                            (220, 220, 255, 160),  # Light blue
                            (255, 255, 255, 160),  # Pure white
                        ]
                        
                        x_pos = random.uniform(0, self.screen_size[0])
                        
                        self.graphics.particle_system.emit(
                            x=x_pos,
                            y=random.uniform(0, self.screen_size[1] * 0.9),
                            particle_type=ParticleType.STAR,
                            count=1,
                            color=random.choice(star_colors),
                            size_range=(1.0, 3.5),  # More varied star sizes
                            lifetime_range=(5.0, 12.0),
                            use_world_space=False
                        )
                    
                    # Sparkles - softer appearance
                    if random.random() < 0.08:
                        sparkle_colors = [
                            (255, 255, 255, 180),  # White (dimmer)
                            (200, 255, 255, 180),  # Cyan tint (dimmer)
                            (255, 230, 200, 180),  # Warm tint (dimmer)
                        ]
                        x_pos = random.uniform(0, self.screen_size[0])
                        
                        self.graphics.particle_system.emit(
                            x=x_pos,
                            y=self.screen_size[1] + 5, # Start closer to screen bottom
                            particle_type=ParticleType.SPARKLE,
                            count=1, # Emit one at a time
                            color=random.choice(sparkle_colors),
                            size_range=(1.0, 2.5),  # Smaller sparkles
                            lifetime_range=(3.0, 6.0),
                            use_world_space=False
                        )
                    
                    # Leaves - natural look with more variation
                    if random.random() < 0.12:  # Doubled frequency (was 0.06)
                        # More varied leaf colors including yellows and reds
                        leaf_colors = [
                            (139, 69, 19, 200),    # Brown
                            (160, 82, 45, 200),    # Sienna
                            (110, 139, 61, 200),   # Olive green
                            (205, 133, 63, 200),   # Peru (tan)
                            (220, 200, 40, 200),   # Yellow
                            (240, 230, 80, 200),   # Light yellow
                            (210, 180, 60, 200),   # Golden
                            (180, 30, 30, 200),    # Red
                            (210, 90, 30, 200),    # Orange-red
                        ]
                        
                        # Random positions across the screen width
                        x_pos = random.uniform(0, self.screen_size[0])
                        
                        # Multiple leaves at once for more dense appearance
                        leaf_count = random.randint(1, 3)  # 1-3 leaves at a time
                        
                        for _ in range(leaf_count):
                            # Slight x-position variation for multiple leaves
                            leaf_x = x_pos + random.uniform(-50, 50)
                            
                            # Start above screen
                            self.graphics.particle_system.emit(
                                x=leaf_x,
                                y=random.uniform(-30, -10),  # Varied start heights
                                particle_type=ParticleType.LEAF,
                                count=1,
                                color=random.choice(leaf_colors),
                                size_range=(2.0, 5.5),  # Wider size range
                                lifetime_range=(6.0, 12.0),  # Longer lifetime for slower falling effect
                                use_world_space=False
                            )
                    
                    # Sunbeams - softer look
                    if random.random() < 0.02:
                        beam_colors = [
                            (255, 223, 186, 120),  # Soft yellow
                            (255, 210, 170, 120),  # Light orange
                            (230, 230, 255, 120),  # Light blue
                        ]
                        x_pos = random.uniform(0, self.screen_size[0])
                        
                        self.graphics.particle_system.emit(
                            x=x_pos,
                            y=self.screen_size[1],
                            particle_type=ParticleType.SUNBEAM,
                            count=1,
                            color=random.choice(beam_colors),
                            size_range=(1.5, 3.0),  # Narrower beams
                            lifetime_range=(3.0, 5.0),
                            use_world_space=False
                        )
                    
                    # Fireflies - softer glow
                    if random.random() < 0.05:
                        firefly_colors = [
                            (255, 255, 150, 200),  # Yellowish
                            (200, 255, 200, 200),  # Greenish
                            (255, 220, 150, 200),  # Orange-yellow
                        ]
                        x_pos = random.uniform(0, self.screen_size[0])
                        
                        self.graphics.particle_system.emit(
                            x=x_pos,
                            y=random.uniform(self.screen_size[1] * 0.3, self.screen_size[1] * 0.9),
                            particle_type=ParticleType.FIREFLY,
                            count=1,
                            color=random.choice(firefly_colors),
                            size_range=(2.0, 3.0),
                            lifetime_range=(9.0, 15.0),
                            use_world_space=False
                        )
                        
                    # Dust - smaller and subtler
                    if random.random() < 0.06:
                        dust_colors = [
                            (200, 200, 200, 80),  # Light gray (more transparent)
                            (200, 200, 230, 80),  # Light blue-gray
                            (230, 220, 200, 80),  # Light tan
                        ]
                        x_pos = random.uniform(0, self.screen_size[0])
                        
                        self.graphics.particle_system.emit(
                            x=x_pos,
                            y=random.uniform(0, self.screen_size[1]),
                            particle_type=ParticleType.DUST,
                            count=1,
                            color=random.choice(dust_colors),
                            size_range=(1.0, 2.5),  # Smaller dust
                            lifetime_range=(4.0, 7.0),
                            use_world_space=False
                        )
                except Exception as e:
                    self.logger.error(f"Error updating menu particles: {e}", exc_info=True)
                    self.graphics.particle_system.disabled = True

        # Update time tracking (only when not paused)
        if not self.pause_menu.is_visible:
            current_time = time.time()
            self.play_time += current_time - self.last_time
            self.last_time = current_time
            
        # Update particle system (even when paused for ambient effect)
        if hasattr(self.graphics, 'particle_system') and not self.graphics.particle_system.disabled:
            try:
                self.graphics.particle_system.update(dt)
            except Exception as e:
                self.logger.error(f"Error updating particle system: {e}", exc_info=True)
                self.graphics.particle_system.disabled = True # Disable particles on error
                
            # Emit new ambient particles periodically (only if particles are working)
            # Only emit world particles if we're in a game mode with a world
            if random.random() < 0.05 and self.world and self.game_mode not in [GameState.MAIN_MENU, GameState.OPTIONS]: 
                try:
                    # Get camera offset to emit particles in visible area
                    offset_x, offset_y = self.graphics.get_camera_offset()
                    # Emit in world space within the visible area
                    spawn_x = random.uniform(offset_x, offset_x + self.screen_size[0])
                    spawn_y = random.uniform(offset_y, offset_y + self.screen_size[1])
                    
                    # Use semi-transparent dust particles
                    dust_colors = [
                        (180, 180, 180, 40),  # Very transparent light gray
                        (200, 200, 230, 30),  # Very transparent light blue-gray
                    ]
                    
                    self.graphics.particle_system.emit(
                        x=spawn_x, y=spawn_y,
                        particle_type=ParticleType.DUST,
                        count=1,
                        color=random.choice(dust_colors),
                        size_range=(1.0, 2.0),
                        lifetime_range=(1.0, 3.0),
                        use_world_space=True
                    )
                except Exception as e:
                    self.logger.error(f"Error emitting particle: {e}", exc_info=True)
                    self.graphics.particle_system.disabled = True # Disable particles on error

        # Handle game state updates
        if self.game_mode == GameState.OPTIONS:
            pass # Options menu state is handled via handle_input
        elif self.game_mode == GameState.SINGLE_PLAYER or self.game_mode == GameState.LOCAL_COOP:
            # Only update gameplay elements if not paused and inventory is closed
            if self.world and self.players and not self.pause_menu.is_visible and not (self.inventory_ui and self.inventory_ui.visible):
                try:
                    # Update world first (including time)
                    self.world.update(dt, self.graphics) 
                    
                    # Update players
                    for player in self.players:
                        player.update(dt)
                        
                    # Update combat system
                    if self.combat:
                        self.combat.update(dt, self.players)
                        
                    # Update camera to follow the first player (in single player)
                    if self.players and self.game_mode == GameState.SINGLE_PLAYER:
                        target_x, target_y = self.players[0].rect.center
                        self.graphics.set_camera_target(target_x, target_y)
                        
                    # Optional: Update chunks based on player position (might need refinement for camera)
                    # if self.players:
                    #    self.world.update_chunks(self.players[0].pos[0], self.players[0].pos[1])
                        
                except Exception as e:
                    self.logger.error(f"Error during gameplay update: {e}", exc_info=True)
                    self.pause_menu.is_visible = True
        
        # Update inventory UI if visible
        if self.inventory_ui and self.inventory_ui.visible:
            self.inventory_ui.update(dt)
            
        if self.game_mode == GameState.MAIN_MENU:
            self.logger.debug("Main menu update end.")
    
    def draw(self):
        # Add debug info about particle system at the top less frequently
        if hasattr(self.graphics, 'particle_system'):
            # Only show debug message every 30 seconds (instead of 5 seconds)
            current_time = pygame.time.get_ticks()
            if not hasattr(self, '_last_particle_debug') or current_time - self._last_particle_debug > 30000:
                particle_count = len(self.graphics.particle_system.particles)
                print(f"Debug: Particles active: {particle_count}, Disabled: {self.graphics.particle_system.disabled}")
                self._last_particle_debug = current_time
            
        if self.game_mode == GameState.MAIN_MENU:
            self.logger.debug("Main menu draw start.")
            
        # Clear screen with background color based on game state
        if self.game_mode == GameState.MAIN_MENU:
            # Create a magical gradient background for the main menu
            # Smoother, deeper gradient
            bg_color_top = (5, 5, 20)        # Deeper blue
            bg_color_middle = (15, 10, 35)   # Darker indigo
            bg_color_bottom = (25, 5, 45)    # Deeper purple
            
            # Create gradient using a pre-rendered surface for performance
            gradient_cache_key = f"bg_gradient_{self.screen_size[0]}x{self.screen_size[1]}"
            gradient_surface = self.graphics.get_cached_surface(gradient_cache_key)
            
            if not gradient_surface:
                gradient_surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
                height = self.screen_size[1]
                rect_height = 1 # Draw line by line for smoothness
                
                for y in range(height):
                    progress = y / (height - 1)
                    if progress < 0.5:
                        blend_factor = progress * 2
                        color = [
                            int(bg_color_top[0] + (bg_color_middle[0] - bg_color_top[0]) * blend_factor),
                            int(bg_color_top[1] + (bg_color_middle[1] - bg_color_top[1]) * blend_factor),
                            int(bg_color_top[2] + (bg_color_middle[2] - bg_color_top[2]) * blend_factor)
                        ]
                    else:
                        blend_factor = (progress - 0.5) * 2
                        color = [
                            int(bg_color_middle[0] + (bg_color_bottom[0] - bg_color_middle[0]) * blend_factor),
                            int(bg_color_middle[1] + (bg_color_bottom[1] - bg_color_middle[1]) * blend_factor),
                            int(bg_color_middle[2] + (bg_color_bottom[2] - bg_color_middle[2]) * blend_factor)
                        ]
                    pygame.draw.line(gradient_surface, color, (0, y), (self.screen_size[0], y))
                self.graphics.cache_surface(gradient_cache_key, gradient_surface)
                
            self.screen.blit(gradient_surface, (0, 0))
                
            # Draw a large moon or sun in the background (with softer appearance)
            time_offset = pygame.time.get_ticks() / 6000.0  # Slower movement
            moon_x = self.screen_size[0] * (0.15 + 0.015 * math.sin(time_offset * 0.5))
            moon_y = self.screen_size[1] * (0.2 + 0.01 * math.cos(time_offset * 0.3))
            moon_radius = int(min(self.screen_size[0], self.screen_size[1]) * 0.08) # Slightly smaller
            
            use_moon = (pygame.time.get_ticks() / 25000) % 2 > 1 # Slower transition
            
            if use_moon:  # Draw moon
                moon_color = (220, 220, 230)  # Cooler white
                pygame.draw.circle(self.screen, moon_color, (int(moon_x), int(moon_y)), moon_radius)
                
                # Softer glow
                glow_surf = pygame.Surface((moon_radius * 5, moon_radius * 5), pygame.SRCALPHA)
                for r in range(int(moon_radius * 1.5), 0, -2):
                    alpha = 15 * ((moon_radius * 1.5 - r) / (moon_radius * 1.5))**2 # Softer falloff
                    pygame.draw.circle(glow_surf, (*moon_color, int(alpha)), 
                                    (moon_radius * 2.5, moon_radius * 2.5), r + moon_radius)
                self.screen.blit(glow_surf, 
                              (int(moon_x - moon_radius * 2.5), 
                               int(moon_y - moon_radius * 2.5)), 
                              special_flags=pygame.BLEND_RGBA_ADD)
                
                # Subtle Craters
                for _ in range(3):
                    crater_x = moon_x + random.uniform(-0.5, 0.5) * moon_radius
                    crater_y = moon_y + random.uniform(-0.5, 0.5) * moon_radius
                    crater_radius = moon_radius * random.uniform(0.08, 0.15)
                    crater_color = (190, 190, 200) # Dimmer crater color
                    pygame.draw.circle(self.screen, crater_color, (int(crater_x), int(crater_y)), int(crater_radius))
            else:  # Draw sun
                sun_color = (255, 235, 190)  # Softer warm yellow
                pygame.draw.circle(self.screen, sun_color, (int(moon_x), int(moon_y)), moon_radius)
                
                # Softer Sun glow
                glow_surf = pygame.Surface((moon_radius * 7, moon_radius * 7), pygame.SRCALPHA)
                for r in range(int(moon_radius * 2.5), 0, -3):
                    alpha = 10 * ((moon_radius * 2.5 - r) / (moon_radius * 2.5))**2 # Softer falloff
                    pygame.draw.circle(glow_surf, (255, 210, 140, int(alpha)), 
                                    (moon_radius * 3.5, moon_radius * 3.5), r + moon_radius)
                self.screen.blit(glow_surf, 
                              (int(moon_x - moon_radius * 3.5), 
                               int(moon_y - moon_radius * 3.5)), 
                              special_flags=pygame.BLEND_RGBA_ADD)
                
                # Softer Sun rays
                ray_count = 10 # More rays for softer look
                for i in range(ray_count):
                    angle = i * (2 * math.pi / ray_count) + time_offset * 0.8 # Slightly faster rotation
                    ray_length = moon_radius * 1.6
                    
                    # Draw ray as a soft, wide line
                    start_pos = (moon_x + math.cos(angle) * moon_radius * 0.8, 
                                 moon_y + math.sin(angle) * moon_radius * 0.8)
                    end_pos = (moon_x + math.cos(angle) * ray_length, 
                               moon_y + math.sin(angle) * ray_length)
                    
                    pygame.draw.line(self.screen, (255, 235, 190, 50), # Soft alpha
                                   start_pos, end_pos, int(moon_radius * 0.4)) # Wider ray
            
            # Enhanced Noise Texture (Subtler, more blended)
            noise_cache_key = f"noise_{self.screen_size[0]}x{self.screen_size[1]}"
            noise_surface = self.graphics.get_cached_surface(noise_cache_key)
            if not noise_surface or random.random() < 0.1: # Regenerate occasionally
                try:
                    noise_surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
                    noise_alpha = 8 # Even subtler
                    for _ in range(int(self.screen_size[0] * self.screen_size[1] * 0.001)): # Fewer, larger speckles
                        x = random.randint(0, self.screen_size[0]-1)
                        y = random.randint(0, self.screen_size[1]-1)
                        brightness = random.randint(50, 150) # Less extreme brightness
                        size = random.randint(1, 2) # Slightly larger speckles
                        color = (brightness, brightness, brightness, noise_alpha)
                        # Draw small rect for softer speckle
                        noise_surface.fill(color, (x, y, size, size))
                        
                    self.graphics.cache_surface(noise_cache_key, noise_surface)
                except Exception as e:
                    self.logger.error(f"Error drawing noise texture: {e}")
            
            if noise_surface:
                self.screen.blit(noise_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                
        else:
            # For other game states, use the standard dark background
            self.screen.fill((30, 30, 30))  # Dark background

        # Render based on game state
        if self.game_mode == GameState.MAIN_MENU:
            self.menu.draw(self.screen)
            self.logger.debug("Main menu drawn.")
        elif self.game_mode == GameState.OPTIONS:
            self.options_menu.draw(self.screen)
        elif self.game_mode == GameState.SINGLE_PLAYER or self.game_mode == GameState.LOCAL_COOP:
            self.graphics.render_all(self.screen)
            self._draw_world_time()
            self._draw_control_hints()
            
            # Draw Inventory UI on top of game world, if visible
            if self.inventory_ui and self.inventory_ui.visible:
                overlay = self.graphics.get_cached_surface('inventory_overlay')
                if overlay:
                    self.screen.blit(overlay, (0, 0))
                self.inventory_ui.draw(self.screen)
            
            # Draw Pause Menu last, on top of everything else (except particles)
            if self.pause_menu.is_visible:
                self.pause_menu.draw(self.screen)
                
        # Draw particles last (with error handling)
        if hasattr(self.graphics, 'particle_system') and not self.graphics.particle_system.disabled:
            try:
                self.graphics.particle_system.draw(self.screen)
            except Exception as e:
                self.logger.error(f"Error drawing particles: {e}", exc_info=True)
                self.graphics.particle_system.disabled = True # Disable particles on error
        
        # Update display (only ONCE per frame)
        try:
            pygame.display.flip()
        except Exception as e:
            self.logger.error(f"Error during display flip: {e}", exc_info=True)
            # If flip fails, we might need to quit
            pygame.quit()
        
        if self.game_mode == GameState.MAIN_MENU:
            self.logger.debug("Main menu draw end (after flip).")
    
    def run(self):
        try:
            while True:
                # Check for music end events first - handle these immediately
                # for seamless playback between tracks
                # Skip processing music end events when in the music player
                if hasattr(self, 'options_menu') and hasattr(self.options_menu, 'state') and self.options_menu.state == self.options_menu.state.__class__.MUSIC_PLAYER:
                    # Just clear the music end events without processing them
                    pygame.event.get([self.options.music_end_event])
                else:
                    music_events = pygame.event.get([self.options.music_end_event])
                    for event in music_events:
                        if event.type == self.options.music_end_event:
                            print(f"DEBUG: Music end event at {pygame.time.get_ticks()} ms")
                            self.options.handle_music_event(event)
                
                # Ensure the game loop continues even if there are non-fatal errors
                try:
                    # Store current game state
                    current_state = self.game_mode
                    
                    # Handle input first
                    self.handle_input()
                    
                    # Check if state changed
                    if current_state == GameState.OPTIONS and self.game_mode != GameState.OPTIONS:
                        self.logger.debug(f"State changed from OPTIONS to {self.game_mode}")
                        continue  # Skip update and draw for this frame to ensure clean transition
                    
                    # Then update game state
                    self.update()
                    # Finally, draw the current frame
                    self.draw()
                except Exception as e:
                    self.logger.error(f"Error in game loop iteration: {e}", exc_info=True)
                    # Attempt recovery or inform user
                    # For now, just log and continue; consider pausing or returning to menu
                    
                # Cap the framerate
                self.clock.tick(self.target_fps)
                
        except Exception as e:
            # Log fatal errors that escape the inner loop's catch
            self.logger.critical(f"FATAL ERROR in main game loop: {e}", exc_info=True)
            # Exception hook (handle_exception) should catch this if not handled here
            # Raising it ensures the exception hook gets called
            raise 
        finally:
            # Ensure pygame shuts down properly in MOST cases
            # If a fatal error occurred, the hook might handle quit/exit
            self.logger.info("Game loop finished or terminated. Attempting shutdown...")
            try:
                if pygame.get_init():
                    pygame.quit()
                    self.logger.info("Pygame shut down successfully.")
            except Exception as ex:
                self.logger.error(f"Error during pygame shutdown in finally block: {ex}")
            # Removed sys.exit(1) - Allow batch file to pause

    def __del__(self):
        """Cleanup when the game exits"""
        try:
            if hasattr(self, 'graphics'):
                self.graphics.cleanup()
            if hasattr(self, 'logger'):
                self.logger.info("Game object destroyed")
        except Exception:
            pass  # Don't crash during cleanup

    def save_current_game(self):
        """Save the current game state"""
        if not self.world or not self.players:
            print("Nothing to save!")
            return
            
        # Temporary notification
        print("Saving game...")
        
        # Create player data
        player_data = {}
        for i, player in enumerate(self.players):
            # Get player position, inventory, health, etc.
            player_data[f"player{i+1}"] = {
                "position": player.pos,
                "health": player.stats.hp,
                "inventory": player.inventory.to_dict(),
                "color": player.color,
                "controls": player.controls
            }
            
        # Create world data (using existing serialization)
        world_data = {
            "seed": self.world.seed,
            "loaded_chunks": {},
            "spawn_points": self.world.spawn_points
        }
        
        # Save loaded chunks
        for pos, chunk in self.world.loaded_chunks.items():
            world_data["loaded_chunks"][f"{pos[0]}_{pos[1]}"] = chunk.to_dict()
        
        # Build the complete game state
        game_state = {
            "player": player_data,
            "world": world_data,
            "game_mode": self.game_mode,
            "play_time": self.play_time,
        }
        
        # Create a default slot name based on date/time if none exists
        slot_name = self.save_manager.current_save_slot
        if not slot_name:
            slot_name = f"Save_{time.strftime('%Y%m%d_%H%M%S')}"
            
        # Save the game
        success = self.save_manager.save_game(slot_name, game_state)
        
        if success:
            print(f"Game saved successfully to slot: {slot_name}")
            self.options.play_sound('menu_click')
        else:
            print("Failed to save game!")
    
    def load_game(self):
        """Load a saved game"""
        # For now, we'll just load the most recent save
        # In the future, add a proper save selection UI
        
        slots = self.save_manager.get_save_slots()
        if not slots:
            print("No saved games found!")
            return
            
        # Use current slot if available, otherwise use most recent
        slot_name = self.save_manager.current_save_slot
        if not slot_name and slots:
            slot_name = slots[0]["name"]  # Most recent save
            
        if not slot_name:
            print("No save slot selected!")
            return
            
        try:
            # Load the game state
            print(f"Loading game from slot: {slot_name}")
            game_state = self.save_manager.load_game(slot_name)
            
            # Set the game mode
            self.game_mode = game_state.get("game_mode", GameState.SINGLE_PLAYER)
            
            # Set play time
            self.play_time = game_state.get("play_time", 0)
            
            # Load world
            world_data = game_state.get("world", {})
            self.world = World(seed=world_data.get("seed", 0))
            self.world.spawn_points = world_data.get("spawn_points", self.world.spawn_points)
            
            # Load chunks
            loaded_chunks = world_data.get("loaded_chunks", {})
            for pos_str, chunk_data in loaded_chunks.items():
                x, y = map(int, pos_str.split("_"))
                self.world.loaded_chunks[(x, y)] = self.world.generator.load_chunk_from_dict(chunk_data)
                # Generate tile variations for loaded chunks
                self.world._generate_tile_variations(self.world.loaded_chunks[(x, y)])
            
            # Initialize grass blades for the loaded world
            self.world.init_grass()
                
            # Create players
            player_data = game_state.get("player", {})
            self.players = []
            
            # Clear existing render layers
            for layer in RenderLayer:
                self.graphics.clear_layer(layer)
                
            # Load player 1 (always exists)
            if "player1" in player_data:
                p1_data = player_data["player1"]
                p1 = Player(
                    p1_data["position"][0], 
                    p1_data["position"][1],
                    p1_data["color"],
                    p1_data["controls"],
                    self.world
                )
                p1.stats.hp = p1_data["health"]
                p1.inventory.from_dict(p1_data["inventory"])
                self.players.append(p1)
                self.graphics.add_to_layer(RenderLayer.ENTITIES, p1)
                
            # Load player 2 (if exists)
            if "player2" in player_data and self.game_mode == GameState.LOCAL_COOP:
                p2_data = player_data["player2"]
                p2 = Player(
                    p2_data["position"][0], 
                    p2_data["position"][1],
                    p2_data["color"],
                    p2_data["controls"],
                    self.world
                )
                p2.stats.hp = p2_data["health"]
                p2.inventory.from_dict(p2_data["inventory"])
                self.players.append(p2)
                self.graphics.add_to_layer(RenderLayer.ENTITIES, p2)
                
            # Add world to render layers
            self.graphics.add_to_layer(RenderLayer.TERRAIN, self.world)
            
            # Initialize inventory UI for the first player
            if self.players:
                self.inventory_ui = InventoryUI(self.players[0].inventory, self.screen_size)
                
            # Initialize combat system
            self.combat = CombatSystem()
            
            # Close pause menu
            self.pause_menu.is_visible = False
            
            # Start game music using sectioned approach
            if pygame.mixer.get_init():
                self.options.queue_game_music()
                
            print("Game loaded successfully!")
            self.options.play_sound('menu_click')
            
        except SaveCorruptionError as e:
            print(f"Error loading save: {e}")
        except VersionMismatchError as e:
            print(f"Save version incompatible: {e}")
        except Exception as e:
            print(f"Failed to load game: {e}")

    def _draw_world_time(self):
        """Draw the world time at the top right of the screen"""
        if not self.world:
            return
            
        # Create background rectangle
        time_bg_rect = pygame.Rect(self.screen_size[0] - 140, 10, 130, 60)
        time_bg = pygame.Surface((time_bg_rect.width, time_bg_rect.height), pygame.SRCALPHA)
        time_bg.fill((0, 0, 0, 150))
        self.screen.blit(time_bg, time_bg_rect)
        
        # Format time string (24-hour format with leading zeros)
        time_str = f"{self.world.hours:02d}:{int(self.world.minutes):02d}"
        day_str = f"Day {self.world.days}"
        phase = self.world.get_day_phase()
        
        # Choose color based on day phase
        if phase == "day":
            time_color = (255, 215, 0)  # Golden
        elif phase == "night":
            time_color = (100, 149, 237)  # Cornflower blue
        else:  # dawn or dusk
            time_color = (255, 165, 0)  # Orange
        
        # Draw time with shadow effect
        font = pygame.font.Font(None, 28)
        # Manually calculate centered position
        time_text_pos = (self.screen_size[0] - 75, 15)
        self.graphics.draw_text(
            self.screen,
            time_str,
            font,
            time_color,
            time_text_pos,
            shadow=True
        )
        
        # Draw day with shadow effect
        day_font = pygame.font.Font(None, 22)
        # Manually calculate centered position
        day_text_pos = (self.screen_size[0] - 75, 35)
        self.graphics.draw_text(
            self.screen,
            day_str,
            day_font,
            (255, 255, 255),
            day_text_pos,
            shadow=True
        )
        
        # Draw phase name
        phase_font = pygame.font.Font(None, 20)
        phase_text_pos = (self.screen_size[0] - 75, 55)
        self.graphics.draw_text(
            self.screen,
            phase.capitalize(),
            phase_font,
            time_color,
            phase_text_pos,
            shadow=True
        )

    def _draw_control_hints(self):
        """Draw control hints on screen during gameplay."""
        if self.game_mode not in [GameState.SINGLE_PLAYER, GameState.LOCAL_COOP]:
            return
            
        # Only show hints if not in pause menu
        if self.pause_menu.is_visible:
            return
            
        # Get screen dimensions
        screen_w, screen_h = self.screen_size
        
        # Create font for hints
        hint_font = pygame.font.Font(None, 24)
        hint_color = (200, 200, 200)  # Light gray
        
        # Define hints
        hints = [
            "ESC: Pause Menu",
            "I: Inventory",
            "WASD: Move",
            "Space: Jump",
            "Left Click: Attack",
            "Right Click: Block"
        ]
        
        # Draw hints in bottom-left corner
        y_pos = screen_h - 30  # Start from bottom
        for hint in reversed(hints):
            text_surface = hint_font.render(hint, True, hint_color)
            text_rect = text_surface.get_rect()
            text_rect.bottomleft = (10, y_pos)  # 10 pixels from left edge
            self.screen.blit(text_surface, text_rect)
            y_pos -= 25  # Move up for next hint

    def create_game(self):
        """Create a new game world"""
        # Get keybinds from options system
        player_controls = {
            'up': self.options.get_keybind('player1', 'up'),
            'down': self.options.get_keybind('player1', 'down'),
            'left': self.options.get_keybind('player1', 'left'),
            'right': self.options.get_keybind('player1', 'right'),
            'attack': self.options.get_keybind('player1', 'attack'),
            'inventory': self.options.get_keybind('player1', 'inventory'),
            'run': self.options.get_keybind('player1', 'run')  # Added run keybind
        }
        
        # Clear any existing game objects
        for layer in RenderLayer:
            self.graphics.clear_layer(layer)
        
        # Create world
        self.world = World(seed=random.randint(0, 999999))
        self.graphics.add_to_layer(RenderLayer.TERRAIN, self.world)
        
        # Set particle system world bounds based on world size
        world_width = self.world.width * 32  # Convert tile coords to pixels
        world_height = self.world.height * 32
        self.graphics.particle_system.set_world_bounds(0, 0, world_width, world_height)
        
        # Initialize the day/night system with the graphics engine
        if hasattr(self.world, 'day_night_system'):
            self.world.day_night_system.initialize(self.screen_size)
            # Add celestial body to EFFECTS layer
            self.graphics.add_to_layer(RenderLayer.EFFECTS, 
                                     lambda surface: self.world.day_night_system.draw_celestial_body(surface))
            # Add shadows to SHADOWS layer
            self.graphics.add_to_layer(RenderLayer.SHADOWS, 
                                     lambda surface: self.world.day_night_system.draw_shadows(surface, self.graphics))
            
        # Create player in single player mode
        self.players = []
        p1 = Player(self.world.spawn_points[0][0] * 32, self.world.spawn_points[0][1] * 32, (255, 0, 0), player_controls, self.world)
        self.players.append(p1)
        self.graphics.add_to_layer(RenderLayer.ENTITIES, p1)
        
        # Create inventory UI for first player
        self.inventory_ui = InventoryUI(p1.inventory, self.screen_size)
        
        # Initialize combat system
        self.combat = CombatSystem()
        
        # Add test items to inventory
        test_item = Item("Health Potion", "Restores 50 HP", ItemType.CONSUMABLE)
        p1.add_item(test_item)
        
        sword = Item("Iron Sword", "+5 Attack", ItemType.WEAPON)
        sword.stats = {"attack": 5}
        p1.add_item(sword)
        
        # Start game music using sectioned approach
        if pygame.mixer.get_init():
            self.options.queue_game_music()

    def start_new_game(self, mode=GameState.SINGLE_PLAYER):
        """Start a new game with selected mode"""
        # Clear any particles from the main menu before starting game
        if hasattr(self.graphics, 'particle_system'):
            self.graphics.particle_system.particles.clear()
            # Temporarily disable particles during transition
            self.graphics.particle_system.disable()
            
        self.game_mode = mode
        self.play_time = 0
        
        # Create new game objects
        self.create_game()
        
        # Re-enable particles after game is initialized
        if hasattr(self.graphics, 'particle_system'):
            if self.options.video.get('particles_enabled', True):
                self.graphics.particle_system.enable()

    def apply_video_settings(self):
        """Apply video settings (fullscreen toggle, resolution) and resize UI"""
        self.logger.info("Applying video settings...")
        new_resolution = tuple(self.options.video['resolution'])
        fullscreen = self.options.video['fullscreen']
        vsync = self.options.video['vsync']
        particles_enabled = self.options.video['particles_enabled']
        self.logger.debug(f"Target state - Resolution: {new_resolution}, Fullscreen: {fullscreen}, VSync: {vsync}, Particles: {particles_enabled}")
        
        # Update particle system state
        if hasattr(self.graphics, 'particle_system'):
            if particles_enabled:
                self.graphics.particle_system.enable()
                self.logger.debug("Particle system enabled")
            else:
                self.graphics.particle_system.disable()
                self.logger.debug("Particle system disabled")
        
        # Center window position if switching TO windowed mode
        if not fullscreen:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "center"
            self.logger.debug("Set SDL_VIDEO_WINDOW_POS=center for windowed mode.")
        else:
            # Remove env var if going fullscreen (might not be necessary, but cleaner)
            if 'SDL_VIDEO_WINDOW_POS' in os.environ:
                del os.environ['SDL_VIDEO_WINDOW_POS']
                self.logger.debug("Removed SDL_VIDEO_WINDOW_POS for fullscreen mode.")

        # Use pygame constants directly - safer on all systems
        display_flags = 0
        if fullscreen:
            display_flags = pygame.FULLSCREEN  # Use pygame's constant
        if vsync:
            display_flags |= pygame.DOUBLEBUF  # Add DOUBLEBUF with OR operation
        
        # Debug the actual values we're using
        self.logger.debug(f"Using flags: {display_flags} (pygame.FULLSCREEN={pygame.FULLSCREEN}, pygame.DOUBLEBUF={pygame.DOUBLEBUF})")
        
        try:
            self.logger.info(f"Attempting pygame.display.set_mode({new_resolution}, flags={display_flags})")
            # Store the screen before changing it, in case we need to revert
            old_screen_size = self.screen.get_size()
            old_flags = self.screen.get_flags()
            
            self.screen = pygame.display.set_mode(new_resolution, display_flags)
            
            # Update screen_size again AFTER set_mode, as it might differ
            self.screen_size = self.screen.get_size()
            self.logger.info(f"Display mode set. Actual screen size: {self.screen_size}, Actual flags: {self.screen.get_flags()}")
            
            # Check if the actual state matches the intended state
            if fullscreen and not (self.screen.get_flags() & pygame.FULLSCREEN):
                 self.logger.warning("Requested fullscreen, but display is not fullscreen after set_mode.")
            elif not fullscreen and (self.screen.get_flags() & pygame.FULLSCREEN):
                 self.logger.warning("Requested windowed, but display is fullscreen after set_mode.")
            if new_resolution != self.screen_size:
                 self.logger.warning(f"Requested resolution {new_resolution}, but got {self.screen_size} after set_mode.")
            
            # Update graphics engine with new screen size
            if hasattr(self.graphics, 'update_screen_size'):
                self.graphics.update_screen_size(self.screen_size)
            if hasattr(self.graphics, 'particle_system'): # Update particle system bounds
                self.graphics.particle_system.set_screen_size(*self.screen_size)
            
            # Re-cache UI elements that depend on screen size (optional, depends on caching logic)
            # self._cache_ui_elements() # Need to ensure this handles new size
            
            # Update other UI systems with new screen size
            self.logger.debug("Resizing UI systems...")
            if self.menu and hasattr(self.menu, 'resize'): self.menu.resize(self.screen_size)
            if self.options_menu: self.options_menu.resize(self.screen_size)
            if self.pause_menu and hasattr(self.pause_menu, 'resize'): self.pause_menu.resize(self.screen_size)
            if self.inventory_ui and hasattr(self.inventory_ui, 'resize'): self.inventory_ui.resize(self.screen_size)
            self.logger.debug("UI systems resized.")

        except pygame.error as e:
            self.logger.error(f"Failed to apply video settings: {e}")
            # Optionally, revert settings or show an error message
            self.logger.info("Attempting to revert video settings...")
            # Revert internal state for consistency
            try:
                 # Re-apply old settings
                 self.screen = pygame.display.set_mode(old_screen_size, old_flags)
                 self.screen_size = self.screen.get_size()
                 # Re-set options to match the state we reverted to
                 self.options.video['resolution'] = list(self.screen_size)
                 self.options.video['fullscreen'] = bool(old_flags & pygame.FULLSCREEN)
                 self.logger.info(f"Reverted video settings to: {self.screen_size}, Fullscreen: {self.options.video['fullscreen']}")
                 # Need to resize UI back to old settings
                 self.logger.debug("Resizing UI systems back to previous state...")
                 if self.menu and hasattr(self.menu, 'resize'): self.menu.resize(self.screen_size)
                 if self.options_menu: self.options_menu.resize(self.screen_size)
                 if self.pause_menu and hasattr(self.pause_menu, 'resize'): self.pause_menu.resize(self.screen_size)
                 if self.inventory_ui and hasattr(self.inventory_ui, 'resize'): self.inventory_ui.resize(self.screen_size)
                 self.logger.debug("UI systems resized back.")
            except Exception as revert_err:
                 self.logger.error(f"Failed to revert video settings after error: {revert_err}")

if __name__ == "__main__":
    game = Game()
    game.run() 