# ui/spell_manager.py
import os
import re
from models.spell import Spell
from models.spellbook import SpellBook

class SpellManager:
    """Interfaz para gestionar hechizos en la aplicación."""
    
    def __init__(self, character=None):
        """
        Inicializar el gestor de hechizos.
        
        Args:
            character (Character, optional): Personaje al que asociar los hechizos.
        """
        self.spellbook = SpellBook()
        self.character = character
    
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
        """Ejecutar el gestor de hechizos como menú independiente."""
        self.print_header("Gestor de Hechizos")
        
        while True:
            print("Opciones disponibles:")
            print("1. Ver lista de hechizos")
            print("2. Ver detalles de un hechizo")
            print("3. Crear nuevo hechizo")
            print("4. Modificar hechizo existente")
            print("5. Eliminar hechizo")
            if self.character:
                print("6. Asignar hechizo al personaje")
                print("7. Eliminar hechizo del personaje")
            print("0. Volver")
            print()
            
            choice = self.get_input("Elige una opción: ", lambda x: x in [str(i) for i in range(8 if self.character else 6)])
            
            if choice == "0":
                break
            elif choice == "1":
                self.view_spell_list()
            elif choice == "2":
                self.view_spell_details()
            elif choice == "3":
                self.create_spell()
            elif choice == "4":
                self.edit_spell()
            elif choice == "5":
                self.delete_spell()
            elif choice == "6" and self.character:
                self.assign_spell_to_character()
            elif choice == "7" and self.character:
                self.remove_spell_from_character()
    
    def view_spell_list(self, filter_level=None, filter_type=None):
        """
        Ver lista de hechizos con filtros opcionales.
        
        Args:
            filter_level (int, optional): Filtrar por nivel de hechizo.
            filter_type (str, optional): Filtrar por tipo de hechizo.
            
        Returns:
            list: Lista de hechizos filtrados.
        """
        self.print_header("Lista de Hechizos")
        
        # Aplicar filtros si están presentes
        if filter_level is not None and filter_type is not None:
            filtered_spells = [s for s in self.spellbook.spells if s.level == filter_level and s.spell_type.lower() == filter_type.lower()]
            print(f"Hechizos de nivel {filter_level} de tipo {filter_type}:")
        elif filter_level is not None:
            filtered_spells = self.spellbook.get_spells_by_level(filter_level)
            print(f"Hechizos de nivel {filter_level}:")
        elif filter_type is not None:
            filtered_spells = self.spellbook.get_spells_by_type(filter_type)
            print(f"Hechizos de tipo {filter_type}:")
        else:
            filtered_spells = self.spellbook.spells
            print("Todos los hechizos disponibles:")
        
        # Agrupar por nivel
        spells_by_level = {}
        for spell in filtered_spells:
            if spell.level not in spells_by_level:
                spells_by_level[spell.level] = []
            spells_by_level[spell.level].append(spell)
        
        # Mostrar hechizos agrupados por nivel
        for level in sorted(spells_by_level.keys()):
            level_name = "Trucos" if level == 0 else f"Nivel {level}"
            print(f"\n{level_name}:")
            for i, spell in enumerate(sorted(spells_by_level[level], key=lambda s: s.name), 1):
                damage_str = f" - {spell.damage_dice} {spell.damage_type}" if spell.damage_dice else ""
                healing_str = f" - Cura {spell.healing_dice}" if spell.healing_dice else ""
                print(f"  {i}. {spell.name} ({spell.spell_type}){damage_str}{healing_str}")
        
        print()
        input("Presiona Enter para continuar...")
        
        return filtered_spells
    
    def view_spell_details(self):
        """Ver detalles completos de un hechizo seleccionado."""
        self.print_header("Detalles de Hechizo")
        
        # Filtrar primero para facilitar la selección
        print("Filtrar hechizos (opcional):")
        print("1. Por nivel")
        print("2. Por tipo")
        print("3. Ver todos")
        filter_choice = self.get_input("Elige una opción: ", lambda x: x in ["1", "2", "3"])
        
        if filter_choice == "1":
            level = int(self.get_input("Nivel (0-9): ", lambda x: x.isdigit() and 0 <= int(x) <= 9))
            filtered_spells = self.view_spell_list(filter_level=level)
        elif filter_choice == "2":
            spell_type = self.get_input("Tipo (ofensivo, defensivo, utilidad, curación, etc.): ")
            filtered_spells = self.view_spell_list(filter_type=spell_type)
        else:
            filtered_spells = self.view_spell_list()
        
        if not filtered_spells:
            print("No hay hechizos que cumplan con los filtros.")
            input("Presiona Enter para continuar...")
            return
        
        # Seleccionar un hechizo
        spell_index = int(self.get_input(
            "Selecciona un hechizo para ver detalles (0 para cancelar): ", 
            lambda x: x == "0" or (x.isdigit() and 1 <= int(x) <= len(filtered_spells))
        ))
        
        if spell_index == 0:
            return
        
        # Mostrar detalles
        spell = filtered_spells[spell_index - 1]
        self.print_header(f"Detalles de {spell.name}")
        print(spell.get_full_description())
        
        print()
        input("Presiona Enter para continuar...")
    
    def create_spell(self):
        """Crear un nuevo hechizo y añadirlo al libro de hechizos."""
        self.print_header("Crear Nuevo Hechizo")
        
        try:
            # Atributos básicos
            name = self.get_input("Nombre del hechizo: ", lambda x: len(x) > 0)
            
            # Verificar si ya existe
            if self.spellbook.get_spell(name):
                print(f"Ya existe un hechizo llamado '{name}'.")
                input("Presiona Enter para continuar...")
                return
            
            description = self.get_input("Descripción: ", lambda x: len(x) > 0)
            spell_type = self.get_input("Tipo (ofensivo, defensivo, utilidad, curación, etc.): ", lambda x: len(x) > 0)
            level = int(self.get_input("Nivel (0-9): ", lambda x: x.isdigit() and 0 <= int(x) <= 9))
            
            # Tiempo de lanzamiento y duración
            cast_time = self.get_input("Tiempo de lanzamiento (por defecto '1 acción'): ") or "1 acción"
            duration = self.get_input("Duración (por defecto 'Instantáneo'): ") or "Instantáneo"
            
            # Alcance y componentes
            range_str = self.get_input("Alcance (por defecto '60 pies'): ") or "60 pies"
            components = self.get_input("Componentes (V, S, M): ") or "V, S"
            
            # Mecánicas de ataque/salvación
            attack_roll = self.get_input("¿Requiere tirada de ataque? (s/n): ", lambda x: x.lower() in ["s", "n"]).lower() == "s"
            
            saving_throw = None
            saving_throw_attribute = None
            if not attack_roll:
                requires_save = self.get_input("¿Requiere tirada de salvación? (s/n): ", lambda x: x.lower() in ["s", "n"]).lower() == "s"
                if requires_save:
                    saving_throw = self.get_input("Tipo de salvación (Destreza, Constitución, etc.): ")
                    saving_throw_attribute = self.get_input("Atributo abreviado (DEX, CON, etc.): ")
            
            # Daño o curación
            damage_dice = None
            damage_type = None
            healing_dice = None
            
            spell_effect = self.get_input("¿El hechizo causa daño o cura? (daño/curación/ninguno): ", 
                                        lambda x: x.lower() in ["daño", "curación", "ninguno"]).lower()
            
            if spell_effect == "daño":
                damage_dice = self.get_input("Dados de daño (ej. 2d6, 1d8): ", 
                                           lambda x: re.match(r"\d+d\d+", x))
                damage_type = self.get_input("Tipo de daño (fuego, frío, contundente, etc.): ")
            elif spell_effect == "curación":
                healing_dice = self.get_input("Dados de curación (ej. 1d8+modificador, 2d4): ", 
                                           lambda x: re.match(r"\d+d\d+", x) or "modificador" in x.lower())
            
            # Área de efecto
            has_aoe = self.get_input("¿Tiene área de efecto? (s/n): ", lambda x: x.lower() in ["s", "n"]).lower() == "s"
            aoe_type = None
            aoe_size = None
            
            if has_aoe:
                aoe_type = self.get_input("Tipo de área (cono, esfera, cubo, etc.): ")
                aoe_size = self.get_input("Tamaño del área (ej. 20 pies de radio, 15 pies de lado): ")
            
            # Efectos adicionales
            effects = []
            while True:
                has_effect = self.get_input("¿Quieres añadir un efecto adicional? (s/n): ", 
                                          lambda x: x.lower() in ["s", "n"]).lower() == "s"
                if not has_effect:
                    break
                
                effect_name = self.get_input("Nombre del efecto: ")
                effect_desc = self.get_input("Descripción del efecto: ")
                effect_duration = int(self.get_input("Duración en turnos (-1 para permanente): ", 
                                                   lambda x: x.isdigit() or (x.startswith("-") and x[1:].isdigit())))
                effect_type = self.get_input("Tipo de efecto (positivo, negativo, neutral): ", 
                                           lambda x: x.lower() in ["positivo", "negativo", "neutral"]).lower()
                
                has_modifier = self.get_input("¿El efecto modifica algún atributo o estadística? (s/n): ", 
                                           lambda x: x.lower() in ["s", "n"]).lower() == "s"
                
                effect_modifier = None
                effect_attribute = None
                effect_value = 0
                
                if has_modifier:
                    effect_modifier = self.get_input("Tipo de modificador (ataque, daño, CA, velocidad, etc.): ")
                    effect_attribute = self.get_input("Atributo afectado (si aplica): ")
                    effect_value = int(self.get_input("Valor de la modificación: ", 
                                                   lambda x: x.isdigit() or (x.startswith("-") and x[1:].isdigit())))
                
                effects.append({
                    "name": effect_name,
                    "description": effect_desc,
                    "duration": effect_duration,
                    "effect_type": effect_type,
                    "modifier": effect_modifier,
                    "attribute": effect_attribute,
                    "value": effect_value
                })
            
            # Crear el hechizo
            spell = Spell(
                name=name,
                description=description,
                spell_type=spell_type,
                level=level,
                cast_time=cast_time,
                range=range_str,
                components=components,
                duration=duration,
                attack_roll=attack_roll,
                saving_throw=saving_throw,
                saving_throw_attribute=saving_throw_attribute,
                damage_dice=damage_dice,
                damage_type=damage_type,
                healing_dice=healing_dice,
                aoe_type=aoe_type,
                aoe_size=aoe_size,
                effects=effects
            )
            
            # Añadir al libro de hechizos
            if self.spellbook.add_spell(spell):
                print(f"\nHechizo '{name}' creado y añadido al libro de hechizos con éxito!")
            else:
                print(f"\nError al añadir el hechizo '{name}' al libro de hechizos.")
        
        except ValueError as e:
            print(f"\nError: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def edit_spell(self):
        """Modificar un hechizo existente."""
        self.print_header("Modificar Hechizo")
        
        # Mostrar todos los hechizos para selección
        filtered_spells = self.view_spell_list()
        
        if not filtered_spells:
            print("No hay hechizos disponibles para modificar.")
            input("Presiona Enter para continuar...")
            return
        
        # Seleccionar un hechizo
        spell_index = int(self.get_input(
            "Selecciona un hechizo para modificar (0 para cancelar): ", 
            lambda x: x == "0" or (x.isdigit() and 1 <= int(x) <= len(filtered_spells))
        ))
        
        if spell_index == 0:
            return
        
        original_spell = filtered_spells[spell_index - 1]
        
        # Para simplificar, eliminamos el hechizo original y creamos uno nuevo
        original_name = original_spell.name
        self.spellbook.remove_spell(original_name)
        
        self.print_header(f"Modificar Hechizo: {original_name}")
        print("Ingresa los nuevos datos del hechizo. Para mantener el valor actual, deja el campo en blanco.")
        
        try:
            # Atributos básicos
            name = self.get_input(f"Nombre ({original_spell.name}): ") or original_spell.name
            description = self.get_input(f"Descripción ({original_spell.description}): ") or original_spell.description
            spell_type = self.get_input(f"Tipo ({original_spell.spell_type}): ") or original_spell.spell_type
            
            level_str = self.get_input(f"Nivel ({original_spell.level}): ")
            level = int(level_str) if level_str else original_spell.level
            
            # Tiempo de lanzamiento y duración
            cast_time = self.get_input(f"Tiempo de lanzamiento ({original_spell.cast_time}): ") or original_spell.cast_time
            duration = self.get_input(f"Duración ({original_spell.duration}): ") or original_spell.duration
            
            # Alcance y componentes
            range_str = self.get_input(f"Alcance ({original_spell.range}): ") or original_spell.range
            components = self.get_input(f"Componentes ({original_spell.components}): ") or original_spell.components
            
            # Mecánicas de ataque/salvación
            attack_roll_str = self.get_input(
                f"¿Requiere tirada de ataque? ({'s' if original_spell.attack_roll else 'n'}): ", 
                lambda x: x == "" or x.lower() in ["s", "n"]
            )
            attack_roll = original_spell.attack_roll
            if attack_roll_str:
                attack_roll = attack_roll_str.lower() == "s"
            
            saving_throw = original_spell.saving_throw
            saving_throw_attribute = original_spell.saving_throw_attribute
            
            if not attack_roll:
                requires_save_str = self.get_input(
                    f"¿Requiere tirada de salvación? ({'s' if saving_throw else 'n'}): ", 
                    lambda x: x == "" or x.lower() in ["s", "n"]
                )
                
                requires_save = saving_throw is not None
                if requires_save_str:
                    requires_save = requires_save_str.lower() == "s"
                
                if requires_save:
                    saving_throw = self.get_input(f"Tipo de salvación ({saving_throw or ''}): ") or saving_throw
                    saving_throw_attribute = self.get_input(f"Atributo abreviado ({saving_throw_attribute or ''}): ") or saving_throw_attribute
                else:
                    saving_throw = None
                    saving_throw_attribute = None
            
            # Daño o curación
            damage_dice = original_spell.damage_dice
            damage_type = original_spell.damage_type
            healing_dice = original_spell.healing_dice
            
            spell_effect_options = []
            if damage_dice:
                spell_effect_options.append("daño")
            if healing_dice:
                spell_effect_options.append("curación")
            if not damage_dice and not healing_dice:
                spell_effect_options.append("ninguno")
            
            current_effect = spell_effect_options[0] if spell_effect_options else "ninguno"
            
            spell_effect = self.get_input(
                f"¿El hechizo causa daño o cura? ({current_effect}): ", 
                lambda x: x == "" or x.lower() in ["daño", "curación", "ninguno"]
            ).lower() or current_effect
            
            if spell_effect == "daño":
                damage_dice = self.get_input(
                    f"Dados de daño ({damage_dice or ''}): ", 
                    lambda x: x == "" or re.match(r"\d+d\d+", x)
                ) or damage_dice
                
                damage_type = self.get_input(f"Tipo de daño ({damage_type or ''}): ") or damage_type
                healing_dice = None
            elif spell_effect == "curación":
                healing_dice = self.get_input(
                    f"Dados de curación ({healing_dice or ''}): ", 
                    lambda x: x == "" or re.match(r"\d+d\d+", x) or "modificador" in x.lower()
                ) or healing_dice
                
                damage_dice = None
                damage_type = None
            else:
                damage_dice = None
                damage_type = None
                healing_dice = None
            
            # Área de efecto
            has_aoe = original_spell.aoe_type is not None
            aoe_type = original_spell.aoe_type
            aoe_size = original_spell.aoe_size
            
            has_aoe_str = self.get_input(
                f"¿Tiene área de efecto? ({'s' if has_aoe else 'n'}): ", 
                lambda x: x == "" or x.lower() in ["s", "n"]
            )
            
            if has_aoe_str:
                has_aoe = has_aoe_str.lower() == "s"
            
            if has_aoe:
                aoe_type = self.get_input(f"Tipo de área ({aoe_type or ''}): ") or aoe_type
                aoe_size = self.get_input(f"Tamaño del área ({aoe_size or ''}): ") or aoe_size
            else:
                aoe_type = None
                aoe_size = None
            
            # Efectos adicionales
            effects = original_spell.effects.copy()
            
            # Opción para modificar efectos existentes
            if effects:
                print("\nEfectos actuales:")
                for i, effect in enumerate(effects, 1):
                    print(f"{i}. {effect['name']} - {effect['description'][:30]}...")
                
                modify_effects = self.get_input(
                    "¿Quieres modificar los efectos existentes? (s/n): ", 
                    lambda x: x.lower() in ["s", "n"]
                ).lower() == "s"
                
                if modify_effects:
                    # Para simplicidad, eliminamos todos y añadimos nuevos
                    effects = []
            
            # Añadir nuevos efectos
            while True:
                has_effect = self.get_input("¿Quieres añadir un efecto adicional? (s/n): ", 
                                          lambda x: x.lower() in ["s", "n"]).lower() == "s"
                if not has_effect:
                    break
                
                effect_name = self.get_input("Nombre del efecto: ")
                effect_desc = self.get_input("Descripción del efecto: ")
                effect_duration = int(self.get_input("Duración en turnos (-1 para permanente): ", 
                                                   lambda x: x.isdigit() or (x.startswith("-") and x[1:].isdigit())))
                effect_type = self.get_input("Tipo de efecto (positivo, negativo, neutral): ", 
                                           lambda x: x.lower() in ["positivo", "negativo", "neutral"]).lower()
                
                has_modifier = self.get_input("¿El efecto modifica algún atributo o estadística? (s/n): ", 
                                           lambda x: x.lower() in ["s", "n"]).lower() == "s"
                
                effect_modifier = None
                effect_attribute = None
                effect_value = 0
                
                if has_modifier:
                    effect_modifier = self.get_input("Tipo de modificador (ataque, daño, CA, velocidad, etc.): ")
                    effect_attribute = self.get_input("Atributo afectado (si aplica): ")
                    effect_value = int(self.get_input("Valor de la modificación: ", 
                                                   lambda x: x.isdigit() or (x.startswith("-") and x[1:].isdigit())))
                
                effects.append({
                    "name": effect_name,
                    "description": effect_desc,
                    "duration": effect_duration,
                    "effect_type": effect_type,
                    "modifier": effect_modifier,
                    "attribute": effect_attribute,
                    "value": effect_value
                })
            
            # Crear el hechizo modificado
            spell = Spell(
                name=name,
                description=description,
                spell_type=spell_type,
                level=level,
                cast_time=cast_time,
                range=range_str,
                components=components,
                duration=duration,
                attack_roll=attack_roll,
                saving_throw=saving_throw,
                saving_throw_attribute=saving_throw_attribute,
                damage_dice=damage_dice,
                damage_type=damage_type,
                healing_dice=healing_dice,
                aoe_type=aoe_type,
                aoe_size=aoe_size,
                effects=effects
            )
            
            # Añadir al libro de hechizos
            if self.spellbook.add_spell(spell):
                print(f"\nHechizo '{name}' modificado con éxito!")
            else:
                print(f"\nError al modificar el hechizo. Recuperando versión original...")
                self.spellbook.add_spell(original_spell)
        
        except ValueError as e:
            print(f"\nError: {e}")
            print("Recuperando versión original del hechizo...")
            self.spellbook.add_spell(original_spell)
        
        input("\nPresiona Enter para continuar...")
    
    def delete_spell(self):
        """Eliminar un hechizo del libro."""
        self.print_header("Eliminar Hechizo")
        
        # Mostrar todos los hechizos para selección
        filtered_spells = self.view_spell_list()
        
        if not filtered_spells:
            print("No hay hechizos disponibles para eliminar.")
            input("Presiona Enter para continuar...")
            return
        
        # Seleccionar un hechizo
        spell_index = int(self.get_input(
            "Selecciona un hechizo para eliminar (0 para cancelar): ", 
            lambda x: x == "0" or (x.isdigit() and 1 <= int(x) <= len(filtered_spells))
        ))
        
        if spell_index == 0:
            return
        
        spell = filtered_spells[spell_index - 1]
        
        # Confirmar eliminación
        confirm = self.get_input(
            f"¿Estás seguro de que quieres eliminar el hechizo '{spell.name}'? (s/n): ", 
            lambda x: x.lower() in ["s", "n"]
        ).lower()
        
        if confirm == "s":
            if self.spellbook.remove_spell(spell.name):
                print(f"\nHechizo '{spell.name}' eliminado con éxito!")
            else:
                print(f"\nError al eliminar el hechizo '{spell.name}'.")
        else:
            print("\nOperación cancelada.")
        
        input("\nPresiona Enter para continuar...")
    
    def assign_spell_to_character(self):
        """Asignar un hechizo del libro al personaje."""
        if not self.character:
            print("No hay personaje seleccionado.")
            input("Presiona Enter para continuar...")
            return
        
        self.print_header(f"Asignar Hechizo a {self.character.name}")
        
        # Mostrar hechizos disponibles en el libro
        filtered_spells = self.view_spell_list()
        
        if not filtered_spells:
            print("No hay hechizos disponibles para asignar.")
            input("Presiona Enter para continuar...")
            return
        
        # Seleccionar un hechizo
        spell_index = int(self.get_input(
            "Selecciona un hechizo para asignar (0 para cancelar): ", 
            lambda x: x == "0" or (x.isdigit() and 1 <= int(x) <= len(filtered_spells))
        ))
        
        if spell_index == 0:
            return
        
        spell = filtered_spells[spell_index - 1]
        
        # Verificar si el personaje ya conoce el hechizo
        if any(s.name.lower() == spell.name.lower() for s in self.character.spells):
            print(f"\n{self.character.name} ya conoce el hechizo {spell.name}.")
        else:
            # Añadir el hechizo al personaje
            result = self.character.add_spell(spell)
            print(f"\n{result}")
        
        input("\nPresiona Enter para continuar...")
    
    def remove_spell_from_character(self):
        """Eliminar un hechizo del personaje."""
        if not self.character:
            print("No hay personaje seleccionado.")
            input("Presiona Enter para continuar...")
            return
        
        self.print_header(f"Eliminar Hechizo de {self.character.name}")
        
        # Mostrar hechizos del personaje
        character_spells = self.character.spells
        
        if not character_spells:
            print(f"{self.character.name} no conoce ningún hechizo.")
            input("Presiona Enter para continuar...")
            return
        
        # Agrupar por nivel para facilitar visualización
        spells_by_level = {}
        for spell in character_spells:
            if spell.level not in spells_by_level:
                spells_by_level[spell.level] = []
            spells_by_level[spell.level].append(spell)
        
        # Mostrar hechizos agrupados por nivel
        for level in sorted(spells_by_level.keys()):
            level_name = "Trucos" if level == 0 else f"Nivel {level}"
            print(f"\n{level_name}:")
            for i, spell in enumerate(sorted(spells_by_level[level], key=lambda s: s.name), 1):
                damage_str = f" - {spell.damage_dice} {spell.damage_type}" if spell.damage_dice else ""
                healing_str = f" - Cura {spell.healing_dice}" if spell.healing_dice else ""
                print(f"  {i}. {spell.name} ({spell.spell_type}){damage_str}{healing_str}")
        
        print()
        
        # Seleccionar un hechizo
        spell_index = int(self.get_input(
            "Selecciona un hechizo para eliminar (0 para cancelar): ", 
            lambda x: x == "0" or (x.isdigit() and 1 <= int(x) <= len(character_spells))
        ))
        
        if spell_index == 0:
            return
        
        spell = character_spells[spell_index - 1]
        
        # Confirmar eliminación
        confirm = self.get_input(
            f"¿Estás seguro de que quieres eliminar el hechizo '{spell.name}' de {self.character.name}? (s/n): ", 
            lambda x: x.lower() in ["s", "n"]
        ).lower()
        
        if confirm == "s":
            result = self.character.remove_spell(spell.name)
            print(f"\n{result}")
        else:
            print("\nOperación cancelada.")
        
        input("\nPresiona Enter para continuar...")