import json
import abstra.forms as af
from abstra.tasks import send_task
from doc_vision.process_document import process_document
import tempfile

# Dropdown to select document type
document_type = af.read_dropdown(
    "Selecione o tipo de documento:", 
    options=[
        "RG",
        "CPF",
        "CNH",
        "Certidão de Nascimento",
        "Certidão de Casamento",
        "Comprovante de Endereço",
        "CTPS",
        "Holerite",
        "Imposto de Renda",
        "FGTS"
    ]
)

# File upload by user
uploaded_file = af.read_file("Faça o upload do documento para processar:")

if uploaded_file:
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(uploaded_file.file.read()) 
            temp_file_path = temp_file.name 

        # Process the document
        result = process_document(temp_file_path, document_type)

        print(f"✅ DEBUG: Resultado retornado pelo process_document:\n{json.dumps(result, indent=4, ensure_ascii=False)}")

        # Ensure that "Texto Visível" is available
        visible_text = result.get("Texto Visível", "Nenhum texto extraído.")
        structured_info = result.get("Informações Organizadas", {})

        # Prepare display content
        display_content = "<h3>Resultado:</h3>"
        display_content += f"<h3>Texto Visível:</h3><p>{visible_text}</p>"

        # Display structured JSON
        display_content += "<h3>Resultado Organizado:</h3>"
        display_content += f"<pre>{json.dumps(structured_info, indent=4, ensure_ascii=False)}</pre>"

        # Display the final content
        af.display_html(display_content)

    except Exception as e:
        print(f"❌ DEBUG: Erro ao processar documento: {e}")
        af.display_html(f"<span style='color: red;'>Erro ao processar: {e}</span>")

