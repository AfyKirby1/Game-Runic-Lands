# Runic Lands Refactoring Plan

This document outlines suggested improvements to the Runic Lands codebase organization and structure.

## Current Issues

1. **UI Components Mixed with Game Systems**: Menu, inventory UI, and other UI elements are mixed with game logic in the systems directory.
2. **Large Main.py File**: The main game file is becoming too large and handles too many concerns.
3. **No Clear Asset Management System**: Assets are loaded directly where needed without a unified system.
4. **Lack of State Management Pattern**: Game state transitions are handled in multiple places.
5. **Limited Configuration Management**: Configuration is loaded but not managed systematically.

## Proposed Refactoring

### 1. Reorganize Directory Structure

```
runiclands/
├── assets/              # No change
├── docs/                # No change
├── src/                 # New main code directory
│   ├── entities/        # Moved from root
│   ├── systems/         # Core game systems only
│   ├── ui/              # New directory for all UI components
│   │   ├── menu/        # Menu screens
│   │   ├── hud/         # In-game HUD elements
│   │   └── widgets/     # Reusable UI components
│   ├── utils/           # Moved from root
│   ├── config/          # Configuration management
│   └── assets/          # Asset loading and caching
├── maps/                # No change
├── tools/               # New directory for generation scripts
│   └── generate_*.py    # Moved from root
├── main.py              # Simplified entry point
├── config.json          # No change
└── ...                  # Other root files
```

### 2. Implement a Game State Manager

Create a dedicated state management system to handle transitions between different game states:

```python
# src/systems/state_manager.py
from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    INVENTORY = auto()
    OPTIONS = auto()
    GAME_OVER = auto()

class StateManager:
    def __init__(self, game):
        self.game = game
        self.current_state = GameState.MAIN_MENU
        self.previous_state = None
        self.state_handlers = {
            GameState.MAIN_MENU: self._handle_main_menu,
            GameState.PLAYING: self._handle_playing,
            GameState.PAUSED: self._handle_paused,
            # etc.
        }
    
    def change_state(self, new_state):
        self.previous_state = self.current_state
        self.current_state = new_state

    def update(self):
        self.state_handlers[self.current_state]()
    
    # State handler methods...
```

### 3. Create an Asset Manager

Implement a unified asset loading and caching system:

```python
# src/assets/asset_manager.py
class AssetManager:
    def __init__(self):
        self.sprites = {}
        self.sounds = {}
        self.music = {}
        
    def load_sprite(self, name, path):
        if name not in self.sprites:
            self.sprites[name] = pygame.image.load(path).convert_alpha()
        return self.sprites[name]
        
    def load_sound(self, name, path):
        if name not in self.sounds:
            self.sounds[name] = pygame.mixer.Sound(path)
        return self.sounds[name]
        
    # Additional loading methods...
```

### 4. Separate UI from Game Logic

Move UI-related code to dedicated classes:

```
# src/ui/pause/pause_menu.py
# src/ui/inventory/inventory_panel.py 
# etc.
```

### 5. Implement a Config Manager

Create a centralized configuration system:

```python
# src/config/config_manager.py
import json

class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)
            
    def get(self, section, key, default=None):
        return self.config.get(section, {}).get(key, default)
        
    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        
    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
```

### 6. Simplify main.py

Reduce the main file to primarily initialization and the game loop:

```python
# main.py
from src.systems.state_manager import StateManager
from src.assets.asset_manager import AssetManager
from src.config.config_manager import ConfigManager

def main():
    # Initialize pygame
    pygame.init()
    
    # Initialize managers
    config = ConfigManager()
    assets = AssetManager()
    state = StateManager()
    
    # Set up screen
    screen_size = (config.get("display", "width", 800), 
                   config.get("display", "height", 600))
    screen = pygame.display.set_mode(screen_size)
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            state.handle_event(event)
            
        # Update
        state.update()
        
        # Draw
        screen.fill((0, 0, 0))
        state.draw(screen)
        pygame.display.flip()
        
        # Maintain framerate
        clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()
```

## Implementation Strategy

1. **Phase 1: Directory Restructuring**
   - Create the new directory structure
   - Move files to their new locations without changing functionality

2. **Phase 2: Core Systems**
   - Implement the State Manager
   - Implement the Asset Manager
   - Implement the Config Manager

3. **Phase 3: UI Separation**
   - Extract UI components to their own modules
   - Update references to maintain functionality

4. **Phase 4: Main.py Simplification**
   - Refactor the main game class to use the new systems
   - Simplify the main loop

## Benefits

- **Improved Maintainability**: Clearer separation of concerns makes the code easier to maintain
- **Better Testability**: Isolated components can be tested independently
- **Easier Collaboration**: Team members can work on different areas with minimal conflicts
- **Smoother Scaling**: Adding new features becomes easier with a well-organized structure
- **Code Reusability**: UI components and managers can be reused across the project 