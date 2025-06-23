# RunicMelodys Audio System

## Current Implementation (Updated April 2024)

### Audio Files Structure
Located in `assets/audio/`:
- `menu_click.wav` - UI interaction sound
- `game_theme.wav` - Combined game music theme
- `enhanced_game_theme.wav` - Enhanced version of game theme

Located in `assets/audio/game/`:
- `game_section1.wav` through `game_section10.wav` - Individual game music sections

### Game Music Sections
Each game section is 8 seconds long with distinct musical patterns:
1. `game_section1.wav` - Main theme introduction
2. `game_section2.wav` - E4-based progression
3. `game_section3.wav` - A3-based progression
4. `game_section4.wav` - G3-based progression
5. `game_section5.wav` - D4-based progression
6. `game_section6.wav` - F4-based progression
7. `game_section7.wav` - B3-based progression
8. `game_section8.wav` - E4-based progression
9. `game_section9.wav` - Additional variation
10. `game_section10.wav` - Final variation

## Generation System

### Tools
The game music is generated using `tools/generate_game_music.py`, which:
- Creates each section with precise musical notes
- Applies ADSR envelopes for smooth transitions
- Generates crossfades between sections
- Combines sections into complete themes
- Saves files in the correct format and location

### Note System
The generator uses musical notes in the A3-A5 range:
```
A3: 220.00 Hz
B3: 246.94 Hz
C4: 261.63 Hz
D4: 293.66 Hz
E4: 329.63 Hz
F4: 349.23 Hz
G4: 392.00 Hz
A4: 440.00 Hz
B4: 493.88 Hz
C5: 523.25 Hz
D5: 587.33 Hz
E5: 659.25 Hz
F5: 698.46 Hz
G5: 783.99 Hz
A5: 880.00 Hz
```

## Technical Specifications

### Audio Format
- Sample Rate: 44100 Hz (CD quality)
- Bit Depth: 16-bit
- Channels: Mono
- Format: WAV (uncompressed)
- Duration: 8.0 seconds per section

### ADSR Envelope Parameters
- Attack: 0.02 (2% of note duration)
- Decay: 0.1 (10% of note duration)
- Sustain: 0.8 (80% of peak amplitude)
- Release: 0.15 (15% of note duration)

### Crossfade System
- Duration: 150ms at start and end
- Type: Square root curve for natural fade
- Implementation: Section-wide envelope

## Troubleshooting

### Common Issues
1. **Files Not Generating**
   - Ensure numpy is installed: `pip install numpy`
   - Run as administrator if needed
   - Close any programs using the audio files
   - Use the PowerShell script to clean up properly

2. **Transitions Not Smooth**
   - Check crossfade duration
   - Verify note spacing
   - Ensure ADSR envelope parameters are appropriate

3. **Volume Issues**
   - Adjust amplitude constant
   - Check normalization
   - Verify sustain level

### Best Practices
1. **Creating Game Music**
   - Use lower octaves for game music (A3-A5 range)
   - Create longer sections (8 seconds)
   - Include more complex patterns
   - Ensure smooth transitions between sections

2. **Testing Changes**
   - Back up working files
   - Test individual sections
   - Check combined theme
   - Verify volume consistency

## Future Improvements
- Add dynamic music system
- Implement environmental audio
- Add more complex harmonies
- Support for different musical styles
- Real-time parameter adjustment
- GUI for music creation

## Overview
RunicMelodys is the complete audio management system for Runic Lands, providing a robust framework for dynamic music playback, sound effects, and audio settings. The system features seamless track transitions, sectioned music organization, and comprehensive debugging capabilities.

## Core Components

### Audio Files
Located in `assets/audio/`:
- `menu_theme.wav` - Main menu background music (original version)
- `enhanced_menu_theme.wav` - Enhanced version with structured RPG-style sections (combined track)
- `new_menu_theme.wav` - Latest version with continuous playback and seamless looping
- `menu_section1.wav` - Section 1: Heroic Intro
- `menu_section2.wav` - Section 2: Calm Town-like Section
- `menu_section3.wav` - Section 3: Energetic Battle-like Section
- `menu_section4.wav` - Section 4: Mystical Bridge transitioning from D minor to E minor
- `menu_section5.wav` - Section 5: Misty Woods Intro with atmospheric forest ambience
- `menu_click.wav` - UI interaction sound
- `menu_select.wav` - Menu navigation sound
- `attack.wav` - Player attack sound

