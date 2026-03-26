
import json
import os
from typing import List, Dict


def load_json_folder(folder_path: str) -> List[Dict]:
    print(f"Buscando JSON en: {folder_path}")

    if not os.path.exists(folder_path):
        print(f"❌ La carpeta {folder_path} NO existe.")
        return []

    files = os.listdir(folder_path)
    print(f"Archivos encontrados: {files}")

    data = []
    for filename in files:
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            if os.path.getsize(file_path) == 0:
                print(f"⚠️ El archivo está vacío: {file_path}")
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data.append(json.load(f))
            except json.JSONDecodeError as err:
                print(f"❌ JSON inválido en {file_path}: {err}")
            except Exception as err:
                print(f"❌ Error leyendo {file_path}: {err}")

    print(f"Total JSON cargados: {len(data)}\n")
    return data


def load_tickets() -> List[Dict]:
    return load_json_folder("data/tickets")


def load_confluence_docs() -> List[Dict]:
    return load_json_folder("data/confluence")


if __name__ == "__main__":
    tickets = load_tickets()
    docs = load_confluence_docs()

    print("TICKETS CARGADOS:")
    for t in tickets:
        print(f"- {t['id']}: {t['summary']}")

    print("\nDOCUMENTOS DE CONFLUENCE CARGADOS:")
    for d in docs:
        print(f"- {d['id']}: {d['title']}")