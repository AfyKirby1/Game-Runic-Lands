# Particle System Documentation

## Overview

The Particle System is part of the `SynapstexGraphics` engine (located in `systems/synapstex.py`) and is responsible for creating and managing temporary visual effects like dust, leaves, sparkles, etc. It provides a simple way to add dynamic flair to both the game world and UI elements.

The system manages a list of active `Particle` objects, updating their position and lifetime each frame, and drawing them to the screen.

## Core Components

- **`ParticleSystem`**: The main class that manages all active particles. It handles emitting, updating, and drawing particles. It's accessed via `graphics.particle_system` (where `graphics` is an instance of `SynapstexGraphics`).
- **`Particle`**: Represents a single particle with properties like position, velocity, color, size, lifetime, and type.
- **`ParticleType` (Enum)**: Defines the different kinds of particles that can be created:
  - `STAR`: Twinkling stars for background effects
  - `SPARKLE`: Rising sparkles for magical effects
  - `DUST`: Basic dust particles for movement effects
  - `LEAF`: Natural leaf particles with swaying motion and autumn colors
  - `SUNBEAM`: Vertical light beams with gradient effects
  - `FIREFLY`: Glowing particles with trails and natural movement

## Main Menu Particle Effects

The main menu features a rich combination of particle effects that create a magical, autumn atmosphere:

### Stars (25 initial, continuous emission)
- Twinkling celestial bodies that drift slowly
- Blue-white color with soft alpha
- Emit every 2.5 seconds on average

### Sparkles (15 initial, every 1.5 seconds)
- Golden magical particles that rise from bottom 60% of screen
- Creates magical atmosphere
- Multiple sparkles emit at once

### Fireflies (8 initial, every 3 seconds)
- Soft yellow glowing creatures
- Move with natural, purposeful patterns
- Long lifetime for ambient presence

### Dust (12 initial, every 2 seconds)
- Light gray floating particles
- Start from bottom 80% of screen and float upward
- Adds atmospheric depth

### Autumn Leaves (15 initial, every 3 seconds)
- **NEW**: 10 different autumn colors including:
  - Forest green (34, 139, 34)
  - Dark orange (255, 140, 0)
  - Orange (255, 165, 0)
  - Red-orange (255, 69, 0)
  - Crimson red (220, 20, 60)
  - Gold/yellow (255, 215, 0)
  - Dark golden rod (184, 134, 11)
  - Saddle brown (139, 69, 19)
  - Saddle brown lighter (160, 82, 45)
  - Tomato red (255, 99, 71)
- Fall from top of screen with natural swaying motion
- Emit 2-4 leaves at a time for natural distribution

## Usage Examples

### Menu Particles (Screen Space)
```python
# Create twinkling stars in the menu background
graphics.particle_system.emit(
    x=random.uniform(0, screen_width),
    y=random.uniform(0, screen_height),
    particle_type=ParticleType.STAR,
    count=1,
    color=(220, 225, 255, 160),  # Blue-white with soft alpha
    size_range=(1.0, 3.5),
    lifetime_range=(5.0, 12.0),
    use_world_space=False  # Stays fixed to screen
)

# Create autumn leaves with varied colors
leaf_colors = [
    (34, 139, 34, 150),    # Forest green
    (255, 140, 0, 150),    # Dark orange  
    (255, 165, 0, 150),    # Orange
    (255, 69, 0, 150),     # Red-orange
    (220, 20, 60, 150),    # Crimson red
    (255, 215, 0, 150),    # Gold/yellow
    (184, 134, 11, 150),   # Dark golden rod
    (139, 69, 19, 150),    # Saddle brown
    (160, 82, 45, 150),    # Saddle brown lighter
    (255, 99, 71, 150),    # Tomato red
]

graphics.particle_system.emit(
    x=random.uniform(0, screen_width),
    y=random.uniform(-50, 0),
    particle_type=ParticleType.LEAF,
    count=1,
    color=random.choice(leaf_colors),
    size_range=(2.0, 4.5),
    lifetime_range=(10.0, 18.0),
    use_world_space=False
)

# Create sparkles around menu items
graphics.particle_system.emit(
    x=menu_item_x,
    y=menu_item_y,
    particle_type=ParticleType.SPARKLE,
    count=3,
    color=(255, 220, 150, 180),
    size_range=(1.0, 2.0),
    lifetime_range=(1.0, 3.0),
    use_world_space=False
)
```

