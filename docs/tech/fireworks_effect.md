# Fireworks Particle Effect Documentation

## Overview
The fireworks effect is a dynamic particle system that creates realistic-looking fireworks in the main menu. The effect consists of three main components:
1. Launch phase - Firework rocket rising from the bottom of the screen
2. Explosion phase - Burst of particles at the target location
3. Trail phase - Falling embers and sparks

## Particle Types

### 1. Rocket Particle
- Properties:
  - Color: White to yellow gradient
  - Size: 2-4 pixels
  - Speed: 400-600 pixels per second
  - Lifetime: 1-2 seconds
  - Behavior: Rises in a slight arc

### 2. Explosion Particles
- Properties:
  - Color: Random from predefined palette
  - Size: 3-6 pixels
  - Speed: 200-400 pixels per second
  - Lifetime: 1-1.5 seconds
  - Behavior: Radiates outward in all directions

### 3. Trail Particles
- Properties:
  - Color: Fading from explosion color to black
  - Size: 1-3 pixels
  - Speed: 100-200 pixels per second
  - Lifetime: 0.5-1 second
  - Behavior: Falls with slight random movement

## Implementation Details

### Launch Phase
```python
def create_rocket_particle(x, y):
    return {
        'type': 'rocket',
        'position': (x, y),
        'velocity': (0, -500),
        'color': (255, 255, 255),
        'size': 3,
        'lifetime': 1.5
    }
```

### Explosion Phase
```python
def create_explosion_particles(x, y, count=50):
    particles = []
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255)   # Cyan
    ]
    
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(200, 400)
        particles.append({
            'type': 'explosion',
            'position': (x, y),
            'velocity': (
                speed * math.cos(angle),
                speed * math.sin(angle)
            ),
            'color': random.choice(colors),
            'size': random.uniform(3, 6),
            'lifetime': random.uniform(1, 1.5)
        })
    return particles
```

### Trail Phase
```python
def create_trail_particle(x, y, color):
    return {
        'type': 'trail',
        'position': (x, y),
        'velocity': (
            random.uniform(-50, 50),
            random.uniform(100, 200)
        ),
        'color': color,
        'size': random.uniform(1, 3),
        'lifetime': random.uniform(0.5, 1)
    }
```

## Performance Considerations

1. **Particle Limits**
   - Maximum active particles: 200
   - Maximum rockets: 3
   - Maximum explosions: 2

2. **Optimization Techniques**
   - Use particle pooling
   - Implement viewport culling
   - Use appropriate blend modes
   - Cache frequently used surfaces

3. **Memory Management**
   - Clear particles when changing scenes
   - Reuse particle objects
   - Monitor particle counts

## Integration Example

```python
class FireworksEffect:
    def __init__(self, graphics):
        self.graphics = graphics
        self.particles = []
        self.last_launch_time = 0
        self.launch_interval = 2.0  # seconds

    def update(self, dt):
        current_time = time.time()
        
        # Launch new rocket
        if current_time - self.last_launch_time >= self.launch_interval:
            self.launch_rocket()
            self.last_launch_time = current_time

        # Update existing particles
        for particle in self.particles[:]:
            particle['lifetime'] -= dt
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
            else:
                # Update position
                particle['position'] = (
                    particle['position'][0] + particle['velocity'][0] * dt,
                    particle['position'][1] + particle['velocity'][1] * dt
                )

    def launch_rocket(self):
        # Create rocket at bottom of screen
        x = random.uniform(100, 700)  # Random x position
        y = 600  # Bottom of screen
        rocket = create_rocket_particle(x, y)
        self.particles.append(rocket)

    def explode_rocket(self, rocket):
        # Create explosion at rocket position
        explosion_particles = create_explosion_particles(
            rocket['position'][0],
            rocket['position'][1]
        )
        self.particles.extend(explosion_particles)

    def draw(self, screen):
        for particle in self.particles:
            self.graphics.draw_particle(screen, particle)
```

## Best Practices

1. **Timing**
   - Space out rocket launches
   - Vary explosion patterns
   - Coordinate with menu music

2. **Visual Quality**
   - Use appropriate blend modes
   - Implement smooth color transitions
   - Add subtle random variations

3. **Performance**
   - Monitor particle counts
   - Implement efficient updates
   - Use appropriate culling

## Troubleshooting

1. **Performance Issues**
   - Check particle counts
   - Review update logic
   - Monitor memory usage

2. **Visual Problems**
   - Verify blend modes
   - Check color values
   - Review particle lifetimes

3. **Integration Issues**
   - Check coordinate systems
   - Verify timing
   - Review particle creation 