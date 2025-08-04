"""
File utilities for video processing script.
Handles file I/O operations and processing report management.
"""

import os
import json
import yaml


def load_config(config_file_path):
    """
    Loads configuration from a specified JSON or YAML file.
    Returns a dictionary of configuration values.
    Raises an error if the file cannot be read or is invalid.
    """
    try:
        with open(config_file_path, "r") as config_file:
            if config_file_path.endswith(".json"):
                return json.load(config_file)
            elif config_file_path.endswith(".yaml") or config_file_path.endswith(".yml"):
                return yaml.safe_load(config_file)
            else:
                raise ValueError("Unsupported configuration file format. Use JSON or YAML.")
    except Exception as e:
        raise ValueError(f"Failed to load configuration file '{config_file_path}': {e}")


def merge_config_and_args(config, args):
    """
    Merges CLI arguments with configuration file values.
    CLI arguments take precedence over configuration file values.
    Returns a dictionary of merged settings.
    """
    merged = config.copy()
    merged.update({k: v for k, v in args.items() if v is not None})
    return merged


def load_or_create_processing_report(output_folder, input_folder):
    """
    Loads the processing report from the output folder if it exists.
    If not, creates a new processing report file.
    Returns the report as a dictionary.
    """
    report_path = os.path.join(output_folder, "processing-report.txt")

    # Load existing report
    if os.path.exists(report_path):
        try:
            with open(report_path, "r") as report_file:
                return json.load(report_file)
        except Exception as e:
            raise ValueError(f"Failed to load processing report: {e}")

    # Create a new report
    report = {"input_folder": input_folder, "videos": {}}
    save_progress(report, output_folder)
    return report


def save_progress(report, output_folder):
    """
    Saves the processing progress to the 'processing-report.txt' file.
    """
    report_path = os.path.join(output_folder, "processing-report.txt")
    try:
        # Ensure output directory exists
        os.makedirs(output_folder, exist_ok=True)
        with open(report_path, "w") as report_file:
            json.dump(report, report_file, indent=4)
    except Exception as e:
        raise ValueError(f"Failed to save processing report: {e}")


def get_video_files(input_folder):
    """
    Get list of video files from input folder.
    Supports common video formats.
    """
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
    video_files = []
    
    for filename in os.listdir(input_folder):
        if any(filename.lower().endswith(ext) for ext in video_extensions):
            video_files.append(os.path.join(input_folder, filename))
    
    return sorted(video_files)


def ensure_output_folder(output_folder):
    """
    Ensures the output folder exists, creates it if it doesn't.
    """
    os.makedirs(output_folder, exist_ok=True)