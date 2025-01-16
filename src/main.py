import json
from vision_api_project.process_document import process_document

if __name__ == "__main__":
    image_path = "data/BID Sample Dataset/CNH_Aberta/00000021_in.jpg"  # Replace with your image path
    document_type = "CNH"  # Replace with "CPF", "RG", or "CNH"

    # Process the document and get the results
    resultado = process_document(image_path, document_type)
    
    # Print the result as JSON
    print(json.dumps(resultado, indent=4, ensure_ascii=False))

    # Save the result to a file
    with open("results/output.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)
