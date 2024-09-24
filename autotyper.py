import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import pyautogui
import keyboard
import time
import threading
import random

class Autotyper:
    def __init__(self, master):
        self.master = master
        master.title("Autotyper Pro")
        icon_path = os.path.join(os.path.dirname(__file__), 'autotyper.ico')
        try:
            master.iconbitmap(icon_path)
        except Exception as e:
            print(f"Failed to set icon: {e}")

        main_frame = ttk.Frame(master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        self.about_button = ttk.Button(main_frame, text="About", command=self.show_about, width=10)
        self.about_button.grid(column=1, row=0, sticky=tk.E, pady=5)

        ttk.Label(main_frame, text="Enter text to type:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.text_input = scrolledtext.ScrolledText(main_frame, width=50, height=10)
        self.text_input.grid(column=0, row=2, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(main_frame, text="Typing speed (CPM):").grid(column=0, row=3, sticky=tk.W, pady=5)
        self.speed_entry = ttk.Entry(main_frame)
        self.speed_entry.insert(0, "300")
        self.speed_entry.grid(column=0, row=4, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(main_frame, text="Delay between words (ms):").grid(column=1, row=3, sticky=tk.W, pady=5)
        self.delay_entry = ttk.Entry(main_frame)
        self.delay_entry.insert(0, "100")
        self.delay_entry.grid(column=1, row=4, sticky=(tk.W, tk.E), pady=5)

        self.random_speed_var = tk.BooleanVar()
        self.random_speed_check = ttk.Checkbutton(main_frame, text="Random speed per word", 
                                                  variable=self.random_speed_var)
        self.random_speed_check.grid(column=0, row=5, columnspan=2, sticky=tk.W, pady=5)

        hotkey_frame = ttk.Frame(main_frame)
        hotkey_frame.grid(column=0, row=6, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(hotkey_frame, text="Start hotkey:").grid(column=0, row=0, sticky=tk.W)
        self.start_hotkey_entry = ttk.Entry(hotkey_frame, width=10)
        self.start_hotkey_entry.insert(0, "alt+s")
        self.start_hotkey_entry.grid(column=1, row=0, sticky=tk.W, padx=(0, 10))

        ttk.Label(hotkey_frame, text="Stop hotkey:").grid(column=2, row=0, sticky=tk.W)
        self.stop_hotkey_entry = ttk.Entry(hotkey_frame, width=10)
        self.stop_hotkey_entry.insert(0, "alt+x")
        self.stop_hotkey_entry.grid(column=3, row=0, sticky=tk.W)

        self.save_button = ttk.Button(main_frame, text="Save Changes", command=self.save_changes)
        self.save_button.grid(column=0, row=7, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(column=0, row=8, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_typing)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_typing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=380)
        self.status_label.grid(column=0, row=9, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.is_typing = False
        self.start_key = self.start_hotkey_entry.get()
        self.stop_key = self.stop_hotkey_entry.get()

        self.setup_hotkeys()

    def setup_hotkeys(self):
        try:
            keyboard.add_hotkey(self.start_key, self.start_typing)
            keyboard.add_hotkey(self.stop_key, self.stop_typing)
        except Exception as e:
            self.show_status(f"Failed to set up hotkeys: {str(e)}", "error")

    def start_typing(self):
        if not self.is_typing:
            self.is_typing = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            threading.Thread(target=self.type_text, daemon=True).start()

    def type_text(self):
        try:
            text = self.text_input.get("1.0", tk.END).strip()
            base_speed = int(self.speed_entry.get())
            delay = int(self.delay_entry.get()) / 1000

            lines = text.split('\n')

            for line in lines:
                if not self.is_typing:
                    break
                
                words = line.split()
                for word in words:
                    if not self.is_typing:
                        break
                    
                    if self.random_speed_var.get():
                        speed = random.uniform(base_speed * 0.8, base_speed * 1.2)
                    else:
                        speed = base_speed
                    
                    char_delay = 60 / speed

                    for char in word:
                        if not self.is_typing:
                            break
                        pyautogui.write(char, interval=char_delay)
                    pyautogui.press('space')
                    time.sleep(delay)
                
                pyautogui.press('enter') 

            self.show_status("Typing completed successfully!", "success")
        except ValueError:
            self.show_status("Please enter valid numbers for speed and delay.", "error")
        except Exception as e:
            self.show_status(f"An error occurred while typing: {str(e)}", "error")
        finally:
            self.is_typing = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def stop_typing(self):
        self.is_typing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.show_status("Typing stopped.", "info")

    def save_changes(self):
        try:
            keyboard.remove_hotkey(self.start_key)
            keyboard.remove_hotkey(self.stop_key)
            self.start_key = self.start_hotkey_entry.get()
            self.stop_key = self.stop_hotkey_entry.get()
            self.setup_hotkeys()
            self.show_status("Changes saved successfully!", "success")
        except Exception as e:
            self.show_status(f"Failed to save changes: {str(e)}", "error")

    def show_status(self, message, status_type):
        self.status_var.set(message)
        if status_type == "error":
            self.status_label.config(foreground="red")
        elif status_type == "success":
            self.status_label.config(foreground="green")
        else:
            self.status_label.config(foreground="black")

    def show_about(self):
        about_text = """
        ✨ This Autotyper tool was created by Srijan Pathak.

        ⭐ If you like this tool, give it a star on GitHub!

        🔗 GitHub: https://github.com/srijanpathak03/Autotyper

        How to use:
        1️⃣ Type the text you want to auto-type.
        2️⃣ Set the typing speed and delay between words.
        3️⃣ Enable random speed for more natural typing.
        4️⃣ Set your start and stop hotkeys.
        5️⃣ Press 'Start' or use the hotkey to begin typing.
        6️⃣ Press 'Stop' or use the stop hotkey to halt typing.

        🚀 Features:
        - Customizable speed and delays for typing.
        - Supports multi-line text.
        - Random speed option for more human-like typing.
        - Global hotkeys for easy control.

        Do share you Feedback !
        """
        messagebox.showinfo("About Autotyper", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    autotyper = Autotyper(root)
    root.mainloop()