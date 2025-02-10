import json
import abstra.forms as af
from doc_vision.process_document import process_document
import pdf2image
from io import BytesIO
from PIL import Image
import tempfile

# Select document type
document_type = af.read_dropdown(
    "Selecione o tipo de documento:", 
    options=[
        "RG", "CPF", "CNH", "Certidão de Nascimento",
        "Certidão de Casamento", "Comprovante de Endereço",
        "CTPS", "Holerite", "Imposto de Renda", "FGTS", "Driver's License"
    ]
)

# File upload
uploaded_file = af.read_file("Faça o upload do documento para processar:")

if uploaded_file:
    try:
        # Read file bytes
        file_bytes = uploaded_file.file.read()
        
        # Check if it is a PDF
        if uploaded_file.name.endswith(".pdf"):
            print("📄 Documento PDF detectado. Convertendo para imagem...")

            # Convert the first page of the PDF to an image (JPG)
            images = pdf2image.convert_from_bytes(file_bytes, dpi=300)

            # Save the first page as a temporary image
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
                images[0].save(temp_img.name, format="JPEG")
                temp_img_path = temp_img.name 

            print(f"✅ PDF convertido para imagem: {temp_img_path}")

            # Process the extracted image
            final_result = process_document(temp_img_path, document_type)

        else:
            # If it is an image, save it as a temporary file and process it directly
            img = Image.open(BytesIO(file_bytes))
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
                img.save(temp_img.name, format="JPEG")
                temp_img_path = temp_img.name

            print(f"✅ Imagem carregada: {temp_img_path}")

            final_result = process_document(temp_img_path, document_type)

        # Debug logs
        print(f"""✅ DEBUG: Resultado final:
{json.dumps(final_result, indent=4, ensure_ascii=False)}""")

        # Display results in the interface
        display_content = "<h3>Resultado:</h3>"
        display_content += f"<h3>Texto Visível:</h3><p>{final_result['Texto Visível']}</p>"
        display_content += "<h3>Resultado Organizado:</h3>"
        display_content += f"<pre>{json.dumps(final_result['Informações Organizadas'], indent=4, ensure_ascii=False)}</pre>"

        af.display_html(display_content)

    except Exception as e:
        error_message = f"<span style='color: red;'>Erro ao processar: {e}</span>"
        print(f"❌ DEBUG: {error_message}")
        af.display_html(error_message)
