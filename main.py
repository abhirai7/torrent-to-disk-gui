import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox, filedialog
import asyncio
import libtorrent as lt
import threading

download_active = True  # Flag to control download state

async def download_torrent(magnet_link, save_path='/home/abhishek/D/Torrent-to-Disk'):
    global download_active
    ses = lt.session()
    ses.listen_on(6881, 6891)  # Fallback for port configuration

    # Parse the magnet link and configure torrent parameters
    params = lt.parse_magnet_uri(magnet_link)
    params.save_path = save_path
    handle = ses.add_torrent(params)

    download_active = True

    # Wait for metadata asynchronously
    while not handle.status().has_metadata:
        await asyncio.sleep(1)

    # Start the download loop
    await download_loop(handle)

async def download_loop(handle):
    global download_active
    while download_active and handle.status().state != lt.torrent_status.seeding:
        status = handle.status()
        progress = status.progress * 100
        download_rate = status.download_rate / 1000  # kB/s
        upload_rate = status.upload_rate / 1000  # kB/s
        num_peers = status.num_peers
        
        print(f"Downloading: {progress:.2f}% complete "
              f"(down: {download_rate:.2f} kB/s, up: {upload_rate:.2f} kB/s, peers: {num_peers})")

        # Update the progress bar and percentage label
        progress_bar['value'] = progress
        progress_label.config(text=f"Download Progress: {progress:.2f}%")
        speed_label.config(text=f"Download : {download_rate:.2f}kB/s       Upload : {upload_rate:.2f}kB/s           peers : {num_peers}")

        window.update_idletasks()  # Force update of the GUI

        await asyncio.sleep(1)

    if not download_active:
        return 
    # When download completes
    progress_label.config(text="Download Complete!")
    window.update_idletasks()

# Function to start download in the Tkinter GUI
def start_download():
    magnet_link = link_input.get()  # Get the link from the input box
    if magnet_link:
        # Reset the progress bar and label
        progress_bar['value'] = 0
        progress_label.config(text="Download Progress: 0.00%")
        speed_label.config(text="Download : 0kB/s       Upload : 0kB/s           peers : 0")
        # Start the asyncio loop in a separate thread to prevent blocking the GUI
        threading.Thread(target=lambda: asyncio.run(download_torrent(magnet_link, save_path_var.get()))).start()
    else:
        messagebox.showwarning("Input Error", "Please enter a valid torrent/magnet link.")

def choose_save_path():
    path = filedialog.askdirectory()
    if path:
        save_path_var.set(path)

# Function to stop the download
def stop_download():
    global download_active
    download_active = False  # Stop the download loop
    progress_label.config(text="Download Stopped")
    progress_bar['value'] = 0

# Create the main window using ttkbootstrap's theme support
window = ttk.Window(themename="darkly")  # You can change the theme if needed
window.title("Torrent Downloader")
window.geometry("900x600")

window_width = 900
window_height = 600
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculate the x and y coordinates for the window to be centered
x_coordinate = (screen_width // 2) - (window_width // 2)
y_coordinate = (screen_height // 2) - (window_height // 2)

window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

save_path_var = tk.StringVar()

# Custom style for widgets
style = ttk.Style()
style.configure("Custom.TButton", font=("Helvetica", 12, "bold"), padding=10)
style.configure("Custom.TLabel", font=("Helvetica", 14))

# Create a frame to center the widgets
frame = ttk.Frame(window)
frame.pack(expand=True, fill="both", padx=20, pady=30)

header = ttk.Label(frame, text="Torrent to Disk", bootstyle=INFO, font=("Helvetica", 24, "bold"),
                     relief="flat", borderwidth=0, anchor="center", width=30, justify="center")
header.pack(pady=10)

separator = ttk.Separator(frame, orient="horizontal")
separator.pack(fill="x", pady=10, expand=True)

# Create the input label
label = ttk.Label(frame, text="Enter Torrent/Magnet Link:", bootstyle=PRIMARY, font=("Helvetica", 16, "bold"), 
                  relief="flat", borderwidth=0, anchor="center", width=30, justify="center")
label.pack(pady=10)

# Create the input field with enhanced styling
link_input = ttk.Entry(frame, width=50, bootstyle="success", font=("Helvetica", 14), justify="center", background="white")
link_input.pack(pady=10)

# Button to choose save path
choose_path_button = ttk.Button(frame, text="Choose Save Path", command=choose_save_path, bootstyle=PRIMARY)
choose_path_button.pack(pady=5)

# Label to show chosen save path
save_path_label = ttk.Label(frame, textvariable=save_path_var, font=("Helvetica", 12), bootstyle=INFO)
save_path_label.pack(pady=5)

# Create the download button with custom style applied
download_button = ttk.Button(
    frame, 
    text="Download", 
    command=start_download, 
    bootstyle=SUCCESS,  # Use success style for a green button
    style="Custom.TButton",  # Apply the custom style
    width=20,
)
download_button.pack(pady=10)

stop_button = ttk.Button(
    frame, 
    text="Stop", 
    command=stop_download, 
    bootstyle=DANGER,  # Use danger style for a red button
    style="Custom.TButton",  # Apply the custom style
    width=20,
)
stop_button.pack(pady=5)

# Enhanced Progress Bar
progress_bar = ttk.Progressbar(
    frame, 
    bootstyle="info-striped",  # Gives a striped look for more visual appeal
    length=400, 
    mode="determinate", 
    orient="horizontal",
    maximum=100
)
progress_bar.pack(pady=10)

# Increase the height of the progress bar for better visibility
progress_bar.configure(style="custom.Horizontal.TProgressbar")
style.configure("custom.Horizontal.TProgressbar", thickness=30)

# Label to display download progress percentage
progress_label = ttk.Label(frame, text="Download Progress: 0.00%", style="Custom.TLabel")
progress_label.pack(pady=10)

# Label to show download/upload speed and peers info
speed_label = ttk.Label(
    frame, 
    text="Download: 0 kB/s       Upload: 0 kB/s       Peers: 0", 
    font=("Monospace", 12), 
    bootstyle=INFO
)
speed_label.pack(pady=5)

# Run the Tkinter event loop
window.mainloop()
