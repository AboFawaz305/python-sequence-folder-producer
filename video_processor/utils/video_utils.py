"""
Video processing utilities for the video sequence producer.
Handles video processing, sequence generation, and OpenCV operations.
"""

import os
import cv2
from .file_utils import save_progress


def get_resume_state(video_path, report, sequence_size):
    """
    Get the resume state for a video from the processing report.
    Returns (start_frame, last_sequence) tuple.
    """
    video_name = os.path.basename(video_path)
    
    if video_name in report.get("videos", {}):
        video_info = report["videos"][video_name]
        last_seq = video_info.get("last_seq_processed", 0)
        start_frame = last_seq * sequence_size
        return start_frame, last_seq
    
    return 0, 0


def get_video_writer_settings(settings):
    """
    Get OpenCV VideoWriter settings based on configuration.
    """
    fourcc_map = {
        ".mp4": cv2.VideoWriter_fourcc(*'mp4v'),
        ".avi": cv2.VideoWriter_fourcc(*'XVID'),
        ".mov": cv2.VideoWriter_fourcc(*'mp4v'),
        ".mkv": cv2.VideoWriter_fourcc(*'XVID'),
    }
    
    compression_quality = {
        "low": 50,
        "medium": 75,
        "high": 90
    }
    
    output_format = settings.get("output_format", ".mp4")
    fourcc = fourcc_map.get(output_format, cv2.VideoWriter_fourcc(*'mp4v'))
    
    return fourcc, compression_quality.get(settings.get("compression", "medium"), 75)


def scale_frame(frame, scale_setting):
    """
    Scale a frame according to the scaling setting.
    scale_setting should be in format "WIDTHxHEIGHT" (e.g., "640x480")
    """
    if scale_setting and 'x' in scale_setting:
        try:
            width, height = map(int, scale_setting.split('x'))
            return cv2.resize(frame, (width, height))
        except ValueError:
            pass  # Invalid format, return original frame
    return frame


def save_sequence(frames, output_folder, video_name, sequence_num, settings):
    """
    Save a sequence of frames as a video file.
    """
    if not frames:
        return False
    
    # Create sequence filename
    base_name = os.path.splitext(video_name)[0]
    output_format = settings.get("output_format", ".mp4")
    sequence_filename = f"{base_name}_seq{sequence_num:04d}{output_format}"
    sequence_path = os.path.join(output_folder, sequence_filename)
    
    # Get video writer settings
    fourcc, _ = get_video_writer_settings(settings)
    
    # Get frame dimensions from first frame
    height, width = frames[0].shape[:2]
    
    # Determine frame rate
    frame_rate = settings.get("frame_rate", 30.0)
    if frame_rate is None:
        frame_rate = 30.0
    
    # Create video writer
    writer = cv2.VideoWriter(sequence_path, fourcc, frame_rate, (width, height))
    
    if not writer.isOpened():
        return False
    
    try:
        # Write all frames
        for frame in frames:
            writer.write(frame)
        return True
    except Exception:
        return False
    finally:
        writer.release()


def process_video(video_path, output_folder, settings, report, progress_tracker):
    """
    Processes a single video into sequences.
    Updates the processing report after processing each sequence.
    """
    video_name = os.path.basename(video_path)
    sequence_size = settings.get("sequence_size", 32)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        progress_tracker.print_error(f"Failed to open video '{video_path}'")
        return 0
    
    try:
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Get resume state
        start_frame, last_sequence = get_resume_state(video_path, report, sequence_size)
        
        # Check if video is already fully processed
        expected_sequences = total_frames // sequence_size
        if last_sequence >= expected_sequences:
            progress_tracker.print_info(f"Video '{video_name}' already fully processed. Skipping.")
            return 0
        
        # Set starting position
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        current_frame = start_frame
        sequences_produced = last_sequence
        
        progress_tracker.print_info(f"Processing '{video_name}' - Total frames: {total_frames}, FPS: {fps:.2f}")
        if start_frame > 0:
            progress_tracker.print_info(f"Resuming from frame {start_frame} (sequence {last_sequence})")
        
        # Process sequences
        new_sequences = 0
        while current_frame + sequence_size <= total_frames:
            frames = []
            
            # Read sequence_size frames
            for _ in range(sequence_size):
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply scaling if specified
                if settings.get("scaling_dim"):
                    frame = scale_frame(frame, settings["scaling_dim"])
                
                frames.append(frame)
            
            # Save sequence if we have enough frames
            if len(frames) == sequence_size:
                if save_sequence(frames, output_folder, video_name, sequences_produced, settings):
                    sequences_produced += 1
                    new_sequences += 1
                    current_frame += sequence_size
                    
                    # Update progress report
                    if video_name not in report["videos"]:
                        report["videos"][video_name] = {}
                    
                    report["videos"][video_name].update({
                        "total_frames": total_frames,
                        "stopped_at_frame": current_frame,
                        "last_seq_processed": sequences_produced
                    })
                    
                    # Save progress periodically
                    if sequences_produced % 10 == 0:  # Save every 10 sequences
                        save_progress(report, output_folder)
                else:
                    progress_tracker.print_error(f"Failed to save sequence {sequences_produced} for '{video_name}'")
                    break
            else:
                break
        
        # Final progress save
        save_progress(report, output_folder)
        
        if new_sequences > 0:
            progress_tracker.print_success(f"Created {new_sequences} new sequences from '{video_name}'")
        
        return new_sequences
        
    finally:
        cap.release()


def get_video_info(video_path):
    """
    Get basic information about a video file.
    Returns dict with frame count, fps, duration, and resolution.
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return None
    
    try:
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        return {
            "frame_count": frame_count,
            "fps": fps,
            "duration": duration,
            "resolution": f"{width}x{height}",
            "width": width,
            "height": height
        }
    finally:
        cap.release()