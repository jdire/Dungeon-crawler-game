"""Party management system"""

from src.character import Character
from src.constants import *

class Party:
    """Manages party of 4 characters"""
    
    def __init__(self):
        """Initialize party with 4 characters"""
        self.members = [
            Character("Warrior", RED, "Warrior"),
            Character("Mage", BLUE, "Mage"),
            Character("Rogue", GREEN, "Rogue"),
            Character("Cleric", YELLOW, "Cleric")
        ]
        
        # Set different starting stats based on class
        self.members[0].max_health = 120  # Warrior - high health
        self.members[0].health = 120
        self.members[0].max_mana = 50
        self.members[0].mana = 50
        self.members[0].strength = 8  # Warriors are strong
        self.members[0].equipment['main_hand'] = "Sword"
        self.members[0].equipment['off_hand'] = "Shield"
        
        self.members[1].max_health = 70  # Mage - low health, high mana
        self.members[1].health = 70
        self.members[1].max_mana = 150
        self.members[1].mana = 150
        self.members[1].strength = 3  # Mages are weak
        self.members[1].equipment['main_hand'] = "Staff"
        
        self.members[2].max_health = 90  # Rogue - medium health, high stamina
        self.members[2].health = 90
        self.members[2].max_stamina = 130
        self.members[2].stamina = 130
        self.members[2].strength = 5  # Rogues are average
        self.members[2].equipment['main_hand'] = "Dagger"
        self.members[2].equipment['off_hand'] = "Dagger"
        
        self.members[3].max_health = 100  # Cleric - balanced
        self.members[3].health = 100
        self.members[3].max_mana = 120
        self.members[3].mana = 120
        self.members[3].strength = 6  # Clerics are slightly strong
        self.members[3].equipment['main_hand'] = "Mace"
        
        # Add some test inventory items
        self.members[0].inventory = ["Sword", "Shield", "Potion", "Bread"]
        self.members[1].inventory = ["Staff", "Scroll", "Mana Pot"]
        self.members[2].inventory = ["Dagger", "Lockpick", "Rope", "Poison", "Cloak"]
        self.members[3].inventory = ["Mace", "Holy Symbol", "Bandage"]
    
    def get_member(self, index):
        """Get party member by index"""
        if 0 <= index < len(self.members):
            return self.members[index]
        return None
    
    def is_alive(self):
        """Check if at least one party member is alive"""
        return any(member.health > 0 for member in self.members)
    
    def restore_all(self):
        """Restore all party members to full health/stamina/mana"""
        for member in self.members:
            member.health = member.max_health
            member.stamina = member.max_stamina
            member.mana = member.max_mana
