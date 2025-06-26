"""
Base Audio Converter GUI Application
Provides the common GUI elements and functionality for both sequential and parallel converters.
"""
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BaseAudioConverterApp:
    """Base class for audio converter application with GUI components."""
    
    def __init__(self, root, title, mode='sequential'):
        """Initialize base audio converter application."""
        self.root = root
        self.mode = mode
        self.root.title(title)
        self.root.geometry("950x750")
        self.root.minsize(900, 700)
        
        # Setup application
        self.setup_style()
        self.create_scrollable_container()
        
        # Supported audio formats
        self.formats = {
            "MP3": ".mp3",
            "WAV": ".wav",
            "FLAC": ".flac",
            "OGG": ".ogg",
            "AAC": ".aac"
        }
        
        # State variables
        self.files = []  # List of files to convert
        self.conversion_times = []  # Individual file conversion times
        self.total_time = 0  # Total conversion time
        
        self.setup_ui()

    def setup_style(self):
        """Configure the style of the application."""
        try:
            style = ttk.Style()
            if "clam" in style.theme_names():
                style.theme_use("clam")
            style.configure("TButton", font=("Segoe UI", 11), padding=6)
            style.configure("TLabel", font=("Segoe UI", 11))
            style.configure("TFrame")
            style.configure("TLabelframe", font=("Segoe UI", 11, "bold"))
            style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        except Exception:
            pass

    def create_scrollable_container(self):
        """Create a scrollable container for the main content."""
        self.outer_frame = ttk.Frame(self.root, padding=0)
        self.outer_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.outer_frame, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self.outer_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", self._resize_frame)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def _resize_frame(self, event):
        """Resize the frame when the window is resized."""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def setup_ui(self):
        """Setup the user interface components."""
        main_frame = ttk.Frame(self.scrollable_frame, padding=24)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_title(main_frame)
        self.setup_file_selection(main_frame)
        self.setup_files_display(main_frame)
        self.setup_format_selection(main_frame)
        self.setup_conversion_controls(main_frame)
        self.setup_progress_display(main_frame)
        self.setup_performance_metrics(main_frame)
        self.setup_chart_frame(main_frame)

    def setup_title(self, parent):
        """Setup the title label."""
        self.title_label = ttk.Label(parent, text=self.root.title(), 
                                   font=("Segoe UI", 22, "bold"), anchor="center")
        self.title_label.pack(pady=(10, 18), fill=tk.X)

    def setup_file_selection(self, parent):
        """Setup the file selection controls."""
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding=(16, 10))
        file_frame.pack(fill=tk.X, pady=(0, 16))
        
        select_btn = ttk.Button(file_frame, text="Select Audio Files", command=self.select_files)
        clear_btn = ttk.Button(file_frame, text="Clear Selection", command=self.clear_selection)
        show_chart_btn = ttk.Button(file_frame, text="Show Chart", command=self.scroll_to_chart)
        
        select_btn.pack(side=tk.LEFT, padx=(0, 8), pady=2)
        clear_btn.pack(side=tk.LEFT, padx=(0, 8), pady=2)
        show_chart_btn.pack(side=tk.RIGHT, padx=(8, 0), pady=2)

    def setup_files_display(self, parent):
        """Setup the display for selected files."""
        files_frame = ttk.LabelFrame(parent, text="Selected Files", padding=(16, 10))
        files_frame.pack(fill=tk.X, pady=(0, 16))
        files_frame.configure(height=120)
        
        scrollbar = ttk.Scrollbar(files_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox = tk.Listbox(files_frame, yscrollcommand=scrollbar.set, 
                                      font=("Consolas", 10), height=6, 
                                      borderwidth=0, highlightthickness=0)
        self.files_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        scrollbar.config(command=self.files_listbox.yview)

    def setup_format_selection(self, parent):
        """Setup the output format selection controls."""
        self.format_frame = ttk.LabelFrame(parent, text="Output Format", padding=(16, 10))
        self.format_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.output_format = tk.StringVar(value="MP3")
        for format_name in self.formats.keys():
            format_radio = ttk.Radiobutton(self.format_frame, text=format_name, 
                                        value=format_name, 
                                        variable=self.output_format)
            format_radio.pack(side=tk.LEFT, padx=12, pady=2)

    def setup_conversion_controls(self, parent):
        """Setup the conversion control buttons."""
        convert_frame = ttk.Frame(parent)
        convert_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.convert_btn = ttk.Button(convert_frame, text="Convert Files", 
                                    command=self.start_conversion)
        self.convert_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        mode_text = "Switch to Parallel" if self.mode == 'sequential' else "Switch to Sequential"
        self.switch_btn = ttk.Button(convert_frame, text=mode_text,
                                   command=self.switch_mode)
        self.switch_btn.pack(side=tk.RIGHT, padx=2, pady=2)

    def setup_progress_display(self, parent):
        """Setup the progress display components."""
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding=(16, 10))
        progress_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", 
                                          length=100, mode="determinate")
        self.progress_bar.pack(fill=tk.X, padx=2, pady=(0, 4))
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var, 
                               font=("Segoe UI", 10, "italic"), foreground="#444")
        status_label.pack(pady=2)

    def setup_performance_metrics(self, parent):
        """Setup the performance metrics display."""
        metrics_frame = ttk.LabelFrame(parent, text="Performance Metrics", padding=(16, 10))
        metrics_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.time_var = tk.StringVar(value="Time taken: 0.00 seconds")
        time_label = ttk.Label(metrics_frame, textvariable=self.time_var, 
                             font=("Segoe UI", 11, "bold"), foreground="#333")
        time_label.pack(pady=2)

    def setup_chart_frame(self, parent):
        """Setup the frame for displaying the performance chart."""
        self.chart_frame = ttk.LabelFrame(parent, text="Performance Chart", padding=(16, 10))
        self.chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chart_frame.configure(height=320)
        
        placeholder = ttk.Label(self.chart_frame, 
                              text="Chart will appear here after conversion", 
                              font=("Segoe UI", 12, "italic"), 
                              foreground="#888")
        placeholder.pack(pady=60)

    def select_files(self):
        """Open a file dialog to select audio files for conversion."""
        file_paths = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.aac *.ogg")]
        )
        
        if file_paths:
            self.files.extend(list(file_paths))
            self.update_files_listbox()
    
    def update_files_listbox(self):
        """Update the files listbox display."""
        self.files_listbox.delete(0, tk.END)
        for file in self.files:
            self.files_listbox.insert(tk.END, os.path.basename(file))
    
    def clear_selection(self):
        """Clear the current file selection."""
        self.files = []
        self.files_listbox.delete(0, tk.END)
    
    def scroll_to_chart(self):
        """Scroll the view to bring the chart into view."""
        self.root.update_idletasks()
        chart_y = self.chart_frame.winfo_y()
        self.canvas.yview_moveto(chart_y / self.scrollable_frame.winfo_height())

    def switch_mode(self):
        """Switch between sequential and parallel conversion modes."""
        if hasattr(self, 'on_mode_switch'):
            self.on_mode_switch()

    def start_conversion(self):
        """Start the file conversion process."""
        raise NotImplementedError("Subclasses must implement start_conversion")

    def update_performance_chart(self):
        """Update the performance chart display."""
        try:
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            if not self.conversion_times:
                message_label = ttk.Label(self.chart_frame, 
                                        text="No conversion data available to display.", 
                                        font=("Arial", 12))
                message_label.pack(pady=20)
                self.status_var.set("Warning: No performance data to display")
                return
            
            self.chart_frame.update()
            min_height = 400
            if self.chart_frame.winfo_height() < min_height:
                self.chart_frame.configure(height=min_height)
            
            num_files = len(self.conversion_times)
            width = min(12, max(10, num_files * 0.5))
            height = min(8, max(5, num_files * 0.2))
            
            fig = plt.figure(figsize=(width, height), dpi=100)
            ax = fig.add_subplot(111)
            
            sorted_times = sorted(self.conversion_times, key=lambda x: x[1], reverse=True)
            file_names = [item[0] for item in sorted_times]
            times = [item[1] for item in sorted_times]
            
            display_names = []
            max_len = 20 if num_files <= 10 else (15 if num_files <= 20 else 10)
            
            for name in file_names:
                if len(name) > max_len:
                    name = name[:max_len-3] + "..."
                display_names.append(name)
            
            bars = ax.bar(range(len(display_names)), times)
            
            if num_files <= 15:
                for i, (rect, time_value) in enumerate(zip(bars, times)):
                    height = rect.get_height()
                    ax.text(rect.get_x() + rect.get_width()/2., height + 0.02,
                           f'{time_value:.2f}s',
                           ha='center', va='bottom', fontsize=8)
            
            step = 1
            if num_files > 15:
                step = 2
            if num_files > 30:
                step = 3
                
            xticks = range(0, len(display_names), step)
            xtick_labels = [display_names[i] for i in xticks]
            ax.set_xticks(xticks)
            ax.set_xticklabels(xtick_labels, rotation=45, ha='right')
            
            ax.set_ylabel('Time (seconds)', fontsize=12)
            ax.set_title(f'File Conversion Times - {len(file_names)} files', fontsize=14)
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)
            
            plt.subplots_adjust(bottom=0.65)
            
            ax.text(0.5, -0.55,
                   f'Total time: {self.total_time:.2f}s',
                   ha='center', va='top', fontsize=12,
                   bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3),
                   transform=ax.transAxes)
            
            plt.tight_layout(pad=3.0, rect=[0, 0.2, 1, 0.95])
            
            chart_container = ttk.Frame(self.chart_frame)
            chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            canvas = FigureCanvasTkAgg(fig, master=chart_container)
            canvas.draw()
            
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            print(f"Performance chart updated with {len(self.conversion_times)} files")
            print(f"Chart frame dimensions: {self.chart_frame.winfo_width()}x{self.chart_frame.winfo_height()}")
            
            self.root.after(100, self.scroll_to_chart)
            
        except Exception as e:
            error_msg = f"Error creating performance chart: {str(e)}"
            print(error_msg)
            self.status_var.set(error_msg)
            
            error_label = ttk.Label(self.chart_frame, 
                                  text=f"Could not display chart. Error: {str(e)}", 
                                  foreground="red")
            error_label.pack(pady=10)

# No Amdahl's Law code present in this file.


