#!/usr/bin/env python3
"""
Batch Processor for Runic Lands
Process multiple assets, projects, or perform bulk operations
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
from typing import List, Dict, Any
import json
import shutil
from PIL import Image
import subprocess

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class BatchProcessor:
    """Advanced batch processing tool with GUI"""
    
    def __init__(self, parent=None):
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("Runic Lands Batch Processor")
        self.window.geometry("900x700")
        self.window.minsize(700, 500)
        
        # Processing state
        self.processing_queue = []
        self.current_operation = None
        self.is_processing = False
        
        # Create GUI
        self.create_widgets()
        
        if not parent:
            self.window.mainloop()
    
    def create_widgets(self):
        """Create the GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Runic Lands Batch Processor", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Left panel - Operations
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.create_operations_panel(left_frame)
        
        # Right panel - Queue and Log
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_queue_panel(right_frame)
    
    def create_operations_panel(self, parent):
        """Create the operations panel"""
        # Asset Operations
        asset_frame = ttk.LabelFrame(parent, text="Asset Operations", padding="10")
        asset_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(asset_frame, text="Convert Image Formats", 
                  command=self.add_convert_images).pack(fill=tk.X, pady=2)
        ttk.Button(asset_frame, text="Resize Images", 
                  command=self.add_resize_images).pack(fill=tk.X, pady=2)
        ttk.Button(asset_frame, text="Optimize Images", 
                  command=self.add_optimize_images).pack(fill=tk.X, pady=2)
        ttk.Button(asset_frame, text="Generate Sprite Sheets", 
                  command=self.add_generate_sprite_sheets).pack(fill=tk.X, pady=2)
        
        # Project Operations
        project_frame = ttk.LabelFrame(parent, text="Project Operations", padding="10")
        project_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(project_frame, text="Process Multiple Projects", 
                  command=self.add_process_projects).pack(fill=tk.X, pady=2)
        ttk.Button(project_frame, text="Generate All Assets", 
                  command=self.add_generate_all_assets).pack(fill=tk.X, pady=2)
        ttk.Button(project_frame, text="Validate All Assets", 
                  command=self.add_validate_all_assets).pack(fill=tk.X, pady=2)
        ttk.Button(project_frame, text="Clean Project", 
                  command=self.add_clean_project).pack(fill=tk.X, pady=2)
        
        # File Operations
        file_frame = ttk.LabelFrame(parent, text="File Operations", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_frame, text="Rename Files", 
                  command=self.add_rename_files).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Organize Files", 
                  command=self.add_organize_files).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Backup Files", 
                  command=self.add_backup_files).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Delete Duplicates", 
                  command=self.add_delete_duplicates).pack(fill=tk.X, pady=2)
        
        # Custom Operations
        custom_frame = ttk.LabelFrame(parent, text="Custom Operations", padding="10")
        custom_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(custom_frame, text="Custom Script", 
                  command=self.add_custom_script).pack(fill=tk.X, pady=2)
        ttk.Button(custom_frame, text="Load Operation Set", 
                  command=self.load_operation_set).pack(fill=tk.X, pady=2)
        ttk.Button(custom_frame, text="Save Operation Set", 
                  command=self.save_operation_set).pack(fill=tk.X, pady=2)
        
        # Options
        options_frame = ttk.LabelFrame(parent, text="Options", padding="10")
        options_frame.pack(fill=tk.X)
        
        self.parallel_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Process in parallel", 
                       variable=self.parallel_var).pack(anchor=tk.W)
        
        self.stop_on_error_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Stop on first error", 
                       variable=self.stop_on_error_var).pack(anchor=tk.W)
        
        self.backup_before_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Backup before processing", 
                       variable=self.backup_before_var).pack(anchor=tk.W)
    
    def create_queue_panel(self, parent):
        """Create the queue and log panel"""
        # Queue
        queue_frame = ttk.LabelFrame(parent, text="Processing Queue", padding="10")
        queue_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Queue list
        queue_list_frame = ttk.Frame(queue_frame)
        queue_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.queue_listbox = tk.Listbox(queue_list_frame)
        queue_scrollbar = ttk.Scrollbar(queue_list_frame, orient="vertical", 
                                       command=self.queue_listbox.yview)
        self.queue_listbox.configure(yscrollcommand=queue_scrollbar.set)
        
        self.queue_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        queue_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Queue controls
        queue_controls = ttk.Frame(queue_frame)
        queue_controls.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(queue_controls, text="Remove Selected", 
                  command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(queue_controls, text="Clear Queue", 
                  command=self.clear_queue).pack(side=tk.LEFT, padx=5)
        ttk.Button(queue_controls, text="Move Up", 
                  command=self.move_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(queue_controls, text="Move Down", 
                  command=self.move_down).pack(side=tk.LEFT, padx=5)
        
        # Processing controls
        process_frame = ttk.LabelFrame(parent, text="Processing", padding="10")
        process_frame.pack(fill=tk.X, pady=(0, 10))
        
        process_controls = ttk.Frame(process_frame)
        process_controls.pack(fill=tk.X)
        
        self.start_button = ttk.Button(process_controls, text="Start Processing", 
                                     command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(process_controls, text="Stop", 
                                    command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(process_controls, text="Pause", 
                                     command=self.pause_processing, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(process_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
        # Log
        log_frame = ttk.LabelFrame(parent, text="Processing Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(log_controls, text="Clear Log", 
                  command=self.clear_log).pack(side=tk.LEFT)
        ttk.Button(log_controls, text="Save Log", 
                  command=self.save_log).pack(side=tk.LEFT, padx=(10, 0))
    
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
        # Color coding
        if level == "ERROR":
            self.log_text.tag_add("error", f"end-2l", "end-1l")
        elif level == "SUCCESS":
            self.log_text.tag_add("success", f"end-2l", "end-1l")
        elif level == "WARNING":
            self.log_text.tag_add("warning", f"end-2l", "end-1l")
        
        self.window.update_idletasks()
    
    def add_operation(self, operation: Dict[str, Any]):
        """Add operation to queue"""
        self.processing_queue.append(operation)
        self.update_queue_display()
        self.log_message(f"Added operation: {operation['name']}")
    
    def update_queue_display(self):
        """Update the queue display"""
        self.queue_listbox.delete(0, tk.END)
        for i, operation in enumerate(self.processing_queue):
            status = "✓" if operation.get('completed', False) else "○"
            self.queue_listbox.insert(tk.END, f"{status} {operation['name']}")
    
    def remove_selected(self):
        """Remove selected operation from queue"""
        selection = self.queue_listbox.curselection()
        if selection:
            index = selection[0]
            operation = self.processing_queue.pop(index)
            self.update_queue_display()
            self.log_message(f"Removed operation: {operation['name']}")
    
    def clear_queue(self):
        """Clear the processing queue"""
        self.processing_queue.clear()
        self.update_queue_display()
        self.log_message("Queue cleared")
    
    def move_up(self):
        """Move selected operation up in queue"""
        selection = self.queue_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            self.processing_queue[index], self.processing_queue[index-1] = \
                self.processing_queue[index-1], self.processing_queue[index]
            self.update_queue_display()
            self.queue_listbox.selection_set(index-1)
    
    def move_down(self):
        """Move selected operation down in queue"""
        selection = self.queue_listbox.curselection()
        if selection and selection[0] < len(self.processing_queue) - 1:
            index = selection[0]
            self.processing_queue[index], self.processing_queue[index+1] = \
                self.processing_queue[index+1], self.processing_queue[index]
            self.update_queue_display()
            self.queue_listbox.selection_set(index+1)
    
    def start_processing(self):
        """Start processing the queue"""
        if not self.processing_queue:
            messagebox.showwarning("Warning", "No operations in queue")
            return
        
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_queue, daemon=True)
        thread.start()
    
    def stop_processing(self):
        """Stop processing"""
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.log_message("Processing stopped")
    
    def pause_processing(self):
        """Pause/resume processing"""
        # This would implement pause functionality
        self.log_message("Pause functionality not yet implemented")
    
    def process_queue(self):
        """Process the queue"""
        total_operations = len(self.processing_queue)
        self.progress.config(maximum=total_operations)
        
        for i, operation in enumerate(self.processing_queue):
            if not self.is_processing:
                break
            
            self.current_operation = operation
            self.log_message(f"Processing: {operation['name']}")
            
            try:
                # Execute operation
                if operation['type'] == 'convert_images':
                    self.execute_convert_images(operation)
                elif operation['type'] == 'resize_images':
                    self.execute_resize_images(operation)
                elif operation['type'] == 'optimize_images':
                    self.execute_optimize_images(operation)
                elif operation['type'] == 'generate_sprite_sheets':
                    self.execute_generate_sprite_sheets(operation)
                elif operation['type'] == 'process_projects':
                    self.execute_process_projects(operation)
                elif operation['type'] == 'generate_all_assets':
                    self.execute_generate_all_assets(operation)
                elif operation['type'] == 'validate_all_assets':
                    self.execute_validate_all_assets(operation)
                elif operation['type'] == 'clean_project':
                    self.execute_clean_project(operation)
                elif operation['type'] == 'rename_files':
                    self.execute_rename_files(operation)
                elif operation['type'] == 'organize_files':
                    self.execute_organize_files(operation)
                elif operation['type'] == 'backup_files':
                    self.execute_backup_files(operation)
                elif operation['type'] == 'delete_duplicates':
                    self.execute_delete_duplicates(operation)
                elif operation['type'] == 'custom_script':
                    self.execute_custom_script(operation)
                
                operation['completed'] = True
                self.log_message(f"Completed: {operation['name']}", "SUCCESS")
                
            except Exception as e:
                self.log_message(f"Error in {operation['name']}: {e}", "ERROR")
                if self.stop_on_error_var.get():
                    break
            
            self.progress.config(value=i + 1)
            self.update_queue_display()
        
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.log_message("Processing completed", "SUCCESS")
    
    # Operation definitions
    def add_convert_images(self):
        """Add image conversion operation"""
        dialog = ImageConversionDialog(self.window, self)
    
    def add_resize_images(self):
        """Add image resize operation"""
        dialog = ImageResizeDialog(self.window, self)
    
    def add_optimize_images(self):
        """Add image optimization operation"""
        operation = {
            'type': 'optimize_images',
            'name': 'Optimize Images',
            'completed': False
        }
        self.add_operation(operation)
    
    def add_generate_sprite_sheets(self):
        """Add sprite sheet generation operation"""
        operation = {
            'type': 'generate_sprite_sheets',
            'name': 'Generate Sprite Sheets',
            'completed': False
        }
        self.add_operation(operation)
    
    def add_process_projects(self):
        """Add process projects operation"""
        dialog = ProjectSelectionDialog(self.window, self)
    
    def add_generate_all_assets(self):
        """Add generate all assets operation"""
        operation = {
            'type': 'generate_all_assets',
            'name': 'Generate All Assets',
            'completed': False
        }
        self.add_operation(operation)
    
    def add_validate_all_assets(self):
        """Add validate all assets operation"""
        operation = {
            'type': 'validate_all_assets',
            'name': 'Validate All Assets',
            'completed': False
        }
        self.add_operation(operation)
    
    def add_clean_project(self):
        """Add clean project operation"""
        operation = {
            'type': 'clean_project',
            'name': 'Clean Project',
            'completed': False
        }
        self.add_operation(operation)
    
    def add_rename_files(self):
        """Add rename files operation"""
        dialog = FileRenameDialog(self.window, self)
    
    def add_organize_files(self):
        """Add organize files operation"""
        operation = {
            'type': 'organize_files',
            'name': 'Organize Files',
            'completed': False
        }
        self.add_operation(operation)
    
    def add_backup_files(self):
        """Add backup files operation"""
        operation = {
            'type': 'backup_files',
            'name': 'Backup Files',
            'completed': False
        }
        self.add_operation(operation)
    
    def add_delete_duplicates(self):
        """Add delete duplicates operation"""
        operation = {
            'type': 'delete_duplicates',
            'name': 'Delete Duplicates',
            'completed': False
        }
        self.add_operation(operation)
    
    def add_custom_script(self):
        """Add custom script operation"""
        dialog = CustomScriptDialog(self.window, self)
    
    def load_operation_set(self):
        """Load operation set from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    operations = json.load(f)
                self.processing_queue = operations
                self.update_queue_display()
                self.log_message(f"Loaded operation set from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load operation set: {e}")
    
    def save_operation_set(self):
        """Save operation set to file"""
        if not self.processing_queue:
            messagebox.showwarning("Warning", "No operations to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.processing_queue, f, indent=2)
                self.log_message(f"Saved operation set to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save operation set: {e}")
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """Save log to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Log saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {e}")
    
    # Operation execution methods
    def execute_convert_images(self, operation):
        """Execute image conversion"""
        # Implementation for image conversion
        self.log_message("Converting images...")
    
    def execute_resize_images(self, operation):
        """Execute image resizing"""
        # Implementation for image resizing
        self.log_message("Resizing images...")
    
    def execute_optimize_images(self, operation):
        """Execute image optimization"""
        # Implementation for image optimization
        self.log_message("Optimizing images...")
    
    def execute_generate_sprite_sheets(self, operation):
        """Execute sprite sheet generation"""
        # Implementation for sprite sheet generation
        self.log_message("Generating sprite sheets...")
    
    def execute_process_projects(self, operation):
        """Execute project processing"""
        # Implementation for project processing
        self.log_message("Processing projects...")
    
    def execute_generate_all_assets(self, operation):
        """Execute generate all assets"""
        # Implementation for generating all assets
        self.log_message("Generating all assets...")
    
    def execute_validate_all_assets(self, operation):
        """Execute validate all assets"""
        # Implementation for validating all assets
        self.log_message("Validating all assets...")
    
    def execute_clean_project(self, operation):
        """Execute project cleaning"""
        # Implementation for project cleaning
        self.log_message("Cleaning project...")
    
    def execute_rename_files(self, operation):
        """Execute file renaming"""
        # Implementation for file renaming
        self.log_message("Renaming files...")
    
    def execute_organize_files(self, operation):
        """Execute file organization"""
        # Implementation for file organization
        self.log_message("Organizing files...")
    
    def execute_backup_files(self, operation):
        """Execute file backup"""
        # Implementation for file backup
        self.log_message("Backing up files...")
    
    def execute_delete_duplicates(self, operation):
        """Execute duplicate deletion"""
        # Implementation for duplicate deletion
        self.log_message("Deleting duplicates...")
    
    def execute_custom_script(self, operation):
        """Execute custom script"""
        # Implementation for custom script execution
        self.log_message("Executing custom script...")

# Dialog classes for operation configuration
class ImageConversionDialog:
    """Dialog for image conversion configuration"""
    
    def __init__(self, parent, processor):
        self.processor = processor
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Image Conversion")
        self.dialog.geometry("400x300")
        
        # Create dialog widgets
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Image Conversion Settings", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))
        
        # Source format
        ttk.Label(main_frame, text="Source Format:").pack(anchor=tk.W)
        self.source_format = ttk.Combobox(main_frame, values=["PNG", "JPG", "BMP", "GIF"])
        self.source_format.pack(fill=tk.X, pady=(0, 10))
        
        # Target format
        ttk.Label(main_frame, text="Target Format:").pack(anchor=tk.W)
        self.target_format = ttk.Combobox(main_frame, values=["PNG", "JPG", "BMP", "GIF"])
        self.target_format.pack(fill=tk.X, pady=(0, 10))
        
        # Quality (for lossy formats)
        ttk.Label(main_frame, text="Quality (1-100):").pack(anchor=tk.W)
        self.quality = ttk.Scale(main_frame, from_=1, to=100, orient=tk.HORIZONTAL)
        self.quality.set(90)
        self.quality.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Add to Queue", 
                  command=self.add_to_queue).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def add_to_queue(self):
        """Add operation to queue"""
        operation = {
            'type': 'convert_images',
            'name': f"Convert {self.source_format.get()} to {self.target_format.get()}",
            'source_format': self.source_format.get(),
            'target_format': self.target_format.get(),
            'quality': int(self.quality.get()),
            'completed': False
        }
        self.processor.add_operation(operation)
        self.dialog.destroy()

class ImageResizeDialog:
    """Dialog for image resize configuration"""
    
    def __init__(self, parent, processor):
        self.processor = processor
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Image Resize")
        self.dialog.geometry("400x300")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Image Resize Settings", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))
        
        # Width
        ttk.Label(main_frame, text="Width:").pack(anchor=tk.W)
        self.width = ttk.Entry(main_frame)
        self.width.pack(fill=tk.X, pady=(0, 10))
        
        # Height
        ttk.Label(main_frame, text="Height:").pack(anchor=tk.W)
        self.height = ttk.Entry(main_frame)
        self.height.pack(fill=tk.X, pady=(0, 10))
        
        # Maintain aspect ratio
        self.maintain_aspect = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Maintain aspect ratio", 
                       variable=self.maintain_aspect).pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Add to Queue", 
                  command=self.add_to_queue).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def add_to_queue(self):
        """Add operation to queue"""
        operation = {
            'type': 'resize_images',
            'name': f"Resize to {self.width.get()}x{self.height.get()}",
            'width': int(self.width.get()) if self.width.get() else 0,
            'height': int(self.height.get()) if self.height.get() else 0,
            'maintain_aspect': self.maintain_aspect.get(),
            'completed': False
        }
        self.processor.add_operation(operation)
        self.dialog.destroy()

class ProjectSelectionDialog:
    """Dialog for project selection"""
    
    def __init__(self, parent, processor):
        self.processor = processor
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Project Selection")
        self.dialog.geometry("500x400")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Select Projects", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))
        
        # Project list
        self.project_listbox = tk.Listbox(main_frame, selectmode=tk.MULTIPLE)
        self.project_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Add to Queue", 
                  command=self.add_to_queue).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def add_to_queue(self):
        """Add operation to queue"""
        # Implementation for project selection
        self.dialog.destroy()

class FileRenameDialog:
    """Dialog for file renaming configuration"""
    
    def __init__(self, parent, processor):
        self.processor = processor
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("File Rename")
        self.dialog.geometry("400x300")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="File Rename Settings", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))
        
        # Pattern
        ttk.Label(main_frame, text="Rename Pattern:").pack(anchor=tk.W)
        self.pattern = ttk.Entry(main_frame)
        self.pattern.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Add to Queue", 
                  command=self.add_to_queue).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def add_to_queue(self):
        """Add operation to queue"""
        operation = {
            'type': 'rename_files',
            'name': f"Rename files with pattern: {self.pattern.get()}",
            'pattern': self.pattern.get(),
            'completed': False
        }
        self.processor.add_operation(operation)
        self.dialog.destroy()

