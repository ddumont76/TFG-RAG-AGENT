import subprocess
import sys

print("Descargando modelo phi-4 desde Ollama...")
print("Esto puede tomar varios minutos (depende de tu conexión y velocidad del disco)...\n")

result = subprocess.run(['ollama', 'pull', 'phi-4'], 
                       capture_output=False, text=True)

if result.returncode == 0:
    print("\n✅ Modelo phi-4 descargado exitosamente")
else:
    print("\n❌ Error descargando phi-4")
    sys.exit(1)

# Verificar que está instalado
print("\nVerificando modelos instalados...")
result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
print(result.stdout)
