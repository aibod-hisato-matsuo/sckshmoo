import tkinter as tk
from tkinter import filedialog, scrolledtext
from analysis.create_shmooplot_files import extract_test_results

def select_file():
    # Open file dialog with filter for text files
    file_path = filedialog.askopenfilename(
        title="Select SHMOO Log File",
        filetypes=[("Log Files", "*.log"), ("All Files", "*.*")]
    )
    if file_path:
        input_file_label.config(text=file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            display_output(content)
        except Exception as e:
            display_output(f"Error reading file: {e}")

def display_output(text):
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, text)

# Set up the main window
root = tk.Tk()
root.title("Text File Viewer")

# Create a button to open the file dialog
select_button = tk.Button(root, text="Select Text File", command=select_file)
select_button.pack(pady=10)

# Label to show the selected file path
input_file_label = tk.Label(root, text="No file selected")
input_file_label.pack(pady=5)

# ScrolledText widget to display file content
output_text = scrolledtext.ScrolledText(root, width=60, height=20)
output_text.pack(pady=10)

root.mainloop()
