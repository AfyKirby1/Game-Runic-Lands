# 🎮 Runic Lands

A 2D action RPG game with procedural world generation, local co-op, and a robust combat system.

## 🚀 Features

- Python-based game engine built with Pygame
- Local co-op gameplay (up to 2 players)
- Combat system with attack animations
- Health system with visual bars
- Player collision detection
- Pause menu system
- Inventory system
- Options menu with configurable controls
- Particle effects via Synapstex graphics engine
- Robust save/load system with corruption detection and recovery

## 📋 Requirements

- Python 3.8+
- Pygame 2.0+
- Additional dependencies in requirements.txt

## 🎮 How to Play

### Windows
1. Run `launch_game.bat` or
2. Open a command prompt and run:
   ```
   python main.py
   ```

### Controls
- WASD: Player 1 movement
- Arrow keys: Player 2 movement
- Space/Ctrl: Attack
- E/Enter: Open inventory
- Esc: Pause menu

## 🛠️ Development

### Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

### Project Structure
See [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for a detailed breakdown of the codebase organization.

### Documentation
- [CHANGELOG.md](CHANGELOG.md): Version history and changes
- [ROADMAP.md](ROADMAP.md): Development roadmap and planned features
- [SUGGESTIONS.md](SUGGESTIONS.md): Proposed features and improvements
- [docs/](docs/): Detailed documentation for game systems

## 🔄 Recent Updates

- Added comprehensive save/load system with data protection
- Added pause menu system
- Improved graphics with particle effects
- Enhanced world generation system
- Added inventory system
- Upgraded menu music system to support 10 distinct sections with seamless transitions, advanced 100ms crossfades, and dynamic queuing for a richer audio experience

## 🗺️ Roadmap Progress

Currently working on v0.2 (Core Gameplay), with 50% of v0.1 (Basic Engine) features completed. See [ROADMAP.md](ROADMAP.md) for details.

## 🔧 Planned Improvements

We're working on several structural improvements to the codebase. See [REFACTORING.md](docs/REFACTORING.md) for details.

## 🤝 Contributing

Contributions are welcome! See [SUGGESTIONS.md](SUGGESTIONS.md) for ideas on where to help.

## Recent Updates

### Audio System (v1.3.0)
- Implemented sectioned music playback for seamless transitions between menu themes
- Fixed delay issues in menu music transitions for continuous playback
- Added diagnostic tools to analyze audio file properties
- Created comprehensive audio system documentation
- Enhanced error handling and recovery for missing audio files
- Optimized music event processing for minimal latency

### UI Improvements (v1.2.0)
- Fixed menu scaling for different resolutions
- Added responsive button positioning
- Improved ToggleButton functionality
- Enhanced visual feedback for UI interactions

## Getting Started

### Prerequisites
- Python 3.8+
- Pygame 2.0.0+
- NumPy (for audio generation)
- SciPy (for audio file handling)

### Installation
1. Clone the repository
```bash
git clone https://github.com/yourusername/runiclands.git
cd runiclands
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the game
```bash
python main.py
```

## Documentation
- [Audio System](docs/AudioSystem.md) - Detailed audio system documentation
- [Core Systems](docs/CORE_SYSTEMS.md)
- [Particle System](docs/PARTICLE_SYSTEM.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [UI System](docs/UI_SYSTEM.md)

## Controls
- WASD/Arrow Keys: Movement
- Space: Interact/Select
- Esc: Pause/Menu
- M: Toggle Music
- Volume Controls in Options Menu

## Features

### Audio
- Sectioned menu music with seamless transitions between themes
- Dynamic music playback with adaptive queuing system
- Responsive sound effects with volume controls
- Comprehensive diagnostics and error recovery
- Volume controls for master, music, and SFX
- Music mute toggle

### Graphics
- Particle effects system
- Dynamic lighting
- Smooth animations
- Resolution scaling

### Gameplay
- RPG-style combat
- Inventory system
- Quest system
- Character progression

## Project Structure
```
runiclands/
├── assets/
│   ├── audio/
│   │   ├── enhanced_menu_theme.wav
│   │   ├── enhanced_game_theme.wav
│   │   └── sfx/
│   ├── images/
│   └── shaders/
├── docs/
│   ├── AUDIO.md
│   ├── CORE_SYSTEMS.md
│   └── ...
├── scenes/
├── systems/
│   ├── audio.py
│   ├── menu.py
│   ├── options.py
│   └── ...
├── ui/
│   ├── buttons.py
│   └── ...
├── main.py
└── requirements.txt
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Thanks to all contributors
- Pygame community
- Asset creators (see CREDITS.md)

## Utilities

### Audio Tools
The game includes an audio checker and repair utility to help diagnose and fix issues with audio files:

```bash
# Run from the tools directory
python audio_checker.py
```

This tool can:
- Check for missing audio files
- Analyze audio file properties
- Create missing section files
- Verify section consistency
- Fix file permissions 

# Runic Lands Documentation

Welcome to the Runic Lands documentation! This directory contains all the documentation for the project, organized into different categories for easy navigation.

## Directory Structure

- `tech/` - Technical documentation for developers
  - System architecture
  - API references
  - Integration guides
  - Technical specifications

- `design/` - Game design documentation
  - Game mechanics
  - Level design
  - Character design
  - Story and lore

- `guides/` - User guides and tutorials
  - Getting started
  - Game controls
  - Tips and tricks
  - Troubleshooting

## Getting Started

1. Browse the documentation by category
2. Use the search function to find specific topics
3. Check the table of contents in each document
4. Follow the links to related documentation

## Contributing

When adding new documentation:

1. Place files in the appropriate subdirectory
2. Use Markdown format (.md extension)
3. Follow the documentation-first development rules
4. Include clear examples and explanations
5. Update the table of contents if needed

## Best Practices

- Keep documentation up to date
- Use clear and concise language
- Include code examples where relevant
- Add diagrams for complex concepts
- Document all public interfaces
- Include error handling information

## Need Help?

If you can't find what you're looking for:
1. Check the troubleshooting guide
2. Look in the FAQ section
3. Contact the development team
4. Check the issue tracker for known problems 