import pygame
import math
from core.settings import *
from items.item_base import Item

class Collectible(pygame.sprite.Sprite):
    def __init__(self, game, x, y, item):
        self.groups = game.all_sprites, game.items
        super().__init__(self.groups)
        self.game = game
        self.item = item

        if hasattr(item, 'icon_path') and item.icon_path:
            try:
                self.image = game.asset_manager.get_image(item.icon_path)
                if self.image:
                    self.image = pygame.transform.scale(self.image, (ITEM_SIZE, ITEM_SIZE))
                else:
                    raise Exception("Imagem não encontrada")
            except Exception as e:
                print(f"Erro ao carregar imagem {item.icon_path}: {e}")
                # Criar imagem placeholder colorida
                self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE))
                self.image.fill(ITEM_COLOR)
        else:
            print(f"Item {item.name} não tem icon_path definido")
            # Criar imagem placeholder colorida
            self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE))
            self.image.fill(ITEM_COLOR)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.float_timer = 0
        self.base_y = y

    def update(self, dt):

        self.float_timer += dt * 2
        self.rect.centery = self.base_y + int(math.sin(self.float_timer) * 3)

        if self.rect.colliderect(self.game.player.rect):
            self.collect()

    def collect(self):
        if self.game.player.inventory.add_item(self.item):
            print(f"Coletado: {self.item.name}")

            if hasattr(self.game, 'trigger_mission_event'):
                item_type = self.item.name.lower()
                if "munição" in item_type or "ammo" in item_type:
                    self.game.trigger_mission_event("collect", "ammo", 1)
                elif "kit médico" in item_type or "health" in item_type:
                    self.game.trigger_mission_event("collect", "health_pack", 1)
                elif "filtro" in item_type or "filter" in item_type:
                    self.game.trigger_mission_event("collect", "filter_module", 1)
                elif "máscara" in item_type or "mask" in item_type:
                    self.game.trigger_mission_event("collect", "reinforced_mask", 1)

            self.kill()
        else:
            print("Inventário cheio!")
