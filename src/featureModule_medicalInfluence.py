import json
import google.generativeai as genai
from datetime import datetime
import time
import os

# Configurar la API Key
genai.configure(api_key="AIzaSyDuiFvZAfbaODG7EdSGQy1gssyZZeuG7tI")

def load_profile(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no se encontró.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: El archivo '{file_path}' no contiene un JSON válido.")
        exit(1)

def save_profile(file_path, data, module_name):
    try:
        # Guardar el archivo
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"El archivo se ha guardado como: {file_path}")
    except Exception as e:
        print(f"Error al guardar el archivo JSON: {e}")
        exit(1)

def process_response_to_schema(response_text, profile, processing_start_time, module_name, model_version, feature_name):
    try:
        # Dividir la respuesta en líneas
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
                "description": f"Generated {feature_name} based on user recommendations."
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

    except (ValueError, IndexError, TypeError) as ve:
        print(f"Error al procesar la respuesta: {ve}")
        return None

def process_feature(file_path):
    """Función principal para procesar la métrica de 'influence'."""
    try:
        profile = load_profile(file_path)
        recommendations = profile["clip"].get("comments", [])
        recommendations_text = "\n".join([rec["text"] for rec in recommendations]) if recommendations else "No recommendations available."

        model_version = "gemini-1.5-flash"
        module_name = "MedicalInfluenceModule"
        feature_name = "influence"

        prompt = (
            f"Basado en las siguientes recomendaciones sobre un usuario, ¿cuál es su índice de influencia médica? "
            f"Por favor, responde estrictamente en el siguiente formato:\n\n"
            f"influence: <breve descripción del índice numérico>\n"
            f"influence_quality: <número entre 0 y 1>\n\n"
            f"Nota: La respuesta debe incluir exactamente dos líneas en este formato, sin contenido adicional.\n\n"
            f"Recommendations:\n{recommendations_text}"
        )

        model = genai.GenerativeModel(model_version)
        start_time = time.time()
        response = model.generate_content(prompt)
        if response and response.text:
            profile = process_response_to_schema(
                response.text, profile, start_time, module_name, model_version, feature_name
            )
            if profile:
                save_profile(file_path, profile, module_name)
    except Exception as e:
        print(f"Error durante el procesamiento del módulo 'influence': {e}")