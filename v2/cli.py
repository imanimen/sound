import click
import openai
import ffmpeg

openai.api_key = "YOUR_API_KEY"

@click.group()
def cli():
    pass

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
def transcribe(input_file, output_file):
    audio = ffmpeg.input(input_file)
    audio = ffmpeg.output(audio, 'pipe:', format='wav')
    audio = ffmpeg.run(audio, capture_stdout=True)

    response = openai.File.create(
        purpose='transcription', 
        file=openai.FileContent.from_bytes(audio),
        language='english'
    )
    
    transcription = response.transcription
    
    with open(output_file, 'w') as fw:
        fw.write(transcription)
        
    click.echo(f'Transcription saved to {output_file}.')


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--start', type=int, help='Start time in seconds')
@click.option('--end', type=int, help='End time in seconds')
def trim(input_file, output_file, start, end):
    input_audio = ffmpeg.input(input_file)
    
    if start is not None and end is not None:
        trimmed_audio = input_audio.trim(start=start, end=end)
    elif start is not None:
        trimmed_audio = input_audio.trim(start=start)
    elif end is not None:
        trimmed_audio = input_audio.trim(end=end)
    else:
        raise click.BadArgumentUsage("At least one of 'start' or 'end' must be provided.")
    
    output_audio = ffmpeg.output(trimmed_audio, output_file)
    ffmpeg.run(output_audio)
    
    click.echo(f'{input_file} trimmed and saved as {output_file}.')

cli.add_command(trim)
cli.add_command(transcribe)

if __name__ == '__main__':
    cli()