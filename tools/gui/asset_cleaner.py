#!/usr/bin/env python3
"""
Asset Cleaner for Runic Lands
Clean up unused, duplicate, or temporary assets
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from pathlib import Path
from typing import List, Dict, Set, Tuple
import hashlib
import shutil
import json
from PIL import Image
import mimetypes

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class AssetCleaner:
    """Advanced asset cleaning tool with GUI"""
    
    def __init__(self, parent=None):
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("Runic Lands Asset Cleaner")
        self.window.geometry("1000x700")
        self.window.minsize(800, 600)
        
        # Cleaning state
        self.scan_results = {}
        self.duplicates = []
        self.unused_files = []
        self.temp_files = []
        self.large_files = []
        self.is_scanning = False
        
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
        title_label = ttk.Label(main_frame, text="Runic Lands Asset Cleaner", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Left panel - Controls
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.create_control_panel(left_frame)
        
        # Right panel - Results
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_results_panel(right_frame)
    
    def create_control_panel(self, parent):
        """Create the control panel"""
        # Scan Options
        scan_frame = ttk.LabelFrame(parent, text="Scan Options", padding="10")
        scan_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.scan_duplicates = tk.BooleanVar(value=True)
        ttk.Checkbutton(scan_frame, text="Find Duplicates", 
                       variable=self.scan_duplicates).pack(anchor=tk.W)
        
        self.scan_unused = tk.BooleanVar(value=True)
        ttk.Checkbutton(scan_frame, text="Find Unused Files", 
                       variable=self.scan_unused).pack(anchor=tk.W)
        
        self.scan_temp = tk.BooleanVar(value=True)
        ttk.Checkbutton(scan_frame, text="Find Temporary Files", 
                       variable=self.scan_temp).pack(anchor=tk.W)
        
        self.scan_large = tk.BooleanVar(value=True)
        ttk.Checkbutton(scan_frame, text="Find Large Files", 
                       variable=self.scan_large).pack(anchor=tk.W)
        
        # File Size Threshold
        ttk.Label(scan_frame, text="Large File Threshold (MB):").pack(anchor=tk.W, pady=(10, 0))
        self.size_threshold = ttk.Scale(scan_frame, from_=1, to=100, orient=tk.HORIZONTAL)
        self.size_threshold.set(10)
        self.size_threshold.pack(fill=tk.X, pady=(0, 10))
        
        # Scan Button
        ttk.Button(scan_frame, text="Scan Assets", 
                  command=self.start_scan).pack(fill=tk.X, pady=(10, 0))
        
        # Cleanup Options
        cleanup_frame = ttk.LabelFrame(parent, text="Cleanup Options", padding="10")
        cleanup_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.clean_duplicates = tk.BooleanVar()
        ttk.Checkbutton(cleanup_frame, text="Remove Duplicates", 
                       variable=self.clean_duplicates).pack(anchor=tk.W)
        
        self.clean_unused = tk.BooleanVar()
        ttk.Checkbutton(cleanup_frame, text="Remove Unused Files", 
                       variable=self.clean_unused).pack(anchor=tk.W)
        
        self.clean_temp = tk.BooleanVar()
        ttk.Checkbutton(cleanup_frame, text="Remove Temporary Files", 
                       variable=self.clean_temp).pack(anchor=tk.W)
        
        self.clean_large = tk.BooleanVar()
        ttk.Checkbutton(cleanup_frame, text="Remove Large Files", 
                       variable=self.clean_large).pack(anchor=tk.W)
        
        # Safety Options
        safety_frame = ttk.LabelFrame(parent, text="Safety Options", padding="10")
        safety_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_backup = tk.BooleanVar(value=True)
        ttk.Checkbutton(safety_frame, text="Create Backup Before Cleaning", 
                       variable=self.create_backup).pack(anchor=tk.W)
        
        self.confirm_deletions = tk.BooleanVar(value=True)
        ttk.Checkbutton(safety_frame, text="Confirm Each Deletion", 
                       variable=self.confirm_deletions).pack(anchor=tk.W)
        
        # Cleanup Button
        ttk.Button(cleanup_frame, text="Start Cleanup", 
                  command=self.start_cleanup).pack(fill=tk.X, pady=(10, 0))
        
        # Statistics
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X)
        
        self.stats_text = tk.Text(stats_frame, height=6, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
    
    def create_results_panel(self, parent):
        """Create the results panel"""
        # Results tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Duplicates tab
        self.duplicates_frame = ttk.Frame(notebook)
        notebook.add(self.duplicates_frame, text="Duplicates")
        
        self.duplicates_listbox = tk.Listbox(self.duplicates_frame, selectmode=tk.MULTIPLE)
        duplicates_scrollbar = ttk.Scrollbar(self.duplicates_frame, orient="vertical", 
                                           command=self.duplicates_listbox.yview)
        self.duplicates_listbox.configure(yscrollcommand=duplicates_scrollbar.set)
        
        self.duplicates_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        duplicates_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Unused files tab
        self.unused_frame = ttk.Frame(notebook)
        notebook.add(self.unused_frame, text="Unused Files")
        
        self.unused_listbox = tk.Listbox(self.unused_frame, selectmode=tk.MULTIPLE)
        unused_scrollbar = ttk.Scrollbar(self.unused_frame, orient="vertical", 
                                        command=self.unused_listbox.yview)
        self.unused_listbox.configure(yscrollcommand=unused_scrollbar.set)
        
        self.unused_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        unused_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Temporary files tab
        self.temp_frame = ttk.Frame(notebook)
        notebook.add(self.temp_frame, text="Temporary Files")
        
        self.temp_listbox = tk.Listbox(self.temp_frame, selectmode=tk.MULTIPLE)
        temp_scrollbar = ttk.Scrollbar(self.temp_frame, orient="vertical", 
                                      command=self.temp_listbox.yview)
        self.temp_listbox.configure(yscrollcommand=temp_scrollbar.set)
        
        self.temp_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        temp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Large files tab
        self.large_frame = ttk.Frame(notebook)
        notebook.add(self.large_frame, text="Large Files")
        
        self.large_listbox = tk.Listbox(self.large_frame, selectmode=tk.MULTIPLE)
        large_scrollbar = ttk.Scrollbar(self.large_frame, orient="vertical", 
                                       command=self.large_listbox.yview)
        self.large_listbox.configure(yscrollcommand=large_scrollbar.set)
        
        self.large_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        large_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="Select All", 
                  command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Deselect All", 
                  command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Selected", 
                  command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Export List", 
                  command=self.export_list).pack(side=tk.LEFT, padx=5)
    
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # Update statistics
        self.stats_text.insert(tk.END, formatted_message)
        self.stats_text.see(tk.END)
        
        self.window.update_idletasks()
    
    def start_scan(self):
        """Start asset scanning"""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.log_message("Starting asset scan...")
        
        # Clear previous results
        self.duplicates_listbox.delete(0, tk.END)
        self.unused_listbox.delete(0, tk.END)
        self.temp_listbox.delete(0, tk.END)
        self.large_listbox.delete(0, tk.END)
        
        # Start scanning in background thread
        thread = threading.Thread(target=self.scan_assets, daemon=True)
        thread.start()
    
    def scan_assets(self):
        """Scan assets for cleanup opportunities"""
        try:
            assets_dir = Path("../../assets")
            if not assets_dir.exists():
                self.log_message("Assets directory not found", "ERROR")
                return
            
            # Scan for duplicates
            if self.scan_duplicates.get():
                self.log_message("Scanning for duplicates...")
                self.scan_duplicate_files(assets_dir)
            
            # Scan for unused files
            if self.scan_unused.get():
                self.log_message("Scanning for unused files...")
                self.scan_unused_files(assets_dir)
            
            # Scan for temporary files
            if self.scan_temp.get():
                self.log_message("Scanning for temporary files...")
                self.scan_temp_files(assets_dir)
            
            # Scan for large files
            if self.scan_large.get():
                self.log_message("Scanning for large files...")
                self.scan_large_files(assets_dir)
            
            self.log_message("Asset scan completed", "SUCCESS")
            self.update_statistics()
            
        except Exception as e:
            self.log_message(f"Error during scan: {e}", "ERROR")
        finally:
            self.is_scanning = False
    
    def scan_duplicate_files(self, directory: Path):
        """Scan for duplicate files"""
        file_hashes = {}
        duplicates = []
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    # Calculate file hash
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash in file_hashes:
                        duplicates.append((file_path, file_hashes[file_hash]))
                    else:
                        file_hashes[file_hash] = file_path
                        
                except Exception as e:
                    self.log_message(f"Error processing {file_path}: {e}", "WARNING")
        
        # Add duplicates to list
        for duplicate, original in duplicates:
            size = duplicate.stat().st_size
            self.duplicates_listbox.insert(tk.END, f"{duplicate.name} ({size} bytes) - Duplicate of {original.name}")
        
        self.duplicates = duplicates
        self.log_message(f"Found {len(duplicates)} duplicate files")
    
    def scan_unused_files(self, directory: Path):
        """Scan for unused files"""
        # This is a simplified version - in practice, you'd need to analyze
        # the game code to determine which files are actually referenced
        unused_files = []
        
        # Common patterns for unused files
        unused_patterns = [
            "*.tmp", "*.temp", "*.bak", "*.backup", "*.old",
            "*_copy.*", "*_duplicate.*", "*_old.*"
        ]
        
        for pattern in unused_patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    self.unused_listbox.insert(tk.END, f"{file_path.name} ({size} bytes)")
                    unused_files.append(file_path)
        
        self.unused_files = unused_files
        self.log_message(f"Found {len(unused_files)} potentially unused files")
    
    def scan_temp_files(self, directory: Path):
        """Scan for temporary files"""
        temp_files = []
        temp_extensions = ['.tmp', '.temp', '.log', '.cache', '.bak']
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in temp_extensions:
                size = file_path.stat().st_size
                self.temp_listbox.insert(tk.END, f"{file_path.name} ({size} bytes)")
                temp_files.append(file_path)
        
        self.temp_files = temp_files
        self.log_message(f"Found {len(temp_files)} temporary files")
    
    def scan_large_files(self, directory: Path):
        """Scan for large files"""
        large_files = []
        threshold = self.size_threshold.get() * 1024 * 1024  # Convert MB to bytes
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                if size > threshold:
                    size_mb = size / (1024 * 1024)
                    self.large_listbox.insert(tk.END, f"{file_path.name} ({size_mb:.1f} MB)")
                    large_files.append(file_path)
        
        self.large_files = large_files
        self.log_message(f"Found {len(large_files)} large files")
    
    def update_statistics(self):
        """Update statistics display"""
        total_duplicates = len(self.duplicates)
        total_unused = len(self.unused_files)
        total_temp = len(self.temp_files)
        total_large = len(self.large_files)
        
        total_size = 0
        for file_list in [self.duplicates, self.unused_files, self.temp_files, self.large_files]:
            for file_path in file_list:
                if isinstance(file_path, tuple):
                    file_path = file_path[0]  # For duplicates
                total_size += file_path.stat().st_size
        
        size_mb = total_size / (1024 * 1024)
        
        stats = f"""SCAN RESULTS:
