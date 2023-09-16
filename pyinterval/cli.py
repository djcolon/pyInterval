import logging
import yaml
import math
import os.path
from pydub import AudioSegment

def check_config(config: dict):
  """
  Checks configuration file. Exits program if issues are found.
  """
  logging.info("Checking config file for errors.")
  issues = []
  sources = []
  # Check settings.
  if 'settings' not in config:
    issues.append("Config file does not contain a 'settings' section.")
  if 'crossfade' not in config['settings']:
    issues.append("Settings section does not contain a crossfade definition.")
  if type(config['settings']['crossfade']) is not int:
    issues.append("settings > crossfade should be an integer.")
  if 'output_dir' not in config['settings']:
    issues.append("Settings section does not contain an output_dir definition.")
  if type(config['settings']['output_dir']) is not str:
    issues.append("Settings > output_dir should be a string.")
  if not os.path.isdir(config['settings']['output_dir']):
    issues.append("Settings > output_dir is not a directory.")
  
  # Check source definition.
  if 'source' not in config:
    issues.append("Config file does not contain a 'source' section.")
  else:
    if type(config['source']) is not dict:
      issues.append("'source' section should be a dict.")
    if len(config['source']) == 0:
      issues.append("'source' section has no content.")
    # Store the names of the sources to check them against output.
    for key in config['source'].keys():
      if len(config['source'][key]) == 0:
        issues.append("Source['{source}'] has no content.")
      sources.append(key)
  # Check output.
  if 'output' not in config:
    issues.append("Config file does not contain an 'output' section.")
  else:
    if type(config['output']) is not dict:
      issues.append("'output' section should be a dict.")
    if len(config['output']) == 0:
      issues.append("'output' section has no content.")
    for key in config['output']:
      output_item = config['output'][key]
      if type(output_item) is not list:
        issues.append(f"Output item {key} should be a list.")
      else:
        for i, entry in enumerate(output_item):
          if 'duration' not in entry:
            issues.append(f"Output item {key}, item #{i} has no duration.")
          if type(entry['duration']) is not int:
            issues.append(f"Output item {key}, item #{i} duration is not an integer.")
          if 'source' not in entry:
            issues.append(f"Output item {key}, item #{i} has no source.")
          if type(entry['source']) is not str:
            issues.append(f"Output item {key}, item #{i} source is not a string.")
          if entry['source'] not in sources:
            issues.append(f"Output item {key}, item #{i} has undefined source: '{entry['source']}'.")
  if len(issues) > 0:
    logging.error("Configuration file is invalid:")
    for issue in issues:
      logging.error(issue)
    exit(1)

def load_config(path: str) -> dict:
  """
  Loads the config file from the given path into a dict and does some sense
  checks on the format, exits with an error if this fails.
  """
  # Load the file.
  logging.info(f"Loading config file from: '{path}'.")
  try:
    with open(path, 'r') as file:
      config = yaml.safe_load(file)
  except Exception as e:
    logging.error(f"Failed to load config file at '{path}' with error: '{e}'. Terminating...")
    exit(1)
  # Sense check the format.
  try:
    check_config(config)
  except Exception as e:
    logging.error(f"Config file at '{path}' invalid: '{e}'. Terminating...")
    exit(1)
  return config

def load_mp3(path: str) -> AudioSegment:
  """
  Attempts to load a pydub AudioSegment from the given path, exits with an error
  if this fails.
  """
  logging.info(f"Loading source mp3 file from: '{path}'.")
  try:
    segment = AudioSegment.from_mp3(path)
  except Exception as e:
    logging.error(f"Failed to load source audio file at '{path}' with error: '{e}'. Terminating...")
    exit(1)
  return segment

def load_sources(source_config: dict) -> dict:
  """
  Loads the defined sources, concatenates all mp3s defined into a single
  AudioSegment and returns a dict of {source_name: AudioSegment}.
  """
  logging.info("Loading sources.")
   # Load the audio files.
  sources = {}
  for key in source_config.keys():
    # Concatenate the different source files.
    logging.info(f"Loading source files for source {key}.")
    source = AudioSegment.empty()
    for source_file_path in source_config[key]:
      logging.info(f"Adding '{source_file_path}' to source {key}.")
      source = source + load_mp3(source_file_path)
    sources[key] = source
  return sources

def generate_output_audio_segment(output_definition: list, sources: dict, crossfade: 100) -> AudioSegment:
  """
  Generates an AudioSegment from the input definition and source files.
  """
  # Track where we are in the source segment.
  source_position = {}
  for key in sources.keys():
    source_position[key] = 0
  # Then start building.
  result = AudioSegment.empty()
  for segment in output_definition:
    # Crossfade can't be longer than original segment.
    if crossfade > result.duration_seconds * 1000:
      segment_crossfade = math.floor(result.duration_seconds * 1000)

    segment_source = sources[segment['source']]
    if segment['duration'] > segment_source.duration_seconds:
      raise Exception(f"Segment duration of {str(segment['duration'])} longer than source '{segment['source']}'.")
    # Calculate the start and end position for our segment.
    start_position = source_position[segment['source']]
    end_position = start_position + segment['duration']
    # If we don't have enough time remaining in the source we'll need to do it in two steps.
    if(end_position > math.floor(segment_source.duration_seconds)):
      logging.info(f"Looping audio for source {segment['source']}.")
      result = result.append(segment_source[start_position*1000:segment_source.duration_seconds*1000], segment_crossfade)
      start_position = 0
      # Calculate the remainder.
      end_position = segment['duration'] - (segment_source.duration_seconds - end_position)
    # Then append...
    result = result.append(segment_source[start_position*1000:end_position*1000], segment_crossfade)
  return result


def main():
  """Main function."""
  logging.basicConfig(level=logging.INFO)
  logging.info("Starting pyInterval")

  # Get the config.
  config = load_config("config.yml")
  # Load the sources.
  sources = load_sources(config['source'])
  # Then generate outputs.
  for key in config['output']:
    logging.info(f"Generating audio segment for output {key}.")
    try:
      output_segment = generate_output_audio_segment(config['output'][key], sources, 100)
    except Exception as e:
      logging.error(f"Failed to generate output {key} with error: '{e}'. Terminating...")
      exit(1)
    output_path = os.path.join(config['settings']['output_dir'], f"{key}.mp3")
    logging.info(f"Saving audio segment for output {key} to '{output_path}'.")
    output_segment.export(output_path, format="mp3")

if __name__ == '__main__':
  main()