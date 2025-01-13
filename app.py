from flask import Flask, request, render_template_string, send_file
import os
from PIL import Image, ExifTags

# Initialize Flask app
app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snap2PDF - Upload Images</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
        }
        .container {
            margin: 20px;
            padding: 20px;
        }
        .upload-section {
            border: 2px dashed #ccc;
            padding: 20px;
            margin: 20px auto;
            width: 50%;
            background: #f9f9f9;
        }
        .btn {
            padding: 10px 20px;
            color: white;
            background: #007bff;
            border: none;
            cursor: pointer;
        }
        .logo {
            margin: 20px;
        }
        img {
            max-width: 200px;
            height: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="/static/snap2pdf_logo.png" alt="Snap2PDF Logo">
        </div>
        <h1>Snap2PDF - Upload Images</h1>
        <p>Upload your images, and we'll convert them into a PDF!</p>

        <form action="/upload" method="POST" enctype="multipart/form-data">
            <div class="upload-section">
                <label for="file-upload">Upload your images:</label><br><br>
                <input type="file" id="file-upload" name="file-upload" accept=".jpeg, .jpg, .png" multiple><br><br>
                <button class="btn" type="submit">Convert to PDF</button>
            </div>
        </form>
    </div>
</body>
</html>
"""


# Function to correct image orientation based on EXIF metadata
def correct_image_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break
        exif = image._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation)
            if orientation_value == 3:  # Rotate 180 degrees
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:  # Rotate 270 degrees clockwise
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:  # Rotate 90 degrees clockwise
                image = image.rotate(90, expand=True)
    except Exception as e:
        # Ignore if the image has no EXIF data or orientation tag
        pass
    return image

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file-upload' not in request.files:
        return "No file part in the request", 400

    files = request.files.getlist('file-upload')  # Get multiple uploaded files
    image_paths = []

    # Save uploaded files
    for file in files:
        if file.filename == '':
            continue
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)  # Save each file to the uploads folder
        image_paths.append(file_path)

    # Convert images to a single PDF
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf')
    images = []
    for img_path in image_paths:
        img = Image.open(img_path)
        img = correct_image_orientation(img)  # Correct orientation
        img = img.convert("RGB")  # Ensure RGB mode for PDF
        images.append(img)

    # Save the images as a single PDF
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    for img_path in image_paths:
        os.remove(img_path)  # Cleanup image files after conversion

    return send_file(pdf_path, as_attachment=True, download_name="converted.pdf")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
