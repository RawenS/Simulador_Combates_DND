# D&D Combat Simulator
# Estructura del proyecto:
"""
dnd_combat_simulator/
│
├── models/
│   ├── __init__.py
│   ├── entity.py      # Clase base para personajes y monstruos
│   ├── character.py   # Clase para personajes jugadores
│   └── monster.py     # Clase para monstruos enemigos
│
├── core/
│   ├── __init__.py
│   ├── dice.py        # Funcionalidad de tiradas de dados
│   └── combat_engine.py # Mecánicas de combate
│
├── ui/
│   ├── __init__.py
│   ├── cli.py         # Interfaz de línea de comandos
│   └── cheat_menu.py  # Menú de trampas
│
├── persistence/
│   ├── __init__.py
│   ├── data_manager.py  # Funcionalidad de guardado/carga
│   └── combat_logger.py # Registro de combate
│
└── main.py            # Punto de entrada principal
"""

# Primero, implementemos la clase Entity base

# models/entity.py
from abc import ABC, abstractmethod
import json

class Entity(ABC):
    """Clase base para todas las entidades del juego (personajes y monstruos)."""
    
    def __init__(self, name, max_hp, armor_class, initiative_mod=0):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.armor_class = armor_class
        self.initiative_mod = initiative_mod
        self.initiative_roll = 0
        self.is_alive = True
        self.effects = []  # Efectos de estado
        
    def take_damage(self, amount):
        """Aplicar daño a la entidad."""
        self.current_hp = max(0, self.current_hp - amount)
        if self.current_hp == 0:
            self.is_alive = False
        return f"{self.name} recibe {amount} de daño! HP: {self.current_hp}/{self.max_hp}"
        
    def heal(self, amount):
        """Curar a la entidad."""
        if not self.is_alive:
            return f"{self.name} está derrotado y no puede ser curado!"
        
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        if self.current_hp > 0:
            self.is_alive = True
        return f"{self.name} se cura {amount} HP! HP: {self.current_hp}/{self.max_hp}"
    
    def roll_initiative(self, initiative_roll):
        """Establecer la tirada de iniciativa para esta entidad."""
        self.initiative_roll = initiative_roll + self.initiative_mod
        return self.initiative_roll
    
    def get_status(self):
        """Obtener el estado actual de la entidad."""
        status = "Vivo" if self.is_alive else "Derrotado"
        return f"{self.name}: {self.current_hp}/{self.max_hp} HP ({status})"
    
    @abstractmethod
    def attack(self, target, attack_roll):
        """Atacar a otra entidad."""
        pass
    
    def to_dict(self):
        """Convertir la entidad a un diccionario para serialización."""
        return {
            "name": self.name,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "armor_class": self.armor_class,
            "initiative_mod": self.initiative_mod,
            "is_alive": self.is_alive
        }
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        """Crear una entidad a partir de un diccionario."""
        pass

# models/character.py
from .entity import Entity