### Game World Particles (World Space)
```python
# Create dust when player moves
graphics.particle_system.emit(
    x=player_x,
    y=player_y,
    particle_type=ParticleType.DUST,
    count=5,
    color=(180, 180, 180, 220),
    size_range=(2.0, 4.0),
    speed_range=(10.0, 20.0),
    lifetime_range=(0.3, 0.6),
    use_world_space=True  # Moves with camera
)

# Create falling leaves in forest areas
graphics.particle_system.emit(
    x=tree_x,
    y=tree_y,
    particle_type=ParticleType.LEAF,
    count=1,
    color=(55, 180, 55, 255),
    size_range=(4.0, 6.0),
    speed_range=(15.0, 25.0),
    lifetime_range=(3.0, 5.0),
    use_world_space=True
)
```

## Particle Properties

Each particle type has unique behaviors and properties:

### STAR Particles
- Twinkle with varying brightness
- Drift slowly in random directions
- Fade in and out smoothly
- Used for background ambiance

### SPARKLE Particles
- Rise upward with slight horizontal movement
- Fade in quickly, fade out gradually
- Used for magical effects and UI highlights

### DUST Particles
- Float upward with slight swaying
- Fade out near end of life
- Used for movement and impact effects

### LEAF Particles
- Fall with natural swaying motion
- Rotate as they fall
- **NEW**: Support for 10 different autumn colors
- Used for environmental effects and seasonal ambiance

### SUNBEAM Particles
- Float upward with slight horizontal drift
- Have gradient effects
- Used for light and magical effects

### FIREFLY Particles
- Move with natural, purposeful paths
- Leave glowing trails
- Pulse in brightness
- Used for magical and environmental effects

## Performance Considerations

The particle system is designed to be efficient:
- Particles are automatically removed when their lifetime expires
- Drawing is optimized with off-screen culling
- Memory usage is managed by limiting active particle counts
- Different particle types have appropriate emission frequencies

### Recommended Particle Counts
- **Main Menu**: 60+ total particles (25 stars, 15 sparkles, 8 fireflies, 12 dust, 15+ leaves)
- **Game World**: 20-50 particles depending on activity
- **Combat Effects**: Short bursts of 10-20 particles

## Music System Integration

The particle system works seamlessly with the music system:
- **Seamless Music Looping**: All 10 menu sections play continuously using pygame event handling
- **Event-Driven Transitions**: Music end events trigger automatic queue management
- **Infinite Looping**: When queue empties, system automatically restarts sequence
- **Gapless Playback**: No interruptions between sections

### Music System Architecture
1. `start_seamless_menu_music()` - Loads first section and builds complete queue
2. `pygame.USEREVENT + 1` - Event triggered when track ends
3. `handle_music_event()` - Automatically plays next queued track
4. Queue rebuilding - Restarts sequence when all tracks complete

## Future Enhancements

Potential improvements to consider:
- Seasonal leaf color variations based on in-game time
- Weather-based particle effects (rain, snow)
- Interactive particles that respond to mouse movement
- Particle lighting effects for enhanced atmosphere
- Sound-reactive particles that respond to music beats

## Performance and Control

- **`max_particles`**: The absolute maximum number of particles allowed in the system at once (currently `50`). Emission requests are ignored if this limit is reached.
- **Per-Type Limits**: There are also limits on the number of particles *of a specific type* (e.g., max `8` leaves, max `15` of other types). Emission requests are ignored if these specific limits are reached.
- **`disabled` Flag**: The `particle_system.disabled` boolean flag can be set to `True` to completely stop emitting, updating, and drawing particles. This can be useful for performance toggles (used in `main.py`, toggled by the 'P' key).
- **Updates**: Particles are updated in `ParticleSystem.update(dt)` and removed when their `lifetime` runs out.
- **Drawing**: Particles are drawn in `ParticleSystem.draw(surface)`. Only particles within the screen bounds (plus a small margin) are drawn.

