# main.py
# Usa importaciones relativas adecuadas para cuando se ejecuta como módulo
from ui.cli import CLI

def main():
    """Punto de entrada principal de la aplicación."""
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    # Si se ejecuta directamente, añadir el directorio raíz al path
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ui.cli import CLI
    main()