### Music Queue System

The queue system enables gapless playback between music sections using pygame's music end events:

```python
# Set up the music end event detection
self.music_end_event = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(self.music_end_event)

# Track management variables
self.current_track = None  # Currently playing track
self.next_track = None     # Next track to play
self.music_queue = []      # Queue of additional tracks
```

#### Event Handling
The system processes end events to ensure continuous playback:

```python
def handle_music_event(self, event):
    if event.type == self.music_end_event:
        # Play the next queued track
        if self.next_track:
            next_to_play = self.next_track
            self.next_track = None
            self.play_music(next_to_play, loop=False)
            return True
        # If finished section4, transition to misty woods (section5)
        elif getattr(self, 'current_track', '') == 'menu_section4.wav':
            print(f"DEBUG: Moving to misty woods intro from resolving passage")
            self.play_music('assets/audio/menu_section5.wav', loop=False)
            return True
        # If finished section5, loop back to section1
        elif getattr(self, 'current_track', '') == 'menu_section5.wav':
            print(f"DEBUG: Looping back to section1 from misty woods intro")
            self.queue_section_music()
            return True
```

#### Usage
To use sectioned music playback:
```python
# Queue all sections to play in sequence
options.queue_section_music()

# Or manually with specific section:
options.play_music('assets/audio/menu_section5.wav', loop=False)  # Start with misty woods
options.play_music('assets/audio/menu_section1.wav', loop=False, queue=True)  # Queue heroic section
```

### Sectioned Track Organization

The RunicMelodys system organizes music into logical numbered sections:

1. **Section 1 (menu_section1.wav)** - Heroic intro with brass-like sounds
2. **Section 2 (menu_section2.wav)** - Calm, town-like section with gentle melody
3. **Section 3 (menu_section3.wav)** - Energetic section with bass line
4. **Section 4 (menu_section4.wav)** - Mystical Bridge transitioning from D minor to E minor
5. **Section 5 (menu_section5.wav)** - Misty Woods Intro with atmospheric forest ambience

The combined track `enhanced_menu_theme.wav` is still available for fallback.

#### Enhanced Menu Theme Structure
The enhanced menu theme features:
1. **Continuous Background Pad**: Runs throughout the entire track for coherence
2. **Five Musical Sections**: As listed above
3. **Seamless Transitions**: 0.25 second overlap between sections
4. **Time-Based Selection**: Starts with Misty Woods (Section 5) during evening/night (6PM-6AM), Heroic Intro (Section 1) during day
5. **Complete Loop Structure**: Section 5 loops back to Section 1

#### Section 4: Mystical Bridge
The Mystical Bridge section serves as a crucial transition point in the musical journey, shifting from the energetic Section 3 to the atmospheric Misty Woods section. Key characteristics include:

- **Harmonic Shift**: Transitions from D minor to E minor tonality
- **Counterpoint**: Features interweaving melodic lines that create a sense of mystery
- **Rich Bass Movement**: Uses alternating bass notes between D and E to establish the key change
- **Increased Vibrato**: Applied to create an otherworldly, mystical quality
- **Rising Melodic Contour**: Progresses upward to create anticipation for the Misty Woods section

#### Section 5: Misty Woods Intro
This atmospheric section evokes the feeling of being in the woods on a misty evening:

- **Soft, Resonant Pad**: Creates a bed of sound with subtle wind-like modulation
- **Delicate Harp-like Arpeggios**: Resembling dewdrops falling from leaves
- **Nature Sounds**: Incorporates distant owl calls and forest sounds
- **Muted Woodwind Melodies**: With spacious reverb creating depth and distance
- **Low String Bass Notes**: Adding depth and mystery
- **Key and Tempo**: E minor at 68 BPM for a contemplative, mysterious feel

The music generation code includes special functions to create realistic forest ambience and owl sounds, with careful attention to reverb and spatial positioning to create an immersive 3D audio environment.

### Debug Tracking System

The enhanced debug system logs these events:

