# Python Video Sequence Folder Producer

A Python script that uses OpenCV to transform videos from an input folder into smaller sequences of fixed frame size (e.g., 32 frames each). The script handles progress tracking via a processing-report.txt file, allowing it to resume from where it stopped in case of interruptions.

## Project Structure

```
python-sequence-folder-producer/
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── run_video_processor.py            # Entry point from project root
├── .gitignore                        # Git ignore rules
├── video_processor/
│   ├── main.py                       # Main CLI application
│   ├── example_usage.py              # Example programmatic usage
│   ├── config/
│   │   ├── default_config.json       # Default JSON configuration
│   │   └── sample_config.yaml        # Sample YAML configuration
│   └── utils/
│       ├── __init__.py               # Package initialization
│       ├── file_utils.py             # File I/O and report handling
│       ├── video_utils.py            # Video processing functions
│       └── progress_utils.py         # Progress tracking utilities
```

## Features

- **Input and Output Handling**: Read videos from an input folder and save processed sequences in the output folder
- **Processing Report**: Save processing progress in `processing-report.txt` for resumable operations
- **Video Processing**: Split videos into smaller sequences of a fixed size with optional scaling and compression
- **Customization**: Configure behavior via CLI arguments and configuration files
- **Performance Optimization**: Batch-read frames and efficient resource management
- **Real-Time Feedback**: Display real-time progress with optional colored terminal output

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AboFawaz305/python-sequence-folder-producer.git
cd python-sequence-folder-producer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies

- `opencv-python>=4.8.0` - Video processing
- `tqdm>=4.65.0` - Progress bars
- `colorama>=0.4.6` - Colored terminal output
- `PyYAML>=6.0` - YAML configuration support

## Usage

### Basic Usage

From the project root:
```bash
python run_video_processor.py -i /path/to/input/videos -o /path/to/output/sequences
```

Or from the video_processor directory:
```bash
cd video_processor
python main.py -i /path/to/input/videos -o /path/to/output/sequences
```

### Advanced Usage

From the project root:
```bash
# Custom sequence size and scaling
python run_video_processor.py -i videos/ -o sequences/ -s 64 --scale 640x480

# With compression and frame rate control
python run_video_processor.py -i input/ -o output/ --frame-rate 15 --compression high

# Display video information without processing
python run_video_processor.py -i videos/ --info

# Enable colored output
python run_video_processor.py -i videos/ -o sequences/ --color
```

From the video_processor directory:
```bash
# Custom sequence size and scaling
python main.py -i videos/ -o sequences/ -s 64 --scale 640x480

# With compression and frame rate control
python main.py -i input/ -o output/ --frame-rate 15 --compression high

# Display video information without processing
python main.py -i videos/ --info

# Enable colored output
python main.py -i videos/ -o sequences/ --color
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-i, --input-folder` | Path to input folder containing videos | Required |
| `-o, --output-folder` | Path to output folder for sequences | `./sequences` |
| `-s, --sequence-size` | Number of frames per sequence | `32` |
| `-f, --output-format` | Output video format (.mp4, .avi, .mov, .mkv) | `.mp4` |
| `--scale` | Resolution for output videos (e.g., 640x480) | Original resolution |
| `--frame-rate` | Frame rate for output videos | Original frame rate |
| `--compression` | Compression level (low, medium, high) | `medium` |
| `--no-audio` | Remove audio from output videos | `True` |
| `--use-gpu` | Enable GPU acceleration (if available) | `False` |
| `--color` | Enable colored terminal output | `False` |
| `-c, --config` | Path to configuration file | `config/default_config.json` |
| `--info` | Display video information and exit | `False` |

## Configuration File

You can create a JSON or YAML configuration file to set default options:

### JSON Configuration (config/default_config.json)
```json
{
    "sequence_size": 32,
    "output_format": ".mp4",
    "scaling_dim": null,
    "frame_rate": null,
    "compression": "medium",
    "remove_audio": true,
    "use_gpu": false,
    "color_output": false
}
```

### YAML Configuration
```yaml
sequence_size: 32
output_format: ".mp4"
scaling_dim: null
frame_rate: null
compression: "medium"
remove_audio: true
use_gpu: false
color_output: false
```

**Note**: Command line arguments take precedence over configuration file values.

## Output Structure

The script creates the following structure:

```
output_folder/
├── processing-report.txt          # Progress tracking file
├── video1_seq0001.mp4            # First sequence from video1
├── video1_seq0002.mp4            # Second sequence from video1
├── video2_seq0001.mp4            # First sequence from video2
└── ...
```

## Processing Report

The `processing-report.txt` file tracks processing progress:

```json
{
    "input_folder": "/path/to/input",
    "videos": {
        "video1.mp4": {
            "total_frames": 1000,
            "stopped_at_frame": 960,
            "last_seq_processed": 30
        }
    }
}
```

This allows the script to resume from where it left off if interrupted.

## Supported Video Formats

**Input formats**: .mp4, .avi, .mov, .mkv, .wmv, .flv, .webm, .m4v

**Output formats**: .mp4, .avi, .mov, .mkv

## Examples

### Example 1: Basic video processing
```bash
# From project root
python run_video_processor.py -i ./sample_videos -o ./output_sequences

# Or from video_processor directory
cd video_processor
python main.py -i ./sample_videos -o ./output_sequences
```

### Example 2: Custom settings with configuration
```bash
python run_video_processor.py -i ./videos -o ./sequences -s 16 --scale 720x480 --compression high --color
```

### Example 3: Check video information first
```bash
python run_video_processor.py -i ./videos --info
```

### Example 4: Resume interrupted processing
```bash
# The script automatically resumes from the last processed sequence
python run_video_processor.py -i ./videos -o ./sequences
```

### Example 5: Using as a Python module
```bash
cd video_processor
python example_usage.py
```

## Performance Tips

1. **GPU Acceleration**: Use `--use-gpu` if you have OpenCV compiled with CUDA support
2. **Batch Size**: The script processes videos in batches to optimize memory usage
3. **Storage**: Use SSD storage for better I/O performance
4. **Resolution**: Consider scaling down videos with `--scale` to reduce processing time and output size

## Troubleshooting

### Common Issues

1. **"Failed to open video"**: Check if the video file is corrupted or in an unsupported format
2. **"Permission denied"**: Ensure you have write permissions to the output directory
3. **"Out of memory"**: Try processing smaller videos or use scaling to reduce memory usage

### Debug Mode

For debugging, you can check the processing report file to see the exact state of each video:

```bash
cat output_folder/processing-report.txt
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Author

AboFawaz305