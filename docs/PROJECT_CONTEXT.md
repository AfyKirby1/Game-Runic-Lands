# Runic Lands Project Context

## Project Overview

Runic Lands is a 2D action RPG built with Python and Pygame featuring:
- Procedural world generation
- Local co-op multiplayer
- Inventory and item management 
- Day/night cycle with visual effects
- Combat system

The project follows a modular architecture with discrete systems handling different aspects of gameplay.

## Current State of Development

The project is in early development (v0.1), with approximately 50% of core engine functionality complete. The codebase has recently undergone significant refactoring to improve organization and maintainability.

### Recent Development Work

#### Major Refactoring

1. **Reorganized Directory Structure**:
   - `src/systems/` - Core game systems 
   - `src/ui/` - UI components separated by category (menu, hud, widgets)
   - `src/assets/` - Asset management
   - `src/config/` - Configuration handling
   - `src/entities/` - Game entities

2. **New Core Architecture**:
   - **State Manager**: A dedicated system that handles transitions between different game states (menu, playing, paused, etc.)
   - **Asset Manager**: Centralizes loading and caching of game assets
   - **Config Manager**: Handles loading/saving configuration with proper defaults
   - **Improved Synapstex Graphics Engine**: Enhanced with display management capabilities including fullscreen toggle

3. **UI Improvements**:
   - UI components moved to their own modules
   - Options menu now includes video settings with fullscreen toggle
   - Pause screen implementation

#### Recent Feature Implementations

1. **Save/Load System**: A robust system with corruption detection, versioning, and backup functionality
2. **Pause Menu System**: Integrating save/load functionality with a working UI
3. **Video Settings**: Added fullscreen toggle and resolution options
4. **Fixed Escape Key Handling**: Properly implemented state transitions for the pause menu

## Key Features

- **World Generation**: Procedural terrain generation with different biomes and features
- **Player Movement**: Character controls with collision detection
- **Day/Night Cycle**: Time system with visual effects
- **Inventory System**: Item collection and management
- **Save/Load System**: Game state persistence with corruption protection
- **Pause Menu**: Game can be paused with a menu for save/load/options/quit
- **Options System**: Configurable controls, audio, and video settings

## Key Systems and Components

### State Management (`src/systems/state_manager.py`)

The newly implemented state manager provides:
- Clear separation between different game states
- Proper event handling for each state
- State transition with enter/exit hooks
- Support for state stacking (e.g., pause menu → options → back to pause)

### Save/Load System (`systems/save_manager.py`)

The save system features:
- **Data integrity protection**: SHA-256 checksums verify file integrity
- **Version tracking**: Compatibility with future game versions
- **Automatic backups**: Preserves player progress in case of corruption
- **Compression**: Reduces save file size
- **Serialization mechanism**: Game objects implement `to_dict()` and `from_dict()` methods

### Asset Management (`src/assets/asset_manager.py`)

The new asset management system:
- Centralizes asset loading and caching
- Manages sprites, sounds, music, and fonts
- Provides fallbacks for missing assets
- Handles volume control and music transitions

### Configuration (`src/config/config_manager.py`)

The new configuration system:
- Maintains user settings with proper defaults
- Saves/loads configuration from disk
- Handles special types (like resolution tuples)
- Provides callback mechanisms for settings changes

### World Generation (`systems/world_generator.py`)

The Synapstex WRLDs system generates procedural terrain with:
- **Chunk-based approach**: 16x16 tile chunks loaded dynamically
- **Biome system**: Various biome types (Plains, Forest, Desert, Mountains, etc.)
- **Noise-based generation**: Uses OpenSimplex noise for natural terrain
- **Resource distribution**: Biome-specific resources with varying rarity
- **Structure generation**: Trees, rocks, and other features based on biome

### Graphics Engine (`systems/synapstex.py`)

The Synapstex Graphics Engine provides:
- Multiple rendering layers
- Particle system
- UI rendering capabilities
- Primitive shape drawing
- Text rendering with font management
- Display management with fullscreen toggle

## Technical Implementation

- **Graphics Engine**: Custom Synapstex engine built on top of Pygame
- **State Management**: Event-driven architecture with state transitions
- **Configuration**: JSON-based settings with defaults and user overrides
- **Asset Pipeline**: Centralized asset loading with caching for performance
- **Serialization**: Game objects implement to_dict() and from_dict() methods for saving/loading

## Game Controls

- **Movement**: WASD or arrow keys
- **Inventory**: E key
- **Attack**: Space
- **Pause**: Escape

## Code Style and Conventions

