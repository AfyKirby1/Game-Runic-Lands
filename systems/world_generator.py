import random
from typing import Dict, Tuple, List
import json
import os
from opensimplex import OpenSimplex
import math

class BiomeType:
    PLAINS = "plains"
    FOREST = "forest"
    DESERT = "desert"
    MOUNTAINS = "mountains"
    TUNDRA = "tundra"
    VOLCANIC = "volcanic"
    SWAMP = "swamp"

class TerrainType:
    GRASS = "grass"
    DIRT = "dirt"
    SAND = "sand"
    STONE = "stone"
    SNOW = "snow"
    LAVA = "lava"
    WATER = "water"

class WorldChunk:
    def __init__(self, x: int, y: int, size: int = 16):
        self.x = x
        self.y = y
        self.size = size
        self.tiles: List[Dict] = []
        self.entities: List[Dict] = []
        self.structures: List[Dict] = []
        self.resources: List[Dict] = []
        self.biome: str = BiomeType.PLAINS
        self.elevation_map: List[List[float]] = []
        self.temperature_map: List[List[float]] = []
        self.moisture_map: List[List[float]] = []
        self.tile_variations = {}  # Store static tile variations for rendering

    def to_dict(self) -> dict:
        # Convert tile_variations to a serializable format
        # Since dictionary keys can't be tuples in JSON, we need to convert them to strings
        serializable_variations = {}
        if hasattr(self, "tile_variations") and self.tile_variations:
            for key, value in self.tile_variations.items():
                serializable_variations[str(key)] = value
                
        return {
            "x": self.x,
            "y": self.y,
            "size": self.size,
            "tiles": self.tiles,
            "entities": self.entities,
            "structures": self.structures,
            "resources": self.resources,
            "biome": self.biome,
            "tile_variations": serializable_variations
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WorldChunk':
        chunk = cls(data["x"], data["y"], data["size"])
        chunk.tiles = data["tiles"]
        chunk.entities = data["entities"]
        chunk.structures = data["structures"]
        chunk.resources = data["resources"]
        chunk.biome = data["biome"]
        
        # Restore tile_variations if present
        if "tile_variations" in data:
            chunk.tile_variations = {}
            for key_str, value in data["tile_variations"].items():
                # Convert string key back to tuple
                # Strip parentheses and split by comma
                key_str = key_str.strip("()").replace(" ", "")
                parts = key_str.split(",")
                if len(parts) == 2:
                    key = (int(parts[0]), int(parts[1]))
                    chunk.tile_variations[key] = value
                
        return chunk

class SynapstexWorldGenerator:
    def __init__(self, seed: int = None):
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.noise_gen = OpenSimplex(seed=self.seed)
        self.chunk_size = 16
        self.loaded_chunks: Dict[Tuple[int, int], WorldChunk] = {}
        
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

    def get_chunk(self, chunk_x: int, chunk_y: int) -> WorldChunk:
        """Get or generate a chunk at the given coordinates"""
        chunk_key = (chunk_x, chunk_y)
        if chunk_key not in self.loaded_chunks:
            self.loaded_chunks[chunk_key] = self._generate_chunk(chunk_x, chunk_y)
        return self.loaded_chunks[chunk_key]

    def _generate_chunk(self, chunk_x: int, chunk_y: int) -> WorldChunk:
        """Generate a new chunk at the given coordinates"""
        chunk = WorldChunk(chunk_x, chunk_y, self.chunk_size)
        
        # Generate base noise maps
        chunk.elevation_map = self._generate_noise_map(chunk_x, chunk_y, self.elevation_scale)
        chunk.temperature_map = self._generate_noise_map(chunk_x, chunk_y, self.temperature_scale)
        chunk.moisture_map = self._generate_noise_map(chunk_x, chunk_y, self.moisture_scale)
        
        # Determine chunk's primary biome
        avg_elevation = sum(sum(row) for row in chunk.elevation_map) / (self.chunk_size * self.chunk_size)
        avg_temp = sum(sum(row) for row in chunk.temperature_map) / (self.chunk_size * self.chunk_size)
        avg_moisture = sum(sum(row) for row in chunk.moisture_map) / (self.chunk_size * self.chunk_size)
        
        # --- Biome Bias near Origin (0,0) ---
        distance_from_origin = math.sqrt(chunk_x**2 + chunk_y**2)
        if distance_from_origin < 3: # Bias chunks within 3 chunk distance of origin
            # Gently push towards Plains/Forest conditions if extreme
            if avg_temp < -0.2: avg_temp += 0.1 # Reduce extreme cold
            if avg_temp > 0.6: avg_temp -= 0.1 # Reduce extreme heat
            if avg_moisture < -0.2: avg_moisture += 0.1 # Reduce extreme dry
            if avg_elevation > 0.5: avg_elevation -= 0.1 # Reduce extreme height
        # --- End Biome Bias ---
            
        chunk.biome = self._determine_biome(avg_temp, avg_moisture, avg_elevation)
        
        # Generate terrain based on biome and noise maps
        self._generate_terrain(chunk)
        
        # Add biome-specific features (modified tree placement)
        self._add_biome_features(chunk)
        
        # Add resources
        self._add_resources(chunk)
        
        return chunk

    def _generate_noise_map(self, chunk_x: int, chunk_y: int, scale: float) -> List[List[float]]:
        """Generate a noise map for the chunk"""
        noise_map = []
        for y in range(self.chunk_size):
            row = []
            for x in range(self.chunk_size):
                # Convert chunk coordinates to world coordinates
                world_x = chunk_x * self.chunk_size + x
                world_y = chunk_y * self.chunk_size + y
                
                # Generate noise value with some smoothing for chunk edges
                value = self.noise_gen.noise2(
                    world_x / scale,
                    world_y / scale
                )
                
                # Apply additional smoothing and continuity at chunk edges
                # This helps ensure continuous terrain across chunk boundaries
                if x < 2 or x > self.chunk_size - 3 or y < 2 or y > self.chunk_size - 3:
                    # Add additional noise samples and average them for smoother edges
                    edge_samples = []
                    for dx in [-0.3, 0, 0.3]:
                        for dy in [-0.3, 0, 0.3]:
                            sample = self.noise_gen.noise2(
                                (world_x + dx) / scale,
                                (world_y + dy) / scale
                            )
                            edge_samples.append(sample)
                    
                    # Weight the original value more, but blend in the edge samples
                    value = value * 0.6 + sum(edge_samples) / len(edge_samples) * 0.4
                
                row.append(value)
            noise_map.append(row)
        return noise_map

    def _determine_biome(self, temp: float, moisture: float, elevation: float) -> str:
        """Determine the biome type based on temperature, moisture, and elevation"""
        if elevation > self.biome_thresholds[BiomeType.MOUNTAINS]["elevation"]:
            if temp > self.biome_thresholds[BiomeType.VOLCANIC]["temp"]:
                return BiomeType.VOLCANIC
            return BiomeType.MOUNTAINS
            
        if temp < self.biome_thresholds[BiomeType.TUNDRA]["temp"]:
            return BiomeType.TUNDRA
            
        if temp > self.biome_thresholds[BiomeType.DESERT]["temp"] and \
           moisture < self.biome_thresholds[BiomeType.DESERT]["moisture"]:
            return BiomeType.DESERT
            
        if moisture > self.biome_thresholds[BiomeType.SWAMP]["moisture"]:
            return BiomeType.SWAMP
            
        if moisture > self.biome_thresholds[BiomeType.FOREST]["moisture"]:
            return BiomeType.FOREST
            
        return BiomeType.PLAINS

    def _generate_terrain(self, chunk: WorldChunk):
        """Generate terrain tiles based on biome and noise maps"""
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                # Get noise values
                elevation = chunk.elevation_map[y][x]
                temperature = chunk.temperature_map[y][x]
                moisture = chunk.moisture_map[y][x]
                
                # Determine terrain type based on biome and conditions
                terrain_type = self._get_terrain_type(chunk.biome, elevation, temperature, moisture)
                
                # Create tile data
                tile = {
                    "x": chunk.x * self.chunk_size + x,
                    "y": chunk.y * self.chunk_size + y,
                    "type": terrain_type,
                    "elevation": elevation
                }
                chunk.tiles.append(tile)

    def _get_terrain_type(self, biome: str, elevation: float, temperature: float, moisture: float) -> str:
        """Determine terrain type based on biome and conditions"""
        # Original code restored - generate varied terrain instead of only grass
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

    def _add_biome_features(self, chunk: WorldChunk):
        """Add biome-specific features like trees, rocks, etc."""
        if chunk.biome == BiomeType.FOREST:
            self._add_trees(chunk)
        elif chunk.biome == BiomeType.MOUNTAINS:
            self._add_rocks(chunk)
        # Add more biome-specific features as needed

    def _add_trees(self, chunk: WorldChunk, density: float = 0.15): # Increased density slightly
        """Add trees based on biome and noise, ensuring spread"""
        # Use a different noise scale for features like trees
        tree_noise_map = self._generate_noise_map(chunk.x, chunk.y, self.feature_scale * 0.8) # Slightly different scale
        
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                # Check if the tile is grass
                tile_index = y * self.chunk_size + x
                if tile_index < len(chunk.tiles) and chunk.tiles[tile_index]["type"] == TerrainType.GRASS:
                    feature_noise = tree_noise_map[y][x]
                    
                    # Use noise and density check for placement
                    # Adjust threshold for desired density (lower = more trees)
                    if feature_noise > 0.4 and random.random() < density:
                        tree = {
                            "x": chunk.x * self.chunk_size + x,
                            "y": chunk.y * self.chunk_size + y,
                            "type": "tree"
                        }
                        chunk.entities.append(tree)

    def _add_rocks(self, chunk: WorldChunk, density: float = 0.05):
        """Add rocks to the chunk"""
        for tile in chunk.tiles:
            if tile["type"] == TerrainType.STONE and random.random() < density:
                structure = {
                    "type": "rock",
                    "x": tile["x"],
                    "y": tile["y"],
                    "variant": random.randint(0, 2)  # Different rock variants
                }
                chunk.structures.append(structure)

    def _add_resources(self, chunk: WorldChunk):
        """Add resources based on biome and elevation"""
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
                            "x": tile["x"],
                            "y": tile["y"],
                            "quantity": random.randint(1, 5)
                        }
                        chunk.resources.append(resource_data)

    def save_chunk(self, chunk: WorldChunk, save_dir: str = "world/chunks"):
        """Save a chunk to disk"""
        os.makedirs(save_dir, exist_ok=True)
        filename = f"{save_dir}/chunk_{chunk.x}_{chunk.y}.json"
        with open(filename, 'w') as f:
            json.dump(chunk.to_dict(), f, indent=2)

    def load_chunk(self, chunk_x: int, chunk_y: int, save_dir: str = "world/chunks") -> WorldChunk:
        """Load a chunk from disk"""
        filename = f"{save_dir}/chunk_{chunk_x}_{chunk_y}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                return WorldChunk.from_dict(data)
        return self._generate_chunk(chunk_x, chunk_y)
    
    def load_chunk_from_dict(self, chunk_data: dict) -> WorldChunk:
        """
        Create a chunk from dictionary data without file I/O.
        
        This method is primarily used by the save/load system to reconstruct
        world chunks from saved game state. Unlike load_chunk(), it doesn't 
        require disk access and works directly with serialized data.
        
        Args:
            chunk_data: A dictionary containing serialized chunk data
            
        Returns:
            WorldChunk: A reconstructed world chunk object
            
        See Also:
            - save_manager.py: For the complete save/load system implementation
            - docs/save_system.md: For documentation on the save/load system
        """
        return WorldChunk.from_dict(chunk_data) 