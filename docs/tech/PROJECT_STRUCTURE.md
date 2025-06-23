# Runic Lands Project Structure

## Overview
This document outlines the organization of the Runic Lands project, explaining the purpose of each directory and key files.

## Directory Structure

```
runiclands/
├── assets/           # Game assets (sprites, textures, audio)
├── docs/             # Documentation files
├── entities/         # Game entity classes
│   ├── character.py  # Base character class
│   └── player.py     # Player implementation
├── maps/             # Game world maps
├── systems/          # Core game systems
│   ├── combat.py     # Combat mechanics
│   ├── inventory.py  # Inventory and items
│   ├── menu.py       # Main menu
│   ├── options.py    # Game settings
│   ├── options_menu.py # Options UI
│   ├── pause_menu.py # Pause screen
│   ├── save_manager.py # Save/load system
│   ├── sprite.py     # Sprite handling
│   ├── synapstex.py  # Graphics engine
│   ├── world.py      # World management
│   └── world_generator.py # Procedural generation
├── utils/            # Utility functions
├── .gitignore        # Git ignore file
├── CHANGELOG.md      # Version history
├── config.json       # Game configuration
├── create_shortcut.ps1 # Windows shortcut creator
├── generate_*.py     # Asset generation scripts
├── launch_game.bat   # Windows launcher
├── main.py           # Main game entry point
├── README.md         # Project overview
├── requirements.txt  # Python dependencies
├── ROADMAP.md        # Development roadmap
└── SUGGESTIONS.md    # Feature suggestions
```

## Main Modules

### Game Entry Point
- **main.py**: The primary entry point containing the Game class that initializes all systems and runs the main game loop.

### Core Systems
- **systems/**: Contains all the major game subsystems:
  - **combat.py**: Handles combat mechanics and damage calculations
  - **inventory.py**: Manages items, inventory storage, and UI
  - **menu.py**: Main menu interface and state management
  - **options.py**: Stores and retrieves game settings
  - **options_menu.py**: UI for changing game options
  - **pause_menu.py**: In-game pause screen
  - **save_manager.py**: Complete save/load system with versioning and corruption protection
  - **sprite.py**: Sprite loading and animation
  - **synapstex.py**: Graphics rendering engine
  - **world.py**: World state and interaction
  - **world_generator.py**: Procedural world generation

### Entities
- **entities/**: Game character implementations
  - **character.py**: Base character class with common behaviors
  - **player.py**: Player-specific implementation

### Asset Generation
- **generate_*.py**: Python scripts for procedurally generating game assets
  - **generate_assets.py**: Main asset generation coordinator
  - **generate_audio.py**: Generates game audio
  - **generate_base_sprite.py**: Creates base character sprites
  - **generate_walking_sprite.py**: Generates walking animations
  - **generate_attack_sprite.py**: Creates attack animations

### Documentation
- **docs/**: Comprehensive documentation
  - System-specific docs (PAUSE_MENU.md, HERO_SYSTEM.md, etc.)
  - Design documents
  - Technical specifications

## Initialization Flow

1. **launch_game.bat** runs Python with main.py
2. **main.py** initializes the Game class
3. Game loads configuration from **config.json**
4. Game initializes all required systems
5. Main menu is displayed
6. Based on player selection, appropriate game mode is started

## Code Style and Conventions

- **Classes**: CamelCase (e.g., `PauseMenu`, `Player`)
- **Functions/Methods**: snake_case (e.g., `handle_input`, `update`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_HEALTH`, `SCREEN_WIDTH`)
- **Private Members**: Prefixed with underscore (e.g., `_private_method`)

## Future Organization Improvements

1. **Better Separation of UI**: Create a dedicated `ui/` directory for all UI-related components
2. **Config Module**: Create a dedicated configuration module for better settings management
3. **Asset Management**: Implement a unified asset loading/caching system
4. **Plugin Architecture**: Allow for modular extension of game features 