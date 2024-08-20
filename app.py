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
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Load the uploaded GeoJSON file
    try:
        geojson_data = json.load(file)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid GeoJSON format"}), 400

    # Define projections (example for UTM zone 33N)
    utm_proj = pyproj.CRS('EPSG:22332')
    wgs84_proj = pyproj.CRS('EPSG:4326')

    # Transform coordinates
    project = pyproj.Transformer.from_crs(utm_proj, wgs84_proj, always_xy=True).transform

    for feature in geojson_data.get('features', []):
        geom = shape(feature['geometry'])
        geom_wgs84 = transform(project, geom)
        feature['geometry'] = mapping(geom_wgs84)

    # Save the converted GeoJSON file
    save_path = os.path.join('/tmp', 'converted.geojson')
    try:
        with open(save_path, 'w') as f:
            json.dump(geojson_data, f, indent=4)
    except IOError:
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
