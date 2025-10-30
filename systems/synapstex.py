"""
Synapstex Grafix Engine Module

A 2D graphics engine built on top of Pygame, providing advanced rendering capabilities
for game development.
"""

import pygame
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum, auto
import math
import random
import os

class RenderLayer(Enum):
    """
    Defines the rendering layers to ensure a proper draw order for game objects.

    Objects in lower-valued layers are drawn first, appearing behind objects
    in higher-valued layers.
    """
    BACKGROUND = auto()
    TERRAIN = auto()
    SHADOWS = auto()
    ENTITIES = auto()
    EFFECTS = auto()
    UI = auto()
    UI_OVERLAY = auto()

class BlendMode(Enum):
    """
    Specifies the blend mode to be used when rendering surfaces.

    These modes correspond to Pygame's blend constants and are used for
    effects like additive lighting or color multiplication.
    """
    NORMAL = 0  # Normal blitting
    ADD = pygame.BLEND_ADD
    MULTIPLY = pygame.BLEND_MULT
    SUBTRACT = pygame.BLEND_SUB
    ALPHA = pygame.BLEND_RGBA_ADD  # For alpha blending

class ParticleType(Enum):
    """
    Enumeration of different particle types, each with unique behaviors.

    Used by the ParticleSystem to determine how a particle should be updated
    and rendered.
    """
    SPARKLE = auto()
    DUST = auto()
    LEAF = auto()
    STAR = auto()
    SUNBEAM = auto()
    FIREFLY = auto()

