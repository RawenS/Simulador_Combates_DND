# core/dice.py
import random
import re

class Dice:
    """Clase para manejar tiradas de dados."""
    
    @staticmethod
    def roll(dice_notation):
        """
        Tirar dados basados en la notación estándar de dados (ej., "3d6+2").
        
        Args:
            dice_notation (str): La notación de dados para tirar (ej., "3d6+2")
            
        Returns:
            tuple: (total, rolls, modifier) donde total es la suma de todas las tiradas más el modificador,
                  rolls es una lista de resultados individuales de dados, y modifier es el modificador estático
        """
        # Analizar la notación de dados
        pattern = r"(\d+)d(\d+)([+-]\d+)?"
        match = re.match(pattern, dice_notation.lower())
        
        if not match:
            raise ValueError(f"Notación de dados inválida: {dice_notation}")
        
        num_dice = int(match.group(1))
        dice_type = int(match.group(2))
        modifier_str = match.group(3) or "+0"
        modifier = int(modifier_str)
        
        # Tirar los dados
        rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        return total, rolls, modifier
    
    @staticmethod
    def advantage():
        """Tirar con ventaja (tirar d20 dos veces, tomar el mayor)."""
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        return max(roll1, roll2), (roll1, roll2)
    
    @staticmethod
    def disadvantage():
        """Tirar con desventaja (tirar d20 dos veces, tomar el menor)."""
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        return min(roll1, roll2), (roll1, roll2)