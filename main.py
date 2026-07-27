import os
from dotenv import load_dotenv

load_dotenv()

def main():
    host = os.getenv("HOST")
    print("Iniciando aplicación...")
    print(f"La variable HOST es: '{host}'")
    
    # Aquí puedes poner un punto de interrupción (breakpoint) para probar el debugger de VSCode
    pass

if __name__ == "__main__":
    main()
