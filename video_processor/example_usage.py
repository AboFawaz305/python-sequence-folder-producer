#!/usr/bin/env python3
"""
Example usage of the video processor as a Python module.
This demonstrates how to use the video processing functions programmatically.
"""

import os
import sys

# Add the video_processor directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.file_utils import (
    load_config, merge_config_and_args, 
    load_or_create_processing_report, get_video_files
)
from utils.video_utils import process_video, get_video_info
from utils.progress_utils import ProgressTracker


def process_videos_programmatically(input_folder, output_folder, config_file=None):
    """
    Example function that processes videos programmatically.
    """
    # Initialize progress tracker
    progress_tracker = ProgressTracker(use_color=True)
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        progress_tracker.print_error(f"Input folder '{input_folder}' does not exist")
        return False
    
    # Get video files
    video_files = get_video_files(input_folder)
    if not video_files:
        progress_tracker.print_warning(f"No video files found in '{input_folder}'")
        return False
    
    progress_tracker.print_info(f"Found {len(video_files)} video files")
    
    # Load configuration
    config = {}
    if config_file and os.path.exists(config_file):
        try:
            config = load_config(config_file)
            progress_tracker.print_info(f"Loaded configuration from '{config_file}'")
        except Exception as e:
            progress_tracker.print_warning(f"Failed to load config: {e}")
    
    # Set default settings
    default_args = {
        "sequence_size": 32,
        "output_format": ".mp4",
        "compression": "medium"
    }
    
    settings = merge_config_and_args(config, default_args)
    
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Load or create processing report
    report = load_or_create_processing_report(output_folder, input_folder)
    
    # Process each video
    total_sequences = 0
    for video_path in video_files:
        video_name = os.path.basename(video_path)
        progress_tracker.print_info(f"Processing: {video_name}")
        
        try:
            sequences_created = process_video(
                video_path, output_folder, settings, report, progress_tracker
            )
            total_sequences += sequences_created
        except Exception as e:
            progress_tracker.print_error(f"Error processing '{video_name}': {e}")
    
    progress_tracker.print_success(f"Processing complete! Created {total_sequences} sequences")
    return True


if __name__ == "__main__":
    # Example usage
    input_dir = "sample_videos"
    output_dir = "output_sequences"
    config_file = "config/default_config.json"
    
    print("Video Processor Example")
    print("=" * 50)
    print(f"Input folder: {input_dir}")
    print(f"Output folder: {output_dir}")
    print(f"Config file: {config_file}")
    print("=" * 50)
    
    # This would process videos if they existed
    success = process_videos_programmatically(input_dir, output_dir, config_file)
    
    if not success:
        print("\nTo test with real videos:")
        print("1. Create a 'sample_videos' folder")
        print("2. Add some video files (.mp4, .avi, etc.)")
        print("3. Run this script again")
    
    exit(0 if success else 1)