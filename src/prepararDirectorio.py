import os
import shutil

def copy_and_rename_norm_files(source_directory, destination_directory, suffix="_proc"):
    """
    Copia todos los archivos que terminen exactamente en `norm.json` desde los subdirectorios 
    de `source_directory` a `destination_directory` y les agrega un sufijo al nombre.

    :param source_directory: Directorio fuente donde buscar archivos en profundidad.
    :param destination_directory: Directorio destino donde copiar los archivos.
    :param suffix: Sufijo a agregar al nombre de los archivos copiados.
    """
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
        print(f"Directorio creado: {destination_directory}")

    # Recorrer en profundidad el directorio fuente
    for root, _, files in os.walk(source_directory):
        for file in files:
            # Verificar si el archivo termina exactamente en 'norm.json'
            if file.endswith("norm.json"):
                source_file_path = os.path.join(root, file)
                file_name, file_ext = os.path.splitext(file)
                destination_file_name = f"{file_name}{suffix}{file_ext}"
                destination_file_path = os.path.join(destination_directory, destination_file_name)
                
                # Copiar y renombrar
                try:
                    shutil.copy(source_file_path, destination_file_path)
                    print(f"Archivo copiado: {source_file_path} -> {destination_file_path}")
                except Exception as e:
                    print(f"Error al copiar el archivo {source_file_path}: {e}")

# Parámetros de entrada
source_directory = "../clips"  # Directorio fuente
destination_directory = "./"   # Directorio destino

# Ejecutar la rutina
copy_and_rename_norm_files(source_directory, destination_directory)