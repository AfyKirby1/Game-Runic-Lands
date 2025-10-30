"""This module defines the CombatSystem, which handles combat interactions."""

import pygame
from math import floor

class CombatSystem:
    """Manages combat between entities."""
    def __init__(self):
        """Initializes the CombatSystem."""
        self.attack_cooldown = 0.5  # Attack cooldown in seconds
        self.last_attack_time = {}  # Track last attack time for each player
        self.attack_range = 50  # Attack range in pixels
        self.damage = 10  # Base damage
        
    def update(self, dt, players):
        """Updates the combat state, primarily managing attack cooldowns.

        Args:
            dt (float): The time delta since the last update.
            players (list): A list of player objects in the game.
        """
        # Update attack cooldowns
        for player in players:
            if player in self.last_attack_time:
                self.last_attack_time[player] -= dt
                if self.last_attack_time[player] <= 0:
                    del self.last_attack_time[player]
    
    def handle_attack(self, attacker, target):
        """Handles an attack from one entity to another.

        Args:
            attacker: The entity initiating the attack.
            target: The entity being attacked.

        Returns:
            bool: True if the attack was successful, False otherwise.
        """
        # Check if attacker is on cooldown
        if attacker in self.last_attack_time:
            return False
            
        # Calculate distance between players
        dx = target.pos[0] - attacker.pos[0]
        dy = target.pos[1] - attacker.pos[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Check if target is in range
        if distance <= self.attack_range:
            # Apply damage
            target.stats.hp -= self.damage
            # Set attack cooldown
            self.last_attack_time[attacker] = self.attack_cooldown
            return True
            
        return False

    def calculate_damage(self, attacker):
        """Calculates the damage an attacker will deal.

        Args:
            attacker: The entity dealing the damage.

        Returns:
            int: The calculated damage amount.
        """
        base_damage = 10
        
        # Job-specific damage calculations
        job_multipliers = {
            "Wanderer": 1.0,
            "Mercenary": 1.5,
            "Assist": 0.8,
            "Acrobat": 1.2,
            "Magician": 1.3
        }
        
        # Get job multiplier, default to 1.0 if job not found
        job_mult = job_multipliers.get(attacker.job, 1.0)
        
        # Calculate stat-based damage
        if attacker.job in ["Mercenary", "Acrobat"]:
            stat_mult = attacker.stats.strength * 0.1
        elif attacker.job in ["Magician", "Assist"]:
            stat_mult = attacker.stats.intelligence * 0.1
        else:
            # Wanderer uses average of strength and intelligence
            stat_mult = (attacker.stats.strength + attacker.stats.intelligence) * 0.05
            
        return floor(base_damage * job_mult * (1 + stat_mult)) 