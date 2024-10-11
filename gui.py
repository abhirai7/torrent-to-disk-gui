import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap import PRIMARY, SECONDARY, SUCCESS, DANGER, WARNING, INFO, LIGHT, DARK
from torrent import TorrentDownloader
import asyncio
import threading

class GUI:
    def __init__(self, window):
        self.window = window
        self.torrent_downloader = TorrentDownloader()
        self.save_path_var = tk.StringVar()
        self.progress_bar = None
        self.progress_label = None
        self.speed_label = None
        self.seed_leecher_label = None
        self.file_name_label = None
        self.downloaded_size_label = None
        self.download_task = None

        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("Custom.TButton", font=("Helvetica", 12, "bold"), padding=10)
        style.configure("Custom.TLabel", font=("Helvetica", 14))

        frame = ttk.Frame(self.window)
        frame.pack(expand=True, fill="both", padx=20, pady=30)

        header = ttk.Label(frame, text="Torrent to Disk", bootstyle=INFO, font=("Helvetica", 24, "bold"),
                           relief="flat", borderwidth=0, anchor="center", width=30, justify="center")
        header.pack(pady=10)

        separator = ttk.Separator(frame, orient="horizontal")
        separator.pack(fill="x", pady=10, expand=True)

        label = ttk.Label(frame, text="Enter Torrent/Magnet Link:", bootstyle=PRIMARY, font=("Helvetica", 16, "bold"),
                          relief="flat", borderwidth=0, anchor="center", width=30, justify="center")
        label.pack(pady=10)

        self.link_input = ttk.Entry(frame, width=50, bootstyle="success", font=("Helvetica", 14), justify="center", background="white")
        self.link_input.pack(pady=10)

        choose_path_button = ttk.Button(frame, text="Choose Save Path", command=self.choose_save_path, bootstyle=PRIMARY)
        choose_path_button.pack(pady=5)

        save_path_label = ttk.Label(frame, textvariable=self.save_path_var, font=("Helvetica", 12), bootstyle=INFO)
        save_path_label.pack(pady=5)

        self.download_button = ttk.Button(
            frame, 
            text="Download", 
            command=self.start_download, 
            bootstyle=SUCCESS,  # Use success style for a green button
            style="Custom.TButton",  # Apply the custom style
            width=20,
        )
        self.download_button.pack(pady=10)

        stop_button = ttk.Button(
            frame, 
            text="Stop", 
            command=self.stop_download, 
            bootstyle=DANGER,  # Use danger style for a red button
            style=" Custom.TButton",  # Apply the custom style
            width=20,
        )
        stop_button.pack(pady=5)

        self.progress_bar = ttk.Progressbar(
            frame, 
            bootstyle="info-striped",  # Gives a striped look for more visual appeal
            length=400,
        )
        self.progress_bar.pack(pady=10)

        self.progress_label = ttk.Label(frame, text="Progress: 0%", font=("Helvetica", 12), bootstyle=INFO)
        self.progress_label.pack(pady=5)

        self.speed_label = ttk.Label(frame, text="Down Speed: 0 kB/s              Up Speed: 0 kB/s", font=("Helvetica", 12), bootstyle=INFO)
        self.speed_label.pack(pady=5)

        self.seed_leecher_label = ttk.Label(frame, text="Seeds: 0         Leechers: 0       Peers: 0", font=("Helvetica", 12), bootstyle=INFO)
        self.seed_leecher_label.pack(pady=5)

        self.file_name_label = ttk.Label(frame, text="File Name: ", font=("Helvetica", 12), bootstyle=INFO)
        self.file_name_label.pack(pady=5)

        self.downloaded_size_label = ttk.Label(frame, text="Downloaded: 0 bytes", font=("Helvetica", 12), bootstyle=INFO)
        self.downloaded_size_label.pack(pady=5)

    def start_download(self):
        magnet_link = self.link_input.get()
        if magnet_link:
            self.download_button.config(state="disabled")
            self.download_task = threading.Thread(target=lambda: asyncio.run(self.download_torrent(magnet_link, self.save_path_var.get())))
            self.download_task.start()
        else:
            messagebox.showwarning("Input Error", "Please enter a valid torrent/magnet link.")

    async def download_torrent(self, magnet_link, save_path):
        self.torrent_downloader = TorrentDownloader(save_path)
        async for file_name, progress, download_rate, upload_rate, num_peers, num_seeds, num_leechers, downloaded_bytes, total_size in self.torrent_downloader.download_torrent(magnet_link):
            self.window.after(0, self.update_gui, file_name, progress, download_rate, upload_rate, num_peers, num_seeds, num_leechers, downloaded_bytes, total_size)

    def update_gui(self, file_name, progress, download_rate, upload_rate, num_peers, num_seeds, num_leechers, downloaded_bytes, total_size):
        self.progress_bar['value'] = progress
        self.progress_label['text'] = f"Progress: {progress:.2f}%"
        self.speed_label['text'] = f"Down Speed: {download_rate:.2f} kB/s              Up Speed: {upload_rate:.2f} kB/s"
        self.seed_leecher_label['text'] = f"Seeds: {num_seeds}         Leechers: {num_leechers}       Peers: {num_peers}"
        self.file_name_label['text'] = f"File Name: {file_name}"
        self.downloaded_size_label['text'] = f"Downloaded: {self.format_size(downloaded_bytes)} / {self.format_size(total_size)}"
        self.window.update_idletasks()  # Force update of the GUI

    def stop_download(self):
        if self.download_task:
            self.torrent_downloader.stop_download()
            self.download_button.config(state="normal")
            self.download_task = None
        


    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes / 1024**2:.2f} MB"
        else:
            return f"{size_bytes / 1024**3:.2f} GB"
        

    def choose_save_path(self):
        save_path = filedialog.askdirectory()
        self.save_path_var.set(save_path)


if __name__ == "__main__":
    window = ttk.Window(themename="darkly")  # You can change the theme if needed
    window.title("Torrent to Disk")
    window_width = 600
    window_height = 600
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the x and y coordinates for the window to be centered
    x_coordinate = (screen_width // 2) - (window_width // 2)
    y_coordinate = (screen_height // 2) - (window_height // 2)

    window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    gui = GUI(window)
    window.mainloop()