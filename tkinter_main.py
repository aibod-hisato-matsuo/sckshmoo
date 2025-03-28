import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
import tkinter.font as tkfont
from shmooapp.analysis.create_shmooplot_files import extract_test_results
from shmooapp.analysis.fill_missing_vdd import update_files_for_vdd
from shmooapp.analysis.update_shmoo_range import update_files_for_range
from shmooapp.analysis.calculate_margin import calculate_files_for_margin
from shmooapp.analysis.aggregated_shmoo import process_aggregation
from shmooapp.analysis.xor_shmoo import process_xor
from shmooapp.analysis.common_utils import create_yyyymmdd_today

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
        destroy_all_widgets()
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            #display_output(content)
            run_all_tests(file_path)
        except Exception as e:
            display_output(f"Error reading file: {e}")

def destroy_widgets(widgets):
    for widget in widgets:
        widget.destroy()

def destroy_all_widgets():
    destroy_widgets(subdir_buttons_frame.winfo_children())
    destroy_widgets(output_frame_inner1.winfo_children())
    destroy_widgets(output_frame_inner2.winfo_children())

def run_all_tests(filepath):
    if not os.path.exists(PLOTSDIR):
        os.makedirs(PLOTSDIR)
    plotpath = os.path.join(PLOTSDIR,create_yyyymmdd_today())
    subdirs = extract_test_results(filepath,plotpath)
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
    display_output(f"Found {len(subdirs)} Tests.")

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

def display_plots(texts,output_frame_inner,strcolor=None):
    """
    Display multiple texts in the output_frame arranged horizontally.
    """
    custom_font = tkfont.Font(family="Courier", size=6)
    if not strcolor:
        strcolor = "navy"

    # Clear the output_frame before inserting new texts
    for widget in output_frame_inner.winfo_children():
        widget.destroy()

    # Create a ScrolledText widget for each text and pack it horizontally
    for (label, text) in texts:
        frame = tk.Frame(output_frame_inner)
        frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=False)

        # Optional: Add a label to identify each text block
        label = tk.Label(frame, text=f"{label}", anchor='w', font=("Helvetica", 12, "bold"), fg=strcolor)
        label.pack(fill=tk.X)

        st = scrolledtext.ScrolledText(frame, width=60, height=70, font=custom_font)
        st.pack(fill=tk.BOTH, expand=True)
        st.insert(tk.END, text)
        st.configure(state='disabled')  # Make it read-only if desired

def on_subdir_button_click(subdir):
    """
    Callback function when a subdirectory button is clicked.
    """
    # Example action: Display the selected subdirectory
    display_output(f"Selected Test: {subdir}")
    
    # TODO: Add more functionality as needed
    # For example, open the subdirectory, process files, etc.
    try:
        # Example logic to get multiple file contents
        plot_texts = read_plots(subdir)
        aggregation_file_or = process_aggregation(subdir, "OR")
        aggregation_file_and = process_aggregation(subdir, "AND")
        aggregation_file_mj = process_aggregation(subdir, "Majority")
        agg_texts = read_plots_agg(aggregation_file_or, aggregation_file_and, aggregation_file_mj)
        xordir_or = process_xor(subdir, aggregation_file_or, "OR_XOR")
        xordir_and = process_xor(subdir, aggregation_file_and, "AND_XOR")
        xordir_mj = process_xor(subdir, aggregation_file_mj, "MajorityVote_XOR")
        xor_or_texts = read_plots_xor(xordir_or)
        xor_and_texts = read_plots_xor(xordir_and)
        xor_mj_texts = read_plots_xor(xordir_mj)
        
        agg_items = ["OR", "AND", "Majority"]
        agg_texts_with_labels = [(agg_items[i], text) for i, text in enumerate(agg_texts)]

        xor_or_texts_with_labels = [
            (f"OR compared: XOR {i+1}", text) for i, text in enumerate(xor_or_texts)
        ]
        xor_and_texts_with_labels = [
            (f"AND compared: XOR {i+1}", text) for i, text in enumerate(xor_and_texts)
        ]
        xor_mj_texts_with_labels = [
            (f"Mojority Vote compared: XOR {i+1}", text) for i, text in enumerate(xor_mj_texts)
        ]
        
        display_plots(agg_texts_with_labels,output_frame_inner1,"blue")
    except Exception as e:
        display_output([f"Error processing Test {subdir}: {e}"])

    # Clear any existing buttons in subdir_buttons_frame
    destroy_widgets(output_frame_inner2.winfo_children())
    destroy_widgets(subdir_buttons_frame.winfo_children())
    # Define button callbacks
    def handle_or():
        display_output(f"OR button clicked for {subdir}")
        display_plots(xor_or_texts_with_labels,output_frame_inner1)
        display_plots(agg_texts_with_labels,output_frame_inner2,"blue")

    def handle_and():
        display_output(f"AND button clicked for {subdir}")
        display_plots(xor_and_texts_with_labels,output_frame_inner1)
        display_plots(agg_texts_with_labels,output_frame_inner2,"blue")

    def handle_majority():
        display_output(f"Majority button clicked for {subdir}")
        display_plots(xor_mj_texts_with_labels,output_frame_inner1)
        display_plots(agg_texts_with_labels,output_frame_inner2,"blue")

    # Create the three buttons
    or_button = tk.Button(subdir_buttons_frame, text="OR", command=handle_or)
    and_button = tk.Button(subdir_buttons_frame, text="AND", command=handle_and)
    majority_button = tk.Button(subdir_buttons_frame, text="Majority", command=handle_majority)
       
    # Pack the buttons into the frame
    or_button.pack(side=tk.LEFT, padx=5)
    and_button.pack(side=tk.LEFT, padx=5)
    majority_button.pack(side=tk.LEFT, padx=5)


