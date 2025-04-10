from PIL import Image
import os

# Create directories if they don't exist
os.makedirs("assets/sprites/characters/player/png", exist_ok=True)

# Base sprite size
width, height = 32, 32

# Create images for different layers
base_body = Image.new("RGBA", (width, height), (0, 0, 0, 0))
base_clothing = Image.new("RGBA", (width, height), (0, 0, 0, 0))
combined = Image.new("RGBA", (width, height), (0, 0, 0, 0))

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

# Create pixel art based on the ASCII reference
# Head
for x in range(12, 20):
    for y in range(4, 6):
        base_clothing.putpixel((x, y), colors["hair_base"])
    for y in range(6, 8):
        base_clothing.putpixel((x, y), colors["hair_shadow"])

# Face
for x in range(12, 20):
    for y in range(8, 12):
        base_body.putpixel((x, y), colors["skin_base"])

# Torso
for x in range(10, 22):
    for y in range(12, 16):
        base_clothing.putpixel((x, y), colors["shirt_base"])
    for y in range(16, 20):
        base_clothing.putpixel((x, y), colors["shirt_shadow"])

# Arms
for x in range(8, 10):  # Left arm
    for y in range(12, 24):
        base_clothing.putpixel((x, y), colors["shirt_base"])
        
for x in range(22, 24):  # Right arm
    for y in range(12, 24):
        base_clothing.putpixel((x, y), colors["shirt_base"])

# Hands
for x in range(8, 10):  # Left hand
    for y in range(24, 28):
        base_body.putpixel((x, y), colors["skin_base"])
        
for x in range(22, 24):  # Right hand
    for y in range(24, 28):
        base_body.putpixel((x, y), colors["skin_base"])

# Legs
for x in range(12, 16):  # Left leg
    for y in range(20, 28):
        base_clothing.putpixel((x, y), colors["pants_base"])
        
for x in range(16, 20):  # Right leg
    for y in range(20, 28):
        base_clothing.putpixel((x, y), colors["pants_base"])

# Feet
for x in range(12, 16):  # Left foot
    for y in range(28, 32):
        base_clothing.putpixel((x, y), colors["boots_base"])
        
for x in range(16, 20):  # Right foot
    for y in range(28, 32):
        base_clothing.putpixel((x, y), colors["boots_base"])

# Combine layers
combined = Image.alpha_composite(combined, base_body)
combined = Image.alpha_composite(combined, base_clothing)

# Save the images
base_body.save("assets/sprites/characters/player/png/base_body.png")
base_clothing.save("assets/sprites/characters/player/png/base_clothing.png")
combined.save("assets/sprites/characters/player/png/base_wanderer.png")

# Create the sprite sheet with idle animation frames (4 frames)
sprite_sheet = Image.new("RGBA", (width * 4, height), (0, 0, 0, 0))

# Create 4 slightly different frames for idle animation
frames = []
frames.append(combined)  # Frame 1: Original

# Frame 2: Subtle breathing (shoulders slightly up)
frame2 = combined.copy()
for x in range(10, 22):
    for y in range(12, 16):
        if y > 12 and frame2.getpixel((x, y))[3] > 0:
            pixel = frame2.getpixel((x, y-1))
            frame2.putpixel((x, y-1), pixel)
frames.append(frame2)

# Frame 3: Same as frame 1
frames.append(combined.copy())

# Frame 4: Subtle breathing (shoulders slightly down)
frame4 = combined.copy()
for x in range(10, 22):
    for y in range(15, 19):
        if y < 18 and frame4.getpixel((x, y))[3] > 0:
            pixel = frame4.getpixel((x, y+1))
            frame4.putpixel((x, y+1), pixel)
frames.append(frame4)

# Combine frames into sprite sheet
for i, frame in enumerate(frames):
    sprite_sheet.paste(frame, (i * width, 0))

# Save the sprite sheet
sprite_sheet.save("assets/sprites/characters/player/png/base_wanderer_idle.png")

print("Base character sprites generated successfully!") 