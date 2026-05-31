import os
import json
from datetime import datetime

def load_json_file(file_path):
    """Carga un archivo JSON desde la ruta especificada."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: El archivo '{file_path}' no se encontró.")
    except json.JSONDecodeError:
        raise ValueError(f"Error: El archivo '{file_path}' no contiene un JSON válido.")

def load_all_json_files_sorted(directory_path):
    """Carga todos los archivos JSON de un directorio, ordenados por nombre."""
    json_files = [f for f in os.listdir(directory_path) if f.endswith(".json")]
    json_files.sort()  # Ordenar por nombre de archivo
    return [load_json_file(os.path.join(directory_path, f)) for f in json_files]

def consolidate_provenance(original_clip_path, directory_path):
    """
    Consolida el JSON de provenance.
    
    Parameters:
        original_clip_path (str): Ruta del archivo JSON del clip original.
        directory_path (str): Directorio con archivos JSON que forman parte del provenance.
    
    Returns:
        dict: Un JSON que representa el provenance completo.
    """
    # Cargar el clip original
    original_clip = load_json_file(original_clip_path)
    
    # Cargar los archivos JSON del directorio, ordenados cronológicamente
    provenance_clips = load_all_json_files_sorted(directory_path)
    
    # Crear el JSON consolidado
    provenance_json = {
        "prefix": {
            "prov": "http://www.w3.org/ns/prov#",
            "credibility": "http://example.org/credibility#",
            "prov-said": "http://example.org/prov-said#"
        },
        "entity": {},
        "activity": {},
        "agent": {},
        "wasGeneratedBy": [],
        "used": [],
        "wasDerivedFrom": []
    }

    # Añadir el clip original como entidad
    original_clip_id = original_clip.get("id", "clip_original")
    provenance_json["entity"][original_clip_id] = original_clip

    # Añadir los clips relacionados al provenance en orden
    previous_clip_id = original_clip_id
    for clip in provenance_clips:
        clip_id = clip.get("id", f"clip_{datetime.now().timestamp()}")
        provenance_json["entity"][clip_id] = clip

        # Relación derivada (wasDerivedFrom) entre clips consecutivos
        provenance_json["wasDerivedFrom"].append({
            "prov:generatedEntity": clip_id,
            "prov:usedEntity": previous_clip_id
        })

        # Actualizar el último clip procesado
        previous_clip_id = clip_id

    return provenance_json

def save_json_file(file_path, data):
    """Guarda un archivo JSON."""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print(f"Archivo JSON de provenance guardado en: {file_path}")

# Ejemplo de uso
original_clip_path = "./c_x_2_norm_proc.json"  # Ruta al archivo JSON del clip original
directory_path = "../clips/creibles/X/Caso2/PROV"       # Directorio con los archivos JSON del provenance
output_path = "../clips/creibles/X/Caso2/PROV/provenance.json"           # Ruta para guardar el JSON consolidado

# Consolidar el provenance y guardarlo
provenance_data = consolidate_provenance(original_clip_path, directory_path)
save_json_file(output_path, provenance_data)