# models/character.py
from models.entity import Entity
from core.dice import Dice

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
        self.spells = []  # Ahora almacena objetos Spell en lugar de diccionarios
        self.abilities = []
        
        # Sistema de magia
        self.max_mana = self.calculate_max_mana()
        self.current_mana = self.max_mana
        self.spell_slots = self.calculate_spell_slots()
    
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
    
    def calculate_max_mana(self):
        """Calcular puntos de maná máximos basados en nivel e inteligencia."""
        base_mana = self.level * 10
        int_bonus = self._get_modifier(self.intelligence) * 5
        return max(0, base_mana + int_bonus)

    def calculate_spell_slots(self):
        """Calcular espacios de hechizo basados en el nivel del personaje."""
        # Implementación simplificada de la tabla de espacios de hechizo
        slots = {}
        
        # Nivel 1
        if self.level >= 1:
            slots[1] = 2
        
        # Nivel 2
        if self.level >= 3:
            slots[2] = 2
        
        # Nivel 3
        if self.level >= 5:
            slots[3] = 2
        
        # Nivel 4
        if self.level >= 7:
            slots[4] = 1
        
        # Nivel 5
        if self.level >= 9:
            slots[5] = 1
        
        # Incrementos adicionales basados en nivel
        if self.level >= 2:
            slots[1] += 1
        if self.level >= 4:
            slots[1] += 1
            if 2 in slots:
                slots[2] += 1
        if self.level >= 6:
            if 3 in slots:
                slots[3] += 1
        if self.level >= 8:
            if 4 in slots:
                slots[4] += 1
        if self.level >= 10:
            if 5 in slots:
                slots[5] += 1
        
        return slots
    
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
    
    def add_spell(self, spell):
        """
        Añadir un hechizo al repertorio del personaje.
        
        Args:
            spell (Spell): El hechizo a añadir.
            
        Returns:
            str: Mensaje de éxito o error.
        """
        # Verificar si ya conoce el hechizo
        if any(s.name.lower() == spell.name.lower() for s in self.spells):
            return f"{self.name} ya conoce el hechizo {spell.name}."
        
        self.spells.append(spell)
        return f"{self.name} ha aprendido el hechizo {spell.name}!"

    def remove_spell(self, spell_name):
        """
        Eliminar un hechizo del repertorio del personaje.
        
        Args:
            spell_name (str): Nombre del hechizo a eliminar.
            
        Returns:
            str: Mensaje de éxito o error.
        """
        initial_count = len(self.spells)
        self.spells = [s for s in self.spells if s.name.lower() != spell_name.lower()]
        
        if len(self.spells) < initial_count:
            return f"{self.name} ha olvidado el hechizo {spell_name}."
        return f"{self.name} no conoce el hechizo {spell_name}."

    def get_spells_by_level(self, level):
        """
        Obtener todos los hechizos de un nivel específico.
        
        Args:
            level (int): Nivel de los hechizos a obtener.
            
        Returns:
            list: Lista de hechizos del nivel especificado.
        """
        return [spell for spell in self.spells if spell.level == level]

    def get_available_spell_slots(self, level):
        """
        Obtener los espacios de hechizo disponibles para un nivel.
        
        Args:
            level (int): Nivel de hechizo.
            
        Returns:
            int: Número de espacios disponibles.
        """
        return self.spell_slots.get(level, 0)

    def use_spell_slot(self, level):
        """
        Usar un espacio de hechizo de un nivel específico.
        
        Args:
            level (int): Nivel del espacio a usar.
            
        Returns:
            bool: True si se usó con éxito, False si no hay espacios disponibles.
        """
        if level == 0:  # Los trucos no gastan espacios
            return True
        
        if self.spell_slots.get(level, 0) > 0:
            self.spell_slots[level] -= 1
            return True
        return False
    
    def cast_spell(self, spell, target=None, spell_level=None):
        """
        Lanzar un hechizo.
        
        Args:
            spell (Spell): El hechizo a lanzar.
            target (Entity, optional): Objetivo del hechizo si es necesario.
            spell_level (int, optional): Nivel al que lanzar el hechizo (para potenciar).
            
        Returns:
            str: Resultado del lanzamiento del hechizo.
        """
        import random
        
        if not self.is_alive:
            return f"{self.name} está derrotado y no puede lanzar hechizos!"
        
        # Verificar si conoce el hechizo
        if spell not in self.spells:
            return f"{self.name} no conoce el hechizo {spell.name}!"
        
        # Determinar el nivel de lanzamiento
        cast_level = spell_level or spell.level
        
        # Verificar espacios de hechizo
        if cast_level > 0 and not self.use_spell_slot(cast_level):
            return f"{self.name} no tiene espacios de hechizo de nivel {cast_level} disponibles!"
        
        # Construir el mensaje de lanzamiento
        result = f"{self.name} lanza {spell.name}"
        if cast_level > spell.level:
            result += f" a nivel {cast_level}"
        result += "!"
        
        # Aplicar efectos del hechizo según su tipo
        if spell.healing_dice and target:
            # Escalar curación si se lanza a nivel superior
            healing_formula = spell.healing_dice
            if cast_level > spell.level:
                # Añadir dados adicionales por nivel
                level_diff = cast_level - spell.level
                # Extraer el número de dados y tipo
                dice_parts = spell.healing_dice.split('d')
                if len(dice_parts) == 2 and dice_parts[0].isdigit():
                    num_dice = int(dice_parts[0]) + level_diff
                    dice_type = dice_parts[1]
                    healing_formula = f"{num_dice}d{dice_type}"
            
            # Calcular curación
            healing_roll, dice_rolls, mod = Dice.roll(healing_formula)
            if "modificador" in healing_formula:
                # Añadir modificador de habilidad
                modifier = self._get_modifier(self.wisdom)  # Usar sabiduría como estándar
                healing_roll += modifier
            
            # Aplicar curación
            heal_message = target.heal(healing_roll)
            result += f"\n{heal_message}"
        
        elif spell.damage_dice and target:
            # Escalar daño si se lanza a nivel superior
            damage_formula = spell.damage_dice
            if cast_level > spell.level:
                # Añadir dados adicionales por nivel
                level_diff = cast_level - spell.level
                # Extraer el número de dados y tipo
                dice_parts = spell.damage_dice.split('d')
                if len(dice_parts) == 2 and dice_parts[0].isdigit():
                    num_dice = int(dice_parts[0]) + level_diff
                    dice_type = dice_parts[1]
                    damage_formula = f"{num_dice}d{dice_type}"
            
            # Calcular daño
            damage_roll, dice_rolls, mod = Dice.roll(damage_formula)
            
            # Si requiere tirada de ataque
            if spell.attack_roll:
                attack_roll = random.randint(1, 20)
                spell_mod = self._get_modifier(self.intelligence)  # Usar inteligencia como estándar
                spell_attack = attack_roll + spell_mod + self.proficiency_bonus
                
                result += f"\nTirada de ataque: {attack_roll} + {spell_mod} + {self.proficiency_bonus} = {spell_attack} vs CA {target.armor_class}"
                
                if spell_attack >= target.armor_class:
                    result += f"\n¡IMPACTO! Daño: {'+'.join(map(str, dice_rolls))} ({sum(dice_rolls)}) = {damage_roll} de daño {spell.damage_type}"
                    target.take_damage(damage_roll)
                else:
                    result += "\n¡FALLO!"
                    return result
            
            # Si requiere tirada de salvación
            elif spell.saving_throw:
                result += f"\n{target.name} debe realizar una tirada de salvación de {spell.saving_throw}"
                
                # Simular la tirada de salvación (esto sería diferente en un combate real)
                save_dc = 8 + self.proficiency_bonus + self._get_modifier(self.intelligence)
                save_roll = random.randint(1, 20)
                
                # Determinar el modificador del objetivo basado en el atributo requerido
                # (Esto es una simplificación, en un caso real se usaría el modificador del objetivo)
                target_mod = 0
                result += f"\nCD de salvación: {save_dc}, Tirada: {save_roll} + {target_mod} = {save_roll + target_mod}"
                
                if save_roll + target_mod >= save_dc:
                    # Éxito en la salvación (posiblemente mitiga el daño)
                    reduced_damage = damage_roll // 2
                    result += f"\n¡ÉXITO en la salvación! Daño reducido: {reduced_damage} de daño {spell.damage_type}"
                    target.take_damage(reduced_damage)
                else:
                    # Fallo en la salvación
                    result += f"\n¡FALLO en la salvación! Daño: {damage_roll} de daño {spell.damage_type}"
                    target.take_damage(damage_roll)
            
            # Daño directo sin tiradas
            else:
                result += f"\nDaño: {damage_roll} de daño {spell.damage_type}"
                target.take_damage(damage_roll)
        
        # Aplicar efectos adicionales si hay
        if spell.effects and target:
            from models.effect import Effect
            for effect_data in spell.effects:
                # Crear y aplicar el efecto
                effect = Effect(
                    name=effect_data.get("name", "Efecto desconocido"),
                    description=effect_data.get("description", ""),
                    duration=effect_data.get("duration", 1),
                    effect_type=effect_data.get("effect_type", "neutral"),
                    modifier=effect_data.get("modifier"),
                    attribute=effect_data.get("attribute"),
                    value=effect_data.get("value", 0)
                )
                effect_message = effect.apply(target)
                result += f"\n{effect_message}"
        
        return result
    
    def add_weapon(self, weapon):
        """Equipar un arma."""
        self.weapon = weapon
        return f"{self.name} equipa {weapon['name']}!"
    
    def rest_short(self):
        """Tomar un descanso corto."""
        # Restaurar una parte de HP
        healing = max(1, self.level)
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + healing)
        
        # Restaurar una parte del maná
        mana_recovery = max(1, self._get_modifier(self.intelligence) * 2)
        old_mana = self.current_mana
        self.current_mana = min(self.max_mana, self.current_mana + mana_recovery)
        
        result = f"{self.name} toma un descanso corto."
        if old_hp < self.current_hp:
            result += f"\nRecupera {self.current_hp - old_hp} puntos de vida."
        if old_mana < self.current_mana:
            result += f"\nRecupera {self.current_mana - old_mana} puntos de maná."
        
        return result
    
    def rest_long(self):
        """Tomar un descanso largo."""
        # Restaurar HP y espacios de hechizos
        old_hp = self.current_hp
        self.current_hp = self.max_hp
        
        # Restaurar maná
        old_mana = self.current_mana
        self.current_mana = self.max_mana
        
        # Reiniciar espacios de hechizos
        self.spell_slots = self.calculate_spell_slots()
        
        # Eliminar efectos temporales
        removed_effects = []
        for effect in list(self.effects):
            if effect.duration != -1:  # Si no es permanente
                self.effects.remove(effect)
                removed_effects.append(effect.name)
        
        result = f"{self.name} toma un descanso largo y está completamente restaurado!"
        if old_hp < self.max_hp:
            result += f"\nRecuperó {self.max_hp - old_hp} puntos de vida."
        if old_mana < self.max_mana:
            result += f"\nRecuperó {self.max_mana - old_mana} puntos de maná."
        if removed_effects:
            result += f"\nSe han eliminado los siguientes efectos: {', '.join(removed_effects)}."
        
        return result
    
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
            "spells": [spell.to_dict() for spell in self.spells],
            "abilities": self.abilities,
            "spell_slots": self.spell_slots,
            "max_mana": self.max_mana,
            "current_mana": self.current_mana,
            "effects": [effect.to_dict() for effect in self.effects]
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
        
        # Cargar hechizos
        from models.spell import Spell
        character.spells = [Spell.from_dict(spell_data) for spell_data in data.get("spells", [])]
        
        character.abilities = data.get("abilities", [])
        character.spell_slots = data.get("spell_slots", {})
        character.max_mana = data.get("max_mana", character.calculate_max_mana())
        character.current_mana = data.get("current_mana", character.max_mana)
        
        # Cargar efectos
        from models.effect import Effect
        character.effects = [Effect.from_dict(effect_data) for effect_data in data.get("effects", [])]
        
        return character