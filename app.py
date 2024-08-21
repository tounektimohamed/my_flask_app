from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import json
import pyproj
from shapely.geometry import shape, mapping
from shapely.ops import transform
import os

app = Flask(__name__)
CORS(app)  # Permet toutes les origines par défaut

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_geojson():
    if 'file' not in request.files:
        app.logger.error("No file provided")
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        app.logger.error("No file selected")
        return jsonify({"error": "No file selected"}), 400

    try:
        geojson_data = json.load(file)
    except json.JSONDecodeError:
        app.logger.error("Invalid GeoJSON format")
        return jsonify({"error": "Invalid GeoJSON format"}), 400

    # Vérifier si le système de coordonnées est déjà WGS 84
    crs = geojson_data.get('crs', {}).get('properties', {}).get('name')
    if crs == 'urn:ogc:def:crs:OGC:1.3:CRS84' or crs == 'EPSG:4326':
        app.logger.info("Le fichier est déjà en WGS 84, pas de conversion nécessaire")
        save_path = os.path.join('/tmp', 'converted.geojson')
        try:
            with open(save_path, 'w') as f:
                json.dump(geojson_data, f, indent=4)
        except IOError:
            app.logger.error("Failed to save the file")
            return jsonify({"error": "Failed to save the file"}), 500

        return jsonify({"message": "Le fichier est déjà en WGS 84", "download_url": f"/download/converted.geojson"}), 200

    # Si le fichier n'est pas en WGS 84, le convertir
    try:
        utm_proj = pyproj.CRS('EPSG:22332')  # Remplacez par l'EPSG correct pour UTM
        wgs84_proj = pyproj.CRS('EPSG:4326')
        project = pyproj.Transformer.from_crs(utm_proj, wgs84_proj, always_xy=True).transform

        for feature in geojson_data.get('features', []):
            geom = shape(feature['geometry'])
            geom_wgs84 = transform(project, geom)
            feature['geometry'] = mapping(geom_wgs84)
    except Exception as e:
        app.logger.error(f"Error processing GeoJSON: {e}")
        return jsonify({"error": "Error processing GeoJSON"}), 500

    save_path = os.path.join('/tmp', 'converted.geojson')
    try:
        with open(save_path, 'w') as f:
            json.dump(geojson_data, f, indent=4)
    except IOError:
        app.logger.error("Failed to save the converted file")
        return jsonify({"error": "Failed to save the converted file"}), 500

    return jsonify({"message": "Conversion complete", "download_url": f"/download/converted.geojson"}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Ensure the file exists before attempting to send it
    file_path = os.path.join('/tmp', filename)
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