## Integration with `SynapstexGraphics`

The `ParticleSystem` is instantiated as part of the `SynapstexGraphics` engine initialization.

```python
# systems/synapstex.py
class SynapstexGraphics:
    def __init__(self, ...):
        # ... other initializations ...
        self.particle_system = ParticleSystem()

    def update(self, dt):
        # ... other updates ...
        self.particle_system.update(dt) # Called automatically by graphics engine update (if implemented) or manually

    def render_all(self, screen):
        # ... render layers ...
        # Particles might be drawn here or separately
        self.particle_system.draw(screen) # Typically called after rendering layers
```

In the current `main.py`, the particle system's `update` and `draw` are called explicitly in the main game loop's `update` and `draw` methods respectively. 

## Recent Updates

The particle system has been significantly enhanced with multiple improvements focused on visual quality, performance, and stability:

### Bug Fixes

- **Fixed SUNBEAM Particles**: Added missing `beam_length` attribute initialization to properly render sun beam particles without errors.
- **Fixed FIREFLY Particles**: Added missing `drift_speed_x` and `drift_speed_y` attributes used during boundary checking to prevent AttributeError exceptions.
- **Fixed Event Handling**: Corrected spacebar debug event handling in main menu to properly access events within scope.

### Performance Improvements

- **Enhanced Enable/Disable Methods**: Improved `enable()` and `disable()` methods that properly handle particle state transitions. The `disable()` method now properly clears particles to prevent memory waste.
- **Proper Initialization**: Added proper initialization for FPS tracking variables used in performance monitoring.
- **Optimized Culling**: Improved particle culling using world bounds and screen bounds with appropriate margins to avoid unnecessary rendering.

### Visual Enhancements

- **Star Particles Overhaul**:
  - Added fade-in/fade-out effects for stars to appear and disappear gradually
  - Implemented size pulsing to create a twinkling effect
  - Added subtle drift in both X and Y directions
  - Enhanced glow rendering with better alpha falloff and color variation
  - Reduced center point size for a more ethereal look

- **Multiple Particle Types**: Added support for:
  - STAR: Distant, twinkling stars with varying colors
  - SUNBEAM: Vertical light beams with gradient effects
  - LEAF: Natural looking leaf particles with rotation and swaying
  - SPARKLE: Rising particle effects with pulsing
  - FIREFLY: Glowing particles with trails and natural movement
  - DUST: Basic dust particles for general effects

### World Space Integration

- **World Space Support**: Added `use_world_space` parameter to differentiate between UI particles (in screen space) and game world particles (in world space):
  - World-space particles move with the camera/viewport
  - Screen-space particles remain fixed relative to the screen
  
- **World Bounds Support**: Added `set_world_bounds()` method to define the world area where particles can exist, providing better control for gameplay areas.

### Debug Features

- **Runtime Debugging**: Added spacebar debug feature in the main menu that displays particle system status:
  - Shows current particle count
  - Shows whether the system is enabled or disabled
  - Shows particle settings from configuration

### Usage Examples

```python
# Create stars in screen space (for UI/menus)
graphics.particle_system.emit(
    x=random.uniform(0, screen_width),
    y=random.uniform(0, screen_height),
    particle_type=ParticleType.STAR,
    count=1,
    color=(220, 225, 255, 160),  # Blue-white with soft alpha
    size_range=(1.0, 3.5),
    lifetime_range=(5.0, 12.0),
    use_world_space=False  # Stays fixed to screen
)

# Create particles in world space (for gameplay)
graphics.particle_system.emit(
    x=world_x,
    y=world_y,
    particle_type=ParticleType.SPARKLE,
    count=5,
    color=(255, 220, 150, 180),
    size_range=(1.0, 2.0),
    lifetime_range=(1.0, 3.0),
    use_world_space=True  # Moves with camera
)
```

The particle system now offers much more sophisticated visual effects while maintaining better performance through proper optimization. 