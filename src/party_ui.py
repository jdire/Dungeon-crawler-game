"""Party UI - character portraits and stats"""

import pygame
from src.constants import *

class PartyUI:
    """Display party member portraits and stats"""
    
    def __init__(self, party):
        """Initialize party UI"""
        self.party = party
        self.portrait_size = 80
        self.portrait_padding = 10
        self.bar_width = 10
        self.bar_height = 70
        self.font = pygame.font.Font(None, 18)
        
        # Calculate portrait positions
        self.portrait_rects = []
        for i in range(4):
            x = 10 + i * (self.portrait_size + 50 + self.portrait_padding)  # More space for vertical bars
            y = 10
            self.portrait_rects.append(pygame.Rect(x, y, self.portrait_size, self.portrait_size))
    
    def handle_click(self, pos):
        """Check if a portrait was clicked, return character index or None"""
        for i, rect in enumerate(self.portrait_rects):
            if rect.collidepoint(pos):
                return i
        return None
    
    def draw(self, screen):
        """Draw all party member portraits and stats"""
        for i, member in enumerate(self.party.members):
            self.draw_portrait(screen, member, i)
    
    def draw_portrait(self, screen, character, index):
        """Draw single character portrait with stats"""
        rect = self.portrait_rects[index]
        
        # Draw portrait background
        if character.health > 0:
            pygame.draw.rect(screen, character.portrait_color, rect)
        else:
            pygame.draw.rect(screen, DARK_GRAY, rect)  # Dead character
        
        pygame.draw.rect(screen, WHITE, rect, 2)
        
        # Draw character initial in center
        initial = character.name[0]
        text = self.font.render(initial, True, WHITE if character.health > 0 else GRAY)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        
        # Draw stat bars to the right (vertical)
        bars_x = rect.right + 5
        bars_y = rect.top + 5
        
        # Health bar (red) - leftmost
        self.draw_stat_bar(screen, bars_x, bars_y, character.health, character.max_health, RED)
        
        # Stamina bar (green) - middle
        self.draw_stat_bar(screen, bars_x + 15, bars_y, character.stamina, character.max_stamina, GREEN)
        
        # Mana bar (blue) - rightmost
        self.draw_stat_bar(screen, bars_x + 30, bars_y, character.mana, character.max_mana, BLUE)
        
        # Draw character name below portrait
        name_text = self.font.render(character.name, True, WHITE)
        name_rect = name_text.get_rect(centerx=rect.centerx, top=rect.bottom + 2)
        screen.blit(name_text, name_rect)
    
    def draw_stat_bar(self, screen, x, y, current, maximum, color):
        """Draw a vertical stat bar (health/stamina/mana)"""
        # Background
        pygame.draw.rect(screen, DARK_GRAY, (x, y, self.bar_width, self.bar_height))
        
        # Filled portion (from bottom up)
        if maximum > 0:
            fill_height = int((current / maximum) * self.bar_height)
            fill_y = y + self.bar_height - fill_height
            pygame.draw.rect(screen, color, (x, fill_y, self.bar_width, fill_height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (x, y, self.bar_width, self.bar_height), 1)
