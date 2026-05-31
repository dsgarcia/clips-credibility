import json
import os
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
    base, ext = file_path.rsplit('.', 1)
    updated_file_path = f"{base}.{ext}"
    with open(updated_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print(f"Archivo actualizado guardado en: {updated_file_path}")
    return updated_file_path

def calculate_credibility_metric(data):
    """Calcula la métrica Credibility y la agrega al JSON en quality_metrics."""
    try:
        start_time = time.perf_counter()  # Inicia el cronómetro de alta precisión

        # Verificar existencia de las métricas
        trustworthiness_path_stability = next(
            (metric["metric_value"] for metric in data.get("quality_metrics", [])
             if metric["metric_name"] == "trustworthiness_path_stability"),
            None  # Valor predeterminado
        )
        trustworthiness = next(
            (metric["metric_value"] for metric in data.get("quality_metrics", [])
             if metric["metric_name"] == "trustworthiness"),
            0  # Valor predeterminado
        )

        # Ajustar pesos según la disponibilidad de trustworthiness_path_stability
        if trustworthiness_path_stability is None:
            weight_tps = 0  # No se considera la métrica de estabilidad
            weight_trustworthiness = 1  # Se asigna todo el peso a trustworthiness
            trustworthiness_path_stability = 0  # Asignar un valor predeterminado de 0
            remarks = "trustworthiness_path_stability no encontrada; se asignó peso 0."
        else:
            weight_tps = 0.6  # Peso para Trustworthiness_Path_Stability
            weight_trustworthiness = 0.4  # Peso para Trustworthiness
            remarks = None

        # Calcular Credibility
        credibility = (
            weight_tps * trustworthiness_path_stability +
            weight_trustworthiness * trustworthiness
        )

        # Calcular tiempo de procesamiento
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        # Crear la métrica Credibility
        credibility_metric = {
            "clip_id": data["clip"]["identification"]["clip_id"],
            "metric_name": "credibility",
            "metric_value": credibility,
            "metric_factor": f"{weight_tps} * trustworthiness_path_stability + {weight_trustworthiness} * trustworthiness",
            "calculation_timestamp": datetime.now().isoformat(),
            "processing_time_ms": processing_time_ms,
            "calculation_method": (
                f"credibility = {weight_tps} * Trustworthiness_Path_Stability + {weight_trustworthiness} * Trustworthiness"
            ),
            "quality_metadata": {
                "trustworthiness_path_stability": trustworthiness_path_stability,
                "trustworthiness": trustworthiness
            },
            "remarks": remarks  # Observaciones adicionales
        }

        # Agregar la métrica a quality_metrics
        if "quality_metrics" not in data:
            data["quality_metrics"] = []
        data["quality_metrics"].append(credibility_metric)

        return data

    except Exception as e:
        raise ValueError(f"Error al calcular credibility: {e}")

def process_quality_metrics(input_file):
    """Carga, procesa y guarda las métricas de calidad en el archivo JSON."""
    try:
        # Cargar el JSON
        data = load_json_file(input_file)
        
        # Calcular la métrica Credibility
        updated_data = calculate_credibility_metric(data)
        
        # Guardar el archivo actualizado
        save_json_file(input_file, updated_data)
    except Exception as e:
        raise RuntimeError(f"Error durante el procesamiento de métricas: {e}")

def process_files_in_directory(directory_path):
    """
    Procesa todos los archivos con formato *norm_proc.json en un directorio dado,
    calculando la métrica Credibility.
    """
    try:
        for file_name in os.listdir(directory_path):
            if file_name.endswith("*norm_proc.json"):
                file_path = os.path.join(directory_path, file_name)
                print(f"Procesando archivo: {file_name}")
                process_quality_metrics(file_path)
    except Exception as e:
        raise RuntimeError(f"Error al procesar los archivos en el directorio {directory_path}: {e}")

# Ejemplo de uso
if __name__ == "__main__":
     #Procesar todos los archivos en el directorio raíz
    process_files_in_directory("./")

#process_quality_metrics("c_fb_1_norm_proc.json")