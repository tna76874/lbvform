#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LBV FORM WEBAPP
"""

from flask import Flask, request, render_template, send_file, send_from_directory, redirect, url_for
import os
import yaml
import zipfile
import io

from lbvform.module import *

app = Flask(__name__)

def add_pdf_to_zip(antrag, zip_file):
    """Fügt einen Antrag (PDF) zu einem ZIP-Objekt hinzu."""
    pdf_writer = antrag.rendered  # Angenommen, 'rendered' ist ein PdfWriter-Objekt
    pdf_bytes = io.BytesIO()
    pdf_writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    # Füge die PDF-Datei zum ZIP-Ordner hinzu
    zip_file.writestr(antrag._filename, pdf_bytes.getvalue())
    
# Fehler-Handler für Serverfehler
@app.errorhandler(500)
def internal_error(error):
    return redirect(url_for('index'))

@app.route('/example')
def download_example():
    return send_from_directory(os.path.join(app.root_path, 'example'), 'config.yml', as_attachment=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    # Überprüfen, ob die Datei eine YAML-Datei ist
    if not file.filename.endswith('.yml') and not file.filename.endswith('.yaml'):
        return 'File is not a YAML file', 400

    # YAML-Datei direkt im Speicher parsen
    try:
        data = yaml.safe_load(file.stream)
        
        LBV_frame = ReisekostenFrame(data = DatenParser(data), output=True)
        LBV_frame.render()
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for antrag in LBV_frame.antraege:
                add_pdf_to_zip(antrag, zip_file)
            
            add_pdf_to_zip(LBV_frame.genemigung, zip_file)
            
    
        zip_buffer.seek(0)
    
        return send_file(zip_buffer, as_attachment=True, download_name=f'reisekostenantrag_{LBV_frame.data.get_description()}.zip', mimetype='application/zip')


    except Exception as e:
        return f'Ungültige Konfigurationsdatei', 400

    return 'File uploaded and processed successfully', 200

if __name__ == '__main__':
    app.run(debug=True)
