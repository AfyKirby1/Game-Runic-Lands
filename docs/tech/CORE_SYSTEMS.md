# Core Systems Implementation

## 1. Inventory System
```python
class Inventory:
    def __init__(self, size: int = 20):
        self.size = size
        self.slots = [None] * size
        self.gold = 0
        
    def add_item(self, item):
        """Try to add item to first available slot"""
        for i in range(self.size):
            if self.slots[i] is None:
                self.slots[i] = item
                return True
        return False  # Inventory full

class EquipmentSlots:
    def __init__(self):
        self.slots = {
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
            'weapon': None,
            'offhand': None,
            'ring1': None,
            'ring2': None,
            'necklace': None
        }
```

### UI Layout
```
[Equipment]    [Inventory Grid]
 O  (head)     [1] [2] [3] [4] [5]
 |             [6] [7] [8] [9] [10]
/|\ (chest)    ... more slots ...
 |  
/ \ (legs)     [Gold: 0]
 ⅃ ⅂ (feet)    [Weight: 0/100]
```

## 2. Item Generation System
```python
class Item:
    def __init__(self):
        self.name = ""
        self.type = ""  # weapon, armor, consumable
        self.rarity = "common"
        self.level = 1
        self.stats = {}
        self.value = 0
        self.weight = 0

class ItemGenerator:
    def generate_item(self, level: int, item_type: str = None):
        item = Item()
        item.level = level
        # Scale stats based on level
        item.stats = self._generate_stats(level)
        # Add random properties based on rarity
        self._add_properties(item)
        return item
        
    def _generate_stats(self, level: int):
        """Generate base stats scaled to level"""
        base_stats = {
            'damage': 5 + (level * 2),
            'defense': 3 + (level * 1.5),
            'durability': 100
        }
        return base_stats
```

## 3. Rendering (Synapstex Graphics Engine)
- Handles drawing all game elements (tiles, entities, UI, particles).
- Uses a layer system (`RenderLayer` enum) for correct draw order.
- Supports basic particle effects via `ParticleSystem`.
- **NEW:** Implements a camera system (`set_camera_target`, `get_camera_offset`) to follow the player.
- Renders world elements relative to the camera offset.
- UI elements are drawn without camera offset.
- Caches surfaces for performance (`cached_surfaces`).
- Manages display mode (fullscreen, resolution, VSync).

## 4. World System (`systems/world.py`)
- Manages game world state: chunks, time, day/night cycle.
- Uses `SynapstexWorldGenerator` for procedural terrain generation.
- Handles chunk loading/unloading based on view distance (`_load_chunks_around`).
- Implements day/night cycle with lighting overlays and celestial bodies (`DayNightSystem`).
- Draws world tiles, structures, resources, and grass blades, applying camera offset.
- **UPDATED:** Resource drawing (`_draw_resource`) uses more descriptive shapes.
- Includes basic collision detection (`check_collision`).
- Manages world time (`update` method).

## 5. World Generation (`systems/world_generator.py`)
- Generates `WorldChunk` objects containing tiles, structures, etc.
- Uses OpenSimplex noise for elevation, temperature, and moisture maps.
- Determines biomes based on noise values and thresholds.
- **UPDATED:** Terrain generation (`_get_terrain_type`) creates varied terrain (grass, dirt, stone, etc.) based on biome and conditions (restored from previous grass-only state).
- Places features like trees and rocks based on biome and noise.
- Adds resources (ores, herbs) based on biome.
- Includes logic to bias starting chunks towards more favorable biomes.
- Supports saving/loading individual chunks (`save_chunk`, `load_chunk`).

## 6. Entity System (`entities/`)
- Base `Character` class (`entities/character.py`).
- `Player` class (`entities/player.py`) inherits from `Character`:
    - Handles player input (`move`).
    - Manages player state (position, velocity, stats, inventory).
    - **UPDATED:** Draw method (`draw`) now accepts and applies camera offset.
    - **NEW:** Flips sprite horizontally based on movement direction.
    - Includes health bar and level display.
    - Uses `Stats` system (`systems/stats.py`) for attributes.
- Placeholder for future `NPC` and `Enemy` classes.

## 7. Stats System (`systems/stats.py`)
- `Stats` class manages character attributes (HP, MP, strength, agility, etc.).
- Includes derived stats (attack, defense, speed) calculated from base stats.
- **UPDATED:** Player speed values adjusted for better gameplay feel.
- Handles leveling up (`level_up`) and experience gain (`add_exp`).
- Includes methods for taking damage, healing, and using/restoring MP.

