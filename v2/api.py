from flask import Flask, request, jsonify
import os
import ffmpeg
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from google.oauth2 import service_account
import openai


# Initialize the Google Cloud Speech-to-Text API
credentials = service_account.Credentials.from_service_account_file('/path/to/service/account/key.json')
client = speech_v1.SpeechClient(credentials=credentials)

app = Flask(__name__)

# Initialize the OpenAI API
openai.api_key = 'YOUR_API_KEY'

@app.route('/open-ai/transcribe', methods=['POST'])
def transcribe():
    # Get the input audio file from the request
    audio_file = request.files.get('audio')

    # Convert the audio to base64 format
    audio_content = audio_file.read()
    audio_base64 = base64.b64encode(audio_content).decode('utf-8')

    # Use the OpenAI Whisper API to transcribe the audio
    response = openai.Completion.create(
        engine='davinci',
        prompt=f"Transcribe the following speech:\n{audio_base64}",
        max_tokens=2048,
        temperature=0.5,
        n = 1,
        stop=None
    )

    # Extract the transcript from the OpenAI response
    transcript = response.choices[0].text.strip()

    # Return the transcript
    return {'transcript': transcript}

@app.route('/google/transcribe', methods=['POST'])
def transcribe():
    # Get the input audio file from the request
    audio_file = request.files.get('audio')

    # Convert the audio to PCM format
    audio_content = audio_file.read()
    audio = speech_v1.types.RecognitionAudio(content=audio_content)
    config = speech_v1.types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code='en-US',
    )

    # Use the Google Cloud Speech-to-Text API to transcribe the audio
    response = client.recognize(config=config, audio=audio)
    transcript = response.results[0].alternatives[0].transcript

    # Return the transcript
    return {'transcript': transcript}

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
    
    # Construct the FFmpeg command using ffmpeg-python
    output_filename = os.path.splitext(filename)[0] + '.mp3'
    output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    (
        ffmpeg
        .input(filepath)
        .output(output_filepath, format='mp3', audio_bitrate='256k')
        .run()
    )
    
    # Check if the output file was created successfully
    if os.path.isfile(output_filepath):
        return jsonify({'message': 'Conversion successful.', 'file': output_filename}), 200
    else:
        return jsonify({'message': 'Error converting file.'}), 500

@app.route('/sound/convert', methods=['POST'])
def convert():
    # Get the input and output file formats from the request
    input_format = request.form.get('input_format')
    output_format = request.form.get('output_format')

    # Get the input file from the request
    file = request.files['file']
    
    # Save the file to disk
    filename = secure_filename(file.filename)
    file.save(filename)

    # Use ffmpeg to convert the file
    input_filename = f"{filename}.{input_format}"
    output_filename = f"{filename}.{output_format}"
    (
        ffmpeg
        .input(input_filename)
        .output(output_filename)
        .run()
    )

    # Send the converted file back to the client
    return send_file(output_filename, as_attachment=True)


@app.route('/trim', methods=['POST'])
def trim_audio():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({'message': 'No file in request.'}), 400
    
    file = request.files['file']
    
    # Check if the file is an audio file
    if file.filename.split('.')[-1] != 'mp3':
        return jsonify({'message': 'Invalid file type.'}), 400
    
    # Get the start and end times from the request
    start_time = request.form.get('start_time', None)
    end_time = request.form.get('end_time', None)
    
    if not start_time or not end_time:
        return jsonify({'message': 'Start and/or end time missing.'}), 400
    
    # Construct the FFmpeg command using ffmpeg-python
    input_filename = file.filename
    input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    output_filename = 'trimmed_' + input_filename
    output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    (
        ffmpeg
        .input(input_filepath)
        .filter('atrim', start=start_time, end=end_time)
        .output(output_filepath, format='mp3', audio_bitrate='256k')
        .run()
    )
    
    # Check if the output file was created successfully
    if os.path.isfile(output_filepath):
        return jsonify({'message': 'Trimming successful.', 'file': output_filename}), 200
    else:
        return jsonify({'message': 'Error trimming file.'}), 500

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.run(debug=True)
