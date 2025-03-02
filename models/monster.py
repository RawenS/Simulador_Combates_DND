# models/monster.py
from models.entity import Entity
from core.dice import Dice

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
        
        # Habilidades especiales y hechizos
        self.abilities = []
        self.spells = []
        self.spell_slots = {}
        self.spell_dc = 10 + self.challenge_rating // 2
    
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
    
    def add_spell(self, spell):
        """
        Añadir un hechizo al repertorio del monstruo.
        
        Args:
            spell (Spell): El hechizo a añadir.
            
        Returns:
            str: Mensaje de éxito o error.
        """
        # Verificar si ya conoce el hechizo
        if any(s.name.lower() == spell.name.lower() for s in self.spells):
            return f"{self.name} ya conoce el hechizo {spell.name}."
        
        self.spells.append(spell)
        return f"{self.name} ha adquirido el hechizo {spell.name}!"

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
        
        # Verificar espacios de hechizo si es necesario para el monstruo
        if cast_level > 0 and self.spell_slots:
            if self.spell_slots.get(cast_level, 0) <= 0:
                return f"{self.name} no tiene espacios de hechizo de nivel {cast_level} disponibles!"
            self.spell_slots[cast_level] -= 1
        
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
                # Para monstruos, usar un valor fijo basado en el CR
                modifier = self.challenge_rating // 2
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
                spell_attack = attack_roll + self.attack_bonus
                
                result += f"\nTirada de ataque: {attack_roll} + {self.attack_bonus} = {spell_attack} vs CA {target.armor_class}"
                
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
                save_dc = self.spell_dc
                save_roll = random.randint(1, 20)
                
                # Determinar el modificador del objetivo basado en el atributo requerido
                # (Esto es una simplificación)
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
            "abilities": self.abilities,
            "spells": [spell.to_dict() for spell in self.spells],
            "spell_slots": self.spell_slots,
            "spell_dc": self.spell_dc,
            "effects": [effect.to_dict() for effect in self.effects]
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
        
        # Cargar hechizos
        from models.spell import Spell
        monster.spells = [Spell.from_dict(spell_data) for spell_data in data.get("spells", [])]
        
        monster.spell_slots = data.get("spell_slots", {})
        monster.spell_dc = data.get("spell_dc", 10 + monster.challenge_rating // 2)
        
        # Cargar efectos
        from models.effect import Effect
        monster.effects = [Effect.from_dict(effect_data) for effect_data in data.get("effects", [])]
        
        return monster