#### Music Events
```
DEBUG: Music request - assets/audio/menu_section5.wav
DEBUG: Music started - menu_section5.wav
DEBUG: Next track ready - menu_section1.wav
DEBUG: Music ended - menu_section5.wav
DEBUG: Music stopped - menu_section4.wav
DEBUG: Moving to misty woods intro from resolving passage
```

#### Volume Events
```
DEBUG: Music volume changed - music_volume=0.70, effective=0.56
```

#### Queuing Events
```
DEBUG: Added to queue - menu_section3.wav
DEBUG: Queued 5 menu sections for continuous playback
```

### Audio Settings
Managed through the Options Menu (`OptionsSystem`):
- Master Volume (0-100%)
- Music Volume (0-100%)
- SFX Volume (0-100%)
- Music Mute Toggle

## Implementation

### OptionsSystem Audio Controls
```python
class OptionsSystem:
    def __init__(self):
        # Track current playing music for debugging
        self.current_track = None
        
        # Audio settings
        self.audio = {
            'master_volume': 0.7,  # 70% default
            'music_volume': 0.5,   # 50% default
            'sfx_volume': 0.8,     # 80% default
            'is_muted': False      # Music mute state
        }
```

### Playing Audio
```python
# Play music with automatic enhanced version detection
options.play_music('assets/audio/menu_theme.wav')  # Will prioritize new_menu_theme.wav, then enhanced_menu_theme.wav

# Play individual sections if needed
options.play_music('assets/audio/menu_section5.wav')  # Play just the misty woods intro

# Play sound effect
options.play_sound('menu_click')
```

### MenuSystem Integration
The `MenuSystem` class handles music management:

```python
def start_menu_music(self):
    """Start menu music using the section queue system"""
    if hasattr(self, 'options') and self.options:
        try:
            # Decide whether to start with heroic intro or misty woods based on time of day
            current_hour = datetime.datetime.now().hour
            if 18 <= current_hour or current_hour <= 6:  # Evening/night (6PM-6AM)
                self.options.play_music('assets/audio/menu_section5.wav', loop=False)
                # Queue the standard sequence after misty woods
                self.options.play_music('assets/audio/menu_section1.wav', loop=False, queue=True)
            else:
                self.options.queue_section_music()
        except Exception as e:
            print(f"Error using sectioned playback: {e}")
            self.options.play_music('assets/audio/menu_theme.wav')
```

The reset method restarts music when returning to the menu:

```python
def reset(self):
    self.state = GameState.MAIN_MENU
    self.setup_main_menu()
    
    # Restart menu music when returning to menu
    if hasattr(self, 'options') and self.options:
        self.start_menu_music()
```

### Game Integration
The main game initialization triggers sectioned music:

```python
# Start menu music by initiating the queue system
self.menu.start_menu_music()
```

### Queue Section Music Method
```python
def queue_section_music(self):
    """Queue all menu sections to play in sequence without gaps"""
    try:
        # Clear any existing queue
        self.next_track = None
        self.music_queue = []
        
        # Create a seamless sequence of all five sections
        base_path = "assets/audio/"
        
        # Determine starting section based on time of day if datetime is available
        try:
            import datetime
            current_hour = datetime.datetime.now().hour
            if 18 <= current_hour or current_hour <= 6:  # Evening/night (6PM-6AM)
                first_section = f"{base_path}menu_section5.wav"  # Start with misty woods at night
                start_index = 5
            else:
                first_section = f"{base_path}menu_section1.wav"  # Start with heroic intro during day
                start_index = 1
        except ImportError:
            # Fallback if datetime not available
            first_section = f"{base_path}menu_section1.wav"
            start_index = 1
        
        # Define all sections
        all_sections = [
            f"{base_path}menu_section1.wav",  # Heroic Intro
            f"{base_path}menu_section2.wav",  # Calm Town-like Section
            f"{base_path}menu_section3.wav",  # Energetic Battle-like Section
            f"{base_path}menu_section4.wav",  # Mystical Bridge
            f"{base_path}menu_section5.wav",  # Misty Woods Intro
        ]
        
        # Start with the determined first section
        self.play_music(first_section, loop=False)
        
        # Queue the rest of the sections in order (wrapping around if needed)
        if start_index in [1, 5]:  # Valid starting sections
            # Queue remaining sections in order
            for i in range(1, len(all_sections)):
                section_index = (start_index - 1 + i) % len(all_sections)
                self.music_queue.append(all_sections[section_index])
        
        print(f"DEBUG: Queued {len(all_sections)} menu sections for continuous playback")
        return True
    except Exception as e:
        print(f"Error queuing sections: {e}")
        # Fallback to continuous track
        self.play_music('assets/audio/menu_theme.wav')
        return False
```

