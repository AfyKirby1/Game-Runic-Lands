# 🛠️ Runic Lands Development Tools

This directory contains all the development tools for Runic Lands, organized and modernized for better maintainability and ease of use.

## 📁 Tool Organization

### 🎨 Sprite Generation (`sprite_generation/`)
- **`sprite_generator.py`** - Modern unified sprite generation tool
  - Generates all character sprites and animations
  - Validates generated assets
  - Creates sprite sheet previews
  - Comprehensive error handling and logging

### 🎵 Audio Generation (`audio_generation/`)
- **`audio_manager.py`** - Unified audio management system
  - Generates menu and game music sections
  - Creates sound effects
  - Validates audio files
  - Backup and restore functionality

### 🔍 Asset Validation (`asset_validation/`)
- **`asset_validator.py`** - Comprehensive asset validation tool
  - Validates sprite files (size, format, content)
  - Validates audio files (format, duration, quality)
  - Generates detailed validation reports
  - Health scoring system

### 🛠️ Unified Management
- **`asset_manager.py`** - Master tool for all asset operations
  - Single command for all asset needs
  - Complete setup and maintenance workflows
  - Comprehensive statistics and reporting

## 🚀 Quick Start

### Check Asset Status
```bash
# Check what assets exist
python tools/asset_manager.py --check

# Check specific asset types
python tools/sprite_generation/sprite_generator.py --check
python tools/audio_manager.py --check
```

### Generate All Assets
```bash
# Generate everything at once
python tools/asset_manager.py --generate

# Or generate specific types
python tools/sprite_generation/sprite_generator.py --generate-all
python tools/audio_manager.py --generate-all
```

### Validate Assets
```bash
# Validate all assets
python tools/asset_manager.py --validate

# Or validate specific types
python tools/asset_validation/asset_validator.py --all
```

### Complete Setup
```bash
# Full asset setup (recommended for new projects)
python tools/asset_manager.py --setup

# Maintenance mode (check and fix issues)
python tools/asset_manager.py --maintain
```

## 📋 Tool Features

### ✅ What's Fixed
- **Eliminated redundancy** - No more duplicate tools
- **Unified interfaces** - Consistent command-line options
- **Better error handling** - Comprehensive error reporting
- **Asset validation** - Quality checks for all assets
- **Progress feedback** - Clear status messages and statistics
- **Cross-platform** - Works on Windows, Mac, and Linux

### 🎯 Key Improvements
- **Single source of truth** - One tool per asset type
- **Modular design** - Easy to extend and maintain
- **Comprehensive validation** - Catch issues before they cause problems
- **Better documentation** - Clear usage instructions and examples
- **Statistics tracking** - Monitor asset health over time

## 🔧 Advanced Usage

### Sprite Generation
```bash
# Generate only base sprites
python tools/sprite_generation/sprite_generator.py --generate-base

# Generate only animations
python tools/sprite_generation/sprite_generator.py --generate-animations

# Create sprite preview
python tools/sprite_generation/sprite_generator.py --preview

# Force regenerate all
python tools/sprite_generation/sprite_generator.py --generate-all --force
```

### Audio Generation
```bash
# Generate only menu music
python tools/audio_manager.py --generate-menu

# Generate only game music
python tools/audio_manager.py --generate-game

# Generate only sound effects
python tools/audio_manager.py --generate-sfx

# Analyze existing audio files
python tools/audio_manager.py --analyze
```

### Asset Validation
```bash
# Validate only sprites
python tools/asset_validation/asset_validator.py --sprites

# Validate only audio
python tools/asset_validation/asset_validator.py --audio

# Generate detailed report
python tools/asset_validation/asset_validator.py --all --report
```

## 📊 Asset Health Monitoring

The tools include comprehensive health monitoring:

- **Asset completeness** - Track missing files
- **Quality validation** - Check file formats and properties
- **Health scoring** - Overall asset health percentage
- **Issue tracking** - Detailed problem identification
- **Report generation** - Save validation results

## 🗂️ File Structure

```
tools/
├── README.md                          # This file
├── asset_manager.py                   # Master asset management tool
├── audio_manager.py                   # Audio generation and management
├── sprite_generation/
│   └── sprite_generator.py            # Sprite generation tool
├── asset_validation/
│   └── asset_validator.py             # Asset validation tool
└── audio/
    └── README.md                      # Audio tools documentation
```

## 🚨 Removed Tools

The following old, redundant tools have been removed:

- ❌ `generate_base_sprite.py` (replaced by sprite_generator.py)
- ❌ `generate_walking_sprite.py` (replaced by sprite_generator.py)
- ❌ `generate_attack_sprite.py` (replaced by sprite_generator.py)
- ❌ `tools/fix_audio.bat` (replaced by audio_manager.py)
- ❌ `tools/quick_fix_audio.bat` (replaced by audio_manager.py)

## 🎯 Best Practices

1. **Always validate** after generating assets
2. **Use the unified manager** for most operations
3. **Check asset health** regularly during development
4. **Backup before major changes** using `--backup`
5. **Use `--force` sparingly** to avoid overwriting good assets

## 🐛 Troubleshooting

### Common Issues
- **Import errors**: Make sure you're running from the project root
- **Missing dependencies**: Run `pip install -r docs/requirements.txt`
- **Permission errors**: Check file/directory permissions
- **Asset validation failures**: Check file formats and sizes

### Getting Help
- Use `--help` with any tool for detailed usage information
- Check the validation reports for specific issues
- Review the generated asset previews for visual problems

---

*For more detailed information about specific tools, see their individual help documentation using `--help`.*
