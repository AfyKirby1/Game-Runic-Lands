# Runic Lands Save System Documentation

This document provides a comprehensive overview of the Runic Lands save system, including its implementation, usage guidelines, and practices for maintaining save compatibility across game versions.

## Table of Contents

1. [Overview](#overview)
2. [Save File Structure](#save-file-structure)
3. [How to Use the Save System](#how-to-use-the-save-system)
4. [Save Corruption Protection](#save-corruption-protection)
5. [Version Compatibility](#version-compatibility)
6. [Backup System](#backup-system)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview

The Runic Lands save system is designed to be robust, maintainable, and resistant to data corruption. It features:

- **Data integrity protection**: SHA-256 checksums verify file integrity
- **Version tracking**: Save files include version information for forwards/backwards compatibility
- **Error recovery**: Automatic backup and restore functionality
- **Compression**: Save files are compressed to reduce storage requirements
- **Metadata separation**: Game metadata is stored separately for quick loading of save info

## Save File Structure

The save system uses two files for each save:

1. **Save file (.sav)**: Contains the compressed, serialized game state
2. **Metadata file (.meta)**: Contains metadata about the save for quick access

### Game State Structure

The primary game state is structured as a dictionary with the following components:

```python
{
    "version": 1,  # Current save format version
    "timestamp": 1713901245,  # Unix timestamp of save
    "game_state": {
        "player": {
            "level": 1,
            "position": [100, 200],
            "inventory": [...],
            "stats": {...}
        },
        "world": {
            "seed": 12345,
            "chunks": [...],
            "entities": [...],
            "time": 3600
        },
        "game_settings": {
            "difficulty": "normal",
            "play_time": 7200
        }
    }
}
```

### Metadata Structure

The metadata file contains a subset of information used for displaying save slots:

```json
{
    "version": 1,
    "timestamp": 1713901245,
    "checksum": "3a9eb1be3a0c5641c191eb28a58d92e65becd824f3215312d673c9f129197b9a",
    "player_level": 5,
    "player_position": [100, 200],
    "world_seed": 12345,
    "play_time": 7200,
    "screenshot": null
}
```

## How to Use the Save System

### Initializing the Save System

```python
from systems.save_manager import SaveManager

# Create a save manager instance
save_manager = SaveManager()
```

### Saving a Game

```python
# Collect the current game state
game_state = {
    "player": player.to_dict(),
    "world": world.to_dict(),
    "game_settings": {
        "difficulty": difficulty,
        "play_time": play_time
    }
}

# Save to a specific slot
slot_name = "Save Game 1"
success = save_manager.save_game(slot_name, game_state)

if success:
    print(f"Game saved successfully to {slot_name}")
else:
    print("Failed to save game")
```

### Loading a Game

```python
try:
    # Load from a specific slot
    slot_name = "Save Game 1"
    game_state = save_manager.load_game(slot_name)
    
    # Apply the loaded state to the game
    player.from_dict(game_state["player"])
    world.from_dict(game_state["world"])
    difficulty = game_state["game_settings"]["difficulty"]
    play_time = game_state["game_settings"]["play_time"]
    
    print(f"Game loaded successfully from {slot_name}")
    
except SaveCorruptionError as e:
    print(f"Save file is corrupted: {e}")
    # Handle corruption (notify player, create new game, etc.)
    
except VersionMismatchError as e:
    print(f"Save version is incompatible: {e}")
    # Handle version mismatch (notify player, try migration, etc.)
    
except FileNotFoundError:
    print(f"Save file not found for slot: {slot_name}")
    # Handle missing file (notify player, show available saves, etc.)
```

### Listing Available Save Slots

```python
# Get a list of all save slots with metadata
save_slots = save_manager.get_save_slots()

for slot in save_slots:
    print(f"Save: {slot['name']}")
    print(f"Date: {slot['date']}")
    print(f"Player Level: {slot['player_level']}")
    print(f"Play Time: {format_time(slot['play_time'])}")
    print("---")
```

### Deleting a Save

```python
# Delete a save slot
slot_name = "Save Game 1"
success = save_manager.delete_save(slot_name)

if success:
    print(f"Save '{slot_name}' deleted successfully")
else:
    print(f"Failed to delete save '{slot_name}'")
```

## Save Corruption Protection

The save system employs several mechanisms to protect against and recover from data corruption:

1. **Checksums**: Each save file has a SHA-256 checksum stored in its metadata file
2. **Validation**: Files are validated before loading to detect corruption
3. **Backups**: Automatic backups are created before each save operation
4. **Recovery**: If a save file is corrupted, the system attempts to restore from a backup

If a save file fails validation, the system follows this process:

1. Log the corruption error
2. Search for the most recent backup for that slot
3. If a backup exists, attempt to restore from it
4. If no backup exists or restoration fails, raise a `SaveCorruptionError`

## Version Compatibility

### Save File Versioning

Each save file includes a version number that corresponds to the save format version (not the game version). When loading a save file, the system checks this version against the current expected version.

If the save version is:
- **Lower than current**: The system migrates the data to the current format
- **Equal to current**: The file is loaded normally
- **Higher than current**: A `VersionMismatchError` is raised (newer game save format)

### Adding New Features

When adding new features that require save format changes, follow these steps:

1. Increment the `SAVE_VERSION` constant in `save_manager.py`
2. Implement the appropriate migration logic in the `_migrate_save_data` method
3. Document the changes in a comment next to the version increment

Example migration:

```python
def _migrate_save_data(self, save_data: Dict) -> Dict:
    current_version = save_data["version"]
    
    # Apply migrations sequentially
    if current_version < 1:
        # Migrate from version 0 to 1
        # Added player skill tree
        save_data["game_state"].setdefault("skills", {"points": 0, "unlocked": []})
    
    # Update to current version
    save_data["version"] = SAVE_VERSION
    return save_data
```

### Breaking Changes

For major changes that would break compatibility entirely, consider:

1. Adding a save converter tool
2. Providing a warning to players about save incompatibility
3. Documenting exactly what changes occurred and why compatibility was broken

## Backup System

### How Backups Work

The save system automatically creates backups:

1. Before overwriting an existing save
2. Before deleting a save slot

Backups are stored in the `saves/backups` directory with filenames like:
```
SaveGame1_1713901245.bak
SaveGame1_1713901245.meta
```

### Backup Cleanup

To prevent excessive disk usage, old backups can be cleaned up:

```python
# Keep only the 5 most recent backups per save slot
removed_count = save_manager.cleanup_old_backups(max_backups_per_slot=5)
print(f"Removed {removed_count} old backups")
```

## Best Practices

### For Developers

1. **Backwards Compatibility**: Always test loading older save versions
2. **Migration Path**: Provide clean migration paths in the `_migrate_save_data` method
3. **Testing**: Test save/load cycles with corrupted files to ensure recovery works
4. **Documentation**: Document all save format changes in version control
5. **Sanitization**: Always sanitize player-provided slot names

### For Data Structure Changes

When changing game data structures:

1. **Additive Changes**: Add new fields with default values for older saves
2. **Renamed Fields**: In migrations, copy data from old fields to new ones
3. **Removed Fields**: Consider keeping but ignoring obsolete fields
4. **Changed Semantics**: Convert old values to new format in migrations

### Versioning Guidelines

- **Increment version** when adding required fields or changing data structure
- **No need to increment** for purely additive changes that work with defaults
- **Major version changes** should be rare and well-documented

## Troubleshooting

### Common Issues

#### Corrupted Save Files

Signs of corruption:
- Checksum validation failures
- Unexpected exceptions when loading
- Missing or incomplete data

Resolution steps:
1. Check logs for detailed error information
2. Attempt manual restoration from a backup
3. Use the validation function to check integrity

#### Version Mismatch Errors

If encountering VersionMismatchError:
- Check that the game version matches the expected save version
- Ensure all migrations are properly implemented
- Consider implementing additional migration paths

#### Missing Backups

If backups are missing:
- Verify the backup directory permissions
- Check for disk space issues
- Review cleanup policies

### Manual Recovery

For advanced recovery:
```python
# Manual validation of a save file
save_path = save_manager._get_save_path("Save Game 1")
metadata_path = save_manager._get_metadata_path("Save Game 1")
is_valid, error_message = save_manager._validate_save_file(save_path, metadata_path)

# Manual backup restoration
backup_path = "saves/backups/SaveGame1_1713901245.bak"
success, error = save_manager._restore_from_backup("Save Game 1", backup_path)
```

---

For more information, consult the source code documentation in `systems/save_manager.py`. 