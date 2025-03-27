import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, Listbox
from analysis.create_shmooplot_files import extract_test_results
from analysis.fill_missing_vdd import update_files_for_vdd
from analysis.update_shmoo_range import update_files_for_range
from analysis.calculate_margin import calculate_files_for_margin
from analysis.aggregated_shmoo import process_aggregation
from analysis.xor_shmoo import process_xor

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
    subdirs = extract_test_results(filepath,PLOTSDIR)
    for test in subdirs:
        update_files_for_vdd(test)
        #update_files_for_range(test)
        margin_sets = calculate_files_for_margin(test)
        read_plots(test)
        aggregation_file_or = process_aggregation(test,"OR")
        aggregation_file_and = process_aggregation(test,"AND")
        aggregation_file_mj = process_aggregation(test,"Majority")
        agg_texts = read_plots_agg(aggregation_file_or, aggregation_file_and, aggregation_file_mj)
        xordir_or = process_xor(test,aggregation_file_or,"OR_XOR")
        xordir_and = process_xor(test,aggregation_file_and,"AND_XOR")
        xordir_mj = process_xor(test,aggregation_file_mj,"MajorityVote_XOR")
        xor_or_texts = read_plots_xor(xordir_or)
        xor_and_texts = read_plots_xor(xordir_and)
        xor_mj_texts = read_plots_xor(xordir_mj)


    display_subdirs(subdirs)
    display_output(f"Found {len(subdirs)} subdirectories.")

def read_plots(directory: str):
    subfiles = sorted(os.listdir(directory))
    subfile_texts = []
    for file in subfiles:
        filepath = os.path.join(directory,file)
        with open(filepath,encoding='UTF-8') as f:
            text = f.read()
        subfile_texts.append(text)
    return subfile_texts

def read_plots_agg(or_file,and_file,mj_file):
    aggfile_texts = []
    for filepath in [or_file,and_file,mj_file]:
        with open(filepath,encoding='UTF-8') as f:
            text = f.read()
        aggfile_texts.append(text)
    return aggfile_texts

def read_plots_xor(xordir):
    xorfile_texts = []
    xorfiles = sorted(os.listdir(xordir))
    for file in xorfiles:
        filepath = os.path.join(xordir,file)
        with open(filepath,encoding='UTF-8') as f:
            text = f.read()
        xorfile_texts.append(text)
    return xorfile_texts

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
