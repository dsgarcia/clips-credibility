import os
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

def extract_trustworthiness(data):
    """Extrae la métrica trustworthiness de un archivo JSON."""
    try:
        trustworthiness_metric = next(
            (metric for metric in data.get("quality_metrics", [])
             if metric["metric_name"] == "trustworthiness"),
            None
        )
        if not trustworthiness_metric:
            raise ValueError("La métrica 'trustworthiness' no se encuentra en el archivo.")
        return trustworthiness_metric["metric_value"]
    except Exception as e:
        raise ValueError(f"Error al extraer trustworthiness: {e}")

def calculate_trustworthiness_path_stability(trustworthiness_values):
    """
    Calcula la métrica trustworthiness_path_stability.
    """
    try:
        if len(trustworthiness_values) < 2:
            raise ValueError("Se requieren al menos dos valores de trustworthiness para calcular la estabilidad.")

        # Calcular las diferencias absolutas entre nodos consecutivos
        differences = [abs(trustworthiness_values[i + 1] - trustworthiness_values[i])
                       for i in range(len(trustworthiness_values) - 1)]

        # Calcular el promedio de diferencias
        avg_difference = sum(differences) / len(differences)

        # Calcular la estabilidad
        stability = 1 - avg_difference
        return round(stability, 4)  # Redondear a 4 decimales

    except Exception as e:
        raise ValueError(f"Error al calcular trustworthiness_path_stability: {e}")

def consolidate_trustworthiness_path_stability(directory_path, output_file):
    """
    Procesa un directorio que contiene archivos JSON, extrae los valores de trustworthiness
    y calcula trustworthiness_path_stability, agregando una nueva entrada en quality_metrics
    del archivo de salida.
    """
    # Obtener lista de archivos JSON en el directorio
    input_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith(".json")]
    
    if not input_files or len(input_files) < 2:
        raise ValueError("El directorio debe contener al menos dos archivos JSON.")

    # Medir el tiempo de procesamiento
    start_time = time.perf_counter()

    # Extraer trustworthiness de todos los archivos
    trustworthiness_values = []
    for file_path in input_files:
        file_data = load_json_file(file_path)
        trustworthiness = extract_trustworthiness(file_data)
        trustworthiness_values.append(trustworthiness)

    # Calcular trustworthiness_path_stability
    trustworthiness_path_stability = calculate_trustworthiness_path_stability(trustworthiness_values)

    # Calcular tiempo de procesamiento
    processing_time_ms = int((time.perf_counter() - start_time) * 1000)

    # Crear la métrica trustworthiness_path_stability
    path_stability_metric = {
        "metric_name": "trustworthiness_path_stability",
        "metric_value": trustworthiness_path_stability,
        "calculation_timestamp": datetime.now().isoformat(),
        "processing_time_ms": processing_time_ms,
        "calculation_method": "1 - avg(|T(i+1) - T(i)|)",
        "trustworthiness_values": trustworthiness_values,
        "remarks": None  # Observaciones adicionales
    }

    # Cargar o inicializar el archivo de salida
    try:
        output_data = load_json_file(output_file)
    except FileNotFoundError:
        output_data = {}

    # Asegurarse de que "quality_metrics" existe en el archivo de salida
    if "quality_metrics" not in output_data:
        output_data["quality_metrics"] = []

    # Agregar la nueva métrica al campo "quality_metrics"
    output_data["quality_metrics"].append(path_stability_metric)

    # Guardar el archivo de salida actualizado
    save_json_file(output_file, output_data)

directory_path = "../clips/creibles/X/Caso2/PROV"  # Reemplaza con el directorio que contiene los JSON
output_file = "./c_x_2_norm_proc.json"  # Reemplaza con el nombre del archivo de salida
consolidate_trustworthiness_path_stability(directory_path, output_file)