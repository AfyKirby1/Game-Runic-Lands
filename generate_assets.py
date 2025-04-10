#!/usr/bin/env python
"""
Asset Generation Script
Run this script to generate all game assets.
"""

import argparse
from utils.generators import (
    generate_base_character,
    generate_idle_animation,
    generate_walking_animation,
    generate_attack_animation,
    generate_menu_select_sound,
    generate_menu_click_sound,
    generate_attack_sound,
    generate_background_music,
    generate_all_game_assets
)

def main():
    """Main function to parse arguments and generate assets."""
    parser = argparse.ArgumentParser(description="Generate game assets")
    parser.add_argument('--sprites-only', action='store_true', help='Generate only sprite assets')
    parser.add_argument('--audio-only', action='store_true', help='Generate only audio assets')
    parser.add_argument('--all', action='store_true', help='Generate all assets (default)')
    
    args = parser.parse_args()
    
    # If no specific flags are set, generate all assets
    if not (args.sprites_only or args.audio_only):
        args.all = True
    
    if args.all:
        generate_all_game_assets()
        return
    
    if args.sprites_only:
        print("Generating character sprites...")
        base_sprite = generate_base_character()
        generate_idle_animation(base_sprite)
        generate_walking_animation(base_sprite)
        generate_attack_animation(base_sprite)
        print("Sprite generation complete!")
    
    if args.audio_only:
        print("Generating audio assets...")
        generate_menu_select_sound()
        generate_menu_click_sound()
        generate_attack_sound()
        generate_background_music("menu_theme.wav", duration=5.0, base_freq=220)
        generate_background_music("game_theme.wav", duration=8.0, base_freq=196)
        print("Audio generation complete!")

if __name__ == "__main__":
    main() 