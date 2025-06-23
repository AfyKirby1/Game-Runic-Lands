# 🎭 Class & Leveling System Design

## Class Progression

### Base Class
```python
class Vagrant:
    level_requirement: int = 1
    base_stats = {
        "hp": 100,
        "mp": 50,
        "strength": 15,
        "stamina": 15,
        "dexterity": 15,
        "intelligence": 15
    }
    skills = [
        "basic_attack",
        "self_healing",
        "sprint"
    ]
```

### First Job Classes (Level 15)
1. **Mercenary**
   - Focus: Melee Combat
   - Weapons: Swords, Axes
   - Key Stats: STR, STA
   - Special: Highest HP, Tank role

2. **Assist**
   - Focus: Support/Healing
   - Weapons: Knuckles, Sticks
   - Key Stats: INT, STA
   - Special: Healing & Buff abilities

3. **Acrobat**
   - Focus: Ranged Combat
   - Weapons: Bow, Yoyo
   - Key Stats: DEX, STR
   - Special: Distance attacks, Mobility

4. **Magician**
   - Focus: Spell Damage
   - Weapons: Staff, Wand+Shield
   - Key Stats: INT
   - Special: Elemental magic

### Second Job Classes (Level 60)
```python
SECOND_JOB_PATHS = {
    "Mercenary": ["Knight", "Blade"],
    "Assist": ["Ringmaster", "Billposter"],
    "Acrobat": ["Ranger", "Jester"],
    "Magician": ["Elementor", "Psykeeper"]
}
```

### Third Job Classes (Level 130)
```python
THIRD_JOB_PATHS = {
    "Knight": "Templar",
    "Blade": "Slayer",
    "Ringmaster": "Seraph",
    "Billposter": "Force Master",
    "Ranger": "Crackshooter",
    "Jester": "Harlequin",
    "Elementor": "Arcanist",
    "Psykeeper": "Mentalist"
}
```

## Leveling System

### Level Progression
```python
class LevelSystem:
    current_level: int
    current_exp: int
    required_exp: int
    job_rank: str  # "Vagrant", "First", "Second", "Master", "Hero", "Third"
    
    def calculate_exp_requirement(self, level: int) -> int:
        base = 100
        multiplier = 1.2
        return int(base * (multiplier ** level))
    
    def handle_job_advancement(self, level: int) -> bool:
        job_thresholds = {
            15: "First",
            60: "Second",
            120: "Master",  # Requires Master Quest
            121: "Hero",    # Requires Hero Quest
            130: "Third"    # Requires Job Quest
        }
        return level in job_thresholds
```

### Experience System
- Base EXP from monsters scaled by level difference
- Party bonus: +20% per additional member
- Chain kill bonus: +5% per consecutive kill
- Rest bonus: +50% after offline period
- Quest EXP rewards
- Event bonuses

### Job Advancement Requirements
```python
class JobAdvancement:
    level_requirement: int
    quest_requirements: List[str]
    stat_requirements: Dict[str, int]
    skill_requirements: List[str]
    item_requirements: List[str]
    
    def check_eligibility(self, player: Player) -> bool:
        # Check all requirements
        pass
    
    def execute_advancement(self, player: Player) -> None:
        # Reset stats for reallocation
        # Grant new abilities
        # Update class
        pass
```

## Stat System

### Base Stats
- STR: Melee damage, Carry weight
- STA: HP, Defense
- DEX: Attack speed, Critical rate, Ranged damage
- INT: Magic damage, MP, Healing power

### Class-Specific Bonuses
```python
CLASS_STAT_BONUSES = {
    "Knight": {"STA": 1.5, "STR": 1.3},
    "Blade": {"DEX": 1.4, "STR": 1.4},
    "Ringmaster": {"INT": 1.6, "STA": 1.2},
    "Billposter": {"STR": 1.4, "STA": 1.3},
    "Ranger": {"DEX": 1.5, "STR": 1.2},
    "Jester": {"DEX": 1.6, "STR": 1.1},
    "Elementor": {"INT": 1.7},
    "Psykeeper": {"INT": 1.6, "STA": 1.1}
}
```

## Skill System

### Skill Points
- Gain 1 point per level
- First job skills: 1 point cost
- Second job skills: 2 points cost
- Third job skills: 3 points cost

### Skill Categories
1. Active Combat
2. Passive Buffs
3. Support/Utility
4. Ultimate Abilities (Third Job)

## Quest System

### Job Advancement Quests
```python
class JobQuest:
    quest_type: str  # "First", "Second", "Master", "Hero", "Third"
    requirements: List[str]
    tasks: List[Task]
    rewards: Dict[str, Any]
    
    def start_quest(self, player: Player) -> None:
        pass
    
    def check_progress(self, player: Player) -> float:
        pass
    
    def complete_quest(self, player: Player) -> None:
        pass
```

## Future Enhancements
- [ ] Class-specific mount abilities
- [ ] Hybrid class system
- [ ] Prestige system
- [ ] Class-specific crafting
- [ ] Guild class bonuses 