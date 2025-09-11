#!/usr/bin/env python3
"""
Example: Using the Modern World System

This example shows how to use the new modern world system
that fixes the flashing tree issue.
"""

import pygame
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from systems.world_modern import ModernWorld, WorldConfig
from systems.world_generation_modern import TreeType


def main():
    """Example usage of the modern world system."""
    # Initialize pygame
    pygame.init()
    
    # Create screen
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Modern World System Example")
    clock = pygame.time.Clock()
    
    # Create world with custom config
    config = WorldConfig(
        world_width=32,  # Smaller for demo
        world_height=32,
        view_distance=3,
        wind_strength=1.0
    )
    
    world = ModernWorld(config=config, seed=12345)
    
    # Camera offset
    camera_x, camera_y = 0, 0
    
    # Main loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Handle camera movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            camera_x -= 200 * dt
        if keys[pygame.K_RIGHT]:
            camera_x += 200 * dt
        if keys[pygame.K_UP]:
            camera_y -= 200 * dt
        if keys[pygame.K_DOWN]:
            camera_y += 200 * dt
        
        # Update world
        world.update(dt)
        world.update_chunks(int(camera_x), int(camera_y))
        
        # Draw world
        screen.fill((135, 206, 235))  # Sky blue background
        world.draw(screen, (camera_x, camera_y))
        
        # Draw UI
        font = pygame.font.Font(None, 24)
        time_text = f"Time: {world.get_world_time()[0]:02d}:{world.get_world_time()[1]:02d}"
        screen.blit(font.render(time_text, True, (255, 255, 255)), (10, 10))
        
        screen.blit(font.render("Arrow keys to move camera", True, (255, 255, 255)), (10, 40))
        screen.blit(font.render("ESC to exit", True, (255, 255, 255)), (10, 70))
        
        pygame.display.flip()
    
    # Cleanup
    world.cleanup()
    pygame.quit()


if __name__ == "__main__":
    main()
