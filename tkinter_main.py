import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
import tkinter.font as tkfont
from analysis.create_shmooplot_files import extract_test_results
from analysis.fill_missing_vdd import update_files_for_vdd
from analysis.update_shmoo_range import update_files_for_range
from analysis.calculate_margin import calculate_files_for_margin
from analysis.aggregated_shmoo import process_aggregation
from analysis.xor_shmoo import process_xor

PLOTSDIR = "out.plot"
ARCHIVEDIR = "out.archive"

#custom_font = tkfont.Font(family="Courier", size=8, weight="bold", slant="italic")

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
        plot_texts = read_plots(test)
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

def display_plots(texts):
    """
    Display multiple texts in the output_frame arranged horizontally.
    
    Params:
        texts (list of str): List of text contents to display.
    """
    custom_font = tkfont.Font(family="Courier", size=6, foreground='#ff0000')

    # Clear the output_frame before inserting new texts
    for widget in output_frame_inner.winfo_children():
        widget.destroy()

    # Create a ScrolledText widget for each text and pack it horizontally
    for index, text in enumerate(texts):
        frame = tk.Frame(output_frame_inner)
        frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Optional: Add a label to identify each text block
        label = tk.Label(frame, text=f"Content {index + 1}", anchor='w', font=("Helvetica", 12, "bold"))
        label.pack(fill=tk.X)

        st = scrolledtext.ScrolledText(frame, width=60, height=60, font=custom_font)
        st.pack(fill=tk.BOTH, expand=True)
        st.insert(tk.END, text)
        st.configure(state='disabled')  # Make it read-only if desired

def on_subdir_button_click(subdir):
    """
    Callback function when a subdirectory button is clicked.
    """
    # Example action: Display the selected subdirectory
    display_output(f"Selected Subdirectory: {subdir}")
    
    # TODO: Add more functionality as needed
    # For example, open the subdirectory, process files, etc.
    try:
        # Example logic to get multiple file contents
        plot_texts = read_plots(subdir)
        aggregation_file_or = process_aggregation(subdir, "OR")
        aggregation_file_and = process_aggregation(subdir, "AND")
        aggregation_file_mj = process_aggregation(subdir, "Majority")
        agg_texts = read_plots_agg(aggregation_file_or, aggregation_file_and, aggregation_file_mj)
        #xordir_or = process_xor(subdir, aggregation_file_or, "OR_XOR")
        #xordir_and = process_xor(subdir, aggregation_file_and, "AND_XOR")
        #xordir_mj = process_xor(subdir, aggregation_file_mj, "MajorityVote_XOR")
        #xor_or_texts = read_plots_xor(xordir_or)
        #xor_and_texts = read_plots_xor(xordir_and)
        #xor_mj_texts = read_plots_xor(xordir_mj)
        
        # Combine all texts to display
        all_texts = []
        #all_texts.append(f"Subdirectory: {subdir}")
        #all_texts.append("Plot Texts:")
        #all_texts.extend(plot_texts)
        #all_texts.append("Aggregation Texts (OR, AND, Majority):")
        all_texts.extend(agg_texts)
        #all_texts.append("XOR OR Texts:")
        #all_texts.extend(xor_or_texts)
        #all_texts.append("XOR AND Texts:")
        #all_texts.extend(xor_and_texts)
        #all_texts.append("XOR MajorityVote Texts:")
        #all_texts.extend(xor_mj_texts)
        
        display_plots(all_texts)
    except Exception as e:
        display_output([f"Error processing subdirectory {subdir}: {e}"])


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
            width=80, 
            command=lambda s=subdir: on_subdir_button_click(s)
        )
        btn.pack(pady=2)

# Set up the main window
root = tk.Tk()
root.title("SHMOO Plots Viewer")
root.geometry("1000x1000")

# Create a button to open the file dialog
select_button = tk.Button(root, text="Select SHMOO Log File", command=select_file)
select_button.pack(pady=10)

# Label to show the selected file path
input_file_label = tk.Label(root, text="No file selected")
input_file_label.pack(pady=5)

# ScrolledText widget to display file content
output_text = scrolledtext.ScrolledText(root, width=100, height=6)
output_text.pack(pady=10)

# Label for Subdirectories
subdirs_label = tk.Label(root, text="Tests:")
subdirs_label.pack(pady=5)

# Frame to hold the subdirectory buttons
subdirs_frame = tk.Frame(root)
subdirs_frame.pack(pady=5, fill=tk.BOTH, expand=True)

# Create a container frame for output with horizontal scrollbar
output_container = tk.Frame(root,height="800",bg="red")
output_container.pack(pady=10, fill=tk.BOTH, expand=True)

# Create a Canvas inside the container
output_canvas = tk.Canvas(output_container, borderwidth=0)
output_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Create a horizontal scrollbar linked to the Canvas
output_scrollbar_x = tk.Scrollbar(output_container, orient=tk.HORIZONTAL, command=output_canvas.xview)
output_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

output_canvas.configure(xscrollcommand=output_scrollbar_x.set)

# Create the output_frame_inner inside the Canvas
output_frame_inner = tk.Frame(output_canvas)
output_canvas.create_window((0, 0), window=output_frame_inner, anchor='nw')

# Update scrollregion when the output_frame_inner changes size
def on_output_frame_configure(event):
    output_canvas.configure(scrollregion=output_canvas.bbox("all"))

output_frame_inner.bind("<Configure>", on_output_frame_configure)


root.mainloop()
