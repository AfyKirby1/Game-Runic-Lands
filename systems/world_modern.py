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
    """Configuration for the world system."""
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
    """Modern world system with fixed flashing trees and better performance."""
    
    def __init__(self, config: Optional[WorldConfig] = None, seed: Optional[int] = None):
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
        """Update world state including time, wind, and particles."""
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
            if graphics and random.random() < 0.01:  # 1% chance per frame
                self._emit_environmental_particles(graphics)
                
        except Exception as e:
            logger.error(f"Error updating world: {e}", exc_info=True)
    
    def get_chunk(self, chunk_x: int, chunk_y: int) -> ModernWorldChunk:
        """Get or generate a chunk at the given coordinates."""
        chunk_key = (chunk_x, chunk_y)
        if chunk_key not in self.loaded_chunks:
            self.loaded_chunks[chunk_key] = self.generator.get_chunk(chunk_x, chunk_y)
        return self.loaded_chunks[chunk_key]
    
    def update_chunks(self, player_x: int, player_y: int):
        """Update loaded chunks around player position."""
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
        """Draw the world with camera offset."""
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
        """Generate forest border with persistent colors."""
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
        """Check if position is in the border area."""
        return (x < min_x or x > max_x or y < min_y or y > max_y) and \
               (min_x - depth <= x <= max_x + depth and min_y - depth <= y <= max_y + depth)
    
    def _calculate_depth_layer(self, x: int, y: int, min_x: int, max_x: int, min_y: int, max_y: int) -> int:
        """Calculate depth layer for border position."""
        dist_from_edge = min(
            abs(x - min_x), abs(x - max_x),
            abs(y - min_y), abs(y - max_y)
        )
        return min(dist_from_edge, 10)  # Cap at 10
    
    def _is_extended_position(self, x: int, y: int, min_x: int, max_x: int, min_y: int, max_y: int, depth: int) -> bool:
        """Check if position is in extended forest area."""
        return (x < min_x - depth or x > max_x + depth or 
                y < min_y - depth or y > max_y + depth)
    
    def _generate_initial_grass(self):
        """Generate initial grass blades."""
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
        """Update grass wind animation."""
        for grass in self.grass_blades:
            grass["angle"] += dt * 0.5  # Gentle swaying
    
    def _emit_environmental_particles(self, graphics: SynapstexGraphics):
        """Emit environmental particles like falling leaves."""
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
        """Draw border ground tiles."""
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
        """Draw loaded world chunks."""
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
        """Draw border trees with persistent colors."""
        offset_x, offset_y = offset
        
        for tree in self.border_trees:
            tree_screen_x = tree.x * self.config.tile_size - offset_x
            tree_screen_y = tree.y * self.config.tile_size - offset_y
            
            if (tree_screen_x + self.config.tile_size < 0 or tree_screen_x > screen.get_width() or
                tree_screen_y + self.config.tile_size < 0 or tree_screen_y > screen.get_height()):
                continue
            
            self.tree_renderer.render_tree(screen, tree, (tree_screen_x, tree_screen_y))
    
    def _draw_grass(self, screen: pygame.Surface, offset: Tuple[float, float]):
        """Draw grass blades."""
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
        """Get color for terrain type."""
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
        """Get collision rectangles for the world."""
        return self.collision_rects.copy()
    
    def get_world_time(self) -> Tuple[int, int, int]:
        """Get current world time (hours, minutes, days)."""
        return (self._hours, int(self._minutes), self._days)
    
    def cleanup(self):
        """Clean up resources."""
        self.loaded_chunks.clear()
        self.border_trees.clear()
        self.border_tiles.clear()
        self.collision_rects.clear()
        self.grass_blades.clear()
        logger.info("World cleanup completed")
    
    # Compatibility methods for old World class interface
    @property
    def seed(self) -> int:
        """Get world seed for compatibility."""
        return self._seed
    
    @property
    def width(self) -> int:
        """Get world width in tiles for compatibility."""
        return self.config.world_width
    
    @property
    def height(self) -> int:
        """Get world height in tiles for compatibility."""
        return self.config.world_height
    
    @property
    def hours(self) -> int:
        """Get current hour for compatibility."""
        return self._hours
    
    @property
    def minutes(self) -> float:
        """Get current minutes for compatibility."""
        return self._minutes
    
    @property
    def spawn_points(self) -> List[Tuple[int, int]]:
        """Get spawn points for compatibility."""
        # Generate spawn points in the center of the world
        center_x = self.config.world_width // 2
        center_y = self.config.world_height // 2
        return [(center_x, center_y), (center_x + 1, center_y + 1)]
    
    @spawn_points.setter
    def spawn_points(self, value: List[Tuple[int, int]]):
        """Set spawn points for compatibility (no-op in modern system)."""
        pass
    
    @property
    def graphics(self) -> Optional[SynapstexGraphics]:
        """Get graphics reference for compatibility."""
        return getattr(self, '_graphics', None)
    
    @graphics.setter
    def graphics(self, value: SynapstexGraphics):
        """Set graphics reference for compatibility."""
        self._graphics = value
    
    def get_centered_spawn(self) -> Tuple[int, int]:
        """Get centered spawn point for compatibility."""
        center_x = self.config.world_width // 2
        center_y = self.config.world_height // 2
        return (center_x, center_y)
    
    def init_grass(self):
        """Initialize grass for compatibility (already done in constructor)."""
        pass
    
    def _generate_tile_variations(self, chunk):
        """Generate tile variations for compatibility (no-op in modern system)."""
        pass
