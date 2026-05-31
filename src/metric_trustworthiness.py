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

def calculate_trustworthiness_metric(data):
    """Calcula la métrica trustworthiness y la agrega al JSON en quality_metrics."""
    try:
        start_time = time.perf_counter()  # Inicia el cronómetro de alta precisión

        # Pesos para cada métrica
        beta_1 = 0.4  # Peso para Access to Source Data
        beta_2 = 0.4  # Peso para Certification
        beta_3 = 0.2  # Peso para Confidence

        # Obtener los valores de las métricas
        access_to_source_data = next(
            (metric["metric_value"] for metric in data.get("quality_metrics", [])
             if metric["metric_name"] == "access_to_source_data"),
            0
        )
        certification = next(
            (metric["metric_value"] for metric in data.get("quality_metrics", [])
             if metric["metric_name"] == "certification"),
            0
        )
        confidence = next(
            (metric["metric_value"] for metric in data.get("quality_metrics", [])
             if metric["metric_name"] == "confidence"),
            0
        )

        # Calcular trustworthiness
        trustworthiness = (
            beta_1 * access_to_source_data +
            beta_2 * certification +
            beta_3 * confidence
        )

        # Calcular tiempo de procesamiento
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        # Crear la métrica trustworthiness
        trustworthiness_metric = {
            "clip_id": data["clip"]["identification"]["clip_id"],
            "metric_name": "trustworthiness",
            "metric_value": trustworthiness,
            "metric_factor": "0.4 * access_to_source_data + 0.4 * certification + 0.2 * confidence",
            "calculation_timestamp": datetime.now().isoformat(),
            "processing_time_ms": processing_time_ms,
            "calculation_method": (
                "trustworthiness = 0.4 * Access to Source Data + 0.4 * Certification + 0.2 * Confidence"
            ),
            "quality_metadata": {
                "access_to_source_data": access_to_source_data,
                "certification": certification,
                "confidence": confidence
            },
            "remarks": None  # Observaciones adicionales
        }

        # Agregar la métrica a quality_metrics
        if "quality_metrics" not in data:
            data["quality_metrics"] = []
        data["quality_metrics"].append(trustworthiness_metric)

        return data

    except Exception as e:
        raise ValueError(f"Error al calcular trustworthiness: {e}")

# Función de procesamiento
def process_metric(file_path):
    """Función principal para procesar la métrica trustworthiness."""
    try:
        # Cargar el JSON
        data = load_json_file(file_path)
        
        # Calcular la métrica trustworthiness
        updated_data = calculate_trustworthiness_metric(data)
        
        # Guardar el archivo actualizado
        save_json_file(file_path, updated_data)
    except Exception as e:
        print(f"Error al procesar la métrica Trustworthiness: {e}")

process_metric("c_x_2_norm_proc.json")