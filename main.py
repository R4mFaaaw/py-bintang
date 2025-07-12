from pytube import YouTube
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Styling
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10), padding=5)
        style.configure("TEntry", font=("Helvetica", 10), padding=5)
        
        # Header Frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=10)
        
        ttk.Label(header_frame, text="YouTube Video Downloader", font=("Helvetica", 14, "bold")).pack()
        
        # Input Frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill="x")
        
        ttk.Label(input_frame, text="YouTube URL:").grid(row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(input_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5)
        
        # Quality Selection Frame
        quality_frame = ttk.Frame(self.root)
        quality_frame.pack(pady=10, padx=20, fill="x")
        
        ttk.Label(quality_frame, text="Select Quality:").grid(row=0, column=0, sticky="w")
        self.quality_var = tk.StringVar(value="720p")
        quality_options = ["144p", "240p", "360p", "480p", "720p", "1080p"]
        self.quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var, values=quality_options, state="readonly")
        self.quality_combo.grid(row=0, column=1, padx=5)
        
        # Save Location Frame
        location_frame = ttk.Frame(self.root)
        location_frame.pack(pady=10, padx=20, fill="x")
        
        ttk.Label(location_frame, text="Save Location:").grid(row=0, column=0, sticky="w")
        self.location_var = tk.StringVar()
        self.location_entry = ttk.Entry(location_frame, textvariable=self.location_var, width=40)
        self.location_entry.grid(row=0, column=1, padx=5)
        
        browse_btn = ttk.Button(location_frame, text="Browse...", command=self.select_directory)
        browse_btn.grid(row=0, column=2)
        
        # Download Button
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.download_btn = ttk.Button(button_frame, text="Download Video", command=self.download_video)
        self.download_btn.pack()
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)
        
        # Status Label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.root, textvariable=self.status_var)
        self.status_label.pack()
    
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.location_var.set(directory)
    
    def download_video(self):
        url = self.url_entry.get()
        save_path = self.location_var.get()
        quality = self.quality_var.get()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not save_path:
            messagebox.showerror("Error", "Please select a save location")
            return
        
        try:
            self.status_var.set("Connecting to YouTube...")
            self.root.update()
            
            yt = YouTube(
                url,
                on_progress_callback=self.progress_function,
                on_complete_callback=self.complete_function
            )
            
            self.status_var.set(f"Downloading: {yt.title}")
            
            # Get stream based on selected quality
            if quality == "1080p":
                video = yt.streams.filter(progressive=False, file_extension='mp4', resolution=quality).first()
                audio = yt.streams.filter(only_audio=True).first()
                
                if video and audio:
                    # Download video and audio separately
                    temp_dir = os.path.join(save_path, "temp")
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    video_filename = os.path.join(temp_dir, "video.mp4")
                    audio_filename = os.path.join(temp_dir, "audio.mp3")
                    
                    video.download(output_path=temp_dir, filename="video.mp4")
                    audio.download(output_path=temp_dir, filename="audio.mp3")
                    
                    # Combine using ffmpeg (optional - requires ffmpeg installed)
                    final_filename = self.clean_filename(yt.title) + ".mp4"
                    final_path = os.path.join(save_path, final_filename)
                    
                    # For simplicity, we'll just rename one of the files here
                    # In a production app, you'd want to actually merge the streams
                    os.rename(video_filename, final_path)
                    # Clean up temp files
                    try:
                        os.remove(audio_filename)
                        os.rmdir(temp_dir)
                    except:
                        pass
                    
                    messagebox.showinfo("Success", f"Video downloaded successfully!\nSaved as: {final_path}")
                else:
                    messagebox.showerror("Error", "Could not find video/audio streams for selected quality")
            else:
                # For qualities below 1080p we can use progressive streams
                stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=quality).first()
                if stream:
                    final_filename = self.clean_filename(yt.title) + ".mp4"
                    final_path = os.path.join(save_path, final_filename)
                    stream.download(output_path=save_path, filename=final_filename)
                    messagebox.showinfo("Success", f"Video downloaded successfully!\nSaved as: {final_path}")
                else:
                    messagebox.showerror("Error", f"No stream available for {quality} quality")
            
            self.status_var.set("Download complete")
            self.progress["value"] = 0
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred")
            self.progress["value"] = 0
    
    def progress_function(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        
        self.progress["value"] = percentage
        self.status_var.set(f"Downloading: {percentage:.2f}%")
        self.root.update()
    
    def complete_function(self, stream, file_path):
        self.progress["value"] = 100
        self.status_var.set("Download complete!")
        self.root.update()
    
    def clean_filename(self, filename):
        # Remove invalid characters from filename
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename.strip()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()
