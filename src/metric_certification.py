import json
from datetime import datetime
import time

def load_json_file(file_path):
    """Carga un archivo JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: El archivo '{file_path}' no se encontró.")
    except json.JSONDecodeError:
        raise ValueError(f"Error: El archivo '{file_path}' no contiene un JSON válido.")

def save_json_file(file_path, data):
    """Guarda un archivo JSON actualizado."""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print(f"Archivo actualizado guardado en: {file_path}")
    return file_path

def calculate_certification_metric(data):
    """Calcula la métrica Certification y la agrega al JSON en quality_metrics."""
    try:
        start_time = time.perf_counter()  # Inicia el cronómetro de alta precisión

        # Obtener los valores de Education y Profession, asumir 0 si no existen
        education_feature = next(
            (feature for feature in data.get("features", {}).get("generated_features", [])
             if feature["feature_name"] == "education"),
            {}
        )
        profession_feature = next(
            (feature for feature in data.get("features", {}).get("generated_features", [])
             if feature["feature_name"] == "profession"),
            {}
        )

        education_quality = education_feature.get("confidence_level", 0)
        profession_quality = profession_feature.get("confidence_level", 0)

        # Parámetro de ajuste para ponderar los factores
        alpha = 0.6

        # Calcular Certification
        certification = alpha * education_quality + (1 - alpha) * profession_quality

        # Calcular tiempo de procesamiento
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        # Crear la métrica Certification
        certification_metric = {
            "clip_id": data["clip"]["identification"]["clip_id"],
            "metric_name": "certification",
            "metric_value": certification,
            "metric_factor": "alpha * Education Quality + (1 - alpha) * Profession Quality",
            "calculation_timestamp": datetime.now().isoformat(),
            "processing_time_ms": processing_time_ms,
            "calculation_method": "Certification = alpha * Education Quality + (1 - alpha) * Profession Quality",
            "quality_metadata": {
                "education_quality": education_quality,
                "profession_quality": profession_quality,
                "alpha": alpha
            },
            "remarks": None  # Observaciones adicionales
        }

        # Agregar la métrica a quality_metrics
        if "quality_metrics" not in data:
            data["quality_metrics"] = []
        data["quality_metrics"].append(certification_metric)

        return data

    except Exception as e:
        print(f"Advertencia: Error al calcular Certification, estableciendo como 0. Detalles: {e}")
        # Crear una métrica Certification con valor 0 en caso de error
        certification_metric = {
            "clip_id": data["clip"]["identification"]["clip_id"],
            "metric_name": "certification",
            "metric_value": 0,
            "metric_factor": "Certification",
            "calculation_timestamp": datetime.now().isoformat(),
            "processing_time_ms": 0,
            "calculation_method": "Certification = alpha * Education Quality + (1 - alpha) * Profession Quality",
            "quality_metadata": {
                "education_quality": 0,
                "profession_quality": 0,
                "alpha": alpha
            },
            "remarks": "Calculado como 0 debido a valores faltantes o errores en el cálculo."
        }

        # Agregar la métrica a quality_metrics
        if "quality_metrics" not in data:
            data["quality_metrics"] = []
        data["quality_metrics"].append(certification_metric)

        return data

def process_metric(file_path):
    """Función principal que procesa la métrica Certification."""
    try:
        # Cargar el archivo JSON
        data = load_json_file(file_path)
        
        # Calcular la métrica Certification
        updated_data = calculate_certification_metric(data)
        
        # Guardar el archivo actualizado
        save_json_file(file_path, updated_data)
    except Exception as e:
        print(f"Error al procesar la métrica Certification: {e}")

process_metric("c_x_2_norm_proc.json")