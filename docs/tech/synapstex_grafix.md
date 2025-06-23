# Synapstex Grafix Engine Documentation

## Overview
Synapstex Grafix is a 2D game graphics engine built on top of Pygame, providing advanced rendering capabilities for game development. The engine supports sprite-based animation, UI rendering, particle effects, and primitive shape drawing.

## Quick Reference

### Initialization
```python
from systems.synapstex import SynapstexGraphics

# Basic initialization
graphics = SynapstexGraphics(
    screen_size=(800, 600),  # Default resolution
    target_fps=60,           # Target frame rate
    fullscreen=False,        # Windowed mode
    vsync=True              # Vertical sync
)

# Fullscreen toggle
graphics.set_fullscreen(True)

# Resolution change
graphics.set_screen_resolution(1920, 1080)

# VSync toggle
graphics.set_vsync(False)
```

### Common Operations
```python
# Create a new surface
surface = graphics.create_surface((100, 100))

# Draw text with shadow
graphics.draw_text(
    surface=screen,
    text="Hello World",
    font=font,
    color=(255, 255, 255),
    position=(100, 100),
    shadow=True
)

# Draw a progress bar
graphics.draw_progress_bar(
    surface=screen,
    rect=pygame.Rect(100, 100, 200, 20),
    progress=0.75,
    color=(0, 255, 0)
)

# Create a gradient
gradient = graphics.create_gradient(
    size=(200, 200),
    start_color=(255, 0, 0),
    end_color=(0, 0, 255),
    vertical=True
)
```

## Core Features

### 1. Render Layers
The engine uses a layered rendering system for proper draw order:
```python
class RenderLayer(Enum):
    BACKGROUND = auto()  # Background elements
    TERRAIN = auto()     # World terrain
    SHADOWS = auto()     # Shadow effects
    ENTITIES = auto()    # Game entities
    EFFECTS = auto()     # Visual effects
    UI = auto()          # User interface
    UI_OVERLAY = auto()  # UI overlays

# Usage example
graphics.add_to_layer(RenderLayer.UI, ui_element)
graphics.clear_layer(RenderLayer.EFFECTS)
```

### 2. Blend Modes
Multiple blend modes for different rendering effects:
```python
class BlendMode(Enum):
    NORMAL = 0           # Normal blitting
    ADD = pygame.BLEND_ADD
    MULTIPLY = pygame.BLEND_MULT
    SUBTRACT = pygame.BLEND_SUB
    ALPHA = pygame.BLEND_RGBA_ADD  # For alpha blending

# Usage example
graphics.draw_shape(
    surface=screen,
    shape_type="circle",
    color=(255, 255, 255, 128),
    params={"center": (100, 100), "radius": 50},
    blend_mode=BlendMode.ADD
)
```

### 3. Particle System
Advanced particle system with multiple particle types. See [Particle System Documentation](PARTICLE_SYSTEM.md) for detailed information.

Common particle types:
```python
class ParticleType(Enum):
    STAR = auto()      # Twinkling stars
    SPARKLE = auto()   # Rising sparkles
    DUST = auto()      # Movement dust
    LEAF = auto()      # Falling leaves
    SUNBEAM = auto()   # Light beams
    FIREFLY = auto()   # Glowing fireflies

# Usage example
graphics.particle_system.emit(
    x=100,
    y=100,
    particle_type=ParticleType.SPARKLE,
    count=5,
    color=(255, 255, 255, 180),
    size_range=(1.0, 3.0),
    use_world_space=True
)
```

### 4. UI System
Sophisticated menu and UI rendering with responsive design:
```python
# Menu item creation
menu_item = MenuItem(
    text="Play",
    action=GameState.PLAY,
    position=(center_x, start_y),
    size=(200, 50)
)

# Dynamic positioning
button_width = 200
button_height = 50
center_x = screen_size[0] // 2 - button_width // 2
title_y = screen_size[1] * 0.25  # 25% from top
start_y = screen_size[1] * 0.45  # 45% from top
```

### 5. Shape Drawing
Comprehensive shape drawing capabilities:
```python
# Rounded rectangle
graphics.create_rounded_rect(
    size=(200, 100),
    radius=10,
    color=(255, 255, 255),
    alpha=200
)

# Gradient creation
gradient = graphics.create_gradient(
    size=(200, 200),
    start_color=(255, 0, 0),
    end_color=(0, 0, 255),
    vertical=True
)
```

## Technical Specifications

### Display Configuration
```python
# Resolution settings
DEFAULT_RESOLUTION = (800, 600)
SUPPORTED_RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1920, 1080)
]

# Performance settings
TARGET_FPS = 60
VSYNC_ENABLED = True
FULLSCREEN = False
```