class Particle:
    """
    Represents a single particle in the ParticleSystem.

    This class manages the state and behavior of a particle, including its
    position, color, size, lifetime, and movement logic, which varies based
    on its ParticleType.
    """
    def __init__(self, x: float, y: float, particle_type: ParticleType,
                 color: Tuple[int, int, int, int],
                 size: float = 1.5,
                 lifetime: float = 3.0,
                 screen_width: int = 800,
                 screen_height: int = 600,
                 use_world_space: bool = False):
        """
        Initializes a Particle.

        Args:
            x (float): The initial x-coordinate.
            y (float): The initial y-coordinate.
            particle_type (ParticleType): The type of the particle.
            color (Tuple[int, int, int, int]): The RGBA color of the particle.
            size (float, optional): The size of the particle. Defaults to 1.5.
            lifetime (float, optional): The duration the particle will exist, in seconds.
                                       Defaults to 3.0.
            screen_width (int, optional): The width of the screen, for boundary checks.
                                          Defaults to 800.
            screen_height (int, optional): The height of the screen, for boundary checks.
                                           Defaults to 600.
            use_world_space (bool, optional): Whether the particle's coordinates are
                                              in world space or screen space.
                                              Defaults to False.
        """
        self.x = x
        self.y = y
        self.type = particle_type
        self.color = list(color) if isinstance(color, tuple) else color  # Make sure color is mutable
        self.original_alpha = color[3]
        self.size = size
        self.lifetime = lifetime
        self.initial_lifetime = lifetime  # Store original lifetime
        self.original_lifetime = lifetime  # Additional name for compatibility
        self.age = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.use_world_space = use_world_space
        
        # Initialize velocities
        self.vx = 0
        self.vy = 0
        
        # Initialize state variables
        self.angle = 0
        self.pulse_time = 0
        
        # Type-specific initialization
        if self.type == ParticleType.LEAF:
            # Leaves sway as they fall
            self.vx = random.uniform(-10, 10)
            self.vy = random.uniform(20, 40)
            self.sway_offset = random.uniform(0, math.pi * 2)
            self.sway_speed = random.uniform(1.0, 2.0)
            self.fall_speed = random.uniform(15, 25)
            self.rotation = random.uniform(0, 360)
            self.rot_speed = random.uniform(-50, 50)
            self.sway_amount = random.uniform(10, 20)
            
        elif self.type == ParticleType.SPARKLE:
            # Sparkles rise slowly
            self.vx = random.uniform(-10, 10)
            self.vy = random.uniform(-30, -15)
            self.pulse_speed = random.uniform(2, 4)
            self.fade_in_time = random.uniform(0.5, 1.2)
            self.fade_in_progress = 0
            
        elif self.type == ParticleType.STAR:
            # Stars twinkle in place
            self.pulse_speed = random.uniform(1.0, 3.0)
            self.twinkle_offset = random.uniform(0, math.pi * 2)
            
            # Enhanced star parameters
            self.drift_speed_x = random.uniform(-2.0, 2.0)
            self.drift_speed_y = random.uniform(-2.0, 2.0)
            self.original_size = size
            self.pulse_factor = random.uniform(0.8, 1.2)
            self.pulse_period = random.uniform(1.0, 3.0)
            
            # Fade parameters
            self.fade_in_time = min(lifetime * 0.2, 1.0)  # 20% of lifetime or 1 second
            self.fade_in_complete = False
            
        elif self.type == ParticleType.SUNBEAM:
            # Sunbeams move upward
            self.vx = random.uniform(-5, 5)
            self.vy = random.uniform(-20, -10)
            self.rise_speed = random.uniform(10, 20)
            # Add beam_length attribute 
            self.beam_length = random.randint(50, 150)  # Initial beam length
            
        elif self.type == ParticleType.FIREFLY:
            # Fireflies move with more purposeful path changes
            self.vx = random.uniform(-15, 15)
            self.vy = random.uniform(-15, 15)
            
            # Use an intended direction for more purposeful movement
            self.direction_angle = random.uniform(0, math.pi * 2)
            self.target_x = x + math.cos(self.direction_angle) * random.uniform(80, 150)
            self.target_y = y + math.sin(self.direction_angle) * random.uniform(80, 150)
            
            # Movement parameters
            self.turn_speed = random.uniform(0.5, 1.5)  # Reduced for more directional movement
            self.move_speed = random.uniform(20, 35)    # Increased for more noticeable movement
            self.glow_time = 0
            self.glow_speed = random.uniform(0.5, 1.5)
            self.move_timer = 0
            self.move_interval = random.uniform(2.0, 4.0)  # Longer intervals for more consistent direction
            self.move_dir_x = math.cos(self.direction_angle)
            self.move_dir_y = math.sin(self.direction_angle)
            self.twinkle_offset = random.uniform(0, math.pi * 2)
            
            # Pulse brightness for glow effect
            self.pulse_phase = random.uniform(0, math.pi * 2)
            self.pulse_speed = random.uniform(2.0, 4.0)
            
            # Add drift speed attributes used in boundary checking
            self.drift_speed_x = self.vx
            self.drift_speed_y = self.vy
            
            # Trail parameters
            self.trail_positions = []
            self.max_trail_length = random.randint(3, 6)
            self.trail_update_interval = 0.05  # Time between trail position updates
            self.trail_timer = 0
            
        else:
            # Default dust behavior
            self.vx = random.uniform(-10, 10)
            self.vy = random.uniform(-5, 5)

    def update(self, dt: float):
        """
        Updates the particle's state based on its type and elapsed time.

        Args:
            dt (float): The time delta since the last update, in seconds.

        Returns:
            bool: True if the particle's lifetime has expired, False otherwise.
        """
        self.age += dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            return True  # Particle is dead
            
        if self.type == ParticleType.DUST:
            # Dust floats upward slowly
            self.y -= 15 * dt
            self.x += math.sin(self.pulse_time) * 5 * dt
            self.pulse_time += dt
            
            # Fade out near end of life
            if self.lifetime < 1.0:
                self.color = (self.color[0], self.color[1], self.color[2], 
                            int(self.color[3] * (self.lifetime / 1.0)))
                
        elif self.type == ParticleType.LEAF:
            # Leaves fall with swaying
            self.y += self.fall_speed * dt
            self.x += math.sin(self.pulse_time * self.sway_speed) * self.sway_amount * dt
            self.pulse_time += dt
            
            # Rotate the leaf
            self.angle += self.rot_speed * dt
            
        elif self.type == ParticleType.STAR:
            # Keep the star animations and drifting
            # Update position with drift
            self.x += self.drift_speed_x * dt * 0.5
            self.y += self.drift_speed_y * dt * 0.5
            
            # Update twinkling
            self.pulse_time += dt
            twinkle_factor = (math.sin(self.pulse_time + self.twinkle_offset) + 1) / 2
            
            # Handle fade-in effect
            fade_in_factor = 1.0
            if not self.fade_in_complete:
                if self.age < self.fade_in_time:
                    fade_in_factor = self.age / self.fade_in_time
                else:
                    self.fade_in_complete = True
            
            # Handle fade-out effect
            fade_out_factor = 1.0
            if self.lifetime < (self.initial_lifetime * 0.3):
                fade_out_factor = self.lifetime / (self.initial_lifetime * 0.3)
            
            # Apply all effects to alpha
            alpha = int(self.original_alpha * fade_in_factor * fade_out_factor * (0.6 + 0.4 * twinkle_factor))
            self.color = (self.color[0], self.color[1], self.color[2], max(0, min(255, alpha)))
        
        elif self.type == ParticleType.SPARKLE:
            # Sparkles rise slowly and fade
            self.y -= 40 * dt
            
            # Fade in at start
            self.fade_in_progress += dt
            if self.fade_in_progress < self.fade_in_time:
                alpha_factor = self.fade_in_progress / self.fade_in_time
            else:
                # Fade out near end
                alpha_factor = self.lifetime / self.initial_lifetime
                
            self.color = (self.color[0], self.color[1], self.color[2], 
                        int(self.original_alpha * alpha_factor))
            
        elif self.type == ParticleType.SUNBEAM:
            # Sunbeams float upward
            self.y += self.vy * 30 * dt
            self.x += self.vx * 10 * dt
            
            # Fade out gradually
            alpha_factor = self.lifetime / self.initial_lifetime
            self.color = (self.color[0], self.color[1], self.color[2], 
                        int(self.original_alpha * alpha_factor))
            
        elif self.type == ParticleType.FIREFLY:
            # Firefly movement with improved directional behavior
            # Update trail positions periodically
            self.trail_timer += dt
            if self.trail_timer >= self.trail_update_interval:
                self.trail_timer = 0
                self.trail_positions.insert(0, (self.x, self.y))  # Add current position to start of trail
                while len(self.trail_positions) > self.max_trail_length:
                    self.trail_positions.pop()  # Remove oldest positions
            
            # Change direction occasionally
            self.move_timer += dt
            if self.move_timer >= self.move_interval:
                self.move_timer = 0
                self.move_interval = random.uniform(2.0, 4.0)
                # Set a new target in the general direction we're already moving
                # This creates smoother directional changes
                angle_change = random.uniform(-math.pi/4, math.pi/4)  # Max 45 degree change
                self.direction_angle = (self.direction_angle + angle_change) % (math.pi * 2)
                distance = random.uniform(80, 150)
                self.target_x = self.x + math.cos(self.direction_angle) * distance
                self.target_y = self.y + math.sin(self.direction_angle) * distance
                
                # Update movement direction vector
                self.move_dir_x = math.cos(self.direction_angle)
                self.move_dir_y = math.sin(self.direction_angle)
            
            # Move toward target direction
            self.x += self.move_dir_x * dt * self.move_speed
            self.y += self.move_dir_y * dt * self.move_speed
            
            # Keep fireflies within a reasonable screen area with more realistic bouncing
            if self.x < 0 or self.x > self.screen_width:
                # Reflect direction when hitting screen edge
                self.direction_angle = math.pi - self.direction_angle
                self.move_dir_x = math.cos(self.direction_angle)
                self.move_dir_y = math.sin(self.direction_angle)
                # Keep within bounds
                self.x = max(0, min(self.screen_width, self.x))
                
            if self.y < 0 or self.y > self.screen_height:
                # Reflect direction when hitting screen edge
                self.direction_angle = -self.direction_angle
                self.move_dir_x = math.cos(self.direction_angle)
                self.move_dir_y = math.sin(self.direction_angle)
                # Keep within bounds
                self.y = max(0, min(self.screen_height, self.y))
            
            # Update pulsing glow effect
            self.pulse_time += dt
            glow_factor = (math.sin(self.pulse_time * self.pulse_speed + self.pulse_phase) + 1) / 2
            self.color = (self.color[0], self.color[1], self.color[2], 
                        int(self.original_alpha * (0.7 + 0.3 * glow_factor)))
        
        # Handle bounds check for world-space particles
        if self.use_world_space and hasattr(self, 'world_bounds'):
            # Add margin to world bounds
            margin = 100
            if (self.x < self.world_bounds[0] - margin or 
                self.x > self.world_bounds[2] + margin or
                self.y < self.world_bounds[1] - margin or 
                self.y > self.world_bounds[3] + margin):
                return True  # Remove if outside world bounds
                
        return False  # Particle is still alive

    def draw(self, screen: pygame.Surface, offset: Tuple[float, float] = (0, 0)):
        """
        Draws the particle on the screen.

        This method handles the visual representation of the particle, which
        varies depending on its type. It also accounts for the camera offset
        if the particle exists in world space.

        Args:
            screen (pygame.Surface): The screen surface to draw on.
            offset (Tuple[float, float], optional): The camera's world offset.
                                                     Defaults to (0, 0).
        """
        if self.use_world_space:
            # Calculate screen position from world position
            screen_x = self.x - offset[0]
            screen_y = self.y - offset[1]
        else:
            # Already in screen space
            screen_x = self.x
            screen_y = self.y
            
        # Skip drawing if off-screen with a margin
        screen_rect = pygame.Rect(-100, -100, self.screen_width + 200, self.screen_height + 200)
        if not screen_rect.collidepoint((screen_x, screen_y)):
            return
        
        if self.type == ParticleType.LEAF:
            # Draw leaf as a rotated rectangle
            leaf_rect = pygame.Rect(0, 0, self.size, self.size * 2)
            leaf_rect.center = (int(screen_x), int(screen_y))
            
            leaf_surf = pygame.Surface((leaf_rect.width, leaf_rect.height), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf_surf, self.color, (0, 0, leaf_rect.width, leaf_rect.height))
            
            rotated_leaf = pygame.transform.rotate(leaf_surf, self.rotation)
            rotated_rect = rotated_leaf.get_rect(center=leaf_rect.center)
            
            screen.blit(rotated_leaf, rotated_rect)
        
        elif self.type == ParticleType.SPARKLE:
            # Draw sparkle (small bright dot)
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), int(self.size))
        
        elif self.type == ParticleType.STAR:
            # Simpler star drawing with more direct rendering
            # Create a simpler star with just a bright center and glow
            size = int(self.size * 2) # Base size
            glow_size = int(self.size * 4) # Outer glow size
            
            # Create surface for the star
            star_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            center = (glow_size, glow_size)
            
            # Get color components
            r, g, b = self.color[0], self.color[1], self.color[2]
            alpha = self.color[3]
            
            # Draw outer glow first
            for radius in range(glow_size, 0, -1):
                # Calculate decreasing alpha for glow effect
                glow_alpha = int(alpha * (radius / glow_size) ** 2)
                if glow_alpha <= 0:
                    continue
                
                color = (r, g, b, glow_alpha)
                pygame.draw.circle(star_surf, color, center, radius)
            
            # Draw center point
            pygame.draw.circle(star_surf, (r, g, b, alpha), center, size // 4)
            
            # Blit to screen
            screen.blit(star_surf, 
                       (int(screen_x - glow_size), 
                        int(screen_y - glow_size)))
        
        elif self.type == ParticleType.SUNBEAM:
            # Draw sunbeam (vertical line with glow)
            beam_height = self.size * 10
            beam_width = self.size
            
            beam_surf = pygame.Surface((int(beam_width * 3), int(beam_height)), pygame.SRCALPHA)
            
            # Draw the beam with a gradient
            for i in range(int(beam_height)):
                # Fade from bottom to top
                alpha_factor = 1.0 - (i / beam_height)
                beam_alpha = int(self.color[3] * alpha_factor)
                
                # Calculate beam width at this point (thinner at top)
                current_width = beam_width * (0.5 + 0.5 * (1.0 - i / beam_height))
                
                pygame.draw.line(
                    beam_surf,
                    (self.color[0], self.color[1], self.color[2], beam_alpha),
                    (int(beam_width * 1.5), i),
                    (int(beam_width * 1.5), i),
                    int(current_width)
                )
            
            beam_rect = beam_surf.get_rect(center=(int(screen_x), int(screen_y)))
            screen.blit(beam_surf, beam_rect)
        
        elif self.type == ParticleType.FIREFLY:
            # Enhanced firefly with directional trail
            glow_size = self.size * 4.0  # Larger glow
            
            # Draw trail first (behind the glow)
            if hasattr(self, 'trail_positions') and len(self.trail_positions) > 1:
                # Calculate movement direction for elongated trail effect
                direction_x = self.move_dir_x if hasattr(self, 'move_dir_x') else 0
                direction_y = self.move_dir_y if hasattr(self, 'move_dir_y') else 0
                
                # Draw trail particles with diminishing size and opacity
                for i, (trail_x, trail_y) in enumerate(self.trail_positions):
                    # Skip first position (current position)
                    if i == 0:
                        continue
                        
                    # Calculate screen position
                    if hasattr(self, 'use_world_space') and self.use_world_space:
                        trail_screen_x = trail_x - offset[0]
                        trail_screen_y = trail_y - offset[1]
                    else:
                        trail_screen_x = trail_x
                        trail_screen_y = trail_y
                    
                    # Decrease size and alpha based on position in trail
                    trail_factor = 1.0 - (i / len(self.trail_positions))
                    trail_size = int(self.size * trail_factor * 0.8)  # Smaller trail particles
                    trail_alpha = int(self.color[3] * trail_factor * 0.6)  # More transparent trail
                    
                    if trail_size <= 0:
                        continue
                        
                    trail_color = (*self.color[:3], trail_alpha)
                    trail_surf = pygame.Surface((trail_size*2, trail_size*2), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surf, trail_color, 
                                    (trail_size, trail_size), 
                                    trail_size)
                    
                    screen.blit(trail_surf, 
                               (int(trail_screen_x - trail_size), 
                                int(trail_screen_y - trail_size)),
                               special_flags=pygame.BLEND_RGBA_ADD)
            
            # Create a better glow effect for the firefly
            glow_surf = pygame.Surface((int(glow_size*2), int(glow_size*2)), pygame.SRCALPHA)
            center = (int(glow_size), int(glow_size))
            
            # Get color components with enhanced brightness
            r, g, b = min(255, self.color[0]*1.2), min(255, self.color[1]*1.2), min(255, self.color[2]*1.2)
            
            # Create a more pronounced core with multiple layers of glow
            for i in range(5):  # More layers for smoother falloff
                radius = int(glow_size * (1.0 - (i / 5.0)))
                # Higher alpha for central glow
                alpha = int(min(255, self.color[3] * (1.0 - (i / 7.0))))
                color = (r, g, b, alpha)
                pygame.draw.circle(glow_surf, color, center, radius)
            
            # Add directional elongation to the glow if moving
            if hasattr(self, 'move_dir_x') and hasattr(self, 'move_dir_y'):
                speed = math.sqrt(self.move_dir_x**2 + self.move_dir_y**2)
                if speed > 0.1:  # Only if moving significantly
                    elongation_length = int(glow_size * 0.8)
                    elongation_width = int(glow_size * 0.5)
                    
                    # Calculate the angle of movement
                    angle = math.atan2(self.move_dir_y, self.move_dir_x)
                    
                    # Create points for an elongated shape in the direction of movement
                    # This adds a subtle directional indicator to the glow
                    elongation_points = [
                        (center[0] + math.cos(angle) * elongation_length, 
                         center[1] + math.sin(angle) * elongation_length),
                        (center[0] + math.cos(angle + math.pi/2) * elongation_width,
                         center[1] + math.sin(angle + math.pi/2) * elongation_width),
                        (center[0] - math.cos(angle) * elongation_length/3,
                         center[1] - math.sin(angle) * elongation_length/3),
                        (center[0] + math.cos(angle - math.pi/2) * elongation_width,
                         center[1] + math.sin(angle - math.pi/2) * elongation_width)
                    ]
                    
                    # Draw a semi-transparent elongation
                    pygame.draw.polygon(glow_surf, (r, g, b, self.color[3]//3), elongation_points)
            
            # Draw a bright core in the center
            core_size = max(2, int(self.size * 0.5))
            pygame.draw.circle(glow_surf, (min(255, r+40), min(255, g+40), min(255, b+40), 
                                        min(255, self.color[3])), 
                            center, core_size)
            
            # Blit the complete firefly
            screen.blit(glow_surf, 
                       (int(screen_x - glow_size), 
                        int(screen_y - glow_size)),
                       special_flags=pygame.BLEND_RGBA_ADD)
        
        else:  # Default dust particle
            particle_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, self.color,
                            (self.size//2, self.size//2), self.size//2)
            screen.blit(particle_surf, 
                       (int(screen_x - self.size//2), 
                        int(screen_y - self.size//2)),
                       special_flags=pygame.BLEND_RGBA_ADD)

    def set_random_movement(self):
        angle = random.uniform(0, math.pi * 2)
        self.move_dir_x = math.cos(angle)
        self.move_dir_y = math.sin(angle)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.cached_surfaces = {}
        self.max_particles = 500  # Increased to allow more particles
        self.disabled = False
        self.screen_width = 800  # Default screen width
        self.screen_height = 600  # Default screen height
        self.world_bounds = (-1000, -1000, 2000, 2000)  # Default world bounds (x, y, width, height)
        self.ui_particles = []  # List for particles in screen-space (UI)
        self.world_particles = []  # List for particles in world-space

    def set_screen_size(self, width: int, height: int):
        """Update screen dimensions for particle spawning bounds."""
        if width <= 0 or height <= 0:
            return  # Don't set invalid dimensions
        self.screen_width = width
        self.screen_height = height
        
        # Update the division between particle lists
        new_particles = []
        for particle in self.particles:
            new_particles.append(particle)
        self.particles = new_particles
        
    def set_world_bounds(self, x: float, y: float, width: float, height: float):
        """Set the world bounds for particle spawning."""
        self.world_bounds = (x, y, width, height)
        
    def emit(self, x: Optional[float] = None, y: Optional[float] = None, 
             particle_type: ParticleType = ParticleType.DUST,
             count: int = 1, 
             color: Optional[Tuple[int, int, int, int]] = None,
             size_range: Tuple[float, float] = (1.0, 3.0),
             max_speed: float = 10.0,
             lifetime_range: Tuple[float, float] = (2.0, 5.0),
             use_world_space: bool = True):
        """Emit particles with safety checks."""
        if self.disabled and count > 1:  # Allow single particle emission even when disabled
            return

        if len(self.particles) >= self.max_particles:
            return

        # Get world or screen bounds based on space
        world_x, world_y, world_width, world_height = self.world_bounds

        for _ in range(count):
            # Spawn randomly in world space if no position given
            if use_world_space:
                spawn_x = x if x is not None else random.uniform(world_x, world_x + world_width)
                spawn_y = y if y is not None else random.uniform(world_y, world_y + world_height)
            else:
                # Use screen space for UI particles
                spawn_x = x if x is not None else random.uniform(0, self.screen_width)
                spawn_y = y if y is not None else random.uniform(0, self.screen_height)
                spawn_y = y if y is not None else random.uniform(0, self.screen_height)
            
            size = random.uniform(*size_range)
            lifetime = random.uniform(*lifetime_range)
            
            # Use default color for dust, or provided color
            particle_color = color if color else (200, 200, 200, 180)
            if len(particle_color) == 3:
                particle_color = (*particle_color, 180)  # Add default alpha
                
            particle = Particle(
                spawn_x, spawn_y, particle_type,
                color=particle_color,
                size=size,
                lifetime=lifetime,
                screen_width=self.screen_width,
                screen_height=self.screen_height,
                use_world_space=use_world_space
            )
            
            # Particle knows if it's in world or screen space
            particle.use_world_space = use_world_space
            self.particles.append(particle)

    def update(self, dt: float):
        """Update all particles"""
        if self.disabled:
            self.particles.clear()
            return
            
        # Process particles based on space type
        remaining_particles = []
        world_x, world_y, world_width, world_height = self.world_bounds
        world_margin = 100  # Larger margin for world space
        screen_margin = 50  # Margin for screen space
        
        for particle in self.particles:
            # Update the particle physics
            if particle.update(dt):
                continue  # Skip dead particles
                
            if hasattr(particle, 'use_world_space') and particle.use_world_space:
                # Check world bounds for world-space particles
                if (world_x - world_margin < particle.x < world_x + world_width + world_margin and 
                    world_y - world_margin < particle.y < world_y + world_height + world_margin):
                    remaining_particles.append(particle)
            else:
                # Check screen bounds for screen-space particles
                if (-screen_margin < particle.x < self.screen_width + screen_margin and 
                    -screen_margin < particle.y < self.screen_height + screen_margin):
                    remaining_particles.append(particle)
        
        self.particles = remaining_particles
        
        if len(self.cached_surfaces) > 10:  # Keep cache check
            self.cached_surfaces.clear()

    def draw(self, surface: pygame.Surface, offset: Tuple[float, float] = (0, 0)):
        """Draw particles with alpha blending, applying camera offset only to world-space particles."""
        if not self.particles:
            return
            
        offset_x, offset_y = offset
        screen_rect = surface.get_rect()
        
        for particle in self.particles:
            # Calculate screen position from world position if in world space
            if hasattr(particle, 'use_world_space') and particle.use_world_space:
                screen_x = particle.x - offset_x
                screen_y = particle.y - offset_y
            else:
                # Use particle position directly if in screen space
                screen_x = particle.x
                screen_y = particle.y
            
            # Basic check if particle is potentially visible (with larger margin)
            particle_screen_rect = pygame.Rect(
                int(screen_x - particle.size * 3), 
                int(screen_y - particle.size * 3),
                int(particle.size * 6), 
                int(particle.size * 6)
            )
            
            # Skip if completely off-screen
            if not screen_rect.colliderect(particle_screen_rect):
                continue
                
            # Use a temporary surface for alpha blending
            size = int(particle.size * 2)  # Base diameter
            if size <= 0:
                continue  # Skip zero-size particles
            
            # Create particle surface based on type
            if particle.type == ParticleType.LEAF:
                # Create a leaf shape (more natural looking)
                size_x = int(size * 1.8)
                size_y = int(size * 1.3)
                leaf_surf = pygame.Surface((size_x, size_y), pygame.SRCALPHA)
                
                # Draw more realistic leaf shape with stem
                leaf_points = [
                    (size_x * 0.5, 0),                # Tip
                    (size_x * 0.8, size_y * 0.3),     # Right top curve
                    (size_x * 0.9, size_y * 0.5),     # Right bulge
                    (size_x * 0.8, size_y * 0.7),     # Right bottom curve
                    (size_x * 0.5, size_y * 0.9),     # Bottom before stem
                    (size_x * 0.5, size_y),           # Stem end
                    (size_x * 0.5, size_y * 0.9),     # Bottom before stem (mirror)
                    (size_x * 0.2, size_y * 0.7),     # Left bottom curve
                    (size_x * 0.1, size_y * 0.5),     # Left bulge
                    (size_x * 0.2, size_y * 0.3),     # Left top curve
                ]
                
                # Draw leaf outline and fill
                pygame.draw.polygon(leaf_surf, particle.color, leaf_points)
                
                # Add simple vein
                vein_color = (particle.color[0] * 0.8, particle.color[1] * 0.8, particle.color[2] * 0.8, particle.color[3] * 0.8)
                pygame.draw.line(leaf_surf, vein_color, 
                              (size_x * 0.5, 0), 
                              (size_x * 0.5, size_y * 0.8), 
                              max(1, int(size_x * 0.1)))
                
                # Rotate leaf
                rotated_leaf = pygame.transform.rotate(leaf_surf, particle.angle)
                # Get new rect for rotated surface
                rot_rect = rotated_leaf.get_rect(center=(int(screen_x), int(screen_y)))
                surface.blit(rotated_leaf, rot_rect, special_flags=pygame.BLEND_RGBA_ADD)
                
            elif particle.type == ParticleType.SPARKLE:
                # Create a softer sparkle (less sharp lines)
                sparkle_size = size * 2
                sparkle_surf = pygame.Surface((sparkle_size, sparkle_size), pygame.SRCALPHA)
                center = sparkle_size // 2
                
                # Draw softer glowy points instead of lines
                for angle in range(0, 360, 90):  # 4 main points
                    rad = math.radians(angle)
                    end_x = center + math.cos(rad) * (sparkle_size * 0.4)
                    end_y = center + math.sin(rad) * (sparkle_size * 0.4)
                    # Draw a small circle at the end of each line
                    pygame.draw.circle(sparkle_surf, particle.color, 
                                   (int(end_x), int(end_y)), 
                                   max(1, size // 3))
                                   
                # Center point glow
                pygame.draw.circle(sparkle_surf, particle.color, 
                               (center, center), 
                               max(1, size // 2))
                
                surface.blit(sparkle_surf, 
                           (int(screen_x - sparkle_size//2), 
                            int(screen_y - sparkle_size//2)),
                           special_flags=pygame.BLEND_RGBA_ADD)
                
            elif particle.type == ParticleType.STAR:
                # Simpler star drawing with more direct rendering
                # Create a simpler star with just a bright center and glow
                size = int(particle.size * 2) # Base size
                glow_size = int(particle.size * 4) # Outer glow size
                
                # Create surface for the star
                star_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                center = (glow_size, glow_size)
                
                # Get color components
                r, g, b = particle.color[0], particle.color[1], particle.color[2]
                alpha = particle.color[3]
                
                # Draw outer glow first
                for radius in range(glow_size, 0, -1):
                    # Calculate decreasing alpha for glow effect
                    glow_alpha = int(alpha * (radius / glow_size) ** 2)
                    if glow_alpha <= 0:
                        continue
                    
                    color = (r, g, b, glow_alpha)
                    pygame.draw.circle(star_surf, color, center, radius)
                
                # Draw center point
                pygame.draw.circle(star_surf, (r, g, b, alpha), center, size // 4)
                
                # Blit to screen
                surface.blit(star_surf, 
                           (int(screen_x - glow_size), 
                            int(screen_y - glow_size)))
            
            elif particle.type == ParticleType.SUNBEAM:
                # Create elongated beam
                beam_length = int(particle.beam_length)
                beam_width = size
                beam_surf = pygame.Surface((beam_width, beam_length), pygame.SRCALPHA)
                
                # Create gradient beam
                for y in range(beam_length):
                    alpha = int(particle.color[3] * (1 - y/beam_length))
                    color = (*particle.color[:3], alpha)
                    pygame.draw.line(beam_surf, color, 
                                  (beam_width//2, y), 
                                  (beam_width//2, y+1), 
                                  beam_width)
                
                surface.blit(beam_surf, 
                           (int(screen_x - beam_width//2), 
                            int(screen_y)),
                           special_flags=pygame.BLEND_RGBA_ADD)
                
            elif particle.type == ParticleType.FIREFLY:
                # Enhanced firefly with directional trail
                glow_size = size * 4.0  # Larger glow
                
                # Draw trail first (behind the glow)
                if hasattr(particle, 'trail_positions') and len(particle.trail_positions) > 1:
                    # Calculate movement direction for elongated trail effect
                    direction_x = particle.move_dir_x if hasattr(particle, 'move_dir_x') else 0
                    direction_y = particle.move_dir_y if hasattr(particle, 'move_dir_y') else 0
                    
                    # Draw trail particles with diminishing size and opacity
                    for i, (trail_x, trail_y) in enumerate(particle.trail_positions):
                        # Skip first position (current position)
                        if i == 0:
                            continue
                            
                        # Calculate screen position
                        if hasattr(particle, 'use_world_space') and particle.use_world_space:
                            trail_screen_x = trail_x - offset_x
                            trail_screen_y = trail_y - offset_y
                        else:
                            trail_screen_x = trail_x
                            trail_screen_y = trail_y
                        
                        # Decrease size and alpha based on position in trail
                        trail_factor = 1.0 - (i / len(particle.trail_positions))
                        trail_size = int(size * trail_factor * 0.8)  # Smaller trail particles
                        trail_alpha = int(particle.color[3] * trail_factor * 0.6)  # More transparent trail
                        
                        if trail_size <= 0:
                            continue
                            
                        trail_color = (*particle.color[:3], trail_alpha)
                        trail_surf = pygame.Surface((trail_size*2, trail_size*2), pygame.SRCALPHA)
                        pygame.draw.circle(trail_surf, trail_color, 
                                        (trail_size, trail_size), 
                                        trail_size)
                        
                        surface.blit(trail_surf, 
                                   (int(trail_screen_x - trail_size), 
                                    int(trail_screen_y - trail_size)),
                                   special_flags=pygame.BLEND_RGBA_ADD)
                
                # Create a better glow effect for the firefly
                glow_surf = pygame.Surface((int(glow_size*2), int(glow_size*2)), pygame.SRCALPHA)
                center = (int(glow_size), int(glow_size))
                
                # Get color components with enhanced brightness
                r, g, b = min(255, particle.color[0]*1.2), min(255, particle.color[1]*1.2), min(255, particle.color[2]*1.2)
                
                # Create a more pronounced core with multiple layers of glow
                for i in range(5):  # More layers for smoother falloff
                    radius = int(glow_size * (1.0 - (i / 5.0)))
                    # Higher alpha for central glow
                    alpha = int(min(255, particle.color[3] * (1.0 - (i / 7.0))))
                    color = (r, g, b, alpha)
                    pygame.draw.circle(glow_surf, color, center, radius)
                
                # Add directional elongation to the glow if moving
                if hasattr(particle, 'move_dir_x') and hasattr(particle, 'move_dir_y'):
                    speed = math.sqrt(particle.move_dir_x**2 + particle.move_dir_y**2)
                    if speed > 0.1:  # Only if moving significantly
                        elongation_length = int(glow_size * 0.8)
                        elongation_width = int(glow_size * 0.5)
                        
                        # Calculate the angle of movement
                        angle = math.atan2(particle.move_dir_y, particle.move_dir_x)
                        
                        # Create points for an elongated shape in the direction of movement
                        # This adds a subtle directional indicator to the glow
                        elongation_points = [
                            (center[0] + math.cos(angle) * elongation_length, 
                             center[1] + math.sin(angle) * elongation_length),
                            (center[0] + math.cos(angle + math.pi/2) * elongation_width,
                             center[1] + math.sin(angle + math.pi/2) * elongation_width),
                            (center[0] - math.cos(angle) * elongation_length/3,
                             center[1] - math.sin(angle) * elongation_length/3),
                            (center[0] + math.cos(angle - math.pi/2) * elongation_width,
                             center[1] + math.sin(angle - math.pi/2) * elongation_width)
                        ]
                        
                        # Draw a semi-transparent elongation
                        pygame.draw.polygon(glow_surf, (r, g, b, particle.color[3]//3), elongation_points)
                
                # Draw a bright core in the center
                core_size = max(2, int(size * 0.5))
                pygame.draw.circle(glow_surf, (min(255, r+40), min(255, g+40), min(255, b+40), 
                                    min(255, particle.color[3])), 
                                center, core_size)
                
                # Blit the complete firefly
                surface.blit(glow_surf, 
                           (int(screen_x - glow_size), 
                            int(screen_y - glow_size)),
                           special_flags=pygame.BLEND_RGBA_ADD)
        
            else:  # Default dust particle
                particle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, particle.color,
                                (size//2, size//2), size//2)
                surface.blit(particle_surf, 
                           (int(screen_x - size//2), 
                            int(screen_y - size//2)),
                           special_flags=pygame.BLEND_RGBA_ADD)

    def enable(self):
        """Enable the particle system"""
        self.disabled = False
        
    def disable(self):
        """Disable the particle system and clear all particles"""
        self.disabled = True
        self.particles.clear()

class SynapstexGraphics:
    def __init__(self, screen_size: Tuple[int, int], target_fps: int = 60, 
                 fullscreen: bool = False, vsync: bool = True):
        """Initialize the graphics engine"""
        self.screen_size = screen_size
        self.target_fps = target_fps
        self.fullscreen = fullscreen
        self.vsync = vsync
        
        # Initialize display with settings
        self.display_flags = pygame.SCALED  # Add SCALED flag for better scaling
        if self.fullscreen:
            self.display_flags |= pygame.FULLSCREEN
        if self.vsync:
            self.display_flags |= pygame.HWSURFACE | pygame.DOUBLEBUF
            
        self.render_layers: Dict[RenderLayer, List] = {layer: [] for layer in RenderLayer}
        self.cached_surfaces: Dict[str, pygame.Surface] = {}
        self.active_camera = None # Deprecated, use camera_offset instead
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.particle_system = ParticleSystem()
        self.particle_system.set_screen_size(*self.screen_size) # Initialize particle system size
        self.display_changed_callbacks = []
        
    def set_fullscreen(self, enabled: bool) -> bool:
        """Set fullscreen mode and reinitialize display if changed"""
        if self.fullscreen == enabled:
            return False  # No change
            
        self.fullscreen = enabled
        
        # Reset flags and set appropriate ones
        self.display_flags = pygame.SCALED  # Always include SCALED
        if self.fullscreen:
            self.display_flags |= pygame.FULLSCREEN
        if self.vsync:
            self.display_flags |= pygame.HWSURFACE | pygame.DOUBLEBUF
            
        self._update_display()
        return True
    
    def set_screen_resolution(self, width: int, height: int) -> bool:
        """Set screen resolution and reinitialize display if changed"""
        if self.screen_size == (width, height):
            return False  # No change
            
        self.screen_size = (width, height)
        self._update_display()
        return True
    
    def set_vsync(self, enabled: bool) -> bool:
        """Set vertical sync and reinitialize display if changed"""
        if self.vsync == enabled:
            return False  # No change
            
        self.vsync = enabled
        if self.vsync:
            self.display_flags |= pygame.HWSURFACE | pygame.DOUBLEBUF
        else:
            self.display_flags &= ~(pygame.HWSURFACE | pygame.DOUBLEBUF)
            
        self._update_display()
        return True
    
    def add_display_changed_callback(self, callback):
        """Register a callback to be notified when display settings change"""
        if callback not in self.display_changed_callbacks:
            self.display_changed_callbacks.append(callback)
    
    def remove_display_changed_callback(self, callback):
        """Remove a display change callback"""
        if callback in self.display_changed_callbacks:
            self.display_changed_callbacks.remove(callback)
    
    def _update_display(self) -> pygame.Surface:
        """Reinitialize the display with current settings"""
        # Center window when switching to windowed mode
        if not self.fullscreen:
            os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        try:
            # Get current display info
            display_info = pygame.display.Info()
            
            # Set display flags for Windows compatibility
            self.display_flags = pygame.HWSURFACE | pygame.DOUBLEBUF
            if self.fullscreen:
                self.display_flags |= pygame.FULLSCREEN
            
            # Set the display mode
            screen = pygame.display.set_mode(self.screen_size, self.display_flags)
            pygame.display.flip()  # Ensure the display updates
            
            # Update particle system with new screen size
            if hasattr(self, 'particle_system'):
                self.particle_system.set_screen_size(*self.screen_size)
            
            # Notify callbacks about the display change
            for callback in self.display_changed_callbacks:
                try:
                    callback(self.screen_size, self.fullscreen, self.vsync)
                except Exception as e:
                    print(f"Error in display changed callback: {e}")
                    
            return screen
        except pygame.error as e:
            print(f"Failed to set display mode: {e}")
            # Revert to windowed mode if fullscreen fails
            if self.fullscreen:
                self.fullscreen = False
                self.display_flags = pygame.HWSURFACE | pygame.DOUBLEBUF
                return pygame.display.set_mode(self.screen_size, self.display_flags)
            raise
    
    def update_screen_size(self, new_size: Tuple[int, int]):
        """Update the screen size for internal calculations (e.g., particle bounds)."""
        self.screen_size = new_size
        
        # Update particle system bounds if it exists
        if hasattr(self, 'particle_system'):
             self.particle_system.set_screen_size(*self.screen_size)

        # Clear cache if necessary, as cached surfaces might depend on size
        # Consider a more targeted cache invalidation if possible
        self.cached_surfaces.clear()

    def create_surface(self, size: Tuple[int, int], flags: int = pygame.SRCALPHA) -> pygame.Surface:
        """Create a new surface with the specified size and flags"""
        return pygame.Surface(size, flags)
    
    def cache_surface(self, name: str, surface: pygame.Surface):
        """Cache a surface for reuse"""
        self.cached_surfaces[name] = surface
    
    def get_cached_surface(self, name: str) -> Optional[pygame.Surface]:
        """Retrieve a cached surface"""
        return self.cached_surfaces.get(name)
    
    def add_to_layer(self, layer: RenderLayer, drawable: any):
        """Add an object to a render layer"""
        self.render_layers[layer].append(drawable)
    
    def clear_layer(self, layer: RenderLayer):
        """Clear all objects from a render layer"""
        self.render_layers[layer].clear()
    
    def draw_shape(self, surface: pygame.Surface, shape_type: str, 
                   color: Union[Tuple[int, int, int], Tuple[int, int, int, int]], 
                   params: Dict, blend_mode: BlendMode = BlendMode.NORMAL):
        """Draw various shapes with optional blend modes"""
        if shape_type == "rect":
            pygame.draw.rect(surface, color, params["rect"], 
                           params.get("width", 0), params.get("border_radius", -1))
        elif shape_type == "circle":
            pygame.draw.circle(surface, color, params["center"], params["radius"], 
                            params.get("width", 0))
        elif shape_type == "polygon":
            pygame.draw.polygon(surface, color, params["points"], 
                              params.get("width", 0))
        elif shape_type == "line":
            pygame.draw.line(surface, color, params["start"], params["end"], 
                           params.get("width", 1))
    
    def draw_text(self, surface: pygame.Surface, text: str, font: pygame.font.Font,
                  color: Tuple[int, int, int], position: Tuple[int, int],
                  align: str = "left", shadow: bool = False,
                  shadow_color: Tuple[int, int, int] = (0, 0, 0),
                  shadow_offset: Tuple[int, int] = (2, 2)):
        """Draw text with optional shadow and alignment"""
        if shadow:
            shadow_surface = font.render(text, True, shadow_color)
            shadow_pos = (position[0] + shadow_offset[0], 
                         position[1] + shadow_offset[1])
            surface.blit(shadow_surface, shadow_pos)
        
        text_surface = font.render(text, True, color)
        if align == "center":
            position = (position[0] - text_surface.get_width()//2, position[1])
        elif align == "right":
            position = (position[0] - text_surface.get_width(), position[1])
        
        surface.blit(text_surface, position)
    
    def create_gradient(self, size: Tuple[int, int], start_color: Tuple[int, int, int],
                       end_color: Tuple[int, int, int], vertical: bool = True) -> pygame.Surface:
        """Create a gradient surface"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        if vertical:
            for y in range(size[1]):
                factor = y / (size[1] - 1)
                color = tuple(int(start + (end - start) * factor) 
                            for start, end in zip(start_color, end_color))
                pygame.draw.line(surface, color, (0, y), (size[0], y))
        else:
            for x in range(size[0]):
                factor = x / (size[0] - 1)
                color = tuple(int(start + (end - start) * factor) 
                            for start, end in zip(start_color, end_color))
                pygame.draw.line(surface, color, (x, 0), (x, size[1]))
        return surface
    
    def create_rounded_rect(self, size: Tuple[int, int], radius: int,
                          color: Tuple[int, int, int],
                          alpha: int = 255) -> pygame.Surface:
        """Create a surface with a rounded rectangle"""
        rect_surf = pygame.Surface(size, pygame.SRCALPHA)
        rect_surf.fill((0, 0, 0, 0))
        
        r = radius
        w, h = size
        color_with_alpha = (*color, alpha)
        
        # Draw four rectangles
        pygame.draw.rect(rect_surf, color_with_alpha, (r, 0, w - 2*r, h))
        pygame.draw.rect(rect_surf, color_with_alpha, (0, r, w, h - 2*r))
        
        # Draw four circles for corners
        pygame.draw.circle(rect_surf, color_with_alpha, (r, r), r)
        pygame.draw.circle(rect_surf, color_with_alpha, (w - r, r), r)
        pygame.draw.circle(rect_surf, color_with_alpha, (r, h - r), r)
        pygame.draw.circle(rect_surf, color_with_alpha, (w - r, h - r), r)
        
        return rect_surf
    
    def draw_progress_bar(self, surface: pygame.Surface, rect: pygame.Rect,
                         progress: float, color: Tuple[int, int, int],
                         background_color: Optional[Tuple[int, int, int]] = None,
                         border_color: Optional[Tuple[int, int, int]] = None,
                         border_width: int = 1):
        """Draw a progress bar with optional background and border"""
        if background_color:
            pygame.draw.rect(surface, background_color, rect)
        
        # Draw progress
        progress_width = int(rect.width * max(0, min(1, progress)))
        progress_rect = pygame.Rect(rect.x, rect.y, progress_width, rect.height)
        pygame.draw.rect(surface, color, progress_rect)
        
        if border_color:
            pygame.draw.rect(surface, border_color, rect, border_width)
    
    def set_camera_target(self, target_x: float, target_y: float):
        """Calculate camera offset to keep the target centered."""
        # Center the camera on the target position
        self.camera_offset_x = target_x - self.screen_size[0] / 2
        self.camera_offset_y = target_y - self.screen_size[1] / 2
        # Potentially add clamping here later if needed to keep camera within world bounds

    def get_camera_offset(self) -> Tuple[float, float]:
        """Return the current camera offset."""
        return (self.camera_offset_x, self.camera_offset_y)
    
    def render_all(self, screen: pygame.Surface):
        """Render all layers onto the screen, applying camera offset."""
        offset = self.get_camera_offset()
        
        # Remove excessive debug prints that spam the console every frame
        # print(f"GRAPHICS DEBUG: Rendering {len(self.render_layers)} layers with offset {offset}")
        
        # Render layers in order
        for layer_type in RenderLayer:
            layer_objects = self.render_layers[layer_type]
            # if layer_objects:
            #     print(f"GRAPHICS DEBUG: Rendering {layer_type} with {len(layer_objects)} objects")
            
            if layer_type == RenderLayer.UI or layer_type == RenderLayer.UI_OVERLAY:
                 # Draw UI layers without camera offset
                 for drawable in layer_objects:
                     if hasattr(drawable, 'draw'):
                         try:
                             # Pass only screen for UI elements
                             drawable.draw(screen)
                         except TypeError:
                             # Fallback if draw doesn't take screen (or handle specific cases)
                             print(f"UI element {type(drawable)} draw method might need update.")
                         except Exception as e:
                             print(f"Error drawing UI element {type(drawable)}: {e}")
                             import traceback
                             traceback.print_exc()
            else:
                 # Draw game world layers with camera offset
                 for i, drawable in enumerate(layer_objects):
                     if hasattr(drawable, 'draw'):
                         # print(f"GRAPHICS DEBUG: Drawing {type(drawable)} object {i+1}/{len(layer_objects)}")
                         try:
                             # Pass screen and offset
                             drawable.draw(screen, offset)
                         except TypeError as e:
                             # Catch if the draw method doesn't accept offset yet
                             print(f"Drawable {type(drawable)} draw method doesn't accept offset? {e}")
                             try:
                                 # Attempt fallback to draw without offset (might look wrong)
                                 drawable.draw(screen)
                             except Exception as e_fallback:
                                  print(f"Error drawing {type(drawable)} even without offset: {e_fallback}")
                                  import traceback
                                  traceback.print_exc()
                         except Exception as e:
                             print(f"Error drawing {type(drawable)}: {e}")
                             import traceback
                             traceback.print_exc()
                             
        # Draw particles separately, applying offset
        if hasattr(self, 'particle_system') and not self.particle_system.disabled:
             try:
                 self.particle_system.draw(screen, offset)
             except Exception as e:
                 print(f"Error drawing particles: {e}")
                 self.particle_system.disabled = True # Disable particles on error
    
    def cleanup(self):
        """Clean up resources (if any needed in future)"""
        pass 