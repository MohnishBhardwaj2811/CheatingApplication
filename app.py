from flask import Flask, request, jsonify, send_from_directory
import base64
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Access Phone Camera</title>
</head>
<body>
    <video id="video" autoplay playsinline></video>
    <button id="toggleCamera">Switch Camera</button>
    <button id="capture">Capture</button>
    <canvas id="canvas" style="display: none;"></canvas>
    <img id="capturedImage" style="display: none; width: 100%;" />

    <script>
        let isFrontCamera = false;
        let stream = null;

        async function startCamera() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            
            const constraints = {
                video: { facingMode: isFrontCamera ? "user" : "environment" }
            };
            
            try {
                stream = await navigator.mediaDevices.getUserMedia(constraints);
                document.getElementById('video').srcObject = stream;
            } catch (error) {
                console.error("Error accessing camera:", error);
            }
        }

        document.getElementById("toggleCamera").addEventListener("click", () => {
            isFrontCamera = !isFrontCamera;
            startCamera();
        });

        document.getElementById("capture").addEventListener("click", () => {
            const video = document.getElementById("video");
            const canvas = document.getElementById("canvas");
            const img = document.getElementById("capturedImage");

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const context = canvas.getContext("2d");
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const imageData = canvas.toDataURL("image/png");

            // Show the captured image
            img.src = imageData;
            img.style.display = "block";

            // Send image data to Flask backend
            fetch("/upload", {
                method: "POST",
                body: JSON.stringify({ image: imageData }),
                headers: { "Content-Type": "application/json" }
            })
            .then(response => response.json())
            .then(data => {
                console.log("Image uploaded successfully:", data);
                if (data.image_url) {
                    window.location.href = "/Image"; // Redirect to image display page
                }
            })
            .catch(error => console.error("Error uploading image:", error));
        });

        startCamera();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return index_html

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.json['image']
        image_data = base64.b64decode(data.split(',')[1])
        
        image_path = os.path.join(UPLOAD_FOLDER, "captured_image.png")
        with open(image_path, "wb") as f:
            f.write(image_data)

        return jsonify({"message": "Image uploaded successfully", "image_url": "/Image"})
    
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/Image')
def show_image():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Captured Image</title>
    </head>
    <body>
        <h2>Captured Image</h2>
        <img src="/static/uploads/captured_image.png" style="width:100%;" />
        <br><br>
        <a href="/">Go Back</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)
