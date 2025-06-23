# Sprite System Documentation

## Spritesheet Structure
Each character spritesheet should be organized in a 12x4 grid of 32x32 pixel frames:

```
[Direction]  [Idle] [Walk1][Walk2][Walk3][Walk4] [Atk1][Atk2][Atk3][Atk4] [Hurt1][Hurt2]
Down         0,0    0,1    0,2    0,3    0,4     0,5   0,6   0,7   0,8    0,9    0,10
Left         1,0    1,1    1,2    1,3    1,4     1,5   1,6   1,7   1,8    1,9    1,10
Right        2,0    2,1    2,2    2,3    2,4     2,5   2,6   2,7   2,8    2,9    2,10
Up          3,0    3,1    3,2    3,3    3,4     3,5   3,6   3,7   3,8    3,9    3,10
```

## Animation States
1. **Idle** (1 frame)
   - Static pose for each direction
   - Located in column 0

2. **Walking** (4 frames)
   - Basic movement animation
   - Located in columns 1-4

3. **Attacking** (4 frames)
   - Combat animation sequence
   - Located in columns 5-8

4. **Hurt** (2 frames)
   - Damage reaction animation
   - Located in columns 9-10

## Character Types

### 1. Player Characters
- Location: `assets/sprites/characters/player/`
- Required animations: All
- Example files:
  - `warrior.png`
  - `mage.png`

### 2. NPCs
- Location: `assets/sprites/characters/npcs/`
- Required animations: Idle, Walking
- Optional animations: Others
- Categories:
  - Humans (villagers, merchants, etc.)
  - Non-humans (elves, dwarves, etc.)

### 3. Animals
- Location: `assets/sprites/characters/animals/`
- Required animations: Idle, Walking
- Optional animations: Attacking
- Examples:
  - Wild animals (wolves, bears)
  - Domestic animals (cats, dogs)

## Usage Example
```python
from systems.sprite import CharacterSprite, Direction, AnimationState

# Create a character sprite
player_sprite = CharacterSprite("assets/sprites/characters/player/warrior.png")

# Update animation state
player_sprite.set_state(AnimationState.WALKING)
player_sprite.set_direction(Direction.RIGHT)

# Update animation (in game loop)
player_sprite.update(dt)  # dt is time since last frame

# Get current frame to draw
current_frame = player_sprite.get_current_frame()
```

## Creating New Sprites
1. Create a new 384x128 pixel image (12 columns x 4 rows of 32x32 frames)
2. Follow the spritesheet structure above
3. Save in the appropriate directory based on character type
4. Use transparency for empty space
5. Maintain consistent character size and positioning within each frame

## Tips
- Keep character sprites centered in their frames
- Use clear silhouettes for readability
- Maintain consistent style across related characters
- Test animations in-game for smooth movement
- Consider adding special frames for character-specific actions 