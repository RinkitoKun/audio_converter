"""
Main Audio Converter Application
Manages switching between sequential and parallel conversion modes.
"""

import tkinter as tk
from audio_converter_sequential import AudioConverterSequential
from audio_converter_parallel import AudioConverterParallel

class AudioConverter:
    """Main application class that handles mode switching."""
    
    def __init__(self):
        """Initialize the application."""
        self.setup_root()
        # Add threading flag
        self.is_converting = False
        self.start_sequential()  # Start in sequential mode by default

    def setup_root(self):
        """Setup the root window with proper closing behavior."""
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def start_sequential(self):
        """Switch to sequential conversion mode."""
        if hasattr(self, 'current_app'):
            self.save_state()
            self.current_app = None
            self.root.destroy()
            self.setup_root()
        self.current_app = AudioConverterSequential(self.root)
        self.current_app.on_mode_switch = self.start_parallel
        self.restore_state()
    
    def start_parallel(self):
        """Switch to parallel conversion mode."""
        if hasattr(self, 'current_app'):
            self.save_state()
            self.current_app = None
            self.root.destroy()
            self.setup_root()
        self.current_app = AudioConverterParallel(self.root)
        self.current_app.on_mode_switch = self.start_sequential
        self.restore_state()
    
    def save_state(self):
        """Save the current application state before switching modes."""
        if self.current_app:
            self.files = self.current_app.files.copy() if self.current_app.files else []
            self.output_format = self.current_app.output_format.get()
    
    def restore_state(self):
        """Restore the saved application state after switching modes."""
        if hasattr(self, 'files'):
            self.current_app.files = self.files.copy()
            self.current_app.update_files_listbox()
        if hasattr(self, 'output_format'):
            self.current_app.output_format.set(self.output_format)

    def on_closing(self):
        """Handle application closing with proper process cleanup."""
        try:
            if hasattr(self, 'current_app'):
                if isinstance(self.current_app, AudioConverterParallel):
                    # Force cleanup of any remaining processes
                    for process in getattr(self.current_app, '_active_processes', set()):
                        try:
                            if process.is_alive():
                                process.terminate()
                                process.join(timeout=1.0)
                        except:
                            pass
                    self.current_app._active_processes.clear()
                
                if hasattr(self.current_app, 'is_converting') and self.current_app.is_converting:
                    self.current_app.stop_conversion()
                if hasattr(self.current_app, 'conversion_active') and self.current_app.conversion_active:
                    self.current_app.conversion_active = False
        finally:
            if hasattr(self, 'root') and self.root:
                self.root.quit()
                self.root.destroy()
    
    def run(self):
        """Start the application main loop."""
        if hasattr(self, 'root') and self.root:
            self.root.mainloop()

if __name__ == "__main__":
    try:
        # Check if required libraries are installed
        import pydub
        import matplotlib
    except ImportError as e:
        print(f"Missing required library: {e}")
        print("Please install required libraries with:")
        print("pip install pydub matplotlib")
        print("Note: pydub requires ffmpeg to be installed on your system")
        exit(1)
    
    # Create and run the application
    app = AudioConverter()
    app.run()

# No Amdahl's Law code present in this file.