# Changelog - Runic Lands

All notable changes to this project will be documented in this file.

## [0.1.1] - 2024-12-24

### Fixed
- **Launch Script**: Fixed `launch_game.bat` to properly install all required dependencies
- **Dependency Management**: Added comprehensive dependency checking for all 7 required packages
- **Error Handling**: Improved launch script error messages and user feedback
- **Missing opensimplex**: Resolved `ModuleNotFoundError` for opensimplex dependency

### Added
- **Dependency Installer**: Created standalone `install_dependencies.bat` script
- **Better Error Messages**: Clear instructions when dependencies fail to install

### Changed
- **Launch Process**: Now automatically installs missing dependencies before starting game
- **Dependency Check**: Verifies all packages (pygame, opensimplex, numpy, scipy, pillow, pytmx, pyscroll) are available

## [0.1.0] - 2024-12-24

### Initial Release
- Complete 2D action RPG with custom Synapstex graphics engine
- Procedural world generation with multiple biomes
- Local co-op multiplayer support
- Advanced audio system with seamless music looping
- Day/night cycle with dynamic lighting
- Forest border system with tree generation
- Save/load system with corruption protection
- Comprehensive UI systems (main menu, pause, options, inventory)

---

*Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)*
