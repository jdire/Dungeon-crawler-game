"""Item system with stats"""

class Item:
    """Base item class"""
    
    def __init__(self, name, item_type="misc"):
        self.name = name
        self.item_type = item_type  # weapon, armor, consumable, misc
        
class Weapon(Item):
    """Weapon item with damage and properties"""
    
    def __init__(self, name, damage, weapon_type="melee"):
        super().__init__(name, "weapon")
        self.damage = damage  # Base damage
        self.weapon_type = weapon_type  # melee, ranged
        self.equipped_slot = None  # main_hand or off_hand
    
    def get_total_damage(self, character):
        """Calculate total damage including character strength"""
        base = self.damage
        # Melee weapons benefit from strength
        if self.weapon_type == "melee":
            strength_bonus = character.strength // 2
            return base + strength_bonus
        return base

class Armor(Item):
    """Armor item with defense"""
    
    def __init__(self, name, defense, armor_slot):
        super().__init__(name, "armor")
        self.defense = defense
        self.armor_slot = armor_slot  # head, chest, arms, hands, legs, feet, belt

class Consumable(Item):
    """Consumable item with effect"""
    
    def __init__(self, name, effect_type, effect_value):
        super().__init__(name, "consumable")
        self.effect_type = effect_type  # heal, mana, stamina, buff
        self.effect_value = effect_value
    
    def use(self, character):
        """Use the consumable on a character"""
        if self.effect_type == "heal":
            character.heal(self.effect_value)
            return f"{character.name} restored {self.effect_value} HP"
        elif self.effect_type == "mana":
            character.restore_mana(self.effect_value)
            return f"{character.name} restored {self.effect_value} MP"
        elif self.effect_type == "stamina":
            character.restore_stamina(self.effect_value)
            return f"{character.name} restored {self.effect_value} SP"
        return f"{character.name} used {self.name}"

# Predefined weapons
WEAPONS = {
    "Sword": Weapon("Sword", damage=8, weapon_type="melee"),
    "Axe": Weapon("Axe", damage=10, weapon_type="melee"),
    "Dagger": Weapon("Dagger", damage=4, weapon_type="melee"),
    "Mace": Weapon("Mace", damage=7, weapon_type="melee"),
    "Staff": Weapon("Staff", damage=5, weapon_type="melee"),
    "Bow": Weapon("Bow", damage=6, weapon_type="ranged"),
    "Crossbow": Weapon("Crossbow", damage=8, weapon_type="ranged"),
}
