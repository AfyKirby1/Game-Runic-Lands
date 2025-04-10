class Stats:
    def __init__(self):
        # Base stats
        self.hp = 100
        self.max_hp = 100
        self.mp = 50
        self.max_mp = 50
        self.strength = 10
        self.agility = 10
        self.intelligence = 10
        self.vitality = 10
        
        # Combat stats
        self.attack = 10
        self.defense = 5
        self.magic_attack = 10
        self.magic_defense = 5
        self.critical_rate = 0.05
        self.critical_damage = 1.5
        
        # Movement stats
        self.speed = 120
        self.jump_power = 300
        
        # Experience
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100
        
    def level_up(self):
        """Handle level up logic"""
        self.level += 1
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        
        # Increase base stats
        self.max_hp += 20
        self.max_mp += 10
        self.strength += 2
        self.agility += 2
        self.intelligence += 2
        self.vitality += 2
        
        # Restore HP/MP
        self.hp = self.max_hp
        self.mp = self.max_mp
        
        # Update derived stats
        self.update_derived_stats()
        
    def update_derived_stats(self):
        """Update stats that are derived from base stats"""
        self.attack = self.strength * 2
        self.defense = self.vitality * 1.5
        self.magic_attack = self.intelligence * 2
        self.magic_defense = self.intelligence * 1.5
        self.speed = 120 + (self.agility * 3)
        
    def add_exp(self, amount):
        """Add experience points and handle level ups"""
        self.exp += amount
        while self.exp >= self.exp_to_next_level:
            self.exp -= self.exp_to_next_level
            self.level_up()
            
    def take_damage(self, amount):
        """Handle taking damage"""
        self.hp = max(0, self.hp - amount)
        return self.hp <= 0
        
    def heal(self, amount):
        """Heal HP"""
        self.hp = min(self.max_hp, self.hp + amount)
        
    def use_mp(self, amount):
        """Use MP if available"""
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False
        
    def restore_mp(self, amount):
        """Restore MP"""
        self.mp = min(self.max_mp, self.mp + amount) 