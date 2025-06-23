# Integrating Fireworks Effect into Main Game

## Overview
This guide explains how to integrate the new fireworks effect into the main game. The integration involves adding the main menu scene and updating the game's main loop to handle the new menu state.

## Directory Structure
First, ensure the following directory structure exists:
```
project/
├── scenes/
├── systems/
│   └── effects/
└── docs/
    └── tech/
```

## Required Files
1. `scenes/main_menu.py` - Main menu scene with fireworks
2. `systems/effects/fireworks.py` - Fireworks particle effect
3. `main_menu_integration.py` - Integration code for main.py

## Integration Steps

### 1. Create Required Directories
```python
import os
from pathlib import Path

# Create required directories
directories = [
    'scenes',
    'systems/effects',
    'docs/tech'
]

for directory in directories:
    Path(directory).mkdir(parents=True, exist_ok=True)
```

### 2. Update Imports
Add these imports to the top of your `main.py`:
```python
from scenes.main_menu import MainMenu
from main_menu_integration import integrate_main_menu
```

### 3. Update Game Class Initialization
In your `Game` class `__init__` method, add:
```python
# Initialize game state
self.current_state = "main_menu"
self.main_menu = MainMenu(screen_size)
```

### 4. Replace Game Methods
Replace these methods in your `Game` class with the versions from `main_menu_integration.py`:
- `handle_input()`
- `update()`
- `draw()`
- `return_to_menu()`

### 5. Initialize Integration
After creating your game instance, call:
```python
game = Game()
integrate_main_menu(game)
```

## Testing the Integration

1. Run the game
2. You should see:
   - A dark gradient background
   - "Runic Lands" title
   - Menu options (Play Game, Options, Quit)
   - Fireworks effect in the background
   - Menu navigation with arrow keys

## Troubleshooting

### Common Issues

1. **Directory Structure**
   - Verify all required directories exist
   - Check directory permissions
   - Ensure correct file locations
   - Fix any path issues

2. **Fireworks Not Showing**
   - Check if `scenes` and `systems/effects` directories exist
   - Verify all required files are present
   - Check for import errors in the console

3. **Menu Not Responding**
   - Verify keyboard event handling
   - Check state transitions
   - Ensure menu items are properly initialized

4. **Performance Issues**
   - Reduce particle count in `FireworksEffect`
   - Adjust launch interval
   - Check frame rate

### Debug Tips

1. Add debug prints:
```python
print(f"Current state: {self.current_state}")
print(f"Particle count: {len(self.main_menu.fireworks.particles)}")
```

2. Monitor performance:
```python
fps = self.clock.get_fps()
print(f"FPS: {fps}")
```

## Best Practices

1. **Directory Management**
   - Create directories before adding files
   - Use consistent naming
   - Document structure
   - Handle errors gracefully

2. **Performance**
   - Keep particle counts reasonable
   - Use appropriate update intervals
   - Monitor frame rate

3. **Memory Management**
   - Clean up particles when changing scenes
   - Reuse particle objects
   - Monitor memory usage

4. **User Experience**
   - Ensure smooth transitions
   - Maintain consistent frame rate
   - Provide clear menu navigation

## Future Enhancements

1. **Visual Improvements**
   - Add more particle types
   - Enhance color variations
   - Add sound effects

2. **Performance Optimizations**
   - Implement particle pooling
   - Add viewport culling
   - Optimize draw calls

3. **Feature Additions**
   - Add menu animations
   - Implement save/load system
   - Add settings menu 