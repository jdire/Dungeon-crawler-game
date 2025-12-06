"""Character inventory UI"""

import pygame
from src.constants import *

class InventoryUI:
    """Character inventory and equipment screen"""
    
    def __init__(self):
        """Initialize inventory UI"""
        self.active = False
        self.selected_character = None
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # UI layout - leave space for combat UI on right (250px)
        combat_ui_width = 250
        self.panel_rect = pygame.Rect(50, 50, SCREEN_WIDTH - combat_ui_width - 100, SCREEN_HEIGHT - 100)
        
        # Split panel into two sections: equipment (left) and inventory (right)
        self.equipment_panel_width = 350
        self.inventory_panel_x = self.equipment_panel_width + 10
        
        # Equipment slot positions (relative to panel)
        self.equipment_slots = {
            'arms': (70, 130),
            'belt': (220, 210),
            'chest': (220, 130),
            'feet': (180, 320),
            'hands': (70, 210),
            'head': (150, 50),
            'legs': (120, 320),
            'main_hand': (10, 210),
            'off_hand': (290, 210),
            'ranged': (290, 130),
        }
        
        # Stick figure position (relative to panel)
        self.stick_figure_pos = (170, 230)
        
        self.slot_size = 50
        self.grid_size = 10  # Snap to 10 pixel grid
        
        # Drag and drop system
        self.dragging_item = None  # Item being dragged
        self.dragging_source = None  # 'equipment' or 'inventory'
        self.dragging_source_slot = None  # Slot name or index
        self.drag_offset = (0, 0)
        
        # Layout editing mode
        self.edit_mode = False
        self.dragging_slot = None
        self.dragging_stick_figure = False
        self.edit_button_rect = None
    
    def open(self, character):
        """Open inventory for character"""
        self.active = True
        self.selected_character = character
    
    def close(self):
        """Close inventory"""
        self.active = False
        self.selected_character = None
    
    def handle_click(self, pos):
        """Handle mouse click in inventory"""
        if not self.active:
            return False
        
        # Check edit mode button click
        if self.edit_button_rect and self.edit_button_rect.collidepoint(pos):
            if self.edit_mode:
                # Exiting edit mode - save layout to file
                self.save_layout_to_file()
            self.edit_mode = not self.edit_mode
            self.dragging_slot = None
            self.dragging_stick_figure = False
            print(f"Edit mode: {'ON' if self.edit_mode else 'OFF'}")
            return True
        
        # Check if clicked outside panel to close (but not in edit mode)
        if not self.panel_rect.collidepoint(pos):
            if not self.edit_mode:
                self.close()
            return True
        
        adjusted_pos = (pos[0] - self.panel_rect.x, pos[1] - self.panel_rect.y)
        
        if self.edit_mode:
            # Edit mode: drag equipment slots or stick figure
            # Check stick figure FIRST but with a smaller clickable area (just the torso)
            # This allows equipment slots to be clickable even if they overlap the figure
            stick_click_rect = pygame.Rect(
                self.stick_figure_pos[0] - 20,  # Smaller width
                self.stick_figure_pos[1] - 60,  # Just the torso area
                40,                              # 40 pixels wide
                80                               # 80 pixels tall (torso only)
            )
            
            if stick_click_rect.collidepoint(adjusted_pos):
                self.dragging_stick_figure = True
                self.drag_offset = (adjusted_pos[0] - self.stick_figure_pos[0], 
                                   adjusted_pos[1] - self.stick_figure_pos[1])
                print("Dragging stick figure")
                return True
            
            # Then check equipment slots
            for slot_name, (slot_x, slot_y) in self.equipment_slots.items():
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                if slot_rect.collidepoint(adjusted_pos):
                    self.dragging_slot = slot_name
                    self.drag_offset = (adjusted_pos[0] - slot_x, adjusted_pos[1] - slot_y)
                    print(f"Dragging {slot_name} slot")
                    return True
        else:
            # Normal mode: drag items
            # Check equipment slots (left side)
            if adjusted_pos[0] < self.equipment_panel_width:
                for slot_name, (slot_x, slot_y) in self.equipment_slots.items():
                    slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                    if slot_rect.collidepoint(adjusted_pos):
                        item = self.selected_character.equipment.get(slot_name)
                        if item:
                            self.dragging_item = item
                            self.dragging_source = 'equipment'
                            self.dragging_source_slot = slot_name
                            self.drag_offset = (adjusted_pos[0] - slot_x, adjusted_pos[1] - slot_y)
                            print(f"Dragging {item} from {slot_name}")
                        return True
            else:
                # Check inventory slots (right side)
                inv_slot = self.get_inventory_slot_at_pos(adjusted_pos)
                if inv_slot is not None and inv_slot < len(self.selected_character.inventory):
                    item = self.selected_character.inventory[inv_slot]
                    self.dragging_item = item
                    self.dragging_source = 'inventory'
                    self.dragging_source_slot = inv_slot
                    print(f"Dragging {item} from inventory slot {inv_slot}")
                    return True
        
        return True
    
    def handle_mouse_motion(self, pos):
        """Handle mouse motion for dragging slots in edit mode"""
        if not self.active or not self.edit_mode:
            return False
        
        if self.panel_rect.collidepoint(pos):
            adjusted_pos = (pos[0] - self.panel_rect.x, pos[1] - self.panel_rect.y)
            
            if self.dragging_stick_figure:
                # Move stick figure
                new_x = adjusted_pos[0] - self.drag_offset[0]
                new_y = adjusted_pos[1] - self.drag_offset[1]
                
                # Snap to grid
                new_x = round(new_x / self.grid_size) * self.grid_size
                new_y = round(new_y / self.grid_size) * self.grid_size
                
                # Constrain within panel bounds
                new_x = max(40, min(new_x, self.panel_rect.width - 40))
                new_y = max(100, min(new_y, self.panel_rect.height - 100))
                
                self.stick_figure_pos = (170, 230)
                return True
            
            elif self.dragging_slot:
                # Calculate new position relative to panel
                new_x = adjusted_pos[0] - self.drag_offset[0]
                new_y = adjusted_pos[1] - self.drag_offset[1]
                
                # Snap to grid
                new_x = round(new_x / self.grid_size) * self.grid_size
                new_y = round(new_y / self.grid_size) * self.grid_size
                
                # Constrain within panel bounds
                new_x = max(0, min(new_x, self.panel_rect.width - self.slot_size))
                new_y = max(0, min(new_y, self.panel_rect.height - self.slot_size))
                
                # Update slot position
                self.equipment_slots[self.dragging_slot] = (new_x, new_y)
                return True
        
        return False
    
    def handle_mouse_release(self, pos):
        """Handle mouse button release"""
        if not self.active:
            return False
        
        if self.edit_mode:
            if self.dragging_slot or self.dragging_stick_figure:
                if self.dragging_slot:
                    print(f"Released {self.dragging_slot} at {self.equipment_slots[self.dragging_slot]}")
                elif self.dragging_stick_figure:
                    print(f"Released stick figure at {self.stick_figure_pos}")
                self.dragging_slot = None
                self.dragging_stick_figure = False
                return True
        else:
            # Handle item drop
            if self.dragging_item:
                adjusted_pos = (pos[0] - self.panel_rect.x, pos[1] - self.panel_rect.y)
                
                # Check if dropped on equipment slot
                if adjusted_pos[0] < self.equipment_panel_width:
                    for slot_name, (slot_x, slot_y) in self.equipment_slots.items():
                        slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                        if slot_rect.collidepoint(adjusted_pos):
                            if self.can_equip_to_slot(self.dragging_item, slot_name):
                                self.move_item_to_equipment(slot_name)
                            else:
                                print(f"Cannot equip {self.dragging_item} to {slot_name}")
                            self.dragging_item = None
                            self.dragging_source = None
                            self.dragging_source_slot = None
                            return True
                else:
                    # Dropped on inventory side
                    inv_slot = self.get_inventory_slot_at_pos(adjusted_pos)
                    if inv_slot is not None:
                        self.move_item_to_inventory(inv_slot)
                    self.dragging_item = None
                    self.dragging_source = None
                    self.dragging_source_slot = None
                    return True
                
                # Dropped outside valid area
                self.dragging_item = None
                self.dragging_source = None
                self.dragging_source_slot = None
                return True
        
        return False
    
    def can_equip_to_slot(self, item, slot_name):
        """Check if item can be equipped to the given slot"""
        item_lower = item.lower()
        
        # Basic equipment logic
        equipment_rules = {
            'head': ['helm', 'helmet', 'hat', 'cap', 'crown'],
            'chest': ['armor', 'chest', 'plate', 'mail', 'robe', 'tunic'],
            'arms': ['bracers', 'armguards', 'sleeves'],
            'hands': ['gloves', 'gauntlets', 'mitts'],
            'legs': ['pants', 'greaves', 'leggings', 'trousers'],
            'feet': ['boots', 'shoes', 'sandals'],
            'belt': ['belt', 'sash', 'girdle'],
            'main_hand': ['sword', 'axe', 'mace', 'dagger', 'staff', 'wand', 'club', 'hammer'],
            'off_hand': ['shield', 'dagger', 'tome', 'orb'],
            'ranged': ['bow', 'crossbow', 'gun', 'sling']
        }
        
        if slot_name not in equipment_rules:
            return False
        
        # Check if any keyword matches
        for keyword in equipment_rules[slot_name]:
            if keyword in item_lower:
                return True
        
        return False
    
    def move_item_to_equipment(self, slot_name):
        """Move dragging item to equipment slot"""
        char = self.selected_character
        
        # Get item currently in slot
        old_item = char.equipment.get(slot_name)
        
        # Remove item from source
        if self.dragging_source == 'equipment':
            char.equipment[self.dragging_source_slot] = None
        elif self.dragging_source == 'inventory':
            char.inventory.pop(self.dragging_source_slot)
        
        # Place new item in equipment slot
        char.equipment[slot_name] = self.dragging_item
        
        # If there was an old item, add it to inventory
        if old_item:
            char.inventory.append(old_item)
            print(f"Swapped {self.dragging_item} with {old_item}")
        else:
            print(f"Equipped {self.dragging_item} to {slot_name}")
    
    def move_item_to_inventory(self, target_slot):
        """Move dragging item to inventory"""
        char = self.selected_character
        
        # Remove item from source
        if self.dragging_source == 'equipment':
            char.equipment[self.dragging_source_slot] = None
            char.inventory.append(self.dragging_item)
            print(f"Unequipped {self.dragging_item}")
        elif self.dragging_source == 'inventory' and self.dragging_source_slot != target_slot:
            # Move within inventory (swap positions)
            char.inventory.pop(self.dragging_source_slot)
            if target_slot < len(char.inventory):
                char.inventory.insert(target_slot, self.dragging_item)
            else:
                char.inventory.append(self.dragging_item)
    
    def get_inventory_slot_at_pos(self, adjusted_pos):
        """Get inventory slot index at the given position"""
        if not self.selected_character:
            return None
        
        inventory_size = self.selected_character.get_inventory_size()
        
        # Calculate grid dimensions
        import math
        cols = 6  # Fixed 6 columns for inventory
        rows = math.ceil(inventory_size / cols)
        
        slot_size = 45
        padding = 5
        start_x = self.inventory_panel_x + 10
        start_y = 100
        
        # Check if in inventory area
        if adjusted_pos[0] < start_x or adjusted_pos[1] < start_y:
            return None
        
        col = int((adjusted_pos[0] - start_x) / (slot_size + padding))
        row = int((adjusted_pos[1] - start_y) / (slot_size + padding))
        
        if col >= 0 and col < cols and row >= 0 and row < rows:
            slot_index = row * cols + col
            if slot_index < inventory_size:
                return slot_index
        
        return None
    
    def save_layout_to_file(self):
        """Save the current layout directly to the inventory_ui.py file"""
        print("\n=== Saving layout to file ===")
        
        # Read the current file
        file_path = '/media/joe_h/GameDrive/Games/dungeon-crawler/src/inventory_ui.py'
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Create the new equipment slots dictionary string
        slots_str = "self.equipment_slots = " + "{\n"
        for slot_name, pos in sorted(self.equipment_slots.items()):
            slots_str += f"            '{slot_name}': {pos},\n"
        slots_str += "        " + "}"
        
        # Find and replace the equipment_slots definition
        import re
        pattern = r"self\.equipment_slots = \{[^}]+\}"
        content = re.sub(pattern, slots_str, content, flags=re.DOTALL)
        
        # Replace stick figure position
        stick_pattern = r"self\.stick_figure_pos = \([^)]+\)"
        stick_replacement = f"self.stick_figure_pos = {self.stick_figure_pos}"
        content = re.sub(stick_pattern, stick_replacement, content)
        
        # Write back to file
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("Layout saved successfully!")
        print(f"Stick figure position: {self.stick_figure_pos}")
        print("================================\n")
    
    def draw(self, screen):
        """Draw inventory UI"""
        if not self.active or not self.selected_character:
            return
        
        char = self.selected_character
        
        # Draw semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Draw main panel
        pygame.draw.rect(screen, DARK_GRAY, self.panel_rect)
        pygame.draw.rect(screen, WHITE, self.panel_rect, 3)
        
        # Draw character name and class
        title_text = self.font.render(f"{char.name} - {char.char_class}", True, char.portrait_color)
        screen.blit(title_text, (self.panel_rect.x + 20, self.panel_rect.y + 10))
        
        # Draw divider between equipment and inventory
        divider_x = self.panel_rect.x + self.equipment_panel_width
        pygame.draw.line(screen, WHITE, (divider_x, self.panel_rect.y), (divider_x, self.panel_rect.bottom), 2)
        
        # Draw section labels
        equip_label = self.font.render("Equipment", True, WHITE)
        screen.blit(equip_label, (self.panel_rect.x + 20, self.panel_rect.y + 45))
        
        inv_label = self.font.render("Inventory", True, WHITE)
        screen.blit(inv_label, (self.panel_rect.x + self.inventory_panel_x + 10, self.panel_rect.y + 45))
        
        # Draw edit mode button (only in dev mode)
        if DEV_MODE:
            button_width = 120
            button_height = 35
            self.edit_button_rect = pygame.Rect(
                self.panel_rect.right - button_width - 20,
                self.panel_rect.y + 10,
                button_width,
                button_height
            )
            button_color = YELLOW if self.edit_mode else DARK_GRAY
            pygame.draw.rect(screen, button_color, self.edit_button_rect)
            pygame.draw.rect(screen, WHITE, self.edit_button_rect, 2)
            
            button_text = "EDIT MODE" if not self.edit_mode else "SAVE LAYOUT"
            button_label = self.small_font.render(button_text, True, BLACK if self.edit_mode else WHITE)
            button_label_rect = button_label.get_rect(center=self.edit_button_rect.center)
            screen.blit(button_label, button_label_rect)
        else:
            self.edit_button_rect = None
        
        # Draw equipment panel (left side)
        self.draw_equipment_panel(screen, char)
        
        # Draw inventory panel (right side)
        self.draw_inventory_panel(screen, char)
        
        # Draw dragging item (if any)
        if self.dragging_item and not self.edit_mode:
            mouse_pos = pygame.mouse.get_pos()
            self.draw_dragging_item(screen, mouse_pos)
        
        # Draw edit mode instructions
        if self.edit_mode:
            instructions = [
                "EDIT MODE: Drag boxes/figure to reposition",
                "Click 'SAVE LAYOUT' when done"
            ]
            for i, instruction in enumerate(instructions):
                inst_text = self.small_font.render(instruction, True, YELLOW)
                screen.blit(inst_text, (self.panel_rect.x + 20, self.panel_rect.bottom - 60 + i * 20))
        else:
            # Draw close instruction
            close_text = self.small_font.render("Click outside to close | Drag items to move them", True, GRAY)
            screen.blit(close_text, (self.panel_rect.x + 20, self.panel_rect.bottom - 30))
    
    def draw_paper_doll(self, screen):
        """Draw simple stick figure"""
        base_x = self.panel_rect.x
        base_y = self.panel_rect.y
        center_x = base_x + self.stick_figure_pos[0]
        center_y = base_y + self.stick_figure_pos[1]
        
        # Draw bounding box in edit mode (smaller clickable area)
        if self.edit_mode:
            click_bbox = pygame.Rect(center_x - 20, center_y - 60, 40, 80)
            pygame.draw.rect(screen, YELLOW if self.dragging_stick_figure else BLUE, click_bbox, 2)
            # Also draw the full figure outline in a different color
            full_bbox = pygame.Rect(center_x - 40, center_y - 100, 80, 180)
            pygame.draw.rect(screen, GRAY, full_bbox, 1)
        
        # Head (circle)
        pygame.draw.circle(screen, GRAY, (center_x, center_y - 80), 12, 2)
        
        # Body (vertical line)
        pygame.draw.line(screen, GRAY, (center_x, center_y - 68), (center_x, center_y + 20), 2)
        
        # Arms (horizontal line)
        pygame.draw.line(screen, GRAY, (center_x - 35, center_y - 50), (center_x + 35, center_y - 50), 2)
        
        # Legs (two lines)
        pygame.draw.line(screen, GRAY, (center_x, center_y + 20), (center_x - 20, center_y + 80), 2)
        pygame.draw.line(screen, GRAY, (center_x, center_y + 20), (center_x + 20, center_y + 80), 2)
    
    def draw_equipment_panel(self, screen, character):
        """Draw equipment panel on the left side"""
        base_x = self.panel_rect.x
        base_y = self.panel_rect.y
        
        # Draw character stats
        stats_y = base_y + 80
        stats = [
            f"HP: {character.health}/{character.max_health}",
            f"SP: {character.stamina}/{character.max_stamina}",
            f"MP: {character.mana}/{character.max_mana}",
            f"STR: {character.strength}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.small_font.render(stat, True, WHITE)
            screen.blit(stat_text, (base_x + 20, stats_y + i * 20))
        
        # Draw paper doll figure
        self.draw_paper_doll(screen)
        
        # Draw equipment slots
        self.draw_equipment_slots(screen, character)
    
    def draw_inventory_panel(self, screen, character):
        """Draw inventory panel on the right side"""
        base_x = self.panel_rect.x
        base_y = self.panel_rect.y
        
        inventory_size = character.get_inventory_size()
        
        # Draw inventory info
        info_y = base_y + 80
        info_lines = [
            f"Slots: {inventory_size} (20+STR*2)",
            f"Used: {len(character.inventory)}/{inventory_size}"
        ]
        
        for i, line in enumerate(info_lines):
            info_text = self.small_font.render(line, True, WHITE)
            screen.blit(info_text, (base_x + self.inventory_panel_x + 10, info_y + i * 20))
        
        # Draw inventory grid
        cols = 6
        slot_size = 45
        padding = 5
        start_x = base_x + self.inventory_panel_x + 10
        start_y = base_y + 120
        
        for i in range(inventory_size):
            row = i // cols
            col = i % cols
            
            x = start_x + col * (slot_size + padding)
            y = start_y + row * (slot_size + padding)
            
            # Check if within panel bounds
            if y + slot_size > self.panel_rect.bottom - 40:
                break
            
            slot_rect = pygame.Rect(x, y, slot_size, slot_size)
            
            # Check if slot has an item
            has_item = i < len(character.inventory)
            
            # Don't draw the item being dragged
            if has_item and self.dragging_item and self.dragging_source == 'inventory' and self.dragging_source_slot == i:
                has_item = False
            
            color = GREEN if has_item else DARK_GRAY
            
            pygame.draw.rect(screen, color, slot_rect)
            pygame.draw.rect(screen, WHITE, slot_rect, 1)
            
            # Draw item name if present
            if has_item:
                item = character.inventory[i]
                item_text = self.small_font.render(str(item)[:5], True, BLACK)
                item_rect = item_text.get_rect(center=slot_rect.center)
                screen.blit(item_text, item_rect)
    
    def draw_dragging_item(self, screen, pos):
        """Draw the item currently being dragged"""
        if not self.dragging_item:
            return
        
        # Draw semi-transparent box with item name
        box_size = 50
        box_rect = pygame.Rect(pos[0] - box_size // 2, pos[1] - box_size // 2, box_size, box_size)
        
        # Draw with transparency
        temp_surf = pygame.Surface((box_size, box_size))
        temp_surf.fill(YELLOW)
        temp_surf.set_alpha(180)
        screen.blit(temp_surf, box_rect)
        
        pygame.draw.rect(screen, WHITE, box_rect, 2)
        
        # Draw item name
        item_text = self.small_font.render(str(self.dragging_item)[:5], True, BLACK)
        item_rect = item_text.get_rect(center=box_rect.center)
        screen.blit(item_text, item_rect)
    
    def draw_equipment_slots(self, screen, character):
        """Draw all equipment slots"""
        base_x = self.panel_rect.x
        base_y = self.panel_rect.y
        
        for slot_name, (slot_x, slot_y) in self.equipment_slots.items():
            # Draw slot box
            slot_rect = pygame.Rect(
                base_x + slot_x,
                base_y + slot_y,
                self.slot_size,
                self.slot_size
            )
            
            # Color based on mode and state
            if self.edit_mode:
                if self.dragging_slot == slot_name:
                    color = YELLOW
                else:
                    color = BLUE
            else:
                # Color based on whether item is equipped
                item = character.equipment.get(slot_name)
                color = GREEN if item else DARK_GRAY
            
            pygame.draw.rect(screen, color, slot_rect)
            pygame.draw.rect(screen, WHITE, slot_rect, 2)
            
            # Draw slot label
            label = slot_name.replace('_', ' ').title()
            label_text = self.small_font.render(label, True, WHITE)
            label_rect = label_text.get_rect(center=(slot_rect.centerx, slot_rect.bottom + 12))
            screen.blit(label_text, label_rect)
            
            # Draw item name if equipped (and not in edit mode or being dragged)
            if not self.edit_mode:
                item = character.equipment.get(slot_name)
                # Don't draw if it's being dragged
                if item and not (self.dragging_item and self.dragging_source == 'equipment' and self.dragging_source_slot == slot_name):
                    item_text = self.small_font.render(item[:6], True, BLACK)
                    item_rect = item_text.get_rect(center=slot_rect.center)
                    screen.blit(item_text, item_rect)
