from flask import Flask, request, jsonify
import json
import pyproj
from shapely.geometry import shape, mapping
from shapely.ops import transform

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_geojson():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Load the uploaded GeoJSON file
    geojson_data = json.load(file)

    # Define projections (example for UTM zone 33N)
    utm_proj = pyproj.CRS('EPSG:22332')
    wgs84_proj = pyproj.CRS('EPSG:4326')

    # Transform coordinates
    project = pyproj.Transformer.from_crs(utm_proj, wgs84_proj, always_xy=True).transform

    for feature in geojson_data['features']:
        geom = shape(feature['geometry'])
        geom_wgs84 = transform(project, geom)
        feature['geometry'] = mapping(geom_wgs84)

    # Save the converted GeoJSON file
    save_path = '/tmp/converted.geojson'
    with open(save_path, 'w') as f:
        json.dump(geojson_data, f, indent=4)

    return jsonify({"message": "Conversion complete", "download_url": f"/download/{save_path}"}), 200

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

