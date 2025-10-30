"""This module defines the base Character class for the game."""

from dataclasses import dataclass
from typing import Dict, List
import pygame
from systems.stats import Stats
    
class Character:
    """Represents a character in the game."""
    def __init__(self, x: int, y: int, color: tuple):
        """Initializes a new Character.

        Args:
            x (int): The initial x-coordinate of the character.
            y (int): The initial y-coordinate of the character.
            color (tuple): The color of the character.
        """
        self.x = x
        self.y = y
        self.color = color
        self.stats = Stats()
        self.level = 1
        self.exp = 0
        self.job = "Wanderer"
        self.skills: List[str] = []
        
    def gain_exp(self, amount: int) -> bool:
        """Adds experience points to the character and checks for level up.

        Args:
            amount (int): The amount of experience to gain.

        Returns:
            bool: True if the character leveled up, False otherwise.
        """
        self.exp += amount
        if self.exp >= self.get_exp_for_next_level():
            self.level_up()
            return True
        return False
    
    def get_exp_for_next_level(self) -> int:
        """Calculates the experience needed for the next level.

        This uses a formula similar to Old School RuneScape's experience scaling.

        Returns:
            int: The total experience required for the next level.
        """
        return int(0.25 * (self.level + 300 * pow(2, self.level / 7)))
    
    def level_up(self):
        """Levels up the character, increasing stats and restoring HP/MP."""
        self.level += 1
        self.stats.max_hp += 5
        self.stats.max_mp += 3
        self.stats.hp = self.stats.max_hp  # Restore HP on level up
        self.stats.mp = self.stats.max_mp  # Restore MP on level up
        # Base stat increases
        self.stats.strength += 2
        self.stats.agility += 2
        self.stats.intelligence += 2
        self.stats.vitality += 2
        # Update derived stats
        self.stats.update_derived_stats()
        
    def can_advance_job(self) -> bool:
        """Checks if the character meets the requirements for a job advancement.

        Returns:
            bool: True if the character can advance, False otherwise.
        """
        if self.job == "Wanderer" and self.level >= 15:
            return True
        return False
    
    def advance_job(self, new_job: str) -> bool:
        """Advances the character to a new job.

        Args:
            new_job (str): The new job to advance to.

        Returns:
            bool: True if the job advancement was successful, False otherwise.
        """
        if not self.can_advance_job():
            return False
            
        valid_jobs = {
            "Wanderer": ["Mercenary", "Assist", "Acrobat", "Magician"],
        }
        
        if self.job in valid_jobs and new_job in valid_jobs[self.job]:
            self.job = new_job
            self._apply_job_bonuses()
            return True
        return False
    
    def _apply_job_bonuses(self):
        """Applies stat bonuses based on the character's new job."""
        bonuses = {
            "Mercenary": {"strength": 5, "vitality": 3},
            "Assist": {"intelligence": 5, "vitality": 3},
            "Acrobat": {"agility": 5, "strength": 3},
            "Magician": {"intelligence": 5, "mp": 20}
        }
        
        if self.job in bonuses:
            for stat, value in bonuses[self.job].items():
                if stat == "mp":
                    # Handle MP bonus specially
                    self.stats.max_mp += value
                    self.stats.mp = self.stats.max_mp
                else:
                    setattr(self.stats, stat, getattr(self.stats, stat) + value)
            # Update derived stats after applying bonuses
            self.stats.update_derived_stats() 