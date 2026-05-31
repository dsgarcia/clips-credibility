import json
import google.generativeai as genai
from datetime import datetime
import time
import os

# Configurar la API Key
genai.configure(api_key="AIzaSyDuiFvZAfbaODG7EdSGQy1gssyZZeuG7tI")

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
        print(f"El archivo se ha guardado como: {file_path}")
    except Exception as e:
        print(f"Error al guardar el archivo JSON: {e}")
        exit(1)

# Procesar la respuesta del modelo y estructurarla en `features.generated_features`
def process_response_to_schema(response_text, profile, processing_start_time, module_name, model_version, feature_name):
    try:
        lines = response_text.strip().split("\n")

        if len(lines) < 2:
            raise ValueError("La respuesta no contiene las líneas esperadas.")
        
        value_line = lines[0].strip()
        if not value_line.lower().startswith(f"{feature_name}:"):
            raise ValueError(f"La primera línea no sigue el formato '{feature_name}:'.")
        feature_value = value_line.split(":", 1)[1].strip()
        
        quality_line = lines[1].strip()
        if not quality_line.lower().startswith(f"{feature_name}_quality:"):
            raise ValueError(f"La segunda línea no sigue el formato '{feature_name}_quality:'.")
        confidence_level = float(quality_line.split(":", 1)[1].strip())

        processing_end_time = time.time()
        processing_time_ms = int((processing_end_time - processing_start_time) * 1000)

        generated_feature = {
            "module_name": module_name,
            "feature_name": feature_name,
            "feature_value": feature_value,
            "confidence_level": confidence_level,
            "feature_details": {
                "description": f"Generated {feature_name} based on input profile."
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

    except Exception as e:
        print(f"Error al procesar la respuesta: {e}")
        return None

# Función principal del módulo
def process_feature(file_path):
    profile = load_profile(file_path)
    profile_str = json.dumps(profile, ensure_ascii=False, indent=2)

    model_version = "gemini-1.5-flash"
    module_name_education = "MedicalEducationModule"
    feature_name_education = "education"

    prompt_education = (
    f"Basado en el siguiente perfil, ¿qué nivel de educación relacionado con la medicina tiene el usuario? "
    f"Solo debe incluir títulos relacionados con la medicina. "
    f"La respuesta debe contener el nivel de educación en la primera línea, con el formato Education: "
    f"y un índice numérico entre 0 y 1 que indique qué tan relevante es para la medicina, en la segunda línea, con el formato education_quality:\n\n"
    f"Profile:\n{profile_str}"
)

    try:
        model = genai.GenerativeModel(model_version)
        start_time = time.time()
        response_education = model.generate_content(prompt_education)
        if response_education and response_education.text:
            profile = process_response_to_schema(
                response_education.text, profile, start_time, module_name_education, model_version, feature_name_education
            )
            if profile:
                save_profile(file_path, profile, module_name_education)
    except Exception as e:
        print(f"Error al procesar el feature: {e}")

