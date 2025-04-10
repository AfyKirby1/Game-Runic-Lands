from dataclasses import dataclass
from typing import Dict, List
import pygame

@dataclass
class Stats:
    hp: int = 100
    mp: int = 50
    strength: int = 10
    agility: int = 10
    intelligence: int = 10
    vitality: int = 10
    speed: int = 5
    
class Character:
    def __init__(self, x: int, y: int, color: tuple):
        self.x = x
        self.y = y
        self.color = color
        self.stats = Stats()
        self.level = 1
        self.exp = 0
        self.job = "Wanderer"
        self.skills: List[str] = []
        
    def gain_exp(self, amount: int) -> bool:
        """Returns True if leveled up"""
        self.exp += amount
        if self.exp >= self.get_exp_for_next_level():
            self.level_up()
            return True
        return False
    
    def get_exp_for_next_level(self) -> int:
        """OSRS-style exp scaling"""
        return int(0.25 * (self.level + 300 * pow(2, self.level / 7)))
    
    def level_up(self):
        self.level += 1
        self.stats.hp += 5
        self.stats.mp += 3
        # Base stat increases
        self.stats.strength += 2
        self.stats.agility += 2
        self.stats.intelligence += 2
        self.stats.vitality += 2
        
    def can_advance_job(self) -> bool:
        """Check if character meets requirements for job advancement"""
        if self.job == "Wanderer" and self.level >= 15:
            return True
        return False
    
    def advance_job(self, new_job: str) -> bool:
        """Attempt to advance to a new job"""
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
        """Apply stat bonuses based on job"""
        bonuses = {
            "Mercenary": {"strength": 5, "vitality": 3},
            "Assist": {"intelligence": 5, "vitality": 3},
            "Acrobat": {"agility": 5, "strength": 3},
            "Magician": {"intelligence": 5, "mp": 20}
        }
        
        if self.job in bonuses:
            for stat, value in bonuses[self.job].items():
                setattr(self.stats, stat, getattr(self.stats, stat) + value) 