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