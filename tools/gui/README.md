# 🎨 Runic Lands Asset Generator GUI

Modern graphical interface for asset generation, management, and advanced tools for Runic Lands.

## 🚀 Quick Start

### Launch the GUI
```bash
# From the tools/gui directory:
launch_asset_gui.bat

# Or directly with Python:
python asset_gui.py
```

## 🛠️ Available Tools

### 1. **Main Asset Generator** (`asset_gui.py`)
**Primary GUI for all asset operations**

#### Features:
- **Asset Status Monitoring** - Real-time view of all game assets
- **One-Click Generation** - Generate sprites, audio, and all assets
- **Live Preview** - Visual preview of generated sprites
- **Comprehensive Logging** - Detailed operation logs with timestamps
- **Background Processing** - Non-blocking operations
- **Auto-Validation** - Automatic asset validation after generation

#### Controls:
- **Generate Sprites** - Create all character sprites and animations
- **Generate Audio** - Create menu music, game music, and sound effects
- **Validate Assets** - Check asset quality and completeness
- **Complete Setup** - Full asset generation and validation
- **Preview Controls** - View, refresh, and explore generated assets

### 2. **Location Generator** (`location_generator.py`)
**Procedural location and area generation**

#### Features:
- **Multiple Location Types** - Forest, Dungeon, Village, Castle
- **Custom Features** - Add your own location elements
- **Map Visualization** - Simple map preview for generated locations
- **Export Options** - Save as JSON or export to game format
- **Atmosphere Generation** - Procedural mood and description

#### Location Types:
- **Forest** - Mystic woods with trees, streams, and wildlife
- **Dungeon** - Dark crypts with traps, puzzles, and treasures
- **Village** - Peaceful settlements with shops and NPCs
- **Castle** - Majestic fortresses with towers and halls

### 3. **Batch Processor** (`batch_processor.py`)
**Advanced bulk operations and automation**

#### Features:
- **Operation Queue** - Queue multiple operations for batch processing
- **Asset Operations** - Convert, resize, optimize images
- **Project Operations** - Process multiple projects simultaneously
- **File Operations** - Rename, organize, backup files
- **Custom Scripts** - Execute custom Python/batch scripts
- **Progress Tracking** - Real-time progress monitoring

#### Operation Types:
- **Image Processing** - Convert formats, resize, optimize
- **Sprite Sheet Generation** - Create animation sheets
- **Project Management** - Multi-project asset generation
- **File Management** - Organization and cleanup
- **Custom Automation** - Run your own scripts

### 4. **Asset Cleaner** (`asset_cleaner.py`)
**Clean up unused and problematic assets**

#### Features:
- **Duplicate Detection** - Find and remove duplicate files
- **Unused File Detection** - Identify potentially unused assets
- **Temporary File Cleanup** - Remove temp and cache files
- **Large File Detection** - Find oversized assets
- **Safety Features** - Backup before cleaning, confirmation dialogs
- **Statistics** - Detailed cleanup statistics

#### Cleanup Options:
- **Duplicates** - Remove identical files
- **Unused Files** - Clean up orphaned assets
- **Temporary Files** - Remove .tmp, .log, .cache files
- **Large Files** - Identify oversized assets
- **Custom Patterns** - Define your own cleanup rules

## 📋 Usage Examples

### Generate All Assets
1. Launch `asset_gui.py`
2. Click "Generate All Assets"
3. Wait for completion
4. Check preview and validation results

### Create a New Location
1. Launch `location_generator.py`
2. Select location type (e.g., "Forest")
3. Customize name and features
4. Click "Generate Random" or "Generate Custom"
5. Export to game format

### Batch Process Images
1. Launch `batch_processor.py`
2. Click "Convert Image Formats"
3. Configure source/target formats
4. Add to queue
5. Click "Start Processing"

### Clean Up Assets
1. Launch `asset_cleaner.py`
2. Select scan options
3. Click "Scan Assets"
4. Review results
5. Select cleanup options
6. Click "Start Cleanup"

## 🎯 Advanced Features

### Preview System
- **Sprite Preview** - Visual preview of generated sprites
- **Full Size View** - View assets at full resolution
- **Asset Explorer** - Open asset folders directly
- **Real-time Updates** - Preview updates automatically

### Logging and Monitoring
- **Comprehensive Logs** - Detailed operation logs
- **Error Tracking** - Clear error messages and solutions
- **Progress Indicators** - Visual progress bars and status
- **Statistics** - Asset counts and health metrics

### Safety Features
- **Backup Creation** - Automatic backups before operations
- **Confirmation Dialogs** - Prevent accidental deletions
- **Error Recovery** - Graceful handling of failures
- **Undo Support** - Restore from backups

## 🔧 Configuration

### GUI Options
- **Force Overwrite** - Overwrite existing files
- **Auto-validate** - Validate after generation
- **Auto-preview** - Show preview after generation
- **Parallel Processing** - Process operations in parallel

### Asset Settings
- **Output Directories** - Customize asset locations
- **File Formats** - Choose preferred formats
- **Quality Settings** - Adjust compression and quality
- **Size Thresholds** - Set limits for large files

## 📁 File Structure

```
tools/gui/
├── README.md                    # This documentation
├── launch_asset_gui.bat        # Windows launcher
├── asset_gui.py                # Main asset generator GUI
├── location_generator.py       # Location generation tool
├── batch_processor.py          # Batch processing tool
└── asset_cleaner.py            # Asset cleanup tool
```

## 🚨 Requirements

### Dependencies
- **Python 3.7+** - Required for all tools
- **tkinter** - GUI framework (usually included with Python)
- **PIL/Pillow** - Image processing
- **numpy** - Numerical operations
- **pathlib** - File path handling

### Installation
```bash
# Install required packages
pip install pillow numpy

# Or use the launcher (installs automatically)
launch_asset_gui.bat
```

## 🐛 Troubleshooting

### Common Issues
- **Import Errors** - Run from correct directory
- **Missing Dependencies** - Install required packages
- **Permission Errors** - Check file/directory permissions
- **GUI Not Responding** - Check for background processes

### Getting Help
- Check the operation logs for detailed error messages
- Use the built-in help and documentation
- Verify file paths and permissions
- Ensure all dependencies are installed

## 🎨 Customization

### Adding New Tools
1. Create new Python file in `tools/gui/`
2. Follow the existing GUI patterns
3. Import and integrate with main GUI
4. Add launcher button if needed

### Custom Operations
1. Use the Batch Processor for custom scripts
2. Create operation definitions
3. Add to the processing queue
4. Execute with full logging and error handling

## 🔮 Future Features

### Planned Enhancements
- **Asset Browser** - Visual file browser
- **Template System** - Reusable asset templates
- **Version Control** - Asset versioning and history
- **Cloud Sync** - Sync assets across devices
- **Plugin System** - Extensible tool architecture

### Integration Plans
- **Game Engine Integration** - Direct game asset loading
- **Version Control** - Git integration for assets
- **CI/CD Pipeline** - Automated asset processing
- **Team Collaboration** - Multi-user asset management

---

*For more information about specific tools, see their individual help documentation or use the built-in help system.*