def display_subdirs(subdirs):
    """
    Display each subdirectory as a button within the subdirs_frame.
    """
    # Clear any existing buttons in the frame
    destroy_widgets(subdirs_frame.winfo_children())
    # Create a button for each subdirectory
    for subdir in subdirs:
        btn = tk.Button(
            subdirs_frame, 
            text=subdir, 
            anchor='w',
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
output_text = scrolledtext.ScrolledText(root, width=120, height=1, fg="blue")
output_text.pack(pady=10)

# Label for Subdirectories
subdirs_label = tk.Label(root, text="Tests:")
subdirs_label.pack(pady=5)

# Frame to hold the subdirectory buttons
subdirs_frame = tk.Frame(root)
subdirs_frame.pack(pady=5, fill=tk.BOTH, expand=False)

# Label for Subdirectories
subdir_buttons_label = tk.Label(root, text="Aggregation Mode:")
subdir_buttons_label.pack(pady=5)

# Frame to hold extra buttons after a subdir is selected
subdir_buttons_frame = tk.Frame(root, height="100")
subdir_buttons_frame.pack(pady=5)

# Create a container frame for output with horizontal scrollbar
output_container = tk.Frame(root,bg="navy")
output_container.pack(pady=10, fill=tk.BOTH, expand=True)

# Create a Canvas inside the container
output_canvas = tk.Canvas(output_container, borderwidth=0,bg="lightblue")

# Create vertical scrollbar linked to the Canvas
output_scrollbar_y = tk.Scrollbar(output_container, orient=tk.VERTICAL, command=output_canvas.yview)

# Create a horizontal scrollbar linked to the Canvas
output_scrollbar_x = tk.Scrollbar(output_container, orient=tk.HORIZONTAL, command=output_canvas.xview)

output_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
output_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
output_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

output_canvas.configure(yscrollcommand=output_scrollbar_y.set, xscrollcommand=output_scrollbar_x.set)

# Create a parent frame inside the Canvas to hold both plot frames
parent_frame = tk.Frame(output_canvas)
output_canvas.create_window((0, 0), window=parent_frame, anchor='nw')

# Create and pack the first inner frame for the first set of plots
output_frame_inner1 = tk.Frame(parent_frame)
output_frame_inner1.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH, expand=True)

# Create and pack the second inner frame for the second set of plots
output_frame_inner2 = tk.Frame(parent_frame)
output_frame_inner2.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH, expand=True)

# Update scrollregion when the output_frame_inner changes size
def on_parent_frame_configure(event):
    output_canvas.configure(scrollregion=output_canvas.bbox("all"))

parent_frame.bind("<Configure>", on_parent_frame_configure)


root.mainloop()