class CustomScriptDialog:
    """Dialog for custom script configuration"""
    
    def __init__(self, parent, processor):
        self.processor = processor
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Custom Script")
        self.dialog.geometry("500x400")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Custom Script Settings", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))
        
        # Script path
        ttk.Label(main_frame, text="Script Path:").pack(anchor=tk.W)
        script_frame = ttk.Frame(main_frame)
        script_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.script_path = ttk.Entry(script_frame)
        self.script_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(script_frame, text="Browse", 
                  command=self.browse_script).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Arguments
        ttk.Label(main_frame, text="Arguments:").pack(anchor=tk.W)
        self.arguments = ttk.Entry(main_frame)
        self.arguments.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Add to Queue", 
                  command=self.add_to_queue).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def browse_script(self):
        """Browse for script file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("Batch files", "*.bat"), ("All files", "*.*")]
        )
        if filename:
            self.script_path.delete(0, tk.END)
            self.script_path.insert(0, filename)
    
    def add_to_queue(self):
        """Add operation to queue"""
        operation = {
            'type': 'custom_script',
            'name': f"Custom Script: {Path(self.script_path.get()).name}",
            'script_path': self.script_path.get(),
            'arguments': self.arguments.get(),
            'completed': False
        }
        self.processor.add_operation(operation)
        self.dialog.destroy()

def main():
    """Main entry point"""
    app = BatchProcessor()

if __name__ == "__main__":
    main()
