"""
Modern World System for Runic Lands

This module provides a clean, modern implementation of the world system
that fixes the flashing tree issue and provides better performance.

Key Features:
- Fixed color flashing by using persistent tree colors
- Separated generation from rendering logic
- Performance optimizations with caching
- Proper error handling and logging
- Type hints throughout
- Modular design for easy testing
"""

import pygame
import random
import math
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from pathlib import Path

from systems.world_generation_modern import (
    ModernWorldGenerator, ModernWorldChunk, TreeData, TileData,
    BiomeType, TerrainType, TreeType
)
from systems.tree_renderer import ModernTreeRenderer, RenderConfig
from systems.synapstex import SynapstexGraphics, ParticleType, RenderLayer, BlendMode


logger = logging.getLogger(__name__)


@dataclass
class WorldConfig:
    """
    Holds configuration settings for the modern world system.

    Attributes:
        tile_size (int): The size of a single tile in pixels.
        chunk_size (int): The size of a world chunk (width and height) in tiles.
        world_width (int): The total width of the world in chunks.
        world_height (int): The total height of the world in chunks.
        view_distance (int): The radius of chunks to keep loaded around the player.
        max_grass_blades (int): The maximum number of grass blades to render.
        wind_strength (float): The strength of the wind effect on trees and grass.
        minutes_per_second (float): The rate at which in-game time passes.
        start_hour (int): The initial hour of the day when the world is created.
    """
    tile_size: int = 32
    chunk_size: int = 16
    world_width: int = 64
    world_height: int = 64
    view_distance: int = 2
    max_grass_blades: int = 1000
    wind_strength: float = 0.5
    minutes_per_second: float = 1.0
    start_hour: int = 8