class Character(Entity):
    """Clase que representa a un personaje jugador."""
    
    def __init__(self, name, max_hp, armor_class, 
                 strength, dexterity, constitution, intelligence, wisdom, charisma,
                 level=1, proficiency_bonus=2):
        super().__init__(name, max_hp, armor_class, initiative_mod=self._get_modifier(dexterity))
        
        # Atributos
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma
        
        # Detalles del personaje
        self.level = level
        self.proficiency_bonus = proficiency_bonus
        self.experience = 0
        
        # Equipo y habilidades
        self.weapon = None
        self.spells = []
        self.abilities = []
        self.spell_slots = {}
        
    def _get_modifier(self, stat):
        """Calcular el modificador de atributo."""
        return (stat - 10) // 2
    
    def get_attack_modifier(self, weapon=None):
        """Obtener el modificador de ataque para un arma específica."""
        if weapon and weapon.get('finesse', False):
            # Usar el mejor entre FUE o DES para armas con finesse
            return max(self._get_modifier(self.strength), self._get_modifier(self.dexterity)) + self.proficiency_bonus
        else:
            # Por defecto FUE para cuerpo a cuerpo, DES para a distancia
            if weapon and weapon.get('type') == 'ranged':
                return self._get_modifier(self.dexterity) + self.proficiency_bonus
            else:
                return self._get_modifier(self.strength) + self.proficiency_bonus
    
    def get_damage_modifier(self, weapon=None):
        """Obtener el modificador de daño para un arma específica."""
        if weapon and weapon.get('finesse', False):
            # Usar el mejor entre FUE o DES para armas con finesse
            return max(self._get_modifier(self.strength), self._get_modifier(self.dexterity))
        else:
            # Por defecto FUE para cuerpo a cuerpo, DES para a distancia
            if weapon and weapon.get('type') == 'ranged':
                return self._get_modifier(self.dexterity)
            else:
                return self._get_modifier(self.strength)
    
    def attack(self, target, attack_roll):
        """Atacar a otra entidad con el arma actual."""
        if not self.is_alive:
            return f"{self.name} está derrotado y no puede atacar!"
        
        if not self.weapon:
            return f"{self.name} no tiene un arma equipada!"
        
        attack_mod = self.get_attack_modifier(self.weapon)
        total_attack_roll = attack_roll + attack_mod
        
        result = f"{self.name} ataca a {target.name} con {self.weapon['name']} - "
        result += f"Tirada: {attack_roll} + {attack_mod} = {total_attack_roll} vs CA {target.armor_class}"
        
        if total_attack_roll >= target.armor_class:
            # Impacto
            damage_dice = self.weapon['damage_dice']
            damage_mod = self.get_damage_modifier(self.weapon)
            
            # Esto será reemplazado con tiradas de dados reales en el CombatEngine
            damage_roll = 0  # Marcador para la tirada de dados real
            total_damage = damage_roll + damage_mod
            
            result += f" - ¡IMPACTO! Daño: {damage_roll} + {damage_mod} = {total_damage}"
            result += "\n" + target.take_damage(total_damage)
        else:
            # Fallo
            result += " - ¡FALLO!"
        
        return result
    
    def cast_spell(self, spell, target=None, spell_roll=None):
        """Lanzar un hechizo."""
        # La implementación depende del diseño del sistema de hechizos
        # Esto es un marcador por ahora
        if spell not in self.spells:
            return f"{self.name} no conoce el hechizo {spell['name']}!"
        
        if spell['level'] > 0:
            # Verificar espacios de hechizos para no-cantrips
            if self.spell_slots.get(spell['level'], 0) <= 0:
                return f"{self.name} no tiene espacios de hechizo de nivel {spell['level']} restantes!"
            self.spell_slots[spell['level']] -= 1
        
        # El efecto del hechizo se implementaría aquí
        result = f"{self.name} lanza {spell['name']}!"
        
        return result
    
    def add_weapon(self, weapon):
        """Equipar un arma."""
        self.weapon = weapon
        return f"{self.name} equipa {weapon['name']}!"
    
    def add_spell(self, spell):
        """Aprender un nuevo hechizo."""
        self.spells.append(spell)
        return f"{self.name} aprende {spell['name']}!"
    
    def rest_short(self):
        """Tomar un descanso corto."""
        # Implementar mecánicas de descanso corto
        return f"{self.name} toma un descanso corto."
    
    def rest_long(self):
        """Tomar un descanso largo."""
        # Restaurar HP y espacios de hechizos
        self.current_hp = self.max_hp
        # Reiniciar espacios de hechizos
        for level in self.spell_slots:
            self.spell_slots[level] = self.get_max_spell_slots(level)
        
        return f"{self.name} toma un descanso largo y está completamente restaurado!"
    
    def get_max_spell_slots(self, level):
        """Obtener el máximo de espacios de hechizo para un nivel dado basado en el nivel del personaje."""
        # Esto se basaría en la clase y nivel
        # Implementación de marcador
        return max(0, self.level // 2)
    
    def to_dict(self):
        """Convertir el personaje a un diccionario para serialización."""
        data = super().to_dict()
        data.update({
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
            "level": self.level,
            "proficiency_bonus": self.proficiency_bonus,
            "experience": self.experience,
            "weapon": self.weapon,
            "spells": self.spells,
            "abilities": self.abilities,
            "spell_slots": self.spell_slots
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crear un personaje a partir de un diccionario."""
        character = cls(
            name=data["name"],
            max_hp=data["max_hp"],
            armor_class=data["armor_class"],
            strength=data["strength"],
            dexterity=data["dexterity"],
            constitution=data["constitution"],
            intelligence=data["intelligence"],
            wisdom=data["wisdom"],
            charisma=data["charisma"],
            level=data.get("level", 1),
            proficiency_bonus=data.get("proficiency_bonus", 2)
        )
        character.current_hp = data["current_hp"]
        character.is_alive = data["is_alive"]
        character.experience = data.get("experience", 0)
        character.weapon = data.get("weapon")
        character.spells = data.get("spells", [])
        character.abilities = data.get("abilities", [])
        character.spell_slots = data.get("spell_slots", {})
        return character

# models/monster.py
from .entity import Entity

class Monster(Entity):
    """Clase que representa a un monstruo o enemigo."""
    
    def __init__(self, name, max_hp, armor_class, initiative_mod=0, 
                 attack_bonus=0, damage_dice="1d6", damage_bonus=0, 
                 challenge_rating=0, experience_reward=0):
        super().__init__(name, max_hp, armor_class, initiative_mod)
        
        # Estadísticas de combate
        self.attack_bonus = attack_bonus
        self.damage_dice = damage_dice
        self.damage_bonus = damage_bonus
        
        # Recompensas
        self.challenge_rating = challenge_rating
        self.experience_reward = experience_reward
        
        # Habilidades especiales
        self.abilities = []
    
    def attack(self, target, attack_roll):
        """Atacar a otra entidad."""
        if not self.is_alive:
            return f"{self.name} está derrotado y no puede atacar!"
        
        total_attack_roll = attack_roll + self.attack_bonus
        
        result = f"{self.name} ataca a {target.name} - "
        result += f"Tirada: {attack_roll} + {self.attack_bonus} = {total_attack_roll} vs CA {target.armor_class}"
        
        if total_attack_roll >= target.armor_class:
            # Impacto
            # Esto será reemplazado con tiradas de dados reales en el CombatEngine
            damage_roll = 0  # Marcador para la tirada de dados real
            total_damage = damage_roll + self.damage_bonus
            
            result += f" - ¡IMPACTO! Daño: {damage_roll} + {self.damage_bonus} = {total_damage}"
            result += "\n" + target.take_damage(total_damage)
        else:
            # Fallo
            result += " - ¡FALLO!"
        
        return result
    
    def use_ability(self, ability_name, target=None):
        """Usar una habilidad especial."""
        ability = next((a for a in self.abilities if a['name'] == ability_name), None)
        if not ability:
            return f"{self.name} no tiene la habilidad {ability_name}!"
        
        # El efecto de la habilidad se implementaría aquí
        result = f"{self.name} usa {ability_name}!"
        
        return result
    
    def add_ability(self, ability):
        """Añadir una habilidad especial al monstruo."""
        self.abilities.append(ability)
        return f"{self.name} gana la habilidad {ability['name']}!"
    
    def to_dict(self):
        """Convertir el monstruo a un diccionario para serialización."""
        data = super().to_dict()
        data.update({
            "attack_bonus": self.attack_bonus,
            "damage_dice": self.damage_dice,
            "damage_bonus": self.damage_bonus,
            "challenge_rating": self.challenge_rating,
            "experience_reward": self.experience_reward,
            "abilities": self.abilities
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crear un monstruo a partir de un diccionario."""
        monster = cls(
            name=data["name"],
            max_hp=data["max_hp"],
            armor_class=data["armor_class"],
            initiative_mod=data["initiative_mod"],
            attack_bonus=data["attack_bonus"],
            damage_dice=data["damage_dice"],
            damage_bonus=data["damage_bonus"],
            challenge_rating=data.get("challenge_rating", 0),
            experience_reward=data.get("experience_reward", 0)
        )
        monster.current_hp = data["current_hp"]
        monster.is_alive = data["is_alive"]
        monster.abilities = data.get("abilities", [])
        return monster

# Ahora, implementemos la clase Dice para manejar tiradas de dados:

# core/dice.py
import random
import re

class Dice:
    """Clase para manejar tiradas de dados."""
    
    @staticmethod
    def roll(dice_notation):
        """
        Tirar dados basados en la notación estándar de dados (ej., "3d6+2").
        
        Args:
            dice_notation (str): La notación de dados para tirar (ej., "3d6+2")
            
        Returns:
            tuple: (total, rolls, modifier) donde total es la suma de todas las tiradas más el modificador,
                  rolls es una lista de resultados individuales de dados, y modifier es el modificador estático
        """
        # Analizar la notación de dados
        pattern = r"(\d+)d(\d+)([+-]\d+)?"
        match = re.match(pattern, dice_notation.lower())
        
        if not match:
            raise ValueError(f"Notación de dados inválida: {dice_notation}")
        
        num_dice = int(match.group(1))
        dice_type = int(match.group(2))
        modifier_str = match.group(3) or "+0"
        modifier = int(modifier_str)
        
        # Tirar los dados
        rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        return total, rolls, modifier
    
    @staticmethod
    def advantage():
        """Tirar con ventaja (tirar d20 dos veces, tomar el mayor)."""
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        return max(roll1, roll2), (roll1, roll2)
    
    @staticmethod
    def disadvantage():
        """Tirar con desventaja (tirar d20 dos veces, tomar el menor)."""
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        return min(roll1, roll2), (roll1, roll2)

# Implementemos el CombatEngine para manejar mecánicas de combate:

# core/combat_engine.py
import random
from .dice import Dice
from ..persistence.combat_logger import CombatLogger

class CombatEngine:
    """Clase para manejar mecánicas y flujo de combate."""
    
    def __init__(self):
        self.characters = []
        self.monsters = []
        self.initiative_order = []
        self.current_turn_index = 0
        self.round_number = 0
        self.combat_active = False
        self.logger = CombatLogger()
    
    def add_character(self, character):
        """Añadir un personaje al combate."""
        self.characters.append(character)
        self.logger.log(f"Personaje añadido: {character.name}")
        return f"{character.name} se une a la batalla!"
    
    def add_monster(self, monster):
        """Añadir un monstruo al combate."""
        self.monsters.append(monster)
        self.logger.log(f"Monstruo añadido: {monster.name}")
        return f"{monster.name} aparece!"
    
    def start_combat(self):
        """Iniciar un nuevo encuentro de combate."""
        if not self.characters:
            return "¡No hay personajes disponibles para el combate!"
        
        if not self.monsters:
            return "¡No hay monstruos disponibles para el combate!"
        
        self.combat_active = True
        self.round_number = 0
        self.initiative_order = []
        
        # Reiniciar iniciativa para todas las entidades
        for entity in self.characters + self.monsters:
            entity.initiative_roll = 0
        
        self.logger.log("Combate iniciado")
        return "¡Combate iniciado! Tira por iniciativa."
    
    def roll_initiative(self):
        """Tirar iniciativa para todas las entidades y ordenar el orden de iniciativa."""
        if not self.combat_active:
            return "¡El combate no ha comenzado aún!"
        
        self.initiative_order = []
        all_entities = self.characters + self.monsters
        
        # Tirar iniciativa para cada entidad que no ha tirado aún
        for entity in all_entities:
            if entity.initiative_roll == 0:
                initiative_die_roll = random.randint(1, 20)
                initiative_total = entity.roll_initiative(initiative_die_roll)
                self.logger.log(f"{entity.name} tira iniciativa: {initiative_die_roll} + {entity.initiative_mod} = {initiative_total}")
        
        # Ordenar entidades por iniciativa (descendente)
        self.initiative_order = sorted(
            all_entities,
            key=lambda e: e.initiative_roll,
            reverse=True
        )
        
        # Reiniciar contador de turnos
        self.current_turn_index = 0
        
        # Iniciar la primera ronda
        self.round_number = 1
        
        # Crear resumen de iniciativa
        result = "Orden de iniciativa:\n"
        for i, entity in enumerate(self.initiative_order, 1):
            result += f"{i}. {entity.name}: {entity.initiative_roll}\n"
        
        self.logger.log(f"Ronda {self.round_number} iniciada, iniciativa tirada")
        return result
    
    def get_current_entity(self):
        """Obtener la entidad cuyo turno es actualmente."""
        if not self.combat_active or not self.initiative_order:
            return None
        
        return self.initiative_order[self.current_turn_index]
    
    def next_turn(self):
        """Avanzar al siguiente turno en el orden de iniciativa."""
        if not self.combat_active:
            return "¡El combate no ha comenzado aún!"
        
        if not self.initiative_order:
            return "¡La iniciativa no ha sido tirada aún!"
        
        # Moverse a la siguiente entidad en el orden de iniciativa
        self.current_turn_index = (self.current_turn_index + 1) % len(self.initiative_order)
        
        # Si hemos vuelto a la primera entidad, incrementar el contador de rondas
        if self.current_turn_index == 0:
            self.round_number += 1
            self.logger.log(f"Ronda {self.round_number} iniciada")
            result = f"¡Iniciando Ronda {self.round_number}!\n"
        else:
            result = ""
        
        current_entity = self.get_current_entity()
        result += f"Es el turno de {current_entity.name}"
        
        # Verificar si la entidad está viva
        if not current_entity.is_alive:
            result += f" (Derrotado - se salta su turno)"
            return self.next_turn()
        
        self.logger.log(f"Turno de {current_entity.name}")
        return result
    
    def attack(self, attacker, target):
        """Realizar un ataque de una entidad a otra."""
        if not self.combat_active:
            return "¡El combate no ha comenzado aún!"
        
        if not attacker.is_alive:
            return f"{attacker.name} está derrotado y no puede atacar!"
        
        if not target.is_alive:
            return f"{target.name} ya está derrotado!"
        
        # Tirar para atacar
        attack_roll = random.randint(1, 20)
        
        # Verificar si es un crítico (20 natural)
        is_critical = attack_roll == 20
        
        # Permitir que la entidad ejecute su ataque
        if isinstance(attacker, type(self.characters[0])):  # Si es un personaje
            # Tirar el daño específico del arma
            damage_dice = attacker.weapon['damage_dice']
            raw_damage, damage_rolls, damage_mod = Dice.roll(damage_dice)
            # Si es crítico, duplicar los dados de daño
            if is_critical:
                raw_damage = sum(damage_rolls) * 2 + damage_mod
            
            result = attacker.attack(target, attack_roll)
            
            # Reemplazar el marcador de daño con la tirada real
            if "¡IMPACTO!" in result:
                if is_critical:
                    result = result.replace("¡IMPACTO!", "¡CRÍTICO!") 
                    
                damage_mod = attacker.get_damage_modifier(attacker.weapon)
                total_damage = raw_damage + damage_mod
                
                # Reemplazar el placeholder del daño
                result = re.sub(r"Daño: \d+ \+ \d+ = \d+", 
                                f"Daño: {'+'.join(map(str, damage_rolls))} ({sum(damage_rolls)}) + {damage_mod} = {total_damage}", 
                                result)
                
                # Aplicar el daño real al objetivo
                target.take_damage(total_damage)
        else:  # Si es un monstruo
            # Tirar el daño específico del monstruo
            raw_damage, damage_rolls, _ = Dice.roll(attacker.damage_dice)
            # Si es crítico, duplicar los dados de daño
            if is_critical:
                raw_damage = sum(damage_rolls) * 2 + attacker.damage_bonus
            
            result = attacker.attack(target, attack_roll)
            
            # Reemplazar el marcador de daño con la tirada real
            if "¡IMPACTO!" in result:
                if is_critical:
                    result = result.replace("¡IMPACTO!", "¡CRÍTICO!")
                    
                total_damage = raw_damage + attacker.damage_bonus
                
                # Reemplazar el placeholder del daño
                result = re.sub(r"Daño: \d+ \+ \d+ = \d+", 
                                f"Daño: {'+'.join(map(str, damage_rolls))} ({sum(damage_rolls)}) + {attacker.damage_bonus} = {total_damage}", 
                                result)
                
                # Aplicar el daño real al objetivo
                target.take_damage(total_damage)
        
        self.logger.log(result)
        return result
    
    def cast_spell(self, caster, spell_name, target=None):
        """Hacer que una entidad lance un hechizo."""
        if not self.combat_active:
            return "¡El combate no ha comenzado aún!"
        
        if not caster.is_alive:
            return f"{caster.name} está derrotado y no puede lanzar hechizos!"
        
        # Buscar el hechizo
        spell = next((s for s in caster.spells if s['name'] == spell_name), None)
        if not spell:
            return f"{caster.name} no conoce el hechizo {spell_name}!"
        
        # Implementar lógica de lanzamiento de hechizos
        result = caster.cast_spell(spell, target)
        
        self.logger.log(result)
        return result
    
    def check_combat_status(self):
        """Verificar el estado actual del combate."""
        if not self.combat_active:
            return "No hay un combate activo."
        
        # Verificar si todos los personajes han sido derrotados
        all_characters_defeated = all(not char.is_alive for char in self.characters)
        if all_characters_defeated:
            self.combat_active = False
            self.logger.log("Combate terminado - Todos los personajes han sido derrotados")
            return "¡Todos los personajes han sido derrotados! El combate ha terminado."
        
        # Verificar si todos los monstruos han sido derrotados
        all_monsters_defeated = all(not monster.is_alive for monster in self.monsters)
        if all_monsters_defeated:
            self.combat_active = False
            self.logger.log("Combate terminado - Todos los monstruos han sido derrotados")
            return "¡Todos los monstruos han sido derrotados! Victoria para el equipo de aventureros."
        
        # Si el combate sigue activo, mostrar el estado actual
        result = f"Ronda {self.round_number}, Turno de {self.get_current_entity().name}\n"
        
        # Mostrar estado de los personajes
        result += "\nPersonajes:\n"
        for char in self.characters:
            result += f"  {char.get_status()}\n"
        
        # Mostrar estado de los monstruos
        result += "\nMonstruos:\n"
        for monster in self.monsters:
            result += f"  {monster.get_status()}\n"
        
        return result
    
    def end_combat(self):
        """Terminar el combate actual."""
        if not self.combat_active:
            return "No hay un combate activo para terminar."
        
        self.combat_active = False
        self.logger.log("Combate terminado manualmente")
        return "El combate ha finalizado."
    
    def save_state(self, filename):
        """Guardar el estado actual del combate."""
        # Implementado en la clase DataManager
        pass
    
    def load_state(self, filename):
        """Cargar un estado de combate guardado."""
        # Implementado en la clase DataManager
        pass

# Ahora, implementemos la funcionalidad de persistencia:

# persistence/combat_logger.py
import datetime
import os

class CombatLogger:
    """Clase para registrar eventos de combate."""
    
    def __init__(self, log_file="combat_log.txt"):
        self.log_file = log_file
        
        # Crear directorio para logs si no existe
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def log(self, message):
        """Registrar un mensaje en el log de combate."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error al escribir en el log: {e}")
    
    def clear_log(self):
        """Limpiar el archivo de log."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")
        except Exception as e:
            print(f"Error al limpiar el log: {e}")
    
    def get_last_entries(self, n=10):
        """Obtener las últimas n entradas del log."""
        try:
            if not os.path.exists(self.log_file):
                return []
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            return lines[-n:] if lines else []
        except Exception as e:
            print(f"Error al leer el log: {e}")
            return []

# persistence/data_manager.py
import json
import os
from ..models.character import Character
from ..models.monster import Monster

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

# Implementemos la interfaz de línea de comandos:

# ui/cli.py
import os
import re
from ..core.dice import Dice
from ..models.character import Character
from ..models.monster import Monster
from ..core.combat_engine import CombatEngine
from ..persistence.data_manager import DataManager
from .cheat_menu import CheatMenu

class CLI:
    """Interfaz de línea de comandos para la aplicación de combate."""
    
    def __init__(self):
        self.combat_engine = CombatEngine()
        self.data_manager = DataManager()
        self.cheat_menu = CheatMenu(self.combat_engine)
        self.running = True
    
    def clear_screen(self):
        """Limpiar la pantalla de la consola."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Imprimir un encabezado formateado."""
        self.clear_screen()
        print("=" * 60)
        print(f"{title:^60}")
        print("=" * 60)
        print()
    
    def print_menu(self, options):
        """Imprimir un menú de opciones."""
        for key, option in options.items():
            print(f"{key}. {option}")
        print()
    
    def get_input(self, prompt, validator=None):
        """Obtener entrada del usuario con validación opcional."""
        while True:
            user_input = input(prompt).strip()
            
            if validator is None:
                return user_input
            
            if validator(user_input):
                return user_input
            
            print("Entrada inválida. Inténtalo de nuevo.")
    
    def run(self):
        """Ejecutar la interfaz de línea de comandos."""
        self.print_header("D&D Combat Simulator")
        
        while self.running:
            print("Menú Principal")
            self.print_menu({
                "1": "Gestionar Personajes",
                "2": "Gestionar Monstruos",
                "3": "Iniciar Combate",
                "4": "Cargar Combate Guardado",
                "5": "Menú de Trampas",
                "6": "Salir"
            })
            
            choice = self.get_input("Elige una opción: ", lambda x: x in ["1", "2", "3", "4", "5", "6"])
            
            if choice == "1":
                self.manage_characters_menu()
            elif choice == "2":
                self.manage_monsters_menu()
            elif choice == "3":
                self.combat_menu()
            elif choice == "4":
                self.load_combat()
            elif choice == "5":
                self.cheat_menu.run()
            elif choice == "6":
                self.running = False
                print("¡Gracias por jugar!")
    
    def manage_characters_menu(self):
        """Menú para gestionar personajes."""
        self.print_header("Gestión de Personajes")
        
        while True:
            characters = self.data_manager.load_characters()
            
            print("Personajes Disponibles:")
            if characters:
                for i, character in enumerate(characters, 1):
                    print(f"{i}. {character.name} (Nivel {character.level})")
            else:
                print("No hay personajes guardados.")
            
            print("\nOpciones:")
            self.print_menu({
                "1": "Crear Nuevo Personaje",
                "2": "Ver Detalles de Personaje",
                "3": "Editar Personaje",
                "4": "Eliminar Personaje",
                "5": "Volver al Menú Principal"
            })
            
            choice = self.get_input("Elige una opción: ", lambda x: x in ["1", "2", "3", "4", "5"])
            
            if choice == "1":
                self.create_character()
            elif choice == "2":
                if characters:
                    self.view_character(characters)
                else:
                    print("No hay personajes para ver.")
                    input("Presiona Enter para continuar...")
            elif choice == "3":
                if characters:
                    self.edit_character(characters)
                else:
                    print("No hay personajes para editar.")
                    input("Presiona Enter para continuar...")
            elif choice == "4":
                if characters:
                    self.delete_character(characters)
                else:
                    print("No hay personajes para eliminar.")
                    input("Presiona Enter para continuar...")
            elif choice == "5":
                break
    
    def create_character(self):
        """Crear un nuevo personaje."""
        self.print_header("Crear Nuevo Personaje")
        
        name = self.get_input("Nombre del personaje: ", lambda x: len(x) > 0)
        
        try:
            # Atributos básicos
            level = int(self.get_input("Nivel (1-20): ", lambda x: x.isdigit() and 1 <= int(x) <= 20))
            max_hp = int(self.get_input("Puntos de vida máximos: ", lambda x: x.isdigit() and int(x) > 0))
            armor_class = int(self.get_input("Clase de Armadura: ", lambda x: x.isdigit() and int(x) > 0))
            
            # Estadísticas
            strength = int(self.get_input("Fuerza (1-30): ", lambda x: x.isdigit() and 1 <= int(x) <= 30))
            dexterity = int(self.get_input("Destreza (1-30): ", lambda x: x.isdigit() and 1 <= int(x) <= 30))
            constitution = int(self.get_input("Constitución (1-30): ", lambda x: x.isdigit() and 1 <= int(x) <= 30))
            intelligence = int(self.get_input("Inteligencia (1-30): ", lambda x: x.isdigit() and 1 <= int(x) <= 30))
            wisdom = int(self.get_input("Sabiduría (1-30): ", lambda x: x.isdigit() and 1 <= int(x) <= 30))
            charisma = int(self.get_input("Carisma (1-30): ", lambda x: x.isdigit() and 1 <= int(x) <= 30))
            
            # Crear el personaje
            character = Character(
                name=name,
                max_hp=max_hp,
                armor_class=armor_class,
                strength=strength,
                dexterity=dexterity,
                constitution=constitution,
                intelligence=intelligence,
                wisdom=wisdom,
                charisma=charisma,
                level=level
            )
            
            # Equipar un arma básica
            weapon_name = self.get_input("Nombre del arma: ", lambda x: len(x) > 0)
            weapon_type = self.get_input("Tipo de arma (melee/ranged): ", lambda x: x in ["melee", "ranged"])
            weapon_damage_dice = self.get_input("Dados de daño (ej. 1d6, 2d8): ", 
                                               lambda x: re.match(r"\d+d\d+", x))
            
            weapon = {
                "name": weapon_name,
                "type": weapon_type,
                "damage_dice": weapon_damage_dice,
                "finesse": self.get_input("¿Es un arma de finesse? (s/n): ", lambda x: x.lower() in ["s", "n"]).lower() == "s"
            }
            
            character.add_weapon(weapon)
            
            # Guardar el personaje
            if self.data_manager.save_character(character):
                print(f"\nPersonaje {name} creado y guardado con éxito!")
            else:
                print("\nError al guardar el personaje.")
        
        except ValueError:
            print("\nEntrada inválida. Por favor ingresa valores numéricos donde sea necesario.")
        
        input("\nPresiona Enter para continuar...")
    
    def view_character(self, characters):
        """Ver detalles de un personaje."""
        self.print_header("Detalles de Personaje")
        
        # Seleccionar personaje
        for i, character in enumerate(characters, 1):
            print(f"{i}. {character.name}")
        
        choice = int(self.get_input("\nSelecciona un personaje: ", 
                                   lambda x: x.isdigit() and 1 <= int(x) <= len(characters)))
        
        character = characters[choice - 1]
        
        self.print_header(f"Detalles de {character.name}")
        
        print(f"Nivel: {character.level}")
        print(f"HP: {character.current_hp}/{character.max_hp}")
        print(f"Clase de Armadura: {character.armor_class}")
        print()
        print("Atributos:")
        print(f"  Fuerza: {character.strength} (Mod: {character._get_modifier(character.strength)})")
        print(f"  Destreza: {character.dexterity} (Mod: {character._get_modifier(character.dexterity)})")
        print(f"  Constitución: {character.constitution} (Mod: {character._get_modifier(character.constitution)})")
        print(f"  Inteligencia: {character.intelligence} (Mod: {character._get_modifier(character.intelligence)})")
        print(f"  Sabiduría: {character.wisdom} (Mod: {character._get_modifier(character.wisdom)})")
        print(f"  Carisma: {character.charisma} (Mod: {character._get_modifier(character.charisma)})")
        print()
        
        if character.weapon:
            print("Arma equipada:")
            print(f"  Nombre: {character.weapon['name']}")
            print(f"  Tipo: {character.weapon['type']}")
            print(f"  Daño: {character.weapon['damage_dice']}")
            print(f"  Finesse: {'Sí' if character.weapon.get('finesse', False) else 'No'}")
            print(f"  Bono de ataque: +{character.get_attack_modifier(character.weapon)}")
            print(f"  Bono de daño: +{character.get_damage_modifier(character.weapon)}")
        else:
            print("No tiene arma equipada.")
        
        input("\nPresiona Enter para continuar...")
    
    def edit_character(self, characters):
        """Editar un personaje existente."""
        self.print_header("Editar Personaje")
        
        # Seleccionar personaje
        for i, character in enumerate(characters, 1):
            print(f"{i}. {character.name}")
        
        choice = int(self.get_input("\nSelecciona un personaje: ", 
                                   lambda x: x.isdigit() and 1 <= int(x) <= len(characters)))
        
        character = characters[choice - 1]
        
        self.print_header(f"Editar {character.name}")
        
        print("¿Qué deseas modificar?")
        self.print_menu({
            "1": "Puntos de vida máximos",
            "2": "Clase de Armadura",
            "3": "Nivel",
            "4": "Atributos",
            "5": "Arma",
            "6": "Volver"
        })
        
        choice = self.get_input("Elige una opción: ", lambda x: x in ["1", "2", "3", "4", "5", "6"])
        
        try:
            if choice == "1":
                max_hp = int(self.get_input(f"Nuevos puntos de vida máximos (actual: {character.max_hp}): ", 
                                           lambda x: x.isdigit() and int(x) > 0))
                character.max_hp = max_hp
                character.current_hp = min(character.current_hp, max_hp)
            
            elif choice == "2":
                armor_class = int(self.get_input(f"Nueva Clase de Armadura (actual: {character.armor_class}): ", 
                                               lambda x: x.isdigit() and int(x) > 0))
                character.armor_class = armor_class
            
            elif choice == "3":
                level = int(self.get_input(f"Nuevo nivel (actual: {character.level}): ", 
                                         lambda x: x.isdigit() and 1 <= int(x) <= 20))
                character.level = level
            
            elif choice == "4":
                print("Ingresa los nuevos valores de atributos:")
                character.strength = int(self.get_input(f"Fuerza (actual: {character.strength}): ", 
                                                     lambda x: x.isdigit() and 1 <= int(x) <= 30))
                character.dexterity = int(self.get_input(f"Destreza (actual: {character.dexterity}): ", 
                                                      lambda x: x.isdigit() and 1 <= int(x) <= 30))
                character.constitution = int(self.get_input(f"Constitución (actual: {character.constitution}): ", 
                                                         lambda x: x.isdigit() and 1 <= int(x) <= 30))
                character.intelligence = int(self.get_input(f"Inteligencia (actual: {character.intelligence}): ", 
                                                         lambda x: x.isdigit() and 1 <= int(x) <= 30))
                character.wisdom = int(self.get_input(f"Sabiduría (actual: {character.wisdom}): ", 
                                                   lambda x: x.isdigit() and 1 <= int(x) <= 30))
                character.charisma = int(self.get_input(f"Carisma (actual: {character.charisma}): ", 
                                                     lambda x: x.isdigit() and 1 <= int(x) <= 30))
            
            elif choice == "5":
                weapon_name = self.get_input("Nombre del arma: ", lambda x: len(x) > 0)
                weapon_type = self.get_input("Tipo de arma (melee/ranged): ", lambda x: x in ["melee", "ranged"])
                weapon_damage_dice = self.get_input("Dados de daño (ej. 1d6, 2d8): ", 
                                                  lambda x: re.match(r"\d+d\d+", x))
                
                weapon = {
                    "name": weapon_name,
                    "type": weapon_type,
                    "damage_dice": weapon_damage_dice,
                    "finesse": self.get_input("¿Es un arma de finesse? (s/n): ", 
                                            lambda x: x.lower() in ["s", "n"]).lower() == "s"
                }
                
                character.add_weapon(weapon)
            
            elif choice == "6":
                return
            
            # Guardar los cambios
            if self.data_manager.save_character(character):
                print(f"\nPersonaje {character.name} actualizado con éxito!")
            else:
                print("\nError al guardar los cambios.")
        
        except ValueError:
            print("\nEntrada inválida. Por favor ingresa valores numéricos donde sea necesario.")
        
        input("\nPresiona Enter para continuar...")
    
    def delete_character(self, characters):
        """Eliminar un personaje."""
        self.print_header("Eliminar Personaje")
        
        # Seleccionar personaje
        for i, character in enumerate(characters, 1):
            print(f"{i}. {character.name}")
        
        choice = int(self.get_input("\nSelecciona un personaje a eliminar: ", 
                                   lambda x: x.isdigit() and 1 <= int(x) <= len(characters)))
        
        character = characters[choice - 1]
        
        confirm = self.get_input(f"¿Estás seguro de que deseas eliminar a {character.name}? (s/n): ", 
                               lambda x: x.lower() in ["s", "n"])
        
        if confirm.lower() == "s":
            # Eliminar personaje de la lista
            characters.pop(choice - 1)
            
            # Guardar la lista actualizada
            if self.data_manager.save_characters(characters):
                print(f"\nPersonaje {character.name} eliminado con éxito!")
            else:
                print("\nError al eliminar el personaje.")
        else:
            print("\nOperación cancelada.")
        
        input("\nPresiona Enter para continuar...")
    
    def manage_monsters_menu(self):
        """Menú para gestionar monstruos."""
        self.print_header("Gestión de Monstruos")
        
        while True:
            monsters = self.data_manager.load_monsters()
            
            print("Monstruos Disponibles:")
            if monsters:
                for i, monster in enumerate(monsters, 1):
                    print(f"{i}. {monster.name} (CR {monster.challenge_rating})")
            else:
                print("No hay monstruos guardados.")
            
            print("\nOpciones:")
            self.print_menu({
                "1": "Crear Nuevo Monstruo",
                "2": "Ver Detalles de Monstruo",
                "3": "Editar Monstruo",
                "4": "Eliminar Monstruo",
                "5": "Volver al Menú Principal"
            })
            
            choice = self.get_input("Elige una opción: ", lambda x: x in ["1", "2", "3", "4", "5"])
            
            if choice == "1":
                self.create_monster()
            elif choice == "2":
                if monsters:
                    self.view_monster(monsters)
                else:
                    print("No hay monstruos para ver.")
                    input("Presiona Enter para continuar...")
            elif choice == "3":
                if monsters:
                    self.edit_monster(monsters)
                else:
                    print("No hay monstruos para editar.")
                    input("Presiona Enter para continuar...")
            elif choice == "4":
                if monsters:
                    self.delete_monster(monsters)
                else:
                    print("No hay monstruos para eliminar.")
                    input("Presiona Enter para continuar...")
            elif choice == "5":
                break
    
    def create_monster(self):
        """Crear un nuevo monstruo."""
        self.print_header("Crear Nuevo Monstruo")
        
        name = self.get_input("Nombre del monstruo: ", lambda x: len(x) > 0)
        
        try:
            # Atributos básicos
            max_hp = int(self.get_input("Puntos de vida máximos: ", lambda x: x.isdigit() and int(x) > 0))
            armor_class = int(self.get_input("Clase de Armadura: ", lambda x: x.isdigit() and int(x) > 0))
            initiative_mod = int(self.get_input("Modificador de iniciativa: ", lambda x: x.isdigit() or (x.startswith("-") and x[1:].isdigit())))
            
            # Estadísticas de ataque
            attack_bonus = int(self.get_input("Bono de ataque: ", lambda x: x.isdigit() or (x.startswith("-") and x[1:].isdigit())))
            damage_dice = self.get_input("Dados de daño (ej. 1d6, 2d8): ", lambda x: re.match(r"\d+d\d+", x))
            damage_bonus = int(self.get_input("Bono de daño: ", lambda x: x.isdigit() or (x.startswith("-") and x[1:].isdigit())))
            
            # Información adicional
            challenge_rating = float(self.get_input("Challenge Rating (CR): ", lambda x: re.match(r"\d+(\.\d+)?", x)))
            experience_reward = int(self.get_input("Recompensa de experiencia: ", lambda x: x.isdigit() and int(x) >= 0))
            
            # Crear el monstruo
            monster = Monster(
                name=name,
                max_hp=max_hp,
                armor_class=armor_class,
                initiative_mod=initiative_mod,
                attack_bonus=attack_bonus,
                damage_dice=damage_dice,
                damage_bonus=damage_bonus,
                challenge_rating=challenge_rating,
                experience_reward=experience_reward
            )
            
            # Guardar el monstruo
            if self.data_manager.save_monster(monster):
                print(f"\nMonstruo {name} creado y guardado con éxito!")
            else:
                print("\nError al guardar el monstruo.")
        
        except ValueError:
            print("\nEntrada inválida. Por favor ingresa valores numéricos donde sea necesario.")
        
        input("\nPresiona Enter para continuar...")
    
    def view_monster(self, monsters):
        """Ver detalles de un monstruo."""
        self.print_header("Detalles de Monstruo")
        
        # Seleccionar monstruo
        for i, monster in enumerate(monsters, 1):
            print(f"{i}. {monster.name}")
        
        choice = int(self.get_input("\nSelecciona un monstruo: ", 
                                   lambda x: x.isdigit() and 1 <= int(x) <= len(monsters)))
        
        monster = monsters[choice - 1]
        
        self.print_header(f"Detalles de {monster.name}")
        
        print(f"HP: {monster.current_hp}/{monster.max_hp}")
        print(f"Clase de Armadura: {monster.armor_class}")
        print(f"Modificador de iniciativa: {monster.initiative_mod:+d}")
        print()
        print("Estadísticas de ataque:")
        print(f"  Bono de ataque: {monster.attack_bonus:+d}")
        print(f"  Daño: {monster.damage_dice} {monster.damage_bonus:+d}")
        print()
        print(f"Challenge Rating: {monster.challenge_rating}")
        print(f"Recompensa de experiencia: {monster.experience_reward} XP")
        
        if monster.abilities:
            print("\nHabilidades especiales:")
            for ability in monster.abilities:
                print(f"  {ability['name']}: {ability.get('description', 'Sin descripción')}")
        
        input("\nPresiona Enter para continuar...")
    
    def edit_monster(self, monsters):
        """Editar un monstruo existente."""
        self.print_header("Editar Monstruo")
        
        # Seleccionar monstruo
        for i, monster in enumerate(monsters, 1):
            print(f"{i}. {monster.name}")
        
        choice = int(self.get_input("\nSelecciona un monstruo: ", 
                                   lambda x: x.isdigit() and 1 <= int(x) <= len(monsters)))
        
        monster = monsters[choice - 1]
        
        self.print_header(f"Editar {monster.name}")
        
        print("¿Qué deseas modificar?")
        self.print_menu({
            "1": "Puntos de vida máximos",
            "2": "Clase de Armadura",
            "3": "Modificador de iniciativa",
            "4": "Estadísticas de ataque",
            "5": "Challenge Rating y XP",
            "6": "Añadir habilidad especial",
            "7": "Volver"
        })
        
        choice = self.get_input("Elige una opción: ", lambda x: x in ["1", "2", "3", "4", "5", "6", "7"])
        
        try:
            if choice == "1":
                max_hp = int(self.get_input(f"Nuevos puntos de vida máximos (actual: {monster.max_hp}): ", 
                                           lambda x: x.isdigit() and int(x) > 0))
                monster.max_hp = max_hp
                monster.current_hp = min(monster.current_hp, max_hp)
            
            elif choice == "2":
                armor_class = int(self.get_input(f"Nueva Clase de Armadura (actual: {monster.armor_class}): ", 
                                               lambda x: x.isdigit() and int(x) > 0))
                monster.armor_class = armor_class
            
            elif choice == "3":
                initiative_mod = int(self.get_input(f"Nuevo modificador de iniciativa (actual: {monster.initiative_mod}): ", 
                                                  lambda x: x.isdigit() or (x.startswith("-") and x[1:].isdigit())))
                monster.initiative_mod = initiative_mod
            
            elif choice == "4":
                attack_bonus = int(self.get_input(f"Nuevo bono de ataque (actual: {monster.attack_bonus}): ", 
                                                lambda x: x.isdigit() or (x.startswith("-") and x[1:].isdigit())))
                damage_dice = self.get_input(f"Nuevos dados de daño (actual: {monster.damage_dice}): ", 
                                            lambda x: re.match(r"\d+d\d+", x))
                damage_bonus = int(self.get_input(f"Nuevo bono de daño (actual: {monster.damage_bonus}): ", 
                                                lambda x: x.isdigit() or (x.startswith("-") and x[1:].isdigit())))
                
                monster.attack_bonus = attack_bonus
                monster.damage_dice = damage_dice
                monster.damage_bonus = damage_bonus
            
            elif choice == "5":
                challenge_rating = float(self.get_input(f"Nuevo Challenge Rating (actual: {monster.challenge_rating}): ", 
                                                      lambda x: re.match(r"\d+(\.\d+)?", x)))
                experience_reward = int(self.get_input(f"Nueva recompensa de experiencia (actual: {monster.experience_reward}): ", 
                                                    lambda x: x.isdigit() and int(x) >= 0))
                
                monster.challenge_rating = challenge_rating
                monster.experience_reward = experience_reward
            
            elif choice == "6":
                ability_name = self.get_input("Nombre de la habilidad: ", lambda x: len(x) > 0)
                ability_description = self.get_input("Descripción: ", lambda x: len(x) > 0)
                
                monster.add_ability({
                    "name": ability_name,
                    "description": ability_description
                })
            
            elif choice == "7":
                return
            
            # Guardar los cambios
            if self.data_manager.save_monster(monster):
                print(f"\nMonstruo {monster.name} actualizado con éxito!")
            else:
                print("\nError al guardar los cambios.")
        
        except ValueError:
            print("\nEntrada inválida. Por favor ingresa valores numéricos donde sea necesario.")
        
        input("\nPresiona Enter para continuar...")
    
    def delete_monster(self, monsters):
        """Eliminar un monstruo."""
        self.print_header("Eliminar Monstruo")
        
        # Seleccionar monstruo
        for i, monster in enumerate(monsters, 1):
            print(f"{i}. {monster.name}")
        
        choice = int(self.get_input("\nSelecciona un monstruo a eliminar: ", 
                                   lambda x: x.isdigit() and 1 <= int(x) <= len(monsters)))
        
        monster = monsters[choice - 1]
        
        confirm = self.get_input(f"¿Estás seguro de que deseas eliminar a {monster.name}? (s/n): ", 
                               lambda x: x.lower() in ["s", "n"])
        
        if confirm.lower() == "s":
            # Eliminar monstruo de la lista
            monsters.pop(choice - 1)
            
            # Guardar la lista actualizada
            if self.data_manager.save_monsters(monsters):
                print(f"\nMonstruo {monster.name} eliminado con éxito!")
            else:
                print("\nError al eliminar el monstruo.")
        else:
            print("\nOperación cancelada.")
        
        input("\nPresiona Enter para continuar...")
    
    def combat_menu(self):
        """Menú de combate."""
        self.print_header("Preparar Combate")
        
        # Reiniciar el motor de combate
        self.combat_engine = CombatEngine()
        
        # Cargar personajes y monstruos disponibles
        available_characters = self.data_manager.load_characters()
        available_monsters = self.data_manager.load_monsters()
        
        if not available_characters:
            print("No hay personajes disponibles. Crea personajes primero.")
            input("Presiona Enter para continuar...")
            return
        
        if not available_monsters:
            print("No hay monstruos disponibles. Crea monstruos primero.")
            input("Presiona Enter para continuar...")
            return
        
        # Seleccionar personajes para el combate
        print("Selecciona los personajes para el combate:")
        for i, character in enumerate(available_characters, 1):
            print(f"{i}. {character.name} (Nivel {character.level})")
        
        selected_characters = []
        while True:
            choice = self.get_input("\nSelecciona un personaje (0 para terminar): ", 
                                   lambda x: x == "0" or (x.isdigit() and 1 <= int(x) <= len(available_characters)))
            
            if choice == "0":
                break
            
            character_index = int(choice) - 1
            selected_characters.append(available_characters[character_index])
            print(f"{available_characters[character_index].name} añadido al combate.")
        
        if not selected_characters:
            print("No se seleccionaron personajes. Volviendo al menú principal.")
            input("Presiona Enter para continuar...")
            return
        
        # Añadir personajes al combate
        for character in selected_characters:
            self.combat_engine.add_character(character)
        
        # Seleccionar monstruos para el combate
        print("\nSelecciona los monstruos para el combate:")
        for i, monster in enumerate(available_monsters, 1):
            print(f"{i}. {monster.name} (CR {monster.challenge_rating})")
        
        selected_monsters = []
        while True:
            choice = self.get_input("\nSelecciona un monstruo (0 para terminar): ", 
                                   lambda x: x == "0" or (x.isdigit() and 1 <= int(x) <= len(available_monsters)))
            
            if choice == "0":
                break
            
            monster_index = int(choice) - 1
            monster = available_monsters[monster_index]
            
            # Preguntar cuántas instancias de este monstruo añadir
            count = int(self.get_input(f"¿Cuántos {monster.name} quieres añadir? ", 
                                     lambda x: x.isdigit() and int(x) > 0))
            
            for i in range(count):
                # Crear una copia del monstruo con un nombre único si hay más de uno
                monster_copy = Monster.from_dict(monster.to_dict())
                if count > 1:
                    monster_copy.name = f"{monster.name} {i+1}"
                
                selected_monsters.append(monster_copy)
                print(f"{monster_copy.name} añadido al combate.")
        
        if not selected_monsters:
            print("No se seleccionaron monstruos. Volviendo al menú principal.")
            input("Presiona Enter para continuar...")
            return
        
        # Añadir monstruos al combate
        for monster in selected_monsters:
            self.combat_engine.add_monster(monster)
        
        # Iniciar el combate
        start_message = self.combat_engine.start_combat()
        print(f"\n{start_message}")
        
        # Tirar iniciativa
        initiative_result = self.combat_engine.roll_initiative()
        print(f"\n{initiative_result}")
        
        input("\nPresiona Enter para comenzar el combate...")
        
        # Iniciar bucle de combate
        self.run_combat()
    
    def run_combat(self):
        """Ejecutar el bucle principal de combate."""
        while self.combat_engine.combat_active:
            self.print_header(f"Combate - Ronda {self.combat_engine.round_number}")
            
            # Obtener la entidad actual
            current_entity = self.combat_engine.get_current_entity()
            
            if not current_entity:
                print("Error: No hay entidades en el combate.")
                break
            
            # Mostrar estado del combate
            print(self.combat_engine.check_combat_status())
            
            # Si la entidad está derrotada, pasar al siguiente turno
            if not current_entity.is_alive:
                print(f"{current_entity.name} está derrotado y se salta su turno.")
                input("Presiona Enter para continuar...")
                self.combat_engine.next_turn()
                continue
            
            # Determinar si es un personaje o un monstruo
            is_character = current_entity in self.combat_engine.characters
            
            if is_character:
                self.handle_character_turn(current_entity)
            else:
                self.handle_monster_turn(current_entity)
            
            # Verificar si el combate ha terminado
            if not self.combat_engine.combat_active:
                break
        
        print("\nEl combate ha terminado!")
        input("Presiona Enter para continuar...")
    
    def handle_character_turn(self, character):
        """Manejar el turno de un personaje."""
        print(f"\nEs el turno de {character.name}")
        
        self.print_menu({
            "1": "Atacar",
            "2": "Lanzar hechizo",
            "3": "Usar objeto",
            "4": "Ayudar",
            "5": "Pasar turno",
            "6": "Ver estado del combate",
            "7": "Guardar combate",
            "8": "Menú de trampas",
            "9": "Terminar combate"
        })
        
        choice = self.get_input("Elige una acción: ", 
                              lambda x: x in ["1", "2", "3", "4", "5", "6", "7", "8", "9"])
        
        if choice == "1":  # Atacar
            # Mostrar objetivos disponibles
            print("\nObjetivos disponibles:")
            for i, monster in enumerate(self.combat_engine.monsters, 1):
                if monster.is_alive:
                    print(f"{i}. {monster.name} - {monster.current_hp}/{monster.max_hp} HP")
            
            if not any(monster.is_alive for monster in self.combat_engine.monsters):
                print("No hay objetivos disponibles.")
                input("Presiona Enter para continuar...")
                return
            
            # Seleccionar objetivo
            target_choice = int(self.get_input("\nSelecciona un objetivo: ", 
                                             lambda x: x.isdigit() and 1 <= int(x) <= len(self.combat_engine.monsters) and 
                                                      self.combat_engine.monsters[int(x)-1].is_alive))
            
            target = self.combat_engine.monsters[target_choice - 1]
            
            # Realizar ataque
            print("\nTirando d20 para atacar...")
            input("Presiona Enter para tirar...")
            
            attack_result = self.combat_engine.attack(character, target)
            print(f"\n{attack_result}")
        
        elif choice == "2":  # Lanzar hechizo
            if not character.spells:
                print("\nNo tienes hechizos disponibles.")
            else:
                print("\nHechizos disponibles:")
                for i, spell in enumerate(character.spells, 1):
                    level_str = "Truco" if spell["level"] == 0 else f"Nivel {spell['level']}"
                    slots_str = ""
                    if spell["level"] > 0:
                        slots = character.spell_slots.get(spell["level"], 0)
                        slots_str = f" ({slots} espacios restantes)"
                    print(f"{i}. {spell['name']} - {level_str}{slots_str}")
                
                spell_choice = int(self.get_input("\nSelecciona un hechizo: ", 
                                                lambda x: x.isdigit() and 1 <= int(x) <= len(character.spells)))
                
                spell = character.spells[spell_choice - 1]
                
                # Seleccionar objetivo si es necesario
                target = None
                if spell.get("target_required", True):
                    print("\nObjetivos disponibles:")
                    all_entities = []
                    
                    # Añadir monstruos
                    for i, monster in enumerate(self.combat_engine.monsters, 1):
                        if monster.is_alive:
                            all_entities.append(("monster", i-1))
                            print(f"{len(all_entities)}. {monster.name} (Monstruo)")
                    
                    # Añadir personajes
                    for i, char in enumerate(self.combat_engine.characters, 1):
                        if char.is_alive:
                            all_entities.append(("character", i-1))
                            print(f"{len(all_entities)}. {char.name} (Personaje)")
                    
                    if not all_entities:
                        print("No hay objetivos disponibles.")
                        input("Presiona Enter para continuar...")
                        return
                    
                    target_choice = int(self.get_input("\nSelecciona un objetivo: ", 
                                                     lambda x: x.isdigit() and 1 <= int(x) <= len(all_entities)))
                    
                    entity_type, entity_index = all_entities[target_choice - 1]
                    if entity_type == "monster":
                        target = self.combat_engine.monsters[entity_index]
                    else:
                        target = self.combat_engine.characters[entity_index]
                
                # Lanzar hechizo
                spell_result = self.combat_engine.cast_spell(character, spell["name"], target)
                print(f"\n{spell_result}")
        
        elif choice == "3":  # Usar objeto
            print("\nFuncionalidad no implementada aún.")
        
        elif choice == "4":  # Ayudar
            print("\nFuncionalidad no implementada aún.")
        
        elif choice == "5":  # Pasar turno
            print(f"\n{character.name} pasa su turno.")
        
        elif choice == "6":  # Ver estado del combate
            print(f"\n{self.combat_engine.check_combat_status()}")
            input("Presiona Enter para continuar...")
            # No avanzar al siguiente turno
            return
        
        elif choice == "7":  # Guardar combate
            save_result = self.data_manager.save_combat_state(self.combat_engine)
            if save_result:
                print("\nCombate guardado con éxito!")
            else:
                print("\nError al guardar el combate.")
            
            input("Presiona Enter para continuar...")
            # No avanzar al siguiente turno
            return
        
        elif choice == "8":  # Menú de trampas
            self.cheat_menu.run()
            return
        
        elif choice == "9":  # Terminar combate
            confirm = self.get_input("\n¿Estás seguro de que deseas terminar el combate? (s/n): ", 
                                   lambda x: x.lower() in ["s", "n"])
            
            if confirm.lower() == "s":
                self.combat_engine.end_combat()
                print("\nCombate terminado.")
            else:
                print("\nContinuando combate.")
                # No avanzar al siguiente turno
                return
        
        # Avanzar al siguiente turno si no se ha terminado el combate
        if self.combat_engine.combat_active:
            input("\nPresiona Enter para continuar al siguiente turno...")
            self.combat_engine.next_turn()
    
    def handle_monster_turn(self, monster):
        """Manejar el turno de un monstruo."""
        print(f"\nEs el turno de {monster.name}")
        
        # Los monstruos atacan automáticamente a un personaje aleatorio
        alive_characters = [char for char in self.combat_engine.characters if char.is_alive]
        
        if not alive_characters:
            print(f"{monster.name} no tiene objetivos disponibles.")
            input("Presiona Enter para continuar...")
            self.combat_engine.next_turn()
            return
        
        # Seleccionar un personaje aleatorio como objetivo
        target = random.choice(alive_characters)
        
        print(f"{monster.name} ataca a {target.name}...")
        input("Presiona Enter para continuar...")
        
        # Realizar el ataque
        attack_result = self.combat_engine.attack(monster, target)
        print(f"\n{attack_result}")
        
        # Avanzar al siguiente turno
        input("\nPresiona Enter para continuar al siguiente turno...")
        self.combat_engine.next_turn()
    
    def load_combat(self):
        """Cargar un combate guardado."""
        self.print_header("Cargar Combate Guardado")
        
        if not os.path.exists(self.data_manager.combat_state_file):
            print("No hay combates guardados disponibles.")
            input("Presiona Enter para continuar...")
            return
        
        # Intentar cargar el estado del combate
        self.combat_engine = CombatEngine()
        if self.data_manager.load_combat_state(self.combat_engine):
            print("Combate cargado con éxito!")
            input("Presiona Enter para continuar el combate...")
            self.run_combat()
        else:
            print("Error al cargar el combate.")
            input("Presiona Enter para continuar...")

# ui/cheat_menu.py
class CheatMenu:
    """Menú de trampas para modificar el combate."""
    
    def __init__(self, combat_engine):
        self.combat_engine = combat_engine
    
    def run(self):
        """Ejecutar el menú de trampas."""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=" * 60)
            print(f"{'MENÚ DE TRAMPAS':^60}")
            print("=" * 60)
            print()
            
            print("Opciones disponibles:")
            print("1. Modificar puntos de vida")
            print("2. Forzar resultados de tiradas")
            print("3. Modificar estadísticas")
            print("4. Revivir entidad")
            print("5. Derrotar entidad")
            print("6. Volver al combate")
            print()
            
            choice = input("Elige una opción: ").strip()
            
            if choice == "1":
                self.modify_hp()
            elif choice == "2":
                self.force_rolls()
            elif choice == "3":
                self.modify_stats()
            elif choice == "4":
                self.revive_entity()
            elif choice == "5":
                self.defeat_entity()
            elif choice == "6":
                break
            else:
                print("Opción inválida.")
                input("Presiona Enter para continuar...")
    
    def select_entity(self):
        """Seleccionar una entidad del combate."""
        if not self.combat_engine.characters and not self.combat_engine.monsters:
            print("No hay entidades en el combate.")
            return None
        
        print("\nSelecciona una entidad:")
        
        entities = []
        
        # Añadir personajes
        for i, char in enumerate(self.combat_engine.characters, 1):
            entities.append(("character", i-1))
            print(f"{len(entities)}. {char.name} (Personaje)")
        
        # Añadir monstruos
        for i, monster in enumerate(self.combat_engine.monsters, 1):
            entities.append(("monster", i-1))
            print(f"{len(entities)}. {monster.name} (Monstruo)")
        
        while True:
            try:
                choice = int(input("\nSelecciona una entidad (0 para cancelar): ").strip())
                
                if choice == 0:
                    return None
                
                if 1 <= choice <= len(entities):
                    entity_type, entity_index = entities[choice - 1]
                    
                    if entity_type == "character":
                        return self.combat_engine.characters[entity_index]
                    else:
                        return self.combat_engine.monsters[entity_index]
                
                print("Opción inválida.")
            
            except ValueError:
                print("Por favor, ingresa un número.")
    
    def modify_hp(self):
        """Modificar los puntos de vida de una entidad."""
        entity = self.select_entity()
        
        if not entity:
            return
        
        print(f"\nModificar HP de {entity.name}")
        print(f"HP actual: {entity.current_hp}/{entity.max_hp}")
        
        try:
            amount = int(input("\nCantidad de HP a añadir/quitar (negativo para dañar): ").strip())
            
            if amount > 0:
                result = entity.heal(amount)
            else:
                result = entity.take_damage(-amount)
            
            print(f"\n{result}")
        
        except ValueError:
            print("\nPor favor, ingresa un número válido.")
        
        input("\nPresiona Enter para continuar...")
    
    def force_rolls(self):
        """Forzar resultados de tiradas de dados."""
        print("\nForzar resultados de tiradas")
        print("Esta función cambiará temporalmente los resultados de las tiradas.")
        print("Los cambios se aplicarán solo a la siguiente tirada.")
        
        try:
            d20_value = int(input("\nValor forzado para d20 (1-20, 0 para aleatorio): ").strip())
            
            if 0 <= d20_value <= 20:
                # Monkey patch la función random.randint
                original_randint = random.randint
                
                def patched_randint(a, b):
                    if a == 1 and b == 20:
                        # Restaurar la función original después de usarla
                        random.randint = original_randint
                        return d20_value
                    return original_randint(a, b)
                
                random.randint = patched_randint
                
                if d20_value == 0:
                    print("\nLa próxima tirada de d20 será aleatoria.")
                else:
                    print(f"\nLa próxima tirada de d20 será {d20_value}.")
            else:
                print("\nValor fuera de rango (1-20).")
        
        except ValueError:
            print("\nPor favor, ingresa un número válido.")
        
        input("\nPresiona Enter para continuar...")
    
    def modify_stats(self):
        """Modificar estadísticas de una entidad."""
        entity = self.select_entity()
        
        if not entity:
            return
        
        print(f"\nModificar estadísticas de {entity.name}")
        
        if entity in self.combat_engine.characters:
            # Personaje
            print("1. Modificar CA")
            print("2. Modificar atributos")
            print("3. Volver")
            
            choice = input("\nElige una opción: ").strip()
            
            try:
                if choice == "1":
                    current_ac = entity.armor_class
                    new_ac = int(input(f"Nueva CA (actual: {current_ac}): ").strip())
                    entity.armor_class = new_ac
                    print(f"\nCA de {entity.name} modificada a {new_ac}.")
                
                elif choice == "2":
                    print("\nAtributos actuales:")
                    print(f"FUE: {entity.strength}")
                    print(f"DES: {entity.dexterity}")
                    print(f"CON: {entity.constitution}")
                    print(f"INT: {entity.intelligence}")
                    print(f"SAB: {entity.wisdom}")
                    print(f"CAR: {entity.charisma}")
                    
                    attr_choice = input("\nModificar (FUE/DES/CON/INT/SAB/CAR): ").strip().upper()
                    
                    if attr_choice in ["FUE", "DES", "CON", "INT", "SAB", "CAR"]:
                        attr_map = {
                            "FUE": "strength",
                            "DES": "dexterity",
                            "CON": "constitution",
                            "INT": "intelligence",
                            "SAB": "wisdom",
                            "CAR": "charisma"
                        }
                        
                        attr_name = attr_map[attr_choice]
                        current_value = getattr(entity, attr_name)
                        new_value = int(input(f"Nuevo valor para {attr_choice} (actual: {current_value}): ").strip())
                        
                        setattr(entity, attr_name, new_value)
                        print(f"\n{attr_choice} de {entity.name} modificada a {new_value}.")
            
            except ValueError:
                print("\nPor favor, ingresa un número válido.")
        
        else:
            # Monstruo
            print("1. Modificar CA")
            print("2. Modificar estadísticas de ataque")
            print("3. Volver")
            
            choice = input("\nElige una opción: ").strip()
            
            try:
                if choice == "1":
                    current_ac = entity.armor_class
                    new_ac = int(input(f"Nueva CA (actual: {current_ac}): ").strip())
                    entity.armor_class = new_ac
                    print(f"\nCA de {entity.name} modificada a {new_ac}.")
                
                elif choice == "2":
                    print("\nEstadísticas de ataque actuales:")
                    print(f"Bono de ataque: {entity.attack_bonus}")
                    print(f"Dados de daño: {entity.damage_dice}")
                    print(f"Bono de daño: {entity.damage_bonus}")
                    
                    stat_choice = input("\nModificar (ataque/dados/daño): ").strip().lower()
                    
                    if stat_choice == "ataque":
                        new_attack = int(input(f"Nuevo bono de ataque (actual: {entity.attack_bonus}): ").strip())
                        entity.attack_bonus = new_attack
                        print(f"\nBono de ataque de {entity.name} modificado a {new_attack}.")
                    
                    elif stat_choice == "dados":
                        new_dice = input(f"Nuevos dados de daño (actual: {entity.damage_dice}): ").strip()
                        # Validar formato de dados
                        if re.match(r"\d+d\d+", new_dice):
                            entity.damage_dice = new_dice
                            print(f"\nDados de daño de {entity.name} modificados a {new_dice}.")
                        else:
                            print("\nFormato inválido. Usa la forma XdY (ej. 2d6).")
                    
                    elif stat_choice == "daño":
                        new_damage = int(input(f"Nuevo bono de daño (actual: {entity.damage_bonus}): ").strip())
                        entity.damage_bonus = new_damage
                        print(f"\nBono de daño de {entity.name} modificado a {new_damage}.")
            
            except ValueError:
                print("\nPor favor, ingresa un número válido.")
        
        input("\nPresiona Enter para continuar...")
    
    def revive_entity(self):
        """Revivir una entidad derrotada."""
        # Filtrar entidades derrotadas
        defeated_characters = [char for char in self.combat_engine.characters if not char.is_alive]
        defeated_monsters = [monster for monster in self.combat_engine.monsters if not monster.is_alive]
        
        if not defeated_characters and not defeated_monsters:
            print("\nNo hay entidades derrotadas para revivir.")
            input("\nPresiona Enter para continuar...")
            return
        
        print("\nSelecciona una entidad para revivir:")
        
        entities = []
        
        # Añadir personajes derrotados
        for i, char in enumerate(defeated_characters, 1):
            entities.append(("character", self.combat_engine.characters.index(char)))
            print(f"{len(entities)}. {char.name} (Personaje)")
        
        # Añadir monstruos derrotados
        for i, monster in enumerate(defeated_monsters, 1):
            entities.append(("monster", self.combat_engine.monsters.index(monster)))
            print(f"{len(entities)}. {monster.name} (Monstruo)")
        
        try:
            choice = int(input("\nSelecciona una entidad (0 para cancelar): ").strip())
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(entities):
                entity_type, entity_index = entities[choice - 1]
                
                if entity_type == "character":
                    entity = self.combat_engine.characters[entity_index]
                else:
                    entity = self.combat_engine.monsters[entity_index]
                
                hp_amount = int(input(f"¿Con cuántos HP revivir a {entity.name}? (max: {entity.max_hp}): ").strip())
                hp_amount = min(max(1, hp_amount), entity.max_hp)
                
                entity.current_hp = hp_amount
                entity.is_alive = True
                
                print(f"\n¡{entity.name} ha revivido con {hp_amount} HP!")
        
        except ValueError:
            print("\nPor favor, ingresa un número válido.")
        
        input("\nPresiona Enter para continuar...")
    
    def defeat_entity(self):
        """Derrotar instantáneamente a una entidad."""
        entity = self.select_entity()
        
        if not entity:
            return
        
        if not entity.is_alive:
            print(f"\n{entity.name} ya está derrotado.")
            input("\nPresiona Enter para continuar...")
            return
        
        confirm = input(f"\n¿Estás seguro de que quieres derrotar a {entity.name}? (s/n): ").strip().lower()
        
        if confirm == "s":
            entity.current_hp = 0
            entity.is_alive = False
            print(f"\n{entity.name} ha sido derrotado!")
        else:
            print("\nOperación cancelada.")
        
        input("\nPresiona Enter para continuar...")

# main.py
def main():
    """Punto de entrada principal de la aplicación."""
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    main()