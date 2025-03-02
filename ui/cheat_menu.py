# ui/cheat_menu.py
import os
import random
from models.effect import Effect
from models.spell import Spell
from models.spellbook import SpellBook

class CheatMenu:
    """Menú de trampas para modificar el combate."""
    
    def __init__(self, combat_engine):
        self.combat_engine = combat_engine
        self.spellbook = SpellBook()
    
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
            print("6. Otorgar hechizo")
            print("7. Aplicar efecto")
            print("8. Eliminar efecto")
            print("9. Restaurar recursos (HP/Maná/Espacios de hechizo)")
            print("0. Volver al combate")
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
                self.grant_spell()
            elif choice == "7":
                self.apply_effect()
            elif choice == "8":
                self.remove_effect()
            elif choice == "9":
                self.restore_resources()
            elif choice == "0":
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
            print("3. Modificar nivel")
            print("4. Volver")
            
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
                
                elif choice == "3":
                    current_level = entity.level
                    new_level = int(input(f"Nuevo nivel (actual: {current_level}): ").strip())
                    if 1 <= new_level <= 20:
                        entity.level = new_level
                        # Actualizar espacios de hechizo
                        entity.spell_slots = entity.calculate_spell_slots()
                        print(f"\nNivel de {entity.name} modificado a {new_level}.")
                    else:
                        print("\nEl nivel debe estar entre 1 y 20.")
            
            except ValueError:
                print("\nPor favor, ingresa un número válido.")
        
        else:
            # Monstruo
            print("1. Modificar CA")
            print("2. Modificar estadísticas de ataque")
            print("3. Modificar Challenge Rating")
            print("4. Volver")
            
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
                        import re
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
                
                elif choice == "3":
                    current_cr = entity.challenge_rating
                    new_cr = float(input(f"Nuevo Challenge Rating (actual: {current_cr}): ").strip())
                    entity.challenge_rating = new_cr
                    # Actualizar CD de hechizos
                    entity.spell_dc = 10 + entity.challenge_rating // 2
                    print(f"\nChallenge Rating de {entity.name} modificado a {new_cr}.")
            
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
    
    def grant_spell(self):
        """Otorgar un hechizo a una entidad."""
        entity = self.select_entity()
        
        if not entity:
            return
        
        print(f"\nOtorgar hechizo a {entity.name}")
        
        # Listar hechizos disponibles en el libro de hechizos
        all_spells = self.spellbook.spells
        
        if not all_spells:
            print("No hay hechizos disponibles en el libro de hechizos.")
            input("Presiona Enter para continuar...")
            return
        
        # Agrupar por nivel para facilitar la visualización
        spells_by_level = {}
        for spell in all_spells:
            if spell.level not in spells_by_level:
                spells_by_level[spell.level] = []
            spells_by_level[spell.level].append(spell)
        
        # Mostrar hechizos agrupados por nivel
        for level in sorted(spells_by_level.keys()):
            level_name = "Trucos" if level == 0 else f"Nivel {level}"
            print(f"\n{level_name}:")
            
            for i, spell in enumerate(sorted(spells_by_level[level], key=lambda s: s.name), 1):
                print(f"{len(spells_by_level[level]) * level + i}. {spell.name} - {spell.spell_type}")
        
        try:
            spell_index = int(input("\nSelecciona un hechizo (0 para cancelar): ").strip())
            
            if spell_index == 0:
                return
            
            # Encontrar el hechizo seleccionado
            selected_spell = None
            counter = 1
            
            for level in sorted(spells_by_level.keys()):
                for spell in sorted(spells_by_level[level], key=lambda s: s.name):
                    if counter == spell_index:
                        selected_spell = spell
                        break
                    counter += 1
                
                if selected_spell:
                    break
            
            if selected_spell:
                # Verificar si la entidad ya conoce el hechizo
                if hasattr(entity, 'spells'):
                    if any(s.name.lower() == selected_spell.name.lower() for s in entity.spells):
                        print(f"\n{entity.name} ya conoce el hechizo {selected_spell.name}.")
                    else:
                        entity.add_spell(selected_spell)
                        print(f"\n¡{entity.name} ha aprendido el hechizo {selected_spell.name}!")
                else:
                    print(f"\n{entity.name} no puede aprender hechizos.")
            else:
                print("\nHechizo no encontrado.")
        
        except ValueError:
            print("\nPor favor, ingresa un número válido.")
        
        input("\nPresiona Enter para continuar...")
    
    def apply_effect(self):
        """Aplicar un efecto a una entidad."""
        entity = self.select_entity()
        
        if not entity:
            return
        
        print(f"\nAplicar efecto a {entity.name}")
        
        try:
            effect_name = input("Nombre del efecto: ").strip()
            effect_description = input("Descripción del efecto: ").strip()
            effect_duration = int(input("Duración en turnos (-1 para permanente): ").strip())
            effect_type = input("Tipo de efecto (positivo/negativo/neutral): ").strip().lower()
            
            has_modifier = input("¿El efecto modifica algún atributo? (s/n): ").strip().lower() == "s"
            modifier = None
            attribute = None
            value = 0
            
            if has_modifier:
                # Mostrar posibles modificadores
                print("\nPosibles modificadores:")
                print("- ataque: Modificar tiradas de ataque")
                print("- daño: Modificar daño causado")
                print("- ca: Modificar Clase de Armadura")
                print("- velocidad: Modificar velocidad de movimiento")
                print("- iniciativa: Modificar iniciativa")
                print("- fuerza: Modificar Fuerza")
                print("- destreza: Modificar Destreza")
                print("- constitución: Modificar Constitución")
                print("- inteligencia: Modificar Inteligencia")
                print("- sabiduría: Modificar Sabiduría")
                print("- carisma: Modificar Carisma")
                
                modifier = input("\nTipo de modificador: ").strip().lower()
                
                if modifier in ["fuerza", "destreza", "constitución", "inteligencia", "sabiduría", "carisma"]:
                    attribute = modifier
                
                value = int(input("Valor de la modificación: ").strip())
            
            # Crear el efecto
            effect = Effect(
                name=effect_name,
                description=effect_description,
                duration=effect_duration,
                effect_type=effect_type,
                modifier=modifier,
                attribute=attribute,
                value=value
            )
            
            # Aplicar el efecto
            result = effect.apply(entity)
            print(f"\n{result}")
        
        except ValueError:
            print("\nPor favor, ingresa valores válidos.")
        
        input("\nPresiona Enter para continuar...")
    
    def remove_effect(self):
        """Eliminar un efecto de una entidad."""
        entity = self.select_entity()
        
        if not entity:
            return
        
        if not entity.effects:
            print(f"\n{entity.name} no tiene efectos activos.")
            input("\nPresiona Enter para continuar...")
            return
        
        print(f"\nEfectos activos en {entity.name}:")
        
        for i, effect in enumerate(entity.effects, 1):
            remaining = " (Permanente)" if effect.duration == -1 else f" ({effect.remaining_turns} turnos restantes)"
            print(f"{i}. {effect.name}{remaining}: {effect.description}")
        
        try:
            effect_index = int(input("\nSelecciona un efecto para eliminar (0 para cancelar): ").strip())
            
            if effect_index == 0:
                return
            
            if 1 <= effect_index <= len(entity.effects):
                effect = entity.effects[effect_index - 1]
                result = effect.remove(entity)
                print(f"\n{result}")
            else:
                print("\nÍndice de efecto inválido.")
        
        except ValueError:
            print("\nPor favor, ingresa un número válido.")
        
        input("\nPresiona Enter para continuar...")
    
    def restore_resources(self):
        """Restaurar HP, maná y espacios de hechizo de una entidad."""
        entity = self.select_entity()
        
        if not entity:
            return
        
        print(f"\nRestaurar recursos de {entity.name}")
        print("1. Restaurar HP completo")
        print("2. Restaurar maná completo")
        print("3. Restaurar espacios de hechizo")
        print("4. Restaurar todo")
        print("5. Cancelar")
        
        choice = input("\nElige una opción: ").strip()
        
        if choice == "1":
            # Restaurar HP
            old_hp = entity.current_hp
            entity.current_hp = entity.max_hp
            print(f"\n{entity.name} ha recuperado {entity.max_hp - old_hp} puntos de vida. (HP: {entity.current_hp}/{entity.max_hp})")
        
        elif choice == "2":
            # Restaurar maná si es personaje
            if hasattr(entity, 'current_mana'):
                old_mana = entity.current_mana
                entity.current_mana = entity.max_mana
                print(f"\n{entity.name} ha recuperado {entity.max_mana - old_mana} puntos de maná. (Maná: {entity.current_mana}/{entity.max_mana})")
            else:
                print(f"\n{entity.name} no utiliza maná.")
        
        elif choice == "3":
            # Restaurar espacios de hechizo
            if hasattr(entity, 'spell_slots'):
                if hasattr(entity, 'calculate_spell_slots'):
                    # Para personajes
                    entity.spell_slots = entity.calculate_spell_slots()
                else:
                    # Para monstruos, establecer un valor arbitrario
                    for level in range(1, 10):
                        if level in entity.spell_slots:
                            entity.spell_slots[level] = max(1, entity.challenge_rating // 2)
                
                print(f"\nEspacios de hechizo de {entity.name} restaurados.")
                for level, slots in sorted(entity.spell_slots.items()):
                    print(f"  Nivel {level}: {slots} espacios")
            else:
                print(f"\n{entity.name} no utiliza espacios de hechizo.")
        
        elif choice == "4":
            # Restaurar todo
            # HP
            old_hp = entity.current_hp
            entity.current_hp = entity.max_hp
            
            # Maná si aplica
            if hasattr(entity, 'current_mana'):
                old_mana = entity.current_mana
                entity.current_mana = entity.max_mana
                print(f"\n{entity.name} ha recuperado {entity.max_mana - old_mana} puntos de maná.")
            
            # Espacios de hechizo si aplica
            if hasattr(entity, 'spell_slots'):
                if hasattr(entity, 'calculate_spell_slots'):
                    entity.spell_slots = entity.calculate_spell_slots()
                else:
                    for level in range(1, 10):
                        if level in entity.spell_slots:
                            entity.spell_slots[level] = max(1, entity.challenge_rating // 2)
                
                print(f"\nEspacios de hechizo de {entity.name} restaurados.")
            
            print(f"\n{entity.name} ha restaurado todos sus recursos.")
        
        elif choice == "5":
            print("\nOperación cancelada.")
        
        else:
            print("\nOpción inválida.")
        
        input("\nPresiona Enter para continuar...")