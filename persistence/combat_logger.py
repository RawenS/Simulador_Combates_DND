# persistence/combat_logger.py
import datetime
import os

class CombatLogger:
    """Clase para registrar eventos de combate."""
    
    def __init__(self, log_file="combat_log.txt"):
        self.log_file = log_file
        
        # Crear directorio para logs si no existe
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def log(self, message):
        """Registrar un mensaje en el log de combate."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error al escribir en el log: {e}")
    
    def clear_log(self):
        """Limpiar el archivo de log."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")
        except Exception as e:
            print(f"Error al limpiar el log: {e}")
    
    def get_last_entries(self, n=10):
        """Obtener las últimas n entradas del log."""
        try:
            if not os.path.exists(self.log_file):
                return []
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            return lines[-n:] if lines else []
        except Exception as e:
            print(f"Error al leer el log: {e}")
            return []