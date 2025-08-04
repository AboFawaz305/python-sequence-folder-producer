#!/usr/bin/env python3
"""
Video Sequence Folder Producer

A Python script that uses OpenCV to transform videos from an input folder 
into smaller sequences of fixed frame size. The script handles progress 
tracking via a processing-report.txt file, allowing it to resume from 
where it stopped in case of interruptions.

Author: AboFawaz305
License: MIT
"""

import os
import sys
import argparse
from utils.file_utils import (
    load_config, merge_config_and_args, load_or_create_processing_report,
    save_progress, get_video_files, ensure_output_folder
)
from utils.video_utils import process_video, get_video_info
from utils.progress_utils import ProgressTracker, VideoProgressDisplay, display_processing_summary

# Constants
DEFAULT_SEQUENCE_SIZE = 32
DEFAULT_OUTPUT_FORMAT = ".mp4"
DEFAULT_SCALING_DIM = None
DEFAULT_FRAME_RATE = None
DEFAULT_COMPRESSION = "medium"
DEFAULT_REMOVE_AUDIO = True
DEFAULT_USE_GPU = False
DEFAULT_COLOR_OUTPUT = False
DEFAULT_CONFIG_FILE = "config/default_config.json"


def parse_arguments():
    """
    Parses command-line arguments and returns them as a dictionary.
    Handles missing or invalid arguments by providing defaults or raising errors.
    """
    parser = argparse.ArgumentParser(
        description="Process videos into smaller sequences.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -i /path/to/videos -o /path/to/output
  python main.py -i videos/ -o sequences/ -s 64 --scale 640x480
  python main.py -i input/ -o output/ --frame-rate 15 --compression high
        """
    )
    
    parser.add_argument(
        "-i", "--input-folder", 
        required=True,
        help="Path to input folder containing videos."
    )
    parser.add_argument(
        "-o", "--output-folder",
        help="Path to output folder for sequences. Defaults to 'sequences' in current directory."
    )
    parser.add_argument(
        "-s", "--sequence-size",
        type=int,
        default=DEFAULT_SEQUENCE_SIZE,
        help=f"Number of frames per sequence. Default: {DEFAULT_SEQUENCE_SIZE}"
    )
    parser.add_argument(
        "-f", "--output-format",
        default=DEFAULT_OUTPUT_FORMAT,
        choices=[".mp4", ".avi", ".mov", ".mkv"],
        help=f"Output video format. Default: {DEFAULT_OUTPUT_FORMAT}"
    )
    parser.add_argument(
        "--scale",
        default=DEFAULT_SCALING_DIM,
        help="Resolution for output videos (e.g., 640x480). Default: preserve original"
    )
    parser.add_argument(
        "--frame-rate",
        type=float,
        default=DEFAULT_FRAME_RATE,
        help="Frame rate for output videos. Default: preserve original"
    )
    parser.add_argument(
        "--compression",
        choices=["low", "medium", "high"],
        default=DEFAULT_COMPRESSION,
        help=f"Compression level for output videos. Default: {DEFAULT_COMPRESSION}"
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        default=DEFAULT_REMOVE_AUDIO,
        help="Remove audio from output videos (OpenCV default behavior)"
    )
    parser.add_argument(
        "--use-gpu",
        action="store_true",
        default=DEFAULT_USE_GPU,
        help="Enable GPU acceleration (if available)"
    )
    parser.add_argument(
        "--color",
        action="store_true",
        default=DEFAULT_COLOR_OUTPUT,
        help="Enable colored terminal output"
    )
    parser.add_argument(
        "-c", "--config",
        default=DEFAULT_CONFIG_FILE,
        help=f"Path to configuration file (JSON or YAML). Default: {DEFAULT_CONFIG_FILE}"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Display information about videos in input folder and exit"
    )
    
    args = vars(parser.parse_args())
    
    # Error handling for missing input folder
    if not os.path.exists(args["input_folder"]):
        raise ValueError(f"Input folder '{args['input_folder']}' does not exist.")
    
    # Set default output folder if not provided
    if not args["output_folder"]:
        args["output_folder"] = os.path.join(os.getcwd(), "sequences")
    
    return args


def display_video_info(video_files, progress_tracker):
    """Display information about videos in the input folder."""
    progress_tracker.print_info(f"Found {len(video_files)} video files:")
    print("\n" + "="*80)
    print(f"{'Filename':<30} {'Resolution':<12} {'Duration':<10} {'Frames':<8} {'FPS':<6}")
    print("="*80)
    
    total_duration = 0
    total_frames = 0
    
    for video_path in video_files:
        filename = os.path.basename(video_path)
        info = get_video_info(video_path)
        
        if info:
            duration_str = f"{info['duration']:.1f}s"
            total_duration += info['duration']
            total_frames += info['frame_count']
            
            print(f"{filename:<30} {info['resolution']:<12} {duration_str:<10} "
                  f"{info['frame_count']:<8} {info['fps']:<6.1f}")
        else:
            print(f"{filename:<30} {'ERROR':<12} {'ERROR':<10} {'ERROR':<8} {'ERROR':<6}")
    
    print("="*80)
    print(f"Total duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
    print(f"Total frames: {total_frames:,}")
    print("="*80)


def main():
    """Main entry point for the video processing script."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Initialize progress tracker
        progress_tracker = ProgressTracker(use_color=args.get("color", False))
        
        # Get list of video files
        video_files = get_video_files(args["input_folder"])
        
        if not video_files:
            progress_tracker.print_warning(f"No video files found in '{args['input_folder']}'")
            return 1
        
        # If info mode, display video information and exit
        if args.get("info"):
            display_video_info(video_files, progress_tracker)
            return 0
        
        progress_tracker.print_info(f"Found {len(video_files)} video files to process")
        
        # Load configuration
        config = {}
        config_path = args.get("config")
        
        # Try to load config from script directory if relative path
        if config_path and not os.path.isabs(config_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, config_path)
        
        if config_path and os.path.exists(config_path):
            try:
                config = load_config(config_path)
                progress_tracker.print_info(f"Loaded configuration from '{config_path}'")
            except Exception as e:
                progress_tracker.print_warning(f"Failed to load config: {e}")
        
        # Merge configuration with command line arguments
        settings = merge_config_and_args(config, args)
        
        # Ensure output folder exists
        ensure_output_folder(settings["output_folder"])
        
        # Load or create processing report
        report = load_or_create_processing_report(
            settings["output_folder"], 
            settings["input_folder"]
        )
        
        progress_tracker.print_info(f"Output folder: {settings['output_folder']}")
        progress_tracker.print_info(f"Sequence size: {settings['sequence_size']} frames")
        progress_tracker.print_info(f"Output format: {settings['output_format']}")
        
        if settings.get("scaling_dim"):
            progress_tracker.print_info(f"Scaling: {settings['scaling_dim']}")
        
        # Process videos
        skipped_videos = 0
        
        # Create custom progress display
        video_display = VideoProgressDisplay(len(video_files), settings.get("color_output", False))
        video_display.initialize_display()
        
        for video_index, video_path in enumerate(video_files, 1):
            video_name = os.path.basename(video_path)
            
            try:
                # Check if video was already fully processed
                if video_name in report.get("videos", {}):
                    video_info = report["videos"][video_name]
                    total_frames = video_info.get("total_frames", 0)
                    last_seq = video_info.get("last_seq_processed", 0)
                    expected_sequences = total_frames // settings["sequence_size"]
                    
                    if last_seq >= expected_sequences and expected_sequences > 0:
                        skipped_videos += 1
                        video_display.update_video_skipped()
                        continue
                
                # Get video total frames for progress tracking
                from utils.video_utils import get_video_info
                video_info_dict = get_video_info(video_path)
                total_frames = video_info_dict.get("total_frames", 0)
                
                video_display.update_video_start(video_index, video_name, total_frames)
                
                sequences_created = process_video(
                    video_path,
                    settings["output_folder"],
                    settings,
                    report,
                    video_display
                )
                
                video_display.update_video_completed()
                
            except Exception as e:
                progress_tracker.print_error(f"Error processing '{video_name}': {e}")
                video_display.update_video_completed()
        
        video_display.finalize_display()
        
        # Display final summary
        display_processing_summary(video_display.processed_videos, video_display.total_sequences, skipped_videos)
        
        # Final save of progress report
        save_progress(report, settings["output_folder"])
        
        progress_tracker.print_success("Processing completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())