"""
Progress utilities for video processing script.
Handles progress bars and logging with optional colored output.
"""

import sys
from tqdm import tqdm
try:
    from colorama import init, Fore, Style
    init()  # Initialize colorama
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class ProgressTracker:
    """Handles progress tracking with optional colored output."""
    
    def __init__(self, use_color=False):
        self.use_color = use_color and COLORAMA_AVAILABLE
        
    def print_info(self, message):
        """Print an info message with optional coloring."""
        if self.use_color:
            print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {message}")
        else:
            print(f"[INFO] {message}")
    
    def print_success(self, message):
        """Print a success message with optional coloring."""
        if self.use_color:
            print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}")
        else:
            print(f"[SUCCESS] {message}")
    
    def print_warning(self, message):
        """Print a warning message with optional coloring."""
        if self.use_color:
            print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}")
        else:
            print(f"[WARNING] {message}")
    
    def print_error(self, message):
        """Print an error message with optional coloring."""
        if self.use_color:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")
        else:
            print(f"[ERROR] {message}")
    
    def create_progress_bar(self, total, description="Processing"):
        """Create a progress bar with the specified total and description."""
        return tqdm(total=total, desc=description, unit="frame", 
                   bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
    
    def create_video_progress_bar(self, total_videos, description="Videos"):
        """Create a progress bar for tracking video processing."""
        return tqdm(total=total_videos, desc=description, unit="video",
                   bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')


def display_processing_summary(total_videos, total_sequences, skipped_videos):
    """Display a summary of the processing results."""
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    print(f"Total videos processed: {total_videos}")
    print(f"Total sequences created: {total_sequences}")
    print(f"Videos skipped (already processed): {skipped_videos}")
    print("="*50)