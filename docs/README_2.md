# Runic Lands Audio System

## Overview
Runic Lands features a sophisticated procedural music generation system that creates dynamic, seamless background music for both the menu and in-game environments. The system uses Python with NumPy to synthesize musical notes and create smooth transitions between sections.

## How the Music Generation System Works

### 1. Basic Setup
- Uses Python with NumPy for audio synthesis
- CD quality audio (44,100 samples per second)
- 16-bit depth for high-quality sound
- Mono audio for consistent playback

### 2. Note Creation Process
Each musical note is created through these steps:
1. **Sine Wave Generation**
   - Creates a pure tone at the note's frequency
   - Example: C5 = 523.25 Hz, D5 = 587.33 Hz

2. **ADSR Envelope Application**
   - Attack (20ms): Note starts softly
   - Decay (100ms): Volume drops slightly
   - Sustain (80%): Holds at steady volume
   - Release (150ms): Smooth fade out

### 3. Section Building
Each music section is constructed as follows:

#### Menu Music Sections
- Duration: 2 seconds
- Contains: 8 distinct notes
- Note Duration: 220ms per note
- Spacing: Small gaps between notes
- Crossfades: 100ms at start and end

#### Game Music Sections
- Duration: 8 seconds
- Contains: More complex patterns
- Note Duration: Varies by pattern type
- Spacing: Adjusted for atmosphere
- Crossfades: 150ms at start and end

### 4. Musical Patterns
The system supports different musical patterns:

#### Menu Patterns
1. **Ascending Scale**
   - Example: C5 → D5 → E5 → F5 → G5 → A5 → B4 → C5
   - Creates an uplifting, heroic feel

2. **Arpeggio Pattern**
   - Example: C5 → E5 → G5 → C5 → E5 → G5 → B4 → C5
   - Creates a calm, town-like atmosphere

3. **Wave Pattern**
   - Example: E5 → D5 → C5 → B4 → C5 → D5 → E5 → F5
   - Creates smooth, flowing melodies

#### Game Patterns
1. **Melodic Patterns**
   - Regular note spacing
   - Clear musical phrases
   - Used for exploration themes

2. **Atmospheric Patterns**
   - Overlapping notes
   - Longer durations
   - Used for environmental themes

3. **Rhythmic Patterns**
   - Distinct note spacing
   - Stronger emphasis
   - Used for action themes

### 5. File Generation Process
1. **Audio Data Creation**
   - Notes are generated and combined
   - Envelopes are applied
   - Crossfades are added

2. **File Saving**
   - Data is normalized to prevent distortion
   - Converted to 16-bit PCM
   - Saved as WAV files
   - Stored in appropriate directories

## Music Generation System

### Menu Music
The menu music consists of 10 distinct sections, each 2 seconds long, that play in sequence:

1. `menu_section1.wav` - Heroic Intro (Ascending scale)
2. `menu_section2.wav` - Calm Town-like Section (Arpeggio pattern)
3. `menu_section3.wav` - Energetic Battle-like Section (Descending scale)
4. `menu_section4.wav` - Resolving Passage (Melodic pattern)
5. `menu_section5.wav` - Misty Woods Intro (Complex melody)
6. `menu_section6.wav` - Descending Arpeggio
7. `menu_section7.wav` - Wave Pattern
8. `menu_section8.wav` - Cascading
9. `menu_section9.wav` - Mountain
10. `menu_section10.wav` - Wandering

Each section features:
- 8 distinct musical notes
- 44.1kHz, 16-bit mono audio quality
- ADSR envelope for smooth note transitions
- 100ms crossfades at start/end
- Precise timing and spacing between notes

### Game Music
The in-game music consists of 10 sections, each 8 seconds long, with different thematic variations:

1. `game_section1.wav` - Forest Exploration
2. `game_section2.wav` - Village Theme
3. `game_section3.wav` - Ancient Ruins
4. `game_section4.wav` - Cave Discovery
5. `game_section5.wav` - Mountain Path
6. `game_section6.wav` - Ocean Journey
7. `game_section7.wav` - Dark Forest
8. `game_section8.wav` - Approaching Storm
9. `game_section9.wav` - Victory Fanfare
10. `game_section10.wav` - Quest Completion

Game music features:
- Longer duration (8 seconds per section)
- More complex musical patterns
- Atmospheric and rhythmic variations
- 150ms crossfades for smoother transitions
- Lower octave notes for deeper atmosphere

## Sound Effects
- `menu_select.wav` - Hover over menu items
- `menu_click.wav` - Click menu items
- `attack.wav` - Player attack sound

## Generating Music
To generate all music sections:

1. Run the menu music generator:
```powershell
cd tools
powershell -ExecutionPolicy Bypass -File .\generate_menu_music.ps1
```

2. Run the game music generator:
```powershell
cd tools
powershell -ExecutionPolicy Bypass -File .\generate_game_music.ps1
```

## Technical Specifications

### Audio Format
- Sample Rate: 44.1kHz (CD quality)
- Bit Depth: 16-bit
- Channels: Mono
- Format: WAV (uncompressed)

### Envelope Parameters
- Attack: 20-30ms
- Decay: 100-150ms
- Sustain: 65-80% of peak amplitude
- Release: 150-250ms

### Crossfade System
- Menu Music: 100ms crossfade
- Game Music: 150ms crossfade
- Type: Square root curve for natural fade

## Music Player
The game includes an in-game music player that allows you to:
- Browse all available tracks
- Play/pause music
- Switch between tracks
- Adjust volume
- View track descriptions

## Troubleshooting
If you experience issues with music playback:
1. Ensure all section files exist in the correct directories
2. Check file permissions
3. Verify audio settings in the options menu
4. Restart the game if music stops playing

For more detailed information about the music system, refer to:
- `docs/AudioSystem.md`
- `docs/MenuMusicSystem.md`

Note: You'll need to provide your own audio files or use royalty-free ones. 
Some good resources for free game audio:
- OpenGameArt.org
- FreeSounds.org
- incompetech.com (for music)

## Musical Inspiration
Our music system is designed to complement Runic Lands' soothing 2D pixel art RPG/adventure style. The musical approach draws inspiration from:

### Core Musical Philosophy
- **Gentle Progression**: Like the game's pixel art, our music uses simple, clear musical elements that build into something greater
- **Organic Flow**: Natural transitions and smooth melodies mirror the game's exploration-focused gameplay
- **Emotional Resonance**: Each section tells a small story, much like the game's narrative moments

### Influences
1. **Classic RPG Soundtracks**
   - The gentle, memorable melodies of early Final Fantasy games
   - The atmospheric exploration themes from Chrono Trigger
   - The peaceful town themes from Dragon Quest

2. **Nature-Inspired Elements**
   - Flowing water-like arpeggios
   - Wind-like sustained notes
   - Forest-like harmonic patterns

3. **Pixel Art Synergy**
   - Simple, clear musical phrases that match the visual style
   - Precise timing that complements the game's pixel-perfect animations
   - Careful use of space and silence, like the intentional empty pixels in our art

### Design Goals
- Create a sense of wonder and discovery
- Support long play sessions without fatigue
- Provide subtle emotional cues without overwhelming the player
- Maintain consistency with the game's pixel art aesthetic
- Allow for smooth transitions between different game states 