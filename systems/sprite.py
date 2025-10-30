import pygame
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import os

class Direction(Enum):
    """Enumeration for character facing directions."""
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()

class AnimationState(Enum):
    """Enumeration for character animation states."""
    IDLE = auto()
    WALKING = auto()
    ATTACKING = auto()
    HURT = auto()

class SpriteSheet:
    """
    A class for loading and parsing sprite sheets.

    This utility class loads a single image file and provides a method to
    extract individual sprites from it.
    """
    def __init__(self, filename: str):
        """
        Initializes the SpriteSheet.

        Args:
            filename (str): The path to the sprite sheet image file.
        """
        self.sprite_sheet = pygame.image.load(filename).convert_alpha()
        
    def get_sprite(self, x: int, y: int, width: int, height: int) -> pygame.Surface:
        """
        Extracts a single sprite from the spritesheet.

        Args:
            x (int): The x-coordinate of the top-left corner of the sprite.
            y (int): The y-coordinate of the top-left corner of the sprite.
            width (int): The width of the sprite.
            height (int): The height of the sprite.

        Returns:
            pygame.Surface: The extracted sprite as a new Surface.
        """
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite

class CharacterSprite:
    """
    Manages character animations and state.

    This class handles loading animations from a sprite sheet, updating the
    current animation frame, and managing the character's state (e.g., idle,
    walking) and direction.
    """
    def __init__(self, sprite_path: str, frame_size: Tuple[int, int] = (32, 32)):
        """
        Initializes the CharacterSprite.

        Args:
            sprite_path (str): Path to the character's sprite sheet.
            frame_size (Tuple[int, int], optional): The size of a single frame.
                                                    Defaults to (32, 32).
        """
        self.sprite_sheet = SpriteSheet(sprite_path)
        self.frame_size = frame_size
        self.animations: Dict[AnimationState, Dict[Direction, List[pygame.Surface]]] = {}
        self.current_state = AnimationState.IDLE
        self.current_direction = Direction.DOWN
        self.current_frame = 0
        self.animation_speed = 0.15  # Seconds per frame
        self.animation_timer = 0
        self.load_animations()
        
    def load_animations(self):
        """
        Loads all animation frames from the sprite sheet.

        This method parses the sprite sheet based on predefined row and column
        layouts for different animation states and directions, populating the
        `self.animations` dictionary.
        """
        # Animation frame counts
        frame_counts = {
            AnimationState.IDLE: 1,
            AnimationState.WALKING: 4,
            AnimationState.ATTACKING: 4,
            AnimationState.HURT: 2
        }
        
        # Y positions for each direction in the spritesheet
        direction_rows = {
            Direction.DOWN: 0,
            Direction.LEFT: 1,
            Direction.RIGHT: 2,
            Direction.UP: 3
        }
        
        # X positions for each animation state in the spritesheet
        state_cols = {
            AnimationState.IDLE: 0,
            AnimationState.WALKING: 1,
            AnimationState.ATTACKING: 5,
            AnimationState.HURT: 9
        }
        
        # Load each animation
        for state in AnimationState:
            self.animations[state] = {}
            for direction in Direction:
                frames = []
                for frame in range(frame_counts[state]):
                    x = (state_cols[state] + frame) * self.frame_size[0]
                    y = direction_rows[direction] * self.frame_size[1]
                    frames.append(
                        self.sprite_sheet.get_sprite(x, y, *self.frame_size)
                    )
                self.animations[state][direction] = frames
                
    def update(self, dt: float):
        """
        Updates the animation frame based on elapsed time.

        Args:
            dt (float): The time delta since the last update, in seconds.
        """
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(
                self.animations[self.current_state][self.current_direction]
            )
            
    def set_state(self, state: AnimationState):
        """
        Changes the character's animation state.

        If the new state is different from the current one, it resets the
        animation frame and timer.

        Args:
            state (AnimationState): The new animation state to set.
        """
        if state != self.current_state:
            self.current_state = state
            self.current_frame = 0
            self.animation_timer = 0
            
    def set_direction(self, direction: Direction):
        """
        Changes the character's facing direction.

        Args:
            direction (Direction): The new direction to set.
        """
        if direction != self.current_direction:
            self.current_direction = direction
            
    def get_current_frame(self) -> pygame.Surface:
        """
        Gets the current animation frame to be drawn.

        Returns:
            pygame.Surface: The Surface of the current animation frame.
        """
        return self.animations[self.current_state][self.current_direction][
            self.current_frame
        ]

class NPCSprite(CharacterSprite):
    """
    Extends CharacterSprite with NPC-specific logic, such as interaction range.
    """
    def __init__(self, sprite_path: str, frame_size: Tuple[int, int] = (32, 32)):
        """
        Initializes the NPCSprite.

        Args:
            sprite_path (str): Path to the NPC's sprite sheet.
            frame_size (Tuple[int, int], optional): The size of a single frame.
                                                    Defaults to (32, 32).
        """
        super().__init__(sprite_path, frame_size)
        self.interaction_range = 50  # Pixels
        
    def is_in_range(self, player_pos: Tuple[float, float], 
                    npc_pos: Tuple[float, float]) -> bool:
        """
        Checks if the player is within the NPC's interaction range.

        Args:
            player_pos (Tuple[float, float]): The player's current position.
            npc_pos (Tuple[float, float]): The NPC's current position.

        Returns:
            bool: True if the player is in range, False otherwise.
        """
        dx = player_pos[0] - npc_pos[0]
        dy = player_pos[1] - npc_pos[1]
        return (dx * dx + dy * dy) <= self.interaction_range * self.interaction_range

class AnimalSprite(CharacterSprite):
    """
    Extends CharacterSprite with animal-specific logic and animations.
    """
    def __init__(self, sprite_path: str, frame_size: Tuple[int, int] = (32, 32)):
        """
        Initializes the AnimalSprite.

        Args:
            sprite_path (str): Path to the animal's sprite sheet.
            frame_size (Tuple[int, int], optional): The size of a single frame.
                                                    Defaults to (32, 32).
        """
        super().__init__(sprite_path, frame_size)
        self.behavior_timer = 0
        self.behavior_duration = 3.0  # Seconds between behavior changes
        
    def update(self, dt: float):
        """
        Updates the animal's animation and behavior timer.

        Args:
            dt (float): The time delta since the last update, in seconds.
        """
        super().update(dt)
        self.behavior_timer += dt
        if self.behavior_timer >= self.behavior_duration:
            self.behavior_timer = 0
            # Implement random behavior changes here 