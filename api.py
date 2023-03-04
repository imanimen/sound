from flask import Flask, request, jsonify
import os
import subprocess

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_video_to_audio():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({'message': 'No file in request.'}), 400
    
    file = request.files['file']
    
    # Check if the file is a video file
    if file.filename.split('.')[-1] not in ['mp4', 'avi', 'mkv']:
        return jsonify({'message': 'Invalid file type.'}), 400
    
    # Save the file to disk
    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Construct the FFmpeg command
    output_filename = os.path.splitext(filename)[0] + '.mp3'
    output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    cmd = f'ffmpeg -i {filepath} -vn -acodec libmp3lame -ab 256k {output_filepath}'
    
    # Run the FFmpeg command using subprocess
    subprocess.run(cmd, shell=True)
    
    # Check if the output file was created successfully
    if os.path.isfile(output_filepath):
        return jsonify({'message': 'Conversion successful.', 'file': output_filename}), 200
    else:
        return jsonify({'message': 'Error converting file.'}), 500

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.run(debug=True)
