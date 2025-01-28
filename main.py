import json
import os
from vision_api_project.process_document import process_document

if __name__ == "__main__":
    # Define input and output directories
    input_dirs = ["data/CNH_Aberta", "data/RG_Aberto"]  # List of folders to process
    results_dir = "results"  # Path to save the JSON output files

    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    failed_files = []  # List to store files that failed processing

    # Process each directory
    for input_dir in input_dirs:
        print(f"🔍 Processing directory: {input_dir}")

        # Ensure results subdirectory exists for the current input directory
        sub_results_dir = os.path.join(results_dir, os.path.basename(input_dir))
        os.makedirs(sub_results_dir, exist_ok=True)

        # Process all files in the current input directory
        for file_name in os.listdir(input_dir):
            if file_name.endswith("_in.jpg"):
                base_name = file_name.replace("_in.jpg", "")
                image_path = os.path.join(input_dir, file_name)
                output_file = os.path.join(sub_results_dir, f"{base_name}.json")

                try:
                    print(f"🔎 Processing {file_name}...")

                    # Process the document
                    result = process_document(image_path, "CNH" if "CNH" in input_dir else "RG")

                    # Check if the result is valid
                    if not result or "Erro" in result:
                        print(f"⚠️ Processing failed for {file_name}. Skipping.")
                        failed_files.append(file_name)
                        continue

                    # Display the extracted result
                    print(f"✅ Processed {file_name}:")
                    print(json.dumps(result, indent=4, ensure_ascii=False))

                    # Save the result to a JSON file
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=4)
                        f.flush()  # Ensure data is written before closing
                        os.fsync(f.fileno())

                    print(f"📂 Saved result for {file_name} at '{output_file}'.")

                except Exception as e:
                    print(f"❌ Error processing {file_name}: {e}")
                    failed_files.append(file_name)

    # Show summary of failed files
    if failed_files:
        print("\n⚠️ The following files failed to process:")
        for file in failed_files:
            print(f"   ❌ {file}")
