"""Main game class"""

import pygame
import asyncio
from src.constants import *
from src.player import Player
from src.dungeon_map import DungeonMap
from src.raycaster import Raycaster
from src.party import Party
from src.party_ui import PartyUI
from src.inventory_ui import InventoryUI
from src.combat_ui import CombatUI

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
        
        # Create player (start at position 1.5, 1.5 in grid coordinates)
        self.player = Player(1.5 * TILE_SIZE, 1.5 * TILE_SIZE, 0)
        
        # Create raycaster
        self.raycaster = Raycaster(self.dungeon_map)
        
        # Create party system
        self.party = Party()
        self.party_ui = PartyUI(self.party)
        self.inventory_ui = InventoryUI()
        self.combat_ui = CombatUI(self.party)
        
        # Give combat UI access to game objects for minimap
        self.combat_ui.dungeon_map = self.dungeon_map
        self.combat_ui.player = self.player
        
        # Game state
        self.paused = False
        
        # Font for info
        self.font = pygame.font.Font(None, 24)
        
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
        
        keys = pygame.key.get_pressed()
        
        forward = 0
        strafe = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            forward = 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            forward = -1
        if keys[pygame.K_a]:
            strafe = -1
        if keys[pygame.K_d]:
            strafe = 1
        
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            self.player.rotate(-ROTATION_SPEED)
        if keys[pygame.K_e] or keys[pygame.K_RIGHT]:
            self.player.rotate(ROTATION_SPEED)
        
        if forward != 0 or strafe != 0:
            self.player.move(self.dungeon_map, forward, strafe)
        
        self.raycaster.cast_rays(self.player)
    
    def draw(self):
        """Draw everything"""
        self.raycaster.render(self.screen)
        
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
