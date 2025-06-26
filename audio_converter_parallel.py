"""
Parallel Audio Converter Implementation
"""
import os
import time
import threading
import multiprocessing
from queue import Queue, Empty
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from concurrent.futures import ProcessPoolExecutor
from pydub import AudioSegment
from audio_converter_base import BaseAudioConverterApp

def convert_file_process(args):
    """Standalone function for process-based conversion."""
    try:
        file_path, output_dir, output_format = args
        base_name = os.path.basename(file_path)
        file_name, _ = os.path.splitext(base_name)
        output_path = os.path.join(output_dir, f"{file_name}{output_format}")
        
        # Load and convert the audio file
        audio = AudioSegment.from_file(file_path)
        audio.export(output_path, format=output_format[1:])
        
        return base_name, time.time()
    except Exception as e:
        return base_name, str(e)

class AudioConverterParallel(BaseAudioConverterApp):
    def __init__(self, root):
        super().__init__(root, "Audio Format Converter - Parallel Version", mode='parallel')
        self._active_processes = set()
        self._process_tasks = defaultdict(int)
        self.ui_queue = Queue()
        self.conversion_active = False
        self.is_converting = False
        self.setup_process_selection()
        self.complexity_var = tk.StringVar(value="Complexity: Not calculated yet")
        self.setup_complexity_display()
        self._start_ui_update_loop()
        self.root = root
        self._ui_update_lock = threading.Lock()
        self.conversion_times = []

    def setup_process_selection(self):
        """Setup the process count selection dropdown."""
        self.process_frame = ttk.LabelFrame(self.scrollable_frame, text="Process Configuration", padding=(16, 10))
        self.process_frame.pack(fill="x", padx=24, pady=(0, 16))

        ttk.Label(self.process_frame, text="Number of processes:").pack(side="left", padx=(5, 10))
        
        # Get CPU count for max processes
        max_processes = os.cpu_count() or 4
        process_options = [2, 4, 6, 8, max_processes]
        process_options = sorted(list(set([p for p in process_options if p <= max_processes])))
        
        self.process_count = ttk.Combobox(self.process_frame, values=process_options, width=5, state="readonly")
        self.process_count.set(4)  # Default to 4 processes
        self.process_count.pack(side="left", padx=5)
        
        ttk.Label(self.process_frame, 
                 text=f"(Available options: {', '.join(map(str, process_options))} processes)", 
                 font=("Segoe UI", 9, "italic")).pack(side="left", padx=5)

    def setup_complexity_display(self):
        """Setup the complexity metrics display."""
        complexity_frame = ttk.LabelFrame(self.scrollable_frame, text="Algorithm Analysis", padding=(16, 10))
        complexity_frame.pack(fill=tk.X, pady=(0, 16), before=self.chart_frame)
        
        complexity_label = ttk.Label(complexity_frame, textvariable=self.complexity_var,
                                   font=("Segoe UI", 11), wraplength=800)
        complexity_label.pack(pady=5)

    def _start_ui_update_loop(self):
        """Start the UI update loop to handle updates from worker threads."""
        try:
            while not self.ui_queue.empty():
                try:
                    action, data = self.ui_queue.get_nowait()
                    self._handle_ui_action(action, data)
                except Empty:
                    break

            # Schedule next update if conversion is active
            if self.conversion_active:
                self.root.after(100, self._start_ui_update_loop)
        except Exception as e:
            print(f"Error in UI update loop: {str(e)}")
            self._reset_ui_state()

    def _handle_ui_action(self, action, data):
        """Handle UI actions based on updates from worker threads."""
        try:
            if action == "progress":
                self.root.after(0, lambda d=data: self.progress_bar.configure(value=d))
            elif action == "status":
                self.root.after(0, lambda d=data: self.status_var.set(d))
            elif action == "error":
                self.root.after(0, lambda d=data: messagebox.showerror("Conversion Error", d))
            elif action == "complete":
                self.root.after(0, lambda d=data: self.handle_conversion_complete(d))
            elif action == "enable_buttons":
                self.root.after(0, self.enable_buttons)
            # Remove UI display of task distribution
            # elif action == "show_distribution":
            #     self.root.after(0, lambda d=data: self.show_distribution_dialog(d))
        except Exception as e:
            print(f"Error in UI action handler: {e}")

    def handle_conversion_complete(self, data):
        """Handle completion of conversion process."""
        total_files, total_time = data
        self.total_time = total_time
        self.time_var.set(f"Time taken: {total_time:.2f} seconds")
        self.status_var.set(
            f"Conversion complete! Converted {total_files} files in {total_time:.2f} seconds "
            f"using {self.max_workers} processes"
        )
        self.update_performance_chart()
        self.enable_buttons()

    def enable_buttons(self):
        """Enable UI buttons and reset conversion state."""
        self.conversion_active = False
        self.is_converting = False
        self.convert_btn.config(state="normal")
        self.switch_btn.config(state="normal")
        self.process_count.config(state="readonly")

    def show_distribution_dialog(self, msg):
        """Show task distribution in a dialog."""
        messagebox.showinfo("Task Distribution", msg)

    def _enable_buttons(self):
        """Enable UI buttons on the main thread."""
        self.conversion_active = False
        self.is_converting = False
        self.convert_btn.config(state="normal")
        self.switch_btn.config(state="normal")
        self.process_count.config(state="readonly")

    def _show_distribution_dialog(self, msg):
        """Show distribution dialog on main thread."""
        messagebox.showinfo("Task Distribution", msg)

    def _reset_ui_state(self):
        """Reset the UI state and clean up processes."""
        try:
            # Terminate any remaining processes
            for process in self._active_processes:
                if process.is_alive():
                    process.terminate()
            self._active_processes.clear()
        except:
            pass
        
        # Schedule UI updates on main thread
        self.ui_queue.put(("enable_buttons", None))

    def start_conversion(self):
        """Start the parallel conversion process."""
        if not self.files:
            messagebox.showwarning("No Files", "No files selected!")
            return

        try:
            if not self._setup_conversion():
                return
            
            self._initialize_conversion()
            threading.Thread(target=self.convert_files, daemon=True).start()
            self._start_ui_update_loop()
            
        except Exception as e:
            self._handle_conversion_error(e)

    def _setup_conversion(self):
        """Prepare for conversion by calculating metrics and getting user input."""
        total_size = sum(os.path.getsize(f) for f in self.files)
        avg_size_mb = (total_size / len(self.files)) / (1024 * 1024)
        n_files = len(self.files)
        processes = int(self.process_count.get())
        
        self.complexity_var.set(self.calculate_complexity_metrics(n_files, avg_size_mb, processes))
        self.selected_format = self.formats[self.output_format.get()]
        self.output_directory = filedialog.askdirectory(title="Select Output Directory")
        
        return bool(self.output_directory)

    def _initialize_conversion(self):
        """Initialize conversion parameters and UI elements."""
        self.conversion_active = True
        self.is_converting = True
        self.max_workers = int(self.process_count.get())
        self.convert_btn.config(state="disabled")
        self.switch_btn.config(state="disabled")
        self.process_count.config(state="disabled")  # Fix typo in 'state'
        self.progress_bar["maximum"] = len(self.files)
        self.progress_bar["value"] = 0

    def calculate_complexity_metrics(self, n_files, avg_file_size_mb, n_processes):
        """Calculate and format complexity metrics for display."""
        time_complexity = f"O({n_files}/{n_processes} * {avg_file_size_mb:.1f}MB)"
        space_complexity = f"O({n_processes} * {avg_file_size_mb:.1f}MB)"
        total_io = f"O({n_files} * {avg_file_size_mb:.1f}MB)"
        
        return (f"Time Complexity: {time_complexity} - Processing {n_files} files using {n_processes} processes\n"
                f"Space Complexity: {space_complexity} - Up to {n_processes} files in memory simultaneously\n"
                f"I/O Complexity: {total_io} - Parallel read/write operations")

    def convert_files(self):
        """Convert files in parallel with process task tracking."""
        try:
            total_files = len(self.files)
            total_start_time = time.time()
            self.conversion_times = []
            completed = 0
            errors = []
            
            self._process_tasks.clear()
            self.ui_queue.put(("status", f"Starting parallel conversion using {self.max_workers} processes..."))
            
            # Use spawn context for Windows compatibility
            ctx = multiprocessing.get_context('spawn')
            
            with ProcessPoolExecutor(max_workers=self.max_workers, mp_context=ctx) as executor:
                conversion_args = [(f, self.output_directory, self.selected_format) for f in self.files]
                futures = []
                for i, args in enumerate(conversion_args):
                    future = executor.submit(convert_file_process, args)
                    futures.append((future, args[0]))
                    self._process_tasks[i % self.max_workers] += 1
                
                for idx, (future, filename) in enumerate(futures):
                    try:
                        name, result = future.result()
                        if isinstance(result, str):  # Error case
                            errors.append((name, result))
                        else:  # Success case
                            duration = result - total_start_time
                            self.conversion_times.append((name, duration))
                            completed += 1
                            self.ui_queue.put(("progress", completed))
                            self.ui_queue.put(("status", f"Converted {completed}/{total_files} files"))
                    except Exception as exc:
                        errors.append((filename, str(exc)))
            
            total_end_time = time.time()
            total_time = total_end_time - total_start_time
            
            if errors:
                err_msg = "\n".join([f"{name}: {err}" for name, err in errors])
                self.ui_queue.put(("error", f"Errors occurred during conversion:\n{err_msg}"))
            
            self.ui_queue.put(("complete", (total_files, total_time)))
        
        except Exception as e:
            self._handle_conversion_error(e)
            self._reset_ui_state()

    def _handle_conversion_error(self, e):
        """Handle exceptions during conversion."""
        self.ui_queue.put(("error", str(e)))
        self._reset_ui_state()

def main():
    root = tk.Tk()
    app = AudioConverterParallel(root)
    root.mainloop()

if __name__ == "__main__":
    main()
