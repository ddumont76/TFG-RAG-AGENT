import os
import subprocess

print("Terminando procesos Ollama...")
result = subprocess.run(['taskkill', '/IM', 'ollama.exe', '/F'], 
                       capture_output=True, text=True)
print(result.stdout)
if result.returncode == 0:
    print("✅ Procesos terminados")
else:
    print("⚠️ No hay procesos de Ollama en ejecución o error:", result.stderr)
