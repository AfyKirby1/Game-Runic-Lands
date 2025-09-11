#!/usr/bin/env python3
"""
Modern Sprite Generation Tool for Runic Lands
Unified tool for generating all character sprites and animations
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.generators import (
    generate_base_character,
    generate_idle_animation,
    generate_walking_animation,
    generate_attack_animation,
    COLORS
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SpriteGenerator:
    """Modern sprite generation system with validation and error handling"""
    
    def __init__(self, output_dir: str = "assets/sprites/characters/player/png"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Expected output files
        self.expected_files = {
            "base_body.png": "Base character body layer",
            "base_clothing.png": "Base character clothing layer", 
            "base_wanderer.png": "Combined base character",
            "base_wanderer_idle.png": "Idle animation (4 frames)",
            "base_wanderer_walk.png": "Walking animation (4 frames)",
            "base_wanderer_attack.png": "Attack animation (4 frames)"
        }
        
        # Generation statistics
        self.stats = {
            "generated": 0,
            "skipped": 0,
            "errors": 0
        }
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def check_existing_files(self) -> Dict[str, bool]:
        """Check which sprite files already exist"""
        self.print_header("Checking Existing Sprite Files")
        
        status = {}
        missing_files = []
        
        for filename, description in self.expected_files.items():
            filepath = self.output_dir / filename
            exists = filepath.exists()
            status[filename] = exists
            
            if exists:
                size = filepath.stat().st_size
                print(f"✅ {filename}: Found ({description}) - {size} bytes")
            else:
                print(f"❌ {filename}: MISSING ({description})")
                missing_files.append(filename)
        
        if missing_files:
            print(f"\n⚠️  {len(missing_files)} files are missing")
        else:
            print(f"\n🎉 All {len(self.expected_files)} sprite files found!")
            
        return status
    
    def validate_generated_files(self) -> bool:
        """Validate that generated files are proper images"""
        self.print_header("Validating Generated Files")
        
        valid_count = 0
        total_count = 0
        
        for filename in self.expected_files.keys():
            filepath = self.output_dir / filename
            if not filepath.exists():
                continue
                
            total_count += 1
            
            try:
                with Image.open(filepath) as img:
                    # Check basic properties
                    if img.mode != 'RGBA':
                        print(f"⚠️  {filename}: Wrong mode ({img.mode}, expected RGBA)")
                        continue
                    
                    if img.size != (32, 32) and 'idle' not in filename and 'walk' not in filename and 'attack' not in filename:
                        print(f"⚠️  {filename}: Wrong size ({img.size}, expected 32x32)")
                        continue
                    
                    # Check for animation sheets
                    if any(anim in filename for anim in ['idle', 'walk', 'attack']):
                        if img.size != (128, 32):  # 4 frames * 32 width
                            print(f"⚠️  {filename}: Wrong animation size ({img.size}, expected 128x32)")
                            continue
                    
                    print(f"✅ {filename}: Valid ({img.size[0]}x{img.size[1]}, {img.mode})")
                    valid_count += 1
                    
            except Exception as e:
                print(f"❌ {filename}: Invalid image file - {e}")
        
        print(f"\n📊 Validation: {valid_count}/{total_count} files are valid")
        return valid_count == total_count
    
    def generate_base_sprites(self, force: bool = False) -> bool:
        """Generate base character sprites"""
        self.print_header("Generating Base Character Sprites")
        
        try:
            base_sprite = generate_base_character(str(self.output_dir))
            self.stats["generated"] += 3  # base_body, base_clothing, base_wanderer
            print("✅ Base character sprites generated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error generating base sprites: {e}")
            self.stats["errors"] += 1
            return False
    
    def generate_animations(self, force: bool = False) -> bool:
        """Generate all character animations"""
        self.print_header("Generating Character Animations")
        
        # Check if base sprite exists
        base_sprite_path = self.output_dir / "base_wanderer.png"
        if not base_sprite_path.exists():
            print("❌ Base wanderer sprite not found. Generate base sprites first.")
            return False
        
        try:
            # Load base sprite
            base_sprite = Image.open(base_sprite_path)
            
            # Generate animations
            generate_idle_animation(base_sprite, str(self.output_dir))
            print("✅ Idle animation generated")
            
            generate_walking_animation(base_sprite, str(self.output_dir))
            print("✅ Walking animation generated")
            
            generate_attack_animation(base_sprite, str(self.output_dir))
            print("✅ Attack animation generated")
            
            self.stats["generated"] += 3
            return True
            
        except Exception as e:
            logger.error(f"Error generating animations: {e}")
            self.stats["errors"] += 1
            return False
    
    def generate_all_sprites(self, force: bool = False) -> bool:
        """Generate all sprite assets"""
        self.print_header("Generating All Sprite Assets")
        
        success = True
        
        # Generate base sprites
        if not self.generate_base_sprites(force):
            success = False
        
        # Generate animations
        if not self.generate_animations(force):
            success = False
        
        # Validate results
        if success:
            self.validate_generated_files()
        
        return success
    
    def create_sprite_sheet_preview(self) -> bool:
        """Create a preview sprite sheet showing all animations"""
        self.print_header("Creating Sprite Sheet Preview")
        
        try:
            # Load all animation files
            idle_sheet = Image.open(self.output_dir / "base_wanderer_idle.png")
            walk_sheet = Image.open(self.output_dir / "base_wanderer_walk.png")
            attack_sheet = Image.open(self.output_dir / "base_wanderer_attack.png")
            base_sprite = Image.open(self.output_dir / "base_wanderer.png")
            
            # Create preview sheet (base + 3 animation rows)
            preview = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
            
            # Add base sprite (top left)
            preview.paste(base_sprite, (0, 0))
            
            # Add idle animation (top right)
            preview.paste(idle_sheet, (32, 0))
            
            # Add walking animation (bottom left)
            preview.paste(walk_sheet, (0, 32))
            
            # Add attack animation (bottom right)
            preview.paste(attack_sheet, (32, 32))
            
            # Add labels
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(preview)
            
            # Try to use a default font, fallback to basic if not available
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            labels = [
                ("Base", 0, 0),
                ("Idle", 32, 0),
                ("Walk", 0, 32),
                ("Attack", 32, 32)
            ]
            
            for text, x, y in labels:
                draw.text((x + 2, y + 2), text, fill=(255, 255, 255, 255), font=font)
                draw.text((x + 1, y + 1), text, fill=(0, 0, 0, 255), font=font)
            
            # Save preview
            preview_path = self.output_dir / "sprite_preview.png"
            preview.save(preview_path)
            print(f"✅ Sprite preview created: {preview_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating sprite preview: {e}")
            return False
    
    def print_statistics(self):
        """Print generation statistics"""
        self.print_header("Generation Statistics")
        
        print(f"📊 Generated: {self.stats['generated']} files")
        print(f"⏭️  Skipped: {self.stats['skipped']} files")
        print(f"❌ Errors: {self.stats['errors']} files")
        
        if self.stats['errors'] == 0:
            print("\n🎉 All sprite generation completed successfully!")
        else:
            print(f"\n⚠️  {self.stats['errors']} errors occurred during generation")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Runic Lands Sprite Generator")
    parser.add_argument("--check", action="store_true", help="Check existing sprite files")
    parser.add_argument("--validate", action="store_true", help="Validate existing sprite files")
    parser.add_argument("--generate-base", action="store_true", help="Generate base character sprites")
    parser.add_argument("--generate-animations", action="store_true", help="Generate character animations")
    parser.add_argument("--generate-all", action="store_true", help="Generate all sprite assets")
    parser.add_argument("--preview", action="store_true", help="Create sprite sheet preview")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--output-dir", type=str, default="assets/sprites/characters/player/png",
                       help="Output directory for sprites")
    
    args = parser.parse_args()
    
    # Initialize sprite generator
    generator = SpriteGenerator(args.output_dir)
    
    print("🎨 Runic Lands Sprite Generator")
    print("="*60)
    
    # Execute requested operations
    if args.check or not any(vars(args).values()):
        generator.check_existing_files()
    
    if args.validate:
        generator.validate_generated_files()
    
    if args.generate_base or args.generate_all:
        generator.generate_base_sprites(args.force)
    
    if args.generate_animations or args.generate_all:
        generator.generate_animations(args.force)
    
    if args.preview:
        generator.create_sprite_sheet_preview()
    
    # Print statistics
    generator.print_statistics()

if __name__ == "__main__":
    main()
