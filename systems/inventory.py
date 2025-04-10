"""
Inventory System Module

This module implements the inventory and equipment system for the game.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import pygame


class ItemType(Enum):
    WEAPON = auto()
    ARMOR = auto()
    HELMET = auto()
    BOOTS = auto()
    GLOVES = auto()
    CONSUMABLE = auto()
    MATERIAL = auto()
    QUEST = auto()


class EquipmentSlot(Enum):
    HEAD = auto()
    NECKLACE = auto()
    TORSO = auto()
    PANTS = auto()
    BOOTS = auto()
    GLOVES = auto()
    RING = auto()
    OFFHAND = auto()
    WEAPON = auto()


class Item:
    def __init__(self, name: str, item_type: ItemType, description: str = "", 
                 icon_path: str = None, stats: Dict = None):
        self.name = name
        self.item_type = item_type
        self.description = description
        self.stats = stats or {}
        
        # Try to load icon, use fallback if necessary
        self.icon = None
        self.icon_path = icon_path
        if icon_path:
            try:
                self.icon = pygame.image.load(icon_path).convert_alpha()
            except (pygame.error, FileNotFoundError):
                # Fallback: create a colored rectangle
                color = self._get_color_for_item_type()
                self.icon = pygame.Surface((32, 32))
                self.icon.fill(color)
                font = pygame.font.Font(None, 18)
                initial = name[0] if name else "?"
                text = font.render(initial, True, (255, 255, 255))
                text_rect = text.get_rect(center=(16, 16))
                self.icon.blit(text, text_rect)
        else:
            # Create a colored rectangle by default
            color = self._get_color_for_item_type()
            self.icon = pygame.Surface((32, 32))
            self.icon.fill(color)
            font = pygame.font.Font(None, 18)
            initial = name[0] if name else "?"
            text = font.render(initial, True, (255, 255, 255))
            text_rect = text.get_rect(center=(16, 16))
            self.icon.blit(text, text_rect)
    
    def _get_color_for_item_type(self) -> Tuple[int, int, int]:
        """Get color based on item type"""
        colors = {
            ItemType.WEAPON: (200, 50, 50),    # Red
            ItemType.ARMOR: (50, 50, 200),     # Blue
            ItemType.HELMET: (50, 200, 50),    # Green
            ItemType.BOOTS: (200, 200, 50),    # Yellow
            ItemType.GLOVES: (200, 50, 200),   # Purple
            ItemType.CONSUMABLE: (50, 200, 200), # Cyan
            ItemType.MATERIAL: (150, 150, 150), # Gray
            ItemType.QUEST: (255, 215, 0)      # Gold
        }
        return colors.get(self.item_type, (100, 100, 100))
    
    def can_equip(self) -> bool:
        """Check if this item can be equipped"""
        return self.item_type in [ItemType.WEAPON, ItemType.ARMOR, ItemType.HELMET, 
                                ItemType.BOOTS, ItemType.GLOVES]
    
    def get_equipment_slot(self) -> Optional[EquipmentSlot]:
        """Get the equipment slot this item goes in"""
        slot_map = {
            ItemType.WEAPON: EquipmentSlot.WEAPON,
            ItemType.ARMOR: EquipmentSlot.TORSO,
            ItemType.HELMET: EquipmentSlot.HEAD,
            ItemType.BOOTS: EquipmentSlot.BOOTS,
            ItemType.GLOVES: EquipmentSlot.GLOVES
        }
        return slot_map.get(self.item_type)
    
    def to_dict(self) -> Dict:
        """Convert item to serializable dictionary"""
        return {
            "name": self.name,
            "item_type": self.item_type.name,  # Store enum as string
            "description": self.description,
            "icon_path": self.icon_path,
            "stats": self.stats
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Create an item from dictionary data"""
        # Convert string to enum
        item_type = ItemType[data["item_type"]] if "item_type" in data else ItemType.MATERIAL
        
        return cls(
            name=data.get("name", "Unknown Item"),
            item_type=item_type,
            description=data.get("description", ""),
            icon_path=data.get("icon_path"),
            stats=data.get("stats", {})
        )


