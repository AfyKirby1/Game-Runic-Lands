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
    def __init__(self, inventory, screen_size):
        self.inventory = inventory
        self.screen_size = screen_size
        self.slot_size = 40
        self.padding = 10
        self.rows = 5
        self.cols = 4
        
        # Calculate inventory window size
        self.width = (self.slot_size + self.padding) * self.cols + self.padding
        self.height = (self.slot_size + self.padding) * self.rows + self.padding
        
        # Center the inventory on screen
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] - self.height) // 2
        
        # Create background surface
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill((40, 40, 40))  # Dark gray
        # Add semi-transparency
        self.background.set_alpha(230)
        
        # Create font for item names
        self.font = pygame.font.Font(None, 20)
        
        # Selected slot
        self.selected_slot = None
        
    def get_slot_rect(self, index):
        """Get the rectangle for a specific inventory slot"""
        row = index // self.cols
        col = index % self.cols
        x = self.x + self.padding + (self.slot_size + self.padding) * col
        y = self.y + self.padding + (self.slot_size + self.padding) * row
        return pygame.Rect(x, y, self.slot_size, self.slot_size)
        
    def draw(self, screen):
        """Draw the inventory interface"""
        # Draw semi-transparent background
        screen.blit(self.background, (self.x, self.y))
        
        # Draw border
        pygame.draw.rect(screen, (100, 100, 100), 
                        (self.x, self.y, self.width, self.height), 2)
        
        # Draw title
        title = self.font.render("Inventory", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=self.x + self.width//2, 
                                  top=self.y + 5)
        screen.blit(title, title_rect)
        
        # Draw slots
        for i in range(self.rows * self.cols):
            slot_rect = self.get_slot_rect(i)
            
            # Draw slot background
            pygame.draw.rect(screen, (60, 60, 60), slot_rect)
            pygame.draw.rect(screen, (100, 100, 100), slot_rect, 1)
            
            # Draw item if slot is filled
            if i < len(self.inventory.items) and self.inventory.items[i]:
                item = self.inventory.items[i]
                # Draw item background based on type
                if item.item_type == ItemType.WEAPON:
                    color = (139, 69, 19)  # Brown for weapons
                elif item.item_type == ItemType.ARMOR:
                    color = (70, 130, 180)  # Steel blue for armor
                elif item.item_type == ItemType.CONSUMABLE:
                    color = (46, 139, 87)  # Sea green for consumables
                else:
                    color = (128, 128, 128)  # Gray for misc
                    
                # Draw item background
                pygame.draw.rect(screen, color, slot_rect)
                
                # Draw item name
                text = self.font.render(item.name[:10], True, (255, 255, 255))
                text_rect = text.get_rect(center=slot_rect.center)
                screen.blit(text, text_rect)
                
                # Draw item count if stackable
                if hasattr(item, 'count') and item.count > 1:
                    count_text = self.font.render(str(item.count), True, (255, 255, 255))
                    count_rect = count_text.get_rect(bottomright=slot_rect.bottomright)
                    screen.blit(count_text, count_rect)
            
            # Highlight selected slot
            if i == self.selected_slot:
                pygame.draw.rect(screen, (255, 255, 255), slot_rect, 2)
                
                # Draw item description if selected
                if i < len(self.inventory.items) and self.inventory.items[i]:
                    item = self.inventory.items[i]
                    desc = self.font.render(item.description, True, (255, 255, 255))
                    desc_rect = desc.get_rect(centerx=self.x + self.width//2,
                                           bottom=self.y + self.height - 5)
                    screen.blit(desc, desc_rect)
    
    def handle_click(self, pos):
        """Handle mouse click in inventory"""
        for i in range(self.rows * self.cols):
            slot_rect = self.get_slot_rect(i)
            if slot_rect.collidepoint(pos):
                self.selected_slot = i
                return True
        return False


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