## 8. Combat System (`systems/combat.py`)
- Basic `CombatSystem` class.
- Placeholder `handle_attack` method.
- **UPDATED:** Includes an `update` method (even if empty) to prevent crashes.
- Needs significant expansion for actual combat mechanics.

## 9. Inventory System (`systems/inventory.py`)
- `Item` class defines item properties (name, type, stats, etc.).
- `Inventory` class manages a list of items.
- `Equipment` class handles equipped items.
- `InventoryUI` class provides the visual interface:
    - Displays inventory slots, character preview, and stats.
    - **UPDATED:** Uses `visible` attribute instead of `is_visible`.
    - Handles item dragging and equipping.

## 10. UI Systems
- `MenuSystem` (`systems/menu.py`): Handles main menu navigation.
- `OptionsMenu` (`systems/options_menu.py`): Manages game settings UI.
    - **UPDATED:** State transitions and ESC key handling improved.
- `PauseMenu` (`systems/pause_menu.py`): Handles the in-game pause screen.
- Relies on `SynapstexGraphics` for drawing UI elements.

## 11. Options System (`systems/options.py`)
- Manages loading, saving, and applying game settings (video, audio, controls).
- Uses `config.json` for persistence.
- Provides methods to get/set specific options.
- Handles applying video setting changes (resolution, fullscreen, vsync).
- Manages music and sound effect playback.

## 12. Save/Load System (`systems/save_manager.py`)
- `SaveManager` handles saving and loading game state to/from JSON files.
- Supports multiple save slots.
- Includes basic error handling for corrupted or version-mismatched saves.
- Defines the structure for save game data.

## 13. Chunk System
```python
class Chunk:
    def __init__(self, x: int, y: int):
        self.x = x  # Chunk coordinates
        self.y = y
        self.size = 16  # 16x16 tiles
        self.tiles = [[None for _ in range(self.size)] 
                     for _ in range(self.size)]
        self.entities = []  # NPCs, monsters, etc.
        self.resources = []  # Gatherable resources
        self.structures = []  # Buildings, dungeons, etc.

class ChunkManager:
    def __init__(self):
        self.loaded_chunks = {}  # (x,y) -> Chunk
        self.view_distance = 2  # Chunks visible in each direction
        
    def get_chunk(self, x: int, y: int):
        """Get or generate chunk at coordinates"""
        key = (x, y)
        if key not in self.loaded_chunks:
            self.loaded_chunks[key] = self._generate_chunk(x, y)
        return self.loaded_chunks[key]
        
    def update_loaded_chunks(self, player_chunk_x: int, 
                           player_chunk_y: int):
        """Load/unload chunks based on player position"""
        # Load new chunks in view distance
        # Unload chunks outside view distance
        pass
```

## 14. Terrain Generation
```python
class TerrainGenerator:
    def __init__(self, seed: int):
        self.seed = seed
        self.noise = PerlinNoise()
        
    def generate_terrain(self, chunk_x: int, chunk_y: int):
        """Generate terrain for a chunk"""
        terrain = []
        for x in range(16):
            row = []
            for y in range(16):
                # Convert chunk coordinates to world coordinates
                world_x = chunk_x * 16 + x
                world_y = chunk_y * 16 + y
                
                # Generate height using noise
                height = self.noise.noise2d(
                    world_x / 50.0,
                    world_y / 50.0
                )
                
                # Determine tile type based on height
                tile_type = self._get_tile_type(height)
                row.append(tile_type)
            terrain.append(row)
        return terrain
```

**NOTE:** The actual implementation in `systems/world_generator.py` currently simplifies terrain generation to always return `GRASS`, overriding the height-based logic shown here. This affects features that depend on specific terrain types.

## 15. Biome System
```python
class BiomeManager:
    def __init__(self, seed: int):
        self.seed = seed
        self.temperature_noise = PerlinNoise()
        self.rainfall_noise = PerlinNoise()
        
    def get_biome(self, x: int, y: int):
        """Determine biome based on temperature and rainfall"""
        temp = self.temperature_noise.noise2d(x / 100.0, y / 100.0)
        rain = self.rainfall_noise.noise2d(x / 100.0, y / 100.0)
        
        return self._determine_biome(temp, rain)
        
    def _determine_biome(self, temp: float, rain: float):
        """Map temperature and rainfall to biome type"""
        if temp < -0.5:
            return Biome.TUNDRA
        elif temp > 0.5 and rain < -0.3:
            return Biome.DESERT
        elif rain > 0.3:
            return Biome.FOREST
        return Biome.PLAINS
```

