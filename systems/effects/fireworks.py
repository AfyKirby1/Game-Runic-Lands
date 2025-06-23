import random
import math
import time
from typing import List, Dict, Tuple
import pygame

class FireworksEffect:
    def __init__(self, graphics):
        self.graphics = graphics
        self.particles: List[Dict] = []
        self.last_launch_time = 0
        self.launch_interval = 2.0  # seconds
        self.max_particles = 200
        self.max_rockets = 3
        self.max_explosions = 2
        self.active_rockets = 0
        self.active_explosions = 0

    def create_rocket_particle(self, x: float, y: float) -> Dict:
        """Create a rocket particle that will rise from the bottom of the screen."""
        return {
            'type': 'rocket',
            'position': (x, y),
            'velocity': (random.uniform(-50, 50), -random.uniform(400, 600)),
            'color': (255, 255, 255),
            'size': random.uniform(2, 4),
            'lifetime': random.uniform(1, 2),
            'exploded': False
        }

    def create_explosion_particles(self, x: float, y: float, count: int = 50) -> List[Dict]:
        """Create explosion particles that radiate outward from a point."""
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

    def create_trail_particle(self, x: float, y: float, color: Tuple[int, int, int]) -> Dict:
        """Create a trail particle that falls from an explosion."""
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

    def update(self, dt: float):
        """Update all particles in the system."""
        current_time = time.time()
        
        # Launch new rocket if conditions are met
        if (current_time - self.last_launch_time >= self.launch_interval and 
            self.active_rockets < self.max_rockets and 
            len(self.particles) < self.max_particles):
            self.launch_rocket()
            self.last_launch_time = current_time

        # Update existing particles
        for particle in self.particles[:]:
            particle['lifetime'] -= dt
            
            # Update position
            particle['position'] = (
                particle['position'][0] + particle['velocity'][0] * dt,
                particle['position'][1] + particle['velocity'][1] * dt
            )

            # Handle rocket explosion
            if (particle['type'] == 'rocket' and 
                not particle['exploded'] and 
                particle['lifetime'] <= particle['lifetime'] * 0.3):
                self.explode_rocket(particle)
                particle['exploded'] = True

            # Remove expired particles
            if particle['lifetime'] <= 0:
                if particle['type'] == 'rocket':
                    self.active_rockets -= 1
                elif particle['type'] == 'explosion':
                    self.active_explosions -= 1
                self.particles.remove(particle)

    def launch_rocket(self):
        """Launch a new rocket from the bottom of the screen."""
        x = random.uniform(100, 700)  # Random x position
        y = 600  # Bottom of screen
        rocket = self.create_rocket_particle(x, y)
        self.particles.append(rocket)
        self.active_rockets += 1

    def explode_rocket(self, rocket: Dict):
        """Create an explosion at the rocket's position."""
        if self.active_explosions >= self.max_explosions:
            return

        explosion_particles = self.create_explosion_particles(
            rocket['position'][0],
            rocket['position'][1]
        )
        
        # Add trail particles
        for _ in range(20):
            trail = self.create_trail_particle(
                rocket['position'][0],
                rocket['position'][1],
                random.choice([
                    (255, 0, 0), (0, 255, 0), (0, 0, 255),
                    (255, 255, 0), (255, 0, 255), (0, 255, 255)
                ])
            )
            explosion_particles.append(trail)

        self.particles.extend(explosion_particles)
        self.active_explosions += 1

    def draw(self, screen: pygame.Surface):
        """Draw all particles to the screen."""
        for particle in self.particles:
            # Calculate alpha based on lifetime
            lifetime_ratio = particle['lifetime'] / particle.get('initial_lifetime', 1.0)
            alpha = int(255 * lifetime_ratio)
            alpha = max(0, min(255, alpha)) # Clamp alpha value
            
            # Create surface for particle
            size = int(particle['size'])
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            # Ensure color is properly formatted
            base_color = particle['color']
            if isinstance(base_color, (tuple, list)):
                if len(base_color) == 3:  # RGB format
                    r = max(0, min(255, int(base_color[0])))
                    g = max(0, min(255, int(base_color[1])))
                    b = max(0, min(255, int(base_color[2])))
                    color = (r, g, b, alpha)
                elif len(base_color) == 4:  # RGBA format
                    r = max(0, min(255, int(base_color[0])))
                    g = max(0, min(255, int(base_color[1])))
                    b = max(0, min(255, int(base_color[2])))
                    a = max(0, min(255, int(base_color[3])))
                    color = (r, g, b, a)
                else:
                    color = (255, 255, 255, alpha)  # Fallback to white
            else:
                color = (255, 255, 255, alpha)  # Fallback to white
            
            pygame.draw.circle(surf, color, (size, size), size)
            
            # Blit to screen
            screen.blit(surf, (
                particle['position'][0] - size,
                particle['position'][1] - size
            ))

    def clear(self):
        """Clear all particles from the system."""
        self.particles.clear()
        self.active_rockets = 0
        self.active_explosions = 0 