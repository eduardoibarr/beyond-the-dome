import pygame
from core.settings import *
from core.mission_system import MissionStatus

class MissionUI:

    def __init__(self, game, mission_system):
        self.game = game
        self.mission_system = mission_system
        self.visible = True
        self.expanded = False

        self.panel_width = 350
        self.panel_height = 200
        self.panel_x = WIDTH - self.panel_width - 10
        self.panel_y = 10

        self.bg_color = (0, 0, 0, 240)
        self.border_color = (255, 255, 255, 255)
        self.title_color = (255, 255, 255)
        self.objective_color = (200, 200, 200)
        self.completed_color = (0, 255, 0)
        self.progress_bar_bg = (50, 50, 50)
        self.progress_bar_fill = (0, 150, 255)

        self.title_font = pygame.font.Font(None, 24)
        self.text_font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 16)

        self.notification_timer = 0
        self.notification_text = ""
        self.notification_color = WHITE

        # Track mission count to avoid debug spam
        self.last_mission_count = 0
        self.debug_cooldown = 0

        self.mission_system.register_callback('mission_started', self._on_mission_started)
        self.mission_system.register_callback('mission_completed', self._on_mission_completed)
        self.mission_system.register_callback('objective_completed', self._on_objective_completed)

    def _on_mission_started(self, mission):
        self.show_notification(f"Nova Missão: {mission.title}", (0, 255, 0))

    def _on_mission_completed(self, mission):
        self.show_notification(f"Missão Completada: {mission.title}", (255, 255, 0))

    def _on_objective_completed(self, mission, objective):
        self.show_notification(f"Objetivo Completado: {objective.description}", (0, 255, 255))

    def show_notification(self, text, color=(255, 255, 255), duration=3000):
        self.notification_text = text
        self.notification_color = color
        self.notification_timer = pygame.time.get_ticks() + duration

    def set_visible(self, visible):
        self.visible = visible

    def toggle_visibility(self):
        self.visible = not self.visible

    def toggle_expanded(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.panel_height = 400
        else:
            self.panel_height = 200
            
    def update(self, dt):
        if self.notification_timer > 0 and pygame.time.get_ticks() > self.notification_timer:
            self.notification_timer = 0
            self.notification_text = ""
        
        # Update debug cooldown
        if self.debug_cooldown > 0:
            self.debug_cooldown -= dt

    def draw(self, screen):
        if not self.visible:
            return
        
        active_missions = self.mission_system.get_active_missions()
        current_mission_count = len(active_missions)
        
        # Se não há missões ativas mas existe a missão tutorial não iniciada, force a inicialização
        if not active_missions and 'tutorial' in self.mission_system.missions:
            tutorial_mission = self.mission_system.missions['tutorial']
            if tutorial_mission.status == MissionStatus.NOT_STARTED:
                print("[DEBUG] Forçando início da missão tutorial via UI")
                self.mission_system.start_mission("tutorial")
                active_missions = self.mission_system.get_active_missions()
                current_mission_count = len(active_missions)
        
        # Only print debug info when mission count changes or on cooldown
        if (current_mission_count != self.last_mission_count or self.debug_cooldown <= 0):
            if current_mission_count > 0:
                print(f"[DEBUG] Exibindo {current_mission_count} missões ativas")
            else:
                print(f"[DEBUG] Nenhuma missão ativa")
            
            self.last_mission_count = current_mission_count
            self.debug_cooldown = 1000  # 1 second cooldown
        
        # Exibe as missões ativas
        if active_missions:
            self._draw_panel(screen, active_missions)
        
        # Exibe notificações se houver
        if self.notification_text and self.visible:
            self._draw_notifications(screen)

    def _draw_panel(self, surface, active_missions):            
        if self.expanded:
            panel_height = min(self.panel_height, 50 + len(active_missions) * 120)
        else:
            panel_height = min(self.panel_height, 50 + len(active_missions) * 80)

        panel_surface = pygame.Surface((self.panel_width, panel_height))
        panel_surface.fill((40, 40, 40))

        pygame.draw.rect(panel_surface, (255, 255, 255), (0, 0, self.panel_width, panel_height), 3)

        title_bg = pygame.Surface((self.panel_width, 30))
        title_bg.fill((60, 60, 80))
        panel_surface.blit(title_bg, (0, 0))

        title_text = self.title_font.render("MISSÕES ATIVAS", True, (255, 255, 255))
        panel_surface.blit(title_text, (10, 5))

        expand_text = "[-]" if self.expanded else "[+]"
        expand_surface = self.small_font.render(expand_text, True, (255, 255, 255))
        panel_surface.blit(expand_surface, (self.panel_width - 30, 5))

        y_offset = 40
        
        for mission in active_missions:
            y_offset += self._draw_mission(panel_surface, mission, y_offset)

        surface.blit(panel_surface, (self.panel_x, self.panel_y))

    def _draw_mission(self, surface, mission, y_offset):
        start_y = y_offset

        mission_title = self.text_font.render(mission.title, True, (255, 255, 255))
        surface.blit(mission_title, (10, y_offset))
        y_offset += 25

        progress = mission.get_progress_percentage()
        bar_width = self.panel_width - 40
        bar_height = 8

        pygame.draw.rect(surface, (80, 80, 80), (10, y_offset, bar_width, bar_height))

        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(surface, (0, 150, 255), (10, y_offset, fill_width, bar_height))

        progress_text = f"{int(progress * 100)}%"
        progress_surface = self.small_font.render(progress_text, True, (255, 255, 255))
        surface.blit(progress_surface, (bar_width - 20, y_offset - 2))

        y_offset += 15

        if self.expanded:
            for objective in mission.objectives:
                obj_text = objective.get_progress_text()
                obj_color = (0, 255, 0) if objective.completed else (200, 200, 200)
                
                if len(obj_text) > 40:
                    obj_text = obj_text[:37] + "..."

                obj_surface = self.small_font.render(obj_text, True, obj_color)
                surface.blit(obj_surface, (20, y_offset))
                y_offset += 18

        return y_offset - start_y + 10

    def _draw_notifications(self, screen):
        if not self.notification_text or self.notification_timer <= 0:
            return

        notification_width = 400
        notification_height = 60
        notification_x = (WIDTH - notification_width) // 2
        notification_y = 50

        time_left = self.notification_timer - pygame.time.get_ticks()
        if time_left < 500:
            alpha = int(255 * (time_left / 500))
        else:
            alpha = 255

        alpha = max(0, min(255, alpha))

        notification_surface = pygame.Surface((notification_width, notification_height), pygame.SRCALPHA)
        
        bg_color = (0, 0, 0, min(alpha, 200))
        notification_surface.fill(bg_color)

        if isinstance(self.notification_color, (list, tuple)) and len(self.notification_color) >= 3:
            border_color = (self.notification_color[0], self.notification_color[1], self.notification_color[2], alpha)
            text_color = (self.notification_color[0], self.notification_color[1], self.notification_color[2], alpha)
        else:
            border_color = (255, 255, 255, alpha)
            text_color = (255, 255, 255, alpha)

        pygame.draw.rect(notification_surface, border_color,
                        (0, 0, notification_width, notification_height), 3)

        text_surface = self.text_font.render(self.notification_text, True, text_color[:3])
        text_rect = text_surface.get_rect(center=(notification_width // 2, notification_height // 2))
        notification_surface.blit(text_surface, text_rect)

        screen.blit(notification_surface, (notification_x, notification_y))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.toggle_visibility()
            elif event.key == pygame.K_n:
                if self.visible:
                    self.toggle_expanded()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos

                expand_button_rect = pygame.Rect(
                    self.panel_x + self.panel_width - 30,
                    self.panel_y + 10,
                    20, 20
                )

                if expand_button_rect.collidepoint(mouse_x, mouse_y) and self.visible:
                    self.toggle_expanded()

class MissionJournal:

    def __init__(self, game, mission_system):
        self.game = game
        self.mission_system = mission_system
        self.visible = False
        self.selected_tab = "active"

        self.journal_width = 800
        self.journal_height = 600
        self.journal_x = (WIDTH - self.journal_width) // 2
        self.journal_y = (HEIGHT - self.journal_height) // 2

        self.bg_color = (20, 20, 30, 240)
        self.tab_active_color = (60, 60, 80)
        self.tab_inactive_color = (40, 40, 50)
        self.border_color = (100, 100, 120)

        self.title_font = pygame.font.Font(None, 32)
        self.tab_font = pygame.font.Font(None, 24)
        self.text_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)

        self.scroll_y = 0
        self.max_scroll = 0

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.scroll_y = 0

    def draw(self, screen):
        if not self.visible:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        journal_surface = pygame.Surface((self.journal_width, self.journal_height), pygame.SRCALPHA)
        journal_surface.fill(self.bg_color)
        pygame.draw.rect(journal_surface, self.border_color,
                        (0, 0, self.journal_width, self.journal_height), 3)

        title_text = self.title_font.render("DIÁRIO DE MISSÕES", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.journal_width // 2, y=20)
        journal_surface.blit(title_text, title_rect)

        self._draw_tabs(journal_surface)

        self._draw_missions_content(journal_surface)

        instructions = "ESC: Fechar | ↑↓: Scroll | Tab: Mudar aba"
        inst_surface = self.small_font.render(instructions, True, LIGHTGREY)
        journal_surface.blit(inst_surface, (10, self.journal_height - 25))

        screen.blit(journal_surface, (self.journal_x, self.journal_y))

    def _draw_tabs(self, surface):
        tabs = [
            ("active", "Ativas"),
            ("completed", "Completadas"),
            ("failed", "Falhadas"),
            ("all", "Todas")
        ]

        tab_width = self.journal_width // len(tabs)
        tab_height = 40

        for i, (tab_id, tab_name) in enumerate(tabs):
            tab_x = i * tab_width
            tab_y = 60

            if tab_id == self.selected_tab:
                tab_color = self.tab_active_color
                text_color = WHITE
            else:
                tab_color = self.tab_inactive_color
                text_color = LIGHTGREY

            pygame.draw.rect(surface, tab_color, (tab_x, tab_y, tab_width, tab_height))
            pygame.draw.rect(surface, self.border_color, (tab_x, tab_y, tab_width, tab_height), 1)

            tab_text = self.tab_font.render(tab_name, True, text_color)
            tab_rect = tab_text.get_rect(center=(tab_x + tab_width // 2, tab_y + tab_height // 2))
            surface.blit(tab_text, tab_rect)

    def _draw_missions_content(self, surface):

        content_y = 110
        content_height = self.journal_height - content_y - 40

        missions = self._get_missions_for_tab()

        if not missions:
            no_missions_text = "Nenhuma missão encontrada"
            text_surface = self.text_font.render(no_missions_text, True, LIGHTGREY)
            text_rect = text_surface.get_rect(center=(self.journal_width // 2, content_y + 50))
            surface.blit(text_surface, text_rect)
            return

        y_offset = content_y - self.scroll_y

        for mission in missions:
            if y_offset > self.journal_height:
                break
            if y_offset > content_y - 100:
                mission_height = self._draw_mission_detail(surface, mission, y_offset)
                y_offset += mission_height + 20

        total_height = len(missions) * 150
        self.max_scroll = max(0, total_height - content_height)

    def _get_missions_for_tab(self):
        all_missions = list(self.mission_system.missions.values())

        if self.selected_tab == "active":
            return [m for m in all_missions if m.status == MissionStatus.ACTIVE]
        elif self.selected_tab == "completed":
            return [m for m in all_missions if m.status == MissionStatus.COMPLETED]
        elif self.selected_tab == "failed":
            return [m for m in all_missions if m.status == MissionStatus.FAILED]
        else:
            return all_missions

    def _draw_mission_detail(self, surface, mission, y_offset):
        start_y = y_offset

        title_color = WHITE
        if mission.status == MissionStatus.COMPLETED:
            title_color = GREEN
        elif mission.status == MissionStatus.FAILED:
            title_color = RED

        title_surface = self.text_font.render(mission.title, True, title_color)
        surface.blit(title_surface, (20, y_offset))
        y_offset += 25

        desc_surface = self.small_font.render(mission.description, True, LIGHTGREY)
        surface.blit(desc_surface, (20, y_offset))
        y_offset += 20

        status_text = f"Status: {mission.status.value.replace('_', ' ').title()}"
        if mission.status == MissionStatus.ACTIVE:
            progress = mission.get_progress_percentage()
            status_text += f" ({int(progress * 100)}%)"

        status_surface = self.small_font.render(status_text, True, CYAN)
        surface.blit(status_surface, (20, y_offset))
        y_offset += 20

        for objective in mission.objectives:
            obj_text = f"  • {objective.get_progress_text()}"
            obj_color = GREEN if objective.completed else WHITE
            obj_surface = self.small_font.render(obj_text, True, obj_color)
            surface.blit(obj_surface, (30, y_offset))
            y_offset += 18

        return y_offset - start_y

    def handle_input(self, event):
        if not self.visible:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle()
            elif event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - 30)
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + 30)
            elif event.key == pygame.K_TAB:
                tabs = ["active", "completed", "failed", "all"]
                current_index = tabs.index(self.selected_tab)
                self.selected_tab = tabs[(current_index + 1) % len(tabs)]
                self.scroll_y = 0

        elif event.type == pygame.MOUSEWHEEL:
            if self.visible:
                self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - event.y * 30))
