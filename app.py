from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin depuis Flutter

OUTPUT_FOLDER = "pdf_outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json  # Récupérer les données envoyées depuis Flutter

    if not data:
        return jsonify({'error': 'No data received'}), 400

    pdf_path = os.path.join(OUTPUT_FOLDER, 'table_results.pdf')

    # Création du fichier PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    c.drawString(50, height - 50, f"École : {data.get('schoolName', 'Inconnu')}")
    c.drawString(50, height - 70, f"Professeur : {data.get('profName', 'Inconnu')}")
    c.drawString(50, height - 90, f"Matière : {data.get('matiereName', 'Inconnu')}")
    c.drawString(50, height - 110, f"Classe : {data.get('className', 'Inconnu')}")
    c.drawString(50, height - 130, f"Date d'impression : {data.get('date', '')}")

    y_position = height - 160
    for student in data.get('students', []):
        c.drawString(50, y_position, f"{student['name']} - Note : {student['note']}")
        y_position -= 20
        if y_position < 50:  # Si on arrive en bas, ajouter une nouvelle page
            c.showPage()
            y_position = height - 50

    c.save()
    
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
