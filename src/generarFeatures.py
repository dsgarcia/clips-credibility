import importlib
import os
import glob
import sys

def run_feature_modules_for_files(modules_directory, input_directory, module_names):
    """
    Ejecuta los módulos de features para todos los archivos en el directorio de entrada
    cuyos nombres terminen con `_norm_proc.json`.

    :param modules_directory: Directorio donde están ubicados los módulos.
    :param input_directory: Directorio donde están ubicados los archivos JSON de entrada.
    :param module_names: Lista de nombres de los módulos en el orden deseado.
    """
    # Encontrar todos los archivos que terminan con `_norm_proc.json` en el directorio de entrada
    # input_files = glob.glob(os.path.join(input_directory, "*_norm_proc.json"))
    input_files = glob.glob(os.path.join(input_directory, "*json"))

    if not input_files:
        print("No se encontraron archivos que terminen con '_norm_proc.json'.")
        return

    for file_path in input_files:
        print(f"Procesando archivo: {file_path}")

        for module_name in module_names:
            try:
                # Asegurar que el módulo está en el PATH
                if modules_directory not in sys.path:
                    sys.path.append(modules_directory)

                # Importar dinámicamente el módulo
                module = importlib.import_module(module_name)
                importlib.reload(module)  # Recargar para evitar estado previo
                
                # Llamar a la función principal del módulo
                if hasattr(module, "process_feature"):
                    print(f"Ejecutando {module_name}.process_feature() para {file_path}...")
                    module.process_feature(file_path)
                else:
                    print(f"Advertencia: El módulo {module_name} no contiene la función 'process_feature'.")
            except Exception as e:
                print(f"Error al ejecutar el módulo {module_name} para el archivo {file_path}: {e}")

# Uso del script
modules_directory = "./"  # Directorio donde están los módulos
input_directory = "../clips/creibles/X/Caso2/PROV"  # Directorio donde están los archivos JSON de entrada
module_names = [
    "featureModule_medicalEducation",
    "featureModule_medicalVerifiability",
    "featureModule_medicalProfession",
    "featureModule_medicalInfluence"
]  # Orden de los módulos a ejecutar

run_feature_modules_for_files(modules_directory, input_directory, module_names)