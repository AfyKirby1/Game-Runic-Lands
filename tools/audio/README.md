# 🎵 Audio Tools - MOVED

## ⚠️ Important Notice

All audio generation and management tools have been **consolidated** into a single, unified tool:

## 🛠️ Use This Instead:

```bash
# From the tools/ directory:
python audio_manager.py --help

# Common commands:
python audio_manager.py --check              # Check which files exist
python audio_manager.py --generate-all       # Generate all missing audio
python audio_manager.py --generate-menu      # Generate menu music only
python audio_manager.py --generate-game      # Generate game music only
python audio_manager.py --generate-sfx       # Generate sound effects only
```

## 📁 Old Tools Removed

The following tools have been **removed** and their functionality moved to `audio_manager.py`:

- ❌ `generate_audio.py`
- ❌ `generate_menu_music.py` 
- ❌ `generate_game_music.py`
- ❌ `generate_menu_music.ps1`
- ❌ `generate_menu_music.bat`
- ❌ `generate_game_music.ps1`
- ❌ `../audio_checker.py`
- ❌ `../fix_audio_files.py`
- ❌ `../quick_fix_audio.py`

## ✅ Benefits of New Unified Tool

- **Single command** for all audio needs
- **Better error handling** and user feedback
- **Consistent interface** for all operations
- **Easier maintenance** and updates
- **Cross-platform compatibility**

---

*For more information, see `../audio_manager.py --help`* 