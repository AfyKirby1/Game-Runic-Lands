"""
Modern World Generation System for Runic Lands

This module provides a clean, modern implementation of world generation
with proper color persistence, performance optimization, and separation of concerns.

Key Features:
- Fixed color flashing issue by storing colors in tree data
- Separated generation from rendering logic
- Performance optimizations with caching
- Type hints and proper error handling
- Modular design for easy testing and maintenance
"""

import random
import math
from typing import Dict, Tuple, List, Optional, NamedTuple
from dataclasses import dataclass
from enum import Enum, auto
import json
import os
from opensimplex import OpenSimplex


class BiomeType(Enum):
    """Biome types for world generation."""
    PLAINS = "plains"
    FOREST = "forest"
    DESERT = "desert"
    MOUNTAINS = "mountains"
    TUNDRA = "tundra"
    VOLCANIC = "volcanic"
    SWAMP = "swamp"


class TerrainType(Enum):
    """Terrain types for world generation."""
    GRASS = "grass"
    DIRT = "dirt"
    SAND = "sand"
    STONE = "stone"
    SNOW = "snow"
    LAVA = "lava"
    WATER = "water"


class TreeType(Enum):
    """Tree types for world generation."""
    OAK = 0
    PINE = 1
    MAPLE = 2


@dataclass
class ColorPalette:
    """Color palette for consistent tree coloring."""
    trunk_base: Tuple[int, int, int] = (101, 67, 33)
    trunk_shadow: Tuple[int, int, int] = (80, 50, 25)
    trunk_highlight: Tuple[int, int, int] = (120, 80, 40)
    
    # Autumn colors for border trees
    autumn_colors: List[Tuple[int, int, int]] = None
    
    # Regular forest colors
    forest_colors: List[Tuple[int, int, int]] = None
    
    def __post_init__(self):
        if self.autumn_colors is None:
            self.autumn_colors = [
                (34, 139, 34),   # Forest green
                (50, 150, 50),   # Darker green
                (255, 140, 0),   # Dark orange
                (255, 69, 0),    # Red-orange
                (220, 20, 60),   # Crimson red
                (255, 215, 0),   # Gold
                (184, 134, 11),  # Dark golden rod
                (139, 69, 19),   # Saddle brown
                (160, 82, 45),   # Saddle brown lighter
                (255, 99, 71)    # Tomato red
            ]
        
        if self.forest_colors is None:
            self.forest_colors = [
                (34, 139, 34),   # Forest green
                (50, 150, 50),   # Darker green  
                (60, 179, 113),  # Medium sea green
                (46, 125, 50)    # Dark green
            ]


@dataclass
class TreeData:
    """Immutable tree data structure with persistent colors."""
    x: int
    y: int
    tree_type: TreeType
    variant: int
    size_modifier: float
    depth_layer: int
    is_border: bool
    # Persistent colors - set once during generation
    leaf_color: Tuple[int, int, int]
    trunk_base_color: Tuple[int, int, int]
    trunk_shadow_color: Tuple[int, int, int]
    trunk_highlight_color: Tuple[int, int, int]
    is_extended: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "tree_type": self.tree_type.value,
            "variant": self.variant,
            "size_modifier": self.size_modifier,
            "depth_layer": self.depth_layer,
            "is_border": self.is_border,
            "is_extended": self.is_extended,
            "leaf_color": self.leaf_color,
            "trunk_base_color": self.trunk_base_color,
            "trunk_shadow_color": self.trunk_shadow_color,
            "trunk_highlight_color": self.trunk_highlight_color
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TreeData':
        """Create from dictionary."""
        return cls(
            x=data["x"],
            y=data["y"],
            tree_type=TreeType(data["tree_type"]),
            variant=data["variant"],
            size_modifier=data["size_modifier"],
            depth_layer=data["depth_layer"],
            is_border=data["is_border"],
            is_extended=data.get("is_extended", False),
            leaf_color=tuple(data["leaf_color"]),
            trunk_base_color=tuple(data["trunk_base_color"]),
            trunk_shadow_color=tuple(data["trunk_shadow_color"]),
            trunk_highlight_color=tuple(data["trunk_highlight_color"])
        )


@dataclass
class TileData:
    """Immutable tile data structure."""
    x: int
    y: int
    terrain_type: TerrainType
    elevation: float
    is_border: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "terrain_type": self.terrain_type.value,
            "elevation": self.elevation,
            "is_border": self.is_border
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TileData':
        """Create from dictionary."""
        return cls(
            x=data["x"],
            y=data["y"],
            terrain_type=TerrainType(data["terrain_type"]),
            elevation=data["elevation"],
            is_border=data.get("is_border", False)
        )


