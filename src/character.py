"""Character class with stats and inventory"""

from src.constants import *

class Character:
    """RPG character with stats, equipment, and inventory"""
    
    def __init__(self, name, portrait_color, char_class="Warrior"):
        """Initialize character"""
        self.name = name
        self.char_class = char_class
        self.portrait_color = portrait_color
        
        # Stats
        self.max_health = 100
        self.health = 100
        self.max_stamina = 100
        self.stamina = 100
        self.max_mana = 100
        self.mana = 100
        
        # Attributes
        self.strength = 5  # Default strength
        
        # Equipment slots
        self.equipment = {
            'head': None,
            'chest': None,
            'arms': None,
            'hands': None,
            'legs': None,
            'feet': None,
            'belt': None,
            'main_hand': None,
            'off_hand': None,
            'ranged': None
        }
        
        # Inventory (list of items)
        self.inventory = []
    
    def take_damage(self, amount):
        """Reduce health"""
        self.health = max(0, self.health - amount)
        return self.health <= 0  # Returns True if dead
    
    def heal(self, amount):
        """Restore health"""
        self.health = min(self.max_health, self.health + amount)
    
    def use_stamina(self, amount):
        """Use stamina"""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False
    
    def use_mana(self, amount):
        """Use mana"""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False
    
    def restore_stamina(self, amount):
        """Restore stamina"""
        self.stamina = min(self.max_stamina, self.stamina + amount)
    
    def restore_mana(self, amount):
        """Restore mana"""
        self.mana = min(self.max_mana, self.mana + amount)
    
    def equip_item(self, item, slot):
        """Equip an item to a slot"""
        if slot in self.equipment:
            old_item = self.equipment[slot]
            self.equipment[slot] = item
            return old_item
        return None
    
    def unequip_item(self, slot):
        """Remove item from slot"""
        if slot in self.equipment:
            item = self.equipment[slot]
            self.equipment[slot] = None
            return item
        return None
    
    def get_inventory_size(self):
        """Calculate inventory size based on strength (20 + 2 per strength point)"""
        return 20 + (self.strength * 2)
