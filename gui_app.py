"""
GUI Application for EC Product Image Generator
User-friendly interface for non-engineers
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
import logging
from PIL import Image, ImageTk
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from logger_config import setup_logger
from main import ECImageGenerator
from config import Config

# Setup logger
logger = setup_logger("GUI", logging.INFO)

class ECImageGeneratorGUI:
    """GUI application for EC product image generation"""
    
    def __init__(self, root):
        """Initialize GUI"""
        self.root = root
        self.root.title("EC Product Image Generator")
        self.root.geometry("900x700")
        
        self.generator = None
        self.current_image = None
        
        logger.info("Initializing GUI application")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # === Left Panel: Input Controls ===
        left_panel = ttk.LabelFrame(main_frame, text="Input Settings", padding="10")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Prompt input
        ttk.Label(left_panel, text="Product Prompt:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.prompt_text = scrolledtext.ScrolledText(left_panel, width=30, height=5, wrap=tk.WORD)
        self.prompt_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.prompt_text.insert("1.0", "Modern product on white background, professional photography")
        
        # Platform selection
        ttk.Label(left_panel, text="EC Platform:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.platform_var = tk.StringVar(value="amazon")
        platform_combo = ttk.Combobox(left_panel, textvariable=self.platform_var, 
                                     values=list(Config.PLATFORMS.keys()), state="readonly")
        platform_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Model selection
        ttk.Label(left_panel, text="AI Model:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="stable_diffusion")
        model_combo = ttk.Combobox(left_panel, textvariable=self.model_var,
                                  values=["stable_diffusion", "lovart"], state="readonly")
        model_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Pattern selection
        ttk.Label(left_panel, text="Layout Pattern:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.pattern_var = tk.StringVar(value="")
        pattern_combo = ttk.Combobox(left_panel, textvariable=self.pattern_var,
                                    values=[""] + [p['name'] for p in Config.TEMPLATE_PATTERNS], state="readonly")
        pattern_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Text elements
        text_frame = ttk.LabelFrame(left_panel, text="Text Elements", padding="5")
        text_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(text_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_entry = ttk.Entry(text_frame, width=25)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(text_frame, text="Price:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.price_entry = ttk.Entry(text_frame, width=25)
        self.price_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(text_frame, text="Tagline:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.tagline_entry = ttk.Entry(text_frame, width=25)
        self.tagline_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Options
        options_frame = ttk.LabelFrame(left_panel, text="Options", padding="5")
        options_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.quality_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Run Quality Check", 
                       variable=self.quality_check_var).grid(row=0, column=0, sticky=tk.W)
        
        self.auto_fix_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Auto-fix Issues", 
                       variable=self.auto_fix_var).grid(row=1, column=0, sticky=tk.W)
        
        self.use_openai_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Use OpenAI Enhancement", 
                       variable=self.use_openai_var).grid(row=2, column=0, sticky=tk.W)
        
        # Generate button
        self.generate_btn = ttk.Button(left_panel, text="Generate Image", 
                                      command=self.on_generate_clicked)
        self.generate_btn.grid(row=7, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))
        
        # Save button
        self.save_btn = ttk.Button(left_panel, text="Save Image", 
                                  command=self.on_save_clicked, state=tk.DISABLED)
        self.save_btn.grid(row=8, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # === Right Panel: Preview and Status ===
        right_panel = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Status label
        self.status_label = ttk.Label(right_panel, text="Ready to generate", 
                                     foreground="green")
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Image preview
        self.preview_label = ttk.Label(right_panel, text="No image generated yet", 
                                      background="lightgray", anchor=tk.CENTER)
        self.preview_label.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Quality report
        report_frame = ttk.LabelFrame(right_panel, text="Quality Report", padding="5")
        report_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        report_frame.columnconfigure(0, weight=1)
        
        self.quality_report = scrolledtext.ScrolledText(report_frame, width=40, height=8, 
                                                        wrap=tk.WORD, state=tk.DISABLED)
        self.quality_report.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Progress bar
        self.progress = ttk.Progressbar(right_panel, mode='indeterminate')
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
    
    def on_generate_clicked(self):
        """Handle generate button click"""
        logger.info("Generate button clicked")
        # Disable button during generation
        self.generate_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Generating...", foreground="blue")
        self.progress.start()
        
        # Clear previous results
        self.quality_report.config(state=tk.NORMAL)
        self.quality_report.delete("1.0", tk.END)
        self.quality_report.config(state=tk.DISABLED)
        
        # Run generation in separate thread
        thread = threading.Thread(target=self.generate_image_thread)
        thread.daemon = True
        thread.start()
    
    def generate_image_thread(self):
        """Generate image in background thread"""
        try:
            # Get input values
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            platform = self.platform_var.get()
            model = self.model_var.get()
            pattern = self.pattern_var.get() if self.pattern_var.get() else None
            
            logger.info(f"Starting generation: prompt='{prompt[:50]}...', platform={platform}, model={model}")
            
            # Build text elements
            text_elements = {}
            title = self.title_entry.get().strip()
            price = self.price_entry.get().strip()
            tagline = self.tagline_entry.get().strip()
            
            if title:
                text_elements['title'] = {'text': title}
            if price:
                text_elements['price'] = {'text': price}
            if tagline:
                text_elements['tagline'] = {'text': tagline}
            
            # Initialize generator
            self.generator = ECImageGenerator(
                model_type=model,
                use_openai=self.use_openai_var.get()
            )
            
            # Generate image
            self.current_image = self.generator.generate_product_image(
                prompt=prompt,
                platform=platform,
                text_elements=text_elements if text_elements else None,
                pattern_name=pattern,
                output_path=None,
                run_quality_check=self.quality_check_var.get(),
                auto_fix=self.auto_fix_var.get()
            )
            
            # Update UI in main thread
            self.root.after(0, self.on_generation_complete)
            
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            self.root.after(0, lambda: self.on_generation_error(str(e)))
    
    def on_generation_complete(self):
        """Handle successful generation"""
        logger.info("Generation completed successfully")
        self.progress.stop()
        self.generate_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Generation complete!", foreground="green")
        
        # Display image
        if self.current_image:
            # Resize for preview (maintain aspect ratio)
            preview_size = (400, 400)
            preview_img = self.current_image.copy()
            preview_img.thumbnail(preview_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(preview_img)
            
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo  # Keep a reference
        
        # Show quality report if available
        if self.generator and self.quality_check_var.get():
            report = self.generator.quality_checker.generate_quality_report(
                self.current_image,
                self.platform_var.get()
            )
            self.quality_report.config(state=tk.NORMAL)
            self.quality_report.insert("1.0", report)
            self.quality_report.config(state=tk.DISABLED)
    
    def on_generation_error(self, error_msg):
        """Handle generation error"""
        logger.error(f"Generation error: {error_msg}")
        self.progress.stop()
        self.generate_btn.config(state=tk.NORMAL)
        self.status_label.config(text=f"Error: {error_msg[:50]}...", foreground="red")
        messagebox.showerror("Generation Error", f"Failed to generate image:\n{error_msg}")
    
    def on_save_clicked(self):
        """Handle save button click"""
        if not self.current_image:
            messagebox.showwarning("No Image", "Please generate an image first.")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                logger.info(f"Saving image to: {filename}")
                self.current_image.save(filename, quality=95)
                messagebox.showinfo("Success", f"Image saved to:\n{filename}")
            except Exception as e:
                logger.error(f"Save failed: {e}")
                messagebox.showerror("Save Error", f"Failed to save image:\n{e}")

def main():
    """Launch GUI application"""
    logger.info("Starting GUI application")
    root = tk.Tk()
    app = ECImageGeneratorGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()

