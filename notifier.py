import tkinter as tk
from threading import Thread
import time

def show_toast(message, duration=3.0):
    """
    Displays a premium, centered green toast notification.
    """
    def create_window():
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.0)
        
        # Premium Green Styling
        bg_color = "#121212" # Even deeper charcoal
        accent_color = "#4CAF50" # Modern Green
        text_color = "#FFFFFF"
        
        root.configure(bg=bg_color)
        
        main_frame = tk.Frame(root, bg=bg_color, highlightbackground=accent_color, highlightthickness=1)
        main_frame.pack(fill="both", expand=True)

        accent_bar = tk.Frame(main_frame, bg=accent_color, width=4)
        accent_bar.pack(side="left", fill="y")

        content_frame = tk.Frame(main_frame, bg=bg_color, padx=25, pady=15)
        content_frame.pack(side="left", fill="both", expand=True)

        icon_label = tk.Label(content_frame, text="✅", fg=text_color, bg=bg_color, font=("Segoe UI Emoji", 16))
        icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 15))

        title_label = tk.Label(content_frame, text="LOGGED TO VAULT", fg=accent_color, bg=bg_color, font=("Segoe UI", 9, "bold"))
        title_label.grid(row=0, column=1, sticky="w")

        msg_label = tk.Label(content_frame, text=message, fg=text_color, bg=bg_color, font=("Segoe UI Variable Small", 11))
        msg_label.grid(row=1, column=1, sticky="w")
        
        root.update_idletasks()
        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()
        
        # CENTER OF SCREEN
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")

        # Fade In and Out Logic
        def fade_in(alpha=0.0):
            if alpha <= 0.95:
                root.attributes("-alpha", alpha)
                root.after(10, lambda: fade_in(alpha + 0.15))
            else:
                root.after(int(duration * 1000), fade_out)

        def fade_out(alpha=0.95):
            if alpha >= 0.0:
                root.attributes("-alpha", alpha)
                root.after(10, lambda: fade_out(alpha - 0.15))
            else:
                root.destroy()

        fade_in()
        root.mainloop()

    Thread(target=create_window, daemon=True).start()
