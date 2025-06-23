# Pause Menu System

## Overview
The pause menu system provides a way to halt gameplay and present the player with several options, including saving the game, loading a game, accessing options, and quitting. The menu appears when the player presses the ESC key during gameplay and disappears when ESC is pressed again or when the Resume option is selected.

## Implementation

The pause menu is implemented as a standalone class in `systems/pause_menu.py` and is integrated into the main game loop in `main.py`.

### Structure

```
PauseMenu
├── Initialization
│   ├── Screen dimensions
│   ├── Menu options
│   └── Visual styling
├── Core Functions
│   ├── toggle() - Show/hide menu
│   ├── handle_input() - Process key presses
│   └── draw() - Render menu to screen
└── Menu Actions
    ├── Resume - Close menu and continue game
    ├── Save Game - Save current game state
    ├── Load Game - Load a previously saved game
    ├── Options - Open options menu
    └── Quit - Return to main menu
```

## Usage

The pause menu is initialized in the game's constructor:

```python
# Inside Game.__init__()
self.pause_menu = PauseMenu(*self.screen_size)
```

### Input Handling

The menu handles three kinds of input:
- **ESC key**: Toggles the menu on/off
- **Arrow keys**: Navigate menu options
- **Enter key**: Select current menu option

### Game Pausing

When the menu is visible, the game's update cycle is paused:

```python
# Inside Game.update()
if self.pause_menu.is_visible:
    return  # Skip updates while paused
```

## Technical Details

### Menu State

The menu's visibility is controlled by the `is_visible` boolean property. When this is `True`, the menu is drawn and processes input. When `False`, the menu is hidden and input passes through to the game.

### Menu Navigation

Menu navigation is handled by tracking the `selected_option` index, which is modified when up/down keys are pressed:

```python
# Inside PauseMenu.handle_input()
elif event.key == pygame.K_UP:
    self.selected_option = (self.selected_option - 1) % len(self.options)
elif event.key == pygame.K_DOWN:
    self.selected_option = (self.selected_option + 1) % len(self.options)
```

### Visual Styling

The menu uses:
- Semi-transparent black background (RGBA: 0,0,0,128)
- White text for normal options
- Gold text (RGB: 255,215,0) for the selected option
- Centered positioning of text

## Future Enhancements

1. **Save/Load Implementation**: Connect save/load options to actual functionality ✅ Implemented
2. **Visual Polish**: Add animations, better styling, and sound effects ✅ Partially Implemented
3. **Controller Support**: Extend input handling for gamepad controls
4. **Custom Themes**: Allow changing the visual appearance through theme settings

## Save/Load Integration

The pause menu is fully integrated with the game's save/load system. When the player selects:

- **Save Game**: The `save_current_game()` method is called, which serializes the current game state and stores it using the `SaveManager` class.
- **Load Game**: The `load_game()` method is called, which retrieves a saved game state and restores it.

For full details on the save/load system, see [save_system.md](save_system.md).

```python
# When "Save Game" is selected
elif action == "save_game":
    self.save_current_game()

# When "Load Game" is selected
elif action == "load_game":
    self.load_game()
```

## Audio Feedback

The pause menu now provides audio feedback for all user interactions:

- **Menu Toggle**: Plays the `menu_click` sound when opening or closing the pause menu with ESC
- **Navigation**: Audio feedback when moving between menu options (not yet implemented)
- **Selection**: Plays the `menu_click` sound when selecting an option

This enhances user experience by providing multi-sensory feedback. The menu uses the enhanced click sound which has a more satisfying feel with multiple frequency components and proper attack/decay.

```python
# In main.py when toggling the pause menu
self.pause_menu.is_visible = not old_state
self.options.play_sound('menu_click')

# When handling menu actions
if action == "resume":
    self.pause_menu.is_visible = False
    self.options.play_sound('menu_click')
```

## Bug Fix: ESC Key Freezing/Crashing

The pause menu system was updated to resolve critical freezing and crashing issues when toggling with the ESC key.

### Problem
Several issues were found that caused the game to freeze or crash when pressing ESC:
1. Circular event handling between main game loop and pause menu
2. Events being processed multiple times
3. State inconsistencies between game modes and UI visibility
4. Resource contention during state transitions

### Solution
The fix included several key changes:

1. **Event Processing Model**: 
   - Events are now processed in two distinct passes
   - First pass handles critical system events (ESC, quit)
   - Second pass handles gameplay events
   - Events are marked as "processed" to prevent duplicated handling

2. **ESC Key Handling**: 
   - ESC key is now handled exclusively by the main game loop, not the pause menu
   - Clear priority order: Options → Inventory → Main Menu → Gameplay

3. **State Management**:
   - Proper sequencing for state transitions between pause/game/menu states
   - Added explicit game state resets when returning to the menu
   - Added logging for all state transitions

4. **Update Loop**:
   - Particle systems continue to update even when game is paused
   - Time tracking continues during pauses to prevent timing issues
   - Updates return early after handling pause toggling

5. **Recovery and Error Handling**:
   - Added try/catch blocks around critical sections
   - Game attempts to recover from non-fatal errors
   - Added proper cleanup in program exit path

### Code Details
Here are the crucial parts of the implementation:

```python
# Event processing model in handle_input():
events = pygame.event.get()
processed_events = []
    
# First pass: handle critical events
for event in events:
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        # ESC handling logic here...
        processed_events.append(event)
        continue

# Remove processed events
remaining_events = [e for e in events if e not in processed_events]

# Second pass: handle game state-specific input
# ...
```

```python
# Crucial change in pause_menu.py:
def handle_input(self, event):
    # Do NOT handle ESC here - let main game loop handle it
    # to prevent conflicts and event loops
    # ...
```

This approach resolves the issue by ensuring clean event handling and state transitions.

## Error Logging and Crash Recovery

To improve stability and aid troubleshooting, a comprehensive error logging and crash recovery system was implemented.

### Logging System

The logging system captures detailed information about game events and errors:

```python
def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create a log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"game_log_{timestamp}.txt"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)
```

### Crash Handling

A global exception handler catches and logs all unhandled exceptions before the game exits:

```python
def handle_exception(exc_type, exc_value, exc_traceback):
    logger = logging.getLogger(__name__)
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Save the full traceback to a separate file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    crash_file = Path("logs") / f"crash_{timestamp}.txt"
    with open(crash_file, 'w') as f:
        f.write(f"Crash occurred at {datetime.now()}\n")
        f.write("Full traceback:\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
    
    pygame.quit()
    sys.exit(1)

# Install the handler
sys.excepthook = handle_exception
```

### Resilient Game Loop

The main game loop includes error recovery to continue running even after non-fatal errors:

```python
def run(self):
    try:
        while True:
            # Ensure the game loop continues even if there are non-fatal errors
            try:
                self.update()
                self.draw()
            except Exception as e:
                self.logger.error(f"Error in game loop iteration: {e}", exc_info=True)
                # Try to recover - reset critical states
                self.pause_menu.is_visible = False
                
            # Cap the framerate
            self.clock.tick(60)
    except Exception as e:
        self.logger.error(f"Fatal error in main game loop: {e}", exc_info=True)
    finally:
        # Ensure pygame shuts down properly
        self.logger.info("Game shutting down...")
        try:
            pygame.quit()
        except Exception as ex:
            self.logger.error(f"Error during pygame shutdown: {ex}")
        sys.exit(1)
```

### Benefits

This system provides several advantages:
1. Detailed logs for debugging pause menu and ESC key issues
2. Ability to recover from minor errors without crashing
3. Proper resource cleanup even when errors occur
4. Timestamped crash reports for developer analysis
