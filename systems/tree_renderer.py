"""
Modern Tree Renderer for Runic Lands

This module provides optimized tree rendering with persistent colors
to prevent the flashing issue. Trees are rendered using pre-calculated
colors stored in the tree data.

Key Features:
- No random color generation during rendering
- Persistent colors prevent flashing
- Optimized rendering with caching
- Support for multiple tree types
- Proper depth layering and shadows
"""

import pygame
import math
from typing import Tuple, List, Optional
from dataclasses import dataclass
from systems.world_generation_modern import TreeData, TreeType


@dataclass
class RenderConfig:
    """
    Holds configuration settings for the tree renderer.

    Attributes:
        tile_size (int): The size of a single tile in pixels.
        shadow_enabled (bool): Whether to render tree shadows.
        shadow_alpha (int): The alpha transparency of shadows (0-255).
        shadow_length (int): The length of the rendered shadows.
        wind_effect (bool): Whether to apply a wind sway effect to trees.
        wind_strength (float): The strength of the wind effect.
    """
    tile_size: int = 32
    shadow_enabled: bool = True
    shadow_alpha: int = 80
    shadow_length: int = 15
    wind_effect: bool = True
    wind_strength: float = 0.5


class ModernTreeRenderer:
    """
    Handles the rendering of trees with persistent colors and optimizations.

    This renderer is designed to work with `TreeData` objects, ensuring that
    each tree maintains its appearance across frames, preventing flashing.
    It supports different tree types, wind effects, and shadows.
    """
    
    def __init__(self, config: Optional[RenderConfig] = None):
        """
        Initializes the ModernTreeRenderer.

        Args:
            config (Optional[RenderConfig], optional): A configuration object.
                                                       If None, default settings are used.
                                                       Defaults to None.
        """
        self.config = config or RenderConfig()
        self._cached_surfaces: Dict[Tuple, pygame.Surface] = {}
        self.wind_time = 0.0
    
    def update(self, dt: float):
        """
        Updates the renderer's state, such as the wind effect timer.

        Args:
            dt (float): The time delta since the last frame, in seconds.
        """
        if self.config.wind_effect:
            self.wind_time += dt * 0.5
    
    def render_tree(self, screen: pygame.Surface, tree: TreeData, 
                   screen_pos: Tuple[float, float], offset: Tuple[float, float] = (0, 0)):
        """
        Renders a single tree to the screen.

        Args:
            screen (pygame.Surface): The screen surface to draw on.
            tree (TreeData): The tree data object to render.
            screen_pos (Tuple[float, float]): The base screen position for the tree.
            offset (Tuple[float, float], optional): The camera offset. Defaults to (0, 0).
        """
        x, y = screen_pos
        x += offset[0]
        y += offset[1]
        
        # Apply wind effect if enabled
        wind_offset = 0
        if self.config.wind_effect:
            wind_offset = math.sin(self.wind_time + tree.x * 0.1) * self.config.wind_strength
        
        # Render based on tree type
        if tree.tree_type == TreeType.OAK:
            self._render_oak_tree(screen, x + wind_offset, y, tree)
        elif tree.tree_type == TreeType.PINE:
            self._render_pine_tree(screen, x + wind_offset, y, tree)
        elif tree.tree_type == TreeType.MAPLE:
            self._render_maple_tree(screen, x + wind_offset, y, tree)
        else:
            # Fallback to oak
            self._render_oak_tree(screen, x + wind_offset, y, tree)
    
    def _render_oak_tree(self, screen: pygame.Surface, x: float, y: float, tree: TreeData):
        """
        Renders an oak tree.

        Args:
            screen (pygame.Surface): The screen surface.
            x (float): The x-coordinate for rendering.
            y (float): The y-coordinate for rendering.
            tree (TreeData): The tree's data.
        """
        # Calculate dimensions
        trunk_width = int(10 * tree.size_modifier)
        trunk_height = int(20 * tree.size_modifier)
        trunk_rect = pygame.Rect(x + 16 - trunk_width//2, y + 12, trunk_width, trunk_height)
        
        # Draw trunk with depth
        self._draw_trunk(screen, trunk_rect, tree)
        
        # Draw branches
        self._draw_oak_branches(screen, x, y, tree)
        
        # Draw foliage
        self._draw_oak_foliage(screen, x, y, tree)
    
    def _render_pine_tree(self, screen: pygame.Surface, x: float, y: float, tree: TreeData):
        """
        Renders a pine tree.

        Args:
            screen (pygame.Surface): The screen surface.
            x (float): The x-coordinate for rendering.
            y (float): The y-coordinate for rendering.
            tree (TreeData): The tree's data.
        """
        # Calculate dimensions
        trunk_width = int(6 * tree.size_modifier)
        trunk_height = int(24 * tree.size_modifier)
        trunk_rect = pygame.Rect(x + 16 - trunk_width//2, y + 8, trunk_width, trunk_height)
        
        # Draw trunk
        self._draw_trunk(screen, trunk_rect, tree)
        
        # Draw pine needles (layered triangles)
        self._draw_pine_needles(screen, x, y, tree)
    
    def _render_maple_tree(self, screen: pygame.Surface, x: float, y: float, tree: TreeData):
        """
        Renders a maple tree.

        Args:
            screen (pygame.Surface): The screen surface.
            x (float): The x-coordinate for rendering.
            y (float): The y-coordinate for rendering.
            tree (TreeData): The tree's data.
        """
        # Calculate dimensions
        trunk_width = int(8 * tree.size_modifier)
        trunk_height = int(18 * tree.size_modifier)
        trunk_rect = pygame.Rect(x + 16 - trunk_width//2, y + 14, trunk_width, trunk_height)
        
        # Draw trunk
        self._draw_trunk(screen, trunk_rect, tree)
        
        # Draw maple leaves (circular clusters)
        self._draw_maple_leaves(screen, x, y, tree)
    
    def _draw_trunk(self, screen: pygame.Surface, trunk_rect: pygame.Rect, tree: TreeData):
        """
        Draws the trunk of a tree, including base color, shadow, and highlight.

        Args:
            screen (pygame.Surface): The screen surface.
            trunk_rect (pygame.Rect): The rectangle defining the trunk's position and size.
            tree (TreeData): The tree's data, containing color information.
        """
        # Trunk shadow (left side)
        shadow_rect = pygame.Rect(trunk_rect.left, trunk_rect.top, trunk_rect.width//3, trunk_rect.height)
        pygame.draw.rect(screen, tree.trunk_shadow_color, shadow_rect)
        
        # Main trunk
        pygame.draw.rect(screen, tree.trunk_base_color, trunk_rect)
        
        # Trunk highlight (right side)
        highlight_rect = pygame.Rect(trunk_rect.right - trunk_rect.width//3, trunk_rect.top, 
                                   trunk_rect.width//3, trunk_rect.height)
        pygame.draw.rect(screen, tree.trunk_highlight_color, highlight_rect)
        
        # Add trunk texture lines
        for i in range(3):
            line_y = trunk_rect.top + 5 + i * 5
            pygame.draw.line(screen, tree.trunk_shadow_color, 
                           (trunk_rect.left + 2, line_y), (trunk_rect.right - 2, line_y), 1)
    
    def _draw_oak_branches(self, screen: pygame.Surface, x: float, y: float, tree: TreeData):
        """
        Draws the branches for an oak tree.

        Args:
            screen (pygame.Surface): The screen surface.
            x (float): The base x-coordinate of the tree.
            y (float): The base y-coordinate of the tree.
            tree (TreeData): The tree's data.
        """
        branch_color = (tree.trunk_base_color[0] + 10, tree.trunk_base_color[1] + 10, tree.trunk_base_color[2] + 10)
        
        # Left branch
        pygame.draw.line(screen, branch_color, (x + 16, y + 15), (x + 8, y + 8), 4)
        pygame.draw.line(screen, branch_color, (x + 8, y + 8), (x + 2, y + 5), 3)
        
        # Right branch
        pygame.draw.line(screen, branch_color, (x + 16, y + 15), (x + 24, y + 8), 4)
        pygame.draw.line(screen, branch_color, (x + 24, y + 8), (x + 30, y + 5), 3)
        
        # Top branch
        pygame.draw.line(screen, branch_color, (x + 16, y + 12), (x + 16, y + 2), 3)
    
    def _draw_oak_foliage(self, screen: pygame.Surface, x: float, y: float, tree: TreeData):
        """
        Draws the foliage for an oak tree as layered circular clusters.

        Args:
            screen (pygame.Surface): The screen surface.
            x (float): The base x-coordinate of the tree.
            y (float): The base y-coordinate of the tree.
            tree (TreeData): The tree's data.
        """
        foliage_centers = [
            (x + 16, y + 2),   # Top
            (x + 8, y + 5),    # Left
            (x + 24, y + 5),   # Right
            (x + 16, y + 8),   # Center
        ]
        
        for i, center in enumerate(foliage_centers):
            # Vary size based on layer
            size = int(12 * tree.size_modifier * (1.0 - i * 0.1))
            if size < 4:
                size = 4
            
            # Draw foliage circle
            pygame.draw.circle(screen, tree.leaf_color, (int(center[0]), int(center[1])), size)
            
            # Add highlight
            highlight_color = self._lighten_color(tree.leaf_color, 0.3)
            highlight_size = max(2, size // 3)
            pygame.draw.circle(screen, highlight_color, 
                             (int(center[0] - 2), int(center[1] - 2)), highlight_size)
    
    def _draw_pine_needles(self, screen: pygame.Surface, x: float, y: float, tree: TreeData):
        """Draw pine tree needles (layered triangles)."""
        base_size = int(8 * tree.size_modifier)
        
        # Draw layered triangles
        for i in range(4):
            layer_size = base_size - i * 2
            if layer_size < 3:
                break
            
            layer_y = y + 2 + i * 4
            points = [
                (x + 16, layer_y),
                (x + 16 - layer_size, layer_y + layer_size),
                (x + 16 + layer_size, layer_y + layer_size)
            ]
            
            pygame.draw.polygon(screen, tree.leaf_color, points)
            
            # Add highlight
            highlight_color = self._lighten_color(tree.leaf_color, 0.2)
            highlight_points = [
                (x + 16, layer_y + 1),
                (x + 16 - layer_size//2, layer_y + layer_size//2),
                (x + 16 + layer_size//2, layer_y + layer_size//2)
            ]
            pygame.draw.polygon(screen, highlight_color, highlight_points)
    
    def _draw_maple_leaves(self, screen: pygame.Surface, x: float, y: float, tree: TreeData):
        """Draw maple tree leaves (circular clusters)."""
        leaf_centers = [
            (x + 16, y + 2),   # Top
            (x + 10, y + 6),   # Left
            (x + 22, y + 6),   # Right
            (x + 16, y + 10),  # Center
        ]
        
        for center in leaf_centers:
            # Draw leaf cluster
            size = int(6 * tree.size_modifier)
            pygame.draw.circle(screen, tree.leaf_color, (int(center[0]), int(center[1])), size)
            
            # Add smaller highlight
            highlight_color = self._lighten_color(tree.leaf_color, 0.4)
            highlight_size = max(2, size // 2)
            pygame.draw.circle(screen, highlight_color, 
                             (int(center[0] - 1), int(center[1] - 1)), highlight_size)
    
    def _lighten_color(self, color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Lighten a color by the given factor."""
        return (
            min(255, int(color[0] + (255 - color[0]) * factor)),
            min(255, int(color[1] + (255 - color[1]) * factor)),
            min(255, int(color[2] + (255 - color[2]) * factor))
        )
    
    def render_tree_shadow(self, screen: pygame.Surface, tree: TreeData, 
                          screen_pos: Tuple[float, float], light_pos: Tuple[float, float]):
        """Render tree shadow based on light position."""
        if not self.config.shadow_enabled:
            return
        
        x, y = screen_pos
        light_x, light_y = light_pos
        
        # Calculate shadow direction
        dx = x - light_x
        dy = y - light_y
        length = max(0.001, math.sqrt(dx*dx + dy*dy))
        dx = dx / length * self.config.shadow_length
        dy = dy / length * self.config.shadow_length
        
        # Create shadow surface
        shadow_surface = pygame.Surface((self.config.tile_size, self.config.tile_size), pygame.SRCALPHA)
        
        # Draw shadow for trunk
        trunk_width = int(10 * tree.size_modifier)
        trunk_height = int(20 * tree.size_modifier)
        shadow_rect = pygame.Rect(
            int(16 - trunk_width//2 + dx/2),
            int(12 + dy/2),
            trunk_width,
            trunk_height
        )
        pygame.draw.rect(shadow_surface, (0, 0, 0, self.config.shadow_alpha), shadow_rect)
        
        # Draw shadow for foliage
        foliage_size = int(12 * tree.size_modifier)
        shadow_center = (int(16 + dx/2), int(2 + dy/2))
        pygame.draw.circle(shadow_surface, (0, 0, 0, self.config.shadow_alpha), 
                          shadow_center, foliage_size)
        
        # Blit shadow to screen
        screen.blit(shadow_surface, (x, y))
