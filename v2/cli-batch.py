import os
import argparse
from tqdm import tqdm
import ffmpeg
import torchaudio
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

# Initialize the Wav2Vec2ForCTC and Wav2Vec2Processor models
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

# Function to transcribe audio files
def transcribe(input_paths, output_path):
    # Create the output file if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # Loop through the input files and transcribe them
    for input_path in tqdm(input_paths):
        # Load the audio file and convert it to a tensor
        waveform, sample_rate = torchaudio.load(input_path)
        # Resample the audio if necessary
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)
        # Preprocess the audio tensor
        input_values = processor(waveform, sampling_rate=16000, return_tensors="pt").input_values
        # Get the model's predictions
        with torch.no_grad():
            logits = model(input_values).logits
        # Decode the model's output
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.decode(predicted_ids[0])
        # Write the transcription to a file
        output_file = os.path.join(output_path, os.path.splitext(os.path.basename(input_path))[0] + ".txt")
        with open(output_file, "w") as f:
            f.write(transcription)

# Function to trim audio files
def trim(input_path, output_path, start_time, end_time):
    # Load the audio file
    audio = ffmpeg.input(input_path)
    # Trim the audio
    audio = audio.trim(start_time=start_time, end_time=end_time)
    # Save the audio to a file
    audio = audio.output(output_path)
    audio.run()

if __name__ == "__main__":
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="CLI for audio processing.")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # Transcribe command
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe audio files")
    transcribe_parser.add_argument("input_dir", type=str, help="Input directory")
    transcribe_parser.add_argument("output_dir", type=str, help="Output directory")

    # Trim command
    trim_parser = subparsers.add_parser("trim", help="Trim audio files")
    trim_parser.add_argument("input_file", type=str, help="Input audio file")
    trim_parser.add_argument("output_file", type=str, help="Output audio file")
    trim_parser.add_argument("start_time", type=str, help="Start time in hh:mm:ss")
    trim_parser.add_argument("end_time", type=str, help="End time in hh:mm:ss")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Process the sub-commands
    if args.command == "transcribe":
        # Get the input and output directories
        input_dir = args.input_dir
        output_dir = args.output_dir
        # Get a list of input files
        # input_files = [os.path 
        # TODO: fix this


def transcribe(directory):
    """
    Transcribe all audio files in a directory using the OpenAI GPT-3 API.
    """
    # Get a list of all audio files in the directory
    audio_files = glob.glob(os.path.join(directory, '*.wav'))

    # Loop over each audio file and transcribe it
    for audio_file in audio_files:
        # Use FFmpeg to convert the audio file to a 16-bit PCM WAV file
        subprocess.run(['ffmpeg', '-i', audio_file, '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-f', 'wav', '-y', 'temp.wav'], check=True)

        # Use the OpenAI API to transcribe the audio
        with open('temp.wav', 'rb') as f:
            audio = f.read()
        response = openai.Completion.create(
            engine="davinci",
            prompt="# Transcribe the following audio:\n\n",
            inputs={
                "audio": audio,
                "audio_format": "wav"
            },
            output_prefix="Transcription:",
            max_tokens=2048
        )
        transcription = response.choices[0].text.strip()

        # Print the transcription
        print(f'Transcription of {audio_file}: {transcription}')

    # Remove the temporary WAV file
    os.remove('temp.wav')