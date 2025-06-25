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
from scenes.main_menu import MainMenu

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

def setup_audio():
    """Initialize audio system with error handling."""
    try:
        pygame.mixer.init()
        
        # Set up the music end event
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        
        # Create assets/audio directory if it doesn't exist
        audio_dir = Path("assets/audio")
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Define required sound files
        required_sounds = {
            'menu_click': 'menu_click.wav',
            'menu_select': 'menu_select.wav',
            'attack': 'attack.wav'
        }
        
        # Load sounds with error handling
        sounds = {}
        for name, filename in required_sounds.items():
            try:
                sound_path = audio_dir / filename
                if sound_path.exists():
                    sounds[name] = pygame.mixer.Sound(str(sound_path))
                    logging.info(f"Loaded sound: {sound_path}")
                else:
                    logging.warning(f"Could not load sound: {sound_path} - File not found")
            except Exception as e:
                logging.warning(f"Error loading sound {filename}: {e}")
        
        return sounds
    except Exception as e:
        logging.error(f"Error initializing audio system: {e}")
        return {}

class Game:
    def __init__(self):
        try:
            # Initialize Pygame FIRST
            pygame.init()
            
            # Set up logging immediately after pygame init
            self.logger = setup_logging()
            self.logger.info("Pygame initialized, setting up logger.")
            
            # Initialize audio system
            self.sounds = setup_audio()
            
            # Initialize Options System (needed for settings)
            self.options_system = OptionsSystem()
            
            # Get screen size from options
            screen_size = self.options_system.get_screen_size()
            
            # Initialize Graphics Engine
            self.graphics = SynapstexGraphics(
                screen_size=screen_size,
                target_fps=60, # Could be sourced from options later
                fullscreen=self.options_system.get_fullscreen(),
                vsync=self.options_system.get_vsync()
            )
            
            # Set options system on graphics for access by other components
            self.graphics.options_system = self.options_system
            
            # Set up video change callback to handle resolution and fullscreen changes
            self.options_system.set_video_change_callback(self._handle_video_change)
            
            # Initialize display (using the screen surface from graphics engine)
            self.screen = self.graphics._update_display() # Get screen from graphics
            pygame.display.set_caption("Runic Lands")
            
            # Initialize clock
            self.clock = pygame.time.Clock()
            
            # Initialize game state
            self.current_state = "main_menu"
            self.main_menu = MainMenu(self.graphics)
            
            # Initialize menu music
            self.main_menu.start_menu_music()
            
            # Initialize other systems
            self.world = None
            self.combat_system = None
            self.players = []
            self.pause_menu = None
            self.inventory_ui = None
            self.options_menu = None  # Add options menu instance
            self.previous_state = None  # Track previous state for options menu
            
            self.logger.info("Game initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error during game initialization: {e}")
            raise

    def handle_input(self):
        """Handle all input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            # Handle music end event to queue the next section
            if event.type == pygame.USEREVENT + 1:
                # This is a music end event, let the options system handle it
                self.options_system.handle_music_event(event)
            
            if self.current_state == "main_menu":
                action = self.main_menu.handle_event(event)
                if action == "play":
                    self.start_new_game(GameState.SINGLE_PLAYER)
                elif action == "options":
                    self.previous_state = self.current_state
                    self.current_state = "options"
                    # Initialize options menu when entering options from main menu
                    self.options_menu = OptionsMenu(self.screen.get_size(), self.options_system)
                elif action == "quit":
                    return False
            elif self.current_state == "game":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Unpack screen size tuple to width and height
                        screen_width, screen_height = self.screen.get_size()
                        # Initialize pause menu if it doesn't exist
                        if self.pause_menu is None:
                            self.pause_menu = PauseMenu(screen_width, screen_height)
                        # Toggle visibility and switch to pause state
                        self.pause_menu.toggle()
                        self.current_state = "pause"
                    elif event.key == self.options_system.get_keybind('player1', 'inventory'):
                        if self.inventory_ui is None and self.players:
                            self.inventory_ui = InventoryUI(self.players[0].inventory, self.screen.get_size())
                        else:
                            self.inventory_ui = None
            elif self.current_state == "pause":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Return to the game
                        self.current_state = "game"
                        # Hide the pause menu
                        if self.pause_menu:
                            self.pause_menu.toggle()  # Toggle visibility off
                    elif event.key == pygame.K_RETURN:
                        # Pass the event to the pause menu for handling
                        action = self.pause_menu.handle_input(event)
                        if action == "resume":
                            self.current_state = "game"
                            # Hide the pause menu
                            if self.pause_menu:
                                self.pause_menu.toggle()  # Toggle visibility off
                        elif action == "options":
                            self.previous_state = self.current_state
                            self.current_state = "options"
                            # Initialize options menu when entering from pause menu
                            self.options_menu = OptionsMenu(self.screen.get_size(), self.options_system)
                        elif action == "quit":
                            self.return_to_menu()
                # Also handle mouse events for the pause menu
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    # Pass mouse events to the pause menu
                    action = self.pause_menu.handle_input(event)
                    if action == "resume":
                        self.current_state = "game"
                        # Hide the pause menu
                        if self.pause_menu:
                            self.pause_menu.toggle()  # Toggle visibility off
                    elif action == "options":
                        self.previous_state = self.current_state
                        self.current_state = "options"
                        # Initialize options menu when entering from pause menu
                        self.options_menu = OptionsMenu(self.screen.get_size(), self.options_system)
                    elif action == "quit":
                        self.return_to_menu()
            elif self.current_state == "options":
                # Initialize options menu if it doesn't exist
                if self.options_menu is None:
                    self.options_menu = OptionsMenu(self.screen.get_size(), self.options_system)
                
                # Handle options menu input
                result = self.options_menu.handle_input([event])
                if result == 'exit_options':
                    # Return to previous state (main_menu, pause, etc.)
                    self.current_state = self.previous_state if self.previous_state else "main_menu"
                    self.previous_state = None
                    self.options_menu = None  # Clean up options menu
        return True

    def update(self):
        """Update game state."""
        dt = self.clock.tick(60) / 1000.0  # Convert to seconds
        
        if self.current_state == "main_menu":
            self.main_menu.update(dt)
        elif self.current_state == "game":
            # Get keyboard state for player movement
            keys = pygame.key.get_pressed()
            
            # Update player movement based on keyboard input
            if self.players:
                self.players[0].move(keys)
            
            # Update world and entities
            if self.world:
                self.world.update(dt, self.graphics)
                # Update chunks around player position
                if self.players:
                    player = self.players[0]
                    self.world.update_chunks(int(player.pos[0]), int(player.pos[1]))
                    
            if self.combat_system:
                self.combat_system.update(dt, self.players)
            for player in self.players:
                player.update(dt)
            
            # Center camera on player - convert player position to pixel coordinates
            if self.players and self.graphics:
                player = self.players[0]
                # Convert player position to pixel coordinates and center camera
                self.graphics.set_camera_target(
                    player.pos[0],  # Player positions are already in pixels
                    player.pos[1]
                )
                
                # Load initial chunks around player to ensure terrain is visible
                self.world.update_chunks(int(player.pos[0]), int(player.pos[1]))
                
                # Update UI elements position relative to camera
                screen_width, screen_height = self.screen.get_size()
                if hasattr(player, 'name_text'):
                    # Position name above player
                    name_x = screen_width // 2
                    name_y = (screen_height // 2) - 30
                    player.name_text_rect.center = (name_x, name_y)
            
        elif self.current_state == "pause":
            pass
        elif self.current_state == "options":
            # Update options menu if it exists
            if self.options_menu:
                # Options menu doesn't need regular updates, just handle input
                pass

    def draw(self):
        """Draw the current game state."""
        if self.current_state == "main_menu":
            self.main_menu.draw(self.screen)
        elif self.current_state == "game":
            self.screen.fill((0, 0, 0))
            
            # Use the graphics engine's proper rendering system
            if self.graphics:
                self.graphics.render_all(self.screen)
            
            # Draw UI elements that need to be on top
            if self.players:
                player = self.players[0]
                # Draw player name and level (UI overlay)
                font = pygame.font.Font(None, 24)
                name_text = font.render(f"{player.name} Lv.{player.level}", True, (255, 255, 255))
                name_rect = name_text.get_rect(center=(self.screen.get_size()[0] // 2, 30))
                self.screen.blit(name_text, name_rect)
            
            # Draw inventory if open
            if self.inventory_ui:
                self.inventory_ui.draw(self.screen)
            
            # Draw control hints and world time
            self._draw_control_hints()
            self._draw_world_time()
            
        elif self.current_state == "pause":
            # First, use graphics engine to draw the game world underneath
            self.screen.fill((0, 0, 0))
            if self.graphics:
                self.graphics.render_all(self.screen)
            
            # Then draw the pause menu on top
            if self.pause_menu and hasattr(self.pause_menu, 'is_visible') and self.pause_menu.is_visible:
                self.pause_menu.draw(self.screen)
        elif self.current_state == "options":
            # Draw options menu
            if self.options_menu:
                self.options_menu.draw(self.screen)
            
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            
        pygame.quit()

    def return_to_menu(self):
        """Return to the main menu from game state."""
        try:
            self.current_state = "main_menu"
            
            # Stop any game music and start menu music
            self.options_system.stop_music()
            self.main_menu.start_menu_music()
            
            # Clean up game state
            self.world = None
            self.combat_system = None
            self.players = []
            self.pause_menu = None
            self.inventory_ui = None
            
            # Clear any render layers that might be active
            if self.graphics:
                self.graphics.clear_render_layers()
            
            self.logger.info("Returned to main menu")
            
        except Exception as e:
            self.logger.error(f"Error returning to menu: {e}")

    def start_new_game(self, mode=GameState.SINGLE_PLAYER):
        """Start a new game."""
        self.current_state = "game"
        if mode == GameState.SINGLE_PLAYER:
            self.init_single_player()
        else:
            self.init_local_coop()

    def init_single_player(self):
        self.logger.info("Initializing single-player mode...")
        try:
            # Clear existing render layers
            self.logger.debug("Clearing render layers...")
            for layer in RenderLayer:
                self.graphics.clear_layer(layer)
            self.logger.debug("Render layers cleared.")
            
            # Clear menu particles to prevent bleeding into game
            if hasattr(self.graphics, 'particle_system'):
                self.graphics.particle_system.particles.clear()
                self.logger.debug("Menu particles cleared.")
                
            # Create a new world or load existing if needed
            self.logger.debug("Creating world...")
            self.world = World(seed=random.randint(0, 999999))
            self.world.graphics = self.graphics
            self.logger.debug(f"World created with seed: {self.world.seed}")
            self.combat_system = CombatSystem()
            self.logger.debug("Combat system initialized.")
            
            # Get the spawn point closest to the center for single player
            spawn = self.world.get_centered_spawn()
            self.logger.debug(f"Using centered spawn point: {spawn}")
            
            # Spawn coordinates are already in pixels, no conversion needed
            spawn_x = spawn[0]
            spawn_y = spawn[1]
            
            controls = {
                'up': self.options_system.get_keybind('player1', 'up'),
                'down': self.options_system.get_keybind('player1', 'down'),
                'left': self.options_system.get_keybind('player1', 'left'),
                'right': self.options_system.get_keybind('player1', 'right'),
                'attack': self.options_system.get_keybind('player1', 'attack'),
                'inventory': self.options_system.get_keybind('player1', 'inventory'),
                'run': self.options_system.get_keybind('player1', 'run')
            }
            self.logger.debug("Player controls retrieved.")
            
            # Create player with pixel coordinates
            self.players = [Player(spawn_x, spawn_y, (255, 0, 0), controls, self.world)]
            self.logger.debug("Player entity created.")
            self.current_state = "game"
            
            # Remove automatic inventory UI initialization
            self.inventory_ui = None
            self.logger.debug("Game state initialized.")
            
            # Add world and player to render layers
            self.graphics.add_to_layer(RenderLayer.TERRAIN, self.world)
            self.graphics.add_to_layer(RenderLayer.ENTITIES, self.players[0])
            self.logger.debug("World and player added to render layers.")
            
            # Initialize camera position on player
            if self.players and self.graphics:
                player = self.players[0]
                self.graphics.set_camera_target(
                    player.pos[0],  # Player positions are in pixels
                    player.pos[1]
                )
                
                # Load initial chunks around player to ensure terrain is visible
                self.world.update_chunks(int(player.pos[0]), int(player.pos[1]))
            
            # Set up particle system for game world
            if hasattr(self.graphics, 'particle_system'):
                world_width = self.world.width * 32
                world_height = self.world.height * 32
                self.graphics.particle_system.set_world_bounds(0, 0, world_width, world_height)
                self.logger.debug(f"Particle system bounds set to {world_width}x{world_height}")
            
            # Switch to game music using the new section-based approach
            if pygame.mixer.get_init():
                self.options_system.queue_game_music()
            
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
        self.world.graphics = self.graphics
        self.combat_system = CombatSystem()
        spawn1, spawn2 = self.world.spawn_points
        
        p1_controls = {
            'up': self.options_system.get_keybind('player1', 'up'),
            'down': self.options_system.get_keybind('player1', 'down'),
            'left': self.options_system.get_keybind('player1', 'left'),
            'right': self.options_system.get_keybind('player1', 'right'),
            'attack': self.options_system.get_keybind('player1', 'attack'),
            'inventory': self.options_system.get_keybind('player1', 'inventory'),
            'run': self.options_system.get_keybind('player1', 'run')  # Added run keybind
        }
        p2_controls = {
            'up': self.options_system.get_keybind('player2', 'up'),
            'down': self.options_system.get_keybind('player2', 'down'),
            'left': self.options_system.get_keybind('player2', 'left'),
            'right': self.options_system.get_keybind('player2', 'right'),
            'attack': self.options_system.get_keybind('player2', 'attack'),
            'inventory': self.options_system.get_keybind('player2', 'inventory'),
            'run': self.options_system.get_keybind('player2', 'run')  # Added run keybind
        }
        
        self.players = [
            Player(*spawn1, (255, 0, 0), p1_controls, self.world),
            Player(*spawn2, (0, 0, 255), p2_controls, self.world)
        ]
        self.current_state = "game"
        
        # Remove automatic inventory UI initialization
        self.inventory_ui = None
        
        # Add world and players to render layers
        self.graphics.add_to_layer(RenderLayer.TERRAIN, self.world)
        for player in self.players:
            self.graphics.add_to_layer(RenderLayer.ENTITIES, player)
        
        # Switch to game music using the new section-based approach
        if pygame.mixer.get_init():
            self.options_system.queue_game_music()
    
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
            "game_mode": self.current_state,
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
            self.options_system.play_sound('menu_click')
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
            self.current_state = game_state.get("game_mode", GameState.SINGLE_PLAYER)
            
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
            if "player2" in player_data and self.current_state == GameState.LOCAL_COOP:
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
                self.inventory_ui = InventoryUI(self.players[0].inventory, self.screen.get_size())
                
            # Initialize combat system
            self.combat_system = CombatSystem()
            
            # Close pause menu
            self.pause_menu = None
            
            # Start game music using sectioned approach
            if pygame.mixer.get_init():
                self.options_system.queue_game_music()
                
            print("Game loaded successfully!")
            self.options_system.play_sound('menu_click')
            
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
        time_bg_rect = pygame.Rect(self.screen.get_size()[0] - 140, 10, 130, 60)
        time_bg = pygame.Surface((time_bg_rect.width, time_bg_rect.height), pygame.SRCALPHA)
        time_bg.fill((0, 0, 0, 150))
        pygame.draw.rect(self.screen, (0, 0, 0, 150), time_bg_rect)
        
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
        time_text_pos = (self.screen.get_size()[0] - 75, 15)
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
        day_text_pos = (self.screen.get_size()[0] - 75, 35)
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
        phase_text_pos = (self.screen.get_size()[0] - 75, 55)
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
        if self.current_state not in [GameState.SINGLE_PLAYER, GameState.LOCAL_COOP]:
            return
            
        # Only show hints if not in pause menu
        if self.pause_menu:
            return
            
        # Get screen dimensions
        screen_w, screen_h = self.screen.get_size()
        
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
            'up': self.options_system.get_keybind('player1', 'up'),
            'down': self.options_system.get_keybind('player1', 'down'),
            'left': self.options_system.get_keybind('player1', 'left'),
            'right': self.options_system.get_keybind('player1', 'right'),
            'attack': self.options_system.get_keybind('player1', 'attack'),
            'inventory': self.options_system.get_keybind('player1', 'inventory'),
            'run': self.options_system.get_keybind('player1', 'run')  # Added run keybind
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
            self.world.day_night_system.initialize(self.screen.get_size())
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
        self.inventory_ui = InventoryUI(p1.inventory, self.screen.get_size())
        
        # Initialize combat system
        self.combat_system = CombatSystem()
        
        # Add test items to inventory
        test_item = Item("Health Potion", "Restores 50 HP", ItemType.CONSUMABLE)
        p1.add_item(test_item)
        
        sword = Item("Iron Sword", "+5 Attack", ItemType.WEAPON)
        sword.stats = {"attack": 5}
        p1.add_item(sword)
        
        # Start game music using sectioned approach
        if pygame.mixer.get_init():
            self.options_system.queue_game_music()

    def _handle_video_change(self):
        """Handle video setting changes like resolution and fullscreen"""
        try:
            # Get current video settings from options
            if hasattr(self.options_system, 'video'):
                new_resolution = self.options_system.video.get('resolution', (800, 600))
                new_fullscreen = self.options_system.video.get('fullscreen', False)
                new_vsync = self.options_system.video.get('vsync', True)
            else:
                # Fallback to old system
                new_resolution = self.options_system.get_screen_size()
                new_fullscreen = self.options_system.get_fullscreen()
                new_vsync = self.options_system.get_vsync()
            
            # Update graphics engine with new settings
            if self.graphics:
                # Use the correct method names from SynapstexGraphics
                self.graphics.set_screen_resolution(new_resolution[0], new_resolution[1])
                self.graphics.set_fullscreen(new_fullscreen)
                self.graphics.set_vsync(new_vsync)
                
                # Update the screen reference
                self.screen = self.graphics._update_display()
                
                # If options menu is open, recreate it with new screen size
                if self.current_state == "options" and self.options_menu:
                    self.options_menu = OptionsMenu(self.screen.get_size(), self.options_system)
                
                self.logger.info(f"Video settings updated: {new_resolution}, fullscreen={new_fullscreen}, vsync={new_vsync}")
                
        except Exception as e:
            self.logger.error(f"Error handling video change: {e}")

if __name__ == "__main__":
    game = Game()
    game.run() 