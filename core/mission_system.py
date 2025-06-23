import pygame
from enum import Enum
from typing import Dict, List, Optional, Callable
import json
import os
import time

class MissionStatus(Enum):
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class ObjectiveType(Enum):
    COLLECT = "collect"
    KILL = "kill"
    REACH = "reach"
    SURVIVE = "survive"
    INTERACT = "interact"
    ESCORT = "escort"

class Objective:
    def __init__(self, obj_id: str, obj_type: ObjectiveType, description: str,
                 target: str = None, target_count: int = 1, current_count: int = 0):
        self.id = obj_id
        self.type = obj_type
        self.description = description
        self.target = target
        self.target_count = target_count
        self.current_count = current_count
        self.completed = False

    def update_progress(self, amount: int = 1) -> bool:
        if self.completed:
            return True

        self.current_count = min(self.current_count + amount, self.target_count)
        self.completed = self.current_count >= self.target_count
        return self.completed

    def get_progress_text(self) -> str:
        if self.completed:
            return f"✓ {self.description}"
        return f"{self.description} ({self.current_count}/{self.target_count})"

class Mission:
    def __init__(self, mission_id: str, title: str, description: str,
                 objectives: List[Objective], rewards: Dict = None):
        self.id = mission_id
        self.title = title
        self.description = description
        self.objectives = objectives
        self.rewards = rewards or {}
        self.status = MissionStatus.NOT_STARTED
        self.start_time = None
        self.completion_time = None

    def start(self) -> bool:
        if self.status == MissionStatus.NOT_STARTED:
            self.status = MissionStatus.ACTIVE
            self.start_time = time.time()
            return True
        return False

    def update_objective(self, objective_id: str, amount: int = 1) -> bool:
        if self.status != MissionStatus.ACTIVE:
            return False

        for objective in self.objectives:
            if objective.id == objective_id:
                objective.update_progress(amount)
                break

        if all(obj.completed for obj in self.objectives):
            self.status = MissionStatus.COMPLETED
            self.completion_time = pygame.time.get_ticks()
            return True

        return False

    def fail(self):
        if self.status == MissionStatus.ACTIVE:
            self.status = MissionStatus.FAILED

    def get_progress_percentage(self) -> float:
        if not self.objectives:
            return 0.0

        total_progress = sum(obj.current_count / obj.target_count for obj in self.objectives)
        return total_progress / len(self.objectives)

