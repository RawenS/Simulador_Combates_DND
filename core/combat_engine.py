# core/combat_engine.py
import random
import re
# Cambiar importaciones relativas a absolutas
from core.dice import Dice
from persistence.combat_logger import CombatLogger

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