# models/spell.py
class Spell:
    """Clase que representa un hechizo individual en el juego."""
    
    def __init__(self, name, description, spell_type, level, cast_time="1 acción", 
                 range="60 pies", components="V, S", duration="Instantáneo",
                 attack_roll=False, saving_throw=None, saving_throw_attribute=None,
                 damage_dice=None, damage_type=None, healing_dice=None,
                 aoe_type=None, aoe_size=None, effects=None):
        """
        Inicializar un nuevo hechizo.
        
        Args:
            name (str): Nombre del hechizo
            description (str): Descripción del efecto del hechizo
            spell_type (str): Tipo de hechizo (ofensivo, defensivo, soporte, utilidad, etc.)
            level (int): Nivel del hechizo (0 para trucos/cantrips)
            cast_time (str, optional): Tiempo de lanzamiento. Por defecto "1 acción".
            range (str, optional): Alcance del hechizo. Por defecto "60 pies".
            components (str, optional): Componentes necesarios (V=verbal, S=somático, M=material). Por defecto "V, S".
            duration (str, optional): Duración del efecto. Por defecto "Instantáneo".
            attack_roll (bool, optional): Si requiere tirada de ataque. Por defecto False.
            saving_throw (str, optional): Tipo de tirada de salvación si aplica (None si no requiere).
            saving_throw_attribute (str, optional): Atributo para la tirada de salvación.
            damage_dice (str, optional): Dados de daño en formato "XdY" (ej. "3d6").
            damage_type (str, optional): Tipo de daño (fuego, hielo, ácido, etc.).
            healing_dice (str, optional): Dados de curación en formato "XdY".
            aoe_type (str, optional): Tipo de área de efecto (cono, esfera, línea, etc.).
            aoe_size (str, optional): Tamaño del área de efecto.
            effects (list, optional): Lista de efectos adicionales que puede causar el hechizo.
        """
        self.name = name
        self.description = description
        self.spell_type = spell_type
        self.level = level
        self.cast_time = cast_time
        self.range = range
        self.components = components
        self.duration = duration
        self.attack_roll = attack_roll
        self.saving_throw = saving_throw
        self.saving_throw_attribute = saving_throw_attribute
        self.damage_dice = damage_dice
        self.damage_type = damage_type
        self.healing_dice = healing_dice
        self.aoe_type = aoe_type
        self.aoe_size = aoe_size
        self.effects = effects or []
    
    def __str__(self):
        """Representación en cadena del hechizo."""
        level_str = "Truco" if self.level == 0 else f"Nivel {self.level}"
        return f"{self.name} ({level_str}): {self.description[:50]}..."
    
    def get_full_description(self):
        """Obtener una descripción completa y formateada del hechizo."""
        level_str = "Truco" if self.level == 0 else f"Nivel {self.level}"
        spell_info = [
            f"Nombre: {self.name}",
            f"Nivel: {level_str}",
            f"Tipo: {self.spell_type}",
            f"Tiempo de lanzamiento: {self.cast_time}",
            f"Alcance: {self.range}",
            f"Componentes: {self.components}",
            f"Duración: {self.duration}"
        ]
        
        if self.attack_roll:
            spell_info.append("Requiere tirada de ataque")
        
        if self.saving_throw:
            spell_info.append(f"Tirada de salvación: {self.saving_throw} ({self.saving_throw_attribute})")
        
        if self.damage_dice:
            spell_info.append(f"Daño: {self.damage_dice} de {self.damage_type}")
        
        if self.healing_dice:
            spell_info.append(f"Curación: {self.healing_dice}")
        
        if self.aoe_type:
            spell_info.append(f"Área de efecto: {self.aoe_type} ({self.aoe_size})")
        
        if self.effects:
            effects_str = ", ".join([effect.get("name", "Efecto") for effect in self.effects])
            spell_info.append(f"Efectos adicionales: {effects_str}")
        
        spell_info.append(f"\nDescripción: {self.description}")
        
        return "\n".join(spell_info)
    
    def to_dict(self):
        """Convertir el hechizo a un diccionario para serialización."""
        return {
            "name": self.name,
            "description": self.description,
            "spell_type": self.spell_type,
            "level": self.level,
            "cast_time": self.cast_time,
            "range": self.range,
            "components": self.components,
            "duration": self.duration,
            "attack_roll": self.attack_roll,
            "saving_throw": self.saving_throw,
            "saving_throw_attribute": self.saving_throw_attribute,
            "damage_dice": self.damage_dice,
            "damage_type": self.damage_type,
            "healing_dice": self.healing_dice,
            "aoe_type": self.aoe_type,
            "aoe_size": self.aoe_size,
            "effects": self.effects
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crear un hechizo a partir de un diccionario."""
        return cls(
            name=data["name"],
            description=data["description"],
            spell_type=data["spell_type"],
            level=data["level"],
            cast_time=data.get("cast_time", "1 acción"),
            range=data.get("range", "60 pies"),
            components=data.get("components", "V, S"),
            duration=data.get("duration", "Instantáneo"),
            attack_roll=data.get("attack_roll", False),
            saving_throw=data.get("saving_throw"),
            saving_throw_attribute=data.get("saving_throw_attribute"),
            damage_dice=data.get("damage_dice"),
            damage_type=data.get("damage_type"),
            healing_dice=data.get("healing_dice"),
            aoe_type=data.get("aoe_type"),
            aoe_size=data.get("aoe_size"),
            effects=data.get("effects", [])
        )