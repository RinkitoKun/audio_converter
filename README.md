# Audio Format Converter Application

A Python-based audio format converter supporting both sequential and parallel processing modes.

## Features

- Multiple format support (MP3, WAV, FLAC, OGG, AAC)
- Sequential and parallel conversion modes
- Real-time performance metrics
- Visual performance charts
- Dynamic thread configuration
- Progress tracking

## System Requirements

- Python 3.x
- FFmpeg installed on system
- Required Python packages:
  ```bash
  pip install pydub matplotlib tkinter
  ```

## Project Structure

```
Main Version - Copy/
├── audio_converter_base.py     # Base GUI and common functionality
├── audio_converter_sequential.py # Sequential processing implementation
├── audio_converter_parallel.py  # Parallel processing implementation
├── audio_converter_main.py     # Main application entry point
└── README.md                   # This documentation
```

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python audio_converter_main.py
   ```

## Usage Guide

### Basic Operation
1. Launch application
2. Select conversion mode (Sequential/Parallel)
3. Click "Select Audio Files"
4. Choose output format
5. Click "Convert Files"
6. Select output directory
7. Monitor progress

### Mode Selection
- **Sequential Mode**: Best for single/few files
- **Parallel Mode**: Optimal for multiple files

### Thread Configuration (Parallel Mode)
- 4 threads: Basic systems
- 8 threads: Default/Recommended
- 12/16 threads: High-performance systems

## Performance Characteristics

### Sequential Mode
- Time Complexity: O(n * s)
  - n = number of files
  - s = average file size
- Space Complexity: O(s)
  - Only one file in memory

### Parallel Mode
- Time Complexity: O((n/p) * s)
  - p = number of threads
- Space Complexity: O(p * s)
  - Up to p files in memory

## Architecture

### BaseAudioConverterApp (audio_converter_base.py)
- GUI foundation
- File management
- Progress tracking
- Performance visualization

### AudioConverterSequential (audio_converter_sequential.py)
- Single-threaded processing
- Sequential file handling
- Memory-efficient

### AudioConverterParallel (audio_converter_parallel.py)
- Multi-threaded processing
- ThreadPoolExecutor implementation
- Configurable thread count
- Queue-based UI updates

## Best Practices

### File Selection
- Group similar-sized files
- Consider available memory
- Check supported formats

### Mode Selection
- Sequential for:
  - Few files
  - Large individual files
  - Limited memory systems

- Parallel for:
  - Multiple files
  - Batch processing
  - Modern multi-core systems

### Thread Count Selection
1. Consider CPU cores
2. Monitor memory usage
3. Test with sample files
4. Adjust based on results

## Error Handling

- File format validation
- Memory management
- Thread safety
- UI responsiveness
- Progress recovery
- Error reporting

## Performance Tips

1. **File Size**
   - Large files: Sequential mode
   - Small files: Parallel mode

2. **Memory Management**
   - Monitor usage
   - Limit thread count
   - Group similar files

3. **System Load**
   - Consider other applications
   - Monitor CPU usage
   - Adjust thread count

## Contributing

1. Fork repository
2. Create feature branch
3. Add/modify features
4. Test thoroughly
5. Submit pull request

## License

MIT License - Feel free to use and modify.

## Support

For issues and questions:
1. Check documentation
2. Review error messages
3. Contact development team

## Version History

- 1.0.0: Initial release
  - Sequential and parallel modes
  - Basic format support
  - Performance metrics

## Future Enhancements

- Additional formats
- Custom thread allocation
- Advanced error recovery
- Format-specific optimization
- Batch preset support
