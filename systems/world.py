import pygame
import json
import random
import math
import os
from typing import List, Tuple, Dict, Optional
from .synapstex import ParticleType, RenderLayer, BlendMode
from .world_generator import SynapstexWorldGenerator, WorldChunk, TerrainType
import logging
from enum import Enum, auto

logger = logging.getLogger(__name__)

class TerrainType(Enum):
    GRASS = "grass"
    STONE = "stone"
    WATER = "water"
    LAVA = "lava"
    DIRT = "dirt"
    SAND = "sand"
    SNOW = "snow"

class GrassBlade:
    def __init__(self, x: int, y: int, height: int = 10):
        self.x = x
        self.y = y
        self.height = height
        self.base_angle = random.uniform(-10, 10)  # Slight natural bend
        self.current_angle = self.base_angle
        self.sway_offset = random.uniform(0, 2 * math.pi)  # Start sway at random phase
        self.sway_speed = random.uniform(1.5, 3.0) # Randomize sway speed
        self.color = (
            random.randint(30, 50), 
            random.randint(130, 170), 
            random.randint(30, 50)
        ) # Slightly varied green

    def update(self, dt: float, wind_strength: float, wind_time: float):
        # Calculate wind effect based on time and blade position
        wind_angle = (math.sin(wind_time + self.x * 0.01) * wind_strength) + \
                     (math.sin(wind_time * 0.7 + self.y * 0.01) * wind_strength * 0.5)
        
        # Add gentle sway
        self.sway_offset += self.sway_speed * dt
        sway_angle = math.sin(self.sway_offset) * 5 # Small sway range
        
        self.current_angle = self.base_angle + wind_angle + sway_angle

    def draw(self, surface: pygame.Surface, offset: Tuple[float, float]):
        # Apply camera offset
        screen_x = self.x - offset[0]
        screen_y = self.y - offset[1]
        
        # Skip drawing if off-screen
        if screen_x < -10 or screen_x > surface.get_width() + 10 or \
           screen_y < -self.height or screen_y > surface.get_height() + 10:
            return
            
        # Calculate tip position based on angle
        rad_angle = math.radians(90 + self.current_angle) # 90 degrees = straight up
        tip_x = screen_x + math.cos(rad_angle) * self.height
        tip_y = screen_y - math.sin(rad_angle) * self.height
        
        # Draw blade as a slightly curved line (using multiple segments)
        num_segments = 3
        points = []
        base_pos = (screen_x, screen_y)
        points.append(base_pos)
        
        # Calculate control point for curve (subtly bends against the lean)
        control_angle = math.radians(90 + self.current_angle * 0.5) # Less angle for control point
        control_height = self.height * 0.6
        cx = screen_x + math.cos(control_angle) * control_height
        cy = screen_y - math.sin(control_angle) * control_height
        
        tip_pos = (tip_x, tip_y)
        
        # Interpolate points along a Bezier curve (simple approximation)
        for i in range(1, num_segments + 1):
            t = i / num_segments
            inv_t = 1 - t
            
            # Quadratic Bezier formula: P = (1-t)^2*P0 + 2*(1-t)*t*P1 + t^2*P2
            px = (inv_t**2 * base_pos[0]) + (2 * inv_t * t * cx) + (t**2 * tip_pos[0])
            py = (inv_t**2 * base_pos[1]) + (2 * inv_t * t * cy) + (t**2 * tip_pos[1])
            points.append((int(px), int(py)))
            
        # Draw the polyline with antialiasing if possible
        if len(points) > 1:
            pygame.draw.aalines(surface, self.color, False, points)

