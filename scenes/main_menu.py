import pygame
import random # Added for particle emission
from typing import Optional
from systems.effects.fireworks import FireworksEffect
from systems.synapstex import SynapstexGraphics, ParticleType
import os

class MainMenu:
    def __init__(self, graphics: SynapstexGraphics):
        self.graphics = graphics
        self.screen_size = self.graphics.screen_size
        
        # Save reference to options system
        self.options_system = getattr(graphics, 'options_system', None)
        
        # Initialize fireworks effect
        self.fireworks = FireworksEffect(self.graphics)
        
        # Ensure the particle system knows the screen size
        self.graphics.particle_system.set_screen_size(self.screen_size[0], self.screen_size[1])
        
        # Initialize multiple particle effects
        self._initialize_particle_effects()
        
        # Load fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)
        
        # Menu items
        self.menu_items = [
            {"text": "Play Game", "action": "play"},
            {"text": "Options", "action": "options"},
            {"text": "Quit", "action": "quit"}
        ]
        
        # Selected menu item
        self.selected_index = 0
        
        # Create menu background
        self.background = self.graphics.create_gradient(
            size=self.screen_size,
            start_color=(20, 20, 40),
            end_color=(40, 40, 60)
        )

        # Store menu item rectangles for click detection
        self.menu_item_rects = []
        for i, item in enumerate(self.menu_items):
            text = self.menu_font.render(item["text"], True, (0,0,0)) # Render temporarily for size
            rect = text.get_rect(center=(
                self.screen_size[0] // 2,
                250 + i * 50
            ))
            self.menu_item_rects.append(rect)

        # Particle emission timers
        self.sparkle_timer = 0
        self.firefly_timer = 0
        self.dust_timer = 0
        self.leaf_timer = 0

    def _initialize_particle_effects(self):
        """Initialize all the different particle effects for the main menu"""
        # Emit initial stars across the screen
        for _ in range(25):
             self.graphics.particle_system.emit(
                 x=random.uniform(0, self.screen_size[0]),
                 y=random.uniform(0, self.screen_size[1]),
                 particle_type=ParticleType.STAR,
                 count=1,
                 color=(220, 225, 255, 160),
                 size_range=(1.0, 3.0),
                 lifetime_range=(8.0, 15.0),
                 use_world_space=False # Keep stars fixed to the screen
             )

        # Emit initial sparkles for magical effect
        for _ in range(15):
             self.graphics.particle_system.emit(
                 x=random.uniform(0, self.screen_size[0]),
                 y=random.uniform(self.screen_size[1] * 0.7, self.screen_size[1]),
                 particle_type=ParticleType.SPARKLE,
                 count=1,
                 color=(255, 215, 0, 180),  # Golden sparkles
                 size_range=(2.0, 4.0),
                 lifetime_range=(3.0, 6.0),
                 use_world_space=False
             )

        # Emit fireflies for ambient life
        for _ in range(8):
             self.graphics.particle_system.emit(
                 x=random.uniform(0, self.screen_size[0]),
                 y=random.uniform(0, self.screen_size[1]),
                 particle_type=ParticleType.FIREFLY,
                 count=1,
                 color=(255, 255, 150, 120),  # Soft yellow glow
                 size_range=(1.5, 3.0),
                 lifetime_range=(10.0, 20.0),
                 use_world_space=False
             )

        # Emit floating dust particles
        for _ in range(12):
             self.graphics.particle_system.emit(
                 x=random.uniform(0, self.screen_size[0]),
                 y=random.uniform(0, self.screen_size[1]),
                 particle_type=ParticleType.DUST,
                 count=1,
                 color=(200, 200, 200, 80),  # Light dust
                 size_range=(0.5, 1.5),
                 lifetime_range=(6.0, 12.0),
                 use_world_space=False
             )

        # Emit falling leaves for natural ambiance
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
        
        for _ in range(15):  # More initial leaves
             selected_color = random.choice(leaf_colors)
             self.graphics.particle_system.emit(
                 x=random.uniform(0, self.screen_size[0]),
                 y=random.uniform(-50, self.screen_size[1] * 0.3),  # Start from top
                 particle_type=ParticleType.LEAF,
                 count=1,
                 color=selected_color,
                 size_range=(2.0, 4.5),
                 lifetime_range=(8.0, 15.0),
                 use_world_space=False
             )

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle pygame events and return action if needed."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                # Add sound effect for selection change (optional)
                # self.graphics.options_system.play_sound('menu_select')
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                # Add sound effect (optional)
                # self.graphics.options_system.play_sound('menu_select')
            elif event.key == pygame.K_RETURN:
                # Add sound effect for confirmation (optional)
                # self.graphics.options_system.play_sound('menu_click')
                return self.menu_items[self.selected_index]["action"]
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.menu_item_rects):
                    if rect.collidepoint(mouse_pos):
                        # Add sound effect (optional)
                        # self.graphics.options_system.play_sound('menu_click')
                        self.selected_index = i # Select the clicked item
                        return self.menu_items[i]["action"]
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.menu_item_rects):
                if rect.collidepoint(mouse_pos):
                    if self.selected_index != i:
                        self.selected_index = i
                        # Add sound effect (optional)
                        # self.graphics.options_system.play_sound('menu_select')
                    break # Stop checking once a hover is found

        return None

    def update(self, dt: float):
        """Update game state."""
        self.fireworks.update(dt)
        self.graphics.particle_system.update(dt)

        # Update particle emission timers
        self.sparkle_timer += dt
        self.firefly_timer += dt
        self.dust_timer += dt
        self.leaf_timer += dt

        # Continuously emit stars
        if random.random() < 0.4 * dt: # Approx 1 star every 2.5 seconds
             self.graphics.particle_system.emit(
                 x=random.uniform(0, self.screen_size[0]),
                 y=random.uniform(0, self.screen_size[1]),
                 particle_type=ParticleType.STAR,
                 count=1,
                 color=(220, 225, 255, random.randint(120, 200)), # Randomize alpha slightly
                 size_range=(1.0, 3.0),
                 lifetime_range=(8.0, 15.0),
                 use_world_space=False
             )

        # Emit sparkles periodically
        if self.sparkle_timer > 1.5:  # Every 1.5 seconds
            self.graphics.particle_system.emit(
                x=random.uniform(0, self.screen_size[0]),
                y=random.uniform(self.screen_size[1] * 0.6, self.screen_size[1]),
                particle_type=ParticleType.SPARKLE,
                count=random.randint(1, 3),
                color=(255, 215, 0, random.randint(150, 200)),  # Golden sparkles
                size_range=(2.0, 4.0),
                lifetime_range=(3.0, 6.0),
                use_world_space=False
            )
            self.sparkle_timer = 0

        # Emit fireflies occasionally
        if self.firefly_timer > 3.0:  # Every 3 seconds
            self.graphics.particle_system.emit(
                x=random.uniform(0, self.screen_size[0]),
                y=random.uniform(0, self.screen_size[1]),
                particle_type=ParticleType.FIREFLY,
                count=1,
                color=(255, 255, 150, random.randint(100, 140)),  # Soft yellow glow
                size_range=(1.5, 3.0),
                lifetime_range=(12.0, 25.0),
                use_world_space=False
            )
            self.firefly_timer = 0

        # Emit dust particles
        if self.dust_timer > 2.0:  # Every 2 seconds
            self.graphics.particle_system.emit(
                x=random.uniform(0, self.screen_size[0]),
                y=random.uniform(self.screen_size[1] * 0.8, self.screen_size[1]),
                particle_type=ParticleType.DUST,
                count=random.randint(2, 4),
                color=(200, 200, 200, random.randint(60, 100)),  # Light dust
                size_range=(0.5, 1.5),
                lifetime_range=(8.0, 15.0),
                use_world_space=False
            )
            self.dust_timer = 0

        # Emit falling leaves occasionally
        if self.leaf_timer > 3.0:  # Every 3 seconds (reduced from 4)
            # Define autumn leaf colors
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
            
            leaf_count = random.randint(2, 4)  # More leaves per emission
            for _ in range(leaf_count):
                selected_color = random.choice(leaf_colors)
                self.graphics.particle_system.emit(
                    x=random.uniform(0, self.screen_size[0]),
                    y=random.uniform(-50, 0),  # Start from above the screen
                    particle_type=ParticleType.LEAF,
                    count=1,
                    color=selected_color,
                    size_range=(2.0, 4.5),
                    lifetime_range=(10.0, 18.0),
                    use_world_space=False
                )
            self.leaf_timer = 0

    def draw(self, screen: pygame.Surface):
        """Draw the menu to the screen."""
        # Draw background
        screen.blit(self.background, (0, 0))
        
        # Draw original particles (behind fireworks)
        self.graphics.particle_system.draw(screen)
        
        # Draw fireworks
        self.fireworks.draw(screen)
        
        # Draw title
        title_text = self.title_font.render("Runic Lands", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_size[0] // 2, 100))
        screen.blit(title_text, title_rect)
        
        # Draw menu items
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 255) if i == self.selected_index else (200, 200, 200)
            text = self.menu_font.render(item["text"], True, color)
            rect = text.get_rect(center=(
                self.screen_size[0] // 2,
                250 + i * 50
            ))
            screen.blit(text, rect)

    def cleanup(self):
        """Clean up resources."""
        self.fireworks.clear()

    def start_menu_music(self):
        """Start menu music using the options system"""
        if self.options_system:
            # First stop any currently playing music
            self.options_system.stop_music()
            
            # Try to start the menu music with sections
            try:
                print("Starting menu music from MainMenu...")
                result = self.options_system.start_seamless_menu_music()
                if result:
                    print("Menu music started successfully with seamless section playback.")
                    return True
                else:
                    print("Seamless playback failed, trying standard queue method.")
                    # Fallback to original queue method
                    result = self.options_system.queue_section_music()
                    if result:
                        print("Menu music started with queue method.")
                        return True
                    else:
                        print("Queue method failed, falling back to standard playback.")
                        # Fallback to standard theme if available
                        fallback_path = "assets/audio/menu_theme.wav"
                        if os.path.exists(fallback_path):
                            self.options_system.play_music(fallback_path)
                            return True
                        else:
                            print("ERROR: No menu music files available")
                            return False
            except Exception as e:
                print(f"Error starting menu music: {e}")
                # Try fallback
                fallback_path = "assets/audio/menu_theme.wav"
                if os.path.exists(fallback_path):
                    self.options_system.play_music(fallback_path)
                    return True
                else:
                    print("ERROR: No menu music files available after error")
                    return False
        else:
            print("WARNING: No options system available, cannot play menu music")
            return False 