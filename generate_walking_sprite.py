from PIL import Image
import os

# Create directories if they don't exist
os.makedirs("assets/sprites/characters/player/png", exist_ok=True)

# Base sprite size
width, height = 32, 32

# Ensure base sprites exist
if not os.path.exists("assets/sprites/characters/player/png/base_wanderer.png"):
    print("Base wanderer sprite not found. Run generate_base_sprite.py first.")
    exit(1)

# Load the base character
base_character = Image.open("assets/sprites/characters/player/png/base_wanderer.png")

# Color palette based on documentation
colors = {
    "skin_base": (224, 176, 136, 255),  # #E0B088
    "skin_shadow": (198, 156, 123, 255),  # #C69C7B
    "hair_base": (74, 74, 74, 255),  # #4A4A4A
    "hair_shadow": (51, 51, 51, 255),  # #333333
    "shirt_base": (139, 69, 19, 255),  # #8B4513
    "shirt_shadow": (101, 67, 33, 255),  # #654321
    "pants_base": (105, 105, 105, 255),  # #696969
    "pants_shadow": (74, 74, 74, 255),  # #4A4A4A
    "boots_base": (139, 69, 19, 255),  # #8B4513
    "boots_shadow": (101, 67, 33, 255),  # #654321
}

# Create walking animation (4 frames)
walk_sheet = Image.new("RGBA", (width * 4, height), (0, 0, 0, 0))
frames = []

# Frame 1: Left foot forward, right foot back
frame1 = base_character.copy()
# Clear leg area
for x in range(12, 20):
    for y in range(20, 32):
        frame1.putpixel((x, y), (0, 0, 0, 0))

# Left leg forward
for x in range(12, 16):
    for y in range(20, 26):
        frame1.putpixel((x, y), colors["pants_base"])
    for y in range(26, 30):
        frame1.putpixel((x, y), colors["boots_base"])

# Right leg back
for x in range(16, 20):
    for y in range(22, 28):
        frame1.putpixel((x, y), colors["pants_base"])
    for y in range(28, 32):
        frame1.putpixel((x, y), colors["boots_base"])

frames.append(frame1)

# Frame 2: Neutral stance (use base character with slight modification)
frame2 = base_character.copy()
# Slight head bob (1px up)
head_area = frame2.crop((12, 4, 20, 12))
frame2.paste((0, 0, 0, 0), (12, 4, 20, 12))
frame2.paste(head_area, (12, 3), head_area)
frames.append(frame2)

# Frame 3: Right foot forward, left foot back
frame3 = base_character.copy()
# Clear leg area
for x in range(12, 20):
    for y in range(20, 32):
        frame3.putpixel((x, y), (0, 0, 0, 0))

# Left leg back
for x in range(12, 16):
    for y in range(22, 28):
        frame3.putpixel((x, y), colors["pants_base"])
    for y in range(28, 32):
        frame3.putpixel((x, y), colors["boots_base"])

# Right leg forward
for x in range(16, 20):
    for y in range(20, 26):
        frame3.putpixel((x, y), colors["pants_base"])
    for y in range(26, 30):
        frame3.putpixel((x, y), colors["boots_base"])

frames.append(frame3)

# Frame 4: Similar to frame 2 but head bob down
frame4 = base_character.copy()
# Slight head bob (1px down)
head_area = frame4.crop((12, 4, 20, 12))
frame4.paste((0, 0, 0, 0), (12, 4, 20, 12))
frame4.paste(head_area, (12, 5), head_area)
frames.append(frame4)

# Combine frames into sprite sheet
for i, frame in enumerate(frames):
    walk_sheet.paste(frame, (i * width, 0))

# Save the sprite sheet
walk_sheet.save("assets/sprites/characters/player/png/base_wanderer_walk.png")

print("Walking animation sprite sheet generated successfully!") 