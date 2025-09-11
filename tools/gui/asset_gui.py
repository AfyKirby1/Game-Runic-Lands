#!/usr/bin/env python3
"""
Runic Lands Asset Generator GUI
Modern graphical interface for asset generation and management
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
import subprocess
from pathlib import Path
import json
import webbrowser

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our asset tools
sys.path.insert(0, str(Path(__file__).parent.parent))
from asset_manager import AssetManager
from sprite_generation.sprite_generator import SpriteGenerator
from asset_validation.asset_validator import AssetValidator
from audio_manager import AudioManager

class AssetGeneratorGUI:
    """Modern GUI for Runic Lands Asset Generator"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Runic Lands Asset Generator")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Initialize asset managers
        self.asset_manager = AssetManager()
        self.sprite_generator = SpriteGenerator()
        self.asset_validator = AssetValidator()
        self.audio_manager = AudioManager()
        
        # Throttling for validation to prevent loops
        self.last_validation_time = 0
        self.validation_throttle_seconds = 2  # Minimum 2 seconds between validations
        
        # GUI state
        self.current_preview_image = None
        self.asset_status = {}
        self.generation_log = []
        self.preview_mode = tk.StringVar(value="all")
        
        # Configure style
        self.setup_styles()
        
        # Create GUI
        self.create_widgets()
        self.load_asset_status()
        
        # Start background monitoring
        self.monitor_assets()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Configure GUI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
        
        # Custom button styles
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        style.configure('Tool.TButton', font=('Arial', 9))
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Runic Lands Asset Generator", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel - Controls
        self.create_control_panel(main_frame)
        
        # Right panel - Preview and Log
        self.create_preview_panel(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_control_panel(self, parent):
        """Create the control panel with scrollable canvas"""
        control_frame = ttk.LabelFrame(parent, text="Asset Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Create scrollable canvas for control panel
        canvas = tk.Canvas(control_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(control_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Asset Status
        status_frame = ttk.LabelFrame(scrollable_frame, text="Asset Status", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_text = tk.Text(status_frame, height=8, width=40, wrap=tk.WORD)
        status_scroll = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scroll.set)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Character Customization Panel
        char_frame = ttk.LabelFrame(scrollable_frame, text="Character Customization", padding="5")
        char_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Character customization variables
        self.skin_tone_var = tk.StringVar(value="light")
        self.hair_color_var = tk.StringVar(value="brown")
        self.shirt_color_var = tk.StringVar(value="blue")
        self.pants_color_var = tk.StringVar(value="gray")
        self.shoes_color_var = tk.StringVar(value="black")
        self.eye_color_var = tk.StringVar(value="brown")
        self.hair_style_var = tk.StringVar(value="short")
        
        # Skin tone
        ttk.Label(char_frame, text="Skin Tone:").grid(row=0, column=0, sticky=tk.W, pady=2)
        skin_combo = ttk.Combobox(char_frame, textvariable=self.skin_tone_var, 
                                 values=["light", "medium", "dark", "pale", "tan"], width=15)
        skin_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Hair color
        ttk.Label(char_frame, text="Hair Color:").grid(row=1, column=0, sticky=tk.W, pady=2)
        hair_combo = ttk.Combobox(char_frame, textvariable=self.hair_color_var,
                                 values=["brown", "blonde", "black", "red", "gray", "white"], width=15)
        hair_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Shirt color
        ttk.Label(char_frame, text="Shirt Color:").grid(row=2, column=0, sticky=tk.W, pady=2)
        shirt_combo = ttk.Combobox(char_frame, textvariable=self.shirt_color_var,
                                  values=["blue", "red", "green", "white", "black", "gray", "brown"], width=15)
        shirt_combo.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Pants color
        ttk.Label(char_frame, text="Pants Color:").grid(row=3, column=0, sticky=tk.W, pady=2)
        pants_combo = ttk.Combobox(char_frame, textvariable=self.pants_color_var,
                                  values=["gray", "blue", "black", "brown", "green", "dark_gray"], width=15)
        pants_combo.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Shoes color
        ttk.Label(char_frame, text="Shoes Color:").grid(row=4, column=0, sticky=tk.W, pady=2)
        shoes_combo = ttk.Combobox(char_frame, textvariable=self.shoes_color_var,
                                  values=["black", "brown", "gray", "white", "dark_brown"], width=15)
        shoes_combo.grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Eye color
        ttk.Label(char_frame, text="Eye Color:").grid(row=5, column=0, sticky=tk.W, pady=2)
        eye_combo = ttk.Combobox(char_frame, textvariable=self.eye_color_var,
                                values=["brown", "blue", "green", "hazel", "gray"], width=15)
        eye_combo.grid(row=5, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Hair style
        ttk.Label(char_frame, text="Hair Style:").grid(row=6, column=0, sticky=tk.W, pady=2)
        style_combo = ttk.Combobox(char_frame, textvariable=self.hair_style_var,
                                  values=["short", "medium", "long", "bald", "curly"], width=15)
        style_combo.grid(row=6, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Character generation buttons
        char_buttons = ttk.Frame(char_frame)
        char_buttons.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(char_buttons, text="Generate Custom Character", 
                  command=self.generate_custom_character, style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(char_buttons, text="Random Character", 
                  command=self.generate_random_character, style='Tool.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(char_buttons, text="Reset to Default", 
                  command=self.reset_customization, style='Tool.TButton').pack(side=tk.LEFT, padx=5)
        
        # Generation Controls
        gen_frame = ttk.LabelFrame(scrollable_frame, text="Generation", padding="5")
        gen_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Sprite controls
        ttk.Button(gen_frame, text="Generate Sprites", command=self.generate_sprites).pack(fill=tk.X, pady=2)
        ttk.Button(gen_frame, text="Validate Sprites", command=self.validate_sprites).pack(fill=tk.X, pady=2)
        ttk.Button(gen_frame, text="Create Sprite Preview", command=self.create_sprite_preview).pack(fill=tk.X, pady=2)
        
        ttk.Separator(gen_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Audio controls
        ttk.Button(gen_frame, text="Generate Audio", command=self.generate_audio).pack(fill=tk.X, pady=2)
        ttk.Button(gen_frame, text="Validate Audio", command=self.validate_audio).pack(fill=tk.X, pady=2)
        ttk.Button(gen_frame, text="Analyze Audio", command=self.analyze_audio).pack(fill=tk.X, pady=2)
        
        ttk.Separator(gen_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # All assets
        ttk.Button(gen_frame, text="Generate All Assets", command=self.generate_all, style='Accent.TButton').pack(fill=tk.X, pady=2)
        ttk.Button(gen_frame, text="Validate All Assets", command=self.validate_all).pack(fill=tk.X, pady=2)
        ttk.Button(gen_frame, text="Complete Setup", command=self.complete_setup).pack(fill=tk.X, pady=2)
        
        # Advanced Tools
        adv_frame = ttk.LabelFrame(scrollable_frame, text="Advanced Tools", padding="5")
        adv_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(adv_frame, text="Location Generator", command=self.open_location_generator).pack(fill=tk.X, pady=2)
        ttk.Button(adv_frame, text="Asset Cleaner", command=self.open_asset_cleaner).pack(fill=tk.X, pady=2)
        ttk.Button(adv_frame, text="Batch Processor", command=self.open_batch_processor).pack(fill=tk.X, pady=2)
        ttk.Button(adv_frame, text="Asset Reporter", command=self.generate_asset_report).pack(fill=tk.X, pady=2)
        
        # Options
        opt_frame = ttk.LabelFrame(scrollable_frame, text="Options", padding="5")
        opt_frame.pack(fill=tk.X)
        
        self.force_var = tk.BooleanVar()
        ttk.Checkbutton(opt_frame, text="Force Overwrite", variable=self.force_var).pack(anchor=tk.W)
        
        self.auto_validate_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_frame, text="Auto-validate after generation", variable=self.auto_validate_var).pack(anchor=tk.W)
        
        self.auto_preview_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_frame, text="Auto-preview after generation", variable=self.auto_preview_var).pack(anchor=tk.W)
        
        # Store canvas reference for cleanup
        self.control_canvas = canvas
    
    def create_preview_panel(self, parent):
        """Create the enhanced preview panel with scrollable canvas"""
        preview_frame = ttk.LabelFrame(parent, text="Asset Preview", padding="10")
        preview_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Preview mode selection
        mode_frame = ttk.Frame(preview_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(mode_frame, text="Preview Mode:").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="All Sprites", variable=self.preview_mode, 
                       value="all", command=self.refresh_preview).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(mode_frame, text="Single", variable=self.preview_mode, 
                       value="single", command=self.refresh_preview).pack(side=tk.LEFT, padx=(10, 0))
        
        # Create scrollable canvas for preview
        self.preview_canvas = tk.Canvas(preview_frame, highlightthickness=0, bg='white')
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_canvas.yview)
        self.preview_canvas.configure(yscrollcommand=preview_scrollbar.set)
        
        # Pack canvas and scrollbar
        self.preview_canvas.pack(side="left", fill="both", expand=True)
        preview_scrollbar.pack(side="right", fill="y")
        
        # Bind canvas resize event
        self.preview_canvas.bind("<Configure>", self.on_canvas_resize)
        
        # Preview controls
        preview_controls = ttk.Frame(preview_frame)
        preview_controls.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(preview_controls, text="Refresh Preview", command=self.refresh_preview).pack(side=tk.LEFT)
        ttk.Button(preview_controls, text="Open in Explorer", command=self.open_asset_folder).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(preview_controls, text="View Full Size", command=self.view_full_size).pack(side=tk.LEFT, padx=(10, 0))
        
        # Log area
        log_frame = ttk.LabelFrame(parent, text="Generation Log", padding="5")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(log_controls, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT)
        ttk.Button(log_controls, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(log_controls, text="Copy Log", command=self.copy_log).pack(side=tk.LEFT, padx=(10, 0))
    
    def create_status_bar(self, parent):
        """Create the status bar"""
        self.status_bar = ttk.Frame(parent)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(self.status_bar, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=(10, 0))
    
    def log_message(self, message, level="INFO"):
        """Add message to log (thread-safe)"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # Schedule GUI update on main thread
        def update_log():
            self.log_text.insert(tk.END, formatted_message)
            self.log_text.see(tk.END)
            
            # Color coding
            if level == "ERROR":
                self.log_text.tag_add("error", f"end-2l", "end-1l")
            elif level == "SUCCESS":
                self.log_text.tag_add("success", f"end-2l", "end-1l")
            elif level == "WARNING":
                self.log_text.tag_add("warning", f"end-2l", "end-1l")
        
        # Use after_idle to ensure it runs on main thread
        self.root.after_idle(update_log)
    
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
            with open(filename, 'w') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log_message(f"Log saved to {filename}", "SUCCESS")
    
    def copy_log(self):
        """Copy log to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_text.get(1.0, tk.END))
        self.log_message("Log copied to clipboard", "SUCCESS")
    
    def set_status(self, message):
        """Update status bar (thread-safe)"""
        def update_status():
            self.status_label.config(text=message)
        
        # Use after_idle to ensure it runs on main thread
        self.root.after_idle(update_status)
    
    def start_progress(self):
        """Start progress indicator (thread-safe)"""
        def start():
            self.progress.start()
        self.root.after_idle(start)
    
    def stop_progress(self):
        """Stop progress indicator (thread-safe)"""
        def stop():
            self.progress.stop()
        self.root.after_idle(stop)
    
    def load_asset_status(self):
        """Load current asset status"""
        self.status_text.delete(1.0, tk.END)
        
        try:
            # Check sprites
            sprite_status = self.sprite_generator.check_existing_files()
            self.status_text.insert(tk.END, "SPRITE ASSETS:\n")
            for filename, exists in sprite_status.items():
                status = "✅" if exists else "❌"
                self.status_text.insert(tk.END, f"  {status} {filename}\n")
            
            self.status_text.insert(tk.END, "\nAUDIO ASSETS:\n")
            # Check audio (simplified)
            audio_files = [
                "menu_click.wav", "menu_select.wav", "attack.wav",
                "menu_theme.wav"
            ]
            for filename in audio_files:
                path = Path("assets/audio") / filename
                exists = path.exists()
                status = "✅" if exists else "❌"
                self.status_text.insert(tk.END, f"  {status} {filename}\n")
            
        except Exception as e:
            self.log_message(f"Error loading asset status: {e}", "ERROR")
    
    def monitor_assets(self):
        """Monitor asset changes"""
        # This could be expanded to watch for file changes
        pass
    
    def on_closing(self):
        """Handle window closing"""
        # Unbind mousewheel to prevent errors
        if hasattr(self, 'control_canvas'):
            self.control_canvas.unbind_all("<MouseWheel>")
        self.root.destroy()
    
    def on_canvas_resize(self, event):
        """Handle canvas resize events"""
        # Refresh preview when canvas is resized
        if hasattr(self, 'preview_canvas') and self.preview_canvas.winfo_width() > 1:
            self.root.after(100, self.refresh_preview)
    
    def refresh_preview(self):
        """Refresh the preview with enhanced grid layout"""
        try:
            # Clear canvas
            self.preview_canvas.delete("all")
            
            # Check for sprite files
            sprite_dir = Path("assets/sprites/characters/player/png")
            if not sprite_dir.exists():
                self.preview_canvas.create_text(200, 100, text="No sprites directory found", 
                                              fill="gray", font=("Arial", 12))
                return
            
            # Get all PNG files
            sprite_files = list(sprite_dir.glob("*.png"))
            if not sprite_files:
                self.preview_canvas.create_text(200, 100, text="No sprite files found", 
                                              fill="gray", font=("Arial", 12))
                return
            
            # Load preview based on mode
            if self.preview_mode.get() == "all":
                self.load_all_sprites_preview(sprite_files)
            else:
                # Single mode - show first available sprite
                if sprite_files:
                    self.load_single_preview(sprite_files[0])
                    
        except Exception as e:
            self.log_message(f"Error refreshing preview: {e}", "ERROR")
            self.preview_canvas.create_text(200, 100, text=f"Error: {e}", 
                                          fill="red", font=("Arial", 12))
    
    def load_single_preview(self, image_path):
        """Load and display a single image"""
        try:
            image = Image.open(image_path)
            
            # Resize for preview - make it larger
            max_size = 400
            if image.width > max_size or image.height > max_size:
                ratio = min(max_size / image.width, max_size / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Center the image
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # If canvas hasn't been drawn yet, use default size
            if canvas_width <= 1:
                canvas_width = 400
            if canvas_height <= 1:
                canvas_height = 400
                
            x = max(20, (canvas_width - image.width) // 2)
            y = max(20, (canvas_height - image.height) // 2)
            
            # Add image to canvas
            self.preview_canvas.create_image(x, y, anchor="nw", image=photo)
            
            # Add filename
            filename = image_path.name
            self.preview_canvas.create_text(x + image.width // 2, y + image.height + 25, 
                                          text=filename, fill="black", font=("Arial", 12))
            
            # Keep reference to prevent garbage collection
            self.preview_canvas.image_ref = photo
            
            # Update scroll region
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
        except Exception as e:
            self.log_message(f"Error loading single preview: {e}", "ERROR")
    
    def load_all_sprites_preview(self, sprite_files):
        """Load and display all sprites in a grid"""
        try:
            # Grid settings
            cols = 3
            sprite_size = 120  # Increased size for better visibility
            padding = 15
            start_x = 20
            start_y = 20
            
            x, y = start_x, start_y
            col = 0
            image_refs = []  # Store all image references
            
            for i, sprite_path in enumerate(sprite_files):
                try:
                    # Load and resize image
                    image = Image.open(sprite_path)
                    image = image.resize((sprite_size, sprite_size), Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(image)
                    
                    # Add image to canvas
                    self.preview_canvas.create_image(x, y, anchor="nw", image=photo)
                    
                    # Add filename (truncated if too long)
                    filename = sprite_path.name
                    if len(filename) > 15:
                        filename = filename[:12] + "..."
                    self.preview_canvas.create_text(x + sprite_size // 2, y + sprite_size + 15, 
                                                  text=filename, fill="black", font=("Arial", 8))
                    
                    # Keep reference to prevent garbage collection
                    image_refs.append(photo)
                    
                    # Move to next position
                    col += 1
                    if col >= cols:
                        col = 0
                        x = start_x
                        y += sprite_size + 50  # Extra space for filename
                    else:
                        x += sprite_size + padding
                        
                except Exception as e:
                    self.log_message(f"Error loading sprite {sprite_path}: {e}", "ERROR")
                    continue
            
            # Store all image references
            self.preview_canvas.image_refs = image_refs
            
            # Update scroll region
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
        except Exception as e:
            self.log_message(f"Error loading all sprites preview: {e}", "ERROR")
    
    def load_preview_image(self, image_path):
        """Load preview image"""
        try:
            image = Image.open(image_path)
            
            # Resize for preview (max 400x400)
            max_size = 400
            if image.width > max_size or image.height > max_size:
                ratio = min(max_size / image.width, max_size / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            self.current_preview_image = ImageTk.PhotoImage(image)
            self.preview_label.config(image=self.current_preview_image, text="")
            
        except Exception as e:
            self.log_message(f"Error loading preview image: {e}", "ERROR")
            self.preview_label.config(text="Error loading preview")
    
    def open_asset_folder(self):
        """Open asset folder in explorer"""
        try:
            asset_path = Path("assets/sprites/characters/player/png")
            if asset_path.exists():
                os.startfile(str(asset_path))
            else:
                messagebox.showwarning("Warning", "Asset folder not found")
        except Exception as e:
            self.log_message(f"Error opening asset folder: {e}", "ERROR")
    
    def view_full_size(self):
        """View all sprites at full size in new window"""
        try:
            sprite_dir = Path("assets/sprites/characters/player/png")
            if not sprite_dir.exists():
                messagebox.showwarning("Warning", "No sprites directory found")
                return
            
            sprite_files = list(sprite_dir.glob("*.png"))
            if not sprite_files:
                messagebox.showwarning("Warning", "No sprite files found")
                return
            
            # Create new window
            window = tk.Toplevel(self.root)
            window.title("Full Size Sprite Viewer")
            window.geometry("800x600")
            
            # Create scrollable canvas
            canvas = tk.Canvas(window, bg='white')
            scrollbar_v = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
            scrollbar_h = ttk.Scrollbar(window, orient="horizontal", command=canvas.xview)
            canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
            
            # Add all sprites to canvas
            y_offset = 20
            for sprite_path in sprite_files:
                try:
                    image = Image.open(sprite_path)
                    photo = ImageTk.PhotoImage(image)
                    
                    # Add image
                    canvas.create_image(20, y_offset, anchor="nw", image=photo)
                    
                    # Add filename
                    canvas.create_text(20 + image.width // 2, y_offset + image.height + 20, 
                                     text=sprite_path.name, fill="black", font=("Arial", 10))
                    
                    # Keep reference
                    setattr(canvas, f"photo_{sprite_path.name}", photo)
                    
                    y_offset += image.height + 60  # Space for filename
                    
                except Exception as e:
                    self.log_message(f"Error loading {sprite_path}: {e}", "ERROR")
                    continue
            
            # Configure scroll region
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Pack widgets
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar_v.pack(side="right", fill="y")
            scrollbar_h.pack(side="bottom", fill="x")
            
        except Exception as e:
            self.log_message(f"Error viewing full size: {e}", "ERROR")
    
    def generate_custom_character(self):
        """Generate custom character with selected settings"""
        self.run_in_thread(self._generate_custom_character)
    
    def _generate_custom_character(self):
        """Generate custom character (runs in thread)"""
        try:
            # Import the enhanced character generator
            from utils.generators import generate_custom_character
            
            # Get settings from GUI
            settings = {
                'skin_tone': self.skin_tone_var.get(),
                'hair_color': self.hair_color_var.get(),
                'shirt_color': self.shirt_color_var.get(),
                'pants_color': self.pants_color_var.get(),
                'shoes_color': self.shoes_color_var.get(),
                'eye_color': self.eye_color_var.get(),
                'hair_style': self.hair_style_var.get()
            }
            
            self.log_message("Generating custom character...", "INFO")
            generate_custom_character(**settings)
            self.log_message("Custom character generated successfully!", "SUCCESS")
            
            # Auto-refresh preview and status
            self.root.after(100, self.refresh_preview)
            self.root.after(200, self.load_asset_status)
            
        except Exception as e:
            self.log_message(f"Error generating custom character: {e}", "ERROR")
    
    def generate_random_character(self):
        """Generate random character"""
        self.run_in_thread(self._generate_random_character)
    
    def _generate_random_character(self):
        """Generate random character (runs in thread)"""
        try:
            # Import the enhanced character generator
            from utils.generators import generate_random_character
            
            self.log_message("Generating random character...", "INFO")
            generate_random_character()
            self.log_message("Random character generated successfully!", "SUCCESS")
            
            # Auto-refresh preview and status
            self.root.after(100, self.refresh_preview)
            self.root.after(200, self.load_asset_status)
            
        except Exception as e:
            self.log_message(f"Error generating random character: {e}", "ERROR")
    
    def reset_customization(self):
        """Reset customization to default values"""
        self.skin_tone_var.set("light")
        self.hair_color_var.set("brown")
        self.shirt_color_var.set("blue")
        self.pants_color_var.set("gray")
        self.shoes_color_var.set("black")
        self.eye_color_var.set("brown")
        self.hair_style_var.set("short")
        self.log_message("Customization reset to defaults", "INFO")
    
    def run_in_thread(self, func, *args, **kwargs):
        """Run function in background thread"""
        def wrapper():
            try:
                self.start_progress()
                self.set_status("Working...")
                result = func(*args, **kwargs)
                self.log_message(f"Operation completed successfully", "SUCCESS")
                
                # Schedule GUI updates on main thread (with delay to prevent loops)
                if self.auto_validate_var.get():
                    self.root.after(1000, self.validate_all)  # 1 second delay
                if self.auto_preview_var.get():
                    self.root.after(500, self.refresh_preview)  # 0.5 second delay
                self.root.after(200, self.load_asset_status)  # 0.2 second delay
                
            except Exception as e:
                self.log_message(f"Error: {e}", "ERROR")
            finally:
                self.stop_progress()
                self.set_status("Ready")
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
    
    def generate_sprites(self):
        """Generate sprite assets"""
        self.run_in_thread(self._generate_sprites)
    
    def _generate_sprites(self):
        """Generate sprites (runs in thread)"""
        self.log_message("Starting sprite generation...", "INFO")
        self.sprite_generator.generate_all_sprites(self.force_var.get())
        self.log_message("Sprite generation completed", "SUCCESS")
        
        # Auto-refresh preview and status after sprite generation
        self.root.after(100, self.refresh_preview)
        self.root.after(200, self.load_asset_status)
    
    def validate_sprites(self):
        """Validate sprite assets (with throttling)"""
        import time
        current_time = time.time()
        
        # Check if enough time has passed since last validation
        if current_time - self.last_validation_time < self.validation_throttle_seconds:
            self.log_message("Validation throttled - please wait before running again", "WARNING")
            return
            
        self.last_validation_time = current_time
        self.run_in_thread(self._validate_sprites)
    
    def _validate_sprites(self):
        """Validate sprites (runs in thread)"""
        self.log_message("Validating sprites...", "INFO")
        self.asset_validator.validate_sprites()
        self.log_message("Sprite validation completed", "SUCCESS")
    
    def create_sprite_preview(self):
        """Create sprite preview"""
        self.run_in_thread(self._create_sprite_preview)
    
    def _create_sprite_preview(self):
        """Create sprite preview (runs in thread)"""
        self.log_message("Creating sprite preview...", "INFO")
        self.sprite_generator.create_sprite_sheet_preview()
        self.log_message("Sprite preview created", "SUCCESS")
        
        # Auto-refresh preview and status after creating preview
        self.root.after(100, self.refresh_preview)
        self.root.after(200, self.load_asset_status)
    
    def generate_audio(self):
        """Generate audio assets"""
        self.run_in_thread(self._generate_audio)
    
    def _generate_audio(self):
        """Generate audio (runs in thread)"""
        self.log_message("Starting audio generation...", "INFO")
        self.audio_manager.generate_all_missing(self.force_var.get())
        self.log_message("Audio generation completed", "SUCCESS")
    
    def validate_audio(self):
        """Validate audio assets (with throttling)"""
        import time
        current_time = time.time()
        
        # Check if enough time has passed since last validation
        if current_time - self.last_validation_time < self.validation_throttle_seconds:
            self.log_message("Validation throttled - please wait before running again", "WARNING")
            return
            
        self.last_validation_time = current_time
        self.run_in_thread(self._validate_audio)
    
    def _validate_audio(self):
        """Validate audio (runs in thread)"""
        self.log_message("Validating audio...", "INFO")
        self.asset_validator.validate_audio()
        self.log_message("Audio validation completed", "SUCCESS")
    
    def analyze_audio(self):
        """Analyze audio assets"""
        self.run_in_thread(self._analyze_audio)
    
    def _analyze_audio(self):
        """Analyze audio (runs in thread)"""
        self.log_message("Analyzing audio files...", "INFO")
        self.audio_manager.analyze_files()
        self.log_message("Audio analysis completed", "SUCCESS")
    
    def generate_all(self):
        """Generate all assets"""
        self.run_in_thread(self._generate_all)
    
    def _generate_all(self):
        """Generate all assets (runs in thread)"""
        self.log_message("Starting complete asset generation...", "INFO")
        self.asset_manager.generate_all_assets(self.force_var.get())
        self.log_message("Complete asset generation finished", "SUCCESS")
        
        # Auto-refresh preview and status after complete generation
        self.root.after(100, self.refresh_preview)
        self.root.after(200, self.load_asset_status)
    
    def validate_all(self):
        """Validate all assets (with throttling)"""
        import time
        current_time = time.time()
        
        # Check if enough time has passed since last validation
        if current_time - self.last_validation_time < self.validation_throttle_seconds:
            self.log_message("Validation throttled - please wait before running again", "WARNING")
            return
            
        self.last_validation_time = current_time
        self.run_in_thread(self._validate_all)
    
    def _validate_all(self):
        """Validate all assets (runs in thread)"""
        self.log_message("Validating all assets...", "INFO")
        self.asset_manager.validate_all_assets()
        self.log_message("Complete validation finished", "SUCCESS")
    
    def complete_setup(self):
        """Complete asset setup"""
        self.run_in_thread(self._complete_setup)
    
    def _complete_setup(self):
        """Complete setup (runs in thread)"""
        self.log_message("Starting complete asset setup...", "INFO")
        self.asset_manager.generate_all_assets(self.force_var.get())
        self.asset_manager.validate_all_assets()
        self.asset_manager.organize_assets()
        self.log_message("Complete setup finished", "SUCCESS")
        
        # Auto-refresh preview and status after complete setup
        self.root.after(100, self.refresh_preview)
        self.root.after(200, self.load_asset_status)
    
    def generate_asset_report(self):
        """Generate asset report"""
        self.run_in_thread(self._generate_asset_report)
    
    def _generate_asset_report(self):
        """Generate asset report (runs in thread)"""
        self.log_message("Generating asset report...", "INFO")
        self.asset_validator.save_report()
        self.log_message("Asset report generated", "SUCCESS")
    
    def open_location_generator(self):
        """Open location generator"""
        LocationGenerator(self.root)
    
    def open_asset_cleaner(self):
        """Open asset cleaner"""
        AssetCleaner(self.root)
    
    def open_batch_processor(self):
        """Open batch processor"""
        BatchProcessor(self.root)

class LocationGenerator:
    """Location generator tool"""
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Location Generator")
        self.window.geometry("600x400")
        
        # Create GUI
        self.create_widgets()
    
    def create_widgets(self):
        """Create location generator widgets"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Location Generator", style='Title.TLabel').pack(pady=(0, 20))
        
        # Location type selection
        type_frame = ttk.LabelFrame(main_frame, text="Location Type", padding="10")
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.location_type = tk.StringVar(value="forest")
        ttk.Radiobutton(type_frame, text="Forest", variable=self.location_type, value="forest").pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="Dungeon", variable=self.location_type, value="dungeon").pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="Village", variable=self.location_type, value="village").pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="Castle", variable=self.location_type, value="castle").pack(anchor=tk.W)
        
        # Generation options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(options_frame, text="Location Name:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(options_frame, width=30)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(options_frame, text="Size:").pack(anchor=tk.W)
        self.size_var = tk.StringVar(value="medium")
        size_combo = ttk.Combobox(options_frame, textvariable=self.size_var, values=["small", "medium", "large"])
        size_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Generate button
        ttk.Button(main_frame, text="Generate Location", command=self.generate_location).pack(pady=10)
    
    def generate_location(self):
        """Generate a new location"""
        # This would integrate with the world generation system
        messagebox.showinfo("Info", "Location generation feature coming soon!")

class AssetCleaner:
    """Asset cleaner tool"""
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Asset Cleaner")
        self.window.geometry("500x300")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create asset cleaner widgets"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Asset Cleaner", style='Title.TLabel').pack(pady=(0, 20))
        
        # Cleanup options
        options_frame = ttk.LabelFrame(main_frame, text="Cleanup Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.clean_temp = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Clean temporary files", variable=self.clean_temp).pack(anchor=tk.W)
        
        self.clean_backups = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Clean old backups", variable=self.clean_backups).pack(anchor=tk.W)
        
        self.clean_unused = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Clean unused assets", variable=self.clean_unused).pack(anchor=tk.W)
        
        # Clean button
        ttk.Button(main_frame, text="Clean Assets", command=self.clean_assets).pack(pady=10)
    
    def clean_assets(self):
        """Clean assets"""
        messagebox.showinfo("Info", "Asset cleaning feature coming soon!")

class BatchProcessor:
    """Batch processor tool"""
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Batch Processor")
        self.window.geometry("600x400")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create batch processor widgets"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Batch Processor", style='Title.TLabel').pack(pady=(0, 20))
        
        # Batch operations
        operations_frame = ttk.LabelFrame(main_frame, text="Batch Operations", padding="10")
        operations_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(operations_frame, text="Process Multiple Projects", command=self.process_projects).pack(fill=tk.X, pady=2)
        ttk.Button(operations_frame, text="Convert Asset Formats", command=self.convert_formats).pack(fill=tk.X, pady=2)
        ttk.Button(operations_frame, text="Resize Assets", command=self.resize_assets).pack(fill=tk.X, pady=2)
        ttk.Button(operations_frame, text="Optimize Assets", command=self.optimize_assets).pack(fill=tk.X, pady=2)
    
    def process_projects(self):
        """Process multiple projects"""
        messagebox.showinfo("Info", "Batch processing feature coming soon!")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = AssetGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
