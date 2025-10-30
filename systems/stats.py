class Stats:
    """
    Manages a character's statistics, including attributes, combat stats, and experience.

    This class holds all numerical data for a character, such as health,
    strength, level, and provides methods for modifying these stats (e.g.,
    leveling up, taking damage).
    """
    def __init__(self):
        """
        Initializes the Stats with default values for a new character.
        """
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
        """
        Handles the logic for leveling up a character.

        Increments the level, increases the experience required for the next level,
        boosts base stats, restores HP/MP, and updates derived stats.
        """
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
        """
        Recalculates combat and other stats that are derived from base attributes.
        """
        self.attack = self.strength * 2
        self.defense = self.vitality * 1.5
        self.magic_attack = self.intelligence * 2
        self.magic_defense = self.intelligence * 1.5
        self.speed = 120 + (self.agility * 3)
        
    def add_exp(self, amount: int):
        """
        Adds experience points and triggers level-ups if necessary.

        Args:
            amount (int): The amount of experience to add.
        """
        self.exp += amount
        while self.exp >= self.exp_to_next_level:
            self.exp -= self.exp_to_next_level
            self.level_up()
            
    def take_damage(self, amount: int) -> bool:
        """
        Reduces HP by a specified amount.

        Args:
            amount (int): The amount of damage to take.

        Returns:
            bool: True if the character's HP has dropped to 0 or below,
                  False otherwise.
        """
        self.hp = max(0, self.hp - amount)
        return self.hp <= 0
        
    def heal(self, amount: int):
        """
        Restores HP by a specified amount, capped at max_hp.

        Args:
            amount (int): The amount of HP to restore.
        """
        self.hp = min(self.max_hp, self.hp + amount)
        
    def use_mp(self, amount: int) -> bool:
        """
        Reduces MP by a specified amount if available.

        Args:
            amount (int): The amount of MP to use.

        Returns:
            bool: True if MP was sufficient and used, False otherwise.
        """
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False
        
    def restore_mp(self, amount: int):
        """
        Restores MP by a specified amount, capped at max_mp.

        Args:
            amount (int): The amount of MP to restore.
        """
        self.mp = min(self.max_mp, self.mp + amount) 