import pygame
from core.settings import *
from graphics.sprites.enemy_base import Enemy
from core.ai.ai import AIController, AIState

class FriendlyScavengerAI(AIController):
    """Controlador de IA específico para o Saqueador Amigável.
    
    Diferente dos outros inimigos, este não ataca o jogador inicialmente.
    Só se torna hostil se receber dano do jogador.
    """
    def __init__(self, enemy_sprite):
        super().__init__(enemy_sprite)
        # Inicia em estado IDLE ao invés de PATROL
        self.state = AIState.IDLE
        
        # Estado de interação 
        self.interaction_state = "GREETING"  # GREETING, PROPOSAL, ACCEPT, REFUSE, POST_TRADE
        self.trade_completed = False
        
        # Mantém o registro de se já se tornou hostil
        self.has_become_hostile = False
        
        # Diálogo
        self.dialogue = {
            "greeting": "Ei, calma! Não atire! Estou só tentando sobreviver como você.",
            "proposal": "Tenho uma máscara reforçada aqui. Posso trocar por um pente de munição. Topa? [Y]es / [N]o",
            "accept_trade": "Ótimo negócio! Aqui está sua máscara. Esta munição vai me ajudar bastante.",
            "refuse_trade": "Tudo bem, entendo. Boa sorte lá fora.",
            "hostile_trigger": "Ei! Por que fez isso?!",
            "post_trade": "Já negociamos. Siga seu caminho.",
            "no_ammo": "Você não tem munição suficiente, volte quando tiver um pente completo."
        }
        self.current_dialogue = ""
        
    def update(self, dt):
        """Atualiza a lógica de IA do Saqueador Amigável.
        
        Diferente dos outros inimigos, este permanece estático e não persegue
        o jogador até se tornar hostil.
        """
        # Se já está hostil, usa comportamento normal de IA
        if self.state == AIState.CHASE or self.state == AIState.ATTACK or self.has_become_hostile:
            return super().update(dt)
        
        # Caso contrário, permanece no lugar
        self.enemy.velocity = pygame.math.Vector2(0, 0)
        
        # Verifica distância para o jogador (para diálogo)
        player_pos = pygame.math.Vector2(self.game.player.position)
        enemy_pos = pygame.math.Vector2(self.enemy.position)
        distance_to_player = enemy_pos.distance_to(player_pos)
        
        # Define o diálogo apenas quando o jogador está próximo
        interaction_distance = TILE_SIZE * 3
        if distance_to_player < interaction_distance:
            if self.interaction_state == "GREETING":
                self.current_dialogue = self.dialogue["greeting"]
            elif self.interaction_state == "PROPOSAL":
                self.current_dialogue = self.dialogue["proposal"]
            elif self.interaction_state == "ACCEPT":
                self.current_dialogue = self.dialogue["accept_trade"]
            elif self.interaction_state == "REFUSE":
                self.current_dialogue = self.dialogue["refuse_trade"]
            elif self.interaction_state == "POST_TRADE":
                self.current_dialogue = self.dialogue["post_trade"]
            elif self.interaction_state == "NO_AMMO":
                self.current_dialogue = self.dialogue["no_ammo"]
        else:
            # Limpa diálogo quando jogador se afasta
            self.current_dialogue = ""
        
        # Sem ataque
        return False
        
    def alert_damage(self, source_pos):
        """Reage quando o saqueador amigável sofre dano, tornando-se hostil."""
        if not self.has_become_hostile:
            self.has_become_hostile = True
            self.state = AIState.CHASE
            self.last_known_player_pos = pygame.math.Vector2(source_pos)
            self.target_position = self.last_known_player_pos
            self.current_dialogue = self.dialogue["hostile_trigger"]
            # Muda o estado de interação
            self.interaction_state = "HOSTILE"
            
    def advance_dialogue(self):
        """Avança para o próximo estado de diálogo."""
        if self.has_become_hostile:
            return
            
        if self.interaction_state == "GREETING":
            self.interaction_state = "PROPOSAL"
        elif self.interaction_state == "NO_AMMO":
            self.interaction_state = "PROPOSAL"
        
    def accept_proposal(self):
        """Aceita a proposta de troca."""
        if self.interaction_state == "PROPOSAL" and not self.has_become_hostile:
            player = self.game.player
            
            # Munição necessária para a troca (um pente completo)
            ammo_needed = PISTOL_MAGAZINE_SIZE
            has_enough_ammo = False
            
            # Verifica se o jogador tem munição de reserva suficiente
            if hasattr(player, 'reserve_ammo'):
                has_enough_ammo = player.reserve_ammo >= ammo_needed
            
            if has_enough_ammo:
                # Remove a munição da reserva do jogador
                player.reserve_ammo -= ammo_needed
                
                # Aplica o buff da máscara diretamente ao jogador
                if hasattr(player, 'apply_mask_buff'):
                    # O buff de máscara dura 60 segundos
                    player.apply_mask_buff(30)  # Em segundos
                
                # Confirma a troca
                self.interaction_state = "ACCEPT"
                self.trade_completed = True
            else:
                # Jogador não tem munição suficiente
                self.interaction_state = "NO_AMMO"
            
    def refuse_proposal(self):
        """Recusa a proposta de troca."""
        if self.interaction_state == "PROPOSAL" and not self.has_become_hostile:
            self.interaction_state = "REFUSE"


