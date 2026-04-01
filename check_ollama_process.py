import psutil

print("Procesos de Ollama en ejecución:")
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    if 'ollama' in proc.name().lower():
        print(f"PID: {proc.pid}, Nombre: {proc.name()}")
        if proc.cmdline():
            print(f"  Comando: {' '.join(proc.cmdline()[:3])}")

print("\nProcesos usando puerto 11434:")
for conn in psutil.net_connections():
    if conn.laddr.port == 11434:
        try:
            p = psutil.Process(conn.pid)
            print(f"PID {conn.pid}: {p.name()}")
        except:
            print(f"PID {conn.pid}: (proceso terminado)")
