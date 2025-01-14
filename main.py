from google.cloud import vision
import io
import os
import re
import datetime
import json


def google_vision_extract(image_path):
    """
    Uses Google Vision API to extract text from an image.
    """
    print(f"Initializing Google Vision API client for {image_path}...")
    client = vision.ImageAnnotatorClient()

    print(f"Reading the image: {image_path}")
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    print("Performing text detection...")
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        print(f"No text found in the image: {image_path}")
        return "No text found."

    # The full text is in the first position
    extracted_text = texts[0].description
    return extracted_text


def extract_information(text):
    """
    Extracts relevant information from the extracted text.
    """
    # Pattern for Name
    name_pattern = r"NOME\s+([A-ZÀ-Ü\s]+)(?=\nFILIAÇÃO)"
    name_match = re.search(name_pattern, text)
    name = name_match.group(1).strip() if name_match else None

    # Pattern for Filiation (two consecutive lines of names)
    filiation_pattern = r"FILIAÇÃO\s+([A-ZÀ-Ü\s]+)\n([A-ZÀ-Ü\s]+)(?=\nDATA NASC)"
    filiation_match = re.search(filiation_pattern, text)
    if filiation_match:
        parent1 = filiation_match.group(1).strip()
        parent2 = filiation_match.group(2).strip()
        filiation = f"{parent1}\n{parent2}"
    else:
        filiation = None

    # Pattern for Date of Birth
    birth_date_pattern = r"DATA NASC\s+(\d{2}[/-]\d{2}[/-]\d{4})"
    birth_date_match = re.search(birth_date_pattern, text)
    birth_date = birth_date_match.group(1) if birth_date_match else None

    # Pattern for Naturalness
    naturality_pattern = r"NATURALIDADE\s+([A-ZÀ-Ü\s]+)"
    naturality_match = re.search(naturality_pattern, text)
    naturality = naturality_match.group(1).strip() if naturality_match else None

    # Pattern for CPF
    cpf_pattern = r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"
    cpf_match = re.search(cpf_pattern, text)
    cpf = cpf_match.group(0) if cpf_match else None

    # Pattern for RG
    rg_pattern = r"\b\d{2}\.\d{3}\.\d{3}-\d{1}\b"
    rg_match = re.search(rg_pattern, text)
    rg = rg_match.group(0) if rg_match else None

    # Pattern for Expedition Date
    expedition_date_pattern = r"DATA DE EXPEDIÇÃO\s+(\d{2}[/-]\d{2}[/-]\d{4})"
    expedition_date_match = re.search(expedition_date_pattern, text)
    expedition_date = expedition_date_match.group(1) if expedition_date_match else None

    # Organize the results
    result = {
        "Name": name,
        "Filiation": filiation,
        "Date of Birth": birth_date,
        "Naturalness": naturality,
        "CPF": cpf,
        "General Registration (RG)": rg,
        "Expedition Date": expedition_date,
    }

    return result


def pretty_print_info(info):
    """
    Prints extracted information in a formatted and readable manner.
    """
    print("\n--- Extracted Information ---")
    for key, value in info.items():
        print(f"{key}: {value if value else 'Not found'}")
    print("-" * 30)


if __name__ == "__main__":
    # Check if the JSON key file is configured
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("Error: The GOOGLE_APPLICATION_CREDENTIALS environment variable is not configured.")
        print("Set it to the full path of your vision-key.json file.")
        exit(1)

    # Paths to identity images (front and back)
    front_image_path = "data/victoria_frente.png"  # Replace with the front image path
    back_image_path = "data/victoria_verso.png"    # Replace with the back image path

    # Check if files exist
    if not os.path.exists(front_image_path):
        print(f"Error: The image file {front_image_path} was not found.")
        exit(1)

    if not os.path.exists(back_image_path):
        print(f"Error: The image file {back_image_path} was not found.")
        exit(1)

    # Process the images
    print("Starting text extraction...")
    front_text = google_vision_extract(front_image_path)
    back_text = google_vision_extract(back_image_path)

    # Concatenate the extracted texts
    full_text = front_text + "\n" + back_text

    # Extract information from the full text
    print("Extracting information...")
    extracted_info = extract_information(full_text)

    # Print the extracted information
    pretty_print_info(extracted_info)

    # Generate JSON with date and time in the filename
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"results/result_{current_datetime}.json"

    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump(extracted_info, json_file, indent=4, ensure_ascii=False)

    print(f"\nJSON saved as: {output_filename}")
