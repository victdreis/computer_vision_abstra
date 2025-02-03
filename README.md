# VISION_API_PROJECT

## 📌 Project Overview
VISION_API_PROJECT is a document processing system that extracts structured information from scanned documents using Google Vision API and OpenAI's GPT models. The project aims to automate the extraction of key details from various types of official documents (e.g., ID cards, birth certificates, pay stubs, etc.).

## 🚀 Features
- **OCR with Google Vision API**: Extracts visible text from images.
- **AI-based Information Extraction**: Uses OpenAI GPT models to organize extracted text into structured JSON.
- **Error Handling & Voting Mechanism**: Implements retry logic with a voting-based approach to improve reliability.
- **Logging & File Management**: Logs processing steps and stores results efficiently.

## 📂 Project Structure
```
VISION_API_PROJECT/
│── data/                     # Folder containing input images
│── results/                  # Folder where processed results are saved
│── src/                      # Source code directory
│   │── google_vision.py      # Handles text extraction using Google Vision
│   │── process_document.py   # Core processing logic (text extraction & GPT processing)
│   │── document_organizer.py # Helps structure extracted data
│   │── display_information.py# (Optional) Displays processed results
│   │── metrics.py            # Evaluates processing accuracy
│   │── position_correction.py# Adjusts text positioning if necessary
│── main.py                   # Entry point for batch document processing
│── requirements.txt           # Required dependencies
│── README.md                  # Project documentation
│── config.json                # Configuration file containing API keys
│── .gitignore                 # Specifies files to be ignored by Git
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
Update `config.json` with your OpenAI API key and Google Vision credentials:
```json
{
    "openai_api_key": "your-openai-key",
    "google_vision_key": "your-google-vision-key"
}
```

## 📌 Usage
### Running the document processor
To process all documents in the `data/` directory, run:
```bash
python main.py
```