class MissionSystem:
    def __init__(self, game):
        self.game = game
        self.missions: Dict[str, Mission] = {}
        self.active_missions: List[str] = []
        self.completed_missions: List[str] = []
        self.failed_missions: List[str] = []
        
        # Rastreamento de objetivos já processados para evitar repetição
        self.processed_reach_objectives = set()

        self.mission_callbacks: Dict[str, List[Callable]] = {
            'mission_started': [],
            'mission_completed': [],
            'mission_failed': [],
            'objective_completed': []
        }

        self._load_missions()
        
        # Inicia automaticamente a missão tutorial se não há missões ativas
        if not self.active_missions and 'tutorial' not in self.completed_missions:
            print("[DEBUG] Iniciando missão tutorial automaticamente")
            self.start_mission("tutorial")

    def _load_missions(self):
        tutorial_objectives = [
            Objective("move", ObjectiveType.REACH, "Mova-se pelo mapa", "tutorial_area", 1),
            Objective("collect_ammo", ObjectiveType.COLLECT, "Colete munição", "ammo", 3),
            Objective("kill_dog", ObjectiveType.KILL, "Elimine um cão selvagem", "wild_dog", 1)
        ]
        tutorial_mission = Mission(
            "tutorial",
            "Primeiros Passos",
            "Aprenda os controles básicos e sobreviva aos primeiros perigos.",
            tutorial_objectives,
            {"experience": 100, "health_pack": 2}
        )

        supply_objectives = [
            Objective("collect_filters", ObjectiveType.COLLECT, "Colete módulos de filtro", "filter_module", 5),
            Objective("collect_health", ObjectiveType.COLLECT, "Colete kits médicos", "health_pack", 3),
            Objective("survive_radiation", ObjectiveType.SURVIVE, "Sobreviva em área radioativa por 60 segundos", "radiation_zone", 60)
        ]
        supply_mission = Mission(
            "supply_run",
            "Corrida de Suprimentos",
            "Colete suprimentos essenciais para a cidade Ômega-7.",
            supply_objectives,
            {"experience": 250, "reinforced_mask": 1}
        )

        combat_objectives = [
            Objective("kill_raiders", ObjectiveType.KILL, "Elimine saqueadores", "raider", 8),
            Objective("rescue_scavenger", ObjectiveType.ESCORT, "Escorte scavenger amigável", "friendly_scavenger", 1),
            Objective("reach_safe_zone", ObjectiveType.REACH, "Chegue à zona segura", "safe_zone", 1)
        ]
        combat_mission = Mission(
            "raider_conflict",
            "Conflito com Saqueadores",
            "Enfrente os saqueadores e proteja os sobreviventes.",
            combat_objectives,
            {"experience": 400, "ammo": 50, "grenade": 3}
        )

        exploration_objectives = [
            Objective("explore_factory", ObjectiveType.REACH, "Explore a fábrica abandonada", "factory_area", 1),
            Objective("collect_components", ObjectiveType.COLLECT, "Colete componentes industriais", "industrial_component", 10),
            Objective("activate_generator", ObjectiveType.INTERACT, "Ative o gerador principal", "main_generator", 1)
        ]
        exploration_mission = Mission(
            "industrial_exploration",
            "Exploração Industrial",
            "Investigue as ruínas industriais em busca de componentes valiosos.",
            exploration_objectives,
            {"experience": 350, "battery": 5, "filter_module": 3}
        )

        truth_objectives = [
            Objective("find_logs", ObjectiveType.COLLECT, "Encontre registros da IA", "ai_log", 5),
            Objective("reach_control_room", ObjectiveType.REACH, "Chegue à sala de controle", "control_room", 1),
            Objective("confront_ai", ObjectiveType.INTERACT, "Confronte a IA", "ai_terminal", 1)
        ]
        truth_mission = Mission(
            "truth_revelation",
            "A Verdade Revelada",
            "Descubra os segredos sombrios sobre a IA e o mundo exterior.",
            truth_objectives,
            {"experience": 500, "special_weapon": 1}
        )

        for mission in [tutorial_mission, supply_mission, combat_mission, exploration_mission, truth_mission]:
            self.missions[mission.id] = mission
            
            
    def start_mission(self, mission_id: str) -> bool:
        if mission_id not in self.missions:
            print(f"[DEBUG] Missão {mission_id} não encontrada!")
            return False

        mission = self.missions[mission_id]
        if mission.status != MissionStatus.NOT_STARTED:
            print(f"[DEBUG] Missão {mission_id} já foi iniciada (status: {mission.status})")
            return False

        if mission.start():
            if mission_id not in self.active_missions:
                self.active_missions.append(mission_id)
                print(f"[DEBUG] Missão {mission_id} iniciada com sucesso!")

            for callback in self.mission_callbacks['mission_started']:
                callback(mission)

            return True
        
        print(f"[DEBUG] Falha ao iniciar missão {mission_id}")
        return False
        
    def complete_mission(self, mission_id: str):
        if mission_id not in self.missions:
            print(f"[DEBUG] Missão {mission_id} não encontrada para completar")
            return

        mission = self.missions[mission_id]
        print(f"[DEBUG] Completando missão {mission_id} com status: {mission.status}")
        
        # Garante que a missão seja marcada como concluída
        mission.status = MissionStatus.COMPLETED
        
        if mission_id in self.active_missions:
            self.active_missions.remove(mission_id)
            print(f"[DEBUG] Removida missão {mission_id} das missões ativas")
            
        if mission_id not in self.completed_missions:
            self.completed_missions.append(mission_id)
            print(f"[DEBUG] Adicionada missão {mission_id} às missões concluídas")

        self._give_rewards(mission.rewards)

        for callback in self.mission_callbacks['mission_completed']:
            callback(mission)

        print(f"[DEBUG] Buscando próxima missão para iniciar automaticamente...")
        # Inicia automaticamente a próxima missão, se disponível
        mission_order = ["tutorial", "supply_run", "raider_conflict", "industrial_exploration", "truth_revelation"]
        current_index = mission_order.index(mission_id) if mission_id in mission_order else -1
        
        if current_index >= 0 and current_index < len(mission_order) - 1:
            next_mission_id = mission_order[current_index + 1]
            next_mission = self.missions.get(next_mission_id)
            
            if next_mission and next_mission.status == MissionStatus.NOT_STARTED:
                print(f"[DEBUG] Tentando iniciar a próxima missão: {next_mission_id}")
                started = self.start_mission(next_mission_id)
                if started:
                    print(f"[DEBUG] Próxima missão {next_mission_id} iniciada com sucesso!")
                else:
                    print(f"[DEBUG] Falha ao iniciar a próxima missão {next_mission_id}")
        else:
            print(f"[DEBUG] Não há mais missões disponíveis após {mission_id}")

    def fail_mission(self, mission_id: str):
        if mission_id not in self.missions:
            return

        mission = self.missions[mission_id]
        mission.fail()

        if mission_id in self.active_missions:
            self.active_missions.remove(mission_id)
        self.failed_missions.append(mission_id)

        for callback in self.mission_callbacks['mission_failed']:
            callback(mission)
    def update_objective(self, objective_type: ObjectiveType, target: str, amount: int = 1):
        print(f"[DEBUG] Atualizando objetivo: {objective_type.value}, target: {target}, amount: {amount}")

        for mission_id in self.active_missions:
            mission = self.missions[mission_id]
            for objective in mission.objectives:
                if objective.type == objective_type and objective.target == target:
                    # Evita atualizar repetidamente objetivos de "REACH" que já foram concluídos
                    if objective.type == ObjectiveType.REACH and objective.completed:
                        continue
                        
                    if objective.type == ObjectiveType.SURVIVE:
                        # Atualiza o progresso em tempo real para objetivos de sobrevivência
                        objective.update_progress(amount)
                        print(f"[DEBUG] Sobrevivendo: {objective.current_count}/{objective.target_count} segundos")
                    else:
                        objective.update_progress(amount)

                    if objective.completed:
                        print(f"[DEBUG] Objetivo {objective.id} concluído!")
                        for callback in self.mission_callbacks['objective_completed']:
                            callback(mission, objective)
                        
                        # Verifica se todos os objetivos da missão foram concluídos
                        if all(obj.completed for obj in mission.objectives):
                            print(f"[DEBUG] Missão {mission_id} concluída! Definindo status como COMPLETED...")
                            mission.status = MissionStatus.COMPLETED
                            self.complete_mission(mission_id)
                    break
    def get_active_missions(self) -> List[Mission]:
        missions = []
        # Cria uma cópia da lista para evitar modificação durante iteração
        active_missions_copy = self.active_missions.copy()
        
        for mid in active_missions_copy:
            if mid in self.missions:
                mission = self.missions[mid]
                if mission.status == MissionStatus.ACTIVE:
                    missions.append(mission)
                elif mission.status in [MissionStatus.COMPLETED, MissionStatus.FAILED]:
                    # Remove missões que não estão mais ativas
                    if mid in self.active_missions:
                        self.active_missions.remove(mid)
            else:
                # Remove IDs de missões que não existem mais
                if mid in self.active_missions:
                    self.active_missions.remove(mid)
        
        return missions

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        return self.missions.get(mission_id)

    def _give_rewards(self, rewards: Dict):
        if not hasattr(self.game, 'player') or not self.game.player:
            return

        player = self.game.player

        for reward_type, amount in rewards.items():
            if reward_type == "experience":
                if hasattr(player, 'add_experience'):
                    player.add_experience(amount)
            elif reward_type == "health_pack":
                if hasattr(player, 'inventory'):
                    from items.item_base import HealthPackItem
                    for _ in range(amount):
                        health_pack = HealthPackItem()
                        player.inventory.add_item(health_pack)
            elif reward_type == "ammo":
                if hasattr(player, 'inventory'):
                    from items.item_base import AmmoItem
                    ammo = AmmoItem()
                    ammo.quantity = amount
                    player.inventory.add_item(ammo)

    def register_callback(self, event_type: str, callback: Callable):
        if event_type in self.mission_callbacks:
            self.mission_callbacks[event_type].append(callback)

    def save_progress(self, filename: str = "mission_progress.json"):
        progress_data = {
            'active_missions': self.active_missions,
            'completed_missions': self.completed_missions,
            'failed_missions': self.failed_missions,
            'missions': {}
        }

        for mission_id, mission in self.missions.items():
            progress_data['missions'][mission_id] = {
                'status': mission.status.value,
                'objectives': [
                    {
                        'id': obj.id,
                        'current_count': obj.current_count,
                        'completed': obj.completed
                    }
                    for obj in mission.objectives
                ]
            }

        try:
            with open(filename, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar progresso das missões: {e}")

    def load_progress(self, filename: str = "mission_progress.json"):
        if not os.path.exists(filename):
            print(f"[DEBUG] Arquivo {filename} não existe, mantendo estado atual")
            return

        try:
            with open(filename, 'r') as f:
                progress_data = json.load(f)
            
            old_active = self.active_missions.copy()
            self.active_missions = progress_data.get('active_missions', [])
            self.completed_missions = progress_data.get('completed_missions', [])
            self.failed_missions = progress_data.get('failed_missions', [])
            
            missions_data = progress_data.get('missions', {})
            for mission_id, mission_data in missions_data.items():
                if mission_id in self.missions:
                    mission = self.missions[mission_id]
                    mission.status = MissionStatus(mission_data['status'])

                    objectives_data = mission_data.get('objectives', [])
                    for i, obj_data in enumerate(objectives_data):
                        if i < len(mission.objectives):
                            obj = mission.objectives[i]
                            obj.current_count = obj_data.get('current_count', 0)
                            obj.completed = obj_data.get('completed', False)

        except Exception as e:
            print(f"Erro ao carregar progresso das missões: {e}")
