from flask import Flask, request,jsonify

import detect_MVP_items_multiple

app = Flask(__name__)

@app.route('/upload_image',methods = ["POST"])
def index():
    if not request.json or not 'image_path' in request.json:
        return "Add an image path"
    pages = detect_MVP_items_multiple.component_detector(request.json['image_path'])
    return jsonify(pages)

if __name__ == '__main__':
    app.run(debug=True)

#curl -i -X POST -d '{"image_path":"/Users/2020shatgiskessell/Downloads/IMG_1607.JPG"}' http://127.0.0.1:5000/upload_image
#curl -i -H "Content-Type: application/json" -X POST -d '{"image_path":"/Users/2020shatgiskessell/Downloads/IMG_1607.JPG"}' http://127.0.0.1:5000/upload_image
