# Vision API Project

This project uses Google Vision API to extract and organize information from Brazilian documents such as CPF, RG, and CNH.

## Project Structure

```
vision_api_project/
├── data/                     # Directory for document images
├── results/                  # Directory for processed JSON results
├── src/                      # Main source code
│   ├── vision_api_project/   # Project module
│   │   ├── __init__.py       # Module initializer
│   │   ├── google_vision.py  # Google Vision integration code
│   │   ├── process_document.py  # Logic for processing documents
│   └── main.py               # Main script for execution
├── pyproject.toml            # Poetry configuration
├── README.md                 # Project documentation
└── .gitignore                # Ignored files in Git
```

---

## Requirements

- Python 3.8 or higher.
- Google Vision API key.

---

## Setup

1. **Install Poetry**:
   ```bash
   pip install poetry
   ```

2. **Configure the Google Vision API key**:
   Set the environment variable with your key file:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/key.json"
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

---

## How to Run

1. Place document images in the `data/` directory.
2. Update the image path and document type in `main.py`:
   ```python
   image_path = "data/BID Sample Dataset/CNH_Aberta/00000028_in.jpg"  # Replace with your image path
   document_type = "CNH"  # Replace with "CPF", "RG", or "CNH"
   ```
3. Execute the script:
   ```bash
   poetry run python src/main.py
   ```

---

## Input and Output

### Input
- Document images in supported formats: `.jpg`, `.png`, `.jpeg`, etc.

### Output
- A JSON file saved in the `results/` directory with extracted and organized information.

Example output:

```json
{
    "Document Type": "CPF",
    "Visible Information": [
        "MINISTÉRIO DA FAZENDA",
        "CPF",
        "123.456.789-00",
        "Name",
        "JOÃO DA SILVA",
        "Birth Date",
        "01/01/2000"
    ],
    "Organized Information": {
        "Name": "JOÃO DA SILVA",
        "CPF": "123.456.789-00",
        "Birth Date": "01/01/2000"
    }
}
```

---

## Supported Documents

1. **CPF**:
   - Name
   - CPF
   - Birth Date

2. **RG**:
   - Name
   - RG
   - CPF (if available)
   - Birth Date
   - Issue Date
   - Parents
   - Place of Birth

3. **CNH**:
   - Name
   - Identity Document
   - CPF
   - Registration Number
   - Birth Date
   - Issue Date
   - Validity
   - Category
   - First License Date
   - Parents
   - Place

---