# Add DayNightSystem class to handle day/night cycle
class DayNightSystem:
    """
    System for managing day/night cycle, lighting, and celestial bodies.
    Designed to integrate with the Synapstex graphics engine.
    """
    def __init__(self, world):
        self.world = world
        self.sun_surface = None
        self.moon_surface = None
        self.shadow_surface = None
        self.overlay_surface = None
        self.initialized = False
        
    def initialize(self, screen_size):
        """Initialize surfaces with the given screen size"""
        self.initialized = True
        self.screen_size = screen_size
        
        # Pre-render sun and moon
        self._create_celestial_surfaces()
        
        # Create empty shadow surface
        self.shadow_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
        
        # Create overlay surface
        self.overlay_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
    
    def _create_celestial_surfaces(self):
        """Pre-render sun and moon surfaces for better performance"""
        # Sun surface with rays
        size = 50
        self.sun_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        
        # Draw sun glow
        pygame.draw.circle(self.sun_surface, (255, 255, 200, 100), (size, size), 25)
        
        # Draw sun rays
        for i in range(8):
            ray_angle = i * math.pi / 4
            ray_x = size + math.cos(ray_angle) * 38
            ray_y = size + math.sin(ray_angle) * 38
            pygame.draw.line(self.sun_surface, (255, 255, 200, 100), (size, size), (ray_x, ray_y), 3)
        
        # Draw sun body
        pygame.draw.circle(self.sun_surface, (255, 255, 0), (size, size), 15)
        
        # Moon surface with craters
        self.moon_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        
        # Draw moon glow
        pygame.draw.circle(self.moon_surface, (200, 200, 255, 80), (size, size), 18)
        
        # Draw moon body
        pygame.draw.circle(self.moon_surface, (220, 220, 255), (size, size), 13)
        
        # Draw moon crater details (pre-defined for consistency)
        crater_positions = [
            (size-5, size-3, 4),
            (size+7, size+2, 3),
            (size-2, size+8, 2)
        ]
        
        for crater_x, crater_y, crater_size in crater_positions:
            pygame.draw.circle(self.moon_surface, (200, 200, 235), (crater_x, crater_y), crater_size)
    
    def update(self, dt):
        """Update day/night cycle state"""
        pass  # Nothing to update directly - world time is updated in World.update()
    
    def get_overlay_for_time(self, graphics):
        """Generate lighting overlay for current time"""
        if not self.initialized:
            return None
            
        # Get lighting parameters
        ambient_light = self.world._calculate_ambient_light()
        phase = self.world.get_day_phase()
        
        # Skip in full daylight
        if ambient_light >= 0.99:
            return None
            
        # Clear overlay
        self.overlay_surface.fill((0, 0, 0, 0))
        
        # Calculate overlay alpha based on time of day
        alpha = int(255 * (1.0 - ambient_light) * 0.7)  # Cap at 70% darkness
        
        # Choose color based on phase
        if phase == "night":
            # Deep blue for night
            overlay_color = (20, 20, 60, alpha)
        elif phase == "dawn":
            # Orange-ish for dawn
            overlay_color = (70, 40, 20, alpha)
        elif phase == "dusk":
            # Red-orange for dusk
            overlay_color = (70, 30, 20, alpha)
        else:
            # Slight darkening for cloudy day, etc.
            overlay_color = (20, 20, 40, alpha)
            
        self.overlay_surface.fill(overlay_color)
        return self.overlay_surface
    
    def get_celestial_body_position(self, screen_width, screen_height):
        """Calculate the position of the sun/moon based on time of day"""
        # Calculate position based on day_progress (0.0 to 1.0)
        angle = self.world.day_progress * math.pi * 2 - math.pi/2
        radius = screen_height * 0.9
        
        # Calculate x, y position on the arc
        x = screen_width * 0.5 + math.cos(angle) * radius
        y = screen_height * 0.9 + math.sin(angle) * radius
        
        # Determine if it's visible (above horizon)
        visible = y < screen_height
        
        return (x, y, visible)
    
    def draw_celestial_body(self, surface):
        """Draw the sun or moon based on time of day"""
        if not self.initialized:
            return
            
        screen_width, screen_height = self.screen_size
        x, y, visible = self.get_celestial_body_position(screen_width, screen_height)
        
        if not visible:
            return
            
        # Determine which celestial body to draw
        phase = self.world.get_day_phase()
        if phase in ["dawn", "day", "dusk"]:
            # Draw sun with appropriate color tint based on time
            if phase == "dawn":
                # Orange-ish tint for dawn
                tinted_sun = self.sun_surface.copy()
                pygame.draw.circle(tinted_sun, (255, 200, 100), (25, 25), 15)
                surface.blit(tinted_sun, (int(x-25), int(y-25)))
            elif phase == "dusk":
                # Red-orange tint for dusk
                tinted_sun = self.sun_surface.copy()
                pygame.draw.circle(tinted_sun, (255, 150, 50), (25, 25), 15)
                surface.blit(tinted_sun, (int(x-25), int(y-25)))
            else:
                # Normal sun
                surface.blit(self.sun_surface, (int(x-25), int(y-25)))
        else:
            # Draw moon
            surface.blit(self.moon_surface, (int(x-25), int(y-25)))
    
    def draw_shadows(self, surface, graphics):
        """Draw shadows for objects based on sun/moon position"""
        if not self.initialized:
            return
            
        # Get light source position
        screen_width, screen_height = self.screen_size
        light_x, light_y, visible = self.get_celestial_body_position(screen_width, screen_height)
        
        if not visible:
            return
        
        # Only process structures that can cast shadows
        phase = self.world.get_day_phase()
        
        # Skip shadows at night
        if phase == "night":
            return
            
        # Clear shadow surface
        self.shadow_surface.fill((0, 0, 0, 0))
            
        # Define shadow parameters
        shadow_length = 30
        shadow_alpha = 100
        
        # Shadows are more pronounced during dawn/dusk
        if phase == "dawn" or phase == "dusk":
            shadow_length = 50
            shadow_alpha = 150
            
        # Shadows are shorter near noon
        if phase == "day" and abs(self.world.hours - 12) < 2:
            shadow_length = 15
            
        # Draw shadows for all structures
        self.world._draw_structure_shadows(self.shadow_surface, light_x, light_y, shadow_length, shadow_alpha)
        
        # Add shadow surface to screen
        surface.blit(self.shadow_surface, (0, 0))

