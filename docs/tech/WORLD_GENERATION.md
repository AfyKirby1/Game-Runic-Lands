# World Generation System

## Overview
The world generation system creates procedural terrain using noise-based algorithms and biome distribution. The system ensures a balanced starting area and consistent tree placement.

**Key Updates:**
- Terrain generation (`_get_terrain_type`) now produces varied terrain types based on biome conditions, resolving the previous issue where only grass was generated.
- Resource drawing (`_draw_resource` in `systems/world.py`) has been enhanced to show more distinct visual representations for different resource types (herbs, mushrooms, ores, etc.).

## Key Components

### Biome Generation
- Uses OpenSimplex noise for natural-looking terrain
- Biomes: Plains, Forest, Desert, Mountains, Tundra, Volcanic, Swamp
- Biome determination based on temperature, moisture, and elevation
- Special biome biasing near world origin (0,0) for better starting experience

### Spawn Point System
```python
def _generate_spawn_points(self, num_points: int = 4):
    """Generate potential spawn points, ensuring one is near the center."""
    # Ensures at least one spawn point near center (0,0)
    # Additional points generated in nearby chunks
    # All points placed on valid grass tiles
```

#### Spawn Point Features
- Primary spawn point guaranteed near world center
- Multiple spawn points for multiplayer support
- Minimum distance enforcement between spawn points
- Fallback to absolute center if no valid grass tiles found
- Points generated only on traversable terrain (grass tiles)

### Tree Generation
```python
def _add_trees(self, chunk: WorldChunk, density: float = 0.15):
    """Add trees based on biome and noise, ensuring spread."""
    # Uses separate noise map for natural distribution
    # Increased density for better forest feel
    # Trees only placed on grass tiles
```

#### Tree Placement Features
- Separate noise map for natural distribution
- Adjusted density parameters for fuller forests
- Biome-specific placement rules
- Proper spacing between trees
- Enhanced visual variety through variants

### Resource Generation
- Resources (`iron_ore`, `herb`, etc.) are added based on biome and random chance.
- **UPDATED:** Visual representation of resources handled by `_draw_resource` in `systems/world.py`.

## World Initialization

### Center-Focused Generation
```python
def get_centered_spawn(self) -> Tuple[int, int]:
    """Return the spawn point closest to the world center."""
    # Calculates distances from (0,0)
    # Returns closest valid spawn point
```
- **NOTE:** While spawn logic aims for center, the *view* is now centered on the player via the camera system in `SynapstexGraphics`.

### Chunk Loading
- Initial chunks loaded around spawn point
- View distance system for dynamic loading
- Chunk persistence for explored areas
- Smooth transitions between chunks

## Technical Details

### Biome Biasing
- Modifies noise values near the origin (0,0) to slightly favor Plains/Forest conditions.
- Prevents overly harsh starting environments (e.g., spawning directly in Lava or deep Water).

### Noise Map Generation
- Uses `OpenSimplex` library.
- Generates separate maps for elevation, temperature, and moisture.
- Includes edge smoothing logic (`_generate_noise_map`) to improve continuity between chunks.

### Terrain Typing
- `_get_terrain_type` function determines the specific tile (Grass, Dirt, Stone, etc.) based on biome and noise values.
- Restored complex logic to generate varied terrain.

## Usage

### Single Player
```python
# Get centered spawn point for single player
spawn = world.get_centered_spawn()
player = Player(*spawn, controls, world)
```

### Multiplayer
```python
# Get multiple spawn points for co-op
spawn1, spawn2 = world.spawn_points[:2]
player1 = Player(*spawn1, p1_controls, world)
player2 = Player(*spawn2, p2_controls, world)
```

## Future Enhancements
- [ ] Dynamic biome transitions
- [ ] More varied tree types per biome
- [ ] Enhanced resource distribution
- [ ] Advanced terrain features
- [ ] Improved spawn point selection for larger groups 