import tkinter as tk
from tkinter import filedialog, scrolledtext, Listbox
from analysis.create_shmooplot_files import extract_test_results

PLOTSDIR = "out.plot"
ARCHIVEDIR = "out.archive"


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
            #display_output(content)
            run_all_tests(file_path)
        except Exception as e:
            display_output(f"Error reading file: {e}")

def run_all_tests(filepath):
    subdirs = []
    subdirs = extract_test_results(filepath,PLOTSDIR)
    display_subdirs(subdirs)
    display_output(f"Found {len(subdirs)} subdirectories.")

def display_output(text):
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, text)

def on_subdir_button_click(subdir):
    """
    Callback function when a subdirectory button is clicked.
    """
    # Example action: Display the selected subdirectory
    display_output(f"Selected Subdirectory: {subdir}")
    
    # TODO: Add more functionality as needed
    # For example, open the subdirectory, process files, etc.

#def display_subdirs(subdirs):
#    # Clear the Listbox before inserting new items
#    subdirs_listbox.delete(0, tk.END)
#    for subdir in subdirs:
#        subdirs_listbox.insert(tk.END, subdir)
def display_subdirs(subdirs):
    """
    Display each subdirectory as a button within the subdirs_frame.
    """
    # Clear any existing buttons in the frame
    for widget in subdirs_frame.winfo_children():
        widget.destroy()
    
    # Create a button for each subdirectory
    for subdir in subdirs:
        btn = tk.Button(
            subdirs_frame, 
            text=subdir, 
            width=50, 
            command=lambda s=subdir: on_subdir_button_click(s)
        )
        btn.pack(pady=2)

# Set up the main window
root = tk.Tk()
root.title("Log File Viewer")

# Create a button to open the file dialog
select_button = tk.Button(root, text="Select Text File", command=select_file)
select_button.pack(pady=10)

# Label to show the selected file path
input_file_label = tk.Label(root, text="No file selected")
input_file_label.pack(pady=5)

# ScrolledText widget to display file content
output_text = scrolledtext.ScrolledText(root, width=60, height=20)
output_text.pack(pady=10)

# Label for Subdirectories Listbox
subdirs_label = tk.Label(root, text="Subdirectories:")
subdirs_label.pack(pady=5)

## Listbox to display subdirectories
#subdirs_listbox = Listbox(root, width=60, height=10)
#subdirs_listbox.pack(pady=5)

# Frame to hold the subdirectory buttons
subdirs_frame = tk.Frame(root)
subdirs_frame.pack(pady=5, fill=tk.BOTH, expand=True)

root.mainloop()
