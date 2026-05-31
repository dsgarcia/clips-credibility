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
        print(f"El archivo se ha guardado como: {file_path}")
    except Exception as e:
        print(f"Error al guardar el archivo JSON: {e}")
        exit(1)

# Procesar la respuesta del modelo y estructurarla en `features.generated_features`
def process_response_to_schema(response_text, profile, processing_start_time, module_name, model_version, feature_name):
    try:
        # Dividir la respuesta en líneas
        lines = [line.strip() for line in response_text.strip().split("\n") if line.strip()]

        # Validar y extraer el contenido de la respuesta
        if len(lines) < 2:
            raise ValueError("La respuesta no contiene las líneas esperadas.")
        
        value_line = lines[0]
        if ":" not in value_line:
            raise ValueError("La primera línea no contiene un separador ':' esperado.")
        
        key, feature_value = value_line.split(":", 1)
        key = key.strip().lower()
        feature_value = feature_value.strip()

        if key != feature_name.lower():
            raise ValueError(f"La clave '{key}' no coincide con '{feature_name.lower()}:'.")

        quality_line = lines[1]
        if ":" not in quality_line:
            raise ValueError("La segunda línea no contiene un separador ':' esperado.")
        
        quality_key, confidence_level = quality_line.split(":", 1)
        quality_key = quality_key.strip().lower()
        confidence_level = confidence_level.strip()

        if quality_key != f"{feature_name.lower()}_quality":
            raise ValueError(f"La clave '{quality_key}' no coincide con '{feature_name.lower()}_quality:'.")

        confidence_level = float(confidence_level)

        # Calcular detalles de procesamiento
        processing_end_time = time.time()
        processing_time_ms = int((processing_end_time - processing_start_time) * 1000)

        # Generar la estructura para `generated_features`
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
    module_name_verifiability = "MedicalVerifiabilityModule"
    feature_name_verifiability = "medicalVerifiability"

    prompt_verifiability = (
        f"Basado en el siguiente perfil, ¿qué nivel de verificabilidad tiene el usuario que afirma ser médico? "
        f"Considera si hay referencias a universidades, hospitales u otras organizaciones reconocidas en el perfil. "
        f"La respuesta debe cumplir estrictamente este formato:\n"
        f"medicalVerifiability: <nivel> (<evidencia encontrada, e.g., nombres de instituciones o enlaces>)\n"
        f"medicalVerifiability_quality: <número> (un índice numérico entre 0 y 1).\n\n"
        f"Profile:\n{profile_str}"
    )

    try:
        model = genai.GenerativeModel(model_version)
        start_time = time.time()
        response_verifiability = model.generate_content(prompt_verifiability)
        if response_verifiability and response_verifiability.text:
            profile = process_response_to_schema(
                response_verifiability.text, profile, start_time, module_name_verifiability, model_version, feature_name_verifiability
            )
            if profile:
                save_profile(file_path, profile, module_name_verifiability)
    except Exception as e:
        print(f"Error al procesar el feature: {e}")