class ModernWorldChunk:
    """Modern world chunk with proper data structures and caching."""
    
    def __init__(self, x: int, y: int, size: int = 16):
        self.x = x
        self.y = y
        self.size = size
        self.tiles: List[TileData] = []
        self.trees: List[TreeData] = []
        self.structures: List[Dict] = []
        self.resources: List[Dict] = []
        self.biome: BiomeType = BiomeType.PLAINS
        self.elevation_map: List[List[float]] = []
        self.temperature_map: List[List[float]] = []
        self.moisture_map: List[List[float]] = []
        
        # Cached data for performance
        self._tile_variations: Dict[Tuple[int, int], Dict] = {}
        self._is_generated: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to serializable dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "size": self.size,
            "tiles": [tile.to_dict() for tile in self.tiles],
            "trees": [tree.to_dict() for tree in self.trees],
            "structures": self.structures,
            "resources": self.resources,
            "biome": self.biome.value,
            "tile_variations": {str(k): v for k, v in self._tile_variations.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModernWorldChunk':
        """Create from dictionary."""
        chunk = cls(data["x"], data["y"], data["size"])
        chunk.tiles = [TileData.from_dict(tile_data) for tile_data in data["tiles"]]
        chunk.trees = [TreeData.from_dict(tree_data) for tree_data in data["trees"]]
        chunk.structures = data["structures"]
        chunk.resources = data["resources"]
        chunk.biome = BiomeType(data["biome"])
        
        # Restore tile variations
        if "tile_variations" in data:
            for key_str, value in data["tile_variations"].items():
                key_str = key_str.strip("()").replace(" ", "")
                parts = key_str.split(",")
                if len(parts) == 2:
                    key = (int(parts[0]), int(parts[1]))
                    chunk._tile_variations[key] = value
        
        return chunk


class ModernWorldGenerator:
    """Modern world generator with proper separation of concerns."""
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.noise_gen = OpenSimplex(seed=self.seed)
        self.chunk_size = 16
        self.loaded_chunks: Dict[Tuple[int, int], ModernWorldChunk] = {}
        self.color_palette = ColorPalette()
        
        # World generation parameters
        self.elevation_scale = 50.0
        self.temperature_scale = 75.0
        self.moisture_scale = 60.0
        self.feature_scale = 25.0
        
        # Biome thresholds
        self.biome_thresholds = {
            BiomeType.TUNDRA: {"temp": -0.5, "moisture": -0.2},
            BiomeType.DESERT: {"temp": 0.5, "moisture": -0.3},
            BiomeType.PLAINS: {"temp": 0.2, "moisture": 0.0},
            BiomeType.FOREST: {"temp": 0.3, "moisture": 0.3},
            BiomeType.MOUNTAINS: {"temp": -0.2, "elevation": 0.6},
            BiomeType.VOLCANIC: {"temp": 0.7, "elevation": 0.7},
            BiomeType.SWAMP: {"temp": 0.1, "moisture": 0.6}
        }
    
    def get_chunk(self, chunk_x: int, chunk_y: int) -> ModernWorldChunk:
        """Get or generate a chunk at the given coordinates."""
        chunk_key = (chunk_x, chunk_y)
        if chunk_key not in self.loaded_chunks:
            self.loaded_chunks[chunk_key] = self._generate_chunk(chunk_x, chunk_y)
        return self.loaded_chunks[chunk_key]
    
    def _generate_chunk(self, chunk_x: int, chunk_y: int) -> ModernWorldChunk:
        """Generate a new chunk with modern data structures."""
        chunk = ModernWorldChunk(chunk_x, chunk_y, self.chunk_size)
        
        # Generate noise maps
        chunk.elevation_map = self._generate_noise_map(chunk_x, chunk_y, self.elevation_scale)
        chunk.temperature_map = self._generate_noise_map(chunk_x, chunk_y, self.temperature_scale)
        chunk.moisture_map = self._generate_noise_map(chunk_x, chunk_y, self.moisture_scale)
        
        # Determine biome
        avg_elevation = sum(sum(row) for row in chunk.elevation_map) / (self.chunk_size * self.chunk_size)
        avg_temp = sum(sum(row) for row in chunk.temperature_map) / (self.chunk_size * self.chunk_size)
        avg_moisture = sum(sum(row) for row in chunk.moisture_map) / (self.chunk_size * self.chunk_size)
        
        # Apply biome bias near origin
        distance_from_origin = math.sqrt(chunk_x**2 + chunk_y**2)
        if distance_from_origin < 3:
            if avg_temp < -0.2: avg_temp += 0.1
            if avg_temp > 0.6: avg_temp -= 0.1
            if avg_moisture < -0.2: avg_moisture += 0.1
            if avg_elevation > 0.5: avg_elevation -= 0.1
        
        chunk.biome = self._determine_biome(avg_temp, avg_moisture, avg_elevation)
        
        # Generate terrain and features
        self._generate_terrain(chunk)
        self._add_biome_features(chunk)
        self._add_resources(chunk)
        
        chunk._is_generated = True
        return chunk
    
    def _generate_noise_map(self, chunk_x: int, chunk_y: int, scale: float) -> List[List[float]]:
        """Generate a noise map for the chunk with edge smoothing."""
        noise_map = []
        for y in range(self.chunk_size):
            row = []
            for x in range(self.chunk_size):
                world_x = chunk_x * self.chunk_size + x
                world_y = chunk_y * self.chunk_size + y
                
                value = self.noise_gen.noise2(world_x / scale, world_y / scale)
                
                # Apply edge smoothing for chunk continuity
                if x < 2 or x > self.chunk_size - 3 or y < 2 or y > self.chunk_size - 3:
                    edge_samples = []
                    for dx in [-0.3, 0, 0.3]:
                        for dy in [-0.3, 0, 0.3]:
                            sample = self.noise_gen.noise2(
                                (world_x + dx) / scale,
                                (world_y + dy) / scale
                            )
                            edge_samples.append(sample)
                    
                    value = value * 0.6 + sum(edge_samples) / len(edge_samples) * 0.4
                
                row.append(value)
            noise_map.append(row)
        return noise_map
    
    def _determine_biome(self, temp: float, moisture: float, elevation: float) -> BiomeType:
        """Determine biome type based on environmental factors."""
        if elevation > self.biome_thresholds[BiomeType.MOUNTAINS]["elevation"]:
            if temp > self.biome_thresholds[BiomeType.VOLCANIC]["temp"]:
                return BiomeType.VOLCANIC
            else:
                return BiomeType.MOUNTAINS
        elif temp < self.biome_thresholds[BiomeType.TUNDRA]["temp"]:
            return BiomeType.TUNDRA
        elif temp > self.biome_thresholds[BiomeType.DESERT]["temp"] and \
             moisture < self.biome_thresholds[BiomeType.DESERT]["moisture"]:
            return BiomeType.DESERT
        elif moisture > self.biome_thresholds[BiomeType.SWAMP]["moisture"]:
            return BiomeType.SWAMP
        elif moisture > self.biome_thresholds[BiomeType.FOREST]["moisture"]:
            return BiomeType.FOREST
        else:
            return BiomeType.PLAINS
    
    def _generate_terrain(self, chunk: ModernWorldChunk):
        """Generate terrain tiles based on biome and noise maps."""
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                elevation = chunk.elevation_map[y][x]
                temperature = chunk.temperature_map[y][x]
                moisture = chunk.moisture_map[y][x]
                
                terrain_type = self._get_terrain_type(chunk.biome, elevation, temperature, moisture)
                
                tile = TileData(
                    x=chunk.x * self.chunk_size + x,
                    y=chunk.y * self.chunk_size + y,
                    terrain_type=terrain_type,
                    elevation=elevation
                )
                chunk.tiles.append(tile)
    
    def _get_terrain_type(self, biome: BiomeType, elevation: float, temperature: float, moisture: float) -> TerrainType:
        """Determine terrain type based on biome and conditions."""
        if biome == BiomeType.MOUNTAINS and elevation > 0.7:
            return TerrainType.STONE
        elif biome == BiomeType.DESERT:
            return TerrainType.SAND
        elif biome == BiomeType.TUNDRA:
            return TerrainType.SNOW
        elif biome == BiomeType.VOLCANIC and elevation > 0.8:
            return TerrainType.LAVA
        elif biome == BiomeType.SWAMP and elevation < -0.2:
            return TerrainType.WATER
        elif moisture > 0.6 and elevation < -0.3:
            return TerrainType.WATER
        elif elevation < -0.4:
            return TerrainType.DIRT
        else:
            return TerrainType.GRASS
    
    def _add_biome_features(self, chunk: ModernWorldChunk):
        """Add biome-specific features like trees."""
        if chunk.biome == BiomeType.FOREST:
            self._add_trees(chunk)
        elif chunk.biome == BiomeType.MOUNTAINS:
            self._add_rocks(chunk)
    
    def _add_trees(self, chunk: ModernWorldChunk, density: float = 0.15):
        """Add trees with persistent colors to prevent flashing."""
        tree_noise_map = self._generate_noise_map(chunk.x, chunk.y, self.feature_scale * 0.8)
        
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                tile_index = y * self.chunk_size + x
                if tile_index < len(chunk.tiles) and chunk.tiles[tile_index].terrain_type == TerrainType.GRASS:
                    feature_noise = tree_noise_map[y][x]
                    
                    if feature_noise > 0.4 and random.random() < density:
                        tree = self._create_tree(
                            chunk.x * self.chunk_size + x,
                            chunk.y * self.chunk_size + y,
                            is_border=False
                        )
                        chunk.trees.append(tree)
    
    def _create_tree(self, x: int, y: int, is_border: bool = False, depth_layer: int = 0, 
                    is_extended: bool = False) -> TreeData:
        """Create a tree with persistent colors to prevent flashing."""
        # Choose tree type
        if is_border:
            if depth_layer < 3:
                tree_type = random.choice([TreeType.OAK, TreeType.PINE, TreeType.MAPLE])
            elif depth_layer < 6:
                tree_type = random.choice([TreeType.OAK, TreeType.MAPLE])
            else:
                tree_type = TreeType.PINE
        else:
            tree_type = random.choice([TreeType.OAK, TreeType.PINE, TreeType.MAPLE])
        
        # Choose colors ONCE during generation
        if is_border:
            if depth_layer > 6:
                leaf_color = random.choice(self.color_palette.autumn_colors[:4])
            else:
                leaf_color = random.choice(self.color_palette.autumn_colors)
        else:
            leaf_color = random.choice(self.color_palette.forest_colors)
        
        # Size modifier
        size_modifier = 1.0
        if is_border and depth_layer < 3:
            size_modifier = 1.2
        elif is_border and depth_layer > 6:
            size_modifier = 0.8
        
        return TreeData(
            x=x,
            y=y,
            tree_type=tree_type,
            variant=tree_type.value,
            size_modifier=size_modifier,
            depth_layer=depth_layer,
            is_border=is_border,
            is_extended=is_extended,
            leaf_color=leaf_color,
            trunk_base_color=self.color_palette.trunk_base,
            trunk_shadow_color=self.color_palette.trunk_shadow,
            trunk_highlight_color=self.color_palette.trunk_highlight
        )
    
    def _add_rocks(self, chunk: ModernWorldChunk, density: float = 0.05):
        """Add rocks to the chunk."""
        for tile in chunk.tiles:
            if tile.terrain_type == TerrainType.STONE and random.random() < density:
                structure = {
                    "type": "rock",
                    "x": tile.x,
                    "y": tile.y,
                    "variant": random.randint(0, 2)
                }
                chunk.structures.append(structure)
    
    def _add_resources(self, chunk: ModernWorldChunk):
        """Add resources based on biome."""
        resource_chances = {
            BiomeType.MOUNTAINS: {
                "iron_ore": 0.02,
                "gold_ore": 0.01,
                "crystal": 0.005
            },
            BiomeType.FOREST: {
                "herb": 0.03,
                "mushroom": 0.02,
                "berry_bush": 0.01
            },
            BiomeType.DESERT: {
                "cactus": 0.01,
                "desert_flower": 0.005
            }
        }
        
        if chunk.biome in resource_chances:
            for tile in chunk.tiles:
                for resource, chance in resource_chances[chunk.biome].items():
                    if random.random() < chance:
                        resource_data = {
                            "type": resource,
                            "x": tile.x,
                            "y": tile.y,
                            "quantity": random.randint(1, 5)
                        }
                        chunk.resources.append(resource_data)
    
    def save_chunk(self, chunk: ModernWorldChunk, save_dir: str = "world/chunks"):
        """Save a chunk to disk."""
        os.makedirs(save_dir, exist_ok=True)
        filename = f"{save_dir}/chunk_{chunk.x}_{chunk.y}.json"
        with open(filename, 'w') as f:
            json.dump(chunk.to_dict(), f, indent=2)
    
    def load_chunk_from_dict(self, chunk_data: Dict) -> ModernWorldChunk:
        """Create a chunk from dictionary data."""
        return ModernWorldChunk.from_dict(chunk_data)
