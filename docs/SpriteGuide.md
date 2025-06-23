# Runic Lands Sprite Guide

## Sprite Dimensions & Requirements

### Core Specifications
- **Base Sprite Size**: 32x32 pixels
- **File Format**: PNG with alpha transparency
- **Color Depth**: 24-bit color with 8-bit alpha channel
- **Style**: Pixel art with clear silhouettes
- **Animation Frames**: Typically 4 frames per animation
- **Animation Sheets**: 128x32 pixels (4 frames horizontally)

### Character Sprite Sheet Layout
Complete character sheets should use a 12x4 grid of 32x32 pixel frames (384x128 pixels total):

```
[Direction]  [Idle] [Walk1][Walk2][Walk3][Walk4] [Atk1][Atk2][Atk3][Atk4] [Hurt1][Hurt2]
Down         0,0    0,1    0,2    0,3    0,4     0,5   0,6   0,7   0,8    0,9    0,10
Left         1,0    1,1    1,2    1,3    1,4     1,5   1,6   1,7   1,8    1,9    1,10
Right        2,0    2,1    2,2    2,3    2,4     2,5   2,6   2,7   2,8    2,9    2,10
Up           3,0    3,1    3,2    3,3    3,4     3,5   3,6   3,7   3,8    3,9    3,10
```

## Animation States

### Required Animations
1. **Idle Animation**
   - Single frame or 4-frame breathing sequence
   - Subtle body movement
   - Gentle clothing sway

2. **Walking Animation**
   - 4-frame cycle
   - Alternating arm/leg movement
   - Slight head bob (1 pixel up/down)

3. **Attack Animation**
   - 4-frame sequence:
     - Wind-up
     - Attack motion
     - Follow-through
     - Recovery

4. **Hurt Animation**
   - 2-frame sequence:
     - Impact reaction 
     - Recoil

## Character Layer System

Runic Lands uses a layered approach for characters to allow equipment overlays:

### Base Layers
1. **Body Layer** (base_body.png)
   - Basic humanoid form
   - Dimensions: 32x32 pixels
   - Head: 8x8 pixels
   - Torso: 12x16 pixels
   - Arms/Legs: 4x12 pixels each

2. **Clothing Layer** (base_clothing.png)
   - Basic outfit (shirt, pants, boots)
   - Should leave room for equipment overlays

3. **Complete Character** (e.g., base_wanderer.png)
   - Combined body and clothing

### Equipment Overlay Slots
1. **Head Slot**: (8,4) to (16,12) from top-left
2. **Body Slot**: (6,12) to (18,28)
3. **Hands Slot**: 
   - Left: (4,16) to (8,28)
   - Right: (16,16) to (20,28)
4. **Feet Slot**: (8,28) to (16,32)
5. **Weapon Slot**: Varies by animation frame

## Sprite Organization

### Directory Structure
- Player Characters: `assets/sprites/characters/player/`
- NPCs: `assets/sprites/characters/npcs/`
- Animals: `assets/sprites/characters/animals/`
- Items/Objects: `assets/sprites/items/`
- Environment: `assets/sprites/environment/`

### File Naming Conventions
- Base Components: `base_[component].png`
- Complete Characters: `[character_name].png`
- Animation Sheets: `[character_name]_[animation].png`
  - Example: `base_wanderer_walk.png`

## Color Palette

### Base Character Colors
```
- Skin: #E0B088 (base), #C69C7B (shadow)
- Hair: #4A4A4A (base), #333333 (shadow)
- Shirt: #8B4513 (base), #654321 (shadow)
- Pants: #696969 (base), #4A4A4A (shadow)
- Boots: #8B4513 (base), #654321 (shadow)
```

### Equipment Colors
```
- Metal: #C0C0C0 (base), #808080 (shadow)
- Leather: #8B4513 (base), #654321 (shadow)
- Cloth: #DEB887 (base), #D2B48C (shadow)
```

## Game Resolution Support

Runic Lands supports multiple resolutions, but sprites are designed with pixel-perfect rendering at the base resolution.

### Supported Resolutions
- 800x600 (default)
- 1024x768
- 1280x720 (720p)
- 1366x768 (Common laptop)
- 1600x900
- 1920x1080 (1080p)
- 2560x1440 (1440p)

### GUI Scale Factor
- Adjustable from 0.5x to 2.5x
- Default: 1.0x
- Sprites will be scaled according to resolution and GUI scale

## Best Practices for Creating Sprites

1. **Maintain Consistent Dimensions**
   - Keep all sprites in multiples of 32x32 pixels
   - Center characters within their frames
   - Use consistent proportions across related sprites

2. **Animation Guidelines**
   - Limit animation frames to 4-6 frames per action
   - Exaggerate key poses for better readability
   - Keep movement fluid with proper in-betweens

3. **Visibility and Clarity**
   - Use clear silhouettes for better readability
   - Maintain sufficient contrast between elements
   - Consider how sprites will look at different resolutions

4. **Technical Considerations**
   - Use transparent backgrounds
   - Minimize unnecessary transparent pixels
   - Test animations in-game for smooth movement
   - Consider adding special frames for character-specific actions

5. **Layering and Equipment**
   - Design equipment with all animations in mind
   - Keep equipment within the designated overlay areas
   - Test equipment overlays on different character bases
   - Maintain consistent light source (top-left)

---

*For more detailed information, refer to the full documentation in `docs/SPRITES.md` and `docs/CHARACTER_SPRITES.md`.* 