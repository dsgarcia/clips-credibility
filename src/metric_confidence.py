import json
import math
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

def calculate_confidence_metric(data, alpha=0.7, max_audience_size=100000):
    """Calcula la métrica Confidence y la agrega al JSON en quality_metrics."""
    try:
        start_time = time.perf_counter()  # Usar perf_counter para mayor precisión

        # Obtener los valores de Influence y Audience Size, asumir 0 si no existen
        influence_feature = next(
            (feature for feature in data.get("features", {}).get("generated_features", [])
             if feature["feature_name"] == "influence"),
            {}
        )
        influence = influence_feature.get("confidence_level", 0)
        audience_size = data.get("user", {}).get("personal_information", {}).get("audience_size", 0)

        # Normalizar el tamaño de la audiencia
        normalized_audience_size = math.log(audience_size + 1) / math.log(max_audience_size + 1)

        # Calcular Confidence como media ponderada
        confidence = alpha * influence + (1 - alpha) * normalized_audience_size

        # Calcular tiempo de procesamiento
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        # Crear la métrica Confidence
        confidence_metric = {
            "clip_id": data.get("clip", {}).get("identification", {}).get("clip_id", "unknown"),
            "metric_name": "confidence",
            "metric_value": min(max(confidence, 0), 1),  # Limitar el valor entre 0 y 1
            "metric_factor": f"alpha * influence + (1 - alpha) * log(audience_size + 1) / log(max_audience_size + 1)",
            "calculation_timestamp": datetime.now().isoformat(),
            "calculation_method": f"Confidence = {alpha} * influence + {1 - alpha} * Normalized Audience Size",
            "processing_time_ms": processing_time_ms,
            "quality_metadata": {
                "influence": influence,
                "audience_size": audience_size,
                "normalized_audience_size": normalized_audience_size,
                "alpha": alpha,
                "max_audience_size": max_audience_size
            },
            "remarks": None  # Observaciones adicionales
        }

        # Agregar la métrica a quality_metrics
        if "quality_metrics" not in data:
            data["quality_metrics"] = []
        data["quality_metrics"].append(confidence_metric)

        return data

    except Exception as e:
        print(f"Advertencia: Error al calcular Confidence, estableciendo como 0. Detalles: {e}")
        return data  # Retornar datos originales sin cambios si falla

def process_metric(file_path):
    """Función principal que procesa la métrica Confidence."""
    try:
        # Cargar el archivo JSON
        data = load_json_file(file_path)
        
        # Calcular la métrica Confidence
        updated_data = calculate_confidence_metric(data)
        
        # Guardar el archivo actualizado
        save_json_file(file_path, updated_data)
    except Exception as e:
        print(f"Error al procesar la métrica Confidence: {e}")