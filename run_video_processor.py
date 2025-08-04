#!/usr/bin/env python3
"""
Entry point for the Video Sequence Folder Producer.
This script allows running the video processor from the project root.
"""

import os
import sys

# Add the video_processor directory to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
video_processor_dir = os.path.join(script_dir, 'video_processor')
sys.path.insert(0, video_processor_dir)

# Import and run the main function
from main import main

if __name__ == "__main__":
    sys.exit(main())