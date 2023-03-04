import os
import subprocess

input_dir = 'videos'
output_dir = 'audios'
bitrate = '256'

# Loop over all video files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.mp4'):
        input_file = os.path.join(input_dir, filename)
        output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + '.mp3')
        cmd = f'ffmpeg -i {input_file} -vn -acodec libmp3lame -ab {bitrate}k {output_file}'
        subprocess.run(cmd, shell=True)
        if os.path.isfile(output_file):
            print(f'{output_file} was created successfully.')
        else:
            print(f'Error creating output file for {input_file}.')
