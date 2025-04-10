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
    "metal": (192, 192, 192, 255),  # #C0C0C0
    "metal_shadow": (128, 128, 128, 255),  # #808080
}

# Create attack animation (4 frames)
attack_sheet = Image.new("RGBA", (width * 4, height), (0, 0, 0, 0))
frames = []

# Frame 1: Wind-up
frame1 = base_character.copy()
# Clear right arm area
for x in range(22, 24):
    for y in range(12, 28):
        frame1.putpixel((x, y), (0, 0, 0, 0))
# Raised arm (wind up)
for x in range(22, 24):
    for y in range(8, 20):
        frame1.putpixel((x, y), colors["shirt_base"])
for x in range(22, 24):
    for y in range(4, 8):
        frame1.putpixel((x, y), colors["skin_base"])

# Add a simple sword (raised)
for x in range(24, 26):
    for y in range(2, 7):
        frame1.putpixel((x, y), colors["metal"])

frames.append(frame1)

# Frame 2: Attack motion
frame2 = base_character.copy()
# Clear right arm area
for x in range(22, 24):
    for y in range(12, 28):
        frame2.putpixel((x, y), (0, 0, 0, 0))
# Extended arm (attack)
for x in range(22, 26):
    for y in range(12, 14):
        frame2.putpixel((x, y), colors["shirt_base"])
for x in range(26, 28):
    for y in range(12, 14):
        frame2.putpixel((x, y), colors["skin_base"])

# Add sword (extended)
for x in range(28, 32):
    for y in range(12, 14):
        frame2.putpixel((x, y), colors["metal"])

frames.append(frame2)

# Frame 3: Follow-through
frame3 = base_character.copy()
# Clear right arm area
for x in range(22, 24):
    for y in range(12, 28):
        frame3.putpixel((x, y), (0, 0, 0, 0))
# Follow through arm position
for x in range(22, 26):
    for y in range(16, 18):
        frame3.putpixel((x, y), colors["shirt_base"])
for x in range(26, 28):
    for y in range(16, 18):
        frame3.putpixel((x, y), colors["skin_base"])

# Add sword (follow through)
for x in range(28, 32):
    for y in range(18, 20):
        frame3.putpixel((x, y), colors["metal"])

frames.append(frame3)

# Frame 4: Recovery
frame4 = base_character.copy()
# Slightly modified arm position
for x in range(22, 24):
    for y in range(16, 24):
        frame4.putpixel((x, y), colors["shirt_base"])
for x in range(22, 24):
    for y in range(24, 28):
        frame4.putpixel((x, y), colors["skin_base"])

frames.append(frame4)

# Combine frames into sprite sheet
for i, frame in enumerate(frames):
    attack_sheet.paste(frame, (i * width, 0))

# Save the sprite sheet
attack_sheet.save("assets/sprites/characters/player/png/base_wanderer_attack.png")

print("Attack animation sprite sheet generated successfully!") 