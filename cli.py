import os
import subprocess
import argparse

# Create an ArgumentParser object to handle command-line arguments
parser = argparse.ArgumentParser(description='Convert a video file to an audio file.')
parser.add_argument('input_file', help='input video file')
parser.add_argument('output_file', help='output audio file')
parser.add_argument('-b', '--bitrate', help='audio bitrate in kbps', default='256')

# Parse the command-line arguments
args = parser.parse_args()

# Get the input and output file names and the audio bitrate from the parsed arguments
input_file = args.input_file
output_file = args.output_file
bitrate = args.bitrate

# Construct the FFmpeg command
cmd = f'ffmpeg -i {input_file} -vn -acodec libmp3lame -ab {bitrate}k {output_file}'

# Run the FFmpeg command using subprocess
subprocess.run(cmd, shell=True)

# Check if the output file was created successfully
if os.path.isfile(output_file):
    print(f'{output_file} was created successfully.')
else:
    print('Error creating output file.')
