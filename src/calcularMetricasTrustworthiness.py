import os
import sys
import glob
import importlib

# Asegurarse de que la carpeta "metrics" esté en el PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
metrics_dir = os.path.join(current_dir, "metrics")
if metrics_dir not in sys.path:
    sys.path.append(metrics_dir)

# Importar dinámicamente los módulos de métricas
module_names = [
    "metric_access_to_source_data",
    "metric_certification",
    "metric_confidence",
    "metric_trustworthiness",
]

def process_files_with_metrics(input_directory, metrics_dir, module_names):
    """
    Procesa todos los archivos que terminen con `_norm_proc.json` usando los módulos de métricas.

    :param input_directory: Directorio donde están ubicados los archivos JSON.
    :param metrics_dir: Directorio donde están ubicados los módulos de métricas.
    :param module_names: Lista de nombres de módulos de métricas a procesar.
    """
    # Buscar todos los archivos que coincidan con el patrón *_norm_proc.json
    #input_files = glob.glob(os.path.join(input_directory, "*_norm_proc.json"))
    input_files = glob.glob(os.path.join(input_directory, "*.json"))

    if not input_files:
        print("No se encontraron archivos que coincidan con '*_norm_proc.json'.")
        return

    # Iterar sobre cada archivo
    for json_file in input_files:
        print(f"\nProcesando archivo: {json_file}")

        # Iterar sobre cada módulo y aplicar al archivo
        for module_name in module_names:
            try:
                # Asegurarse de que el módulo está en el PATH
                if metrics_dir not in sys.path:
                    sys.path.append(metrics_dir)

                # Importar dinámicamente el módulo
                module = importlib.import_module(module_name)
                importlib.reload(module)  # Recargar para evitar estado previo

                # Verificar y ejecutar la función `process_metric`
                if hasattr(module, "process_metric"):
                    print(f"Ejecutando {module_name}.process_metric() para {json_file}...")
                    module.process_metric(json_file)
                else:
                    print(f"Advertencia: El módulo {module_name} no contiene la función 'process_metric'.")
            except Exception as e:
                print(f"Error al procesar el módulo {module_name} para el archivo {json_file}: {e}")

# Directorio de entrada
input_directory = "../clips/creibles/X/Caso2/PROV"  # Cambiar a la ruta de tu directorio de archivos

# Procesar los archivos
process_files_with_metrics(input_directory, metrics_dir, module_names)