from pyftg.models.attack_data import AttackData
from pyftg.models.character_data import CharacterData
from pyftg.models.enums.action import Action
from pyftg.models.enums.state import State
from pyftg.models.frame_data import FrameData

from src.config import (ATTACK_TYPES, MAX_ENERGY, MAX_FRAME_NUMBER, MAX_HP,
                        STAGE_HEIGHT, STAGE_WIDTH)


def process_player_data(character: CharacterData) -> dict:
    return {
        "character_name": "Zen",
        "hp": character.hp,
        "energy": character.energy,
        "position": {
            "left": character.left,
            "right": character.right,
            "top": character.top,
            "bottom": character.bottom,
        },
        "speed": {
            "x": character.speed_x,
            "y": character.speed_y,
        },
        "direction": "Right" if character.front else "Left",
        "state": str.capitalize(str(character.state).split('.')[1]),
        "action": str.capitalize(str(character.action).split('.')[1]),
        "control": character.control,
        "combo": character.hit_count,
    }


def process_projectile_data(attack: AttackData) -> dict:
    return {
        "from": "player_1" if attack.player_number else "player_2",
        "position": {
            "left": attack.current_hit_area.left,
            "right": attack.current_hit_area.right,
            "top": attack.current_hit_area.top,
            "bottom": attack.current_hit_area.bottom,
        },
        "speed": {
            "x": attack.speed_x,
            "y": attack.speed_y,
        },
        "type": ATTACK_TYPES[attack.attack_type],
        "damage": attack.hit_damage,
        "down": attack.down_prop,
    }


def process_frame_data(frame: FrameData) -> dict:
    return {
        "player_1": process_player_data(frame.get_character(True)),
        "player_2": process_player_data(frame.get_character(False)),
        "time_left": (MAX_FRAME_NUMBER - frame.current_frame_number) / 60.0,
        "projectiles": [process_projectile_data(x) for x in frame.projectile_data],
    }


def embedding_character_data(character: dict) -> list[float]:
    embedding = list()
    embedding.append(character["hp"] / MAX_HP)
    embedding.append(character["energy"] / MAX_ENERGY)
    embedding.append(character["position"]["left"] / STAGE_WIDTH)
    embedding.append(character["position"]["right"] / STAGE_WIDTH)
    embedding.append(character["position"]["top"] / STAGE_HEIGHT)
    embedding.append(character["position"]["bottom"] / STAGE_HEIGHT)
    embedding.append(max(min(character["speed"]["x"] + 10, 20), 0) / 20)
    embedding.append(max(min(character["speed"]["y"] + 10, 20), 0) / 20)
    embedding.append(min(9, character["combo"]) / 9)
    embedding.append(1.0 if character["direction"] == "Right" else 0.0)
    embedding.extend([1.0 if i == State[str(character["state"]).upper()].value else 0.0 for i in range(4)])
    embedding.extend([1.0 if i == Action[str(character["action"]).upper()].value else 0.0 for i in range(56)])
    return embedding


def embedding_frame_data(frame: dict) -> list[float]:
    embedding = list()
    embedding.extend(embedding_character_data(frame["player_1"]))
    embedding.extend(embedding_character_data(frame["player_2"]))
    return embedding
