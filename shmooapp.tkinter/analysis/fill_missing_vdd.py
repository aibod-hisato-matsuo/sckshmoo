import os
import re
from analysis.common_utils import VDD_PATTERNS, extract_y_axis_info
from analysis.update_shmoo_range import update_shmoo_log


def sanitize_filename(filename):
    """
    Sanitizes the filename by replacing illegal characters with underscores.

    Args:
        filename (str): The original filename.

    Returns:
        str: The sanitized filename.
    """
    return re.sub(r'[\\/:"*?<>|]+', "_", filename)

def fill_missing_vdd(lines, max_vdd, min_vdd, step):
    """
    Fills in missing VDD values in the data rows based on the step.

    Args:
        lines (list): List of lines from the log file.
        max_vdd (float): Maximum VDD value.
        min_vdd (float): Minimum VDD value.
        step (float): Step value for VDD.

    Returns:
        list: Modified list of lines with missing VDD values filled in.
    """
    # Identify the start of the Shmoo plot data block
    # The data block starts two lines below the line containing only "VDD"
    data_start = None
    for i, line in enumerate(lines):
        if line.strip() in VDD_PATTERNS:
            data_start = i + 2  # Two lines below "VDD" line
            break

    if data_start is None:
        raise ValueError("Shmoo plot data block not found.")

    # Assuming data ends when lines no longer contain plot data
    # This can be an empty line or a line that doesn't start with spaces or doesn't resemble data
    data_end = data_start
    for i in range(data_start, len(lines)):
        '''if not lines[i].strip():
            data_end = i
            break'''
        current_line = lines[i]
        # Check if the line is the terminating line
        # (e.g., '  V   +---------+*--------+--------+')
        # (e.g., '  V   *---------+---------+--------+')
        terminating_match = re.match(r'^\s*V\s+[\+|\*]', current_line)
        if terminating_match:
            data_end = i
            break
        if not re.match(r'^\s', lines[i]):
            data_end = i
            break
    else:
        data_end = len(lines)

    # Initialize current_vdd to max_vdd
    current_vdd = max_vdd

    # To preserve leading_spaces
    for i in range(data_start, data_end):
        line = lines[i]
        leading_spaces = re.match(r'^(\s*)\d+\.\d*\s.*', line).group(1)
        if leading_spaces:
            break
    if leading_spaces is None:
        raise ValueError("leading_spaces can not be set.")
    
    # start loop
    for i in range(data_start, data_end):
        line = lines[i]
        # Check if the line starts with a VDD value (allowing leading spaces)
        vdd_match = re.match(r'^\s*(\d+\.\d+)\s+(.*)', line)
        if vdd_match:
            # Line has VDD value
            current_vdd = float(vdd_match.group(1))
            continue
        else:
            # Line is missing VDD value, calculate it by adding step
            current_vdd += step  # Step is negative, so this decreases VDD
            # Clamp current_vdd to not go below min_vdd
            if current_vdd < min_vdd - 1e-6:  # Allowing a small epsilon for floating point
                current_vdd = min_vdd  # Clamp to min_vdd to avoid going below
            # Insert the calculated VDD at the beginning of the line with proper formatting
            # Assuming VDD should be formatted to three decimal places
            new_vdd_str = f"{current_vdd:.3f}   "
            # Check if the line starts with '*!' after stripping leading spaces
            stripped_line = line.lstrip()
            if stripped_line.startswith("*!") or stripped_line.startswith("*P"):
                # Remove one space to account for the '*' character
                new_vdd_str = f"{current_vdd:.3f}  "
            # Preserve the original indentation by extracting leading spaces
            lines[i] = leading_spaces + new_vdd_str + line.lstrip()

    return lines

def process_log_file(file_path):
    """
    Processes a single log file to fill in missing VDD values.

    Args:
        file_path (str): Path to the log file.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    try:
        max_vdd, min_vdd, step = extract_y_axis_info(lines)
    except ValueError as e:
        print(f"Error processing {file_path}: {e}")
        return

    try:
        modified_lines = fill_missing_vdd(lines, max_vdd, min_vdd, step)
    except ValueError as e:
        print(f"Error processing {file_path}: {e}")
        return

    # Write the modified lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

    print(f"Updated VDD: {os.path.basename(file_path)}")

def update_files_for_vdd(input_directory):
    # Process all .log files in the input directory
    for filename in sorted(os.listdir(input_directory)):
        if filename.endswith('.log'):
            file_path = os.path.join(input_directory, filename)
            process_log_file(file_path)
            update_shmoo_log(file_path,file_path)