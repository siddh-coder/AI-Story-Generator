from flask import Flask, request, jsonify, render_template
import io
from huggingface_hub import InferenceClient
from PIL import Image
import requests
import os
import base64

app = Flask(__name__)

# Hugging Face API settings
HF_API_KEY = os.getenv("HF_API_KEY")
#print(HF_API_KEY)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_gpt():
    data = request.json
    question = data.get('question')
    
    client = InferenceClient(api_key=HF_API_KEY)
    messages = [{"role": "user", "content": question}]
    
    stream = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct",
        messages=messages,
        max_tokens=1000,
        stream=True
    )
    
    answer = ""
    for chunk in stream:
        answer += chunk.choices[0].delta.content

    return jsonify({"answer": answer})

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt')
    
    API_URL = "https://api-inference.huggingface.co/models/Datou1111/shou_xin"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        img_io = io.BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)
        # Convert image to base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        return jsonify({"image_base64": img_base64})
    else:
        return jsonify({"error": "Failed to generate image"}), response.status_code

from flask import Flask, request, jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader  # Import ImageReader
import base64
import io
import requests
from PIL import Image

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    answer = data.get('answer', 'No answer provided.')
    image_base64 = data.get('image_base64', '')

    # Create an in-memory BytesIO object for the PDF
    pdf_stream = io.BytesIO()
    pdf_canvas = canvas.Canvas(pdf_stream, pagesize=A4)
    page_width, page_height = A4
    margin = 50
    text_width = page_width - 2 * margin
    text_height = page_height - 2 * margin

    # Add the text content to the PDF
    pdf_canvas.setFont("Helvetica", 12)
    y_position = page_height - margin  # Start from the top margin
    line_spacing = 14  # Adjust line spacing for better readability

    # Split text into lines that fit within the width of the page
    words = answer.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if pdf_canvas.stringWidth(test_line, "Helvetica", 12) <= text_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    # Add the last line
    if current_line:
        lines.append(current_line)

    # Write the lines to the PDF, handling page breaks
    for line in lines:
        if y_position < margin + line_spacing:  # Not enough space for another line
            pdf_canvas.showPage()
            pdf_canvas.setFont("Helvetica", 12)
            y_position = page_height - margin
        pdf_canvas.drawString(margin, y_position, line)
        y_position -= line_spacing

    # Add image if available
    if image_base64:
        image_data = base64.b64decode(image_base64.split(',')[1])
        image_stream = io.BytesIO(image_data)
        image_stream.seek(0)

        with Image.open(image_stream) as img:
            max_width = page_width - 2 * margin
            max_height = page_height / 3
            img.thumbnail((max_width, max_height))

            img_width, img_height = img.size
            x = margin
            y = y_position - img_height - margin

            if y <= 0:  # Not enough space for the image on the current page
                pdf_canvas.showPage()
                y = page_height - img_height - margin

            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            pdf_canvas.drawImage(ImageReader(img_bytes), x, y, width=img_width, height=img_height)

    # Finalize the PDF
    pdf_canvas.save()
    pdf_stream.seek(0)

    # Return PDF as base64
    pdf_base64 = base64.b64encode(pdf_stream.getvalue()).decode('utf-8')
    return jsonify({"pdf_base64": pdf_base64})



if __name__ == '__main__':
    app.run(debug=True)

