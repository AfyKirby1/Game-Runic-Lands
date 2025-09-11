import pygame
from entities.character import Character
from systems.sprite import CharacterSprite, AnimationState, Direction
from systems.inventory import Inventory, ItemType
from systems.stats import Stats
from systems.synapstex import ParticleType
import os
import logging
import random
from typing import Tuple, Dict

logger = logging.getLogger(__name__)

class Player(Character):
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], controls: Dict[str, int], world=None):
        super().__init__(x, y, color)
        self.pos = [x, y]
        self.color = color
        self.controls = controls
        self.world = world
        self.size = 32  # Player size in pixels
        self.speed = 200  # Pixels per second
        self.run_multiplier = 1.6  # Speed multiplier when running
        
        # Initialize player stats
        self.name = "Adventurer"
        self.level = 1
        self.stats = Stats()
        self.inventory = Inventory()
        
        # Create name text surface
        self.font = pygame.font.Font(None, 24)
        self.update_name_text()
        
        # Movement state
        self.moving = False
        self.running = False
        self.facing = "right"
        
        # Initialize sprite
        sprite_path = "assets/sprites/characters/player/png/base_wanderer.png"
        logger.info(f"Looking for sprite at: {sprite_path}")
        if os.path.exists(sprite_path):
            # If we have a sprite, use it
            self.use_sprite = True
            logger.info(f"Sprite found, loading it")
            # For now, we'll use a simple approach, until we have full sprite sheets
            # Later we'll use CharacterSprite from systems.sprite
            self.sprite_img = pygame.image.load(sprite_path).convert_alpha()
            logger.info(f"Sprite loaded successfully. Size: {self.sprite_img.get_size()}")
            
            # Load animation frames
            self.animations = {}
            self.load_animations()
            
            self.current_state = AnimationState.IDLE
            self.current_direction = Direction.DOWN
            self.animation_timer = 0
            self.animation_speed = 0.15  # Seconds per frame
            self.current_frame = 0
            
            logger.info(f"Animation system initialized. Available animations: {list(self.animations.keys())}")
        else:
            # Fall back to rectangle if sprite isn't available
            logger.warning(f"Sprite not found at {sprite_path}, using fallback rectangle")
            self.use_sprite = False
        
    def load_animation_frames(self, sprite_path: str, frame_count: int):
        """Load animation frames from a sprite sheet"""
        try:
            sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
            frames = []
            frame_width = sprite_sheet.get_width() // frame_count
            frame_height = sprite_sheet.get_height()
            
            for i in range(frame_count):
                frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                frame = sprite_sheet.subsurface(frame_rect)
                frames.append(frame)
                
            logger.info(f"Loaded {len(frames)} animation frames from {sprite_path}")
            return frames
        except Exception as e:
            logger.warning(f"Failed to load animation frames from {sprite_path}: {e}")
            return [self.sprite_img]  # Fallback to base sprite

    def load_animations(self):
        """Load animation frames"""
        # Check for animation sprite sheets
        base_dir = "assets/sprites/characters/player/png"
        
        # For now, since we only have base_body.png, use it for all animations
        logger.info("Loading animations...")
        
        # Idle animation - try specific file first, then fallback to base sprite
        idle_path = f"{base_dir}/base_wanderer_idle.png"
        if os.path.exists(idle_path):
            self.animations[AnimationState.IDLE] = self.load_animation_frames(idle_path, 4)
            logger.info("Loaded idle animation from sprite sheet")
        else:
            self.animations[AnimationState.IDLE] = [self.sprite_img]
            logger.info("Using base sprite for idle animation")
            
        # Walking animation - try specific file first, then fallback to base sprite
        walk_path = f"{base_dir}/base_wanderer_walk.png"
        if os.path.exists(walk_path):
            self.animations[AnimationState.WALKING] = self.load_animation_frames(walk_path, 4)
            logger.info("Loaded walking animation from sprite sheet")
        else:
            self.animations[AnimationState.WALKING] = [self.sprite_img]
            logger.info("Using base sprite for walking animation")
            
        # Attack animation - try specific file first, then fallback to base sprite
        attack_path = f"{base_dir}/base_wanderer_attack.png"
        if os.path.exists(attack_path):
            self.animations[AnimationState.ATTACKING] = self.load_animation_frames(attack_path, 4)
            logger.info("Loaded attack animation from sprite sheet")
        else:
            self.animations[AnimationState.ATTACKING] = [self.sprite_img]
            logger.info("Using base sprite for attack animation")
            
        logger.info(f"Animation loading complete. States available: {list(self.animations.keys())}")
        
    def update_name_text(self):
        """Update the name text surface with current name and level"""
        self.name_text = self.font.render(f"{self.name} Lv.{self.level}", True, (255, 255, 255))
        # Create a rect for the text surface
        self.name_text_rect = self.name_text.get_rect()
        # Set initial position (will be updated in game loop)
        self.name_text_rect.center = (0, 0)  # Initial position, will be updated later
        
    def move(self, keys):
        """Handle player movement based on keyboard input"""
        dx = dy = 0
        
        # Check if running key is pressed
        self.running = keys[self.controls.get('run', pygame.K_LSHIFT)]
        speed = self.speed * (self.run_multiplier if self.running else 1.0)
        
        # Track movement direction for animation
        move_direction = None
        
        if keys[self.controls['up']]:
            dy -= speed
            move_direction = Direction.UP
        if keys[self.controls['down']]:
            dy += speed
            move_direction = Direction.DOWN
        if keys[self.controls['left']]:
            dx -= speed
            self.facing = "left"
            move_direction = Direction.LEFT
        if keys[self.controls['right']]:
            dx += speed
            self.facing = "right"
            move_direction = Direction.RIGHT
            
        # Update movement state
        self.moving = dx != 0 or dy != 0
        
        # Update animation direction when moving
        if self.moving and move_direction:
            self.current_direction = move_direction
            
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071  # 1/√2
            dy *= 0.7071
            
            # For diagonal movement, prioritize horizontal direction for animation
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.current_direction = Direction.RIGHT
                    self.facing = "right"
                else:
                    self.current_direction = Direction.LEFT
                    self.facing = "left"
            else:
                if dy > 0:
                    self.current_direction = Direction.DOWN
                else:
                    self.current_direction = Direction.UP
            
        # Update position with delta time
        dt = 1/60  # Fixed time step for consistent movement
        new_x = self.pos[0] + dx * dt
        new_y = self.pos[1] + dy * dt
        
        # World bounds checking - prevent player from going outside world boundaries
        if self.world:
            world_width = self.world.width * 32  # Convert tiles to pixels
            world_height = self.world.height * 32
            
            # Keep player within world bounds with some padding from the border
            border_padding = 8  # Pixels from the border
            new_x = max(border_padding, min(new_x, world_width - self.size - border_padding))
            new_y = max(border_padding, min(new_y, world_height - self.size - border_padding))
        
        # Apply the bounded position
        self.pos[0] = new_x
        self.pos[1] = new_y
        
    def update(self, dt: float):
        """Update player state including animations"""
        # Store previous state for change detection
        prev_state = getattr(self, '_prev_state', None)
        prev_direction = getattr(self, '_prev_direction', None)
        
        # Update animation state based on movement
        if self.moving:
            self.current_state = AnimationState.WALKING
        else:
            self.current_state = AnimationState.IDLE
            
        # Log state changes for debugging
        if prev_state != self.current_state:
            logger.debug(f"Animation state changed: {prev_state} -> {self.current_state}")
            self._prev_state = self.current_state
            
        if prev_direction != self.current_direction:
            logger.debug(f"Animation direction changed: {prev_direction} -> {self.current_direction}")
            self._prev_direction = self.current_direction
            
        # Update animation timer and frame
        if self.use_sprite and hasattr(self, 'animations'):
            self.animation_timer += dt
            
            # Get current animation frames
            current_animation = self.animations.get(self.current_state, [self.sprite_img])
            
            # Ensure we have valid frames and current_frame is in bounds
            if current_animation and len(current_animation) > 0:
                # Check if it's time to advance to next frame
                if self.animation_timer >= self.animation_speed:
                    self.animation_timer = 0
                    self.current_frame = (self.current_frame + 1) % len(current_animation)
                    
                # Ensure current_frame is within bounds
                if self.current_frame >= len(current_animation):
                    self.current_frame = 0
            else:
                # Fallback if no animation frames available
                self.current_frame = 0
        
    def draw(self, screen: pygame.Surface, offset: Tuple[float, float] = (0, 0)):
        """Draw the player with proper animation"""
        # Calculate screen position (offset from camera)
        screen_x = int(self.pos[0] - offset[0])
        screen_y = int(self.pos[1] - offset[1])
        
        if self.use_sprite and hasattr(self, 'animations'):
            # Get current animation frame with safety checks
            current_animation = self.animations.get(self.current_state, [self.sprite_img])
            
            # Safety check for animation frames
            if current_animation and len(current_animation) > 0:
                # Ensure current_frame is within bounds
                safe_frame_index = min(self.current_frame, len(current_animation) - 1)
                current_sprite = current_animation[safe_frame_index]
            else:
                # Fallback to base sprite
                current_sprite = self.sprite_img
            
            # Handle sprite flipping based on direction
            sprite_to_draw = current_sprite
            if self.current_direction == Direction.LEFT:
                sprite_to_draw = pygame.transform.flip(current_sprite, True, False)
            elif self.current_direction == Direction.RIGHT:
                sprite_to_draw = current_sprite  # No flip needed for right
            elif self.current_direction == Direction.UP:
                sprite_to_draw = current_sprite  # Use base sprite for up movement
            elif self.current_direction == Direction.DOWN:
                sprite_to_draw = current_sprite  # Use base sprite for down movement
            else:
                # Fallback to old facing system for backwards compatibility
                if self.facing == "left":
                    sprite_to_draw = pygame.transform.flip(current_sprite, True, False)
                else:
                    sprite_to_draw = current_sprite
                
            # Draw the animated sprite
            screen.blit(sprite_to_draw, (screen_x, screen_y))
        elif self.use_sprite and hasattr(self, 'sprite_img'):
            # Draw the static sprite
            sprite_to_draw = self.sprite_img
            if self.facing == "left":
                sprite_to_draw = pygame.transform.flip(self.sprite_img, True, False)
            screen.blit(sprite_to_draw, (screen_x, screen_y))
        else:
            # Draw player body as a rectangle
            pygame.draw.rect(screen, self.color, 
                           (screen_x, screen_y, self.size, self.size))
            
            # Draw facing direction indicator
            indicator_color = (255, 255, 255)  # White
            if self.facing == "right":
                pygame.draw.rect(screen, indicator_color,
                               (screen_x + self.size - 4, screen_y + self.size//2 - 2, 4, 4))
            else:  # facing left
                pygame.draw.rect(screen, indicator_color,
                               (screen_x, screen_y + self.size//2 - 2, 4, 4))
        
        # Draw player name text above the player
        if hasattr(self, 'name_text') and hasattr(self, 'name_text_rect'):
            # Position the name text above the player in screen space
            self.name_text_rect.centerx = screen_x + self.size // 2
            self.name_text_rect.bottom = screen_y - 5
            screen.blit(self.name_text, self.name_text_rect)
        
    def add_item(self, item):
        """Add an item to the player's inventory"""
        self.inventory.add_item(item)
        
    def remove_item(self, item):
        """Remove an item from the player's inventory"""
        self.inventory.remove_item(item)
    
    def use_item(self, index):
        """Use an item at the given inventory slot"""
        item = self.inventory.get_item(index)
        if not item:
            return False
            
        # Handle different item types
        if item.item_type == ItemType.CONSUMABLE:
            # Handle consumable use logic
            self.inventory.remove_item(index)
            return True
        elif item.can_equip():
            # Equip the item
            return self.inventory.equip_item(index)
            
        return False

    def get_stats_with_equipment(self):
        """Get player stats including equipment bonuses"""
        base_stats = {
            "hp": self.stats.hp,
            "mp": self.stats.mp,
            "strength": self.stats.strength,
            "agility": self.stats.agility,
            "intelligence": self.stats.intelligence,
            "vitality": self.stats.vitality
        }
        
        equipment_bonuses = self.inventory.equipment.get_stats_boost()
        
        # Combine base stats with equipment bonuses
        combined_stats = base_stats.copy()
        for stat, value in equipment_bonuses.items():
            if stat in combined_stats:
                combined_stats[stat] += value
                
        return combined_stats 