### Volume Control
```python
# Set individual volume levels
options.set_volume('master_volume', 0.7)
options.set_volume('music_volume', 0.5)
options.set_volume('sfx_volume', 0.8)

# Toggle music mute
options.toggle_mute()
```

## Enhanced Audio Generation

The RunicMelodys system includes a sophisticated audio generation component in `assets/audio/new/enhanced_music.py` that dynamically creates themed music and sound effects.

### Menu Theme Generation
```python
def generate_menu_theme(duration=36.0):  # Extended to accommodate 5 sections
    # Create continuous background pad
    pad = generate_ambient_pad(duration)
    
    # Calculate section timing with fixed overlaps
    section_length = (duration - 2.0) / 5  # Reserve 2s for final crossfade, now 5 sections
    fixed_overlap = 0.25  # Brief 0.25s overlap between sections
    
    # Generate each numbered section and save individual files
    section1_signal = generate_section(intro_start, intro_end, intro_pattern)
    wavfile.write("menu_section1.wav", SAMPLE_RATE, section1_audio)
    
    section2_signal = generate_section(a_section_start, a_section_end, a_section_pattern)
    wavfile.write("menu_section2.wav", SAMPLE_RATE, section2_audio)
    
    section3_signal = generate_section(b_section_start, b_section_end, b_section_pattern)
    wavfile.write("menu_section3.wav", SAMPLE_RATE, section3_audio)
    
    section4_signal = generate_section(resolve_start, resolve_end, resolve_pattern)
    wavfile.write("menu_section4.wav", SAMPLE_RATE, section4_audio)
    
    section5_signal = generate_misty_woods_section(misty_start, misty_end)
    wavfile.write("menu_section5.wav", SAMPLE_RATE, section5_audio)
    
    # Apply extended 2-second crossfade between end and beginning for combined track
    apply_seamless_loop_crossfade(signal, crossfade_duration=2.0)
    
    # Save combined version
    wavfile.write("enhanced_menu_theme.wav", SAMPLE_RATE, audio)
```

### Misty Woods Section Generation
```python
def generate_misty_woods_section(start_time, end_time, key='Em', tempo=68):
    """Generate the misty woods section with forest atmosphere"""
    # Create base track with forest ambience
    forest_pad = generate_atmospheric_pad(
        duration=end_time - start_time,
        base_freq=77.78,  # E2 note
        harmonics=[1.0, 0.5, 0.25, 0.125],  # Rich harmonic content
        mod_depth=0.08,  # Subtle modulation
        mod_rate=0.2,   # Slow modulation rate
    )
    
    # Add harp-like arpeggios
    harp_notes = [
        # E minor scale notes (E, G, B, D)
        {'pitch': 'E4', 'start': 0.5, 'duration': 0.5, 'volume': 0.4},
        {'pitch': 'G4', 'start': 1.0, 'duration': 0.5, 'volume': 0.3},
        {'pitch': 'B4', 'start': 1.5, 'duration': 0.5, 'volume': 0.25},
        {'pitch': 'D5', 'start': 2.0, 'duration': 0.5, 'volume': 0.2},
        # Repeating pattern with variation
        {'pitch': 'E5', 'start': 2.5, 'duration': 0.75, 'volume': 0.15},
        {'pitch': 'B4', 'start': 3.25, 'duration': 0.5, 'volume': 0.2},
        {'pitch': 'G4', 'start': 3.75, 'duration': 0.5, 'volume': 0.25},
        {'pitch': 'E4', 'start': 4.25, 'duration': 0.75, 'volume': 0.3},
        # Continue pattern...
    ]
    harp_signal = generate_arpeggio(harp_notes, attack=0.1, decay=0.6, sample_rate=SAMPLE_RATE)
    
    # Add forest sound effects
    owl_call = generate_owl_sound(volume=0.15, reverb=0.7)
    forest_sounds = place_sound_effects([
        {'sound': owl_call, 'time': 2.0, 'volume': 0.15},
        {'sound': owl_call, 'time': 5.5, 'volume': 0.1},
        {'sound': generate_wind_through_leaves(), 'time': 1.0, 'volume': 0.08},
        {'sound': generate_wind_through_leaves(), 'time': 4.0, 'volume': 0.06},
    ], duration=end_time - start_time)
    
    # Add woodwind melody
    woodwind_notes = create_modal_melody('E', 'natural_minor', octave=4, note_count=8)
    woodwind = generate_woodwind_melody(woodwind_notes, volume=0.35, reverb=0.6)
    
    # Mix all elements with appropriate volumes
    mixed_signal = mix_audio_signals([
        (forest_pad, 0.7),
        (harp_signal, 0.5),
        (forest_sounds, 0.3),
        (woodwind, 0.4)
    ])
    
    # Apply subtle reverb for forest space simulation
    misty_woods_audio = apply_reverb(mixed_signal, room_size=0.8, damping=0.5, wet_level=0.4)
    
    return misty_woods_audio
```

