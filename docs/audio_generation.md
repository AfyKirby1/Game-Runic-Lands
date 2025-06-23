# Audio Generation Tools Documentation

## Overview
This document explains how to use the audio generation tools for Runic Lands. These tools are used to generate various sound effects and music for the game.

## Music System Overview

### Menu Music System
- Located in: `assets/audio/`
- Files: `menu_section1.wav` through `menu_section10.wav`
- Each section is 2 seconds long (88,200 frames @ 44.1kHz)
- Sections play in sequence to create a continuous menu background music
- Total unique music: 20 seconds (loops seamlessly)
- The system automatically transitions between sections

### Game Music System
- Located in: `assets/audio/game/`
- Files: `game_section1.wav` through `game_section10.wav`
- Each section is 8 seconds long (352,800 frames @ 44.1kHz)
- Different themes for various game situations:
  - Sections 1-2: Exploration themes (Forest, Village)
  - Sections 3-4: Mystery/Discovery themes (Ruins, Cave)
  - Sections 5-6: Adventure/Journey themes (Mountain, Ocean)
  - Sections 7-8: Tension/Mystery themes (Dark Forest, Storm)
  - Sections 9-10: Triumph/Resolution themes (Victory, Quest)
- Total unique music: 80 seconds
- The system automatically transitions between sections

### Adding Your Own Music
To add your own music to the game:

1. **Menu Music**: 
   - Create WAV files named `menu_section1.wav` through `menu_section10.wav`
   - Place in the `assets/audio/` directory
   - Each file should be exactly 2 seconds long
   - Use 44.1kHz, 16-bit audio format
   - The system will detect and use your files automatically

2. **Game Music**:
   - Create WAV files named `game_section1.wav` through `game_section10.wav`
   - Place in the `assets/audio/game/` directory
   - Each file should be exactly 8 seconds long
   - Use 44.1kHz, 16-bit audio format
   - The system will detect and use your files automatically

3. **Legacy Combined Themes**:
   - `game_theme.wav`: Can be used as a fallback if section files are missing
   - Length should be 80 seconds (10 sections × 8 seconds)

## Technical Details

### Sectioned Music System
The game uses a sectioned music system with the following advantages:
- Precise control over transitions between music segments
- Easy to update individual sections without affecting others
- Automatic rebuilding of the music queue when needed
- Fallback to complete themes if sections are missing

### How It Works
1. The system checks for available section files
2. Sections are played in sequence, with automatic transitions
3. Each section plays until completion, then triggers the next section
4. When all sections have played, the sequence repeats
5. The system uses pygame's USEREVENT to handle music transitions

### Creating Compatible Music
When creating music:
- Ensure consistent tempo between sections for smooth transitions
- Maintain the same audio format (44.1kHz, 16-bit WAV)
- Match the exact duration requirements (2s for menu music, 8s for game music)
- Consider adding subtle crossfades between sections (final 100ms of each section)

## Available Tools

### 1. Menu Music Generator
Location: `tools/audio/generate_menu_music.py`
- Generates menu music sections
- Creates 10 different menu music sections
- Uses pentatonic scale for pleasant melodies
- Output location: `assets/audio/`

When to use:
- When you need new menu background music
- When you want to change the menu music style
- When menu music sections are missing or corrupted

Usage:
```powershell
# Using PowerShell
.\tools\audio\generate_menu_music.ps1

# Using Batch file
.\tools\audio\generate_menu_music.bat
```

### 2. Game Music Generator
Location: `tools/audio/generate_game_music.py`
- Generates game background music sections
- Creates 10 different game music sections
- Each section has a unique theme and mood
- Output location: `assets/audio/game/`

When to use:
- When you need new game background music
- When you want to change the game music style
- When game music sections are missing or corrupted

Usage:
```powershell
# Using PowerShell
.\tools\audio\generate_game_music.ps1
```

### 3. Sound Effects Generator
Location: `tools/audio/generate_audio.py`
- Generates various sound effects and combined game theme
- Creates:
  - `menu_click.wav` - Menu interaction sound (13KB)
  - `menu_select.wav` - Menu selection sound (8.7KB)
  - `attack.wav` - Combat attack sound (26KB)
  - `game_theme.wav` - Combined game theme (689KB)
- Output location: `assets/audio/`

When to use:
- When you need new sound effects
- When sound effects are missing or corrupted
- When you want to change the sound effects style
- When you need to regenerate the combined game theme

Usage:
```powershell
python tools/audio/generate_audio.py
```

## File Structure
```
assets/audio/
├── menu_click.wav          # Menu click sound effect (13KB)
├── menu_select.wav         # Menu selection sound effect (8.7KB)
├── attack.wav             # Attack sound effect (26KB)
├── game_theme.wav         # Combined game theme (689KB)
├── menu_section1.wav      # Menu music sections (172KB each)
├── menu_section2.wav
├── ...
├── menu_section10.wav
└── game/                  # Game music sections (689KB each)
    ├── game_section1.wav  # Forest Exploration theme
    ├── game_section2.wav  # Village theme
    ├── game_section3.wav  # Ancient Ruins theme
    ├── game_section4.wav  # Cave Discovery theme
    ├── game_section5.wav  # Mountain Path theme
    ├── game_section6.wav  # Ocean Journey theme
    ├── game_section7.wav  # Dark Forest theme
    ├── game_section8.wav  # Approaching Storm theme
    ├── game_section9.wav  # Victory Fanfare theme
    └── game_section10.wav # Quest Completion theme
```

## Dependencies
- Python 3.x
- numpy
- pygame (for audio playback)

## Installation
1. Install Python 3.x if not already installed
2. Install required packages:
```powershell
pip install numpy pygame
```

## Troubleshooting
1. If files are locked:
   - Close any programs using the audio files
   - Run the cleanup scripts first
   - Try running as administrator

2. If generation fails:
   - Check Python and package versions
   - Ensure output directories exist
   - Check file permissions

3. If music stops after one or two sections:
   - Check that pygame events are being properly processed in the main game loop
   - Verify that pygame.mixer.music.set_endevent(pygame.USEREVENT + 1) is set
   - Make sure the Game.handle_input() method properly passes events to the options_system

4. If specific files are missing:
   - Run the appropriate generator script
   - Check the output directory
   - Verify file names match expected patterns

## Notes
- Always backup existing audio files before generating new ones
- Generated files are in WAV format for best quality
- Some tools may require administrator privileges
- Each generator creates specific files - use the appropriate one for your needs 