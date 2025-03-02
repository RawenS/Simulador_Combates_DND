# persistence/data_manager.py
import json
import os
import datetime
# Cambiar importaciones relativas a absolutas
from models.character import Character
from models.monster import Monster

class DataManager:
    """Clase para manejar la persistencia de datos."""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        
        # Crear directorio para datos si no existe
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Rutas de archivos
        self.characters_file = os.path.join(data_dir, "characters.json")
        self.monsters_file = os.path.join(data_dir, "monsters.json")
        self.combat_state_file = os.path.join(data_dir, "combat_state.json")
    
    def save_characters(self, characters):
        """Guardar la lista de personajes en un archivo JSON."""
        try:
            data = [char.to_dict() for char in characters]
            with open(self.characters_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar personajes: {e}")
            return False
    
    def load_characters(self):
        """Cargar la lista de personajes desde un archivo JSON."""
        try:
            if not os.path.exists(self.characters_file):
                return []
            
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return [Character.from_dict(char_data) for char_data in data]
        except Exception as e:
            print(f"Error al cargar personajes: {e}")
            return []
    
    def save_monsters(self, monsters):
        """Guardar la lista de monstruos en un archivo JSON."""
        try:
            data = [monster.to_dict() for monster in monsters]
            with open(self.monsters_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar monstruos: {e}")
            return False
    
    def load_monsters(self):
        """Cargar la lista de monstruos desde un archivo JSON."""
        try:
            if not os.path.exists(self.monsters_file):
                return []
            
            with open(self.monsters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return [Monster.from_dict(monster_data) for monster_data in data]
        except Exception as e:
            print(f"Error al cargar monstruos: {e}")
            return []
    
    def save_combat_state(self, combat_engine):
        """Guardar el estado actual del combate."""
        try:
            # Crear un diccionario con el estado del combate
            state = {
                "combat_active": combat_engine.combat_active,
                "round_number": combat_engine.round_number,
                "current_turn_index": combat_engine.current_turn_index,
                "characters": [char.to_dict() for char in combat_engine.characters],
                "monsters": [monster.to_dict() for monster in combat_engine.monsters],
                "initiative_order": [], # No podemos serializar directamente objetos
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Almacenar índices para reconstruir el orden de iniciativa
            char_indices = {id(char): i for i, char in enumerate(combat_engine.characters)}
            monster_indices = {id(monster): i for i, monster in enumerate(combat_engine.monsters)}
            
            for entity in combat_engine.initiative_order:
                if id(entity) in char_indices:
                    state["initiative_order"].append({"type": "character", "index": char_indices[id(entity)]})
                elif id(entity) in monster_indices:
                    state["initiative_order"].append({"type": "monster", "index": monster_indices[id(entity)]})
            
            with open(self.combat_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error al guardar estado del combate: {e}")
            return False
    
    def load_combat_state(self, combat_engine):
        """Cargar un estado de combate guardado."""
        try:
            if not os.path.exists(self.combat_state_file):
                return False
            
            with open(self.combat_state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Cargar personajes y monstruos
            combat_engine.characters = [Character.from_dict(char_data) for char_data in state["characters"]]
            combat_engine.monsters = [Monster.from_dict(monster_data) for monster_data in state["monsters"]]
            
            # Establecer estado del combate
            combat_engine.combat_active = state["combat_active"]
            combat_engine.round_number = state["round_number"]
            combat_engine.current_turn_index = state["current_turn_index"]
            
            # Reconstruir orden de iniciativa
            combat_engine.initiative_order = []
            for entity_ref in state["initiative_order"]:
                if entity_ref["type"] == "character":
                    combat_engine.initiative_order.append(combat_engine.characters[entity_ref["index"]])
                elif entity_ref["type"] == "monster":
                    combat_engine.initiative_order.append(combat_engine.monsters[entity_ref["index"]])
            
            return True
        except Exception as e:
            print(f"Error al cargar estado del combate: {e}")
            return False
    
    def save_character(self, character):
        """Guardar un personaje individual."""
        try:
            # Cargar personajes existentes
            characters = self.load_characters()
            
            # Buscar si el personaje ya existe
            existing_index = next((i for i, c in enumerate(characters) if c.name == character.name), -1)
            
            if existing_index >= 0:
                # Reemplazar personaje existente
                characters[existing_index] = character
            else:
                # Añadir nuevo personaje
                characters.append(character)
            
            # Guardar todos los personajes
            return self.save_characters(characters)
        except Exception as e:
            print(f"Error al guardar personaje: {e}")
            return False
    
    def save_monster(self, monster):
        """Guardar un monstruo individual."""
        try:
            # Cargar monstruos existentes
            monsters = self.load_monsters()
            
            # Buscar si el monstruo ya existe
            existing_index = next((i for i, m in enumerate(monsters) if m.name == monster.name), -1)
            
            if existing_index >= 0:
                # Reemplazar monstruo existente
                monsters[existing_index] = monster
            else:
                # Añadir nuevo monstruo
                monsters.append(monster)
            
            # Guardar todos los monstruos
            return self.save_monsters(monsters)
        except Exception as e:
            print(f"Error al guardar monstruo: {e}")
            return False