class Equipment:
    def __init__(self):
        self.slots: Dict[EquipmentSlot, Optional[Item]] = {
            slot: None for slot in EquipmentSlot
        }
    
    def equip(self, item: Item) -> Tuple[bool, Optional[Item]]:
        """
        Equip an item to its slot
        Returns: (success, previous_item)
        """
        if not item.can_equip():
            return False, None
            
        slot = item.get_equipment_slot()
        if not slot:
            return False, None
            
        # Store the previous item to return to inventory if needed
        previous_item = self.slots[slot]
        self.slots[slot] = item
        return True, previous_item
    
    def unequip(self, slot: EquipmentSlot) -> Optional[Item]:
        """Unequip and return an item from a slot"""
        item = self.slots[slot]
        self.slots[slot] = None
        return item
    
    def get_stats_boost(self) -> Dict:
        """Calculate total stats boost from equipment"""
        total_stats = {}
        
        for item in self.slots.values():
            if item and item.stats:
                for stat, value in item.stats.items():
                    total_stats[stat] = total_stats.get(stat, 0) + value
                    
        return total_stats
    
    def is_slot_filled(self, slot: EquipmentSlot) -> bool:
        """Check if a slot has an item equipped"""
        return self.slots[slot] is not None
    
    def get_item_in_slot(self, slot: EquipmentSlot) -> Optional[Item]:
        """Get the item in a specific slot"""
        return self.slots[slot]
    
    def to_dict(self) -> Dict:
        """Convert equipment to serializable dictionary"""
        result = {}
        for slot, item in self.slots.items():
            if item:
                result[slot.name] = item.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Equipment':
        """Create equipment from dictionary data"""
        equipment = cls()
        
        for slot_name, item_data in data.items():
            try:
                slot = EquipmentSlot[slot_name]
                item = Item.from_dict(item_data)
                equipment.slots[slot] = item
            except (KeyError, ValueError) as e:
                print(f"Error loading equipment slot {slot_name}: {e}")
        
        return equipment


