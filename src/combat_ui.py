"""Combat UI for character actions and equipment"""

import pygame
import math
from src.constants import *
from src.items import WEAPONS

class CombatUI:
    """Combat interface showing character weapons and class abilities"""
    
    def __init__(self, party):
        """Initialize combat UI"""
        self.party = party
        self.dungeon_map = None
        self.player = None
        self.enemy_encounters = None
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        
        # UI layout - full right side panel
        self.panel_width = 380
        self.panel_x = SCREEN_WIDTH - self.panel_width
        self.panel_y = 0
        self.panel_height = SCREEN_HEIGHT
        
        # Selected character for action menu
        self.selected_character_index = 0
        
        # Character orb size
        self.orb_size = 20
        self.weapon_slot_size = 55
        
        # Layout positions
        self.minimap_y = 8
        self.minimap_height = 200
        self.characters_start_y = self.minimap_y + self.minimap_height + 20
        self.separator_y = self.characters_start_y + (75 * 4) + 15
        
        # Class-specific abilities
        self.class_abilities = {
            'Warrior': ['Feat of Strength', 'Intimidate', 'Power Attack'],
            'Mage': ['Spell Wielding', 'Confusion Magic', 'Arcane Blast'],
            'Rogue': ['Stealthing', 'Thieving', 'Trapping'],
            'Cleric': ['Praying', 'Blessing', 'Holy Shield']
        }
        
        # Weapon swing animation
        self.weapon_swinging = None  # (char_index, slot, start_time)
        self.swing_duration = 0.3  # seconds
    
    def handle_click(self, pos):
        """Handle mouse click on combat UI"""
        # Check if click is in the right panel area
        if pos[0] < self.panel_x:
            return False
        
        # Check character orb selections
        for i, char in enumerate(self.party.members):
            orb_y = self.characters_start_y + i * 75
            orb_rect = pygame.Rect(self.panel_x + 15, orb_y, self.orb_size, self.orb_size)
            
            if orb_rect.collidepoint(pos):
                self.selected_character_index = i
                print(f"Selected {char.name}")
                return True
            
            # Check main hand weapon click
            main_hand_rect = pygame.Rect(self.panel_x + 70, orb_y - 8, self.weapon_slot_size, self.weapon_slot_size)
            if main_hand_rect.collidepoint(pos):
                self.use_weapon(i, 'main_hand')
                return True
            
            # Check off hand weapon click
            off_hand_rect = pygame.Rect(self.panel_x + 140, orb_y - 8, self.weapon_slot_size, self.weapon_slot_size)
            if off_hand_rect.collidepoint(pos):
                self.use_weapon(i, 'off_hand')
                return True
        
        # Check ability buttons
        selected_char = self.party.members[self.selected_character_index]
        abilities = self.class_abilities.get(selected_char.char_class, [])
        
        abilities_start_y = self.separator_y + 50
        for i, ability in enumerate(abilities):
            ability_rect = pygame.Rect(
                self.panel_x + 15,
                abilities_start_y + i * 45,
                self.panel_width - 30,
                40
            )
            if ability_rect.collidepoint(pos):
                self.use_ability(ability)
                return True
        
        return False
    
    def use_weapon(self, char_index, slot):
        """Use equipped weapon"""
        import time
        
        char = self.party.members[char_index]
        weapon_name = char.equipment.get(slot)
        
        if not weapon_name:
            print(f"{char.name} has no weapon in {slot}")
            return
        
        # Get weapon stats
        weapon = WEAPONS.get(weapon_name)
        if not weapon:
            print(f"{char.name} swings {weapon_name} (no stats)")
            return
        
        # Calculate damage
        total_damage = weapon.get_total_damage(char)
        
        # Start swing animation
        self.weapon_swinging = (char_index, slot, time.time())
        
        # Check if there's an enemy in front of player
        if self.player and self.enemy_encounters:
            enemy, ex, ey = self.enemy_encounters.get_enemy_in_front_of_player(self.player)
            
            if enemy:
                # Hit the enemy!
                enemy_died = enemy.take_damage(total_damage)
                print(f"{char.name} hits {enemy.name} with {weapon_name} for {total_damage} damage! ({enemy.health}/{enemy.max_health} HP)")
                
                if enemy_died:
                    print(f"{enemy.name} has been defeated!")
                    self.enemy_encounters.remove_enemy(ex, ey)
            else:
                print(f"{char.name} swings {weapon_name} but hits nothing!")
        else:
            print(f"{char.name} swings {weapon_name} ({weapon.weapon_type}) for {total_damage} damage!")
    
    def use_ability(self, ability):
        """Use class ability"""
        char = self.party.members[self.selected_character_index]
        print(f"{char.name} uses {ability}")
        # TODO: Implement ability logic
    
    def draw(self, screen):
        """Draw combat UI"""
        import time
        
        # Draw full right panel background
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(screen, WHITE, panel_rect, 3)
        
        # Check weapon swing animation
        if self.weapon_swinging:
            char_index, slot, start_time = self.weapon_swinging
            elapsed = time.time() - start_time
            if elapsed > self.swing_duration:
                self.weapon_swinging = None  # Animation complete
        
        # Draw minimap at top
        self.draw_minimap(screen)
        
        # Draw character weapons section
        for i, char in enumerate(self.party.members):
            y_offset = self.characters_start_y + i * 75
            
            # Draw character orb with selection indicator
            orb_center = (self.panel_x + 15 + self.orb_size // 2, y_offset + self.orb_size // 2)
            
            # Selection checkbox
            checkbox_rect = pygame.Rect(self.panel_x + 15, y_offset, self.orb_size, self.orb_size)
            pygame.draw.rect(screen, WHITE, checkbox_rect, 2)
            
            # Draw checkmark if selected
            if i == self.selected_character_index:
                pygame.draw.line(screen, GREEN, 
                               (checkbox_rect.left + 4, checkbox_rect.centery),
                               (checkbox_rect.centerx, checkbox_rect.bottom - 4), 3)
                pygame.draw.line(screen, GREEN,
                               (checkbox_rect.centerx, checkbox_rect.bottom - 4),
                               (checkbox_rect.right - 4, checkbox_rect.top + 4), 3)
            
            # Draw character indicator orb next to checkbox
            pygame.draw.circle(screen, char.portrait_color, 
                             (self.panel_x + 50, y_offset + 10), 11)
            pygame.draw.circle(screen, WHITE, 
                             (self.panel_x + 50, y_offset + 10), 11, 2)
            
            # Draw main hand weapon slot
            main_hand_rect = pygame.Rect(self.panel_x + 70, y_offset - 8, 
                                         self.weapon_slot_size, self.weapon_slot_size)
            main_hand = char.equipment.get('main_hand')
            
            # Check if this weapon is swinging
            is_swinging = (self.weapon_swinging and 
                          self.weapon_swinging[0] == i and 
                          self.weapon_swinging[1] == 'main_hand')
            
            color = YELLOW if is_swinging else (GREEN if main_hand else DARK_GRAY)
            pygame.draw.rect(screen, color, main_hand_rect)
            pygame.draw.rect(screen, WHITE, main_hand_rect, 2)
            
            if main_hand:
                weapon_text = self.small_font.render(main_hand[:4], True, BLACK)
                weapon_rect = weapon_text.get_rect(center=main_hand_rect.center)
                screen.blit(weapon_text, weapon_rect)
                
                # Show damage stat if weapon is defined
                weapon_obj = WEAPONS.get(main_hand)
                if weapon_obj:
                    dmg = weapon_obj.get_total_damage(char)
                    dmg_text = self.small_font.render(f"{dmg}dmg", True, RED)
                    screen.blit(dmg_text, (main_hand_rect.x, main_hand_rect.bottom + 2))
            else:
                # Draw "M" for main hand
                label = self.small_font.render("M", True, GRAY)
                label_rect = label.get_rect(center=main_hand_rect.center)
                screen.blit(label, label_rect)
            
            # Draw off hand weapon slot
            off_hand_rect = pygame.Rect(self.panel_x + 140, y_offset - 8,
                                        self.weapon_slot_size, self.weapon_slot_size)
            off_hand = char.equipment.get('off_hand')
            
            # Check if this weapon is swinging
            is_swinging = (self.weapon_swinging and 
                          self.weapon_swinging[0] == i and 
                          self.weapon_swinging[1] == 'off_hand')
            
            color = YELLOW if is_swinging else (GREEN if off_hand else DARK_GRAY)
            pygame.draw.rect(screen, color, off_hand_rect)
            pygame.draw.rect(screen, WHITE, off_hand_rect, 2)
            
            if off_hand:
                weapon_text = self.small_font.render(off_hand[:4], True, BLACK)
                weapon_rect = weapon_text.get_rect(center=off_hand_rect.center)
                screen.blit(weapon_text, weapon_rect)
            else:
                # Draw "O" for off hand
                label = self.small_font.render("O", True, GRAY)
                label_rect = label.get_rect(center=off_hand_rect.center)
                screen.blit(label, label_rect)
            
            # Draw character name
            name_text = self.small_font.render(char.name, True, char.portrait_color)
            screen.blit(name_text, (self.panel_x + 210, y_offset + 15))
        
        # Draw separator line
        pygame.draw.line(screen, WHITE, 
                        (self.panel_x, self.separator_y),
                        (self.panel_x + self.panel_width, self.separator_y), 3)
        
        # Draw selected character's abilities
        selected_char = self.party.members[self.selected_character_index]
        abilities = self.class_abilities.get(selected_char.char_class, [])
        
        # Draw class title
        title_text = self.font.render(f"{selected_char.char_class} Actions", True, WHITE)
        screen.blit(title_text, (self.panel_x + 15, self.separator_y + 15))
        
        # Draw ability buttons
        abilities_start_y = self.separator_y + 50
        for i, ability in enumerate(abilities):
            ability_rect = pygame.Rect(
                self.panel_x + 15,
                abilities_start_y + i * 45,
                self.panel_width - 30,
                40
            )
            
            pygame.draw.rect(screen, BLUE, ability_rect)
            pygame.draw.rect(screen, WHITE, ability_rect, 3)
            
            ability_text = self.small_font.render(ability, True, WHITE)
            text_rect = ability_text.get_rect(center=ability_rect.center)
            screen.blit(ability_text, text_rect)
    
    def draw_minimap(self, screen):
        """Draw overhead minimap inside combat UI panel"""
        # Minimap stretches full width of panel
        minimap_width = self.panel_width - 10
        minimap_x = self.panel_x + 5
        
        minimap_rect = pygame.Rect(minimap_x, self.minimap_y, minimap_width, self.minimap_height)
        pygame.draw.rect(screen, BLACK, minimap_rect)
        pygame.draw.rect(screen, WHITE, minimap_rect, 2)
        
        if not self.dungeon_map or not self.player:
            # Draw placeholder if game objects not set yet
            minimap_label = self.small_font.render("Minimap", True, WHITE)
            screen.blit(minimap_label, (minimap_x + 5, self.minimap_y + 5))
            return
        
        # Calculate scale to fit the dungeon in the minimap
        minimap_scale = min(
            (minimap_width - 10) / (self.dungeon_map.width * TILE_SIZE),
            (self.minimap_height - 10) / (self.dungeon_map.height * TILE_SIZE)
        )
        
        # Calculate offset to center the minimap content
        map_width = self.dungeon_map.width * TILE_SIZE * minimap_scale
        map_height = self.dungeon_map.height * TILE_SIZE * minimap_scale
        offset_x = (minimap_width - map_width) / 2
        offset_y = (self.minimap_height - map_height) / 2
        
        minimap_surf = pygame.Surface((minimap_width, self.minimap_height))
        minimap_surf.fill(BLACK)
        
        # Draw walls
        for y in range(self.dungeon_map.height):
            for x in range(self.dungeon_map.width):
                if self.dungeon_map.get_tile(x, y) == WALL:
                    rect = pygame.Rect(
                        offset_x + x * TILE_SIZE * minimap_scale,
                        offset_y + y * TILE_SIZE * minimap_scale,
                        TILE_SIZE * minimap_scale,
                        TILE_SIZE * minimap_scale
                    )
                    pygame.draw.rect(minimap_surf, WHITE, rect)
        
        # Draw player position and direction
        player_x = offset_x + self.player.x * minimap_scale
        player_y = offset_y + self.player.y * minimap_scale
        pygame.draw.circle(minimap_surf, RED, (int(player_x), int(player_y)), 3)
        
        # Draw direction arrow (pygame Y+ is down, so sin is positive for down angles)
        dir_len = 10
        end_x = player_x + math.cos(self.player.angle) * dir_len
        end_y = player_y + math.sin(self.player.angle) * dir_len
        pygame.draw.line(minimap_surf, RED, (player_x, player_y), (end_x, end_y), 2)
        
        # Draw minimap surface
        screen.blit(minimap_surf, (minimap_x, self.minimap_y))
