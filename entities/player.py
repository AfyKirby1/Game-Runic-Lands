import pygame
from .character import Character
from systems.sprite import CharacterSprite, AnimationState, Direction
from systems.inventory import Inventory, ItemType
from systems.stats import Stats
from systems.synapstex import ParticleType
import os
import logging
import random
from typing import Tuple

logger = logging.getLogger(__name__)

class Player(Character):
    def __init__(self, x: int, y: int, color: tuple, controls: dict, world=None):
        super().__init__(x, y, color)
        self.controls = controls
        self.size = (32, 32)
        self.rect = pygame.Rect(x, y, *self.size)
        self.pos = [x, y]  # For compatibility with existing code
        self.world = world  # Add world reference
        
        # Initialize inventory
        self.inventory = Inventory(20)  # Create inventory with 20 slots
        self.stats = Stats()  # Initialize player stats
        
        # Movement speeds
        self.stats.speed = 75  # Base speed increased from 50
        self.base_speed = 75  # Store base speed for reference
        self.run_multiplier = 2.5  # Run speed multiplier
        
        # Movement attributes
        self.vx = 0  # Horizontal velocity
        self.vy = 0  # Vertical velocity
        self.max_speed = 150  # Maximum movement speed (increased from 100)
        self.acceleration = 200  # Movement acceleration
        self.friction = 0.85  # Movement friction (slows down when not moving)
        self.is_moving = False  # Track if player is moving
        
        # Initialize job and level attributes
        self.job = "Adventurer"
        self.level = self.stats.level
        
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
            
            # Load animation frames
            self.animations = {}
            self.load_animations()
            
            self.current_state = AnimationState.IDLE
            self.current_direction = Direction.DOWN
            self.animation_timer = 0
            self.animation_speed = 0.15  # Seconds per frame
            self.current_frame = 0
        else:
            # Fall back to rectangle if sprite isn't available
            logger.warning(f"Sprite not found at {sprite_path}, using fallback rectangle")
            self.use_sprite = False
        
    def load_animations(self):
        """Load animation frames"""
        # Check for animation sprite sheets
        base_dir = "assets/sprites/characters/player/png"
        
        # Idle animation
        idle_path = f"{base_dir}/base_wanderer_idle.png"
        if os.path.exists(idle_path):
            self.animations[AnimationState.IDLE] = self.load_animation_frames(idle_path, 4)
        else:
            self.animations[AnimationState.IDLE] = [self.sprite_img]
            
        # Walking animation
        walk_path = f"{base_dir}/base_wanderer_walk.png"
        if os.path.exists(walk_path):
            self.animations[AnimationState.WALKING] = self.load_animation_frames(walk_path, 4)
        else:
            self.animations[AnimationState.WALKING] = [self.sprite_img]
            
        # Attack animation
        attack_path = f"{base_dir}/base_wanderer_attack.png"
        if os.path.exists(attack_path):
            self.animations[AnimationState.ATTACKING] = self.load_animation_frames(attack_path, 4)
        else:
            self.animations[AnimationState.ATTACKING] = [self.sprite_img]
    
    def load_animation_frames(self, sheet_path, frame_count):
        """Extract animation frames from a sprite sheet"""
        sheet = pygame.image.load(sheet_path).convert_alpha()
        frames = []
        frame_width = sheet.get_width() // frame_count
        frame_height = sheet.get_height()
        
        for i in range(frame_count):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
            frames.append(frame)
            
        return frames
        
    def move(self, keys):
        """Handle player movement"""
        # Calculate target velocity based on key presses
        target_vx = 0
        target_vy = 0
        
        # Check if running
        is_running = keys[self.controls['run']]
        current_speed = self.stats.speed * (self.run_multiplier if is_running else 1.0)
        current_max_speed = self.max_speed * (self.run_multiplier if is_running else 1.0)
        
        if keys[self.controls['left']]:
            target_vx = -current_speed
            self.current_direction = Direction.LEFT
        if keys[self.controls['right']]:
            target_vx = current_speed
            self.current_direction = Direction.RIGHT
        if keys[self.controls['up']]:
            target_vy = -current_speed
            self.current_direction = Direction.UP
        if keys[self.controls['down']]:
            target_vy = current_speed
            self.current_direction = Direction.DOWN
            
        # Store previous position for movement check
        self.prev_pos = self.pos.copy()
        
        # Apply acceleration toward target velocity
        dt = 1/60  # Assume 60 FPS if not provided
        
        # Gradually approach target velocity
        if target_vx != 0:
            self.vx += (target_vx - self.vx) * 0.2
        else:
            self.vx *= 0.8  # Apply friction when no input
            
        if target_vy != 0:
            self.vy += (target_vy - self.vy) * 0.2
        else:
            self.vy *= 0.8  # Apply friction when no input
        
        # Cap velocity to max speed
        speed = (self.vx**2 + self.vy**2)**0.5
        if speed > current_max_speed:
            scale = current_max_speed / speed
            self.vx *= scale
            self.vy *= scale
        
        # Update animation state based on movement
        if self.vx != 0 or self.vy != 0:
            self.current_state = AnimationState.WALKING
            self.is_moving = True
            # Adjust animation speed based on running
            self.animation_speed = 0.1 if is_running else 0.15
        else:
            self.current_state = AnimationState.IDLE
            self.is_moving = False
            self.animation_speed = 0.15  # Reset animation speed
    
    def is_moving(self) -> bool:
        """Check if the player is currently moving"""
        if not hasattr(self, 'prev_pos'):
            return False
        return self.pos != self.prev_pos
    
    def set_state(self, state):
        """Change animation state"""
        if self.current_state != state:
            self.current_state = state
            self.current_frame = 0
            self.animation_timer = 0
    
    def update(self, dt):
        """Update player state, position, and animation."""
        # logger.debug(f"Player update called with dt: {dt}") # Commented out: can be verbose
        try:
            # Update movement/position based on velocity
            self.pos[0] += self.vx * dt
            self.pos[1] += self.vy * dt

            # Keep player on screen - add screen boundary checks
            # REMOVED CLAMPING - World boundaries handled by collision / chunk loading
            # if self.world and hasattr(self.world, 'width') and hasattr(self.world, 'height'):
            #     # Clamp to world boundaries
            #     self.pos[0] = max(0, min(self.pos[0], self.world.width - self.size[0]))
            #     self.pos[1] = max(0, min(self.pos[1], self.world.height - self.size[1]))
            # else:
            #     # Fallback to reasonable screen boundaries if world dimensions aren't available
            #     self.pos[0] = max(0, min(self.pos[0], 800 - self.size[0]))
            #     self.pos[1] = max(0, min(self.pos[1], 600 - self.size[1]))
            # END REMOVAL

            self.rect.topleft = self.pos
            
            # Apply friction/damping
            damping = 0.85  # Adjust for desired slipperiness
            self.vx *= damping
            self.vy *= damping
            
            # Stop movement if velocity is very low
            threshold = 0.1
            if abs(self.vx) < threshold:
                self.vx = 0
            if abs(self.vy) < threshold:
                self.vy = 0
                
            # Determine animation state based on velocity
            if self.vx != 0 or self.vy != 0:
                self.current_state = AnimationState.WALKING
            else:
                self.current_state = AnimationState.IDLE
                
            # Update direction based on velocity (prioritize horizontal)
            if self.vx > 0:
                self.current_direction = Direction.RIGHT
            elif self.vx < 0:
                self.current_direction = Direction.LEFT
            elif self.vy > 0:
                self.current_direction = Direction.DOWN
            elif self.vy < 0:
                self.current_direction = Direction.UP
            
            # Update sprite animation
            if hasattr(self, 'sprite') and self.use_sprite:
                self.animation_timer += dt
                if self.animation_timer >= self.animation_speed:
                    self.animation_timer = 0
                    frames = self.animations[self.current_state]
                    self.current_frame = (self.current_frame + 1) % len(frames)
            
            # Emit movement particles (if moving and graphics available)
            if (self.vx != 0 or self.vy != 0) and hasattr(self.world, 'graphics'):
                if random.random() < 0.3: # Chance to emit particle
                     self.world.graphics.particle_system.emit(
                        self.rect.centerx, self.rect.bottom, # Emit from feet
                        particle_type=ParticleType.DUST,
                        count=1,
                        color=(180, 180, 180, 150), # Dusty color
                        size_range=(1.0, 2.5),
                        max_speed=5.0,
                        lifetime_range=(0.2, 0.5)
                    )

        except Exception as e:
            logger.error(f"Error during player update: {e}", exc_info=True)
            # Optionally handle error, e.g., reset player state
        
        # Apply equipment stat bonuses
        equipment_stats = self.inventory.equipment.get_stats_boost()
        for stat, value in equipment_stats.items():
            # Apply temporary stat boosts for this frame
            # In a more complex system, we'd have base_stats and bonus_stats
            if hasattr(self.stats, stat):
                # For now, we'll just modify the stats directly
                # A better approach would be to cache original stats and apply modifiers
                pass
        
    def draw(self, screen, offset: Tuple[float, float] = (0, 0)):
        offset_x, offset_y = offset
        screen_pos_x = self.pos[0] - offset_x
        screen_pos_y = self.pos[1] - offset_y

        # Basic culling
        if screen_pos_x + self.size[0] < 0 or screen_pos_x > screen.get_width() or \
           screen_pos_y + self.size[1] < 0 or screen_pos_y > screen.get_height():
           return

        if self.use_sprite:
            # Get current animation frame
            frames = self.animations[self.current_state]
            current_frame_index = self.current_frame % len(frames) # Ensure index is valid
            current_frame_img = frames[current_frame_index]
            
            # Flip sprite based on direction
            if self.current_direction == Direction.LEFT:
                current_frame_img = pygame.transform.flip(current_frame_img, True, False)
            
            # Draw sprite at screen position
            screen.blit(current_frame_img, (int(screen_pos_x), int(screen_pos_y)))
        else:
            # Fallback to rectangle
            pygame.draw.rect(screen, self.color, 
                           (int(screen_pos_x), int(screen_pos_y), self.size[0], self.size[1]))
        
        # Health bar (drawn relative to screen position)
        bar_width = 32
        bar_height = 5
        health_percentage = max(0, min(1, self.stats.hp / self.stats.max_hp))
        
        # Background of health bar
        pygame.draw.rect(screen, (255, 0, 0), 
                         (int(screen_pos_x), int(screen_pos_y) - 10, bar_width, bar_height))
        # Foreground (current health)
        pygame.draw.rect(screen, (0, 255, 0),
                         (int(screen_pos_x), int(screen_pos_y) - 10, 
                          int(bar_width * health_percentage), bar_height))
        
        # Draw job and level (drawn relative to screen position)
        font = pygame.font.Font(None, 20)
        text = font.render(f"{self.job} Lv.{self.level}", True, (255, 255, 255))
        screen.blit(text, (int(screen_pos_x), int(screen_pos_y) - 25))
    
    def add_item(self, item):
        """Add an item to player's inventory"""
        return self.inventory.add_item(item)
    
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