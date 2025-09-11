#!/usr/bin/env python3
"""
Location Generator for Runic Lands
Generates procedural locations, dungeons, and areas
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import math

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class LocationGenerator:
    """Advanced location generator with GUI"""
    
    def __init__(self, parent=None):
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("Runic Lands Location Generator")
        self.window.geometry("800x600")
        self.window.minsize(600, 400)
        
        # Location data
        self.current_location = {}
        self.location_templates = self.load_location_templates()
        
        # Create GUI
        self.create_widgets()
        
        if not parent:
            self.window.mainloop()
    
    def load_location_templates(self) -> Dict:
        """Load location generation templates"""
        return {
            "forest": {
                "name_prefixes": ["Dark", "Mystic", "Ancient", "Whispering", "Shadow"],
                "name_suffixes": ["Woods", "Forest", "Grove", "Thicket", "Wilds"],
                "features": ["trees", "streams", "clearings", "ruins", "caves"],
                "enemies": ["wolves", "bears", "spiders", "bandits", "spirits"],
                "treasures": ["herbs", "gems", "ancient artifacts", "gold coins"],
                "atmosphere": ["mysterious", "peaceful", "dangerous", "magical", "haunted"]
            },
            "dungeon": {
                "name_prefixes": ["Forgotten", "Ancient", "Cursed", "Lost", "Dark"],
                "name_suffixes": ["Crypt", "Catacombs", "Tomb", "Vault", "Chamber"],
                "features": ["corridors", "rooms", "traps", "puzzles", "altars"],
                "enemies": ["skeletons", "zombies", "ghosts", "goblins", "dragons"],
                "treasures": ["gold", "gems", "magic items", "scrolls", "artifacts"],
                "atmosphere": ["dark", "cold", "eerie", "dangerous", "mysterious"]
            },
            "village": {
                "name_prefixes": ["Green", "Bright", "Peaceful", "Merry", "Golden"],
                "name_suffixes": ["Village", "Town", "Hamlet", "Settlement", "Haven"],
                "features": ["houses", "shops", "tavern", "temple", "market"],
                "enemies": ["bandits", "wild animals", "monsters", "undead"],
                "treasures": ["supplies", "information", "quests", "trade goods"],
                "atmosphere": ["friendly", "busy", "safe", "welcoming", "prosperous"]
            },
            "castle": {
                "name_prefixes": ["Royal", "Ancient", "Mystic", "Grand", "Noble"],
                "name_suffixes": ["Castle", "Fortress", "Keep", "Palace", "Citadel"],
                "features": ["towers", "halls", "dungeons", "gardens", "throne room"],
                "enemies": ["guards", "knights", "dragons", "demons", "undead"],
                "treasures": ["royal artifacts", "magic weapons", "gold", "gems", "scrolls"],
                "atmosphere": ["majestic", "imposing", "mysterious", "dangerous", "grand"]
            }
        }
    
    def create_widgets(self):
        """Create the GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Runic Lands Location Generator", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Left panel - Controls
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.create_control_panel(left_frame)
        
        # Right panel - Preview
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_preview_panel(right_frame)
    
    def create_control_panel(self, parent):
        """Create the control panel"""
        # Location type selection
        type_frame = ttk.LabelFrame(parent, text="Location Type", padding="10")
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.location_type = tk.StringVar(value="forest")
        for loc_type in self.location_templates.keys():
            ttk.Radiobutton(type_frame, text=loc_type.title(), 
                           variable=self.location_type, value=loc_type,
                           command=self.on_type_change).pack(anchor=tk.W)
        
        # Generation options
        options_frame = ttk.LabelFrame(parent, text="Generation Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Name
        ttk.Label(options_frame, text="Location Name:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(options_frame, width=30)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Size
        ttk.Label(options_frame, text="Size:").pack(anchor=tk.W)
        self.size_var = tk.StringVar(value="medium")
        size_combo = ttk.Combobox(options_frame, textvariable=self.size_var, 
                                 values=["tiny", "small", "medium", "large", "huge"])
        size_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Difficulty
        ttk.Label(options_frame, text="Difficulty:").pack(anchor=tk.W)
        self.difficulty_var = tk.StringVar(value="normal")
        diff_combo = ttk.Combobox(options_frame, textvariable=self.difficulty_var,
                                 values=["easy", "normal", "hard", "extreme"])
        diff_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Custom features
        custom_frame = ttk.LabelFrame(parent, text="Custom Features", padding="10")
        custom_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.custom_features = []
        for i in range(3):
            feature_entry = ttk.Entry(custom_frame, width=25)
            feature_entry.pack(fill=tk.X, pady=2)
            self.custom_features.append(feature_entry)
        
        # Generation buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Generate Random", 
                  command=self.generate_random).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Generate Custom", 
                  command=self.generate_custom).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # Export buttons
        export_frame = ttk.Frame(parent)
        export_frame.pack(fill=tk.X)
        
        ttk.Button(export_frame, text="Save as JSON", 
                  command=self.save_location).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Export to Game", 
                  command=self.export_to_game).pack(side=tk.LEFT, padx=5)
    
    def create_preview_panel(self, parent):
        """Create the preview panel"""
        # Location details
        details_frame = ttk.LabelFrame(parent, text="Location Details", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        self.details_text = scrolledtext.ScrolledText(details_frame, height=15, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Map preview (placeholder)
        map_frame = ttk.LabelFrame(parent, text="Map Preview", padding="10")
        map_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.map_canvas = tk.Canvas(map_frame, height=150, bg="lightgray")
        self.map_canvas.pack(fill=tk.X)
        
        # Map controls
        map_controls = ttk.Frame(map_frame)
        map_controls.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(map_controls, text="Generate Map", 
                  command=self.generate_map).pack(side=tk.LEFT)
        ttk.Button(map_controls, text="Clear Map", 
                  command=self.clear_map).pack(side=tk.LEFT, padx=(10, 0))
    
    def on_type_change(self):
        """Handle location type change"""
        # Update name suggestions based on type
        template = self.location_templates[self.location_type.get()]
        if not self.name_entry.get():
            prefix = random.choice(template["name_prefixes"])
            suffix = random.choice(template["name_suffixes"])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, f"{prefix} {suffix}")
    
    def generate_random(self):
        """Generate a random location"""
        template = self.location_templates[self.location_type.get()]
        
        # Generate name
        if not self.name_entry.get():
            prefix = random.choice(template["name_prefixes"])
            suffix = random.choice(template["name_suffixes"])
            name = f"{prefix} {suffix}"
        else:
            name = self.name_entry.get()
        
        # Generate features
        num_features = random.randint(3, 6)
        features = random.sample(template["features"], min(num_features, len(template["features"])))
        
        # Add custom features
        custom = [entry.get().strip() for entry in self.custom_features if entry.get().strip()]
        features.extend(custom)
        
        # Generate enemies
        num_enemies = random.randint(2, 4)
        enemies = random.sample(template["enemies"], min(num_enemies, len(template["enemies"])))
        
        # Generate treasures
        num_treasures = random.randint(1, 3)
        treasures = random.sample(template["treasures"], min(num_treasures, len(template["treasures"])))
        
        # Generate atmosphere
        atmosphere = random.choice(template["atmosphere"])
        
        # Create location data
        self.current_location = {
            "name": name,
            "type": self.location_type.get(),
            "size": self.size_var.get(),
            "difficulty": self.difficulty_var.get(),
            "features": features,
            "enemies": enemies,
            "treasures": treasures,
            "atmosphere": atmosphere,
            "description": self.generate_description(name, features, atmosphere)
        }
        
        self.update_preview()
    
    def generate_custom(self):
        """Generate custom location"""
        name = self.name_entry.get() or "Unnamed Location"
        
        features = []
        for entry in self.custom_features:
            if entry.get().strip():
                features.append(entry.get().strip())
        
        self.current_location = {
            "name": name,
            "type": self.location_type.get(),
            "size": self.size_var.get(),
            "difficulty": self.difficulty_var.get(),
            "features": features,
            "enemies": [],
            "treasures": [],
            "atmosphere": "custom",
            "description": f"A custom {self.location_type.get()} called {name}."
        }
        
        self.update_preview()
    
    def generate_description(self, name: str, features: List[str], atmosphere: str) -> str:
        """Generate location description"""
        feature_text = ", ".join(features[:-1]) + f" and {features[-1]}" if len(features) > 1 else features[0]
        
        descriptions = [
            f"{name} is a {atmosphere} place filled with {feature_text}.",
            f"The {atmosphere} {name} contains {feature_text} throughout its area.",
            f"Adventurers will find {feature_text} in this {atmosphere} {name}.",
            f"{name} is known for its {feature_text} and {atmosphere} atmosphere."
        ]
        
        return random.choice(descriptions)
    
    def update_preview(self):
        """Update the preview panel"""
        if not self.current_location:
            return
        
        self.details_text.delete(1.0, tk.END)
        
        # Format location details
        details = f"""LOCATION: {self.current_location['name']}
Type: {self.current_location['type'].title()}
Size: {self.current_location['size'].title()}
Difficulty: {self.current_location['difficulty'].title()}
Atmosphere: {self.current_location['atmosphere'].title()}

DESCRIPTION:
{self.current_location['description']}

FEATURES:
"""
        for feature in self.current_location['features']:
            details += f"• {feature}\n"
        
        if self.current_location['enemies']:
            details += "\nENEMIES:\n"
            for enemy in self.current_location['enemies']:
                details += f"• {enemy}\n"
        
        if self.current_location['treasures']:
            details += "\nTREASURES:\n"
            for treasure in self.current_location['treasures']:
                details += f"• {treasure}\n"
        
        self.details_text.insert(1.0, details)
    
    def generate_map(self):
        """Generate a simple map visualization"""
        if not self.current_location:
            return
        
        self.map_canvas.delete("all")
        
        # Get canvas dimensions
        width = self.map_canvas.winfo_width()
        height = self.map_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Draw based on location type
        loc_type = self.current_location['type']
        
        if loc_type == "forest":
            self.draw_forest_map(width, height)
        elif loc_type == "dungeon":
            self.draw_dungeon_map(width, height)
        elif loc_type == "village":
            self.draw_village_map(width, height)
        elif loc_type == "castle":
            self.draw_castle_map(width, height)
    
    def draw_forest_map(self, width: int, height: int):
        """Draw forest map"""
        # Draw trees
        for _ in range(20):
            x = random.randint(10, width - 10)
            y = random.randint(10, height - 10)
            size = random.randint(5, 15)
            self.map_canvas.create_oval(x-size, y-size, x+size, y+size, 
                                       fill="green", outline="darkgreen")
        
        # Draw paths
        for _ in range(3):
            start_x = random.randint(0, width)
            start_y = random.randint(0, height)
            end_x = random.randint(0, width)
            end_y = random.randint(0, height)
            self.map_canvas.create_line(start_x, start_y, end_x, end_y, 
                                       fill="brown", width=2)
    
    def draw_dungeon_map(self, width: int, height: int):
        """Draw dungeon map"""
        # Draw rooms
        room_size = 30
        for i in range(3):
            for j in range(2):
                x = 20 + i * (room_size + 20)
                y = 20 + j * (room_size + 20)
                self.map_canvas.create_rectangle(x, y, x + room_size, y + room_size,
                                                fill="gray", outline="black")
        
        # Draw corridors
        for i in range(2):
            x = 50 + i * (room_size + 20)
            self.map_canvas.create_rectangle(x, 35, x + 20, 45, fill="gray", outline="black")
    
    def draw_village_map(self, width: int, height: int):
        """Draw village map"""
        # Draw houses
        house_size = 20
        for i in range(4):
            for j in range(3):
                x = 20 + i * (house_size + 10)
                y = 20 + j * (house_size + 10)
                self.map_canvas.create_rectangle(x, y, x + house_size, y + house_size,
                                                fill="brown", outline="black")
        
        # Draw central square
        center_x, center_y = width // 2, height // 2
        self.map_canvas.create_oval(center_x - 15, center_y - 15, 
                                   center_x + 15, center_y + 15,
                                   fill="lightgreen", outline="darkgreen")
    
    def draw_castle_map(self, width: int, height: int):
        """Draw castle map"""
        # Draw main keep
        keep_size = 40
        center_x, center_y = width // 2, height // 2
        self.map_canvas.create_rectangle(center_x - keep_size//2, center_y - keep_size//2,
                                        center_x + keep_size//2, center_y + keep_size//2,
                                        fill="gray", outline="black")
        
        # Draw towers
        tower_size = 15
        positions = [(20, 20), (width-35, 20), (20, height-35), (width-35, height-35)]
        for x, y in positions:
            self.map_canvas.create_rectangle(x, y, x + tower_size, y + tower_size,
                                            fill="darkgray", outline="black")
    
    def clear_map(self):
        """Clear the map"""
        self.map_canvas.delete("all")
    
    def clear_form(self):
        """Clear the form"""
        self.name_entry.delete(0, tk.END)
        for entry in self.custom_features:
            entry.delete(0, tk.END)
        self.current_location = {}
        self.details_text.delete(1.0, tk.END)
        self.clear_map()
    
    def save_location(self):
        """Save location to JSON file"""
        if not self.current_location:
            messagebox.showwarning("Warning", "No location to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.current_location, f, indent=2)
                messagebox.showinfo("Success", f"Location saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save location: {e}")
    
    def export_to_game(self):
        """Export location to game format"""
        if not self.current_location:
            messagebox.showwarning("Warning", "No location to export")
            return
        
        # Create game-compatible location file
        game_location = {
            "id": self.current_location['name'].lower().replace(' ', '_'),
            "name": self.current_location['name'],
            "type": self.current_location['type'],
            "size": self.current_location['size'],
            "difficulty": self.current_location['difficulty'],
            "description": self.current_location['description'],
            "features": self.current_location['features'],
            "enemies": self.current_location['enemies'],
            "treasures": self.current_location['treasures'],
            "atmosphere": self.current_location['atmosphere']
        }
        
        # Save to game locations directory
        locations_dir = Path("../../assets/locations")
        locations_dir.mkdir(parents=True, exist_ok=True)
        
        filename = locations_dir / f"{game_location['id']}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(game_location, f, indent=2)
            messagebox.showinfo("Success", f"Location exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export location: {e}")

def main():
    """Main entry point"""
    app = LocationGenerator()

if __name__ == "__main__":
    main()