class FriendlyScavenger(Enemy):
    """Implementação de um Saqueador Amigável, que não ataca o jogador.
    
    Características:
    - Coloração azul para indicar que é amigável
    - Não ataca o jogador a menos que seja atacado
    - Oferece diálogo e opções de troca quando o jogador interage
    """
    def __init__(self, game, x_pixel, y_pixel):
        """Inicializa um novo Saqueador Amigável no jogo.
        
        Args:
            game: Referência ao objeto principal do jogo
            x_pixel (int): Posição X inicial em pixels
            y_pixel (int): Posição Y inicial em pixels
        """
        # Inicializa a classe base Enemy
        super().__init__(game, x_pixel, y_pixel, (game.all_sprites, game.enemies))
        
        # Atributos específicos para o Saqueador Amigável
        self.health = ENEMY_RAIDER_HEALTH
        self.max_health = ENEMY_RAIDER_HEALTH 
        self.damage = ENEMY_RAIDER_DAMAGE
        self.speed = ENEMY_RAIDER_SPEED * TILE_SIZE
        
        # Cor azul para indicar que é amigável
        self.friendly_color = BLUE
        
        # Configuração visual
        if not self.setup_animations('raider'):  # Usa as mesmas animações do raider comum
            # Fallback para superfície azul
            self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
            self.image.fill(self.friendly_color)
            self.rect = self.image.get_rect(center=self.position)
        
        # Inicializa o controlador de IA específico
        self.ai_controller = FriendlyScavengerAI(self)
        self.ai_controller.game = game
        
        # Guarda o estado das teclas pressionadas no frame anterior
        self.previous_keys = {
            pygame.K_e: False,
            pygame.K_y: False,
            pygame.K_n: False
        }
        
    def take_damage(self, amount, source="player"):
        """Sobrescreve o método take_damage para tornar-se hostil quando atacado pelo jogador."""
        # Passa a informação ao controlador de IA
        player_pos = self.game.player.position
        self.ai_controller.alert_damage(player_pos)
        
        # Chama o método da classe base para aplicar o dano normalmente
        super().take_damage(amount)
        
    def attack(self):
        """Executa o ataque do Saqueador Amigável (só acontece se já estiver hostil)."""
        # Só ataca se já se tornou hostil
        if self.ai_controller.has_become_hostile:
            # Evita reativar o ataque durante a animação atual
            if self.current_animation == ANIM_ENEMY_SLASH:
                return

            # Inicia a animação de ataque
            self.set_animation(ANIM_ENEMY_SLASH)
            
            # Reproduz o efeito sonoro do ataque
            if hasattr(self.game, 'asset_manager'):
                self.game.asset_manager.play_sound('raider_attack')

            # Configuração da Hitbox do Ataque
            hitbox_offset = TILE_SIZE * 0.6  # Distância do centro do sprite
            hitbox_width = TILE_SIZE * 0.8   # Largura da área de ataque
            hitbox_height = self.rect.height * 0.9  # Altura da área de ataque
            
            # Ajusta a posição da hitbox baseado na direção do sprite
            if self.facing_right:
                hitbox_center_x = self.rect.centerx + hitbox_offset
            else:
                hitbox_center_x = self.rect.centerx - hitbox_offset
            hitbox_center_y = self.rect.centery
            
            # Cria e posiciona a hitbox do ataque
            attack_hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
            attack_hitbox.center = (hitbox_center_x, hitbox_center_y)

            # Verifica colisão com o jogador e aplica dano
            if attack_hitbox.colliderect(self.game.player.rect):
                self.game.player.take_damage(self.damage)
    
    def draw(self, screen, camera):
        """Sobrescreve o método de desenho para incluir balão de diálogo."""
        # Chama o método draw da classe base
        super().draw(screen, camera)
        
        # Exibe o diálogo se houver texto
        if self.ai_controller.current_dialogue:
            # Configura fonte para o diálogo
            font = pygame.font.Font(None, 22)
            
            # Renderiza o texto
            text_surface = font.render(self.ai_controller.current_dialogue, True, WHITE)
            text_rect = text_surface.get_rect()
            
            # Posiciona acima do inimigo
            dialogue_x = self.rect.centerx - text_rect.width // 2
            dialogue_y = self.rect.top - text_rect.height - 10
            dialogue_pos = camera.apply_coords(dialogue_x, dialogue_y)
            
            # Adiciona fundo para o texto
            padding = 5
            bg_rect = pygame.Rect(
                dialogue_pos[0] - padding, 
                dialogue_pos[1] - padding,
                text_rect.width + padding * 2, 
                text_rect.height + padding * 2
            )
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(screen, self.friendly_color, bg_rect, 2)
            
            # Desenha o texto
            screen.blit(text_surface, dialogue_pos)
    
    def update(self, dt):
        """Atualiza o estado do Saqueador Amigável."""
        # Atualiza usando o método da classe base
        super().update(dt)
        
        # Processa entrada de teclado para interação com o diálogo
        current_keys = pygame.key.get_pressed()
        
        # Verifica distância para o jogador
        player_pos = pygame.math.Vector2(self.game.player.position)
        enemy_pos = pygame.math.Vector2(self.position)
        distance_to_player = enemy_pos.distance_to(player_pos)
        
        # Só processa interação se o jogador estiver próximo
        interaction_distance = TILE_SIZE * 3
        if distance_to_player < interaction_distance:
            # Tecla E para avançar o diálogo - detecta quando a tecla foi pressionada
            if current_keys[pygame.K_e] and not self.previous_keys[pygame.K_e]:
                self.ai_controller.advance_dialogue()
            
            # Tecla Y para aceitar a proposta
            if current_keys[pygame.K_y] and not self.previous_keys[pygame.K_y] and self.ai_controller.interaction_state == "PROPOSAL":
                self.ai_controller.accept_proposal()
            
            # Tecla N para recusar a proposta
            if current_keys[pygame.K_n] and not self.previous_keys[pygame.K_n] and self.ai_controller.interaction_state == "PROPOSAL":
                self.ai_controller.refuse_proposal()
                
        # Atualiza o estado das teclas para o próximo frame
        self.previous_keys[pygame.K_e] = current_keys[pygame.K_e]
        self.previous_keys[pygame.K_y] = current_keys[pygame.K_y]
        self.previous_keys[pygame.K_n] = current_keys[pygame.K_n] 