### Asset Management
```python
# Surface caching
graphics.cache_surface("button_normal", button_surface)
cached_surface = graphics.get_cached_surface("button_normal")

# Asset paths
ASSET_PATHS = {
    "sprites": "assets/sprites/",
    "ui": "assets/ui/",
    "fonts": "assets/fonts/"
}
```

## Performance Optimization

### 1. Surface Management
```python
# Cache frequently used surfaces
graphics.cache_surface("menu_bg", menu_background)

# Clear cache when needed
graphics.clear_surface_cache()

# Use appropriate surface flags
surface = graphics.create_surface(
    size=(100, 100),
    flags=pygame.SRCALPHA  # For transparency
)
```

### 2. Particle Optimization
```python
# Disable particles when not needed
graphics.particle_system.disable()

# Set particle limits
MAX_PARTICLES = 50
PARTICLE_LIMITS = {
    ParticleType.STAR: 20,
    ParticleType.SPARKLE: 15,
    ParticleType.DUST: 10
}
```

### 3. Rendering Optimization
```python
# Use appropriate blend modes
graphics.draw_shape(
    surface=screen,
    shape_type="circle",
    color=(255, 255, 255, 128),
    blend_mode=BlendMode.ADD
)

# Implement viewport culling
visible_area = pygame.Rect(
    camera_x - screen_width//2,
    camera_y - screen_height//2,
    screen_width,
    screen_height
)
```

## Debug Features

### 1. Performance Monitoring
```python
# FPS tracking
current_fps = graphics.get_fps()

# Particle system status
particle_count = graphics.particle_system.get_particle_count()
system_enabled = graphics.particle_system.is_enabled()

# Memory usage
memory_usage = graphics.get_memory_usage()
```

### 2. Debug Controls
```python
# Toggle particle system (P key)
if event.key == pygame.K_p:
    graphics.particle_system.toggle()

# Show debug info (Spacebar)
if event.key == pygame.K_SPACE:
    graphics.show_debug_info = not graphics.show_debug_info
```

## Integration Examples

### 1. Menu System Integration
```python
class MenuSystem:
    def __init__(self, screen_size, graphics):
        self.graphics = graphics
        self.screen_size = screen_size
        self.setup_menu()

    def setup_menu(self):
        # Create menu background
        self.background = self.graphics.create_gradient(
            size=self.screen_size,
            start_color=(20, 20, 40),
            end_color=(40, 40, 60)
        )

    def draw(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))
        
        # Add ambient particles
        self.graphics.particle_system.emit(
            x=random.uniform(0, self.screen_size[0]),
            y=random.uniform(0, self.screen_size[1]),
            particle_type=ParticleType.STAR,
            count=1,
            use_world_space=False
        )
```

### 2. Game World Integration
```python
class GameWorld:
    def __init__(self, graphics):
        self.graphics = graphics
        self.setup_world()

    def update(self, dt):
        # Update world state
        self.update_entities(dt)
        
        # Add environmental effects
        if random.random() < 0.1:  # 10% chance per frame
            self.graphics.particle_system.emit(
                x=random.uniform(0, world_width),
                y=random.uniform(0, world_height),
                particle_type=ParticleType.LEAF,
                count=1,
                use_world_space=True
            )

    def draw(self, screen):
        # Draw world layers
        self.graphics.render_all(screen)
```

## Best Practices

### 1. Performance Optimization
- Cache frequently used surfaces
- Use appropriate blend modes
- Implement viewport culling
- Monitor particle counts
- Use screen space for UI particles
- Use world space for game effects

### 2. UI Design
- Use proportional positioning
- Implement proper layering
- Consider screen size variations
- Use appropriate font sizes
- Test at different resolutions

### 3. Particle Effects
- Keep particle counts reasonable
- Use appropriate lifetimes
- Clean up particles when changing scenes
- Consider performance impact
- Use appropriate particle types

### 4. General Tips
- Test at different screen sizes
- Consider colorblind accessibility
- Use appropriate alpha values
- Implement proper error handling
- Document custom effects

## Troubleshooting

### Common Issues

1. **Performance Problems**
   - Check particle counts
   - Monitor FPS
   - Review blend mode usage
   - Check surface caching

2. **Visual Artifacts**
   - Verify layer order
   - Check alpha values
   - Review blend modes
   - Check surface flags

3. **Memory Issues**
   - Monitor surface cache
   - Check particle cleanup
   - Review asset loading
   - Implement proper cleanup

### Debug Tools
```python
# Enable debug mode
graphics.debug_mode = True

# Show performance stats
graphics.show_performance_stats = True

# Monitor specific systems
graphics.monitor_particle_system = True
graphics.monitor_surface_cache = True
```

## Future Enhancements
- Enhanced shader support
- Advanced lighting effects
- Improved particle system
- Better performance monitoring
- Enhanced debug tools 