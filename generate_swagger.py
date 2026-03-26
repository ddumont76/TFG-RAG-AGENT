#!/usr/bin/env python3
"""
Script para generar archivos de documentación Swagger/OpenAPI de la API.
"""

import json
import yaml
import requests
import sys

def generate_swagger_files():
    """Genera archivos swagger.json y swagger.yaml desde la API en ejecución."""
    try:
        # Obtener la especificación OpenAPI desde la API
        response = requests.get("http://localhost:8000/openapi.json")
        response.raise_for_status()
        
        openapi_spec = response.json()
        
        # Guardar como JSON
        with open("swagger.json", "w", encoding="utf-8") as f:
            json.dump(openapi_spec, f, indent=2, ensure_ascii=False)
        print("✅ Generado swagger.json")
        
        # Guardar como YAML
        with open("swagger.yaml", "w", encoding="utf-8") as f:
            yaml.dump(openapi_spec, f, default_flow_style=False, allow_unicode=True)
        print("✅ Generado swagger.yaml")
        
        print("\n📖 Archivos de documentación generados exitosamente!")
        print("   - swagger.json (JSON)")
        print("   - swagger.yaml (YAML)")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: La API no está ejecutándose en http://localhost:8000")
        print("   Ejecuta primero: venv\\Scripts\\python.exe run_api.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error generando documentación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_swagger_files()