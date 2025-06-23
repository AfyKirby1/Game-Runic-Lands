# Runic Lands Menu Music System

## Current Implementation (Updated April 2024)

### Audio Files
The menu music consists of 10 sections with distinct musical patterns, located in `assets/audio/`:
1. `menu_section1.wav` - Ascending scale (C5 → C5)
2. `menu_section2.wav` - Arpeggio pattern (C5-based)
3. `menu_section3.wav` - Descending scale (A5 → A4)
4. `menu_section4.wav` - Melodic pattern with C5 focus
5. `menu_section5.wav` - Complex melody with varied intervals
6. `menu_section6.wav` - Descending arpeggio (C5-based)
7. `menu_section7.wav` - Wave pattern (smooth up/down movement)
8. `menu_section8.wav` - Cascading pattern (wide intervals)
9. `menu_section9.wav` - Mountain pattern (rising then falling)
10. `menu_section10.wav` - Wandering melody (varied intervals)

Each section:
- Is exactly 2 seconds long
- Contains 8 distinct musical notes
- Uses high-quality 44.1kHz, 16-bit mono audio
- Has proper ADSR envelope for smooth note transitions
- Includes 100ms crossfades at start/end

## Generation System

### Tools
The menu music is generated using `tools/generate_menu_music.py`, which:
- Creates each section with precise musical notes
- Applies ADSR envelopes for smooth transitions
- Generates crossfades between sections
- Saves files in the correct format and location

### Note System
The generator uses standard musical notes in the A4-A5 range:
```
A4: 440.00 Hz (base frequency)
B4: 493.88 Hz
C5: 523.25 Hz
D5: 587.33 Hz
E5: 659.25 Hz
F5: 698.46 Hz
G5: 783.99 Hz
A5: 880.00 Hz
```

### Current Melodies
```python
# Current sections in the generator:
'menu_section1.wav': ['C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B4', 'C5'],  # Ascending
'menu_section2.wav': ['C5', 'E5', 'G5', 'C5', 'E5', 'G5', 'B4', 'C5'],  # Arpeggios
'menu_section3.wav': ['A5', 'G5', 'F5', 'E5', 'D5', 'C5', 'B4', 'A4'],  # Descending
'menu_section4.wav': ['C5', 'B4', 'C5', 'E5', 'G5', 'E5', 'C5', 'B4'],  # Melodic
'menu_section5.wav': ['E5', 'C5', 'D5', 'B4', 'C5', 'A4', 'B4', 'C5'],  # Complex
'menu_section6.wav': ['C5', 'E5', 'G5', 'C5', 'B4', 'G5', 'E5', 'C5'],  # Descending arpeggio
'menu_section7.wav': ['E5', 'D5', 'C5', 'B4', 'C5', 'D5', 'E5', 'F5'],  # Wave pattern
'menu_section8.wav': ['G5', 'E5', 'C5', 'G5', 'F5', 'D5', 'B4', 'G5'],  # Cascading
'menu_section9.wav': ['A4', 'C5', 'E5', 'A5', 'E5', 'C5', 'B4', 'A4'],  # Mountain
'menu_section10.wav': ['D5', 'G5', 'F5', 'D5', 'E5', 'C5', 'B4', 'G5']  # Wandering
```

## Technical Specifications

### Audio Format
- Sample Rate: 44100 Hz (CD quality)
- Bit Depth: 16-bit
- Channels: Mono
- Format: WAV (uncompressed)
- Duration: 2.0 seconds per section

### ADSR Envelope Parameters
- Attack: 0.02 (2% of note duration)
- Decay: 0.1 (10% of note duration)
- Sustain: 0.8 (80% of peak amplitude)
- Release: 0.15 (15% of note duration)

### Crossfade System
- Duration: 100ms at start and end
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
   - Check crossfade duration (CROSSFADE_DURATION)
   - Verify note spacing in create_section()
   - Ensure ADSR envelope parameters are appropriate

3. **Volume Issues**
   - Adjust AMPLITUDE constant (currently 0.3)
   - Check normalization in save_wave_file()
   - Verify sustain level in ADSR envelope

### Best Practices
1. **Creating Melodies**
   - Keep note patterns musically related
   - Use a mix of ascending and descending patterns
   - Include some repeated notes for rhythm
   - End phrases on C5 or B4 for smooth transitions

2. **Testing Changes**
   - Back up working files before modifications
   - Test with a few sections first
   - Listen for smooth transitions
   - Check volume consistency

## Future Improvements
- Add more complex waveforms (square, triangle, etc.)
- Implement harmony and chord progressions
- Add volume control per section
- Support for longer sequences
- Additional musical scales and modes
- Real-time parameter adjustment
- GUI for melody creation 