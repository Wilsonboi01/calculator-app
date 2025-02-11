from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")  # This will load an HTML page

if __name__ == "__main__":
    app.run()
from tkinter import ttk, messagebox
import pygame
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk, filedialog
import math
import os
import shutil
from PIL import Image, ImageTk
import pygame  # For music playback
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json

class ScientificCalculator:
    def __init__(self):
        # Initialize pygame and mixer first
        try:
            pygame.mixer.quit()  # Clean up any existing mixer
            pygame.mixer.init(frequency=44100)
            pygame.mixer.music.set_volume(1.0)
        except Exception as e:
            print(f"Error initializing mixer: {e}")
        
        self.window = tk.Tk()
        self.window.title("CASIO Scientific Calculator")
        
        # Make calculator responsive
        self.window.minsize(400, 600)
        self.window.resizable(True, True)
        
        # Configure the main window to expand
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        # Initialize music player state
        self.is_playing = False
        self.current_music_index = 0
        self.music_files = []
        self.temp_file = None
        
        # Initialize other variables
        self.buttons = []
        self.is_dark_mode = True
        self.file_window = None
        
        # Setup encryption and file management
        self.setup_encryption()
        self.load_filename_map()
        
        # Add theme toggle
        self.add_theme_toggle()
        
        # Create main calculator frame
        self.calc_frame = ttk.Frame(self.window)
        self.calc_frame.pack(expand=True, fill='both', padx=15, pady=10)
        
        # Create calculator layout
        self.create_calculator_layout()
        
        # Apply initial theme
        self.apply_theme()
        
        # Bind cleanup on window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_calculator_layout(self):
        """Create a Casio-like calculator layout"""
        # Display frame with solar panel effect
        solar_frame = ttk.Frame(self.calc_frame)
        solar_frame.pack(fill='x', padx=10, pady=5)
        
        # Add solar panel effect
        solar_panel = tk.Canvas(
            solar_frame,
            height=20,
            bg='#1a1a1a',
            highlightthickness=1,
            highlightbackground='#333'
        )
        solar_panel.pack(fill='x', pady=(0, 5))
        
        # Main display with Casio styling
        display_frame = ttk.Frame(self.calc_frame)
        display_frame.pack(fill='x', padx=10, pady=5)
        
        self.display = tk.Entry(
            display_frame, 
            font=('Digital-7', 32),  # Calculator-like font
            justify='right',
            bd=8,
            relief=tk.SUNKEN,
            bg='#c8e6c9' if not self.is_dark_mode else '#1a1a1a',
            fg='#333333' if not self.is_dark_mode else '#00ff00',  # Calculator green text
            insertbackground='#333333' if not self.is_dark_mode else '#00ff00'
        )
        self.display.pack(fill='x', padx=5)
        
        # Button layout with Casio-like spacing
        buttons_frame = ttk.Frame(self.calc_frame)
        buttons_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Define button layout
        button_layout = [
            ['sin', 'cos', 'tan', 'log', '√'],
            ['(', ')', 'π', 'x²', 'x³'],
            ['7', '8', '9', '÷', 'C'],
            ['4', '5', '6', '×', '±'],
            ['1', '2', '3', '-', 'del'],
            ['0', '.', '=', '+', 'exp']
        ]
        
        # Casio-like button styles
        button_styles = {
            'font': ('Arial', 14, 'bold'),
            'width': 6,
            'height': 2,
            'bd': 4,
            'relief': tk.RAISED,
            'borderwidth': 2,
        }
        
        # Create buttons with improved styling
        for i, row in enumerate(button_layout):
            for j, text in enumerate(row):
                button = tk.Button(
                    buttons_frame,
                    text=text,
                    cursor='hand2',
                    command=lambda t=text: self.button_click(t),
                    **button_styles
                )
                button.grid(row=i, column=j, padx=3, pady=3, sticky='nsew')
                button.bind('<Enter>', lambda e, b=button: self.on_button_hover(b))
                button.bind('<Leave>', lambda e, b=button: self.on_button_leave(b))
                self.buttons.append(button)
        
        # Configure grid weights for responsive layout
        for i in range(6):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for j in range(5):
            buttons_frame.grid_columnconfigure(j, weight=1)

    def on_button_hover(self, button):
        """Add hover effect to buttons"""
        if self.is_dark_mode:
            button.configure(bg='#505050')
        else:
            text = button.cget('text')
            if text.isdigit() or text == '.':
                button.configure(bg='#0056b3')  # Darker blue on hover
            else:
                button.configure(bg='#cc7000')  # Darker orange on hover

    def on_button_leave(self, button):
        """Remove hover effect from buttons"""
        if self.is_dark_mode:
            button.configure(bg='#404040')
        else:
            text = button.cget('text')
            if text.isdigit() or text == '.':
                button.configure(bg='#007bff')  # Return to normal blue
            else:
                button.configure(bg='#ff8c00')  # Return to normal orange

    def button_click(self, value):
        """Handle button clicks"""
        if value == '=':
            try:
                # Get the current display content
                current_input = self.display.get()
                
                # Check if it might be a password attempt
                if current_input.isdigit() and 4 <= len(current_input) <= 8:
                    # Try to verify as password
                    if self.verify_password_from_display(current_input):
                        # Clear display after successful password attempt
                        self.display.delete(0, tk.END)
                        return
                
                # Replace special operators
                current_input = current_input.replace('×', '*').replace('÷', '/')
                
                # Handle special functions
                if 'sin' in current_input:
                    result = math.sin(eval(current_input.replace('sin', '')))
                elif 'cos' in current_input:
                    result = math.cos(eval(current_input.replace('cos', '')))
                elif 'tan' in current_input:
                    result = math.tan(eval(current_input.replace('tan', '')))
                elif 'log' in current_input:
                    result = math.log10(eval(current_input.replace('log', '')))
                elif '√' in current_input:
                    result = math.sqrt(eval(current_input.replace('√', '')))
                elif 'π' in current_input:
                    result = eval(current_input.replace('π', str(math.pi)))
                elif 'x²' in current_input:
                    num = eval(current_input.replace('x²', ''))
                    result = num ** 2
                elif 'x³' in current_input:
                    num = eval(current_input.replace('x³', ''))
                    result = num ** 3
                else:
                    result = eval(current_input)
                
                self.display.delete(0, tk.END)
                self.display.insert(tk.END, str(result))
            except:
                self.display.delete(0, tk.END)
                self.display.insert(tk.END, "Error")
        elif value == 'C':
            self.display.delete(0, tk.END)
        elif value == 'del':
            current = self.display.get()
            self.display.delete(0, tk.END)
            self.display.insert(0, current[:-1])
        elif value == '±':
            try:
                current = float(self.display.get())
                self.display.delete(0, tk.END)
                self.display.insert(0, str(-current))
            except:
                self.display.delete(0, tk.END)
                self.display.insert(tk.END, "Error")
        else:
            current = self.display.get()
            self.display.delete(0, tk.END)
            self.display.insert(tk.END, str(current) + str(value))

    def verify_password_from_display(self, entered_password):
        """Verify password entered in display"""
        try:
            # Initialize cipher suite if not already done
            if not hasattr(self, 'cipher_suite'):
                self.setup_encryption()
            
            # Check if password file exists
            if not hasattr(self, 'password_file'):
                self.password_file = os.path.join(self.private_dir, '.password')
            
            # If password file doesn't exist, create it with default password
            if not os.path.exists(self.password_file):
                default_password = "1234"  # Default password
                encrypted_password = self.cipher_suite.encrypt(default_password.encode())
                with open(self.password_file, 'wb') as f:
                    f.write(encrypted_password)
            
            # Read and verify password
            with open(self.password_file, 'rb') as f:
                stored_password = self.cipher_suite.decrypt(f.read()).decode()
            
            if entered_password == stored_password:
                # Show file manager
                self.show_file_manager()
                return True
            else:
                messagebox.showerror("Error", "Incorrect password!")
                return False
        except Exception as e:
            messagebox.showerror("Error", f"Error verifying password: {str(e)}")
            return False

    def show_file_manager(self):
        """Create or show file manager window"""
        if self.file_window is None or not tk.Toplevel.winfo_exists(self.file_window):
            self.file_window = tk.Toplevel(self.window)
            self.file_window.title("File Manager")
            self.file_window.geometry("800x600")
            
            # Add back button at the top
            back_frame = ttk.Frame(self.file_window)
            back_frame.pack(fill='x', padx=5, pady=5)
            
            back_button = ttk.Button(
                back_frame, 
                text="Back to Calculator",
                command=self.hide_file_manager
            )
            back_button.pack(side='left', padx=5)
            
            # Create notebook for tabs
            self.tab_control = ttk.Notebook(self.file_window)
            
            # Create tabs
            self.files_tab = ttk.Frame(self.tab_control)
            self.music_tab = ttk.Frame(self.tab_control)
            self.video_tab = ttk.Frame(self.tab_control)
            
            self.tab_control.add(self.files_tab, text='Files')
            self.tab_control.add(self.music_tab, text='Music Player')
            self.tab_control.add(self.video_tab, text='Video Player')
            self.tab_control.pack(expand=1, fill='both')
            
            # Setup tabs
            self.setup_files_tab()
            self.setup_music_tab()
            self.setup_video_tab()
            
            # Load existing files
            self.refresh_file_list()
            self.update_music_list()
            self.update_video_list()
            
            # Hide instead of destroy when closing
            self.file_window.protocol("WM_DELETE_WINDOW", self.hide_file_manager)
        else:
            self.file_window.deiconify()  # Show existing window

    def hide_file_manager(self):
        """Hide the file manager and show calculator"""
        if self.file_window:
            self.file_window.withdraw()  # Hide file manager
            self.window.deiconify()      # Show calculator

    def refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for encrypted_name, original_name in self.filename_map.items():
            self.file_listbox.insert(tk.END, original_name)

    def setup_encryption(self):
        # Create private directory if it doesn't exist
        self.private_dir = os.path.join(os.path.expanduser('~'), '.calculator_files')
        os.makedirs(self.private_dir, exist_ok=True)
        
        # Create or load encryption key
        key_file = os.path.join(self.private_dir, '.key')
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            # Generate a key
            salt = b'calculator_salt'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            self.key = base64.urlsafe_b64encode(kdf.derive(b'calculator_secret'))
            with open(key_file, 'wb') as f:
                f.write(self.key)
        
        self.cipher_suite = Fernet(self.key)

    def load_filename_map(self):
        map_file = os.path.join(self.private_dir, '.filemap')
        if os.path.exists(map_file):
            try:
                with open(map_file, 'r') as f:
                    self.filename_map = json.load(f)
            except:
                self.filename_map = {}
        else:
            self.filename_map = {}

    def save_filename_map(self):
        map_file = os.path.join(self.private_dir, '.filemap')
        with open(map_file, 'w') as f:
            json.dump(self.filename_map, f)

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All Files", "*.*"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Audio", "*.mp3 *.wav"),
                ("Video", "*.mp4 *.avi *.mkv"),
                ("Documents", "*.txt *.pdf *.doc *.docx")
            ]
        )
        if file_path:
            try:
                # Get original filename and generate encrypted filename
                original_filename = os.path.basename(file_path)
                encrypted_filename = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
                
                # Read and encrypt file content
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    encrypted_data = self.cipher_suite.encrypt(file_data)
                
                # Save encrypted file
                encrypted_path = os.path.join(self.private_dir, encrypted_filename)
                with open(encrypted_path, 'wb') as file:
                    file.write(encrypted_data)
                
                # Update filename map
                self.filename_map[encrypted_filename] = original_filename
                self.save_filename_map()
                
                # Refresh file list
                self.refresh_file_list()
                
                # Show success message
                tk.messagebox.showinfo("Success", f"File '{original_filename}' uploaded successfully!")
                
                # Delete original file if user confirms
                if tk.messagebox.askyesno("Delete Original", 
                                        "Do you want to delete the original file from your system?"):
                    try:
                        os.remove(file_path)
                        tk.messagebox.showinfo("Success", "Original file deleted successfully!")
                    except:
                        tk.messagebox.showwarning("Warning", 
                                                "Could not delete original file. Please delete it manually.")
                
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to upload file: {str(e)}")

    def view_image(self):
        selection = self.file_listbox.curselection()
        if selection:
            original_filename = self.file_listbox.get(selection[0])
            encrypted_filename = self.get_encrypted_filename(original_filename)
            
            if encrypted_filename and original_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                encrypted_path = os.path.join(self.private_dir, encrypted_filename)
                
                # Decrypt image data
                with open(encrypted_path, 'rb') as file:
                    encrypted_data = file.read()
                    decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                
                # Create image from decrypted data
                import io
                img = Image.open(io.BytesIO(decrypted_data))
                
                # Create new window for image
                img_window = tk.Toplevel(self.window)
                img_window.title(original_filename)
                
                # Resize if too large
                if img.width > 800 or img.height > 600:
                    img.thumbnail((800, 600))
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(img_window, image=photo)
                label.image = photo
                label.pack()

    def get_encrypted_filename(self, original_filename):
        for encrypted_name, orig_name in self.filename_map.items():
            if orig_name == original_filename:
                return encrypted_name
        return None

    def update_music_list(self):
        """Update the music listbox with available music files"""
        self.music_listbox.delete(0, tk.END)
        self.music_files = []
        for encrypted_name, original_name in self.filename_map.items():
            if original_name.lower().endswith(('.mp3', '.wav')):
                self.music_files.append((encrypted_name, original_name))
                self.music_listbox.insert(tk.END, original_name)

    def toggle_play(self):
        """Toggle play/pause for music"""
        if not hasattr(self, 'is_playing'):
            self.is_playing = False
        
        if not self.music_files:
            return
        
        try:
            if self.is_playing:
                pygame.mixer.music.pause()
                self.play_button.configure(text="▶")
                self.is_playing = False
            else:
                pygame.mixer.music.unpause()
                self.play_button.configure(text="⏸")
                self.is_playing = True
        except Exception as e:
            messagebox.showerror("Error", f"Playback error: {str(e)}")

    def play_current_track(self):
        """Play the current track"""
        if not self.music_files:
            self.playing_label.configure(text="No music files available")
            return
        
        try:
            encrypted_name, original_name = self.music_files[self.current_music_index]
            encrypted_path = os.path.join(self.private_dir, encrypted_name)
            
            # Create temporary decrypted file
            self.temp_file = os.path.join(self.private_dir, f'.temp_media_{os.urandom(4).hex()}')
            with open(encrypted_path, 'rb') as file:
                encrypted_data = file.read()
                decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            
            with open(self.temp_file, 'wb') as file:
                file.write(decrypted_data)
            
            pygame.mixer.music.load(self.temp_file)
            pygame.mixer.music.play()
            
            # Update playing label
            self.playing_label.configure(text=f"Now Playing: {original_name}")
            self.play_button.configure(text="⏸")
            self.is_playing = True
            
            # Setup end of track detection
            self.window.after(100, self.check_music_end)
            
        except Exception as e:
            self.playing_label.configure(text="Error playing track")
            messagebox.showerror("Error", f"Failed to play track: {str(e)}")

    def check_music_end(self):
        """Check if current track has ended"""
        if not pygame.mixer.music.get_busy() and self.is_playing:
            if self.repeat_var.get():
                self.play_current_track()
            else:
                # Automatically play next track
                self.next_track()
        if self.is_playing:
            self.window.after(100, self.check_music_end)

    def next_track(self):
        """Play next track"""
        if not self.music_files:
            return
        self.current_music_index = (self.current_music_index + 1) % len(self.music_files)
        self.play_current_track()

    def previous_track(self):
        """Play previous track"""
        if not self.music_files:
            return
        self.current_music_index = (self.current_music_index - 1) % len(self.music_files)
        self.play_current_track()
        self.play_button.configure(text="⏸")
        self.is_playing = True

    def remove_files(self):
        selections = self.file_listbox.curselection()
        if not selections:
            messagebox.showinfo("Info", "Please select files to remove")
            return
        
        files_to_remove = [self.file_listbox.get(i) for i in selections]
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to remove {len(files_to_remove)} selected file(s)?"):
            removed_count = 0
            for original_filename in files_to_remove:
                encrypted_filename = self.get_encrypted_filename(original_filename)
                
                if encrypted_filename:
                    try:
                        # Remove file from disk
                        file_path = os.path.join(self.private_dir, encrypted_filename)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        
                        # Remove from filename map
                        del self.filename_map[encrypted_filename]
                        removed_count += 1
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to remove {original_filename}: {str(e)}")
            
            # Save updated filename map
            self.save_filename_map()
            
            # Refresh all lists
            self.refresh_file_list()
            self.update_music_list()
            self.update_video_list()
            
            messagebox.showinfo("Success", f"Successfully removed {removed_count} file(s)")

    def remove_all_files(self):
        if not self.filename_map:
            messagebox.showinfo("Info", "No files to remove")
            return
        
        if messagebox.askyesno("Confirm Delete All", 
                              "Are you sure you want to remove ALL files? This cannot be undone!"):
            try:
                # Remove all files from disk
                for encrypted_filename in self.filename_map.keys():
                    file_path = os.path.join(self.private_dir, encrypted_filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                
                # Clear filename map
                self.filename_map.clear()
                self.save_filename_map()
                
                # Refresh all lists
                self.refresh_file_list()
                self.update_music_list()
                self.update_video_list()
                
                messagebox.showinfo("Success", "Successfully removed all files")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error removing files: {str(e)}")

    def update_video_list(self):
        if hasattr(self, 'video_listbox'):  # Check if video_listbox exists
            self.video_listbox.delete(0, tk.END)
            for encrypted_name, original_name in self.filename_map.items():
                if original_name.lower().endswith(('.mp4', '.avi', '.mkv')):
                    self.video_listbox.insert(tk.END, original_name)

    def play_video(self):
        selection = self.video_listbox.curselection()
        if selection:
            original_filename = self.video_listbox.get(selection[0])
            encrypted_filename = self.get_encrypted_filename(original_filename)
            
            if encrypted_filename:
                try:
                    # Create temporary decrypted file
                    temp_path = os.path.join(self.private_dir, f'.temp_video_{os.urandom(4).hex()}')
                    encrypted_path = os.path.join(self.private_dir, encrypted_filename)
                    
                    with open(encrypted_path, 'rb') as file:
                        encrypted_data = file.read()
                        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                    
                    with open(temp_path, 'wb') as file:
                        file.write(decrypted_data)
                    
                    # Open video with default player
                    os.startfile(temp_path)
                    
                    # Delete temp file after a delay
                    self.window.after(2000, lambda: os.remove(temp_path) if os.path.exists(temp_path) else None)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to play video: {str(e)}")

    def cleanup_temp_file(self):
        """Clean up temporary media file if it exists"""
        if hasattr(self, 'temp_file') and self.temp_file:
            try:
                if os.path.exists(self.temp_file):
                    os.remove(self.temp_file)
                self.temp_file = None
            except Exception:
                pass

    def __del__(self):
        """Destructor to clean up resources"""
        self.cleanup_temp_file()

    def add_theme_toggle(self):
        """Add theme toggle button to calculator"""
        # Create a frame for the theme button and branding
        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill='x', padx=5, pady=5)
        
        # Add WILSONBOI branding
        brand_label = tk.Label(
            top_frame,
            text="WILSONBOI",
            font=('Arial', 12, 'bold'),
            fg='#ff8c00'
        )
        brand_label.pack(side='right', padx=10)
        
        # Add theme toggle button
        theme_button = ttk.Button(
            top_frame,
            text="🌙" if self.is_dark_mode else "☀️",
            width=3,
            command=self.toggle_theme
        )
        theme_button.pack(side='left', padx=5)
        self.theme_button = theme_button

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.is_dark_mode = not self.is_dark_mode
        self.theme_button.configure(text="🌙" if self.is_dark_mode else "☀️")
        self.apply_theme()

    def apply_theme(self):
        """Apply enhanced Casio-like theme"""
        if self.is_dark_mode:
            bg_color = '#2b2b2b'
            button_bg = '#404040'
            button_fg = 'white'
            entry_bg = '#1a1a1a'
            entry_fg = '#00ff00'  # Calculator green
        else:
            bg_color = '#e0e0e0'
            digit_bg = '#007bff'
            operator_bg = '#ff8c00'
            entry_bg = '#c8e6c9'  # Light green display
            entry_fg = '#333333'
        
        # Configure window
        self.window.configure(bg=bg_color)
        
        # Configure display
        self.display.configure(
            bg=entry_bg,
            fg=entry_fg,
            insertbackground=entry_fg
        )
        
        # Configure buttons
        for button in self.buttons:
            if isinstance(button, tk.Button):
                text = button.cget('text')
                if text.isdigit() or text == '.':
                    if self.is_dark_mode:
                        button.configure(
                            bg=button_bg,
                            fg=button_fg,
                            activebackground='#505050',
                            activeforeground='white'
                        )
                    else:
                        button.configure(
                            bg=digit_bg,
                            fg='white',
                            activebackground='#0056b3',
                            activeforeground='white'
                        )
                else:
                    if self.is_dark_mode:
                        button.configure(
                            bg=button_bg,
                            fg=button_fg,
                            activebackground='#505050',
                            activeforeground='white'
                        )
                    else:
                        button.configure(
                            bg=operator_bg,
                            fg='white',
                            activebackground='#cc7000',
                            activeforeground='white'
                        )

    def create_button(self, text, row, col, rowspan=1, colspan=1):
        """Create a calculator button with theme support"""
        button = tk.Button(
            self.window,
            text=text,
            width=5,
            height=2,
            font=('Arial', 12),
            command=lambda: self.button_click(text)
        )
        button.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, padx=2, pady=2)
        self.buttons.append(button)
        return button

    def setup_video_tab(self):
        """Create video player tab"""
        # Video list frame
        list_frame = ttk.Frame(self.video_tab)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Video list label
        ttk.Label(list_frame, text="Video Library", font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        
        # Video list with scrollbar
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side='right', fill='y')
        
        self.video_listbox = tk.Listbox(list_frame, width=70, height=15, 
                                       font=('Arial', 10),
                                       yscrollcommand=list_scroll.set)
        self.video_listbox.pack(side='left', fill='both', expand=True)
        list_scroll.config(command=self.video_listbox.yview)
        
        # Video controls frame
        controls_frame = ttk.Frame(self.video_tab)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        # Current video label
        self.video_label = ttk.Label(controls_frame, 
                                    text="No video selected", 
                                    font=('Arial', 11))
        self.video_label.pack(pady=5)
        
        # Play button
        ttk.Button(controls_frame, 
                   text="Play Video", 
                   command=self.play_video).pack(pady=5)

    def setup_files_tab(self):
        """Create files tab"""
        # File operations frame
        file_ops = ttk.Frame(self.files_tab)
        file_ops.pack(fill='x', padx=5, pady=5)
        
        # Buttons for file operations
        ttk.Button(file_ops, text="Upload File", command=self.upload_file).pack(side='left', padx=5)
        ttk.Button(file_ops, text="View Image", command=self.view_image).pack(side='left', padx=5)
        ttk.Button(file_ops, text="Export to System", command=self.export_files).pack(side='left', padx=5)
        ttk.Button(file_ops, text="Delete", command=self.delete_files).pack(side='left', padx=5)
        ttk.Button(file_ops, text="Delete All", command=self.delete_all_files).pack(side='left', padx=5)
        
        # File list with scrollbar
        list_frame = ttk.Frame(self.files_tab)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.file_listbox = tk.Listbox(
            list_frame,
            width=70,
            height=20,
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set
        )
        self.file_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.file_listbox.yview)

    def setup_music_tab(self):
        """Create music player tab"""
        # Music list frame
        list_frame = ttk.Frame(self.music_tab)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Music list label
        ttk.Label(list_frame, text="Music Library", font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        
        # Music list with scrollbar
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side='right', fill='y')
        
        self.music_listbox = tk.Listbox(list_frame, width=70, height=15,
                                       font=('Arial', 10),
                                       yscrollcommand=list_scroll.set)
        self.music_listbox.pack(side='left', fill='both', expand=True)
        list_scroll.config(command=self.music_listbox.yview)
        
        # Bind single-click event to play selected song
        self.music_listbox.bind('<<ListboxSelect>>', self.play_selected_song)
        
        # Music controls frame
        controls_frame = ttk.Frame(self.music_tab)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        # Playing label
        self.playing_label = ttk.Label(controls_frame, 
                                      text="No track playing", 
                                      font=('Arial', 11))
        self.playing_label.pack(pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(pady=5)
        
        # Previous button
        ttk.Button(buttons_frame, 
                   text="⏮", 
                   width=3,
                   command=self.previous_track).pack(side='left', padx=5)
        
        # Play/Pause button
        self.play_button = ttk.Button(buttons_frame, 
                                     text="▶", 
                                     width=3,
                                     command=self.toggle_play)
        self.play_button.pack(side='left', padx=5)
        
        # Next button
        ttk.Button(buttons_frame, 
                   text="⏭", 
                   width=3,
                   command=self.next_track).pack(side='left', padx=5)
        
        # Repeat checkbox
        self.repeat_var = tk.BooleanVar()
        ttk.Checkbutton(buttons_frame, 
                        text="Repeat", 
                        variable=self.repeat_var).pack(side='left', padx=5)

    def play_selected_song(self, event=None):
        """Play song when selected from list"""
        if not self.music_listbox.curselection():
            return
        
        try:
            # Ensure mixer is initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100)
            
            # Update current index
            self.current_music_index = self.music_listbox.curselection()[0]
            
            # Stop current playback if any
            try:
                pygame.mixer.music.stop()
            except:
                pass
            
            # Play selected track
            self.play_current_track()
            
            # Update button state
            self.play_button.configure(text="⏸")
            self.is_playing = True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play track: {str(e)}")

    def export_files(self):
        """Export selected files back to system"""
        selections = self.file_listbox.curselection()
        if not selections:
            messagebox.showinfo("Info", "Please select files to export")
            return
        
        # Ask for export directory
        export_dir = filedialog.askdirectory(title="Select Export Location")
        if not export_dir:
            return
        
        exported_count = 0
        for index in selections:
            original_filename = self.file_listbox.get(index)
            encrypted_filename = self.get_encrypted_filename(original_filename)
            
            if encrypted_filename:
                try:
                    # Read and decrypt file
                    encrypted_path = os.path.join(self.private_dir, encrypted_filename)
                    with open(encrypted_path, 'rb') as file:
                        encrypted_data = file.read()
                        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                    
                    # Save decrypted file to export location
                    export_path = os.path.join(export_dir, original_filename)
                    with open(export_path, 'wb') as file:
                        file.write(decrypted_data)
                    
                    exported_count += 1
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export {original_filename}: {str(e)}")
        
        if exported_count > 0:
            messagebox.showinfo("Success", 
                              f"Successfully exported {exported_count} file(s) to:\n{export_dir}")
        else:
            messagebox.showwarning("Warning", "No files were exported")

    def delete_files(self):
        selections = self.file_listbox.curselection()
        if not selections:
            messagebox.showinfo("Info", "Please select files to delete")
            return
        
        files_to_delete = [self.file_listbox.get(i) for i in selections]
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to permanently delete {len(files_to_delete)} selected file(s)?\n\nThis action cannot be undone!"):
            deleted_count = 0
            for original_filename in files_to_delete:
                encrypted_filename = self.get_encrypted_filename(original_filename)
                
                if encrypted_filename:
                    try:
                        # Remove file from disk
                        file_path = os.path.join(self.private_dir, encrypted_filename)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        
                        # Remove from filename map
                        del self.filename_map[encrypted_filename]
                        deleted_count += 1
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete {original_filename}: {str(e)}")
            
            # Save updated filename map
            self.save_filename_map()
            
            # Refresh all lists
            self.refresh_file_list()
            self.update_music_list()
            self.update_video_list()
            
            messagebox.showinfo("Success", f"Successfully deleted {deleted_count} file(s)")

    def delete_all_files(self):
        if not self.filename_map:
            messagebox.showinfo("Info", "No files to delete")
            return
        
        if messagebox.askyesno("Confirm Delete All", 
                              "Are you sure you want to permanently delete ALL files?\n\nThis action cannot be undone!"):
            try:
                # Remove all files from disk
                for encrypted_filename in self.filename_map.keys():
                    file_path = os.path.join(self.private_dir, encrypted_filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                
                # Clear filename map
                self.filename_map.clear()
                self.save_filename_map()
                
                # Refresh all lists
                self.refresh_file_list()
                self.update_music_list()
                self.update_video_list()
                
                messagebox.showinfo("Success", "Successfully deleted all files")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting files: {str(e)}")

    def show_offline_status(self):
        """Show offline mode confirmation"""
        status_label = ttk.Label(
            self.window,
            text="✓ Running in Offline Mode",
            font=('Helvetica', 10),
            foreground='green'
        )
        status_label.pack(anchor='ne', padx=5, pady=2)
        
        # Auto-hide after 3 seconds
        self.window.after(3000, status_label.destroy)

    def on_closing(self):
        """Clean up resources before closing"""
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except:
            pass
        
        self.cleanup_temp_file()
        self.window.destroy()

if __name__ == "__main__":
    calculator = ScientificCalculator()
    calculator.window.mainloop()
    