Duplicates: {total_duplicates} files
Unused Files: {total_unused} files
Temporary Files: {total_temp} files
Large Files: {total_large} files

Total Cleanup Size: {size_mb:.1f} MB
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
    
    def select_all(self):
        """Select all items in current tab"""
        # This would need to be implemented based on the current tab
        pass
    
    def deselect_all(self):
        """Deselect all items in current tab"""
        # This would need to be implemented based on the current tab
        pass
    
    def delete_selected(self):
        """Delete selected items"""
        if not messagebox.askyesno("Confirm Deletion", 
                                  "Are you sure you want to delete the selected files?"):
            return
        
        # Implementation for deleting selected files
        self.log_message("Deletion not yet implemented", "WARNING")
    
    def export_list(self):
        """Export file list to text file"""
        # Implementation for exporting file lists
        self.log_message("Export not yet implemented", "WARNING")
    
    def start_cleanup(self):
        """Start the cleanup process"""
        if not any([self.clean_duplicates.get(), self.clean_unused.get(), 
                   self.clean_temp.get(), self.clean_large.get()]):
            messagebox.showwarning("Warning", "No cleanup options selected")
            return
        
        if self.create_backup.get():
            self.log_message("Creating backup...")
            # Implementation for creating backup
        
        self.log_message("Cleanup process not yet fully implemented", "WARNING")

def main():
    """Main entry point"""
    app = AssetCleaner()

if __name__ == "__main__":
    main()
