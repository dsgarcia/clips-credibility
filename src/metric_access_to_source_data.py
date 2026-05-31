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

def calculate_access_to_source_data_metric(data):
    """Calcula la métrica Access to Source Data y la agrega al JSON en quality_metrics."""
    try:
        start_time = time.perf_counter()  # Inicia el cronómetro de alta precisión

        # Obtener el feature de verificabilidad
        verifiability_feature = next(
            (feature for feature in data.get("features", {}).get("generated_features", [])
             if feature["feature_name"] == "medicalVerifiability"),
            None
        )

        # Obtener el valor de calidad de verificabilidad o asumir 0
        verifiability_quality = verifiability_feature.get("confidence_level", 0) if verifiability_feature else 0

        # Calcular tiempo de procesamiento
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        # Crear la métrica Access to Source Data
        access_to_source_data_metric = {
            "clip_id": data.get("clip", {}).get("identification", {}).get("clip_id", "unknown"),
            "metric_name": "access_to_source_data",
            "metric_value": verifiability_quality,
            "metric_factor": "verifiability_quality",
            "calculation_timestamp": datetime.now().isoformat(),
            "calculation_method": "Direct mapping from MedicalVerifiabilityModule",
            "processing_time_ms": processing_time_ms,
            "quality_metadata": {
                "verifiability_quality": verifiability_quality
            },
            "remarks": None if verifiability_feature else "Valor asumido como 0 debido a la ausencia del feature MedicalVerifiability."
        }

        # Agregar la métrica a quality_metrics
        if "quality_metrics" not in data:
            data["quality_metrics"] = []
        data["quality_metrics"].append(access_to_source_data_metric)

        return data

    except Exception as e:
        print(f"Error al calcular Access to Source Data: {e}")
        return data  # Retornar datos originales sin cambios si falla

def process_metric(file_path):
    """Función principal que procesa la métrica Access to Source Data."""
    try:
        # Cargar el archivo JSON
        data = load_json_file(file_path)
        
        # Calcular la métrica Access to Source Data
        updated_data = calculate_access_to_source_data_metric(data)
        
        # Guardar el archivo actualizado
        save_json_file(file_path, updated_data)
    except Exception as e:
        print(f"Error al procesar la métrica Access to Source Data: {e}")