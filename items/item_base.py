import pygame
from core.settings import *

class Item:
    def __init__(self, name, description, icon_path=None, stackable=True, max_stack=99):
        self.name = name
        self.description = description
        self.icon_path = icon_path
        self.icon = None
        self.stackable = stackable
        self.max_stack = max_stack if stackable else 1
        self.quantity = 1

    def load_icon(self, asset_manager):
        if self.icon_path and asset_manager:
            try:
                self.icon = asset_manager.get_image(self.icon_path)

                if self.icon:
                    self.icon = pygame.transform.scale(self.icon, (48, 48))
            except Exception as e:
                print(f"Erro ao carregar ícone do item {self.name}: {e}")

    def use(self, player):

        return False

    def can_stack_with(self, other_item):
        if not self.stackable or not other_item.stackable:
            return False
        return self.name == other_item.name

    def add_quantity(self, amount):
        if not self.stackable:
            return amount

        space_available = self.max_stack - self.quantity
        if amount <= space_available:
            self.quantity += amount
            return 0
        else:
            self.quantity = self.max_stack
            return amount - space_available

class AmmoItem(Item):
    def __init__(self, ammo_type="pistol", ammo_count=15):
        super().__init__(
            name=f"Munição de {ammo_type.title()}",
            description=f"Um pente com {ammo_count} balas",
            icon_path="assets/images/tds-modern-hero-weapons-and-props/Ammo/Ammo.png",
            stackable=True,
            max_stack=10
        )
        self.ammo_type = ammo_type
        self.ammo_count = ammo_count

    def use(self, player):
        if hasattr(player, 'reserve_ammo'):
            player.reserve_ammo += self.ammo_count
            self.quantity -= 1
            print(f"Adicionadas {self.ammo_count} balas à reserva")
            return True
        return False

class MaskItem(Item):
    def __init__(self):
        super().__init__(
            name="Máscara Reforçada",
            description="Protege contra radiação por 30 segundos",
            icon_path="assets/images/tds-modern-hero-weapons-and-props/Props/Mask.png",
            stackable=True,
            max_stack=5
        )
        self.buff_duration = 30.0

    def use(self, player):
        if hasattr(player, 'apply_mask_buff'):
            player.apply_mask_buff(self.buff_duration)
            self.quantity -= 1
            print(f"Máscara ativada por {self.buff_duration} segundos")
            return True
        return False

class HealthPackItem(Item):
    def __init__(self):
        super().__init__(
            name="Kit Médico",
            description="Restaura 50 pontos de vida",
            icon_path="assets/images/tds-modern-hero-weapons-and-props/Props/MedKit.png",
            stackable=True,
            max_stack=10
        )
        self.heal_amount = 50

    def use(self, player):
        if hasattr(player, 'health') and hasattr(player, 'max_health'):
            if player.health < player.max_health:
                old_health = player.health
                player.health = min(player.health + self.heal_amount, player.max_health)
                healed = player.health - old_health
                self.quantity -= 1
                print(f"Curado {healed} pontos de vida")
                return True
        return False

class FilterModuleItem(Item):
    def __init__(self):
        super().__init__(
            name="Módulo de Filtro",
            description="Componente especial para melhorar a máscara",
            icon_path="assets/images/tds-modern-hero-weapons-and-props/Props/Filter.png",
            stackable=True,
            max_stack=3
        )

    def use(self, player):
        if hasattr(player, 'collect_filter_module'):
            player.collect_filter_module()
            self.quantity -= 1
            print("Módulo de filtro ativado!")
            return True
        return False
