import json
import google.generativeai as genai
from datetime import datetime
import time
import os
from config import require_env

# Configurar la API Key
genai.configure(api_key=require_env("GEMINI_API_KEY"))

# Leer el archivo JSON con codificación UTF-8
def load_profile(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: El archivo '{file_path}' no se encontró.")
    except json.JSONDecodeError:
        raise ValueError(f"Error: El archivo '{file_path}' no contiene un JSON válido.")

# Guardar el archivo JSON actualizado
def save_profile(file_path, data, module_name):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"Archivo actualizado guardado en: {file_path}")
    except Exception as e:
        print(f"Error al guardar el archivo JSON: {e}")
        exit(1)

# Procesar la respuesta del modelo y estructurarla en `features.generated_features`
def process_response_to_schema(response_text, profile, processing_start_time, module_name, model_version):
    try:
        lines = response_text.strip().split("\n")
        if len(lines) < 2:
            raise ValueError("La respuesta no contiene las líneas esperadas.")
        
        profession_line = lines[0].strip()
        if not profession_line.lower().startswith("profesion:"):
            raise ValueError("La primera línea no sigue el formato 'Profesion:'.")
        profession = profession_line.split(":", 1)[1].strip()
        
        quality_line = lines[1].strip()
        if not quality_line.lower().startswith("profession_quality:"):
            raise ValueError("La segunda línea no sigue el formato 'profession_quality:'.")
        confidence_level = float(quality_line.split(":", 1)[1].strip())

        processing_end_time = time.time()
        processing_time_ms = int((processing_end_time - processing_start_time) * 1000)

        generated_feature = {
            "module_name": module_name,
            "feature_name": "profession",
            "feature_value": profession,
            "confidence_level": confidence_level,
            "feature_details": {
                "description": "Generated medical profession based on input profile."
            },
            "calculation_details": {
                "calculated_at": datetime.now().isoformat(),
                "calculation_method": f"Gemini Language Model ({model_version})",
                "processing_time_ms": processing_time_ms
            }
        }

        if "features" not in profile:
            profile["features"] = {"generated_features": []}
        if "generated_features" not in profile["features"]:
            profile["features"]["generated_features"] = []
        profile["features"]["generated_features"].append(generated_feature)

        return profile

    except (ValueError, IndexError) as ve:
        print(f"Error al procesar la respuesta: {ve}")
        return None

# Función principal del módulo para procesar el feature
def process_feature(file_path):
    profile = load_profile(file_path)

    # Convertir el JSON a string
    profile_str = json.dumps(profile, ensure_ascii=False, indent=2)

    # Especificar la versión del modelo y el nombre del módulo
    model_version = "gemini-1.5-flash"
    module_name = "MedicalProfessionModule"

    prompt = (
        f"Basado en el siguiente perfil, determina si la profesión médica asociada es válida. "
        f"Considera las siguientes condiciones: "
        f"- Analiza el contenido del mensaje y verifica si está relacionado con la medicina. "
        f"- Revisa la biografía y la sección de enlaces para comprobar si se mencionan instituciones, universidades, o términos relevantes relacionados con la medicina. "
        f"- Si no hay evidencia clara en el perfil, utiliza 'Ninguno' como profesión y asigna un índice de confianza bajo. "
        f"La respuesta debe contener el nombre de la profesión en la primera línea, con el formato 'Profesion:'. "
        f"En la segunda línea, incluye un índice numérico entre 0 y 1 que indique qué tan cercana está la profesión a una profesión médica, en el formato 'profession_quality:'.\n\n"
        f"Profile:\n{profile_str}"
    )

    try:
        model = genai.GenerativeModel(model_version)
        start_time = time.time()
        response = model.generate_content(prompt)
        if response and response.text:
            updated_profile = process_response_to_schema(
                response.text, profile, start_time, module_name, model_version
            )
            if updated_profile:
                save_profile(file_path, updated_profile, module_name)
    except Exception as e:
        print(f"Error al procesar el feature: {e}")

process_feature("c_x_2_norm_proc.json")