class World:
    def __init__(self, map_file=None, seed: int = None):
        # Initialize pygame if not already done
        if not pygame.get_init():
            pygame.init()
            
        self.tile_size = 32  # Size of each tile in pixels
        self.chunk_size = 16  # Size of each chunk in tiles
        self.width = 64  # World width in tiles
        self.height = 64  # World height in tiles
        self.view_distance = 2  # Number of chunks to load around player
        
        # Initialize collision system
        self.collision_rects = []  # List to store collision rectangles
        
        # Convert dimensions to pixels for bounds checking
        self.pixel_width = self.width * self.tile_size
        self.pixel_height = self.height * self.tile_size
        
        # Initialize world generation
        self.seed = seed if seed is not None else random.randint(0, 999999)
        random.seed(self.seed)
        self.generator = SynapstexWorldGenerator(self.seed)
        
        # Initialize chunk storage
        self.loaded_chunks = {}
        
        # Initialize spawn points
        self.spawn_points = self._generate_spawn_points()
        
        # Initialize grass system
        self.grass_blades = []
        self.max_grass_blades = 1000
        self.wind_time = 0
        self.wind_strength = 0.5
        
        # World time system
        self.minutes = 0
        self.hours = 8  # Start at 8 AM
        self.days = 1
        self.minutes_per_second = 1  # Game time passes at 1 minute per real second
        
        # Create day/night system
        self.day_night_system = DayNightSystem(self)
        
        # Load map if specified
        if map_file and os.path.exists(map_file):
            self.load_map(map_file)
        else:
            # Get the center chunk coordinates
            center_chunk_x = self.width // (2 * self.chunk_size)
            center_chunk_y = self.height // (2 * self.chunk_size)
            self._load_chunks_around(center_chunk_x, center_chunk_y)
            self.init_grass() # Initialize grass after loading initial chunks
        
    def get_centered_spawn(self) -> Tuple[int, int]:
        """Return the spawn point closest to the world center."""
        if not self.spawn_points:
            return (0, 0) # Default if none exist
        
        # Assume center is near (0,0) world coordinates
        # Calculate distances from (0,0) for each spawn point
        distances = [math.sqrt(sp[0]**2 + sp[1]**2) for sp in self.spawn_points]
        
        # Find the index of the spawn point with the minimum distance
        min_index = distances.index(min(distances))
        
        return self.spawn_points[min_index]
            
    def _generate_spawn_points(self, num_points: int = 4) -> List[Tuple[int, int]]:
        """Generate potential spawn points, ensuring one is near the center."""
        spawn_points = []
        chunk_size_pixels = self.chunk_size * 32 # Approx tile size

        # 1. Ensure a spawn point near the center chunk (0,0)
        center_chunk = self.generator.get_chunk(0, 0)
        found_center = False
        for _ in range(50): # Try 50 times to find a suitable spot in center chunk
            x = random.randint(0, center_chunk.size - 1)
            y = random.randint(0, center_chunk.size - 1)
            tile_index = y * center_chunk.size + x
            if tile_index < len(center_chunk.tiles) and center_chunk.tiles[tile_index]["type"] == TerrainType.GRASS.value:
                spawn_points.append((x * 32 + 16, y * 32 + 16)) # Center of the tile
                found_center = True
                break
        if not found_center:
             spawn_points.append((16, 16)) # Fallback absolute center coord

        # 2. Generate other spawn points in nearby chunks
        tries = 0
        while len(spawn_points) < num_points and tries < 100:
            tries += 1
            # Choose a nearby chunk relative to center
            chunk_x = random.randint(-2, 2)
            chunk_y = random.randint(-2, 2)
            if chunk_x == 0 and chunk_y == 0: continue # Skip center chunk
            
            chunk = self.generator.get_chunk(chunk_x, chunk_y)
            
            # Find a random grass tile in this chunk
            potential_spots = []
            for i, tile in enumerate(chunk.tiles):
                 if tile["type"] == TerrainType.GRASS.value:
                     tile_x = i % chunk.size
                     tile_y = i // chunk.size
                     potential_spots.append((tile_x, tile_y))
            
            if potential_spots:
                 spot = random.choice(potential_spots)
                 world_x = (chunk_x * chunk.size + spot[0]) * 32 + 16
                 world_y = (chunk_y * chunk.size + spot[1]) * 32 + 16
                 
                 # Check distance from existing points
                 too_close = False
                 for sp in spawn_points:
                      dist = math.sqrt((world_x - sp[0])**2 + (world_y - sp[1])**2)
                      if dist < chunk_size_pixels * 1.5: # Ensure reasonable distance
                           too_close = True
                           break
                 
                 if not too_close:
                      spawn_points.append((world_x, world_y))
                      
        return spawn_points
    
    def _generate_tile_variations(self, chunk: WorldChunk):
        """Generate static texture variations for tiles in a chunk"""
        # Clear existing variations first
        chunk.tile_variations = {}
        
        # Use deterministic seeding based on world position and global seed
        # This ensures the same tile always gets the same variation regardless of chunk
        local_seed = self.generator.seed
        
        for tile in chunk.tiles:
            if tile["type"] == TerrainType.GRASS.value:
                # Create a consistent seed for this tile based on its world position
                tile_seed = (tile["x"] * 1299721) ^ (tile["y"] * 5741) ^ local_seed
                rng = random.Random(tile_seed)
                
                variations = []
                # Create base texture pattern - evenly distribute dots
                for i in range(5):  # More dots for denser texture
                    # Use golden ratio to distribute dots more naturally
                    golden_ratio = 0.618033988749895
                    angle = i * golden_ratio * 2 * 3.14159
                    distance = rng.uniform(4, 14)  # Varied distance from center
                    
                    # Calculate position using polar coordinates for better distribution
                    pos_x = 16 + int(math.cos(angle) * distance)
                    pos_y = 16 + int(math.sin(angle) * distance)
                    
                    # Keep within tile bounds
                    pos_x = max(2, min(30, pos_x))
                    pos_y = max(2, min(30, pos_y))
                    
                    # Vary shade slightly but consistently for this tile
                    base_shade = rng.randint(-15, 15)
                    shade = base_shade + rng.randint(-5, 5)
                    
                    size = rng.uniform(1.5, 4.0)  # Smaller, more consistent sizes
                    
                    # Calculate color based on position in world (subtle gradient effect)
                    # This helps hide chunk boundaries by creating gradual color changes
                    world_x, world_y = tile["x"] * 32, tile["y"] * 32
                    region_influence = (math.sin(world_x / 50.0) + math.cos(world_y / 50.0)) * 10
                    
                    var_color = (
                        max(0, min(255, 34 + shade + int(region_influence))),
                        max(0, min(255, 139 + shade)),
                        max(0, min(255, 34 + shade - int(region_influence * 0.5)))
                    )
                    variations.append((pos_x, pos_y, size, var_color))
                
                tile_key = (tile["x"], tile["y"])
                chunk.tile_variations[tile_key] = variations
    
    def _load_chunks_around(self, center_x: int, center_y: int):
        """Load chunks in view distance around given coordinates"""
        chunks_loaded = 0
        for dx in range(-self.view_distance, self.view_distance + 1):
            for dy in range(-self.view_distance, self.view_distance + 1):
                chunk_x = center_x + dx
                chunk_y = center_y + dy
                if (chunk_x, chunk_y) not in self.loaded_chunks:
                    chunk = self.generator.get_chunk(chunk_x, chunk_y)
                    self._generate_tile_variations(chunk)
                    self.loaded_chunks[(chunk_x, chunk_y)] = chunk
                    self._update_collision_rects(chunk)
                    chunks_loaded += 1
                    
                    # Debug: Count grass tiles in this chunk
                    grass_count = sum(1 for tile in chunk.tiles if tile["type"] == TerrainType.GRASS.value)
                    logger.debug(f"Loaded chunk ({chunk_x}, {chunk_y}) with {len(chunk.tiles)} tiles, {grass_count} grass tiles")
                    
        if chunks_loaded > 0:
            logger.debug(f"Loaded {chunks_loaded} new chunks around ({center_x}, {center_y})")
            logger.debug(f"Total loaded chunks: {len(self.loaded_chunks)}")
    
    def _update_collision_rects(self, chunk: WorldChunk):
        """Update collision rectangles based on chunk terrain"""
        for tile in chunk.tiles:
            if tile["type"] in [TerrainType.STONE.value, TerrainType.WATER.value, TerrainType.LAVA.value]:
                self.collision_rects.append(
                    pygame.Rect(tile["x"] * 32, tile["y"] * 32, 32, 32)
                )
        for structure in chunk.structures:
            if structure["type"] in ["rock", "tree"]:
                self.collision_rects.append(
                    pygame.Rect(structure["x"] * 32, structure["y"] * 32, 32, 32)
                )
    
    def init_grass(self):
        """Initialize grass blades on grass tiles"""
        self.grass_blades.clear()
        blade_count = 0
        
        for chunk in self.loaded_chunks.values():
            for tile in chunk.tiles:
                if tile["type"] == TerrainType.GRASS.value and blade_count < self.max_grass_blades:
                    # Only place grass on a subset of grass tiles to reduce counts
                    if random.random() < 0.3:  # 30% chance per grass tile
                        x = tile["x"] * 32 + random.randint(0, 32)
                        y = tile["y"] * 32 + random.randint(0, 32)
                        height = random.randint(8, 12)
                        self.grass_blades.append(GrassBlade(x, y, height))
                        blade_count += 1
    
    def load_map(self, map_file):
        with open(map_file) as f:
            data = json.load(f)
            self.spawn_points = data.get('spawns', self.spawn_points)
            
            # Load chunks from file if they exist
            for chunk_data in data.get('chunks', []):
                chunk = WorldChunk.from_dict(chunk_data)
                # Generate tile variations for loaded chunks
                self._generate_tile_variations(chunk)
                self.loaded_chunks[(chunk.x, chunk.y)] = chunk
                self._update_collision_rects(chunk)
    
    def save_map(self, map_file):
        """Save the current world state"""
        data = {
            'spawns': self.spawn_points,
            'chunks': [chunk.to_dict() for chunk in self.loaded_chunks.values()]
        }
        with open(map_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def check_collision(self, rect):
        return any(rect.colliderect(r) for r in self.collision_rects)
    
    def update_chunks(self, player_x: int, player_y: int):
        """Update loaded chunks based on player position"""
        chunk_x = player_x // (self.generator.chunk_size * 32)
        chunk_y = player_y // (self.generator.chunk_size * 32)
        
        # Load new chunks in view distance
        self._load_chunks_around(chunk_x, chunk_y)
        
        # Unload chunks outside view distance
        chunks_to_unload = []
        for (cx, cy) in self.loaded_chunks.keys():
            if abs(cx - chunk_x) > self.view_distance + 1 or \
               abs(cy - chunk_y) > self.view_distance + 1:
                chunks_to_unload.append((cx, cy))
        
        for chunk_key in chunks_to_unload:
            # Save chunk before unloading
            chunk = self.loaded_chunks[chunk_key]
            self.generator.save_chunk(chunk)
            del self.loaded_chunks[chunk_key]
    
    def update(self, dt: float, graphics=None):
        """Update world state, including tile variations, grass, and day/night cycle."""
        # logger.debug(f"World update called with dt: {dt}") # Commented out: can be verbose

        if not graphics:
            logger.warning("World.update called without graphics object, cannot emit particles.")

        # Update time
        try:
            # Update world time
            real_minutes_passed = dt * self.minutes_per_second
            self.minutes += real_minutes_passed
            
            # Handle hour rollover
            if self.minutes >= 60:
                self.hours += int(self.minutes / 60)
                self.minutes %= 60
                
                # Handle day rollover
                if self.hours >= 24:
                    self.days += int(self.hours / 24)
                    self.hours %= 24
            
            # Update wind and grass
            self.wind_time += dt
            
            # Create more visible leaf particles (Ensure graphics object is passed)
            if graphics and hasattr(graphics, 'particle_system') and not graphics.particle_system.disabled:
                if random.random() < dt * 0.02:  # 2% chance per second
                    x = random.uniform(0, self.pixel_width)
                    y = -20  # Start above world
                    graphics.particle_system.emit(
                        x, y, ParticleType.LEAF,
                        count=1,
                        color=(55, 180, 55, 255),  # Brighter, fully opaque green
                        size_range=(4.0, 6.0),  # Larger leaves
                        max_speed=15.0, # Adjusted speed for drifting leaf
                        lifetime_range=(3.0, 5.0),  # Good lifetime
                        use_world_space=True
                    )
            else:
                if not graphics:
                     logger.warning("World.update called without graphics object, cannot emit particles.")

        except Exception as e:
            logger.error(f"Error during world update: {e}", exc_info=True)
            # Decide how to handle error, e.g., skip frame or log and continue
    
    def draw(self, screen, offset: Tuple[float, float] = (0, 0)):
        """Draw the world with camera offset"""
        offset_x, offset_y = offset
        
        # Debug: Log drawing info
        logger.debug(f"Drawing world with offset ({offset_x}, {offset_y}), {len(self.loaded_chunks)} chunks loaded")
        
        tiles_drawn = 0
        
        # Draw base tiles with smoother gradient base colors
        for chunk in self.loaded_chunks.values():
            for tile in chunk.tiles:
                tile_screen_x = tile["x"] * 32 - offset_x
                tile_screen_y = tile["y"] * 32 - offset_y
                
                # Basic culling: Skip drawing tiles completely off-screen
                if tile_screen_x + 32 < 0 or tile_screen_x > screen.get_width() or \
                   tile_screen_y + 32 < 0 or tile_screen_y > screen.get_height():
                   continue
                   
                tiles_drawn += 1
                   
                # Calculate base color with subtle variation based on world position
                if tile["type"] == TerrainType.GRASS.value:
                    # Original base color
                    base_r, base_g, base_b = 34, 139, 34

                    # Subtle variation based on world position (reduced influence)
                    world_x, world_y = tile["x"] * 32, tile["y"] * 32
                    x_influence = math.sin(world_x / 80.0) * 5 # Reduced divisor and multiplier
                    y_influence = math.cos(world_y / 80.0) * 5 # Reduced divisor and multiplier

                    base_color = (
                        max(25, min(45, base_r + int(x_influence))), # Tighter range
                        max(130, min(150, base_g + int(y_influence))), # Tighter range
                        max(25, min(45, base_b))
                    )
                    pygame.draw.rect(screen, base_color,
                                   pygame.Rect(tile_screen_x, tile_screen_y, 32, 32))
                else:
                    # Use standard color for other types
                    color = self._get_tile_color(tile["type"])
                    pygame.draw.rect(screen, color,
                                   pygame.Rect(tile_screen_x, tile_screen_y, 32, 32))
                
                # Draw static texture/variation for grass tiles
                if tile["type"] == TerrainType.GRASS.value:
                    # Ensure tile_key uses world coordinates matching variation generation
                    tile_key = (tile["x"], tile["y"])
                    if tile_key in chunk.tile_variations:
                        for pos_x, pos_y, size, var_color in chunk.tile_variations[tile_key]:
                            # Apply offset to variation positions
                            var_screen_x = tile_screen_x + pos_x
                            var_screen_y = tile_screen_y + pos_y
                            pygame.draw.circle(screen, var_color, 
                                            (int(var_screen_x), int(var_screen_y)), size)
        
        if tiles_drawn > 0:
            logger.debug(f"Drew {tiles_drawn} tiles on screen")
        else:
            logger.warning("No tiles drawn! Check chunk loading and camera offset")
            
        # Draw structures (with offset)
        for chunk in self.loaded_chunks.values():
            for structure in chunk.structures:
                struct_screen_x = structure["x"] * 32 - offset_x
                struct_screen_y = structure["y"] * 32 - offset_y
                if struct_screen_x + 32 < 0 or struct_screen_x > screen.get_width() or \
                   struct_screen_y + 32 < 0 or struct_screen_y > screen.get_height():
                    continue
                if structure["type"] == "tree":
                    self._draw_tree(screen, structure, (struct_screen_x, struct_screen_y))
                elif structure["type"] == "rock":
                    self._draw_rock(screen, structure, (struct_screen_x, struct_screen_y))
            
            # Draw resources (with offset)
            for resource in chunk.resources:
                res_screen_x = resource["x"] * 32 - offset_x
                res_screen_y = resource["y"] * 32 - offset_y
                if res_screen_x + 32 < 0 or res_screen_x > screen.get_width() or \
                   res_screen_y + 32 < 0 or res_screen_y > screen.get_height():
                    continue
                self._draw_resource(screen, resource, (res_screen_x, res_screen_y))
        
        # Draw world borders - bold black lines at world edges
        world_pixel_width = self.width * 32
        world_pixel_height = self.height * 32
        
        # Calculate border positions on screen
        border_thickness = 4
        
        # Top border
        top_y = -offset_y
        if -border_thickness <= top_y <= screen.get_height():
            pygame.draw.rect(screen, (0, 0, 0), 
                           (-offset_x, top_y, world_pixel_width, border_thickness))
        
        # Bottom border  
        bottom_y = world_pixel_height - offset_y
        if -border_thickness <= bottom_y <= bottom_y + border_thickness:
            pygame.draw.rect(screen, (0, 0, 0), 
                           (-offset_x, bottom_y, world_pixel_width, border_thickness))
        
        # Left border
        left_x = -offset_x
        if -border_thickness <= left_x <= screen.get_width():
            pygame.draw.rect(screen, (0, 0, 0), 
                           (left_x, -offset_y, border_thickness, world_pixel_height))
        
        # Right border
        right_x = world_pixel_width - offset_x
        if -border_thickness <= right_x <= screen.get_width():
            pygame.draw.rect(screen, (0, 0, 0), 
                           (right_x, -offset_y, border_thickness, world_pixel_height))
        
        # Draw grass blades (with offset)
        for blade in self.grass_blades:
            blade.draw(screen, offset)
        
        # -- Day/Night System elements drawn WITHOUT offset relative to screen --
        # Make sure the day/night system is initialized with current screen size
        if not self.day_night_system.initialized or screen.get_size() != getattr(self.day_night_system, 'screen_size', None):
            self.day_night_system.initialize(screen.get_size())
        
        # Draw celestial body (sun/moon)
        self.day_night_system.draw_celestial_body(screen)
        
        # Draw shadows (Shadows are complex, applying offset here needs careful thought - 
        # for now, they are drawn relative to screen, which might look odd)
        # TODO: Rework shadow calculation to use world coords and apply offset correctly
        self.day_night_system.draw_shadows(screen, None) # Passing None for graphics to avoid issues
        
        # Apply day/night cycle overlay
        overlay = self.day_night_system.get_overlay_for_time(None) # Pass None for graphics
        if overlay:
            screen.blit(overlay, (0, 0))
    
    def _calculate_ambient_light(self) -> float:
        """
        Calculate ambient light level based on time of day.
        Returns a value from 0.0 (darkest) to 1.0 (brightest).
        """
        phase = self.get_day_phase()
        progress = self.day_progress
        
        if phase == "day":
            # Brightest at noon (12:00 = 0.5 day_progress)
            return min(1.0, 0.8 + 0.2 * (1.0 - abs(progress - 0.5) * 4))
        elif phase == "dawn":
            # Light increases during dawn
            dawn_progress = (self.hours - 5) * 60 + self.minutes
            return min(1.0, 0.3 + 0.7 * (dawn_progress / 180))
        elif phase == "dusk":
            # Light decreases during dusk
            dusk_progress = (self.hours - 18) * 60 + self.minutes
            return max(0.3, 1.0 - 0.7 * (dusk_progress / 180))
        else:  # night
            # Darkest at midnight (0:00 = 0.0 day_progress)
            night_darkness = 0.3 - 0.2 * (1.0 - min(1.0, abs(progress - 0.0) * 4))
            return max(0.1, night_darkness)
            
    def _apply_lighting_overlay(self, screen, ambient_light):
        """Apply a lighting overlay based on time of day"""
        # Skip in full daylight
        if ambient_light >= 0.99:
            return
            
        # Create a semi-transparent overlay surface
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        
        # Calculate overlay color and alpha based on time of day
        alpha = int(255 * (1.0 - ambient_light) * 0.7)  # Cap at 70% darkness
        
        phase = self.get_day_phase()
        if phase == "night":
            # Deep blue for night
            overlay_color = (20, 20, 60, alpha)
        elif phase == "dawn":
            # Orange-ish for dawn
            overlay_color = (70, 40, 20, alpha)
        elif phase == "dusk":
            # Red-orange for dusk
            overlay_color = (70, 30, 20, alpha)
        else:
            # Slight darkening for cloudy day, etc.
            overlay_color = (20, 20, 40, alpha)
            
        overlay.fill(overlay_color)
        screen.blit(overlay, (0, 0))
        
    def _draw_celestial_body(self, screen):
        """Draw the sun or moon based on time of day"""
        screen_width, screen_height = screen.get_size()
        
        # Calculate position based on day_progress (0.0 to 1.0)
        # This creates an arc path across the sky
        angle = self.day_progress * math.pi * 2 - math.pi/2
        radius = screen_height * 0.9
        
        # Calculate x, y position on the arc
        x = screen_width * 0.5 + math.cos(angle) * radius
        y = screen_height * 0.9 + math.sin(angle) * radius
            
        # Determine if it's sun or moon and if it's visible
        # Only show when it's above the horizon
        visible = y < screen_height
        
        if visible:
            phase = self.get_day_phase()
            if phase in ["dawn", "day", "dusk"]:
                # Draw sun
                # Sun rays and glow
                glow_radius = 25
                glow_color = (255, 255, 200, 100)
                if phase == "dawn":
                    glow_color = (255, 200, 150, 120)
                elif phase == "dusk":
                    glow_color = (255, 150, 100, 120)
                
                pygame.draw.circle(screen, glow_color, (int(x), int(y)), glow_radius, 0)
                
                # Draw sun rays
                for i in range(8):
                    ray_angle = i * math.pi / 4
                    ray_x = x + math.cos(ray_angle) * glow_radius * 1.5
                    ray_y = y + math.sin(ray_angle) * glow_radius * 1.5
                    pygame.draw.line(screen, glow_color, (int(x), int(y)), (int(ray_x), int(ray_y)), 3)
                
                # Draw sun body
                sun_color = (255, 255, 0)
                if phase == "dawn":
                    sun_color = (255, 200, 100)
                elif phase == "dusk":
                    sun_color = (255, 150, 50)
                    
                pygame.draw.circle(screen, sun_color, (int(x), int(y)), 15, 0)
            else:
                # Draw moon
                # Moon glow
                pygame.draw.circle(screen, (200, 200, 255, 80), (int(x), int(y)), 18, 0)
                
                # Draw moon body
                pygame.draw.circle(screen, (220, 220, 255), (int(x), int(y)), 13, 0)
                
                # Draw moon crater details
                for _ in range(3):
                    crater_x = x + random.randint(-8, 8)
                    crater_y = y + random.randint(-8, 8)
                    crater_size = random.randint(2, 4)
                    pygame.draw.circle(screen, (200, 200, 235), (int(crater_x), int(crater_y)), crater_size, 0)
            
            # Draw object shadows (for trees, rocks, etc.) if sun/moon is visible
            self._draw_shadows(screen, x, y)
    
    def _draw_shadows(self, screen, light_x, light_y):
        """Draw shadows for objects based on the light source position"""
        # Only process structures that can cast shadows
        phase = self.get_day_phase()
        
        # Skip shadows at night or if disabled
        if phase == "night":
            return
            
        # Define shadow parameters
        shadow_length = 30
        shadow_alpha = 100
        
        # Shadows are more pronounced during dawn/dusk
        if phase == "dawn" or phase == "dusk":
            shadow_length = 50
            shadow_alpha = 150
            
        # Shadows are shorter near noon
        if phase == "day" and abs(self.hours - 12) < 2:
            shadow_length = 15
            
        # Process all loaded chunks
        for chunk in self.loaded_chunks.values():
            # Draw shadows for trees
            for structure in chunk.structures:
                if structure["type"] == "tree":
                    # Get structure position (center of base)
                    struct_x = structure["x"] * 32 + 16
                    struct_y = structure["y"] * 32 + 24
                    
                    # Calculate vector from light to structure
                    dx = struct_x - light_x
                    dy = struct_y - light_y
                    
                    # Normalize and scale by shadow length
                    length = max(0.001, math.sqrt(dx*dx + dy*dy))
                    dx = dx / length * shadow_length
                    dy = dy / length * shadow_length
                    
                    # Shadow endpoint
                    shadow_x = struct_x + dx
                    shadow_y = struct_y + dy
                    
                    # Create shadow polygon
                    shadow_width = 12  # Half width of tree trunk
                    
                    # Calculate perpendicular vector for shadow width
                    perp_x = -dy / length * shadow_width
                    perp_y = dx / length * shadow_width
                    
                    # Define shadow polygon points
                    points = [
                        (struct_x + perp_x, struct_y + perp_y),
                        (struct_x - perp_x, struct_y - perp_y),
                        (shadow_x - perp_x*0.5, shadow_y - perp_y*0.5),
                        (shadow_x + perp_x*0.5, shadow_y + perp_y*0.5)
                    ]
                    
                    # Draw shadow with transparency
                    shadow_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                    pygame.draw.polygon(shadow_surface, (0, 0, 0, shadow_alpha), [(int(x), int(y)) for x, y in points])
                    screen.blit(shadow_surface, (0, 0))
                    
                elif structure["type"] == "rock":
                    # Get structure position (center of base)
                    struct_x = structure["x"] * 32 + 16
                    struct_y = structure["y"] * 32 + 16
                    
                    # Calculate vector from light to structure
                    dx = struct_x - light_x
                    dy = struct_y - light_y
                    
                    # Normalize and scale by shadow length
                    length = max(0.001, math.sqrt(dx*dx + dy*dy))
                    dx = dx / length * shadow_length * 0.7  # Rocks have shorter shadows
                    dy = dy / length * shadow_length * 0.7
                    
                    # Shadow endpoint
                    shadow_x = struct_x + dx
                    shadow_y = struct_y + dy
                    
                    # Draw shadow
                    shadow_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                    
                    # Draw oval shadow for rock
                    shadow_rect = pygame.Rect(
                        int(struct_x + dx/2 - 10), 
                        int(struct_y + dy/2 - 6),
                        20, 12
                    )
                    pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), shadow_rect)
                    screen.blit(shadow_surface, (0, 0))
    
    def _get_tile_color(self, tile_type: str) -> Tuple[int, int, int]:
        """Get the color for a tile type"""
        colors = {
            TerrainType.GRASS: (34, 139, 34),
            TerrainType.STONE: (128, 128, 128),
            TerrainType.WATER: (30, 144, 255),
            TerrainType.LAVA: (207, 16, 32),
            TerrainType.DIRT: (139, 69, 19),
            TerrainType.SAND: (238, 214, 175),
            TerrainType.SNOW: (250, 250, 250)
        }
        return colors.get(tile_type, (100, 100, 100))  # Default gray color for unknown types
    
    def _draw_tree(self, screen, tree, screen_pos: Tuple[float, float]):
        """Draw a tree structure at the given screen position."""
        x, y = screen_pos
        trunk_color = (139, 69, 19)
        leaves_color = (34, 139, 34)
        
        # Draw trunk
        pygame.draw.rect(screen, trunk_color, (x + 12, y + 8, 8, 24))
        
        # Draw leaves based on variant
        variant = tree.get("variant", 0) # Default to variant 0 if missing
        if variant == 0:  # Round
            pygame.draw.circle(screen, leaves_color, (x + 16, y + 8), 16)
        elif variant == 1:  # Triangular
            points = [(x + 16, y - 8), (x, y + 16), (x + 32, y + 16)]
            pygame.draw.polygon(screen, leaves_color, points)
        else:  # Bushy
            for i in range(3):
                offset = i * 8
                pygame.draw.circle(screen, leaves_color, (x + 16, y + offset), 12)
    
    def _draw_rock(self, screen, rock, screen_pos: Tuple[float, float]):
        """Draw a rock structure at the given screen position."""
        x, y = screen_pos
        color = (128, 128, 128)
        
        variant = rock.get("variant", 0)
        if variant == 0:  # Round
            pygame.draw.circle(screen, color, (x + 16, y + 16), 16)
        elif variant == 1:  # Angular
            points = [(x + 8, y + 8), (x + 24, y + 8), 
                     (x + 28, y + 24), (x + 4, y + 24)]
            pygame.draw.polygon(screen, color, points)
        else:  # Cluster
            for i in range(3):
                for j in range(2):
                    pygame.draw.circle(screen, color, 
                                    (x + 8 + i * 8, y + 8 + j * 8), 6)
    
    def _draw_resource(self, screen, resource, screen_pos: Tuple[float, float]):
        """Draw a resource node with more detail at the given screen position."""
        x, y = screen_pos
        center_x = x + 16
        center_y = y + 16
        
        res_type = resource["type"]
        quantity = resource.get("quantity", 1)

        if res_type == "herb":
            # Draw a few green leaves
            leaf_color = (30, 180, 40)
            pygame.draw.ellipse(screen, leaf_color, (center_x - 5, center_y - 3, 6, 10))
            pygame.draw.ellipse(screen, leaf_color, (center_x + 1, center_y - 3, 6, 10))
            pygame.draw.ellipse(screen, leaf_color, (center_x - 2, center_y - 6, 6, 10), 1) # Outline
        
        elif res_type == "mushroom":
            # Draw a mushroom shape
            stem_color = (220, 220, 200)
            cap_color = (255, 100, 100) # Reddish-pink cap
            pygame.draw.rect(screen, stem_color, (center_x - 2, center_y + 2, 4, 6)) # Stem
            pygame.draw.circle(screen, cap_color, (center_x, center_y - 1), 6) # Cap
            pygame.draw.circle(screen, (0,0,0, 50), (center_x, center_y - 1), 6, 1) # Cap outline
            
        elif res_type == "berry_bush":
            # Draw a small bush with berries
            bush_color = (20, 100, 30)
            berry_color = (220, 20, 60)
            pygame.draw.circle(screen, bush_color, (center_x, center_y), 10) # Bush
            # Add some red dots for berries
            pygame.draw.circle(screen, berry_color, (center_x - 4, center_y - 3), 3)
            pygame.draw.circle(screen, berry_color, (center_x + 3, center_y - 2), 3)
            pygame.draw.circle(screen, berry_color, (center_x, center_y + 4), 3)
            
        elif res_type == "iron_ore":
            # Draw a gray rock shape with darker patches
            rock_color = (160, 160, 160)
            patch_color = (100, 100, 100)
            points = [(center_x - 8, center_y + 8), (center_x, center_y - 8), (center_x + 8, center_y + 8)]
            pygame.draw.polygon(screen, rock_color, points)
            pygame.draw.circle(screen, patch_color, (center_x - 3, center_y + 4), 3)
            pygame.draw.circle(screen, patch_color, (center_x + 4, center_y + 2), 2)
            
        elif res_type == "gold_ore":
            # Draw a yellowish rock shape with sparkles
            rock_color = (220, 180, 50)
            sparkle_color = (255, 255, 150)
            points = [(center_x - 7, center_y + 7), (center_x + 2, center_y - 8), (center_x + 7, center_y + 7)]
            pygame.draw.polygon(screen, rock_color, points)
            # Add sparkles
            pygame.draw.line(screen, sparkle_color, (center_x - 2, center_y - 4), (center_x + 2, center_y - 4), 1)
            pygame.draw.line(screen, sparkle_color, (center_x, center_y - 6), (center_x, center_y - 2), 1)
            
        elif res_type == "crystal":
            # Draw a purple crystal shape
            crystal_color = (147, 112, 219)
            highlight_color = (200, 160, 255)
            points = [
                (center_x, center_y - 10), (center_x + 6, center_y),
                (center_x + 3, center_y + 8), (center_x - 3, center_y + 8),
                (center_x - 6, center_y)
            ]
            pygame.draw.polygon(screen, crystal_color, points)
            pygame.draw.line(screen, highlight_color, (center_x, center_y - 10), (center_x, center_y + 8), 1) # Highlight line

        elif res_type == "cactus":
             # Draw simple cactus shape
             cactus_color = (50, 180, 50)
             pygame.draw.rect(screen, cactus_color, (center_x - 4, center_y - 8, 8, 16), border_radius=2) # Main body
             pygame.draw.rect(screen, cactus_color, (center_x - 8, center_y - 2, 4, 8), border_radius=2) # Left arm
             pygame.draw.rect(screen, cactus_color, (center_x + 4, center_y - 2, 4, 8), border_radius=2) # Right arm

        elif res_type == "desert_flower":
             # Draw simple flower shape
             petal_color = (255, 192, 203) # Pink
             center_color = (255, 255, 100) # Yellow center
             pygame.draw.circle(screen, center_color, (center_x, center_y), 4) # Center
             # Petals
             for angle in range(0, 360, 72):
                 rad = math.radians(angle)
                 px = center_x + math.cos(rad) * 8
                 py = center_y + math.sin(rad) * 8
                 pygame.draw.circle(screen, petal_color, (int(px), int(py)), 5)
                 
        else:
            # Fallback to default circle if type is unknown
            colors = {
                "iron_ore": (192, 192, 192), "gold_ore": (255, 215, 0),
                "crystal": (147, 112, 219), "herb": (50, 205, 50),
                "mushroom": (255, 182, 193), "berry_bush": (220, 20, 60),
                "cactus": (50, 205, 50), "desert_flower": (255, 192, 203)
            }
            color = colors.get(res_type, (200, 200, 200)) # Default gray
            pygame.draw.circle(screen, color, (center_x, center_y), 8)
        
        # Draw quantity indicator (small dots below the main graphic)
        if quantity > 1:
            dot_color = (230, 230, 230) # Light gray dots
            dot_y = y + 28 # Position below the resource graphic
            start_x = center_x - (min(quantity, 4) - 1) * 4 / 2
            for i in range(min(quantity, 4)):
                pygame.draw.circle(screen, dot_color, (int(start_x + i * 4), dot_y), 2)
    
    def to_dict(self) -> dict:
        """Convert world state to serializable dictionary"""
        # Create a dictionary of chunk data
        chunks_data = {}
        for pos, chunk in self.loaded_chunks.items():
            chunks_data[f"{pos[0]}_{pos[1]}"] = chunk.to_dict()
            
        return {
            "seed": self.seed,
            "spawn_points": self.spawn_points,
            "loaded_chunks": chunks_data,
            "time": {
                "minutes": self.minutes,
                "hours": self.hours,
                "days": self.days
            }
        }
    
    def from_dict(self, data: dict) -> None:
        """Load world state from dictionary"""
        # Reset state
        self.loaded_chunks = {}
        self.collision_rects = []
        self.grass_blades = []
        
        # Set seed and create generator (if different)
        self.seed = data.get("seed", self.seed)
        self.generator = SynapstexWorldGenerator(self.seed)
        
        # Set spawn points
        self.spawn_points = data.get("spawn_points", self.spawn_points)
        
        # Load time data
        time_data = data.get("time", {})
        self.minutes = time_data.get("minutes", 0)
        self.hours = time_data.get("hours", 8)
        self.days = time_data.get("days", 1)
        
        # Load chunks
        loaded_chunks = data.get("loaded_chunks", {})
        for pos_str, chunk_data in loaded_chunks.items():
            try:
                x, y = map(int, pos_str.split("_"))
                # Use generator to load or create chunk
                chunk = self.generator.load_chunk_from_dict(chunk_data)
                self._generate_tile_variations(chunk)
                self.loaded_chunks[(x, y)] = chunk
                self._update_collision_rects(chunk)
            except Exception as e:
                print(f"Error loading chunk at {pos_str}: {e}")
        
        # Initialize grass blades
        self.init_grass()
    
    @property
    def day_progress(self) -> float:
        """
        Returns the progress through the current day as a value from 0.0 to 1.0
        where 0.0 is midnight (00:00) and 1.0 is just before midnight (23:59)
        """
        return (self.hours * 60 + self.minutes) / 1440  # 1440 = minutes in a day
    
    def get_day_phase(self) -> str:
        """
        Returns the current phase of the day:
        - Dawn: 5:00 - 7:59
        - Day: 8:00 - 17:59
        - Dusk: 18:00 - 20:59
        - Night: 21:00 - 4:59
        """
        if 5 <= self.hours < 8:
            return "dawn"
        elif 8 <= self.hours < 18:
            return "day"
        elif 18 <= self.hours < 21:
            return "dusk"
        else:  # 21-23, 0-4
            return "night"
    
    def _draw_structure_shadows(self, shadow_surface, light_x, light_y, shadow_length, shadow_alpha):
        """Draw shadows for structures - used by the DayNightSystem"""
        # Process all loaded chunks
        for chunk in self.loaded_chunks.values():
            # Draw shadows for trees
            for structure in chunk.structures:
                if structure["type"] == "tree":
                    # Get structure position (center of base)
                    struct_x = structure["x"] * 32 + 16
                    struct_y = structure["y"] * 32 + 24
                    
                    # Calculate vector from light to structure
                    dx = struct_x - light_x
                    dy = struct_y - light_y
                    
                    # Normalize and scale by shadow length
                    length = max(0.001, math.sqrt(dx*dx + dy*dy))
                    dx = dx / length * shadow_length
                    dy = dy / length * shadow_length
                    
                    # Shadow endpoint
                    shadow_x = struct_x + dx
                    shadow_y = struct_y + dy
                    
                    # Create shadow polygon
                    shadow_width = 12  # Half width of tree trunk
                    
                    # Calculate perpendicular vector for shadow width
                    perp_x = -dy / length * shadow_width
                    perp_y = dx / length * shadow_width
                    
                    # Define shadow polygon points
                    points = [
                        (struct_x + perp_x, struct_y + perp_y),
                        (struct_x - perp_x, struct_y - perp_y),
                        (shadow_x - perp_x*0.5, shadow_y - perp_y*0.5),
                        (shadow_x + perp_x*0.5, shadow_y + perp_y*0.5)
                    ]
                    
                    # Draw shadow with transparency
                    pygame.draw.polygon(shadow_surface, (0, 0, 0, shadow_alpha), [(int(x), int(y)) for x, y in points])
                    
                elif structure["type"] == "rock":
                    # Get structure position (center of base)
                    struct_x = structure["x"] * 32 + 16
                    struct_y = structure["y"] * 32 + 16
                    
                    # Calculate vector from light to structure
                    dx = struct_x - light_x
                    dy = struct_y - light_y
                    
                    # Normalize and scale by shadow length
                    length = max(0.001, math.sqrt(dx*dx + dy*dy))
                    dx = dx / length * shadow_length * 0.7  # Rocks have shorter shadows
                    dy = dy / length * shadow_length * 0.7
                    
                    # Shadow endpoint
                    shadow_x = struct_x + dx
                    shadow_y = struct_y + dy
                    
                    # Draw oval shadow for rock
                    shadow_rect = pygame.Rect(
                        int(struct_x + dx/2 - 10), 
                        int(struct_y + dy/2 - 6),
                        20, 12
                    )
                    pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), shadow_rect) 