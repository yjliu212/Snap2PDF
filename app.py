from flask import Flask, request, render_template_string, send_file
import os
from PIL import Image, ExifTags

# Initialize Flask app
app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
#UPLOAD_FOLDER = ('uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}
MAX_FILES = 10  # Limit to 10 files

# HTML template with error handling
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snap2PDF - Trusted Image-to-PDF Converter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        .container {
            text-align: center;
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
        .how-it-works, .testimonials {
            margin: 40px auto;
            width: 60%;
            text-align: left;
        }
        .testimonial {
            margin-bottom: 20px;
            padding: 10px;
            border-left: 4px solid #007bff;
            background: #f9f9f9;
        }
        .footer {
            margin-top: 50px;
            background: #333;
            color: white;
            padding: 20px;
        }
        .footer a {
            color: white;
            text-decoration: none;
        }
        .footer a:hover {
            color: #ccc; /* Optional: Lighter gray color on hover */
            text-decoration: underline; /* Optional: Add underline on hover */
        }
        .footer a:visited {
            color: white; /* Ensure visited links remain white */
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="/static/snap2pdf_logo.png" alt="Snap2PDF Logo">
        </div>
        <h1>Snap2PDF - Trusted Image-to-PDF Converter</h1>
        <p>Upload your images, and we'll convert them into a PDF instantly!</p>

        <form action="/upload" method="POST" enctype="multipart/form-data">
            <div class="upload-section">
                <label for="file-upload">Upload your images (Max 10 files):</label><br><br>
                <input type="file" id="file-upload" name="file-upload" accept=".jpeg, .jpg, .png, .gif, .bmp, .tiff, .webp, .ico" multiple><br><br>
                <button class="btn" type="submit">Convert to PDF</button>
            </div>
        </form>

        <p style="font-size: 1.5em; font-weight: bold; color: #007bff; margin-top: 20px;">
        Over <span style="color: #ff6600;">{{ upload_count }}</span> images processed successfully!
        </p>

        <!-- How It Works Section -->
        <div class="how-it-works">
            <h2>How It Works</h2>
            <ol>
                <li>Select up to 10 image files (JPEG, JPG, or PNG).</li>
                <li>Click "Convert to PDF" to process your files.</li>
                <li>Your PDF will appear on your screen instantly!<br>
                    <strong>To save or share:</strong>
                    <ul>
                        <li><em>On iPhone:</em> Tap the <strong>up-arrow</strong> button and choose **Save to Files** or **Mail**.</li>
                        <li><em>On Android:</em> Use the browser menu to save or share the file.</li>
                        <li><em>On Desktop:</em> Use your browser's built-in options to download or share the file.</li>
                    </ul>
                </li>
            </ol>
        </div>


        <!-- Testimonials Section -->
        <div class="testimonials">
            <h2>What Our Users Say</h2>
            <div class="testimonial">
                <p><strong>Emily R.:</strong> "Snap2PDF is a lifesaver! I converted my images to PDF in seconds. Highly recommend!"</p>
            </div>
            <div class="testimonial">
                <p><strong>John M.:</strong> "The process was seamless, and I loved how secure it felt. Great job!"</p>
            </div>
            <div class="testimonial">
                <p><strong>Sarah K.:</strong> "The best PDF converter I’ve used. Clean interface and super fast."</p>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <div class="footer">
        <p>
            &copy; 2025 Snap2PDF. All rights reserved. |
            <a href="/privacy">Privacy Policy</a> |
            <a href="/contact">Contact Us</a> |
            <a href="/support">Support Us</a>
        </p>
    </div>

</body>
</html>
"""

# Function to validate file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        pass  # Ignore if the image has no EXIF data or orientation tag
    return image

@app.route('/')
def index():
    # Read the counter value
    counter_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload_counter.txt')
    with open(counter_file, 'r') as f:
        count = f.read()

    # Include the counter in the rendered template
    return render_template_string(html_template.replace("{{ upload_count }}", count))

@app.route('/privacy')
def privacy_policy():
    return """
    <h2>Privacy Policy</h2>
    <p>Your privacy is important to us. Here’s how we handle your data:</p>
    <ul>
        <li>Uploaded files are processed only to generate the requested PDF.</li>
        <li>All files are automatically deleted from our servers after processing.</li>
        <li>We do not store, share, or view your files.</li>
    </ul>
    <p>If you have any questions, feel free to <a href="/contact">Contact Us</a>.</p>
    """

@app.route('/support')
def support_us():
    support_page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Support Us</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin: 20px;
            }
            .donation-container {
                margin: 50px auto;
                padding: 20px;
                border: 1px solid #ccc;
                background: #f9f9f9;
                max-width: 600px;
                border-radius: 10px;
            }
            .donation-container h2 {
                color: #007bff;
            }
            .btn-donate {
                display: inline-block;
                padding: 10px 20px;
                color: white;
                background: #007bff;
                border: none;
                border-radius: 5px;
                text-decoration: none;
                font-size: 16px;
                margin: 20px 0;
            }
            .btn-donate:hover {
                background: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="donation-container">
            <h2>Support Snap2PDF</h2>
            <p>If you enjoy using Snap2PDF and want to help us keep it running, consider making a small donation. Every bit helps!</p>
            <a href="https://paypal.me/yangjunliu" class="btn-donate" target="_blank">
                Donate via PayPal
            </a>
            <p>Thank you for your support! ❤️</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(support_page)

@app.route('/contact')
def contact_us():
    return """
    <h2>Contact Us</h2>
    <p>If you have any questions, feedback, or issues, feel free to reach out to us:</p>
    <form action="/send-message" method="POST">
        <label for="name">Your Name:</label><br>
        <input type="text" id="name" name="name" required><br><br>

        <label for="email">Your Email:</label><br>
        <input type="email" id="email" name="email" required><br><br>

        <label for="message">Your Message:</label><br>
        <textarea id="message" name="message" rows="4" required></textarea><br><br>

        <button type="submit">Send Message</button>
    </form>
    """

@app.route('/send-message', methods=['POST'])
def send_message():
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Save the message to a file
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'messages.txt'), 'a') as f:
        f.write(f"Name: {name}\nEmail: {email}\nMessage: {message}\n{'-'*40}\n")

    # Display a thank-you message
    return f"""
    <h2>Message Sent</h2>
    <p>Thank you, {name}. Your message has been sent successfully.</p>
    <p>We will get back to you at <strong>{email}</strong> soon.</p>
    <a href="/">Return to Home</a>
    """

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('file-upload')

    # Check if files are uploaded
    if not files or all(file.filename == '' for file in files):
        return render_template_string(html_template, error="No files were selected for upload.")

    image_paths = []
    for file in files:
        # Validate file type
        if not allowed_file(file.filename):
            return render_template_string(html_template, error="Unsupported file type. Only JPEG, JPG, and PNG files are allowed.")

        # Save file to the uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        image_paths.append(file_path)

    # Convert images to a single PDF
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf')
    images = []
    for img_path in image_paths:
        img = Image.open(img_path)
        img = correct_image_orientation(img)  # Correct orientation
        img = img.convert("RGB")  # Ensure RGB mode for PDF
        images.append(img)

    images[0].save(pdf_path, save_all=True, append_images=images[1:])

    # Cleanup uploaded files
    for img_path in image_paths:
        os.remove(img_path)

    # Update the counter
    counter_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload_counter.txt')
    with open(counter_file, 'r+') as f:
        count = int(f.read())
        f.seek(0)
        f.write(str(count + len(files)))
        f.truncate()

    return send_file(pdf_path, as_attachment=True, download_name="converted.pdf")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
