import pygame
from core.game import Game
from graphics.ui.screens import show_start_screen, show_go_screen, display_intro

from core.mission_system import MissionSystem, ObjectiveType
from graphics.ui.mission_ui import MissionUI, MissionJournal
from graphics.explosion_system import ExplosionSystem
from core.ai.enhanced_ai import EnhancedRaiderAI, EnhancedWildDogAI, EnhancedFriendlyScavengerAI, EnhancedAIController

def integrate_enhanced_systems(game):
    game.mission_system = MissionSystem(game)
    game.mission_ui = MissionUI(game, game.mission_system)
    game.mission_journal = MissionJournal(game, game.mission_system)
    game.explosion_system = ExplosionSystem(game)

    original_new = game.new
    original_update = game.update
    original_draw = game.draw

    def enhanced_new():
        result = original_new()

        if hasattr(game, 'mission_system') and game.mission_system:
            if game.mission_system.start_mission("tutorial"):
                if hasattr(game, 'mission_ui'):
                    game.mission_ui.set_visible(True)
            else:
                print("[DEBUG] Falha ao iniciar missão tutorial!")

        if hasattr(game, 'enemies'):
            for enemy in game.enemies:
                enemy_class_name = enemy.__class__.__name__
                if "Raider" in enemy_class_name:
                    enemy.ai_controller = EnhancedRaiderAI(enemy)
                elif "WildDog" in enemy_class_name:
                    enemy.ai_controller = EnhancedWildDogAI(enemy)
                elif "FriendlyScavenger" in enemy_class_name:
                    enemy.ai_controller = EnhancedFriendlyScavengerAI(enemy)
                else:
                    enemy.ai_controller = EnhancedAIController(enemy)

        print("[ENHANCED] Sistemas integrados com sucesso!")
        return result

    def enhanced_update():
        result = original_update()

        game.explosion_system.update(game.dt)
        game.mission_ui.update(game.dt)

        return result

    def enhanced_draw():
        result = original_draw()

        if hasattr(game, 'camera'):
            game.explosion_system.draw(game.screen, game.camera)
        game.mission_ui.draw(game.screen)
        game.mission_journal.draw(game.screen)

        return result

    def enhanced_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.playing = False
                game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    if hasattr(game, 'mission_journal') and game.mission_journal.visible:
                        pass
                    elif hasattr(game, 'inventory_ui'):
                        game.inventory_ui.visible = not game.inventory_ui.visible
                
                elif event.key == pygame.K_i:
                    if hasattr(game, 'inventory_ui'):
                        game.inventory_ui.visible = not game.inventory_ui.visible
                
                elif event.key == pygame.K_j:
                    if hasattr(game, 'mission_journal'):
                        game.mission_journal.toggle()
                elif event.key == pygame.K_m:
                    if hasattr(game, 'mission_ui'):
                        game.mission_ui.toggle_visibility()
                elif event.key == pygame.K_g:
                    if hasattr(game, 'player') and hasattr(game, 'explosion_system'):
                        pos = game.player.position
                        game.explosion_system.create_explosion(pos.x + 100, pos.y, "grenade", 1.0)

            if hasattr(game, 'mission_journal'):
                game.mission_journal.handle_input(event)
            
            if hasattr(game, 'mission_ui'):
                game.mission_ui.handle_input(event)

            journal_is_visible = hasattr(game, 'mission_journal') and game.mission_journal.visible
            if hasattr(game, 'inventory_ui') and not journal_is_visible:
                game.inventory_ui.handle_input(event)

    game.new = enhanced_new
    game.update = enhanced_update
    game.draw = enhanced_draw
    game.events = enhanced_events

    def create_explosion(x, y, explosion_type="normal", intensity=1.0):
        return game.explosion_system.create_explosion(x, y, explosion_type, intensity)

    def trigger_mission_event(event_type, target, amount=1):
        objective_type = None
        if event_type == "kill":
            objective_type = ObjectiveType.KILL
        elif event_type == "collect":
            objective_type = ObjectiveType.COLLECT
        elif event_type == "reach":
            objective_type = ObjectiveType.REACH
        elif event_type == "interact":
            objective_type = ObjectiveType.INTERACT

        if objective_type:
            game.mission_system.update_objective(objective_type, target, amount)

    game.create_explosion = create_explosion
    game.trigger_mission_event = trigger_mission_event

if __name__ == '__main__':
    g = Game()
    integrate_enhanced_systems(g)

    while g.running:
        show_start_screen(g)
        if not g.running:
            break

        display_intro(g)
        if not g.running:
            break

        g.new()

        if g.running:
             show_go_screen(g)

    g.quit()
