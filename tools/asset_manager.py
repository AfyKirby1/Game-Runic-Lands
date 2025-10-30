#!/usr/bin/env python3
"""
Unified Asset Manager for Runic Lands
Single tool to manage all asset generation, validation, and organization
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# Add tools to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from sprite_generation.sprite_generator import SpriteGenerator
from asset_validation.asset_validator import AssetValidator

# Import audio manager
sys.path.insert(0, str(tools_dir))
from audio_manager import AudioManager

class AssetManager:
    """
    A unified system for managing all game assets.

    This class orchestrates various asset-related tasks, including generation,
    validation, organization, and backups, by coordinating specialized sub-managers
    for different asset types like sprites and audio.
    """
    
    def __init__(self, project_root: str = "."):
        """
        Initializes the AssetManager.

        Args:
            project_root (str, optional): The root directory of the project.
                                          Defaults to ".".
        """
        self.project_root = Path(project_root)
        self.assets_dir = self.project_root / "assets"
        
        # Initialize sub-managers
        self.sprite_generator = SpriteGenerator()
        self.asset_validator = AssetValidator(project_root)
        self.audio_manager = AudioManager(self.assets_dir / "audio")
        
        # Statistics
        self.stats = {
            "sprites_generated": 0,
            "audio_generated": 0,
            "assets_validated": 0,
            "issues_found": 0
        }
    
    def print_header(self, title: str):
        """
        Prints a formatted header to the console for better readability.

        Args:
            title (str): The title to be displayed in the header.
        """
        print(f"\n{'='*70}")
        print(f" {title}")
        print(f"{'='*70}")
    
    def check_all_assets(self) -> Dict[str, bool]:
        """
        Checks the status of all assets to identify any missing files.

        Returns:
            Dict[str, bool]: A dictionary summarizing the status of different
                             asset types and the overall status.
        """
        self.print_header("Asset Status Check")
        
        results = {}
        
        # Check sprites
        print("\n🎨 Checking Sprite Assets...")
        sprite_status = self.sprite_generator.check_existing_files()
        results["sprites"] = all(sprite_status.values())
        
        # Check audio
        print("\n🎵 Checking Audio Assets...")
        audio_status = self.audio_manager.check_files()
        results["audio"] = all(audio_status.values())
        
        # Overall status
        results["overall"] = results["sprites"] and results["audio"]
        
        if results["overall"]:
            print("\n🎉 All assets are present and ready!")
        else:
            print("\n⚠️  Some assets are missing or need attention.")
        
        return results
    
    def generate_all_assets(self, force: bool = False) -> bool:
        """
        Generates all missing assets, including sprites and audio.

        Args:
            force (bool, optional): If True, existing assets will be overwritten.
                                    Defaults to False.

        Returns:
            bool: True if all assets were generated successfully, False otherwise.
        """
        self.print_header("Generating All Assets")
        
        success = True
        
        # Generate sprites
        print("\n🎨 Generating Sprite Assets...")
        if self.sprite_generator.generate_all_sprites(force):
            print("✅ Sprite generation completed")
            self.stats["sprites_generated"] += 6  # All sprite files
        else:
            print("❌ Sprite generation failed")
            success = False
        
        # Generate audio
        print("\n🎵 Generating Audio Assets...")
        if self.audio_manager.generate_all_missing(force):
            print("✅ Audio generation completed")
            self.stats["audio_generated"] += 24  # All audio files
        else:
            print("❌ Audio generation failed")
            success = False
        
        return success
    
    def validate_all_assets(self) -> bool:
        """
        Validates all existing assets to ensure they meet project standards.

        Returns:
            bool: True if all assets are valid, False otherwise.
        """
        self.print_header("Validating All Assets")
        
        success = True
        
        # Validate sprites
        if not self.asset_validator.validate_sprites():
            success = False
        
        # Validate audio
        if not self.asset_validator.validate_audio():
            success = False
        
        # Generate report
        report = self.asset_validator.generate_asset_report()
        self.stats["assets_validated"] = report["valid_assets"]
        self.stats["issues_found"] = report["issues"]
        
        return success
    
    def organize_assets(self) -> bool:
        """
        Ensures the asset directory structure is correctly set up.

        Returns:
            bool: True if the organization was successful, False otherwise.
        """
        self.print_header("Organizing Asset Structure")
        
        try:
            # Ensure proper directory structure
            directories = [
                "assets/sprites/characters/player/png",
                "assets/audio/menu",
                "assets/audio/game",
                "assets/audio/backups"
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
                print(f"✅ Ensured directory: {directory}")
            
            # Move misplaced files (if any)
            # This could be expanded to handle specific file organization
            
            print("✅ Asset organization completed")
            return True
            
        except Exception as e:
            print(f"❌ Error organizing assets: {e}")
            return False
    
    def create_asset_preview(self) -> bool:
        """
        Creates preview images for visual assets like sprite sheets.

        Returns:
            bool: True if previews were created successfully, False otherwise.
        """
        self.print_header("Creating Asset Previews")
        
        success = True
        
        # Create sprite preview
        if self.sprite_generator.create_sprite_sheet_preview():
            print("✅ Sprite preview created")
        else:
            print("❌ Failed to create sprite preview")
            success = False
        
        # Could add audio waveform previews here
        
        return success
    
    def backup_assets(self) -> bool:
        """
        Creates backups of existing assets.

        Returns:
            bool: True if backups were created successfully, False otherwise.
        """
        self.print_header("Creating Asset Backups")
        
        success = True
        
        # Backup audio files
        if self.audio_manager.backup_files():
            print("✅ Audio files backed up")
        else:
            print("⚠️  No audio files to backup")
        
        # Could add sprite backup functionality here
        
        return success
    
    def print_statistics(self):
        """
        Prints a summary of the actions performed by the AssetManager.
        """
        self.print_header("Asset Management Statistics")
        
        print(f"🎨 Sprites Generated: {self.stats['sprites_generated']}")
        print(f"🎵 Audio Files Generated: {self.stats['audio_generated']}")
        print(f"✅ Assets Validated: {self.stats['assets_validated']}")
        print(f"🔧 Issues Found: {self.stats['issues_found']}")
        
        total_assets = self.stats['sprites_generated'] + self.stats['audio_generated']
        if total_assets > 0:
            print(f"\n📊 Total Assets Managed: {total_assets}")
        
        if self.stats['issues_found'] == 0:
            print("\n🎉 All assets are in perfect condition!")
        else:
            print(f"\n⚠️  {self.stats['issues_found']} issues need attention.")

def main():
    """
    Main function for the command-line interface of the AssetManager.

    This function parses command-line arguments and executes the corresponding
    asset management tasks.
    """
    parser = argparse.ArgumentParser(description="Runic Lands Unified Asset Manager")
    
    # Main operations
    parser.add_argument("--check", action="store_true", help="Check status of all assets")
    parser.add_argument("--generate", action="store_true", help="Generate all missing assets")
    parser.add_argument("--validate", action="store_true", help="Validate all assets")
    parser.add_argument("--organize", action="store_true", help="Organize asset structure")
    parser.add_argument("--preview", action="store_true", help="Create asset previews")
    parser.add_argument("--backup", action="store_true", help="Backup existing assets")
    
    # Comprehensive operations
    parser.add_argument("--setup", action="store_true", help="Complete asset setup (generate + validate + organize)")
    parser.add_argument("--maintain", action="store_true", help="Maintenance mode (check + validate + organize)")
    parser.add_argument("--full-reset", action="store_true", help="Full reset (backup + generate + validate)")
    
    # Options
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--project-root", type=str, default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    # Initialize asset manager
    manager = AssetManager(args.project_root)
    
    print("🛠️  Runic Lands Unified Asset Manager")
    print("="*70)
    
    # Execute operations
    if args.check or not any(vars(args).values()):
        manager.check_all_assets()
    
    if args.generate or args.setup or args.full_reset:
        manager.generate_all_assets(args.force)
    
    if args.validate or args.setup or args.maintain or args.full_reset:
        manager.validate_all_assets()
    
    if args.organize or args.setup or args.maintain:
        manager.organize_assets()
    
    if args.preview:
        manager.create_asset_preview()
    
    if args.backup or args.full_reset:
        manager.backup_assets()
    
    # Print statistics
    manager.print_statistics()
    
    print("\n✅ Asset management complete!")

if __name__ == "__main__":
    main()