- **Classes**: CamelCase (e.g., `PauseMenu`, `SaveManager`)
- **Functions/Methods**: snake_case (e.g., `handle_input`, `load_game`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `SAVE_VERSION`, `SCREEN_WIDTH`)
- **Private Methods**: Prefixed with underscore (e.g., `_create_metadata`)

## Project Structure (After Refactoring)

```
runiclands/
├── assets/           # Game assets (sprites, textures, audio)
├── docs/             # Documentation files
│   ├── PROJECT_CONTEXT.md # Project context for developers
│   ├── PAUSE_MENU.md     # Pause menu documentation
│   ├── PROJECT_STRUCTURE.md # Project organization
│   ├── README.md         # Documentation index
│   ├── WORLD_GENERATION.md # World generation documentation
│   └── save_system.md    # Save system documentation
├── src/              # Source code (new structure)
│   ├── assets/       # Asset management
│   ├── config/       # Configuration management
│   ├── entities/     # Game entity classes
│   ├── systems/      # Core game systems
│   ├── ui/           # UI components
│   │   ├── hud/      # In-game HUD elements
│   │   ├── menu/     # Menu screens (pause, main, options)
│   │   └── widgets/  # Reusable UI components
│   └── utils/        # Utility functions
├── maps/             # Game world maps
├── CHANGELOG.md      # Version history
├── README.md         # Project overview
├── ROADMAP.md        # Development roadmap
└── requirements.txt  # Python dependencies
```

## Documentation

The project maintains comprehensive documentation:
- **README.md**: Overview of the entire project
- **docs/PROJECT_STRUCTURE.md**: Details of the codebase organization
- **docs/WORLD_GENERATION.md**: Explains the procedural generation system
- **docs/save_system.md**: Documents the save/load functionality
- **docs/PAUSE_MENU.md**: Details the pause menu implementation
- **docs/PROJECT_CONTEXT.md**: Project context for developers
- **ROADMAP.md**: Outlines planned features and development timeline
- **CHANGELOG.md**: Records version history and changes

## Serialization

To support saving and loading, game objects implement serialization methods:

- **to_dict()**: Converts object state to a dictionary
- **from_dict()**: Reconstructs object state from a dictionary

Example from `WorldChunk`:
```python
def to_dict(self) -> dict:
    return {
        "x": self.x,
        "y": self.y,
        "size": self.size,
        "tiles": self.tiles,
        "entities": self.entities,
        "structures": self.structures,
        "resources": self.resources,
        "biome": self.biome
    }

@classmethod
def from_dict(cls, data: dict) -> 'WorldChunk':
    chunk = cls(data["x"], data["y"], data["size"])
    chunk.tiles = data["tiles"]
    chunk.entities = data["entities"]
    chunk.structures = data["structures"]
    chunk.resources = data["resources"]
    chunk.biome = data["biome"]
    return chunk
```

## Current Development Focus

- **Refactoring**: Improving code organization for better maintainability
- **UI Enhancements**: Making menus more user-friendly
- **Performance Optimization**: Ensuring smooth gameplay
- **Content Development**: Add more biomes, structures, and gameplay features

## Development Roadmap and Next Steps

According to the roadmap, the project is progressing through v0.1 (Basic Engine) and will soon move to v0.2 (Core Gameplay). Current progress:

- **Completed**:
  - Basic 2D game engine
  - Local co-op functionality
  - Basic combat system
  - Health system with visual bars
  - Player collision detection
  - Basic map loading
  - Save/Load functionality
  - Menu system
  - Configuration options

- **Upcoming priorities**:
  1. **Character Sprites**: Improved visual representation
  2. **Tile-based Maps**: Enhanced world representation
  3. **Basic Animations**: More fluid visual feedback
  4. **UI Elements**: Better user interface
  5. **Improved Combat System**: More engaging gameplay
  6. **Character Classes**: Player progression and specialization
  7. **Collision Improvement**: Better interaction with world objects

## Known Issues

- Some texture issues when loading saved games
- Particle system needs optimization
- Screen transitions between states need improvement

## Getting Started for Development

1. **Setup Environment**:
   ```
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Run the Game**:
   ```
   python main.py
   ```

3. **Key Files to Review First**:
   - `src/main.py`: Understand the game loop and system initialization
   - `src/systems/state_manager.py`: Review the state management system
   - `src/assets/asset_manager.py`: Understand asset loading and caching
   - `src/config/config_manager.py`: Review configuration handling
   - `systems/save_manager.py`: Review the save/load mechanism
   - `systems/world.py`: Understand world management
   - `systems/world_generator.py`: Review procedural generation
   - `docs/*.md`: Read the detailed documentation 