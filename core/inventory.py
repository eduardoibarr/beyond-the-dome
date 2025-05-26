import pygame
from core.settings import *
from items.item_base import Item

class Inventory:
    def __init__(self, size=20):
        self.size = size
        self.slots = [None] * size
        self.selected_slot = 0

    def add_item(self, item):
        if not isinstance(item, Item):
            return False

        if item.stackable:
            for i, slot_item in enumerate(self.slots):
                if slot_item and slot_item.can_stack_with(item):
                    overflow = slot_item.add_quantity(item.quantity)
                    if overflow == 0:
                        return True
                    else:

                        item.quantity = overflow

        for i, slot_item in enumerate(self.slots):
            if slot_item is None:
                self.slots[i] = item
                return True

        return False

    def remove_item(self, slot_index, quantity=1):
        if 0 <= slot_index < self.size and self.slots[slot_index]:
            item = self.slots[slot_index]
            if item.quantity > quantity:
                item.quantity -= quantity

                removed_item = type(item)()
                removed_item.quantity = quantity
                return removed_item
            else:

                self.slots[slot_index] = None
                return item
        return None

    def use_item(self, slot_index, player):
        if 0 <= slot_index < self.size and self.slots[slot_index]:
            item = self.slots[slot_index]
            if item.use(player):
                if item.quantity <= 0:
                    self.slots[slot_index] = None
                return True
        return False

    def get_item(self, slot_index):
        if 0 <= slot_index < self.size:
            return self.slots[slot_index]
        return None

    def swap_items(self, slot1, slot2):
        if 0 <= slot1 < self.size and 0 <= slot2 < self.size:
            self.slots[slot1], self.slots[slot2] = self.slots[slot2], self.slots[slot1]

    def count_item(self, item_name):
        count = 0
        for item in self.slots:
            if item and item.name == item_name:
                count += item.quantity
        return count

    def has_space(self):
        return None in self.slots

