import tkinter as tk
from tkinter import ttk, scrolledtext
import os
from datetime import datetime
import time
from main import setup_elevenlabs, text_to_speech, play_audio
from database import Database

class TextToSpeechGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ElevenLabs Text to Speech")
        self.root.geometry("1200x600")
        
        # Initialize database
        self.db = Database()
        
        # Initialize ElevenLabs client
        self.client = setup_elevenlabs()
        
        # Create main container
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.main_container.columnconfigure(0, weight=1)    # Input area
        self.main_container.columnconfigure(1, weight=2)    # Chat area (reduced from 3)
        self.main_container.columnconfigure(2, weight=2)    # History area (increased from 1)
        self.main_container.rowconfigure(0, weight=1)
        
        # Left side - Input area
        self.create_input_area()
        
        # Middle - Chat display area
        self.create_chat_area()
        
        # Right side - History area
        self.create_history_area()
        
        # Configure root grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Store audio files and their messages
        self.audio_messages = []
        
        # Load saved voice preference
        saved_voice = self.db.get_setting('last_voice', 'Aria')
        self.voice_var.set(saved_voice)
        
        # Bind cleanup to window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_input_area(self):
        """Create the left side input area."""
        input_frame = ttk.LabelFrame(self.main_container, text="Input", padding="5")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Voice selection
        ttk.Label(input_frame, text="Voice:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.voice_var = tk.StringVar(value="Aria")
        self.voice_combo = ttk.Combobox(input_frame, textvariable=self.voice_var)
        self.voice_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.update_voice_list()
        
        # Text input
        ttk.Label(input_frame, text="Text to convert:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.text_input = scrolledtext.ScrolledText(input_frame, width=30, height=10)
        self.text_input.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Convert button
        self.convert_button = ttk.Button(input_frame, text="Convert to Speech", command=self.convert_text)
        self.convert_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        input_frame.columnconfigure(1, weight=1)
        input_frame.rowconfigure(2, weight=1)

    def create_chat_area(self):
        """Create the middle chat display area."""
        chat_frame = ttk.LabelFrame(self.main_container, text="Messages", padding="5")
        chat_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD)
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)

    def create_history_area(self):
        """Create the right side history area."""
        history_frame = ttk.LabelFrame(self.main_container, text="Saved Audio", padding="5")
        history_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # History display
        self.history_display = ttk.Frame(history_frame)
        self.history_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Load history
        self.load_history()

    def load_history(self):
        """Load and display the audio history."""
        # Clear existing history display
        for widget in self.history_display.winfo_children():
            widget.destroy()
        
        # Get history entries
        entries = self.db.get_audio_history()
        
        # Create a frame for each entry
        for text, audio_file, voice_name, created_at in entries:
            entry_frame = ttk.Frame(self.history_display)
            entry_frame.pack(fill=tk.X, pady=2, padx=5)
            
            # Truncate text to 16 characters
            truncated_text = text[:16] + "..." if len(text) > 16 else text
            
            # Add play button (narrower)
            play_button = ttk.Button(entry_frame, text="▶", width=1,
                                   command=lambda f=audio_file: play_audio(f))
            play_button.pack(side=tk.LEFT, padx=2)
            
            # Add text label
            text_label = ttk.Label(entry_frame, text=truncated_text, wraplength=150)
            text_label.pack(side=tk.LEFT, padx=2)
            
            # Add delete button (narrower)
            delete_button = tk.Button(entry_frame, text="❌", width=1,
                                    command=lambda f=audio_file: self.delete_audio(f),
                                    bg='#FFB6C1',  # Light red color
                                    relief='raised')
            delete_button.pack(side=tk.RIGHT, padx=2)

    def update_voice_list(self):
        """Update the voice selection dropdown with available voices."""
        try:
            response = self.client.voices.get_all()
            voices = [voice.name for voice in response.voices]
            self.voice_combo['values'] = voices
        except Exception as e:
            self.add_message(f"Error loading voices: {str(e)}")

    def add_message(self, message, is_audio=False, audio_file=None, original_text=None):
        """Add a message to the chat display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] {message}\n")
        
        if is_audio and audio_file:
            # Create a frame for the audio message
            audio_frame = ttk.Frame(self.chat_display)
            self.chat_display.window_create(tk.END, window=audio_frame)
            
            # Add the audio file name
            ttk.Label(audio_frame, text=f"Audio file: {os.path.basename(audio_file)}").pack(side=tk.LEFT, padx=5)
            
            # Add play button
            play_button = ttk.Button(audio_frame, text="Play Again", 
                                   command=lambda: play_audio(audio_file))
            play_button.pack(side=tk.LEFT, padx=5)
            
            # Add save button
            self.save_button = ttk.Button(audio_frame, text="Save", 
                                        command=lambda f=audio_file, t=original_text: self.save_audio(t, f))
            self.save_button.pack(side=tk.LEFT, padx=5)
            
            # Add newline after the audio message
            self.chat_display.insert(tk.END, "\n")
        
        # Scroll to the bottom
        self.chat_display.see(tk.END)
        # Update the GUI
        self.root.update()

    def update_message(self, message, delay=0.2, is_audio=False, audio_file=None, original_text=None):
        """Update a message with a delay and GUI update."""
        self.add_message(message, is_audio=is_audio, audio_file=audio_file, original_text=original_text)
        time.sleep(delay)

    def save_audio(self, text, audio_file):
        """Save the audio entry to the database."""
        try:
            self.db.save_audio_entry(text, audio_file, self.voice_var.get())
            self.load_history()  # Refresh the history display
            
            # Update save button text
            self.save_button.configure(text="Saved")
            
        except Exception as e:
            self.add_message(f"Error saving audio: {str(e)}")

    def delete_audio(self, audio_file):
        """Delete an audio entry from the database only."""
        try:
            # Delete from database
            self.db.delete_audio_entry(audio_file)
            
            # Refresh the history display
            self.load_history()
            
        except Exception as e:
            self.add_message(f"Error deleting audio: {str(e)}")

    def convert_text(self):
        """Convert the input text to speech."""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            self.add_message("Please enter some text to convert.")
            return
        
        # Save the selected voice preference
        self.db.set_setting('last_voice', self.voice_var.get())
        
        # Disable the convert button while processing
        self.convert_button.state(['disabled'])
        
        try:
            # Add the input text to the chat (truncated to 16 characters)
            truncated_text = text[:16] + "..." if len(text) > 16 else text
            self.update_message(f"Converting text: {truncated_text}")
            
            # Add generating message
            self.update_message("Generating audio...")
            
            # Convert text to speech
            audio_file = text_to_speech(self.client, text, self.voice_var.get())
            
            # Add success message and audio file
            self.update_message("Audio generated successfully!", is_audio=True, audio_file=audio_file, original_text=text)
            
            # Play the audio (without showing message)
            play_audio(audio_file)
            
        except Exception as e:
            self.add_message(f"Error: {str(e)}")
        
        finally:
            # Re-enable the convert button
            self.convert_button.state(['!disabled'])
            
            # Clear the input field
            self.text_input.delete("1.0", tk.END)

    def on_closing(self):
        """Handle window closing event."""
        self.cleanup_audio_files()
        self.root.destroy()

    def cleanup_audio_files(self):
        """Delete all audio files that are not stored in the database."""
        try:
            # Get all audio files from database
            entries = self.db.get_audio_history()
            saved_files = {os.path.relpath(entry[1]) for entry in entries}  # Set of relative saved file paths
            
            # Get all files in output directory
            output_dir = "output"
            if os.path.exists(output_dir):
                for filename in os.listdir(output_dir):
                    if filename.endswith(".mp3"):
                        file_path = os.path.join(output_dir, filename)
                        # Delete file if it's not in the database
                        if file_path not in saved_files:
                            try:
                                os.remove(file_path)
                                print(f"Deleted unsaved file: {filename}")
                            except Exception as e:
                                print(f"Error deleting file {filename}: {str(e)}")
                                
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

def main():
    root = tk.Tk()
    app = TextToSpeechGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 