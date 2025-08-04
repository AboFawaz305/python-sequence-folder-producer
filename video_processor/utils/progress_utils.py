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

try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from rich.live import Live
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class VideoProgressDisplay:
    """Custom progress display for video processing that updates in place."""
    
    def __init__(self, total_videos, use_color=False):
        self.total_videos = total_videos
        self.processed_videos = 0
        self.total_sequences = 0
        self.current_video_num = 0
        self.current_video_name = ""
        self.current_video_frames = 0
        self.current_video_total_frames = 0
        self.use_color = use_color and COLORAMA_AVAILABLE
        self.console = Console() if RICH_AVAILABLE else None
        self.lines_printed = 0
        
    def update_video_start(self, video_num, video_name, total_frames):
        """Update display when starting a new video."""
        self.current_video_num = video_num
        self.current_video_name = video_name
        self.current_video_frames = 0
        self.current_video_total_frames = total_frames
        self._update_display()
    
    def update_video_progress(self, current_frame):
        """Update the current video's frame progress."""
        self.current_video_frames = current_frame
        self._update_display()
    
    def update_sequence_created(self):
        """Increment total sequences count."""
        self.total_sequences += 1
        # Don't update display here to reduce flicker
    
    def update_video_completed(self):
        """Mark current video as completed."""
        self.processed_videos += 1
        self._update_display()
    
    def update_video_skipped(self):
        """Mark current video as skipped."""
        self.processed_videos += 1
        self._update_display()
    
    def _create_progress_bar(self, current, total, width=20):
        """Create a text-based progress bar."""
        if total == 0:
            return "[" + "-" * width + "]"
        
        filled = int((current / total) * width)
        bar = "█" * filled + "-" * (width - filled)
        return f"[{bar}]"
    
    def _update_display(self):
        """Update the progress display in place."""
        if RICH_AVAILABLE:
            self._update_rich_display()
        else:
            self._update_basic_display()
    
    def _update_rich_display(self):
        """Update display using rich library."""
        # Use rich's capabilities for clean updating
        if hasattr(self, '_live'):
            self._live.stop()
        
        content = []
        content.append(f"Processed {self.processed_videos} of {self.total_videos} videos")
        content.append(f"Total Sequences Produced: {self.total_sequences}")
        
        if self.current_video_num > 0 and self.current_video_total_frames > 0:
            percentage = (self.current_video_frames / self.current_video_total_frames) * 100
            progress_bar = self._create_progress_bar(self.current_video_frames, self.current_video_total_frames)
            content.append(
                f"Video {self.current_video_num}: {progress_bar} {percentage:.0f}% "
                f"({self.current_video_frames}/{self.current_video_total_frames} frames)"
            )
        
        # Print content
        sys.stdout.write('\r\033[K')  # Clear current line
        for i, line in enumerate(content):
            if i > 0:
                sys.stdout.write('\033[1A\033[K')  # Move up and clear line
            print(line)
        sys.stdout.flush()
    
    def _update_basic_display(self):
        """Update display using basic print with ANSI escape codes."""
        # Clear previous output if any
        if self.lines_printed > 0:
            for _ in range(self.lines_printed):
                sys.stdout.write('\033[1A\033[K')  # Move up one line and clear it
        
        content = []
        content.append(f"Processed {self.processed_videos} of {self.total_videos} videos")
        content.append(f"Total Sequences Produced: {self.total_sequences}")
        
        if self.current_video_num > 0 and self.current_video_total_frames > 0:
            percentage = (self.current_video_frames / self.current_video_total_frames) * 100
            progress_bar = self._create_progress_bar(self.current_video_frames, self.current_video_total_frames)
            content.append(
                f"Video {self.current_video_num}: {progress_bar} {percentage:.0f}% "
                f"({self.current_video_frames}/{self.current_video_total_frames} frames)"
            )
        
        # Print all content
        for line in content:
            print(line)
        
        self.lines_printed = len(content)
        sys.stdout.flush()
    
    def initialize_display(self):
        """Initialize the display with empty lines."""
        print("Processed 0 of {} videos".format(self.total_videos))
        print("Total Sequences Produced: 0")
        print()  # Empty line for video progress
        self.lines_printed = 3
    
    def finalize_display(self):
        """Finalize the display."""
        print()  # Add a newline after the final display


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