"""Enemy system for combat"""

import random

class Enemy:
    """Enemy entity with stats"""
    
    def __init__(self, name, max_health, damage, gold=0):
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.damage = damage
        self.gold = gold
        self.is_alive = True
    
    def take_damage(self, amount):
        """Enemy takes damage"""
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.is_alive = False
            return True  # Enemy died
        return False
    
    def attack(self):
        """Calculate enemy attack damage with some variance"""
        variance = random.randint(-2, 2)
        return max(1, self.damage + variance)

class EnemyEncounter:
    """Manages enemy encounters at specific map positions"""
    
    def __init__(self):
        self.encounters = {}  # (grid_x, grid_y): Enemy
    
    def add_enemy(self, grid_x, grid_y, enemy):
        """Place an enemy at a grid position"""
        self.encounters[(grid_x, grid_y)] = enemy
    
    def get_enemy_at(self, grid_x, grid_y):
        """Get enemy at position"""
        return self.encounters.get((grid_x, grid_y))
    
    def remove_enemy(self, grid_x, grid_y):
        """Remove enemy at position"""
        if (grid_x, grid_y) in self.encounters:
            del self.encounters[(grid_x, grid_y)]
    
    def get_enemy_in_front_of_player(self, player):
        """Get enemy directly in front of player"""
        # Calculate position in front of player
        forward_dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W
        fx, fy = forward_dirs[player.facing]
        
        check_x = player.grid_x + fx
        check_y = player.grid_y + fy
        
        enemy = self.get_enemy_at(check_x, check_y)
        if enemy and enemy.is_alive:
            return enemy, check_x, check_y
        return None, None, None

# Predefined enemy types
def create_dummy():
    """Create a training dummy"""
    return Enemy("Training Dummy", max_health=50, damage=0, gold=0)

def create_goblin():
    """Create a goblin"""
    return Enemy("Goblin", max_health=20, damage=5, gold=10)

def create_orc():
    """Create an orc"""
    return Enemy("Orc", max_health=40, damage=8, gold=25)

def create_skeleton():
    """Create a skeleton"""
    return Enemy("Skeleton", max_health=25, damage=6, gold=15)
