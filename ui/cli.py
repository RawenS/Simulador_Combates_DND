# ui/cli.py
import os
import re
import random
# Importaciones absolutas
from core.dice import Dice
from models.character import Character
from models.monster import Monster
from ui.spell_manager import SpellManager
from core.combat_engine import CombatEngine
from persistence.data_manager import DataManager
from ui.cheat_menu import CheatMenu


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
                "6": "Gestionar Hechizos",  # Nueva opción
                "7": "Salir"  # Cambiar número
            })
            
            choice = self.get_input("Elige una opción: ", lambda x: x in ["1", "2", "3", "4", "5", "6", "7"])
            
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
                self.spell_manager_menu()
            elif choice == "7":
                self.running = False
                print("¡Gracias por jugar!")
    
    def spell_manager_menu(self):
        """Abrir el gestor de hechizos."""
        spell_manager = SpellManager()
        spell_manager.run()
    
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
            
            # Asignar hechizos al personaje
            add_spells = self.get_input("\n¿Quieres asignar hechizos a este personaje? (s/n): ", 
                                      lambda x: x.lower() in ["s", "n"]).lower() == "s"
            
            if add_spells:
                spell_manager = SpellManager(character)
                print("\nAsignando hechizos a", character.name)
                while True:
                    spell_manager.assign_spell_to_character()
                    more_spells = self.get_input("\n¿Quieres asignar más hechizos? (s/n): ", 
                                               lambda x: x.lower() in ["s", "n"]).lower() == "s"
                    if not more_spells:
                        break
            
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
        
        # Mostrar hechizos conocidos
        if character.spells:
            print("\nHechizos conocidos:")
            spells_by_level = {}
            for spell in character.spells:
                if spell.level not in spells_by_level:
                    spells_by_level[spell.level] = []
                spells_by_level[spell.level].append(spell)
            
            for level in sorted(spells_by_level.keys()):
                level_name = "Trucos" if level == 0 else f"Nivel {level}"
                print(f"  {level_name}:")
                for spell in sorted(spells_by_level[level], key=lambda s: s.name):
                    print(f"    - {spell.name}")
        else:
            print("\nNo conoce ningún hechizo.")
        
        # Mostrar espacios de hechizo
        if character.spell_slots:
            print("\nEspacios de hechizo:")
            for level, slots in sorted(character.spell_slots.items()):
                print(f"  Nivel {level}: {slots}")
        
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
            "6": "Hechizos",  # Nueva opción
            "7": "Volver"  # Cambiar numeración
        })
        
        choice = self.get_input("Elige una opción: ", lambda x: x in ["1", "2", "3", "4", "5", "6", "7"])
        
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
                # Actualizar espacios de hechizo
                character.spell_slots = character.calculate_spell_slots()
            
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
            
            elif choice == "6":  # Gestionar hechizos
                spell_manager = SpellManager(character)
                print("\nGestionando hechizos de", character.name)
                spell_submenu = True
                
                while spell_submenu:
                    self.print_header(f"Gestión de Hechizos de {character.name}")
                    print("1. Asignar nuevo hechizo")
                    print("2. Eliminar hechizo")
                    print("3. Ver hechizos conocidos")
                    print("4. Volver")
                    
                    spell_choice = self.get_input("\nElige una opción: ", lambda x: x in ["1", "2", "3", "4"])
                    
                    if spell_choice == "1":
                        spell_manager.assign_spell_to_character()
                    elif spell_choice == "2":
                        spell_manager.remove_spell_from_character()
                    elif spell_choice == "3":
                        # Mostrar hechizos conocidos
                        if character.spells:
                            print("\nHechizos conocidos:")
                            spells_by_level = {}
                            for spell in character.spells:
                                if spell.level not in spells_by_level:
                                    spells_by_level[spell.level] = []
                                spells_by_level[spell.level].append(spell)
                            
                            for level in sorted(spells_by_level.keys()):
                                level_name = "Trucos" if level == 0 else f"Nivel {level}"
                                print(f"  {level_name}:")
                                for spell in sorted(spells_by_level[level], key=lambda s: s.name):
                                    print(f"    - {spell.name}")
                            input("\nPresiona Enter para continuar...")
                        else:
                            print("\nEl personaje no conoce ningún hechizo.")
                            input("Presiona Enter para continuar...")
                    elif spell_choice == "4":
                        spell_submenu = False
            
            elif choice == "7":
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
        
        # Mostrar hechizos conocidos
        if monster.spells:
            print("\nHechizos conocidos:")
            spells_by_level = {}
            for spell in monster.spells:
                if spell.level not in spells_by_level:
                    spells_by_level[spell.level] = []
                spells_by_level[spell.level].append(spell)
            
            for level in sorted(spells_by_level.keys()):
                level_name = "Trucos" if level == 0 else f"Nivel {level}"
                print(f"  {level_name}:")
                for spell in sorted(spells_by_level[level], key=lambda s: s.name):
                    print(f"    - {spell.name}")
        
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
                # Actualizar CD de hechizos
                monster.spell_dc = 10 + monster.challenge_rating // 2
            
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
                input("Presiona Enter para continuar...")
                return
            
            # Agrupar hechizos por nivel
            spells_by_level = {}
            for spell in character.spells:
                if spell.level not in spells_by_level:
                    spells_by_level[spell.level] = []
                spells_by_level[spell.level].append(spell)
            
            # Mostrar hechizos disponibles
            print("\nHechizos disponibles:")
            for level in sorted(spells_by_level.keys()):
                level_name = "Trucos" if level == 0 else f"Nivel {level}"
                
                # Mostrar información de espacios de hechizo para niveles > 0
                slots_info = ""
                if level > 0:
                    available_slots = character.get_available_spell_slots(level)
                    slots_info = f" ({available_slots} espacios disponibles)"
                
                print(f"\n{level_name}{slots_info}:")
                
                for i, spell in enumerate(sorted(spells_by_level[level], key=lambda s: s.name), 1):
                    damage_info = f" - {spell.damage_dice} {spell.damage_type}" if spell.damage_dice else ""
                    healing_info = f" - Cura {spell.healing_dice}" if spell.healing_dice else ""
                    print(f"  {i}. {spell.name}{damage_info}{healing_info}")
            
            # Seleccionar hechizo
            try:
                spell_choice = int(self.get_input("\nSelecciona un hechizo (0 para cancelar): ", 
                                                lambda x: x == "0" or (x.isdigit() and int(x) > 0)))
                
                if spell_choice == 0:
                    return
                
                # Encontrar el hechizo seleccionado
                selected_spell = None
                spell_index = 1
                
                for level in sorted(spells_by_level.keys()):
                    level_spells = sorted(spells_by_level[level], key=lambda s: s.name)
                    for spell in level_spells:
                        if spell_index == spell_choice:
                            selected_spell = spell
                            break
                        spell_index += 1
                    
                    if selected_spell:
                        break
                
                if not selected_spell:
                    print("Hechizo no encontrado.")
                    input("Presiona Enter para continuar...")
                    return
                
                # Verificar si hay espacios de hechizo disponibles
                spell_level = selected_spell.level
                if spell_level > 0:
                    available_slots = character.get_available_spell_slots(spell_level)
                    
                    if available_slots <= 0:
                        print(f"\nNo tienes espacios de hechizo de nivel {spell_level} disponibles.")
                        input("Presiona Enter para continuar...")
                        return
                    
                    # Opción para lanzar a nivel superior
                    can_upcast = False
                    for higher_level in range(spell_level + 1, 10):
                        if character.get_available_spell_slots(higher_level) > 0:
                            can_upcast = True
                            break
                    
                    if can_upcast:
                        upcast = self.get_input("\n¿Lanzar a nivel superior? (s/n): ", 
                                              lambda x: x.lower() in ["s", "n"]).lower() == "s"
                        
                        if upcast:
                            # Mostrar niveles disponibles
                            print("\nNiveles disponibles:")
                            for level in range(spell_level + 1, 10):
                                slots = character.get_available_spell_slots(level)
                                if slots > 0:
                                    print(f"  {level}: {slots} espacios")
                            
                            cast_level = int(self.get_input("\nSelecciona nivel: ", 
                                                          lambda x: x.isdigit() and int(x) > spell_level and 
                                                                    character.get_available_spell_slots(int(x)) > 0))
                        else:
                            cast_level = spell_level
                    else:
                        cast_level = spell_level
                else:
                    # Los trucos siempre se lanzan a nivel 0
                    cast_level = 0
                
                # Seleccionar objetivo si es necesario
                target = None
                
                if selected_spell.healing_dice:
                    # Para hechizos de curación, mostrar personajes como objetivos
                    print("\nObjetivos disponibles:")
                    for i, char in enumerate(self.combat_engine.characters, 1):
                        if char.is_alive:
                            print(f"{i}. {char.name} - {char.current_hp}/{char.max_hp} HP")
                    
                    target_choice = int(self.get_input("\nSelecciona un objetivo: ", 
                                                     lambda x: x.isdigit() and 
                                                               1 <= int(x) <= len(self.combat_engine.characters) and
                                                               self.combat_engine.characters[int(x)-1].is_alive))
                    
                    target = self.combat_engine.characters[target_choice - 1]
                
                elif selected_spell.damage_dice or selected_spell.effects:
                    # Para hechizos ofensivos o de efectos, mostrar monstruos como objetivos predeterminados
                    print("\nObjetivos disponibles:")
                    all_entities = []
                    
                    # Añadir monstruos
                    for i, monster in enumerate(self.combat_engine.monsters, 1):
                        if monster.is_alive:
                            all_entities.append(("monster", i-1))
                            print(f"{len(all_entities)}. {monster.name} (Monstruo)")
                    
                    # Opción para añadir personajes como objetivo
                    if selected_spell.effects:
                        include_characters = self.get_input("\n¿Incluir personajes como posibles objetivos? (s/n): ", 
                                                         lambda x: x.lower() in ["s", "n"]).lower() == "s"
                        
                        if include_characters:
                            # Añadir personajes
                            for i, char in enumerate(self.combat_engine.characters, 1):
                                if char.is_alive and char != character:  # Excluir al lanzador
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
                
                # Lanzar el hechizo
                print(f"\n{character.name} intenta lanzar {selected_spell.name}...")
                input("Presiona Enter para continuar...")
                
                spell_result = character.cast_spell(selected_spell, target, cast_level)
                print(f"\n{spell_result}")
            
            except ValueError as e:
                print(f"\nError: {e}")
                input("Presiona Enter para continuar...")
                return
        
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
        
        # Determinar si tiene hechizos disponibles
        has_spells = hasattr(monster, 'spells') and monster.spells
        
        # Si tiene hechizos, elegir entre ataque normal o hechizo
        if has_spells and random.random() < 0.3:  # 30% de probabilidad de lanzar hechizo
            # Elegir un hechizo aleatorio
            spell = random.choice(monster.spells)
            
            # Elegir un objetivo para el hechizo
            alive_characters = [char for char in self.combat_engine.characters if char.is_alive]
            
            if not alive_characters:
                print(f"{monster.name} no tiene objetivos disponibles.")
                input("Presiona Enter para continuar...")
                self.combat_engine.next_turn()
                return
            
            # Seleccionar un personaje como objetivo
            target = random.choice(alive_characters)
            
            print(f"{monster.name} lanza {spell.name} a {target.name}...")
            input("Presiona Enter para continuar...")
            
            # Lanzar el hechizo
            spell_result = monster.cast_spell(spell, target)
            print(f"\n{spell_result}")
        else:
            # Ataque normal
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