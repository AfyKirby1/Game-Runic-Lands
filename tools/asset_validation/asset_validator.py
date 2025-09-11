#!/usr/bin/env python3
"""
Asset Validation Tool for Runic Lands
Validates all game assets for correctness and completeness
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image
import wave
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class AssetValidator:
    """Comprehensive asset validation system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.assets_dir = self.project_root / "assets"
        
        # Validation results
        self.results = {
            "sprites": {"valid": 0, "invalid": 0, "missing": 0},
            "audio": {"valid": 0, "invalid": 0, "missing": 0},
            "total_issues": 0
        }
        
        # Expected asset structure
        self.expected_assets = {
            "sprites": {
                "characters/player/png/": [
                    "base_body.png",
                    "base_clothing.png", 
                    "base_wanderer.png",
                    "base_wanderer_idle.png",
                    "base_wanderer_walk.png",
                    "base_wanderer_attack.png"
                ]
            },
            "audio": {
                "": [
                    "menu_click.wav",
                    "menu_select.wav",
                    "attack.wav",
                    "menu_theme.wav"
                ],
                "menu/": [
                    f"menu_section{i}.wav" for i in range(1, 11)
                ],
                "game/": [
                    f"game_section{i}.wav" for i in range(1, 11)
                ]
            }
        }
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def validate_sprite_file(self, filepath: Path) -> Dict[str, Any]:
        """Validate a single sprite file"""
        result = {
            "valid": False,
            "issues": [],
            "properties": {}
        }
        
        if not filepath.exists():
            result["issues"].append("File does not exist")
            return result
        
        try:
            with Image.open(filepath) as img:
                result["properties"] = {
                    "size": img.size,
                    "mode": img.mode,
                    "format": img.format,
                    "file_size": filepath.stat().st_size
                }
                
                # Check basic requirements
                if img.mode != 'RGBA':
                    result["issues"].append(f"Wrong color mode: {img.mode} (expected RGBA)")
                
                # Check size based on file type
                if "idle" in filepath.name or "walk" in filepath.name or "attack" in filepath.name:
                    if img.size != (128, 32):
                        result["issues"].append(f"Wrong animation size: {img.size} (expected 128x32)")
                else:
                    if img.size != (32, 32):
                        result["issues"].append(f"Wrong sprite size: {img.size} (expected 32x32)")
                
                # Check if image has content (not all transparent)
                if img.mode == 'RGBA':
                    # Count non-transparent pixels
                    alpha_channel = img.split()[-1]
                    non_transparent = sum(1 for pixel in alpha_channel.getdata() if pixel > 0)
                    if non_transparent == 0:
                        result["issues"].append("Image is completely transparent")
                
                # Check file size (should be reasonable)
                if filepath.stat().st_size < 100:
                    result["issues"].append("File size suspiciously small")
                elif filepath.stat().st_size > 100000:  # 100KB
                    result["issues"].append("File size suspiciously large")
                
                if not result["issues"]:
                    result["valid"] = True
                    
        except Exception as e:
            result["issues"].append(f"Error reading image: {e}")
        
        return result
    
    def validate_audio_file(self, filepath: Path) -> Dict[str, Any]:
        """Validate a single audio file"""
        result = {
            "valid": False,
            "issues": [],
            "properties": {}
        }
        
        if not filepath.exists():
            result["issues"].append("File does not exist")
            return result
        
        try:
            with wave.open(str(filepath), 'rb') as wav_file:
                result["properties"] = {
                    "channels": wav_file.getnchannels(),
                    "sample_width": wav_file.getsampwidth(),
                    "frame_rate": wav_file.getframerate(),
                    "frames": wav_file.getnframes(),
                    "duration": wav_file.getnframes() / wav_file.getframerate(),
                    "file_size": filepath.stat().st_size
                }
                
                # Check basic requirements
                if wav_file.getnchannels() != 1:
                    result["issues"].append(f"Wrong channel count: {wav_file.getnchannels()} (expected 1)")
                
                if wav_file.getsampwidth() != 2:
                    result["issues"].append(f"Wrong sample width: {wav_file.getsampwidth()} (expected 2)")
                
                if wav_file.getframerate() != 44100:
                    result["issues"].append(f"Wrong sample rate: {wav_file.getframerate()} (expected 44100)")
                
                # Check duration (should be reasonable)
                duration = result["properties"]["duration"]
                if duration < 0.01:  # 10ms
                    result["issues"].append("Audio duration too short")
                elif duration > 60:  # 1 minute
                    result["issues"].append("Audio duration too long")
                
                # Check file size
                file_size = filepath.stat().st_size
                if file_size < 100:
                    result["issues"].append("File size suspiciously small")
                elif file_size > 10000000:  # 10MB
                    result["issues"].append("File size suspiciously large")
                
                if not result["issues"]:
                    result["valid"] = True
                    
        except Exception as e:
            result["issues"].append(f"Error reading audio file: {e}")
        
        return result
    
    def validate_sprites(self) -> bool:
        """Validate all sprite assets"""
        self.print_header("Validating Sprite Assets")
        
        sprite_dir = self.assets_dir / "sprites"
        if not sprite_dir.exists():
            print("❌ Sprites directory not found")
            return False
        
        all_valid = True
        
        for category, files in self.expected_assets["sprites"].items():
            category_dir = sprite_dir / category
            print(f"\n📁 Checking {category}:")
            
            for filename in files:
                filepath = category_dir / filename
                result = self.validate_sprite_file(filepath)
                
                if result["valid"]:
                    print(f"  ✅ {filename}: Valid ({result['properties']['size'][0]}x{result['properties']['size'][1]})")
                    self.results["sprites"]["valid"] += 1
                else:
                    print(f"  ❌ {filename}: Invalid")
                    for issue in result["issues"]:
                        print(f"      - {issue}")
                    self.results["sprites"]["invalid"] += 1
                    self.results["total_issues"] += 1
                    all_valid = False
                
                if not filepath.exists():
                    self.results["sprites"]["missing"] += 1
        
        return all_valid
    
    def validate_audio(self) -> bool:
        """Validate all audio assets"""
        self.print_header("Validating Audio Assets")
        
        audio_dir = self.assets_dir / "audio"
        if not audio_dir.exists():
            print("❌ Audio directory not found")
            return False
        
        all_valid = True
        
        for category, files in self.expected_assets["audio"].items():
            category_dir = audio_dir / category if category else audio_dir
            print(f"\n📁 Checking {category or 'root'}:")
            
            for filename in files:
                filepath = category_dir / filename
                result = self.validate_audio_file(filepath)
                
                if result["valid"]:
                    duration = result["properties"]["duration"]
                    print(f"  ✅ {filename}: Valid ({duration:.2f}s)")
                    self.results["audio"]["valid"] += 1
                else:
                    print(f"  ❌ {filename}: Invalid")
                    for issue in result["issues"]:
                        print(f"      - {issue}")
                    self.results["audio"]["invalid"] += 1
                    self.results["total_issues"] += 1
                    all_valid = False
                
                if not filepath.exists():
                    self.results["audio"]["missing"] += 1
        
        return all_valid
    
    def generate_asset_report(self) -> Dict[str, Any]:
        """Generate comprehensive asset report"""
        self.print_header("Asset Validation Report")
        
        total_assets = sum(
            len(files) for category in self.expected_assets.values() 
            for files in category.values()
        )
        
        valid_assets = (
            self.results["sprites"]["valid"] + 
            self.results["audio"]["valid"]
        )
        
        invalid_assets = (
            self.results["sprites"]["invalid"] + 
            self.results["audio"]["invalid"]
        )
        
        missing_assets = (
            self.results["sprites"]["missing"] + 
            self.results["audio"]["missing"]
        )
        
        print(f"📊 Total Expected Assets: {total_assets}")
        print(f"✅ Valid Assets: {valid_assets}")
        print(f"❌ Invalid Assets: {invalid_assets}")
        print(f"⚠️  Missing Assets: {missing_assets}")
        print(f"🔧 Total Issues: {self.results['total_issues']}")
        
        # Calculate health score
        if total_assets > 0:
            health_score = (valid_assets / total_assets) * 100
            print(f"\n🏆 Asset Health Score: {health_score:.1f}%")
            
            if health_score >= 90:
                print("🎉 Excellent! Your assets are in great shape!")
            elif health_score >= 70:
                print("👍 Good! Minor issues to address.")
            elif health_score >= 50:
                print("⚠️  Fair. Several issues need attention.")
            else:
                print("🚨 Poor. Major asset issues detected!")
        
        return {
            "total_assets": total_assets,
            "valid_assets": valid_assets,
            "invalid_assets": invalid_assets,
            "missing_assets": missing_assets,
            "health_score": health_score if total_assets > 0 else 0,
            "issues": self.results["total_issues"]
        }
    
    def save_report(self, filename: str = "asset_validation_report.json"):
        """Save validation report to file"""
        report = self.generate_asset_report()
        report_path = self.project_root / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to: {report_path}")

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Runic Lands Asset Validator")
    parser.add_argument("--sprites", action="store_true", help="Validate sprite assets only")
    parser.add_argument("--audio", action="store_true", help="Validate audio assets only")
    parser.add_argument("--all", action="store_true", help="Validate all assets (default)")
    parser.add_argument("--report", action="store_true", help="Generate and save validation report")
    parser.add_argument("--project-root", type=str, default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = AssetValidator(args.project_root)
    
    print("🔍 Runic Lands Asset Validator")
    print("="*60)
    
    # Execute validation
    if args.sprites or not any([args.sprites, args.audio]):
        validator.validate_sprites()
    
    if args.audio or not any([args.sprites, args.audio]):
        validator.validate_audio()
    
    # Generate report
    validator.generate_asset_report()
    
    if args.report:
        validator.save_report()

if __name__ == "__main__":
    main()
