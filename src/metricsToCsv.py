import os
import csv
import json

def extract_metrics_to_csv(input_directory, output_csv):
    """
    Extract all attributes from 'quality_metrics' and 'features.generated_features'
    sections in JSON files ending with '*proc.json' and save them flattened to a CSV file.
    Includes the JSON filename and platform as additional columns.

    Args:
        input_directory (str): Directory containing the JSON files.
        output_csv (str): Path to the output CSV file.
    """
    # List to store flattened data
    flattened_data = []

    # Iterate over files in the directory
    for file_name in os.listdir(input_directory):
        if file_name.endswith("proc.json"):
            file_path = os.path.join(input_directory, file_name)
            try:
                # Read the JSON file
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                clip_id = data["clip"]["identification"]["clip_id"]
                platform = data["clip"]["identification"].get("platform", "")

                # Extract 'quality_metrics'
                for metric in data.get("quality_metrics", []):
                    flattened_data.append({
                        "file_name": file_name,
                        "clip_id": clip_id,
                        "platform": platform,
                        "type": "quality_metric",
                        **metric
                    })
                
                # Extract 'features.generated_features'
                for feature in data.get("features", {}).get("generated_features", []):
                    feature_data = {
                        "file_name": file_name,
                        "clip_id": clip_id,
                        "platform": platform,
                        "type": "generated_feature",
                        "feature_name": feature.get("feature_name", ""),
                        "feature_value": feature.get("feature_value", ""),
                        "confidence_level": feature.get("confidence_level", ""),
                        "module_name": feature.get("module_name", ""),
                        "description": feature.get("feature_details", {}).get("description", ""),
                        "calculated_at": feature.get("calculation_details", {}).get("calculated_at", ""),
                        "calculation_method": feature.get("calculation_details", {}).get("calculation_method", ""),
                        "processing_time_ms": feature.get("calculation_details", {}).get("processing_time_ms", "")
                    }
                    flattened_data.append(feature_data)

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    # Write the flattened data to a CSV file
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        # Dynamically determine the fieldnames from the keys of the first item
        if flattened_data:
            fieldnames = set(key for item in flattened_data for key in item.keys())
        else:
            fieldnames = ["file_name", "clip_id", "platform", "type"]  # Default headers if no data found

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened_data)

    print(f"Metrics successfully saved to {output_csv}")

# Define the input directory and output file
input_directory = "./"
output_csv = "./metrics.csv"

# Run the extraction
extract_metrics_to_csv(input_directory, output_csv)