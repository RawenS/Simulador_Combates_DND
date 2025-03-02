# models/spellbook.py
import json
import os
from models.spell import Spell

class SpellBook:
    """Clase para gestionar la colección de hechizos disponibles."""
    
    def __init__(self, spells_file="data/spells.json"):
        """
        Inicializar el libro de hechizos.
        
        Args:
            spells_file (str, optional): Ruta al archivo JSON de hechizos. Por defecto "data/spells.json".
        """
        self.spells_file = spells_file
        self.spells = []
        self.load_spells()
        
        # Si no hay hechizos cargados, inicializar con hechizos predeterminados
        if not self.spells:
            self.initialize_default_spells()
            self.save_spells()
    
    def load_spells(self):
        """Cargar hechizos desde el archivo JSON."""
        try:
            if os.path.exists(self.spells_file):
                with open(self.spells_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.spells = [Spell.from_dict(spell_data) for spell_data in data]
            else:
                self.spells = []
        except Exception as e:
            print(f"Error al cargar hechizos: {e}")
            self.spells = []
    
    def save_spells(self):
        """Guardar hechizos en el archivo JSON."""
        try:
            # Asegurar que el directorio exista
            os.makedirs(os.path.dirname(self.spells_file), exist_ok=True)
            
            data = [spell.to_dict() for spell in self.spells]
            with open(self.spells_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar hechizos: {e}")
            return False
    
    def add_spell(self, spell):
        """
        Añadir un nuevo hechizo al libro.
        
        Args:
            spell (Spell): El hechizo a añadir.
            
        Returns:
            bool: True si se añadió con éxito, False si ya existía o hubo un error.
        """
        # Verificar si ya existe un hechizo con el mismo nombre
        if any(s.name.lower() == spell.name.lower() for s in self.spells):
            return False
        
        self.spells.append(spell)
        self.save_spells()
        return True
    
    def remove_spell(self, spell_name):
        """
        Eliminar un hechizo del libro.
        
        Args:
            spell_name (str): Nombre del hechizo a eliminar.
            
        Returns:
            bool: True si se eliminó con éxito, False si no se encontró.
        """
        initial_count = len(self.spells)
        self.spells = [s for s in self.spells if s.name.lower() != spell_name.lower()]
        
        if len(self.spells) < initial_count:
            self.save_spells()
            return True
        return False
    
    def get_spell(self, spell_name):
        """
        Obtener un hechizo por su nombre.
        
        Args:
            spell_name (str): Nombre del hechizo a obtener.
            
        Returns:
            Spell: El hechizo si se encuentra, None en caso contrario.
        """
        for spell in self.spells:
            if spell.name.lower() == spell_name.lower():
                return spell
        return None
    
    def get_spells_by_level(self, level):
        """
        Obtener todos los hechizos de un nivel específico.
        
        Args:
            level (int): Nivel de los hechizos a obtener.
            
        Returns:
            list: Lista de hechizos del nivel especificado.
        """
        return [spell for spell in self.spells if spell.level == level]
    
    def get_spells_by_type(self, spell_type):
        """
        Obtener todos los hechizos de un tipo específico.
        
        Args:
            spell_type (str): Tipo de los hechizos a obtener.
            
        Returns:
            list: Lista de hechizos del tipo especificado.
        """
        return [spell for spell in self.spells if spell.spell_type.lower() == spell_type.lower()]
    
    def initialize_default_spells(self):
        """Inicializar el libro con hechizos predeterminados."""
        default_spells = [
            # Trucos (nivel 0)
            Spell(
                name="Prestidigitación",
                description="Creas un efecto mágico menor instantáneo como crear una chispa o limpiar un objeto.",
                spell_type="Utilidad",
                level=0,
                range="10 pies",
                duration="Hasta 1 hora"
            ),
            Spell(
                name="Rayo de Escarcha",
                description="Un rayo de frío azul blanquecino se dirige hacia una criatura, causando daño de frío.",
                spell_type="Ofensivo",
                level=0,
                attack_roll=True,
                damage_dice="1d8",
                damage_type="Frío"
            ),
            
            # Nivel 1
            Spell(
                name="Curar Heridas",
                description="Una criatura que tocas recupera puntos de vida.",
                spell_type="Curación",
                level=1,
                range="Toque",
                healing_dice="1d8+modificador"
            ),
            Spell(
                name="Proyectil Mágico",
                description="Creas tres dardos brillantes que impactan automáticamente en objetivos visibles.",
                spell_type="Ofensivo",
                level=1,
                damage_dice="1d4+1",
                damage_type="Fuerza",
                range="120 pies"
            ),
            
            # Nivel 2
            Spell(
                name="Invisibilidad",
                description="Una criatura que tocas se vuelve invisible.",
                spell_type="Utilidad",
                level=2,
                range="Toque",
                duration="Concentración, hasta 1 hora"
            ),
            
            # Nivel 3
            Spell(
                name="Bola de Fuego",
                description="Una bola de fuego explota en un punto que elijas, causando daño a todas las criaturas en el área.",
                spell_type="Ofensivo",
                level=3,
                range="150 pies",
                damage_dice="8d6",
                damage_type="Fuego",
                saving_throw="Destreza",
                saving_throw_attribute="DEX",
                aoe_type="Esfera",
                aoe_size="20 pies de radio"
            ),
            
            # Nivel 4
            Spell(
                name="Polimorfar",
                description="Transforma una criatura en una nueva forma.",
                spell_type="Transformación",
                level=4,
                range="60 pies",
                duration="Concentración, hasta 1 hora",
                saving_throw="Sabiduría",
                saving_throw_attribute="WIS"
            ),
            
            # Nivel 5
            Spell(
                name="Cono de Frío",
                description="Un estallido de aire frío emana de tus manos, causando daño de frío en un área cónica.",
                spell_type="Ofensivo",
                level=5,
                damage_dice="8d8",
                damage_type="Frío",
                saving_throw="Constitución",
                saving_throw_attribute="CON",
                aoe_type="Cono",
                aoe_size="60 pies"
            )
        ]
        
        self.spells = default_spells