class Inventory:
    def __init__(self, size: int = 16):
        self.size = size
        self.items: List[Optional[Item]] = [None] * size
        self.equipment = Equipment()
        
    def add_item(self, item: Item) -> bool:
        """Add an item to the first empty slot, return success"""
        for i in range(self.size):
            if self.items[i] is None:
                self.items[i] = item
                return True
        return False
    
    def remove_item(self, index: int) -> Optional[Item]:
        """Remove and return an item at the specified index"""
        if 0 <= index < self.size and self.items[index]:
            item = self.items[index]
            self.items[index] = None
            return item
        return None
    
    def swap_items(self, index1: int, index2: int) -> bool:
        """Swap two items in the inventory"""
        if (0 <= index1 < self.size and 0 <= index2 < self.size):
            self.items[index1], self.items[index2] = self.items[index2], self.items[index1]
            return True
        return False
    
    def equip_item(self, index: int) -> bool:
        """Try to equip an item from inventory"""
        if 0 <= index < self.size and self.items[index]:
            item = self.items[index]
            if item.can_equip():
                success, previous_item = self.equipment.equip(item)
                if success:
                    self.items[index] = previous_item  # Replace with prev item or None
                    return True
        return False
    
    def unequip_item(self, slot: EquipmentSlot) -> bool:
        """Unequip an item and put it in inventory if there's space"""
        item = self.equipment.get_item_in_slot(slot)
        if not item:
            return False
            
        if self.add_item(item):
            self.equipment.unequip(slot)
            return True
        return False
    
    def get_item(self, index: int) -> Optional[Item]:
        """Get an item reference without removing it"""
        if 0 <= index < self.size:
            return self.items[index]
        return None
    
    def is_full(self) -> bool:
        """Check if inventory is full"""
        return all(item is not None for item in self.items)
    
    def count_items(self) -> int:
        """Count non-empty slots"""
        return sum(1 for item in self.items if item is not None)
    
    def to_dict(self) -> Dict:
        """Convert inventory to serializable dictionary"""
        items_data = []
        for item in self.items:
            if item:
                items_data.append(item.to_dict())
            else:
                items_data.append(None)
                
        return {
            "size": self.size,
            "items": items_data,
            "equipment": self.equipment.to_dict()
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load inventory from dictionary data"""
        # Reset inventory
        self.size = data.get("size", 16)
        self.items = [None] * self.size
        
        # Load items
        items_data = data.get("items", [])
        for i, item_data in enumerate(items_data):
            if i >= self.size:
                break
                
            if item_data:
                try:
                    self.items[i] = Item.from_dict(item_data)
                except Exception as e:
                    print(f"Error loading item at slot {i}: {e}")
        
        # Load equipment
        equipment_data = data.get("equipment", {})
        if equipment_data:
            self.equipment = Equipment.from_dict(equipment_data)


class InventoryUI:
    def __init__(self, inventory: Inventory, screen_size: Tuple[int, int]):
        self.inventory = inventory
        self.screen_size = screen_size
        self.visible = False
        
        # UI dimensions and positions
        self.cell_size = 40
        self.padding = 10
        self.border = 2
        
        # Inventory grid (4x4)
        self.grid_cols = 4
        self.grid_rows = 4
        self.grid_width = self.grid_cols * self.cell_size + (self.grid_cols + 1) * self.padding
        self.grid_height = self.grid_rows * self.cell_size + (self.grid_rows + 1) * self.padding
        
        # Equipment section - make it wider for the character silhouette
        self.equipment_width = 3 * self.cell_size + 6 * self.padding
        self.equipment_height = 6 * self.cell_size + 8 * self.padding
        
        # Overall panel dimensions
        self.panel_width = self.grid_width + self.equipment_width + 3 * self.padding
        self.panel_height = max(self.grid_height, self.equipment_height) + 2 * self.padding
        
        # Position of panel
        self.panel_x = (screen_size[0] - self.panel_width) // 2
        self.panel_y = (screen_size[1] - self.panel_height) // 2
        
        # Grid position
        self.grid_x = self.panel_x + self.padding
        self.grid_y = self.panel_y + self.padding
        
        # Equipment section position
        self.equipment_x = self.grid_x + self.grid_width + self.padding
        self.equipment_y = self.panel_y + self.padding
        
        # Character silhouette dimensions
        self.char_width = 2 * self.cell_size
        self.char_height = 4 * self.cell_size
        self.char_x = self.equipment_x + (self.equipment_width - self.char_width) // 2
        self.char_y = self.equipment_y + 2 * self.padding + self.cell_size
        self.head_radius = int(self.char_width * 0.25)
        
        # Equipment slot positions relative to character silhouette
        self.equipment_slots = {
            EquipmentSlot.HEAD: (self.char_x + self.char_width//2 - self.cell_size//2,  # Center above head
                                self.char_y - self.cell_size//2),
            EquipmentSlot.NECKLACE: (self.char_x + self.char_width//2 - self.cell_size//2,  # Center at neck
                                    self.char_y + self.head_radius * 2),
            EquipmentSlot.WEAPON: (self.char_x - self.cell_size - self.padding,  # Left of body
                                  self.char_y + self.char_height//3),
            EquipmentSlot.OFFHAND: (self.char_x + self.char_width + self.padding,  # Right of body
                                   self.char_y + self.char_height//3),
            EquipmentSlot.TORSO: (self.char_x + self.char_width//2 - self.cell_size//2,  # Center on chest
                                 self.char_y + self.char_height//3),
            EquipmentSlot.PANTS: (self.char_x + self.char_width//2 - self.cell_size//2,  # Center at waist
                                 self.char_y + self.char_height * 0.6),
            EquipmentSlot.GLOVES: (self.char_x - self.cell_size - self.padding,  # Left of body, lower
                                  self.char_y + self.char_height * 0.7),
            EquipmentSlot.RING: (self.char_x + self.char_width + self.padding,  # Right of body, lower
                                self.char_y + self.char_height * 0.7),
            EquipmentSlot.BOOTS: (self.char_x + self.char_width//2 - self.cell_size//2,  # Center at feet
                                 self.char_y + self.char_height - self.cell_size//2),
        }
        
        # Update slot labels
        self.slot_labels = {
            EquipmentSlot.HEAD: "Head",
            EquipmentSlot.NECKLACE: "Neck",
            EquipmentSlot.WEAPON: "Weapon",
            EquipmentSlot.OFFHAND: "Shield",
            EquipmentSlot.TORSO: "Torso",
            EquipmentSlot.PANTS: "Legs",
            EquipmentSlot.BOOTS: "Feet",
            EquipmentSlot.GLOVES: "Hands",
            EquipmentSlot.RING: "Ring",
        }
        
        # UI state
        self.selected_slot = None
        self.dragging_item = None
        self.dragging_from_slot = None
        self.mouse_pos = (0, 0)
        
        # Colors
        self.bg_color = (50, 50, 50, 230)
        self.slot_color = (60, 60, 60)
        self.slot_highlight_color = (100, 100, 100)
        self.border_color = (200, 200, 200)
        self.text_color = (255, 255, 255)
        self.char_color = (40, 40, 40)  # Dark gray for character silhouette
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 36)
        self.label_font = pygame.font.Font(None, 28)
        self.info_font = pygame.font.Font(None, 24)
        
        # Create dark overlay surface
        self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 128))
    
    def resize(self, new_screen_size: Tuple[int, int]):
        """Recalculate UI dimensions and positions based on new screen size."""
        self.screen_size = new_screen_size
        
        # Recalculate panel dimensions (grid and equipment widths/heights are fixed)
        self.panel_width = self.grid_width + self.equipment_width + 3 * self.padding
        self.panel_height = max(self.grid_height, self.equipment_height) + 2 * self.padding
        
        # Recalculate panel position
        self.panel_x = (self.screen_size[0] - self.panel_width) // 2
        self.panel_y = (self.screen_size[1] - self.panel_height) // 2
        
        # Recalculate grid position
        self.grid_x = self.panel_x + self.padding
        self.grid_y = self.panel_y + self.padding
        
        # Recalculate equipment section position
        self.equipment_x = self.grid_x + self.grid_width + self.padding
        self.equipment_y = self.panel_y + self.padding
        
        # Recalculate character silhouette position
        self.char_x = self.equipment_x + (self.equipment_width - self.char_width) // 2
        self.char_y = self.equipment_y + 2 * self.padding + self.cell_size
        
        # Recalculate equipment slot positions relative to character silhouette
        self.equipment_slots = {
            EquipmentSlot.HEAD: (self.char_x + self.char_width//2 - self.cell_size//2,
                                self.char_y - self.cell_size//2),
            EquipmentSlot.NECKLACE: (self.char_x + self.char_width//2 - self.cell_size//2,
                                    self.char_y + self.head_radius * 2),
            EquipmentSlot.WEAPON: (self.char_x - self.cell_size - self.padding,
                                  self.char_y + self.char_height//3),
            EquipmentSlot.OFFHAND: (self.char_x + self.char_width + self.padding,
                                   self.char_y + self.char_height//3),
            EquipmentSlot.TORSO: (self.char_x + self.char_width//2 - self.cell_size//2,
                                 self.char_y + self.char_height//3),
            EquipmentSlot.PANTS: (self.char_x + self.char_width//2 - self.cell_size//2,
                                 self.char_y + self.char_height * 0.6),
            EquipmentSlot.GLOVES: (self.char_x - self.cell_size - self.padding,
                                  self.char_y + self.char_height * 0.7),
            EquipmentSlot.RING: (self.char_x + self.char_width + self.padding,
                                self.char_y + self.char_height * 0.7),
            EquipmentSlot.BOOTS: (self.char_x + self.char_width//2 - self.cell_size//2,
                                 self.char_y + self.char_height - self.cell_size//2),
        }
        
        # Recreate dark overlay surface for the new size
        self.overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 128))
    
    def toggle_visibility(self):
        """Toggle inventory visibility"""
        self.visible = not self.visible
        self.selected_slot = None
        self.dragging_item = None
        self.dragging_from_slot = None
    
    def update(self, dt: float):
        """Update inventory UI state (e.g., animations, cooldowns). Placeholder for now."""
        # TODO: Add any time-dependent updates here
        pass # Nothing to update yet

    def handle_event(self, event):
        """Handle pygame events for the inventory UI"""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Only check for ESC to close
                self.toggle_visibility()
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicked on an inventory slot
                slot_index = self._get_inventory_slot_at_pos(event.pos)
                if slot_index is not None:
                    # If we're already dragging an item, drop it here
                    if self.dragging_item:
                        if self.dragging_from_slot == ("equipment", self.dragging_from_slot[1]):
                            # Moving from equipment to inventory
                            equipment_slot = self.dragging_from_slot[1]
                            item = self.inventory.equipment.unequip(equipment_slot)
                            
                            # Swap with any existing item
                            existing_item = self.inventory.get_item(slot_index)
                            if existing_item:
                                self.inventory.remove_item(slot_index)
                                if existing_item.can_equip() and existing_item.get_equipment_slot() == equipment_slot:
                                    self.inventory.equipment.equip(existing_item)
                            
                            # Add the dragged item to inventory
                            self.inventory.items[slot_index] = item
                        else:
                            # Just swap inventory slots
                            self.inventory.swap_items(self.dragging_from_slot[1], slot_index)
                        
                        self.dragging_item = None
                        self.dragging_from_slot = None
                    else:
                        # Start dragging
                        item = self.inventory.get_item(slot_index)
                        if item:
                            self.dragging_item = item
                            self.dragging_from_slot = ("inventory", slot_index)
                
                # Check if clicked on equipment slot
                eq_slot = self._get_equipment_slot_at_pos(event.pos)
                if eq_slot:
                    if self.dragging_item:
                        if self.dragging_from_slot[0] == "inventory":
                            # Moving from inventory to equipment
                            inv_idx = self.dragging_from_slot[1]
                            item = self.inventory.get_item(inv_idx)
                            
                            # Only equip if it's the right slot type
                            if item and item.get_equipment_slot() == eq_slot:
                                old_equipped = self.inventory.equipment.get_item_in_slot(eq_slot)
                                self.inventory.equipment.equip(item)
                                self.inventory.remove_item(inv_idx)
                                
                                # Put previously equipped item in inventory slot
                                if old_equipped:
                                    self.inventory.items[inv_idx] = old_equipped
                        else:
                            # Equipment slot to equipment slot - not allowed
                            pass
                        
                        self.dragging_item = None
                        self.dragging_from_slot = None
                    else:
                        # Start dragging from equipment
                        item = self.inventory.equipment.get_item_in_slot(eq_slot)
                        if item:
                            self.dragging_item = item
                            self.dragging_from_slot = ("equipment", eq_slot)
            
            # Capture this event
            return True
            
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                if self.dragging_item:
                    # If released outside of a slot, return item to original slot
                    self.dragging_item = None
                    self.dragging_from_slot = None
                return True
                
        # Event wasn't handled
        return False
    
    def _get_inventory_slot_at_pos(self, pos):
        """Get inventory slot index at a position, or None"""
        # Check if position is in the grid area
        if not (self.grid_x <= pos[0] <= self.grid_x + self.grid_width and
                self.grid_y <= pos[1] <= self.grid_y + self.grid_height):
            return None
        
        # Calculate relative position in grid
        rel_x = pos[0] - self.grid_x - self.padding
        rel_y = pos[1] - self.grid_y - self.padding
        
        # Calculate cell coordinates
        col = rel_x // (self.cell_size + self.padding)
        row = rel_y // (self.cell_size + self.padding)
        
        # Check if we're actually in a cell, not on a border
        if (col < 0 or col >= self.grid_cols or 
            row < 0 or row >= self.grid_rows or
            rel_x % (self.cell_size + self.padding) > self.cell_size or
            rel_y % (self.cell_size + self.padding) > self.cell_size):
            return None
        
        # Convert to index
        index = row * self.grid_cols + col
        if 0 <= index < self.inventory.size:
            return index
        return None
    
    def _get_equipment_slot_at_pos(self, pos):
        """Get equipment slot at a position, or None"""
        for slot, (slot_x, slot_y) in self.equipment_slots.items():
            # Check if click is within the equipment slot
            if (slot_x - self.cell_size//2 <= pos[0] <= slot_x + self.cell_size//2 and
                slot_y <= pos[1] <= slot_y + self.cell_size):
                return slot
        return None
    
    def draw(self, surface):
        """Draw the inventory UI"""
        if not self.visible:
            return
            
        # Draw dark overlay first
        surface.blit(self.overlay, (0, 0))
        
        # Create a transparent surface for the panel
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)
        
        # Draw panel border
        pygame.draw.rect(panel_surface, self.border_color, 
                         (0, 0, self.panel_width, self.panel_height), self.border)
        
        # Draw title
        title = self.title_font.render("Inventory", True, self.text_color)
        title_rect = title.get_rect(midtop=(self.panel_width//2, self.padding))
        panel_surface.blit(title, title_rect)
        
        # Draw equipment section title
        eq_title = self.label_font.render("Equipment", True, self.text_color)
        eq_title_rect = eq_title.get_rect(midtop=(
            self.equipment_x + self.equipment_width//2 - self.panel_x, 
            self.padding
        ))
        panel_surface.blit(eq_title, eq_title_rect)
        
        # Draw character silhouette
        char_rel_x = self.char_x - self.panel_x
        char_rel_y = self.char_y - self.panel_y
        
        # Enhanced proportions
        head_radius = int(self.char_width * 0.25)  # Slightly smaller head
        neck_width = int(head_radius * 0.6)
        neck_height = int(head_radius * 0.4)
        shoulder_width = int(self.char_width * 0.9)  # Wider shoulders
        chest_width = int(self.char_width * 0.75)
        waist_width = int(self.char_width * 0.6)
        hip_width = int(self.char_width * 0.7)
        leg_width = int(self.char_width * 0.25)
        
        # Head (circle with slight neck)
        head_center = (char_rel_x + self.char_width//2, char_rel_y + head_radius)
        pygame.draw.circle(panel_surface, self.char_color, head_center, head_radius)
        
        # Neck
        neck_top = char_rel_y + head_radius * 2 - neck_height//2
        pygame.draw.rect(panel_surface, self.char_color,
                        (char_rel_x + self.char_width//2 - neck_width//2,
                         neck_top,
                         neck_width, neck_height))
        
        # Shoulders and upper body (more detailed trapezoid)
        torso_height = int(self.char_height * 0.35)
        upper_torso_points = [
            (char_rel_x + (self.char_width - shoulder_width)//2, neck_top + neck_height),  # Left shoulder
            (char_rel_x + (self.char_width + shoulder_width)//2, neck_top + neck_height),  # Right shoulder
            (char_rel_x + (self.char_width + chest_width)//2, neck_top + neck_height + torso_height//2),  # Right chest
            (char_rel_x + (self.char_width + waist_width)//2, neck_top + neck_height + torso_height),  # Right waist
            (char_rel_x + (self.char_width - waist_width)//2, neck_top + neck_height + torso_height),  # Left waist
            (char_rel_x + (self.char_width - chest_width)//2, neck_top + neck_height + torso_height//2),  # Left chest
        ]
        pygame.draw.polygon(panel_surface, self.char_color, upper_torso_points)
        
        # Lower body (hips and upper legs connection)
        hip_top = neck_top + neck_height + torso_height
        hip_height = int(self.char_height * 0.15)
        lower_body_points = [
            (char_rel_x + (self.char_width - waist_width)//2, hip_top),  # Left waist
            (char_rel_x + (self.char_width + waist_width)//2, hip_top),  # Right waist
            (char_rel_x + (self.char_width + hip_width)//2, hip_top + hip_height),  # Right hip
            (char_rel_x + (self.char_width - hip_width)//2, hip_top + hip_height)   # Left hip
        ]
        pygame.draw.polygon(panel_surface, self.char_color, lower_body_points)
        
        # Legs with slight curve
        leg_height = int(self.char_height * 0.35)
        leg_top_y = hip_top + hip_height
        leg_spacing = self.char_width * 0.2
        
        # Left leg with slight curve
        left_leg_x = char_rel_x + (self.char_width - leg_spacing)//2 - leg_width//2
        left_leg_points = [
            (left_leg_x, leg_top_y),
            (left_leg_x + leg_width, leg_top_y),
            (left_leg_x + leg_width - 4, leg_top_y + leg_height),
            (left_leg_x - 4, leg_top_y + leg_height)
        ]
        pygame.draw.polygon(panel_surface, self.char_color, left_leg_points)
        
        # Right leg with slight curve
        right_leg_x = char_rel_x + (self.char_width + leg_spacing)//2 - leg_width//2
        right_leg_points = [
            (right_leg_x, leg_top_y),
            (right_leg_x + leg_width, leg_top_y),
            (right_leg_x + leg_width + 4, leg_top_y + leg_height),
            (right_leg_x + 4, leg_top_y + leg_height)
        ]
        pygame.draw.polygon(panel_surface, self.char_color, right_leg_points)
        
        # Add arm silhouettes
        arm_width = int(leg_width * 0.8)
        arm_length = int(torso_height * 0.8)
        arm_angle = 15  # Slight angle for arms
        
        # Left arm
        left_arm_top = (char_rel_x + (self.char_width - shoulder_width)//2, neck_top + neck_height)
        left_arm_points = [
            left_arm_top,
            (left_arm_top[0] + arm_width, left_arm_top[1]),
            (left_arm_top[0] + arm_width - arm_angle, left_arm_top[1] + arm_length),
            (left_arm_top[0] - arm_angle, left_arm_top[1] + arm_length)
        ]
        pygame.draw.polygon(panel_surface, self.char_color, left_arm_points)
        
        # Right arm
        right_arm_top = (char_rel_x + (self.char_width + shoulder_width)//2 - arm_width, neck_top + neck_height)
        right_arm_points = [
            right_arm_top,
            (right_arm_top[0] + arm_width, right_arm_top[1]),
            (right_arm_top[0] + arm_width + arm_angle, right_arm_top[1] + arm_length),
            (right_arm_top[0] + arm_angle, right_arm_top[1] + arm_length)
        ]
        pygame.draw.polygon(panel_surface, self.char_color, right_arm_points)
        
        # Draw inventory grid
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                idx = row * self.grid_cols + col
                x = self.padding + col * (self.cell_size + self.padding)
                y = self.padding * 3 + title_rect.height + row * (self.cell_size + self.padding)
                
                # Draw cell background
                pygame.draw.rect(panel_surface, self.slot_color, 
                                (x, y, self.cell_size, self.cell_size))
                
                # Draw highlight if selected
                if self.selected_slot == ("inventory", idx):
                    pygame.draw.rect(panel_surface, self.slot_highlight_color, 
                                    (x, y, self.cell_size, self.cell_size), 2)
                
                # Draw item icon if slot has an item and we're not dragging it
                item = self.inventory.get_item(idx)
                if item and (not self.dragging_item or self.dragging_from_slot != ("inventory", idx)):
                    # Scale icon to fit cell
                    scaled_icon = pygame.transform.scale(item.icon, (self.cell_size-4, self.cell_size-4))
                    panel_surface.blit(scaled_icon, (x+2, y+2))
        
        # Draw equipment slots
        for slot, (slot_x, slot_y) in self.equipment_slots.items():
            rel_x = slot_x - self.panel_x
            rel_y = slot_y - self.panel_y
            
            # Draw slot background
            pygame.draw.rect(panel_surface, self.slot_color, 
                            (rel_x, rel_y, self.cell_size, self.cell_size))
            
            # Draw highlight if selected
            if self.selected_slot == ("equipment", slot):
                pygame.draw.rect(panel_surface, self.slot_highlight_color, 
                                (rel_x, rel_y, self.cell_size, self.cell_size), 2)
            
            # Draw item icon if equipped and not being dragged
            item = self.inventory.equipment.get_item_in_slot(slot)
            if item and (not self.dragging_item or self.dragging_from_slot != ("equipment", slot)):
                # Scale icon to fit cell
                scaled_icon = pygame.transform.scale(item.icon, (self.cell_size-4, self.cell_size-4))
                panel_surface.blit(scaled_icon, (rel_x+2, rel_y+2))
        
        # Draw the panel
        surface.blit(panel_surface, (self.panel_x, self.panel_y))
        
        # Draw dragged item following mouse cursor
        if self.dragging_item:
            # Scale icon to fit cell
            scaled_icon = pygame.transform.scale(self.dragging_item.icon, (self.cell_size, self.cell_size))
            surface.blit(scaled_icon, (self.mouse_pos[0] - self.cell_size//2, 
                                      self.mouse_pos[1] - self.cell_size//2))


# Factory function to create some example items
def create_example_items():
    """Create some example items for testing"""
    return [
        Item("Iron Sword", ItemType.WEAPON, "A basic iron sword", stats={"strength": 5}),
        Item("Leather Armor", ItemType.ARMOR, "Basic leather protection", stats={"defense": 3}),
        Item("Steel Helmet", ItemType.HELMET, "Sturdy steel helmet", stats={"defense": 2}),
        Item("Leather Boots", ItemType.BOOTS, "Comfortable walking boots", stats={"agility": 1}),
        Item("Leather Gloves", ItemType.GLOVES, "Simple leather gloves", stats={"defense": 1}),
        Item("Health Potion", ItemType.CONSUMABLE, "Restores 20 HP"),
        Item("Mana Crystal", ItemType.CONSUMABLE, "Restores 15 MP"),
        Item("Iron Ore", ItemType.MATERIAL, "Raw iron material"),
        Item("Wood Log", ItemType.MATERIAL, "Raw wood material"),
        Item("Quest Scroll", ItemType.QUEST, "A mysterious message")
    ] 