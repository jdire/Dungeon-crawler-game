"""Main game class"""

import pygame
import asyncio
from src.constants import *
from src.player import Player
from src.dungeon_map import DungeonMap
from src.simple_raycaster import SimpleRaycaster
from src.party import Party
from src.party_ui import PartyUI
from src.inventory_ui import InventoryUI
from src.combat_ui import CombatUI
from src.enemy import EnemyEncounter, create_dummy

class Game:
    """Main game controller"""
    
    def __init__(self):
        """Initialize game"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon Crawler")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create dungeon
        self.dungeon_map = DungeonMap()
        
        # Create player (start at grid position 1, 1, facing North)
        self.player = Player(1, 1, 0)
        
        # Create enemy encounter system
        self.enemy_encounters = EnemyEncounter()
        # Place a training dummy directly north of player (player starts at 1,1 facing north)
        self.enemy_encounters.add_enemy(1, 2, create_dummy())
        
        # Create simple raycaster with enemy encounters
        self.renderer = SimpleRaycaster(self.dungeon_map, self.enemy_encounters)
        
        # Create party system
        self.party = Party()
        self.party_ui = PartyUI(self.party)
        self.inventory_ui = InventoryUI()
        self.combat_ui = CombatUI(self.party)
        
        # Give combat UI access to game objects
        self.combat_ui.dungeon_map = self.dungeon_map
        self.combat_ui.player = self.player
        self.combat_ui.enemy_encounters = self.enemy_encounters
        
        # Game state
        self.paused = False
        
        # Font for info
        self.font = pygame.font.Font(None, 32)
        
    async def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
            await asyncio.sleep(0)
        
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.inventory_ui.active:
                        self.inventory_ui.close()
                        self.paused = False
                    else:
                        self.running = False
                elif event.key == pygame.K_i:
                    if self.inventory_ui.active:
                        self.inventory_ui.close()
                        self.paused = False
                    else:
                        self.inventory_ui.open(self.party.members[0])
                        self.paused = True
                # Tile-based movement
                elif not self.paused:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.player.try_move_forward(self.dungeon_map)
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.player.try_move_backward(self.dungeon_map)
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.player.turn_left()
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.player.turn_right()
                    elif event.key == pygame.K_q:
                        self.player.try_strafe_left(self.dungeon_map)
                    elif event.key == pygame.K_e:
                        self.player.try_strafe_right(self.dungeon_map)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check combat UI first (right side)
                if self.combat_ui.handle_click(event.pos):
                    pass  # Combat UI handled the click
                else:
                    char_index = self.party_ui.handle_click(event.pos)
                    if char_index is not None:
                        self.inventory_ui.open(self.party.members[char_index])
                        self.paused = True
                    elif self.inventory_ui.active:
                        self.inventory_ui.handle_click(event.pos)
                        if not self.inventory_ui.active:
                            self.paused = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.inventory_ui.active:
                    self.inventory_ui.handle_mouse_release(event.pos)
                    # If exiting edit mode, print the layout
                    if self.inventory_ui.edit_mode and not self.inventory_ui.dragging_slot:
                        pass  # Layout is printed when save button is clicked
            elif event.type == pygame.MOUSEMOTION:
                if self.inventory_ui.active:
                    self.inventory_ui.handle_mouse_motion(event.pos)
    
    def update(self, dt):
        """Update game state"""
        if self.paused:
            return
    
    def draw(self):
        """Draw everything"""
        self.renderer.render(self.screen, self.player)
        
        self.party_ui.draw(self.screen)
        
        self.combat_ui.draw(self.screen)
        
        self.inventory_ui.draw(self.screen)
        
        if not self.inventory_ui.active:
            info_lines = [
                "WASD: Move | Q/E: Turn",
                "Click portrait: Inventory",
                "I: Toggle Inventory | ESC: Quit"
            ]
            
            y_offset = 120
            for i, line in enumerate(info_lines):
                text = self.font.render(line, True, WHITE)
                self.screen.blit(text, (10, y_offset + i * 25))
        
        pygame.display.flip()