class ModernWorld:
    """
    Manages the game world, including chunk loading, time, and environmental effects.

    This class orchestrates the world generation, rendering, and updates. It handles
    the day-night cycle, weather (via particles), and dynamic elements like wind,
    while optimizing performance by only processing nearby chunks.
    """
    
    def __init__(self, config: Optional[WorldConfig] = None, seed: Optional[int] = None):
        """
        Initializes the ModernWorld.

        Args:
            config (Optional[WorldConfig], optional): A configuration object for
                                                      world settings. Defaults to None.
            seed (Optional[int], optional): A seed for the world generator to
                                            ensure reproducibility. Defaults to None.
        """
        self.config = config or WorldConfig()
        self._seed = seed if seed is not None else random.randint(0, 999999)
        
        # Initialize systems
        self.generator = ModernWorldGenerator(self._seed)
        self.tree_renderer = ModernTreeRenderer(RenderConfig(
            tile_size=self.config.tile_size,
            wind_strength=self.config.wind_strength
        ))
        
        # World state
        self.loaded_chunks: Dict[Tuple[int, int], ModernWorldChunk] = {}
        self.border_trees: List[TreeData] = []
        self.border_tiles: List[TileData] = []
        
        # Collision system
        self.collision_rects: List[pygame.Rect] = []
        
        # Grass system
        self.grass_blades: List[Dict] = []
        self.wind_time = 0.0
        
        # Time system
        self._minutes = 0
        self._hours = self.config.start_hour
        self._days = 1
        
        # Day/night system
        self.day_night_system = None  # Will be initialized separately
        
        # Generate initial world
        self._generate_forest_border()
        self._generate_initial_grass()
        
        logger.info(f"Modern world initialized with seed {self.seed}")
    
    def update(self, dt: float, graphics: Optional[SynapstexGraphics] = None):
        """
        Updates the state of the world.

        This method advances the in-game time, updates wind and other dynamic
        environmental effects, and handles particle emissions.

        Args:
            dt (float): The time delta since the last update, in seconds.
            graphics (Optional[SynapstexGraphics], optional): The graphics engine,
                                                              used for emitting particles.
                                                              Defaults to None.
        """
        try:
            # Update time
            self._minutes += dt * self.config.minutes_per_second
            if self._minutes >= 60:
                self._minutes = 0
                self._hours = (self._hours + 1) % 24
                if self._hours == 0:
                    self._days += 1
            
            # Update wind
            self.wind_time += dt
            self.tree_renderer.update(dt)
            
            # Update grass
            self._update_grass(dt)
            
            # Emit particles if graphics available
            # TODO: Fix particle emission when SynapstexGraphics supports it
            # if graphics and random.random() < 0.01:  # 1% chance per frame
            #     self._emit_environmental_particles(graphics)
                
        except Exception as e:
            logger.error(f"Error updating world: {e}", exc_info=True)
    
    def get_chunk(self, chunk_x: int, chunk_y: int) -> ModernWorldChunk:
        """
        Retrieves a chunk from memory or generates it if it doesn't exist.

        Args:
            chunk_x (int): The x-coordinate of the chunk.
            chunk_y (int): The y-coordinate of the chunk.

        Returns:
            ModernWorldChunk: The requested world chunk.
        """
        chunk_key = (chunk_x, chunk_y)
        if chunk_key not in self.loaded_chunks:
            self.loaded_chunks[chunk_key] = self.generator.get_chunk(chunk_x, chunk_y)
        return self.loaded_chunks[chunk_key]
    
    def update_chunks(self, player_x: int, player_y: int):
        """
        Updates the set of loaded chunks based on the player's position.

        This method loads chunks within the `view_distance` and unloads those
        that are too far away, optimizing memory usage.

        Args:
            player_x (int): The player's x-coordinate in world space.
            player_y (int): The player's y-coordinate in world space.
        """
        try:
            # Convert player position to chunk coordinates
            chunk_x = player_x // (self.config.chunk_size * self.config.tile_size)
            chunk_y = player_y // (self.config.chunk_size * self.config.tile_size)
            
            # Load chunks in view distance
            chunks_to_load = set()
            for dx in range(-self.config.view_distance, self.config.view_distance + 1):
                for dy in range(-self.config.view_distance, self.config.view_distance + 1):
                    chunks_to_load.add((chunk_x + dx, chunk_y + dy))
            
            # Load new chunks
            for chunk_key in chunks_to_load:
                if chunk_key not in self.loaded_chunks:
                    self.loaded_chunks[chunk_key] = self.generator.get_chunk(*chunk_key)
            
            # Unload distant chunks
            chunks_to_remove = []
            for chunk_key in self.loaded_chunks:
                if chunk_key not in chunks_to_load:
                    chunks_to_remove.append(chunk_key)
            
            for chunk_key in chunks_to_remove:
                del self.loaded_chunks[chunk_key]
                
        except Exception as e:
            logger.error(f"Error updating chunks: {e}", exc_info=True)
    
    def draw(self, screen: pygame.Surface, offset: Tuple[float, float] = (0, 0)):
        """
        Draws the visible portion of the world to the screen.

        This includes border tiles, loaded chunks, border trees, and grass, all
        rendered with the appropriate camera offset.

        Args:
            screen (pygame.Surface): The screen surface to draw on.
            offset (Tuple[float, float], optional): The camera's world offset.
                                                     Defaults to (0, 0).
        """
        try:
            offset_x, offset_y = offset
            
            # Draw border tiles first
            self._draw_border_tiles(screen, offset)
            
            # Draw loaded chunks
            self._draw_loaded_chunks(screen, offset)
            
            # Draw border trees
            self._draw_border_trees(screen, offset)
            
            # Draw grass
            self._draw_grass(screen, offset)
            
        except Exception as e:
            logger.error(f"Error drawing world: {e}", exc_info=True)
    
    def _generate_forest_border(self):
        """
        Generates a dense forest border around the playable area of the world.

        This method creates the visual boundary for the game world, complete
        with collision data for the densest parts of the forest.
        """
        try:
            # Calculate world boundaries
            world_chunks_x = self.config.world_width // self.config.chunk_size
            world_chunks_y = self.config.world_height // self.config.chunk_size
            
            world_min_x = 0
            world_max_x = world_chunks_x * self.config.chunk_size - 1
            world_min_y = 0
            world_max_y = world_chunks_y * self.config.chunk_size - 1
            
            # Extended boundaries
            extended_depth = 8
            extended_min_x = world_min_x - extended_depth
            extended_max_x = world_max_x + extended_depth
            extended_min_y = world_min_y - extended_depth
            extended_max_y = world_max_y + extended_depth
            
            # Generate border trees and tiles
            self.border_trees = []
            self.border_tiles = []
            
            # Generate border for all four edges
            for x in range(extended_min_x, extended_max_x + 1):
                for y in range(extended_min_y, extended_max_y + 1):
                    # Check if this position is in the border area
                    if self._is_border_position(x, y, world_min_x, world_max_x, world_min_y, world_max_y, extended_depth):
                        # Add ground tile
                        tile = TileData(
                            x=x, y=y,
                            terrain_type=TerrainType.GRASS,
                            elevation=0.0,
                            is_border=True
                        )
                        self.border_tiles.append(tile)
                        
                        # Add tree with persistent color
                        tree = self.generator._create_tree(
                            x, y,
                            is_border=True,
                            depth_layer=self._calculate_depth_layer(x, y, world_min_x, world_max_x, world_min_y, world_max_y),
                            is_extended=self._is_extended_position(x, y, world_min_x, world_max_x, world_min_y, world_max_y, extended_depth)
                        )
                        self.border_trees.append(tree)
                        
                        # Add collision for dense trees
                        if tree.depth_layer < 6:
                            tree_rect = pygame.Rect(x * self.config.tile_size, y * self.config.tile_size, 
                                                  self.config.tile_size, self.config.tile_size)
                            self.collision_rects.append(tree_rect)
            
            logger.info(f"Generated forest border with {len(self.border_trees)} trees and {len(self.border_tiles)} tiles")
            
        except Exception as e:
            logger.error(f"Error generating forest border: {e}", exc_info=True)
    
    def _is_border_position(self, x: int, y: int, min_x: int, max_x: int, min_y: int, max_y: int, depth: int) -> bool:
        """
        Checks if a given coordinate is within the border area of the world.

        Args:
            x (int): The x-coordinate to check.
            y (int): The y-coordinate to check.
            min_x (int): The minimum x-boundary of the playable world.
            max_x (int): The maximum x-boundary of the playable world.
            min_y (int): The minimum y-boundary of the playable world.
            max_y (int): The maximum y-boundary of the playable world.
            depth (int): The depth of the border area.

        Returns:
            bool: True if the position is in the border, False otherwise.
        """
        return (x < min_x or x > max_x or y < min_y or y > max_y) and \
               (min_x - depth <= x <= max_x + depth and min_y - depth <= y <= max_y + depth)
    
    def _calculate_depth_layer(self, x: int, y: int, min_x: int, max_x: int, min_y: int, max_y: int) -> int:
        """
        Calculates the depth layer of a position within the border.

        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.
            min_x (int): The minimum x-boundary of the playable world.
            max_x (int): The maximum x-boundary of the playable world.
            min_y (int): The minimum y-boundary of the playable world.
            max_y (int): The maximum y-boundary of the playable world.

        Returns:
            int: The depth layer, capped at 10.
        """
        dist_from_edge = min(
            abs(x - min_x), abs(x - max_x),
            abs(y - min_y), abs(y - max_y)
        )
        return min(dist_from_edge, 10)  # Cap at 10
    
    def _is_extended_position(self, x: int, y: int, min_x: int, max_x: int, min_y: int, max_y: int, depth: int) -> bool:
        """
        Checks if a position is in the extended, non-playable area of the forest.

        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.
            min_x (int): The minimum x-boundary of the playable world.
            max_x (int): The maximum x-boundary of the playable world.
            min_y (int): The minimum y-boundary of the playable world.
            max_y (int): The maximum y-boundary of the playable world.
            depth (int): The depth of the border area.

        Returns:
            bool: True if the position is in the extended area, False otherwise.
        """
        return (x < min_x - depth or x > max_x + depth or 
                y < min_y - depth or y > max_y + depth)
    
    def _generate_initial_grass(self):
        """
        Populates the world with an initial set of decorative grass blades.
        """
        self.grass_blades = []
        for _ in range(self.config.max_grass_blades):
            grass = {
                "x": random.randint(0, self.config.world_width * self.config.tile_size),
                "y": random.randint(0, self.config.world_height * self.config.tile_size),
                "height": random.randint(8, 16),
                "angle": random.uniform(0, 2 * math.pi),
                "wind_offset": random.uniform(0, 2 * math.pi)
            }
            self.grass_blades.append(grass)
    
    def _update_grass(self, dt: float):
        """
        Updates the wind animation for grass blades.

        Args:
            dt (float): The time delta since the last update.
        """
        for grass in self.grass_blades:
            grass["angle"] += dt * 0.5  # Gentle swaying
    
    def _emit_environmental_particles(self, graphics: SynapstexGraphics):
        """
        Emits environmental particles, such as falling leaves in a forest.

        Args:
            graphics (SynapstexGraphics): The graphics engine to use for
                                          emitting particles.
        """
        if random.random() < 0.1:  # 10% chance
            x = random.randint(0, self.config.world_width * self.config.tile_size)
            y = random.randint(0, self.config.world_height * self.config.tile_size)
            
            graphics.emit_particle(
                ParticleType.LEAF,
                x, y,
                velocity=(random.uniform(-10, 10), random.uniform(5, 15)),
                lifetime=random.uniform(2, 5)
            )
    
    def _draw_border_tiles(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """
        Draws the ground tiles for the forest border.

        Args:
            screen (pygame.Surface): The screen surface to draw on.
            offset (Tuple[float, float]): The camera offset.
        """
        offset_x, offset_y = offset
        
        for tile in self.border_tiles:
            tile_screen_x = tile.x * self.config.tile_size - offset_x
            tile_screen_y = tile.y * self.config.tile_size - offset_y
            
            # Only draw if on screen
            if (tile_screen_x + self.config.tile_size < 0 or tile_screen_x > screen.get_width() or
                tile_screen_y + self.config.tile_size < 0 or tile_screen_y > screen.get_height()):
                continue
            
            # Draw grass tile
            tile_color = self._get_tile_color(tile.terrain_type)
            pygame.draw.rect(screen, tile_color, 
                           (tile_screen_x, tile_screen_y, self.config.tile_size, self.config.tile_size))
    
    def _draw_loaded_chunks(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """
        Draws all currently loaded world chunks.

        Args:
            screen (pygame.Surface): The screen surface.
            offset (Tuple[float, float]): The camera offset.
        """
        offset_x, offset_y = offset
        
        for chunk in self.loaded_chunks.values():
            # Draw tiles
            for tile in chunk.tiles:
                tile_screen_x = tile.x * self.config.tile_size - offset_x
                tile_screen_y = tile.y * self.config.tile_size - offset_y
                
                if (tile_screen_x + self.config.tile_size < 0 or tile_screen_x > screen.get_width() or
                    tile_screen_y + self.config.tile_size < 0 or tile_screen_y > screen.get_height()):
                    continue
                
                tile_color = self._get_tile_color(tile.terrain_type)
                pygame.draw.rect(screen, tile_color, 
                               (tile_screen_x, tile_screen_y, self.config.tile_size, self.config.tile_size))
            
            # Draw trees
            for tree in chunk.trees:
                tree_screen_x = tree.x * self.config.tile_size - offset_x
                tree_screen_y = tree.y * self.config.tile_size - offset_y
                
                if (tree_screen_x + self.config.tile_size < 0 or tree_screen_x > screen.get_width() or
                    tree_screen_y + self.config.tile_size < 0 or tree_screen_y > screen.get_height()):
                    continue
                
                self.tree_renderer.render_tree(screen, tree, (tree_screen_x, tree_screen_y))
    
    def _draw_border_trees(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """
        Draws the trees in the forest border.

        Args:
            screen (pygame.Surface): The screen surface.
            offset (Tuple[float, float]): The camera offset.
        """
        offset_x, offset_y = offset
        
        for tree in self.border_trees:
            tree_screen_x = tree.x * self.config.tile_size - offset_x
            tree_screen_y = tree.y * self.config.tile_size - offset_y
            
            if (tree_screen_x + self.config.tile_size < 0 or tree_screen_x > screen.get_width() or
                tree_screen_y + self.config.tile_size < 0 or tree_screen_y > screen.get_height()):
                continue
            
            self.tree_renderer.render_tree(screen, tree, (tree_screen_x, tree_screen_y))
    
    def _draw_grass(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """
        Draws decorative grass blades on the screen.

        Args:
            screen (pygame.Surface): The screen surface.
            offset (Tuple[float, float]): The camera offset.
        """
        offset_x, offset_y = offset
        
        for grass in self.grass_blades:
            grass_x = grass["x"] - offset_x
            grass_y = grass["y"] - offset_y
            
            if (grass_x < 0 or grass_x > screen.get_width() or
                grass_y < 0 or grass_y > screen.get_height()):
                continue
            
            # Calculate wind effect
            wind_offset = math.sin(self.wind_time + grass["wind_offset"]) * 2
            end_x = grass_x + wind_offset
            end_y = grass_y - grass["height"]
            
            # Draw grass blade
            pygame.draw.line(screen, (34, 139, 34), (grass_x, grass_y), (end_x, end_y), 1)
    
    def _get_tile_color(self, terrain_type: TerrainType) -> Tuple[int, int, int]:
        """
        Retrieves the color for a given terrain type.

        Args:
            terrain_type (TerrainType): The type of terrain.

        Returns:
            Tuple[int, int, int]: The RGB color for the terrain.
        """
        colors = {
            TerrainType.GRASS: (34, 139, 34),
            TerrainType.DIRT: (139, 69, 19),
            TerrainType.SAND: (238, 203, 173),
            TerrainType.STONE: (128, 128, 128),
            TerrainType.SNOW: (255, 250, 250),
            TerrainType.LAVA: (255, 69, 0),
            TerrainType.WATER: (0, 100, 200)
        }
        return colors.get(terrain_type, (34, 139, 34))
    
    def get_collision_rects(self) -> List[pygame.Rect]:
        """
        Returns a list of all collision rectangles in the world.

        Returns:
            List[pygame.Rect]: A copy of the list of collision rectangles.
        """
        return self.collision_rects.copy()
    
    def get_world_time(self) -> Tuple[int, int, int]:
        """
        Gets the current in-game time.

        Returns:
            Tuple[int, int, int]: A tuple containing the current hour, minute, and day.
        """
        return (self._hours, int(self._minutes), self._days)
    
    def cleanup(self):
        """
        Cleans up world resources, clearing loaded chunks and other data.
        """
        self.loaded_chunks.clear()
        self.border_trees.clear()
        self.border_tiles.clear()
        self.collision_rects.clear()
        self.grass_blades.clear()
        logger.info("World cleanup completed")
    
    # Compatibility methods for old World class interface
    @property
    def seed(self) -> int:
        """Gets the world seed (for compatibility with older systems)."""
        return self._seed
    
    @property
    def width(self) -> int:
        """Gets the world width in tiles (for compatibility)."""
        return self.config.world_width
    
    @property
    def height(self) -> int:
        """Gets the world height in tiles (for compatibility)."""
        return self.config.world_height
    
    @property
    def hours(self) -> int:
        """Gets the current hour of the day (for compatibility)."""
        return self._hours
    
    @property
    def minutes(self) -> float:
        """Gets the current minute of the hour (for compatibility)."""
        return self._minutes
    
    @property
    def days(self) -> int:
        """Gets the current day count (for compatibility)."""
        return self._days
    
    @property
    def spawn_points(self) -> List[Tuple[int, int]]:
        """Gets spawn points for compatibility."""
        # Generate spawn points in the center of the world
        center_x = self.config.world_width // 2
        center_y = self.config.world_height // 2
        return [(center_x, center_y), (center_x + 1, center_y + 1)]
    
    @spawn_points.setter
    def spawn_points(self, value: List[Tuple[int, int]]):
        """Sets spawn points for compatibility (no-op in modern system)."""
        pass
    
    @property
    def graphics(self) -> Optional[SynapstexGraphics]:
        """Gets graphics reference for compatibility."""
        return getattr(self, '_graphics', None)
    
    @graphics.setter
    def graphics(self, value: SynapstexGraphics):
        """Sets graphics reference for compatibility."""
        self._graphics = value
    
    def get_centered_spawn(self) -> Tuple[int, int]:
        """Gets a centered spawn point for compatibility."""
        center_x = self.config.world_width // 2
        center_y = self.config.world_height // 2
        return (center_x, center_y)
    
    def init_grass(self):
        """Initializes grass for compatibility (no-op, done in constructor)."""
        pass
    
    def _generate_tile_variations(self, chunk):
        """Generates tile variations for compatibility (no-op in modern system)."""
        pass
    
    def get_day_phase(self) -> str:
        """
        Gets the current phase of the day (e.g., morning, day, night).

        Returns:
            str: The name of the current day phase.
        """
        if 6 <= self._hours < 12:
            return "morning"
        elif 12 <= self._hours < 18:
            return "day"
        elif 18 <= self._hours < 22:
            return "evening"
        else:
            return "night"
