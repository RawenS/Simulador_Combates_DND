# run_game.py - Colócalo en C:\Users\user\Documents\python_codigos\Simulador_Combates_DND
import sys
import os

# Añadir el directorio actual al path de Python (crucial para encontrar módulos)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ahora las importaciones absolutas funcionarán
from ui.cli import CLI

def main():
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    main()