## 16. Level Scaling System
```python
class LevelScaling:
    def __init__(self):
        self.base_difficulty = 1.0
        self.party_size_factor = 0.2  # 20% increase per party member
        self.distance_factor = 0.1  # 10% increase per chunk from start
        
    def calculate_monster_level(self, base_level: int, 
                              player_level: int,
                              distance_from_start: float,
                              party_size: int,
                              biome_difficulty: float):
        """Calculate scaled monster level"""
        # Start with base level
        level = base_level
        
        # Scale with player level
        level += (player_level - base_level) * 0.8
        
        # Apply distance scaling
        level += distance_from_start * self.distance_factor
        
        # Apply party size scaling
        level += (party_size - 1) * self.party_size_factor
        
        # Apply biome difficulty
        level *= biome_difficulty
        
        return round(max(1, level))
        
    def scale_monster_stats(self, monster, level: int):
        """Scale monster stats to level"""
        scale_factor = level / monster.base_level
        
        monster.health *= scale_factor
        monster.damage *= scale_factor
        monster.defense *= scale_factor
        
        return monster
```

## World Initialization and Spawn System

### Spawn Point Management
The game uses a sophisticated spawn point system that ensures players always start in suitable locations:

```python
class World:
    def get_centered_spawn(self) -> Tuple[int, int]:
        """Returns the spawn point closest to world center (0,0)."""
        
    def _generate_spawn_points(self, num_points: int = 4):
        """Generates multiple spawn points with one near center."""
```

#### Features
- **Center-Focused**: Primary spawn point always near world origin
- **Multiple Points**: Supports up to 4 spawn points for multiplayer
- **Safe Placement**: Points only generated on traversable terrain
- **Distance Control**: Maintains minimum spacing between points
- **Fallback System**: Defaults to (16, 16) if no valid spots found

### World Initialization Process
1. **World Creation**
   ```python
   world = World(seed=random.randint(0, 999999))
   ```
   - Generates initial chunks
   - Creates spawn points
   - Sets up environmental systems

2. **Player Spawning**
   ```python
   # Single Player
   spawn = world.get_centered_spawn()
   player = Player(*spawn, controls, world)
   
   # Multiplayer
   spawn1, spawn2 = world.spawn_points[:2]
   ```

3. **Chunk Loading**
   - Loads chunks around spawn point
   - Initializes terrain and features
   - Sets up collision data

### Integration with Game Modes

#### Single Player
- Uses `get_centered_spawn()` for optimal starting position
- Initializes necessary chunks around spawn
- Sets up player-specific systems

#### Local Co-op
- Distributes players across different spawn points
- Ensures fair starting distances
- Maintains shared world state

### Technical Implementation
- Spawn points stored as world coordinates
- Chunk-based validation system
- Efficient distance calculations
- Persistent spawn data in save files

These systems will interact with each other:
- Inventory system manages items generated by ItemGenerator
- ChunkManager uses TerrainGenerator and BiomeManager
- LevelScaling affects monsters in chunks based on various factors
- Items found in the world scale with the area's level 

## Menu System

The game uses a state-based menu system with the following key components:

### Menu States
- `GameState.MAIN_MENU`: Main menu screen
- `GameState.OPTIONS`: Options menu screen
- `GameState.SINGLE_PLAYER`: Single player game mode
- `GameState.LOCAL_COOP`: Local co-op game mode
- `GameState.QUIT`: Exit game state

### Options Menu States
- `OptionsMenuState.MAIN`: Main options screen
- `OptionsMenuState.VIDEO`: Video settings screen
- `OptionsMenuState.AUDIO`: Audio settings screen
- `OptionsMenuState.CONTROLS`: Controls settings screen
- `OptionsMenuState.REBIND`: Key rebinding screen

### State Transitions
The menu system handles state transitions carefully to ensure proper cleanup and initialization:

1. Main Menu → Options:
   - Stores previous state
   - Initializes options menu in MAIN state
   - Sets game mode to OPTIONS

2. Options → Main Menu:
   - Saves current settings
   - Resets options menu state to MAIN
   - Updates menu state and game mode synchronously
   - Recreates options menu to ensure clean state

3. Options → Pause Menu:
   - Saves current settings
   - Restores previous game mode
   - Shows pause menu
   - Resets from_pause_menu flag

### State Handling Best Practices
- Always reset menu states before transitioning
- Synchronize game mode and menu state changes
- Save settings before exiting options menu
- Recreate menu instances after major state changes
- Handle ESC key consistently across all states 