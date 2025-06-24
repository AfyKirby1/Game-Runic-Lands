# 🏰 Runic Lands
### *A Fantasy RPG Adventure with Custom Graphics Engine*

<div align="center">

[![Game Status](https://img.shields.io/badge/Status-Playable-green)](https://github.com/your-repo/runic-lands)
[![Python](https://img.shields.io/badge/Python-3.13+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-Open%20Source-orange)](LICENSE)
[![Build](https://img.shields.io/badge/Build-Stable-brightgreen)](README.md)

*A mystical realm where ancient magic meets modern gaming technology*

[🎮 Quick Start](#-quick-start) • [🌟 Features](#-features) • [🏗️ Architecture](#️-architecture) • [📖 Documentation](#-documentation)

</div>

---

## 🎮 Quick Start

### 🚀 For Players (One-Click Launch)
```bash
# Windows - Just double-click:
launch_game.bat
```

### 👨‍💻 For Developers
```bash
python main.py
```

**System Requirements**: Python 3.13+, Pygame, Windows 10+

---

## 🌟 Features

### 🎯 **Core Gameplay**
- **🏰 Dynamic World Generation**: Procedurally generated terrain with biomes, structures, and day/night cycles
- **⚔️ Real-Time Combat**: Weapon-based combat system with magic and special abilities
- **📈 Character Progression**: Level up system with stats, skills, and equipment advancement
- **🎒 Inventory Management**: Comprehensive equipment system with weapons, armor, and consumables
- **💾 Save System**: Complete game state persistence with backup and validation

### 🎨 **Synapstex Graphics Engine**
Our custom-built graphics engine featuring:
- **🌊 Advanced Particle Systems**: Autumn leaves, fireflies, magical effects with [10 different leaf colors][[memory:8675283471829075195]]
- **🌅 Dynamic Day/Night Cycle**: Real-time lighting with sun/moon movement and atmospheric overlays
- **🎥 Smooth Camera System**: Seamless player tracking with world boundary constraints
- **🖼️ Render Layers**: Organized depth sorting and optimized culling
- **🌿 Environmental Effects**: Wind-driven grass animation and dynamic shadows
- **✨ Visual Polish**: Smooth animations, particle effects, and atmospheric lighting

### 🎵 **Audio Excellence**
- **🎼 Seamless Music System**: [10 menu sections with gapless looping][[memory:7044340083287372970]] using event-driven transitions
- **🔊 Spatial Audio**: Combat sounds, environmental audio, and UI feedback
- **🛠️ Audio Tools**: Automated generation and management system

### 🏗️ **Technical Innovation**
- **🧩 Chunk-Based World**: Efficient memory management with dynamic loading
- **⚡ Performance Optimized**: Proper culling, render layers, and efficient algorithms
- **🔧 Modular Architecture**: Clean separation of concerns and extensible systems
- **📊 Comprehensive Logging**: Debug and performance monitoring

---

## 🕹️ Controls

| Action | Primary | Alternative |
|--------|---------|-------------|
| **Move** | `WASD` | `Arrow Keys` |
| **Run** | `Left Shift` | Hold while moving |
| **Attack** | `Space` | — |
| **Inventory** | `I` | `Tab` |
| **Pause** | `Escape` | `P` |

---

## 🏗️ Architecture

### 🎮 **Core Systems**
```
🌍 World Generation     → Chunk-based terrain with biomes
💾 Save Manager        → State persistence with validation  
🎛️ Options System      → Customizable controls and settings
📱 Menu System         → Main menu, pause, and options UI
```

### 🎨 **Synapstex Graphics Pipeline**
```
🖼️ Render Layers       → Depth-sorted drawing system
🎥 Camera System       → Smooth tracking with boundaries
✨ Particle Engine     → Advanced effects (leaves, magic, etc.)
🎬 Animation Manager   → Character and sprite animations
🌅 Day/Night System    → Dynamic lighting and celestial bodies
```

### 🔊 **Audio Architecture**
```
🎵 Music Manager       → Section-based seamless looping
🔊 Sound System        → Spatial audio and volume control
🛠️ Asset Generator     → Automated audio creation tools
```

---

## 📁 Project Structure

> 📋 **See [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for detailed file tree**

```
Runic_Lands/
├── 🎮 main.py                 # Game entry point
├── 🚀 launch_game.bat         # One-click launcher
├── 🎯 entities/               # Player & character classes
├── 🌍 systems/                # Core game systems
│   ├── synapstex.py          # 🎨 Custom graphics engine
│   ├── world.py              # 🌍 World generation & rendering
│   ├── music_player.py       # 🎵 Seamless audio system
│   └── save_manager.py       # 💾 Game state persistence
├── 🎨 assets/                 # Game assets
│   ├── audio/                # 🎵 Music & sound effects
│   └── sprites/              # 🖼️ Character & object graphics
├── 📚 docs/                   # 📖 Comprehensive documentation
└── 🛠️ tools/                  # 🔧 Development utilities
```

---

## 🚀 Development Status

### ✅ **Completed Milestones**
- **Phase 1**: ✅ Architecture consolidation & critical fixes
- **Phase 2**: ✅ Code deduplication & dependency cleanup  
- **Phase 3**: ✅ Visual rendering & world boundary fixes
- **Housekeeping**: ✅ Repository optimization & cleanup

### 🎯 **Current State**
| System | Status | Notes |
|--------|--------|-------|
| **🎮 Gameplay** | ✅ Fully Functional | Smooth player movement, combat, inventory |
| **🎨 Graphics** | ✅ Optimized | Synapstex engine with particles & lighting |
| **🎵 Audio** | ✅ Complete | Seamless music loops, spatial sound |
| **💾 Saves** | ✅ Robust | Validation, backups, corruption handling |
| **📁 Repository** | ✅ Clean | Organized structure, proper .gitignore |

### 🔮 **Phase 4 Roadmap**
- 🎯 Enhanced gameplay content and mechanics
- ⚡ Performance optimizations and profiling
- 📚 Documentation polish and tutorials
- 🌟 Additional Synapstex engine features

---

## 🛠️ Development Tools

### 🎵 **Audio Management**
```bash
python tools/audio_manager.py --help    # Unified audio generation
```

### 🎨 **Asset Generation**
```bash
python generate_base_sprite.py          # Character base sprites
python generate_walking_sprite.py       # Walking animations  
python generate_attack_sprite.py        # Combat animations
```

### 🔧 **Development Utilities**
```bash
python main.py --debug                  # Debug mode with logging
launch_game.bat                         # Auto-setup and launch
```

---

## 🐛 Troubleshooting

<details>
<summary><strong>🔧 Common Issues & Solutions</strong></summary>

| Issue | Solution |
|-------|----------|
| **Options Menu Hangs** | ✅ **FIXED** - Options menu integration & missing video settings |
| **Music Player Crash** | ✅ **FIXED** - Resolved naming conflict & automatic music interference & escape navigation |
| **Black Screen** | Fixed in Phase 3 - ensure latest version |
| **No Grass Rendering** | Fixed TerrainType enum mismatch in Phase 3 |
| **Audio Problems** | Check `assets/audio/` files and system volume |
| **Control Issues** | Verify `systems/options.py` keybindings |
| **Performance** | Disable particles in options if needed |
| **Large Logs** | Auto-managed by improved .gitignore |

</details>

### 📞 **Getting Help**
1. 📚 Check comprehensive documentation in `docs/`
2. 📋 Review `logs/` for detailed error information
3. 🚀 Use `launch_game.bat` for automatic dependency setup

---

## 🤝 Contributing

We welcome contributions! Check out our development setup:

1. **Clone & Setup**: Use `launch_game.bat` for automatic environment setup
2. **Architecture**: Review `docs/` for system documentation  
3. **Code Style**: Follow existing patterns and add appropriate logging
4. **Testing**: Test with various save states and world configurations

---

## 📜 License

This project is open source. See [LICENSE](LICENSE) for details.

---

<div align="center">

**🎮 Ready to explore the Runic Lands?**

Run `launch_game.bat` and begin your adventure in our mystical realm!

*Built with ❤️ using Python & the custom Synapstex Graphics Engine*

---

[![Game Preview](https://img.shields.io/badge/🎮-Play%20Now-brightgreen)](#-quick-start)
[![Documentation](https://img.shields.io/badge/📚-Read%20Docs-blue)](docs/)
[![Graphics Engine](https://img.shields.io/badge/🎨-Synapstex%20Engine-purple)](#-synapstex-graphics-engine)

</div>
