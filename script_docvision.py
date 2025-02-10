import json
from doc_vision.process_document import process_document
import pdf2image
from io import BytesIO
from PIL import Image
import tempfile
from abstra.tasks import get_trigger_task, send_task
import requests

task = get_trigger_task()

# Select document type
document_type = task['document_type']

# Select document extension
document_extension = task['document_extension']

# Upload file
document_url = task['document_url']

def get_document_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        document_content = response.content
        return document_content
    else:
        print("Falha ao baixar o documento")
        return None

uploaded_file = get_document_content(document_url)

if uploaded_file:
    print("Documento obtido com sucesso")

if uploaded_file:
    try:
        # Read file bytes
        file_bytes = uploaded_file

        # Check if is pdf
        if document_extension.endswith('pdf'):
            print("📄 Documento PDF detectado. Convertendo para imagem...")

            images = pdf2image.convert_from_bytes(file_bytes, dpi=300)

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

        print(display_content)

        send_task("document_type", {
            "visible_text" : final_result['Texto Visível'],
            "organized_data": final_result['Informações Organizadas'],
            **task.get_payload()
        })

    except Exception as e:
        error_message = f"<span style='color: red;'>Erro ao processar: {e}</span>"
        print(f"❌ DEBUG: {error_message}")
        print(error_message)
        
        send_task("document_type", {
            "error_message":f"Erro ao processar: {e}",
            **task.get_payload()
        })

task.complete()