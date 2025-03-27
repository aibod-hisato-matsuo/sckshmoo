import os
import re
import sys
import argparse
from collections import defaultdict
from shmooapp.analysis.common_utils import VDD_PATTERNS

def parse_log_file(file_path):
    """
    Parses a log file and extracts header, data block, footer, VDD data, and '*' presence.

    Args:
        file_path (str): Path to the log file.

    Returns:
        tuple: (header_lines, data_block, footer_lines, vdd_data_dict, vdd_has_star_dict)
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    header_lines = []
    footer_lines = []
    data_block = []
    vdd_data = {}
    vdd_has_star = {}

    data_start = None
    data_end = None

    # Identify the start of the data block
    for i, line in enumerate(lines):
        #if line.strip() == "VDD":
        if line.strip() in VDD_PATTERNS:
            data_start = i + 2  # Two lines below 'VDD'
            header_lines = lines[:data_start]
            break

    if data_start is None:
        raise ValueError(f"'VDD' line not found in {file_path}")

    # Identify end of data block
    for i in range(data_start, len(lines)):
        current_line = lines[i]
        # Detect terminating conditions (similar to aggregation script)
        terminating_match = re.match(r'^\s*\d+\.\d+\s+V\s+\+', current_line)
        if terminating_match:
            data_end = i
            footer_lines = lines[i:]
            break
        if not re.match(r'^\s', current_line):
            data_end = i
            footer_lines = lines[i:]
            break
    else:
        data_end = len(lines)
        footer_lines = []

    data_block = lines[data_start:data_end]

    # Parse data block
    for line in data_block:
        # Example data row format: "0.720   !.........!.PPPPPPPPPPPPPPPPPP (65.000..      )"
        # Optional '*' just before data string
        match = re.match(r'\s*(\d+\.\d+)\s+(\*?)([!.\w]+)\s*\(.*\)', line)
        if not match:
            # Handle lines that don't match expected format
            continue
        vdd = float(match.group(1))
        has_star = bool(match.group(2))
        data_str = match.group(3)
        # Remove '*' from data string if present
        if has_star and data_str.startswith('*'):
            data_str = data_str[1:]
        vdd_data[vdd] = data_str
        vdd_has_star[vdd] = has_star

    return header_lines, data_block, footer_lines, vdd_data, vdd_has_star

def compute_xor_data(aggregated_data, original_data):
    """
    Computes XOR data string between aggregated and original data strings.

    Args:
        aggregated_data (str): Aggregated data string.
        original_data (str): Original site data string.

    Returns:
        str: XOR data string.
    """
    if len(aggregated_data) != len(original_data):
        raise ValueError("Data string lengths do not match for XOR operation.")

    xor_data = []
    for agg_char, orig_char in zip(aggregated_data, original_data):
        if agg_char != orig_char:
            xor_char = 'X'  # Define 'X' as the XOR result
        else:
            xor_char = '.'  # Mark similar positions with '.'
        xor_data.append(xor_char)
    return ''.join(xor_data)

def aggregate_star_presence(aggregated_star, original_star):
    """
    Determines if any of the logs have '*' presence for a given VDD.

    Args:
        aggregated_star (dict): VDD to '*' presence from aggregated log.
        original_star (dict): VDD to '*' presence from original log.

    Returns:
        dict: VDD to '*' presence for XOR log (True if either has '*').
    """
    xor_star = {}
    for vdd in aggregated_star:
        xor_star[vdd] = aggregated_star.get(vdd, False) or original_star.get(vdd, False)
    return xor_star

def create_xor_log(header_lines, footer_lines, vdd_xor_data, vdd_xor_star, output_file):
    """
    Creates a new log file with XOR data.

    Args:
        header_lines (list): Header lines from the aggregated log.
        footer_lines (list): Footer lines from the aggregated log.
        vdd_xor_data (dict): VDD to XOR data string mapping.
        vdd_xor_star (dict): VDD to '*' presence mapping for XOR log.
        output_file (str): Path to the output XOR log file.
    """
    with open(output_file, 'w') as f:
        # Write header
        f.writelines(header_lines)
        # Write XOR data strings
        sorted_vdd = sorted(vdd_xor_data.keys(), reverse=True)
        for vdd in sorted_vdd:
            data_str = vdd_xor_data[vdd]
            has_star = vdd_xor_star.get(vdd, False)
            # Format VDD value to three decimal places
            vdd_formatted = f"{vdd:7.3f}"
            if has_star:
                # Insert '*' before the data string and adjust spacing
                f.write(f"{vdd_formatted}  *{data_str} (15.000..      )\n")
            else:
                # Standard spacing with three spaces
                f.write(f"{vdd_formatted}   {data_str} (15.000..      )\n")
        # Write footer
        f.writelines(footer_lines)
    print(f"XOR log file created: {output_file}")

def process_xor(curdir:str,aggfile:str,xor_prefix:str):
    #
    aggregated_log_file = aggfile
    original_logs_dir = curdir
    output_dir = curdir+"."+xor_prefix

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Output directory '{output_dir}' created.")

    # Parse aggregated log
    try:
        agg_header, agg_data_block, agg_footer, agg_vdd_data, agg_vdd_has_star = parse_log_file(aggregated_log_file)
    except ValueError as e:
        print(f"Error parsing aggregated log file: {e}")
        sys.exit(1)

    # Iterate over original log files
    original_log_files = [f for f in os.listdir(original_logs_dir) if f.endswith('.log')]
    if not original_log_files:
        print(f"No .log files found in input directory '{original_logs_dir}'.")
        sys.exit(1)

    for orig_log in original_log_files:
        orig_log_path = os.path.join(original_logs_dir, orig_log)
        try:
            orig_header, orig_data_block, orig_footer, orig_vdd_data, orig_vdd_has_star = parse_log_file(orig_log_path)
        except ValueError as e:
            print(f"Error parsing original log file '{orig_log}': {e}")
            continue  # Skip to next file

        # Check VDD consistency
        if set(agg_vdd_data.keys()) != set(orig_vdd_data.keys()):
            print(f"VDD values mismatch between aggregated log and original log '{orig_log}'. Skipping.")
            continue

        # Compute XOR data
        xor_vdd_data = {}
        for vdd in agg_vdd_data:
            agg_data_str = agg_vdd_data[vdd]
            orig_data_str = orig_vdd_data[vdd]
            try:
                xor_data_str = compute_xor_data(agg_data_str, orig_data_str)
                xor_vdd_data[vdd] = xor_data_str
            except ValueError as e:
                print(f"Error computing XOR for VDD={vdd} in log '{orig_log}': {e}")
                xor_vdd_data[vdd] = ''.join(['?'] * len(agg_data_str))  # Placeholder for error

        # Track '*' presence in XOR log (retain '*' if present in either aggregated or original log for the VDD)
        xor_vdd_star = {}
        for vdd in agg_vdd_has_star:
            xor_vdd_star[vdd] = agg_vdd_has_star.get(vdd, False) or orig_vdd_has_star.get(vdd, False)

        # Define output file name, e.g., 'XOR_site1.log' based on original log 'site1.log'
        orig_log_basename = os.path.basename(orig_log)
        #xor_log_basename = f"XOR_{orig_log_basename}"
        xor_log_basename = f"{orig_log_basename}"
        xor_log_path = os.path.join(output_dir, xor_log_basename)

        # Write XOR log file
        try:
            create_xor_log(agg_header, agg_footer, xor_vdd_data, xor_vdd_star, xor_log_path)
        except Exception as e:
            print(f"Error writing XOR log file '{xor_log_basename}': {e}")
            continue
    return output_dir