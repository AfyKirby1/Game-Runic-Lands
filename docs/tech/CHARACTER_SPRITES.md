# Base Character Sprite Design

## Wanderer Base Design
The base character uses a layered approach to allow for equipment overlays:

### Layer 1: Body (base_body.png)
- Simple humanoid form
- Neutral skin tone options
- Basic body proportions: 32x32 pixels
- Head: 8x8 pixels
- Torso: 12x16 pixels
- Arms/Legs: 4x12 pixels each

### Layer 2: Basic Clothing (base_clothing.png)
- Simple tunic/shirt
- Basic pants/leggings
- Leather boots
- Color scheme:
  - Primary: Earth tones (browns, tans)
  - Secondary: Muted colors (greys, dark blues)
  - Accent: Small pops of color in details

### Layer 3: Equipment Slots
1. Head slot
   - Location: (8,4) to (16,12) from top-left
   - For: Helmets, hats, hoods

2. Body slot
   - Location: (6,12) to (18,28)
   - For: Armor, robes, cloaks

3. Hands slot
   - Location: Left: (4,16) to (8,28)
   - Location: Right: (16,16) to (20,28)
   - For: Gloves, bracers

4. Feet slot
   - Location: (8,28) to (16,32)
   - For: Boots, shoes

5. Weapon slot
   - Location: Varies by animation frame
   - For: Weapons, shields, tools

## Animation Guidelines

### Idle Animation
- Subtle breathing motion
- Slight shoulder movement
- Gentle clothing sway

### Walking Animation
- 4-frame cycle
- Alternating arm/leg movement
- Clothing responds to movement
- Head bob: 1 pixel up/down

### Attack Animation
- 4-frame sequence
- Frame 1: Wind-up
- Frame 2: Attack motion
- Frame 3: Follow-through
- Frame 4: Recovery

### Hurt Animation
- 2-frame sequence
- Frame 1: Impact reaction
- Frame 2: Recoil

## Color Palette
```
Base Colors:
- Skin: #E0B088 (base), #C69C7B (shadow)
- Hair: #4A4A4A (base), #333333 (shadow)
- Shirt: #8B4513 (base), #654321 (shadow)
- Pants: #696969 (base), #4A4A4A (shadow)
- Boots: #8B4513 (base), #654321 (shadow)

Equipment Overlay Colors:
- Metal: #C0C0C0 (base), #808080 (shadow)
- Leather: #8B4513 (base), #654321 (shadow)
- Cloth: #DEB887 (base), #D2B48C (shadow)
```

## Sprite Sheet Layout
See [SPRITES.md](SPRITES.md) for the complete sprite sheet layout.

## Equipment Overlay Example
```
Base Character + Equipment:
[Base Layer   ] - Character body and features
[Clothing     ] - Basic wanderer outfit
[Armor        ] - Equipment overlay
[Weapon/Shield] - Equipment overlay
```

## Implementation Notes
1. Each equipment piece should be designed as a separate overlay
2. Use transparency for easy equipment swapping
3. Keep silhouettes clear and readable
4. Maintain consistent light source (top-left)
5. Design equipment with all animations in mind 