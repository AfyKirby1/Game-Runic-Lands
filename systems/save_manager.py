import json
import os
import time
import hashlib
import shutil
import pickle
import gzip
from typing import Dict, List, Any, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='save_manager.log'
)
logger = logging.getLogger('SaveManager')

# Current save format version - increment when making incompatible changes
SAVE_VERSION = 1
SAVE_DIRECTORY = "saves"
BACKUP_DIRECTORY = os.path.join(SAVE_DIRECTORY, "backups")

class SaveCorruptionError(Exception):
    """Exception raised when a save file is detected as corrupt."""
    pass

class VersionMismatchError(Exception):
    """
    Exception raised when a save file version doesn't match the current version.
    """
    pass

class SaveManager:
    """
    Handles saving and loading game states with protection against data corruption.

    This class provides a robust system for managing game saves, featuring
    automatic backups, data integrity checks via checksums, version tracking for
    migrations, and data compression.
    """
    
    def __init__(self):
        """
        Initializes the SaveManager.

        Ensures that the necessary save and backup directories exist.
        """
        self._ensure_directories()
        self.current_save_slot = None
    
    def _ensure_directories(self):
        """
        Creates the save and backup directories if they don't already exist.
        """
        os.makedirs(SAVE_DIRECTORY, exist_ok=True)
        os.makedirs(BACKUP_DIRECTORY, exist_ok=True)
        
    def _get_save_path(self, slot_name: str) -> str:
        """
        Generates the file path for a given save slot name.

        Args:
            slot_name (str): The name of the save slot.

        Returns:
            str: The full path to the save file.
        """
        sanitized_name = "".join([c for c in slot_name if c.isalnum() or c in " _-"])
        return os.path.join(SAVE_DIRECTORY, f"{sanitized_name}.sav")
    
    def _get_metadata_path(self, slot_name: str) -> str:
        """
        Generates the file path for a save slot's metadata.

        Args:
            slot_name (str): The name of the save slot.

        Returns:
            str: The full path to the metadata file.
        """
        sanitized_name = "".join([c for c in slot_name if c.isalnum() or c in " _-"])
        return os.path.join(SAVE_DIRECTORY, f"{sanitized_name}.meta")
    
    def _get_backup_path(self, slot_name: str, timestamp: int = None) -> str:
        """
        Generates a file path for a backup of a save slot.

        Args:
            slot_name (str): The name of the save slot.
            timestamp (int, optional): A specific timestamp for the backup.
                                       If None, the current time is used. Defaults to None.

        Returns:
            str: The full path for the backup file.
        """
        sanitized_name = "".join([c for c in slot_name if c.isalnum() or c in " _-"])
        timestamp = timestamp or int(time.time())
        return os.path.join(BACKUP_DIRECTORY, f"{sanitized_name}_{timestamp}.bak")
    
    def _compute_checksum(self, data: bytes) -> str:
        """
        Computes a SHA256 checksum for the given data.

        Args:
            data (bytes): The data to hash.

        Returns:
            str: The hexadecimal checksum string.
        """
        return hashlib.sha256(data).hexdigest()
    
    def _create_save_data(self, game_state: Dict) -> Dict:
        """
        Wraps the game state in a save data structure with metadata.

        Args:
            game_state (Dict): The dictionary containing the current game state.

        Returns:
            Dict: A dictionary structured for saving, including version and timestamp.
        """
        return {
            "version": SAVE_VERSION,
            "timestamp": int(time.time()),
            "game_state": game_state
        }
    
    def _create_metadata(self, save_data: Dict, checksum: str) -> Dict:
        """
        Creates a metadata dictionary for a save file.

        This metadata includes quick-access info like player level and world seed,
        avoiding the need to load the full save file.

        Args:
            save_data (Dict): The save data dictionary.
            checksum (str): The checksum of the save data.

        Returns:
            Dict: A dictionary containing the save file's metadata.
        """
        game_state = save_data["game_state"]
        world = game_state.get("world", {})
        player = game_state.get("player", {})
        
        return {
            "version": save_data["version"],
            "timestamp": save_data["timestamp"],
            "checksum": checksum,
            "player_level": player.get("level", 1),
            "player_position": player.get("position", [0, 0]),
            "world_seed": world.get("seed", 0),
            "play_time": game_state.get("play_time", 0),
            "screenshot": None  # TODO: Add screenshot capability
        }
    
    def _validate_save_file(self, file_path: str, metadata_path: str) -> Tuple[bool, str]:
        """
        Validates a save file against its metadata, checking for corruption.

        Args:
            file_path (str): The path to the save file.
            metadata_path (str): The path to the metadata file.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating validity
                              and a message.
        """
        if not os.path.exists(file_path):
            return False, f"Save file not found: {file_path}"
            
        if not os.path.exists(metadata_path):
            return False, f"Metadata file not found: {metadata_path}"
            
        try:
            # Load and check metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                
            # Load save data and compute checksum
            with gzip.open(file_path, 'rb') as f:
                save_data_bytes = f.read()
                
            computed_checksum = self._compute_checksum(save_data_bytes)
            
            # Compare checksums
            if computed_checksum != metadata["checksum"]:
                return False, "Checksum mismatch: save file may be corrupted"
                
            # Load and check save version
            save_data = pickle.loads(save_data_bytes)
            if save_data["version"] > SAVE_VERSION:
                return False, f"Save version {save_data['version']} is newer than current version {SAVE_VERSION}"
                
            return True, "Save file validated successfully"
            
        except Exception as e:
            return False, f"Error validating save file: {str(e)}"
    
    def create_backup(self, slot_name: str) -> Optional[str]:
        """
        Creates a backup of a save file and its metadata.

        Args:
            slot_name (str): The name of the save slot to back up.

        Returns:
            Optional[str]: The path to the created backup file, or None on failure.
        """
        save_path = self._get_save_path(slot_name)
        if not os.path.exists(save_path):
            return None
            
        backup_path = self._get_backup_path(slot_name)
        try:
            shutil.copy2(save_path, backup_path)
            metadata_path = self._get_metadata_path(slot_name)
            if os.path.exists(metadata_path):
                backup_meta_path = backup_path.replace('.bak', '.meta')
                shutil.copy2(metadata_path, backup_meta_path)
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return None
    
    def save_game(self, slot_name: str, game_state: Dict) -> bool:
        """
        Saves the current game state to a specified slot.

        This process includes creating a backup, serializing and compressing the
        data, computing a checksum, and writing both the save and metadata files.

        Args:
            slot_name (str): The name of the save slot.
            game_state (Dict): A dictionary containing the full game state.

        Returns:
            bool: True if saving was successful, False otherwise.
        """
        try:
            # Create backup of existing save
            if os.path.exists(self._get_save_path(slot_name)):
                self.create_backup(slot_name)
            
            # Create save data structure
            save_data = self._create_save_data(game_state)
            
            # Serialize and compress the data
            save_data_bytes = pickle.dumps(save_data)
            
            # Compute checksum
            checksum = self._compute_checksum(save_data_bytes)
            
            # Create metadata
            metadata = self._create_metadata(save_data, checksum)
            
            # Write save file
            save_path = self._get_save_path(slot_name)
            with gzip.open(save_path, 'wb') as f:
                f.write(save_data_bytes)
            
            # Write metadata
            metadata_path = self._get_metadata_path(slot_name)
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.current_save_slot = slot_name
            logger.info(f"Game saved successfully to slot: {slot_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving game: {str(e)}")
            return False
    
    def load_game(self, slot_name: str) -> Dict:
        """
        Loads a game state from the specified slot.

        This method validates the save file and, if corruption is detected,
        attempts to restore from the latest backup. It also handles migration
        of older save file versions.

        Args:
            slot_name (str): The name of the save slot to load.

        Returns:
            Dict: The loaded game state.

        Raises:
            SaveCorruptionError: If the save file is corrupted and no valid
                                 backup can be found.
            VersionMismatchError: If the save version is incompatible.
            FileNotFoundError: If the save file does not exist.
        """
        save_path = self._get_save_path(slot_name)
        metadata_path = self._get_metadata_path(slot_name)
        
        # Validate save file
        is_valid, error_message = self._validate_save_file(save_path, metadata_path)
        if not is_valid:
            # Try to restore from backup
            backup = self._find_latest_backup(slot_name)
            if backup:
                logger.warning(f"Attempting to restore from backup: {backup}")
                is_valid, error_message = self._restore_from_backup(slot_name, backup)
                if not is_valid:
                    raise SaveCorruptionError(f"Save file corrupted and backup restore failed: {error_message}")
            else:
                raise SaveCorruptionError(f"Save file corrupted and no backup found: {error_message}")
        
        try:
            # Load save data
            with gzip.open(save_path, 'rb') as f:
                save_data = pickle.loads(f.read())
            
            # Handle version differences
            if save_data["version"] < SAVE_VERSION:
                save_data = self._migrate_save_data(save_data)
            
            self.current_save_slot = slot_name
            logger.info(f"Game loaded successfully from slot: {slot_name}")
            return save_data["game_state"]
            
        except Exception as e:
            logger.error(f"Error loading game: {str(e)}")
            raise
    
    def _find_latest_backup(self, slot_name: str) -> Optional[str]:
        """
        Finds the most recent backup file for a given save slot.

        Args:
            slot_name (str): The name of the save slot.

        Returns:
            Optional[str]: The path to the latest backup, or None if none exist.
        """
        backup_prefix = "".join([c for c in slot_name if c.isalnum() or c in " _-"]) + "_"
        backups = []
        
        for filename in os.listdir(BACKUP_DIRECTORY):
            if filename.startswith(backup_prefix) and filename.endswith('.bak'):
                backups.append(os.path.join(BACKUP_DIRECTORY, filename))
        
        if not backups:
            return None
            
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return backups[0]
    
    def _restore_from_backup(self, slot_name: str, backup_path: str) -> Tuple[bool, str]:
        """
        Restores a save file and its metadata from a backup.

        Args:
            slot_name (str): The name of the save slot to restore.
            backup_path (str): The path to the backup file.

        Returns:
            Tuple[bool, str]: A tuple indicating success and a message.
        """
        try:
            save_path = self._get_save_path(slot_name)
            metadata_path = self._get_metadata_path(slot_name)
            
            # Copy backup to save location
            shutil.copy2(backup_path, save_path)
            
            # Copy backup metadata if it exists
            backup_meta = backup_path.replace('.bak', '.meta')
            if os.path.exists(backup_meta):
                shutil.copy2(backup_meta, metadata_path)
            
            # Validate the restored save
            return self._validate_save_file(save_path, metadata_path)
            
        except Exception as e:
            return False, f"Error restoring from backup: {str(e)}"
    
    def _migrate_save_data(self, save_data: Dict) -> Dict:
        """
        Migrates save data from an older version to the current version.

        This method should be updated with migration logic when `SAVE_VERSION`
        is incremented.

        Args:
            save_data (Dict): The save data from an older version.

        Returns:
            Dict: The migrated save data, updated to the current version.
        """
        current_version = save_data["version"]
        
        # Apply migrations sequentially
        if current_version < 1:
            # Migrate from version 0 to 1
            # Example: Add new field that didn't exist in version 0
            save_data["game_state"].setdefault("new_field_added_in_v1", "default_value")
        
        # Update to current version
        save_data["version"] = SAVE_VERSION
        
        logger.info(f"Migrated save data from version {current_version} to {SAVE_VERSION}")
        return save_data
    
    def get_save_slots(self) -> List[Dict[str, Any]]:
        """
        Retrieves a list of all available save slots with their metadata.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a
                                  save slot with its metadata.
        """
        slots = []
        
        for filename in os.listdir(SAVE_DIRECTORY):
            if filename.endswith('.meta'):
                slot_name = filename[:-5]  # Remove .meta extension
                metadata_path = os.path.join(SAVE_DIRECTORY, filename)
                
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    # Check if corresponding save file exists
                    save_path = self._get_save_path(slot_name)
                    if os.path.exists(save_path):
                        slots.append({
                            "name": slot_name,
                            "timestamp": metadata["timestamp"],
                            "date": time.strftime("%Y-%m-%d %H:%M", time.localtime(metadata["timestamp"])),
                            "player_level": metadata.get("player_level", 1),
                            "play_time": metadata.get("play_time", 0),
                            "version": metadata.get("version", 0)
                        })
                        
                except Exception as e:
                    logger.warning(f"Error reading metadata for {slot_name}: {str(e)}")
        
        # Sort by timestamp (newest first)
        slots.sort(key=lambda x: x["timestamp"], reverse=True)
        return slots
    
    def delete_save(self, slot_name: str) -> bool:
        """
        Deletes a save slot, including its save file and metadata.

        A final backup is created before deletion.

        Args:
            slot_name (str): The name of the save slot to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            # Create one final backup before deletion
            self.create_backup(slot_name)
            
            # Delete save and metadata files
            save_path = self._get_save_path(slot_name)
            metadata_path = self._get_metadata_path(slot_name)
            
            if os.path.exists(save_path):
                os.remove(save_path)
            
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            if self.current_save_slot == slot_name:
                self.current_save_slot = None
                
            logger.info(f"Save slot deleted: {slot_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting save slot: {str(e)}")
            return False
    
    def cleanup_old_backups(self, max_backups_per_slot: int = 5) -> int:
        """
        Removes old backups, keeping a specified number of recent backups per slot.

        Args:
            max_backups_per_slot (int, optional): The number of backups to keep
                                                 for each slot. Defaults to 5.

        Returns:
            int: The total number of backups removed.
        """
        # Group backups by slot name
        backup_groups = {}
        
        for filename in os.listdir(BACKUP_DIRECTORY):
            if filename.endswith('.bak'):
                # Extract slot name from backup filename (slotname_timestamp.bak)
                parts = filename.split('_')
                if len(parts) >= 2:
                    timestamp = parts[-1].replace('.bak', '')
                    slot_name = '_'.join(parts[:-1])
                    
                    if slot_name not in backup_groups:
                        backup_groups[slot_name] = []
                    
                    backup_path = os.path.join(BACKUP_DIRECTORY, filename)
                    backup_groups[slot_name].append((backup_path, int(timestamp) if timestamp.isdigit() else 0))
        
        # Remove old backups for each slot
        removed_count = 0
        for slot_name, backups in backup_groups.items():
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Keep only the latest max_backups_per_slot
            for backup_path, _ in backups[max_backups_per_slot:]:
                try:
                    os.remove(backup_path)
                    # Also remove the metadata file if it exists
                    meta_path = backup_path.replace('.bak', '.meta')
                    if os.path.exists(meta_path):
                        os.remove(meta_path)
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"Error removing old backup {backup_path}: {str(e)}")
        
        logger.info(f"Cleaned up {removed_count} old backups")
        return removed_count 