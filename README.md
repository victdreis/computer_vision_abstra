# VISION_API_PROJECT

## 📌 Project Overview
VISION_API_PROJECT is a document processing system that extracts structured information from scanned documents using Google Vision API and OpenAI's GPT models. The project aims to automate the extraction of key details from various types of official documents (e.g., ID cards, birth certificates, pay stubs, etc.).

## 🚀 Features
- **OCR with Google Vision API**: Extracts visible text from images.
- **AI-based Information Extraction**: Uses OpenAI GPT models to organize extracted text into structured JSON.
- **Error Handling & Voting Mechanism**: Implements retry logic with a voting-based approach to improve reliability.
- **Accuracy Evaluation**: Computes field-wise accuracy using ground truth data.
- **Logging & File Management**: Logs processing steps and stores results efficiently.

## 📂 Project Structure
```
VISION_API_PROJECT/
│── data/                     # Folder containing input images (must be created manually)
│── results/                  # Folder where processed results are saved
│── doc_vision/                      # doc_vision code directory
│   │── google_vision.py      # Handles text extraction using Google Vision
│   │── process_document.py   # Core processing logic (text extraction & GPT processing)
│   │── document_organizer.py # Helps structure extracted data
│   │── display_information.py# (Optional) Displays processed results
│   │── position_correction.py# Adjusts text positioning if necessary
│── metric_calculation.py      # Evaluates processing accuracy
│── main.py                   # Entry point for batch document processing
│── requirements.txt           # Required dependencies
│── README.md                  # Project documentation
│── config.json                # Configuration file containing API keys
│── .gitignore                 # Specifies files to be ignored by Git
│── vision-key.json            # Google Vision API credentials file
```

## ⚙️ Installation & Setup
### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-repo/vision_api_project.git
cd vision_api_project
```
### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
### 3️⃣ Configure API Keys
Update `config.json` with your OpenAI API key and ensure `vision-key.json` contains your Google Vision credentials:
```json
{
    "openai_api_key": "your-openai-key"
}
```

## 📌 Usage
### Running the document processor
To process all documents in the `data/` directory, run:
```bash
python main.py
```

### Evaluating Processing Accuracy
To generate accuracy metrics for the processed documents:
```bash
python metric_calculation.py
```
This script calculates field-wise accuracy by comparing extracted information with ground truth data. The results are stored in `results/summary.json`.

### Required Dataset
Before running the project, create a `data/` directory and populate it with documents from the [Brazilian Identity Document Dataset](https://github.com/ricardobnjunior/Brazilian-Identity-Document-Dataset/tree/master/VIA%20ANNOTATIONS):
```bash
mkdir data
# Add the dataset files inside the data/ directory
```
This dataset provides real examples for testing the document extraction process.

### Generating a Summary Report
After running the processing pipeline, generate a summary report with:
```bash
python metric_calculation.py
```
This script computes:
- Field-by-field accuracy
- Overall document accuracy
- Processing statistics

The generated report is saved as `results/summary.json` and can be used for reproducibility and model evaluation.

### Environment Setup
To ensure smooth execution, create a `.env` file for managing environment variables:
```
OPENAI_API_KEY=your-openai-key
GOOGLE_APPLICATION_CREDENTIALS=vision-key.json
```
