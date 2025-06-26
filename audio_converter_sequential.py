"""
Sequential Audio Converter Implementation
Handles audio file conversion in a sequential manner.
"""
import os
import time
import threading
from queue import Queue, Empty
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pydub import AudioSegment
from audio_converter_base import BaseAudioConverterApp

class AudioConverterSequential(BaseAudioConverterApp):
    def __init__(self, root):
        super().__init__(root, "Audio Format Converter - Sequential Version", mode='sequential')
        self.root = root
        self.on_mode_switch = None
        self.complexity_var = tk.StringVar(value="Complexity: Not calculated yet")
        self.should_stop = False
        self.is_converting = False
        self.ui_queue = Queue()
        self.conversion_active = False
        self.progress_var = tk.IntVar(value=0)
        self.setup_complexity_display()
        self._start_ui_update_loop()
        self.progress_bar["variable"] = self.progress_var

    # ---------------- UI Setup and Update Methods ----------------
    def _start_ui_update_loop(self):
        """Start the UI update loop to handle updates from worker thread."""
        try:
            while not self.ui_queue.empty():
                try:
                    action, data = self.ui_queue.get_nowait()
                    self._handle_ui_action(action, data)
                except Empty:
                    break
            if self.conversion_active:
                self.root.after(100, self._start_ui_update_loop)
        except Exception as e:
            print(f"Error in UI update loop: {str(e)}")
            self._reset_ui_state()

    def _handle_ui_action(self, action, data):
        """Handle UI actions from the conversion thread."""
        if action == "progress":
            self.progress_var.set(data)
            self.progress_bar["value"] = data
            self.root.update_idletasks()
        elif action == "status":
            self.status_var.set(data)
        elif action == "error":
            messagebox.showerror("Conversion Error", data)
        elif action == "complete":
            self._handle_conversion_complete(data)
        elif action == "enable_buttons":
            self._reset_ui_state()

    # ---------------- Conversion Methods ----------------
    def start_conversion(self):
        """Start the sequential conversion process."""
        if not self.files:
            messagebox.showwarning("No Files", "No files selected!")
            return
        try:
            if not self._setup_conversion():
                return
            self._initialize_conversion()
            # Start conversion in a background thread to keep UI responsive
            threading.Thread(target=self.convert_files, daemon=True).start()
            self._start_ui_update_loop()
        except Exception as e:
            self._handle_conversion_error(e)

    def convert_files(self):
        """Convert files sequentially."""
        try:
            total_start_time = time.time()
            self.conversion_times = []
            completed = 0
            
            self.ui_queue.put(("status", "Starting sequential conversion..."))
            self.ui_queue.put(("progress", completed))

            for i, file_path in enumerate(self.files):
                if self.should_stop:
                    break

                try:
                    current_file = os.path.basename(file_path)
                    self.ui_queue.put(("status", f"Converting {current_file} ({i+1}/{self.total_files})"))
                    
                    file_start = time.time()
                    self.convert_file(file_path, self.output_directory, self.selected_format)
                    conversion_time = time.time() - file_start
                    
                    completed += 1
                    # Store conversion time for each file
                    self.conversion_times.append((current_file, conversion_time))
                    self.ui_queue.put(("progress", completed))
                    
                except Exception as e:
                    self.ui_queue.put(("error", f"Error converting {current_file}: {str(e)}"))
                    continue

            if completed == self.total_files:
                self.ui_queue.put(("progress", self.total_files))
                
            total_time = time.time() - total_start_time
            if not self.should_stop:
                self.ui_queue.put(("complete", (completed, total_time)))
            
        except Exception as e:
            self._handle_conversion_error(e)
        finally:
            self._reset_ui_state()
            self.should_stop = False

    def convert_file(self, file_path, output_dir, output_format):
        """Convert a single audio file with error handling."""
        try:
            base_name = os.path.basename(file_path)
            file_name, _ = os.path.splitext(base_name)
            output_path = os.path.join(output_dir, f"{file_name}{output_format}")
            # Load and export audio file using pydub
            audio = AudioSegment.from_file(file_path)
            audio.export(output_path, format=output_format[1:])
        except Exception as e:
            raise Exception(f"Failed to convert {os.path.basename(file_path)}: {str(e)}")

    # ---------------- Utility Methods ----------------
    def _setup_conversion(self):
        """Prepare for conversion by calculating metrics and getting user input."""
        total_size = sum(os.path.getsize(f) for f in self.files)
        avg_size_mb = (total_size / len(self.files)) / (1024 * 1024)
        n_files = len(self.files)
        
        self.complexity_var.set(self.calculate_complexity_metrics(n_files, avg_size_mb))
        self.selected_format = self.formats[self.output_format.get()]
        self.output_directory = filedialog.askdirectory(title="Select Output Directory")
        
        return bool(self.output_directory)

    def _initialize_conversion(self):
        """Initialize conversion parameters and UI elements."""
        self.conversion_active = True
        self.is_converting = True
        self.convert_btn.config(state="disabled")
        self.switch_btn.config(state="disabled")
        self.progress_var.set(0)
        self.progress_bar["value"] = 0
        self.total_files = len(self.files)
        self.progress_bar["maximum"] = self.total_files

    def setup_complexity_display(self):
        """Setup the complexity metrics display."""
        complexity_frame = ttk.LabelFrame(self.scrollable_frame, text="Algorithm Analysis", padding=(16, 10))
        complexity_frame.pack(fill=tk.X, pady=(0, 16), before=self.chart_frame)
        
        complexity_label = ttk.Label(complexity_frame, textvariable=self.complexity_var,
                                   font=("Segoe UI", 11), wraplength=800)
        complexity_label.pack(pady=5)

    def calculate_complexity_metrics(self, n_files, avg_file_size_mb):
        """Calculate and format complexity metrics for display."""
        time_complexity = f"O({n_files} * {avg_file_size_mb:.1f}MB)"
        space_complexity = f"O({avg_file_size_mb:.1f}MB)"
        total_io = f"O({n_files} * {avg_file_size_mb:.1f}MB)"
        
        return (f"Time Complexity: {time_complexity} - Processing {n_files} files sequentially\n"
                f"Space Complexity: {space_complexity} - Only one file in memory at a time\n"
                f"I/O Complexity: {total_io} - Sequential read/write operations")

    # ---------------- Error Handling and Finalization ----------------
    def _handle_conversion_complete(self, data):
        """Handle conversion completion actions."""
        total_files, total_time = data
        self.total_time = total_time
        self.time_var.set(f"Time taken: {total_time:.2f} seconds")
        self.status_var.set(
            f"Conversion complete! Converted {total_files} files in {total_time:.2f} seconds"
        )
        self.update_performance_chart()
        self._reset_ui_state()

    def _reset_ui_state(self):
        """Reset the UI state after conversion."""
        self.conversion_active = False
        self.convert_btn.config(state="normal")
        self.switch_btn.config(state="normal")

    def _handle_conversion_error(self, error):
        """Handle errors that occur during the conversion process."""
        self.ui_queue.put(("error", f"Conversion error: {str(error)}"))
        self.ui_queue.put(("complete", (0, 0)))
        self._reset_ui_state()

if __name__ == "__main__":
    try:
        import pydub
        import matplotlib
    except ImportError as e:
        print(f"Missing required library: {e}")
        print("Please install required libraries with:")
        print("pip install pydub matplotlib")
        print("Note: pydub requires ffmpeg to be installed on your system")
        exit(1)
    
    root = tk.Tk()
    app = AudioConverterSequential(root)
    root.mainloop()