### Game Theme Features
The enhanced game theme includes:
- Complex melody with 16-note pattern
- Complementary counter-melody
- Deep resonant bass line
- Atmospheric pad with slow modulation
- Smooth transitions with 0.5-second crossfades

## Detection System
The system supports automatic enhanced version detection through `_get_enhanced_version()`:

```python
def _get_enhanced_version(self, music_file):
    # Check for enhanced versions in priority order:
    # 1. new_menu_theme.wav (for menu theme)
    # 2. enhanced_[filename].wav
    # 3. Original file as fallback
```

## UI Integration

### Audio Options Menu
The audio settings are accessible through the Options Menu:
- Volume sliders for master, music, and SFX
- Mute toggle button for music
- Settings are saved automatically
- Changes are applied in real-time

### Sound Effect Integration
Sound effects are played on various UI interactions:
- Menu navigation
- Button clicks
- Game events (attacks, item pickups, etc.)

## Testing and Quality Assurance

The RunicMelodys system has been tested for:

1. **Gapless Playback** - No noticeable gaps between sections
2. **Proper Looping** - Sections flow seamlessly into each other with intelligent routing
3. **Debug Output** - Comprehensive logging of all audio events
4. **Fallback Behavior** - Works even if some section files are missing
5. **Time-Based Selection** - Correctly plays Misty Woods section during evening hours

## Best Practices

### Volume Management
- Always respect the user's volume settings
- Apply master volume as a multiplier to other volumes
- Use normalized audio files (peak at -3dB)
- Implement smooth volume transitions

### Audio Loading
- Preload frequently used sound effects
- Load music on demand
- Support fallback to basic versions if enhanced not available
- Handle missing audio files gracefully

### Audio Generation
- Use brief transitions between sections (0.25s recommended)
- Use extended crossfades (2+ seconds) for seamless looping
- Maintain consistent key and tempo
- Use continuous background elements for coherence

### Debug Tracking
- Always log music requests, starts, and stops
- Track the current playing track with `self.current_track`
- Log effective volume when volume settings change
- Use consistent DEBUG: prefix for audio log messages

### Performance
- Use appropriate sample rates (44.1kHz standard)
- Compress audio files when possible
- Limit simultaneous sound effects
- Monitor memory usage

## Future Enhancements

- **Dynamic Section Selection** - Play different section combinations based on game state
- **Adaptive Music Intensity** - Change music elements based on game action
- **Cross-section Mixing** - Real-time crossfading between sections
- **Sound Spatialization** - Positional audio for in-game sounds
- **More Enhanced Music Variations** - Additional themes for different game areas
- **Audio Streaming** - Stream longer tracks for memory efficiency
- **Sound Effect Pooling** - Reuse sound effect instances for better performance
- **Real-time Audio Effects** - Add reverb, echo, etc. based on environment
- **Day/Night Music Variations** - More sophisticated time-based music selection 