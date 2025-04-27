# Importação das bibliotecas necessárias
import pygame
import sys
from settings import *
from sprites import Player, Raider, WildDog 

# Classe principal do jogo
class Game:
    def __init__(self):
        # Inicialização do Pygame e configuração da janela
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        # Configuração das fontes para HUD e tela de game over
        self.font = pygame.font.Font(FONT_NAME, HUD_FONT_SIZE)
        self.game_over_font = pygame.font.Font(FONT_NAME, GAME_OVER_FONT_SIZE)
        self.cause_of_death = None

    def new(self):
        # Inicialização dos grupos de sprites e criação dos personagens
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.stones = pygame.sprite.Group()
        self.player = Player(self, 10, 10) 
        # Criação dos inimigos iniciais
        Raider(self, 15, 5)
        WildDog(self, 5, 15)
        Raider(self, 20, 10)
        self.run()

    def run(self):
        # Loop principal do jogo
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def events(self):
        # Tratamento de eventos do jogo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def update(self):
        # Atualização do estado do jogo
        self.all_sprites.update()

        # Verificação de colisão com inimigos
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for hit in hits:
            self.player.take_damage(hit.damage)

        # Verificação de morte do jogador
        if self.player.health <= 0:
            self.playing = False
            self.cause_of_death = "enemy_collision"

    def draw_hud(self):
        # Cálculo da porcentagem de vida do jogador
        health_pct = max(0, self.player.health / PLAYER_HEALTH)

        # Configuração da barra de vida
        bar_x = HEALTH_BAR_X
        bar_y = HEALTH_BAR_Y
        bar_width = HEALTH_BAR_WIDTH
        bar_height = HEALTH_BAR_HEIGHT
        border_radius = 3
        border_thickness = 2

        # Cálculo da largura do preenchimento da barra
        fill_width = int(bar_width * health_pct)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)

        # Cálculo da cor da barra baseado na vida
        color_r = int(HEALTH_BAR_COLOR_MIN[0] + (HEALTH_BAR_COLOR_MAX[0] - HEALTH_BAR_COLOR_MIN[0]) * health_pct)
        color_g = int(HEALTH_BAR_COLOR_MIN[1] + (HEALTH_BAR_COLOR_MAX[1] - HEALTH_BAR_COLOR_MIN[1]) * health_pct)
        color_b = int(HEALTH_BAR_COLOR_MIN[2] + (HEALTH_BAR_COLOR_MAX[2] - HEALTH_BAR_COLOR_MIN[2]) * health_pct)
        current_color = (color_r, color_g, color_b)

        # Desenho da barra de vida
        border_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)

        pygame.draw.rect(self.screen, HEALTH_BAR_BACKGROUND_COLOR, border_rect, border_radius=border_radius)
        if fill_width > 0:
             pygame.draw.rect(self.screen, current_color, fill_rect, border_radius=border_radius)
        pygame.draw.rect(self.screen, HEALTH_BAR_BORDER_COLOR, border_rect, border_thickness, border_radius=border_radius)

        # Desenho do texto da vida
        health_text_surface = self.font.render(f"{int(health_pct * 100)}%", True, HUD_COLOR)
        text_x = bar_x + bar_width + 5
        text_y = bar_y + (bar_height - health_text_surface.get_height()) // 2
        self.screen.blit(health_text_surface, (text_x, text_y))
        
        # Desenho do contador de pedras
        stone_text = self.font.render(f"Pedras: {self.player.stone_count}", True, WHITE)
        stone_rect = stone_text.get_rect(topright=(WIDTH - 20, 20))
        self.screen.blit(stone_text, stone_rect)

    def draw(self):
        # Desenho de todos os elementos na tela
        self.screen.fill(DARKGREY)

        # Desenho dos sprites (exceto inimigos e jogador)
        for sprite in self.all_sprites:
            if sprite not in self.enemies and sprite != self.player:
                self.screen.blit(sprite.image, sprite.rect)
                
        # Desenho do jogador e sua arma
        self.screen.blit(self.player.image, self.player.rect)
        self.player.draw_weapon(self.screen)
        
        # Desenho dos inimigos
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        # Desenho do HUD e atualização da tela
        self.draw_hud()
        pygame.display.flip()

    def show_start_screen(self):
        # Tela inicial (ainda não implementada)
        pass

    def show_go_screen(self):
        # Tela de game over
        if not self.running:
             return

        self.screen.fill(BLACK)
        # Desenho do título da tela de game over
        title_text = self.game_over_font.render("Você morreu...", True, RED)
        title_rect = title_text.get_rect(center=(WIDTH / 2, HEIGHT / 3))
        self.screen.blit(title_text, title_rect)

        # Mensagem baseada na causa da morte
        if self.cause_of_death == "enemy_collision":
            message = "Os saqueadores e seus cães foram implacáveis."
        else:
            message = "Sua missão termina aqui."

        # Desenho da mensagem
        message_text = self.font.render(message, True, WHITE)
        message_rect = message_text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        self.screen.blit(message_text, message_rect)

        # Desenho da mensagem de reinício
        restart_text = self.font.render("Pressione qualquer tecla para tentar novamente", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH / 2, HEIGHT * 2 / 3))
        self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

        # Loop de espera por input do usuário
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False

# Inicialização e execução do jogo
g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pygame.quit()
sys.exit() 