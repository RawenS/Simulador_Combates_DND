# models/effect.py
class Effect:
    """Clase que representa un efecto o estado que puede afectar a una entidad."""
    
    def __init__(self, name, description, duration, effect_type, 
                 modifier=None, attribute=None, value=0):
        """
        Inicializar un nuevo efecto.
        
        Args:
            name (str): Nombre del efecto (ej. "Envenenado", "Bendecido").
            description (str): Descripción del efecto.
            duration (int): Duración en turnos (-1 para efectos permanentes).
            effect_type (str): Tipo de efecto (positivo, negativo, neutral).
            modifier (str, optional): Tipo de modificación (ataque, daño, CA, etc.).
            attribute (str, optional): Atributo afectado si aplica.
            value (int, optional): Valor de la modificación. Por defecto 0.
        """
        self.name = name
        self.description = description
        self.duration = duration
        self.effect_type = effect_type
        self.modifier = modifier
        self.attribute = attribute
        self.value = value
        self.remaining_turns = duration
    
    def apply(self, entity):
        """
        Aplicar el efecto a una entidad.
        
        Args:
            entity: La entidad a la que se aplica el efecto.
            
        Returns:
            str: Mensaje describiendo el efecto aplicado.
        """
        # Añadir el efecto a la lista de efectos de la entidad
        entity.effects.append(self)
        
        return f"{entity.name} está afectado por {self.name}. {self.description}"
    
    def remove(self, entity):
        """
        Eliminar el efecto de una entidad.
        
        Args:
            entity: La entidad de la que se elimina el efecto.
            
        Returns:
            str: Mensaje describiendo el efecto eliminado.
        """
        # Eliminar el efecto de la lista de efectos de la entidad
        if self in entity.effects:
            entity.effects.remove(self)
        
        return f"El efecto {self.name} ha terminado para {entity.name}."
    
    def tick(self, entity):
        """
        Avanzar un turno en la duración del efecto.
        
        Args:
            entity: La entidad afectada.
            
        Returns:
            bool: True si el efecto sigue activo, False si ha terminado.
        """
        # Si es un efecto permanente, no disminuye
        if self.duration == -1:
            return True
        
        self.remaining_turns -= 1
        
        if self.remaining_turns <= 0:
            self.remove(entity)
            return False
        return True
    
    def get_modifier_value(self):
        """
        Obtener el valor de modificación del efecto.
        
        Returns:
            int: El valor de la modificación.
        """
        return self.value
    
    def to_dict(self):
        """Convertir el efecto a un diccionario para serialización."""
        return {
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "effect_type": self.effect_type,
            "modifier": self.modifier,
            "attribute": self.attribute,
            "value": self.value,
            "remaining_turns": self.remaining_turns
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crear un efecto a partir de un diccionario."""
        effect = cls(
            name=data["name"],
            description=data["description"],
            duration=data["duration"],
            effect_type=data["effect_type"],
            modifier=data.get("modifier"),
            attribute=data.get("attribute"),
            value=data.get("value", 0)
        )
        effect.remaining_turns = data.get("remaining_turns", effect.duration)
        return effect