class InventoryUI:
    def __init__(self, game, inventory):
        self.game = game
        self.inventory = inventory
        self.visible = False

        self.slot_size = 60
        self.slot_padding = 12
        self.cols = 5
        self.rows = 4

        self.window_width = self.cols * (self.slot_size + self.slot_padding) + self.slot_padding * 2
        self.window_height = self.rows * (self.slot_size + self.slot_padding) + 150
        self.window_x = (WIDTH - self.window_width) // 2
        self.window_y = (HEIGHT - self.window_height) // 2

        self.load_ui_images()

        self.title_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)


    def load_ui_images(self):
        if hasattr(self.game, 'asset_manager'):
            self.cell_image = self.game.asset_manager.get_image(
                "assets/images/tds-modern-gui-pixel-art/PNG/Inventory and Stats/Inventory Cell.png"
            )
            if self.cell_image:
                self.cell_image = pygame.transform.scale(self.cell_image, (self.slot_size, self.slot_size))

            self.bg_image = self.game.asset_manager.get_image(
                "assets/images/tds-modern-gui-pixel-art/PNG/Inventory and Stats/Inventory Stats.png"
            )

    def toggle(self):
        self.visible = not self.visible

    def draw(self, screen):
        if not self.visible:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        main_bg = pygame.Surface((self.window_width, self.window_height))
        main_bg.fill((40, 40, 50))
        screen.blit(main_bg, (self.window_x, self.window_y))
        
        pygame.draw.rect(screen, (100, 100, 120), 
                        (self.window_x, self.window_y, self.window_width, self.window_height), 3)

        title_text = self.title_font.render("INVENTÁRIO", True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=self.window_x + self.window_width // 2,
                                        y=self.window_y + 15)
        screen.blit(title_text, title_rect)

        line_y = self.window_y + 45
        pygame.draw.line(screen, (100, 100, 120), 
                        (self.window_x + 20, line_y), 
                        (self.window_x + self.window_width - 20, line_y), 2)

        slots_start_y = self.window_y + 60
        for i in range(self.inventory.size):
            row = i // self.cols
            col = i % self.cols

            x = self.window_x + self.slot_padding * 2 + col * (self.slot_size + self.slot_padding)
            y = slots_start_y + row * (self.slot_size + self.slot_padding)

            slot_color = (60, 60, 70) if self.inventory.get_item(i) else (30, 30, 40)
            pygame.draw.rect(screen, slot_color, (x, y, self.slot_size, self.slot_size))
            
            border_color = (255, 215, 0) if i == self.inventory.selected_slot else (80, 80, 90)
            border_width = 3 if i == self.inventory.selected_slot else 1
            pygame.draw.rect(screen, border_color, (x, y, self.slot_size, self.slot_size), border_width)

            item = self.inventory.get_item(i)
            if item:
                if item.icon:
                    icon_rect = item.icon.get_rect(center=(x + self.slot_size // 2,
                                                          y + self.slot_size // 2))
                    screen.blit(item.icon, icon_rect)
                else:
                    item_rect = pygame.Rect(x + 10, y + 10, self.slot_size - 20, self.slot_size - 20)
                    pygame.draw.rect(screen, (0, 200, 100), item_rect)
                    pygame.draw.rect(screen, (255, 255, 255), item_rect, 2)

                if item.stackable and item.quantity > 1:
                    qty_bg = pygame.Surface((20, 16))
                    qty_bg.fill((0, 0, 0))
                    qty_bg.set_alpha(180)
                    screen.blit(qty_bg, (x + self.slot_size - 22, y + self.slot_size - 18))
                    
                    qty_text = self.small_font.render(str(item.quantity), True, (255, 255, 255))
                    qty_rect = qty_text.get_rect(center=(x + self.slot_size - 12, y + self.slot_size - 10))
                    screen.blit(qty_text, qty_rect)

        selected_item = self.inventory.get_item(self.inventory.selected_slot)
        if selected_item:
            info_bg_y = self.window_y + self.window_height - 90
            info_bg_height = 70
            
            pygame.draw.rect(screen, (50, 50, 60), 
                           (self.window_x + 10, info_bg_y, self.window_width - 20, info_bg_height))
            pygame.draw.rect(screen, (100, 100, 120), 
                           (self.window_x + 10, info_bg_y, self.window_width - 20, info_bg_height), 2)

            name_text = self.font.render(selected_item.name, True, (255, 255, 255))
            name_rect = name_text.get_rect(centerx=self.window_x + self.window_width // 2,
                                          y=info_bg_y + 8)
            screen.blit(name_text, name_rect)

            desc_text = self.small_font.render(selected_item.description, True, (200, 200, 200))
            desc_rect = desc_text.get_rect(centerx=self.window_x + self.window_width // 2,
                                          y=info_bg_y + 28)
            screen.blit(desc_text, desc_rect)

            use_text = self.small_font.render("Pressione E para usar", True, (100, 255, 100))
            use_rect = use_text.get_rect(centerx=self.window_x + self.window_width // 2,
                                        y=info_bg_y + 48)
            screen.blit(use_text, use_rect)

        close_text = self.small_font.render("Pressione TAB para fechar", True, (255, 215, 0))
        close_rect = close_text.get_rect(centerx=self.window_x + self.window_width // 2,
                                        y=self.window_y + self.window_height - 15)
        screen.blit(close_text, close_rect)


    def handle_input(self, event):
        if not self.visible:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.inventory.use_item(self.inventory.selected_slot, self.game.player)
            elif event.key == pygame.K_LEFT:
                self.inventory.selected_slot = (self.inventory.selected_slot - 1) % self.inventory.size
            elif event.key == pygame.K_RIGHT:
                self.inventory.selected_slot = (self.inventory.selected_slot + 1) % self.inventory.size
            elif event.key == pygame.K_UP:
                self.inventory.selected_slot = (self.inventory.selected_slot - self.cols) % self.inventory.size
            elif event.key == pygame.K_DOWN:
                self.inventory.selected_slot = (self.inventory.selected_slot + self.cols) % self.inventory.size
