# Runic Lands Documentation Index

## Overview
This index provides a quick reference to all documentation in the Runic Lands project, organized by category and purpose.

## Quick Links
- [Project Overview](#project-overview)
- [Technical Documentation](#technical-documentation)
- [Audio System](#audio-system)
- [Development Tools](#development-tools)

## Project Overview
Location: `docs/`
- `README.md` - Main project overview and setup instructions
- `README_2.md` - Additional project details and features
- `PROJECT_CONTEXT.md` - Project background and development context
- `requirements.txt` - Python dependencies and requirements

## Technical Documentation
Location: `docs/` and `docs/tech/`
### Core Systems
- `CORE_SYSTEMS.md` - Core game systems and architecture
- `WORLD_GENERATION.md` - World generation algorithms and systems
- `PROJECT_STRUCTURE.md` - Project file structure and organization
- `REFACTORING.md` - Code refactoring guidelines and history
- `GRASS_RENDERING_FIX.md` - Grass rendering bug fix and TerrainType enum mismatch solution

### Game Systems
- `save_system.md` - Save/load system implementation
- `skill_system.md` - Skill system and mechanics
- `class_system.md` - Character class system
- `flying_system.md` - Flying mechanics and controls
- `EQUIPMENT_SYSTEM.md` - Equipment and inventory system
- `HERO_SYSTEM.md` - Hero/character system
- `PARTICLE_SYSTEM.md` - Particle effects system

### Graphics and Sprites
- `CHARACTER_SPRITES.md` - Character sprite documentation
- `SPRITES.md` - General sprite system
- `synapstex_grafix.md` - Graphics system details
- `SpriteGuide.md` - Sprite creation and usage guide

### UI Systems
- `PAUSE_MENU.md` - Pause menu implementation

## Audio System
Location: `docs/music/`
- `RunicMelodys.md` - Game music system documentation
- `MenuMusicSystem.md` - Menu music system documentation
- `Research_CursorMusic.txt` - Music research and development notes

## Development Tools
Location: `docs/`
- `git_commands.md` - Git workflow and commands
- `save_manager.log` - Save system operation logs

## Documentation Structure
```
docs/
├── DOCUMENTATION_INDEX.md  # This file
├── README.md              # Main project overview
├── README_2.md           # Additional project details
├── PROJECT_CONTEXT.md    # Project background
├── GRASS_RENDERING_FIX.md # Grass rendering bug fix documentation
├── requirements.txt      # Python dependencies
├── git_commands.md      # Git workflow
├── save_manager.log     # Save system logs
├── SpriteGuide.md      # Sprite creation guide
│
├── tech/                # Technical documentation
│   ├── CORE_SYSTEMS.md
│   ├── WORLD_GENERATION.md
│   ├── PARTICLE_SYSTEM.md
│   ├── save_system.md
│   ├── skill_system.md
│   ├── class_system.md
│   ├── flying_system.md
│   ├── EQUIPMENT_SYSTEM.md
│   ├── HERO_SYSTEM.md
│   ├── CHARACTER_SPRITES.md
│   ├── SPRITES.md
│   ├── synapstex_grafix.md
│   ├── PAUSE_MENU.md
│   ├── REFACTORING.md
│   └── PROJECT_STRUCTURE.md
│
└── music/              # Audio documentation
    ├── RunicMelodys.md
    ├── MenuMusicSystem.md
    └── Research_CursorMusic.txt
```

## How to Use This Index
1. **Find Documentation by Category**
   - Use the Quick Links section to jump to major categories
   - Each section lists relevant files and their purposes

2. **Locate Specific Files**
   - Use the Documentation Structure tree to see the physical location
   - Files are organized by their primary purpose

3. **Update Documentation**
   - When adding new documentation, place it in the appropriate folder
   - Update this index to include the new file
   - Follow the existing naming conventions

## Contributing to Documentation
1. Place new documentation in the appropriate folder:
   - General docs → `docs/`
   - Technical docs → `docs/tech/`
   - Audio docs → `docs/music/`

2. Follow these naming conventions:
   - Use PascalCase for system documentation
   - Use snake_case for implementation details
   - Use descriptive names that indicate content

3. Update this index when:
   - Adding new documentation
   - Moving existing documentation
   - Removing documentation
   - Making significant changes to documentation structure 