import os
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter
from analysis.common_utils import VDD_PATTERNS,generate_aggfile_name

def _extract_y_axis_info(lines):
    """
    Extracts Max VDD, Min VDD, and Step from the Y-Axis meta information.

    Args:
        lines (list): List of lines from the log file.

    Returns:
        tuple: (max_vdd, min_vdd, step)
    """
    y_axis_pattern = re.compile(
        r"Y-Axis\s*:\s*VDD\s*\[\s*([\d.]+)\s*\.\.\s*([\d.]+)\s*V\s*\]\s*step\s*([-+]?\d*\.\d+|\d+)\s*V",
        re.IGNORECASE
    )
    for line in lines:
        match = y_axis_pattern.search(line)
        if match:
            max_vdd = float(match.group(1))
            min_vdd = float(match.group(2))
            step = float(match.group(3))
            return max_vdd, min_vdd, step
    raise ValueError("Y-Axis information not found or malformed.")

def extract_data_block(lines):
    """
    Extracts the data block from the log file.

    Args:
        lines (list): List of lines from the log file.

    Returns:
        tuple: (header_lines, data_block, footer_lines)
    """
    header_lines = []
    footer_lines = []
    data_block = []
    data_start = None
    data_end = None

    for i, line in enumerate(lines):
        #if line.strip() == "VDD":
        if line.strip() in VDD_PATTERNS:
            data_start = i + 2  # Two lines below "VDD" line
            header_lines = lines[:i+2]
            break

    if data_start is None:
        raise ValueError("VDD line not found.")

    # Determine data_end
    for i in range(data_start, len(lines)):
        current_line = lines[i]
        #terminating_match = re.match(r'^\s*\d+\.\d+\s+V\s+\+', current_line)
        terminating_match = re.match(r'^\s*V\s+\+', current_line)
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

    print(f"--> {footer_lines}")
    data_block = lines[data_start:data_end]
    return header_lines, data_block, footer_lines

def parse_data_block(data_block):
    """
    Parses the data block to extract VDD values and their corresponding data strings.

    Args:
        data_block (list): List of data lines.

    Returns:
        tuple: (vdd_data, vdd_has_star)
            - vdd_data: dict mapping VDD to data string without '*'
            - vdd_has_star: dict mapping VDD to boolean indicating presence of '*' before data
    """
    vdd_data = {}
    vdd_has_star = {}
    # Regex to capture VDD and data strings, optionally starting with '*!'
    # Example line: "0.980  *!.PPPPPPPPPPPPPPPPPPPPPPPPPPPP (15.000..      )"
    data_pattern = re.compile(r'^\s*(\d+\.\d+)\s+([*!]?[\.!P]+).*\(')

    for line in data_block:
        match = data_pattern.match(line)
        if match:
            vdd = float(match.group(1))
            data_str = match.group(2)
            has_star = data_str.startswith('*')
            # Remove '*' from data_str if present
            if has_star:
                data_str = data_str[1:]
            vdd_data[vdd] = data_str
            vdd_has_star[vdd] = has_star
        else:
            # Handle lines that do not match the pattern
            # You may choose to log or handle these lines differently
            print(f"Warning: Could not parse line: {line.strip()}")
    return vdd_data, vdd_has_star

def read_log_file(file_path):
    """
    Reads a single log file and extracts its components.

    Args:
        file_path (str): Path to the log file.

    Returns:
        tuple: (header_lines, data_block, footer_lines, vdd_data, vdd_has_star)
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    header_lines, data_block, footer_lines = extract_data_block(lines)
    vdd_data, vdd_has_star = parse_data_block(data_block)

    return header_lines, data_block, footer_lines, vdd_data, vdd_has_star

def aggregate_or(vdd_data_list):
    """
    Aggregates VDD data using logical OR across all sites.

    Args:
        vdd_data_list (list): List of dictionaries mapping VDD to data strings.

    Returns:
        dict: Aggregated VDD to data string mapping.
    """
    aggregated = {}
    # Assuming all vdd_data have the same VDD keys
    vdd_keys = vdd_data_list[0].keys()
    for vdd in vdd_keys:
        # Collect all data strings for this VDD
        data_strings = [data_dict[vdd] for data_dict in vdd_data_list if vdd in data_dict]
        max_length = max(len(s) for s in data_strings)
        aggregated_data = []
        for i in range(max_length):
            char_set = set()
            for data_str in data_strings:
                if i < len(data_str):
                    char_set.add(data_str[i])
                else:
                    char_set.add(' ')  # Treat missing characters as space
            # Define precedence: 'P' > '!' > '.' > ' '
            if 'P' in char_set:
                aggregated_data.append('P')
            elif '!' in char_set:
                aggregated_data.append('!')
            elif '.' in char_set:
                aggregated_data.append('.')
            else:
                aggregated_data.append(' ')
        aggregated[vdd] = ''.join(aggregated_data)
    return aggregated

def aggregate_majority_vote(vdd_data_list):
    """
    Aggregates VDD data using majority vote across all sites.

    Args:
        vdd_data_list (list): List of dictionaries mapping VDD to data strings.

    Returns:
        dict: Aggregated VDD to data string mapping.
    """
    aggregated = {}
    vdd_keys = vdd_data_list[0].keys()
    for vdd in vdd_keys:
        # Collect all data strings for this VDD
        data_strings = [data_dict[vdd] for data_dict in vdd_data_list if vdd in data_dict]
        max_length = max(len(s) for s in data_strings)
        aggregated_data = []
        for i in range(max_length):
            # Collect all characters at position i
            chars_at_pos = [data_str[i] if i < len(data_str) else ' ' for data_str in data_strings]
            count = Counter(chars_at_pos)
            # Determine the character with the highest count
            # Ignoring spaces
            if len(count) == 0:
                majority_char = ' '
            else:
                # Exclude space from counting
                filtered_count = {k: v for k, v in count.items() if k != ' '}
                if not filtered_count:
                    majority_char = ' '
                else:
                    max_votes = max(filtered_count.values())
                    # Get all characters with max_votes
                    candidates = [k for k, v in filtered_count.items() if v == max_votes]
                    if 'P' in candidates:
                        majority_char = 'P'
                    elif '!' in candidates:
                        majority_char = '!'
                    elif '.' in candidates:
                        majority_char = '.'
                    else:
                        majority_char = candidates[0]  # Default to the first candidate
            aggregated_data.append(majority_char)
        aggregated[vdd] = ''.join(aggregated_data)
    return aggregated

def aggregate_majority_vote_with_precedence(vdd_data_list):
    """
    Aggregates VDD data using majority vote with defined precedence in case of ties.

    Args:
        vdd_data_list (list): List of dictionaries mapping VDD to data strings.

    Returns:
        dict: Aggregated VDD to data string mapping.
    """
    return aggregate_majority_vote(vdd_data_list)

def aggregate_and(vdd_data_list):
    """
    Aggregates data strings using logical AND.

    Args:
        vdd_data_list (list): List of dicts mapping VDD to data string.

    Returns:
        dict: Aggregated data strings for each VDD.
    """
    aggregated_data = {}
    if not vdd_data_list:
        return aggregated_data

    vdd_set = set(vdd_data_list[0].keys())

    for vdd in vdd_set:
        # Collect data strings from all sites for this VDD
        data_strings = [vdd_data[vdd] for vdd_data in vdd_data_list if vdd in vdd_data]
        if not data_strings:
            continue  # or handle missing data

        data_length = len(data_strings[0])
        # Ensure all data strings have the same length
        if any(len(s) != data_length for s in data_strings):
            print(f"Warning: Inconsistent data string lengths for VDD={vdd}. Skipping.")
            continue

        aggregated_str = ''
        for pos in range(data_length):
            chars_at_pos = [s[pos] for s in data_strings]
            if all(c == 'P' for c in chars_at_pos):
                aggregated_str += 'P'
            else:
                if '!' in chars_at_pos:
                    aggregated_str += '!'
                elif '.' in chars_at_pos:
                    aggregated_str += '.'
                else:
                    aggregated_str += ' '
        aggregated_data[vdd] = aggregated_str
    return aggregated_data

def aggregate(vdd_data_list, mode='OR'):
    """
    Aggregates VDD data based on the selected mode.

    Args:
        vdd_data_list (list): List of dictionaries mapping VDD to data strings.
        mode (str): Aggregation mode ('OR' or 'Majority').

    Returns:
        dict: Aggregated VDD to data string mapping.
    """
    if mode == 'OR':
        return aggregate_or(vdd_data_list)
    elif mode == 'AND':
        return aggregate_and(vdd_data_list)
    elif mode == 'Majority':
        return aggregate_majority_vote_with_precedence(vdd_data_list)
    else:
        raise ValueError("Unsupported aggregation mode. Choose 'OR' or 'Majority'.")

def aggregate_star_presence(vdd_has_star_list):
    """
    Aggregates the presence of '*' for each VDD across all sites.

    Args:
        vdd_has_star_list (list): List of dictionaries mapping VDD to boolean for '*' presence.

    Returns:
        dict: Mapping from VDD to boolean indicating if any site has '*' for that VDD.
    """
    aggregated_star = {}
    for vdd_has_star in vdd_has_star_list:
        for vdd, has_star in vdd_has_star.items():
            if vdd in aggregated_star:
                aggregated_star[vdd] = aggregated_star[vdd] or has_star
            else:
                aggregated_star[vdd] = has_star
    return aggregated_star

def create_aggregated_log(header_lines, footer_lines, aggregated_data, aggregated_star, mode, output_file):
    """
    Creates a new log file with aggregated data.

    Args:
        header_lines (list): Header lines from the original log files.
        footer_lines (list): Footer lines from the original log files.
        aggregated_data (dict): Aggregated VDD to data string mapping.
        aggregated_star (dict): Aggregated '*' presence mapping.
        mode (str): Aggregation mode ('OR' or 'Majority').
        output_file (str): Path to the output log file.
    """
    with open(output_file, 'w') as file:
        # Write header
        file.writelines(header_lines)
        #file.write("\n")  # Add a newline between header and data
        #file.write("VDD\n")
        # Assuming there's a specific line pattern in the footer that includes '+---------+*--------+--------+'
        # If present, it can be directly copied from footer or adjusted as needed
        # Here, we'll check if footer has such a line
        # For simplicity, we'll skip adding it manually

        # Write aggregated data
        sorted_vdd = sorted(aggregated_data.keys(), reverse=True)
        for vdd in sorted_vdd:
            data_str = aggregated_data[vdd]
            has_star = aggregated_star.get(vdd, False)
            # Format VDD value to three decimal places
            vdd_formatted = f"{vdd:7.3f}"
            if has_star:
                # Insert '*' before the data string and adjust spacing
                # Remove one space between VDD and data if '*' is present
                file.write(f"{vdd_formatted}  *{data_str} (15.000..      )\n")
            else:
                # Standard spacing with three spaces
                file.write(f"{vdd_formatted}   {data_str} (15.000..      )\n")

        # Write footer
        file.writelines(footer_lines)
    print(f"Aggregated '{mode}' Shmoo plot saved to: {output_file}")


def process_aggregation(input_directory,mode) -> str:

    #out_dirname = Path(input_directory).parent
    #out_basename = Path(input_directory).name
    #out_filename = out_basename + "_aggregated_" + mode + ".log"
    #output_file = os.path.join(out_dirname,out_filename)
    output_file = generate_aggfile_name(input_directory,mode)

    log_files = [f for f in os.listdir(input_directory) if f.endswith('.log')]
    if not log_files:
        print(f"No .log files found in '{input_directory}'.")
        sys.exit(1)

    vdd_data_list = []
    vdd_has_star_list = []
    header_lines_common = None
    footer_lines_common = None

    for log_file in log_files:
        file_path = os.path.join(input_directory, log_file)
        try:
            header_lines, data_block, footer_lines, vdd_data, vdd_has_star = read_log_file(file_path)
            vdd_data_list.append(vdd_data)
            vdd_has_star_list.append(vdd_has_star)
            if header_lines_common is None:
                header_lines_common = header_lines
            if footer_lines_common is None:
                footer_lines_common = footer_lines
        except ValueError as e:
            print(f"Error processing '{log_file}': {e}")

    if not vdd_data_list:
        print("No valid data extracted from log files.")
        sys.exit(1)

    # Aggregate data based on the selected mode
    aggregated_data = aggregate(vdd_data_list, mode=mode)
    aggregated_star = aggregate_star_presence(vdd_has_star_list)

    # Create the aggregated log
    create_aggregated_log(header_lines_common, footer_lines_common, aggregated_data, aggregated_star, mode, output_file)

    return output_file



'''def main():
    parser = argparse.ArgumentParser(description="Aggregate Shmoo plot data across multiple sites using logical OR or Majority Vote.")
    parser.add_argument('-i', '--input_dir', type=str, default='extracted_tests',
                        help='Input directory containing site log files.')
    parser.add_argument('-o', '--output_file', type=str, default='aggregated_Shmoo_Plot.log',
                        help='Output file for aggregated data.')
    parser.add_argument('-m', '--mode', type=str, choices=['OR', 'Majority'], default='OR',
                        help='Aggregation mode: "OR" or "Majority".')
    args = parser.parse_args()

    input_directory = args.input_dir
    output_file = args.output_file
    mode = args.mode

    if not os.path.exists(input_directory):
        print(f"Input directory '{input_directory}' does not exist.")
        sys.exit(1)

    log_files = [f for f in os.listdir(input_directory) if f.endswith('.log')]
    if not log_files:
        print(f"No .log files found in '{input_directory}'.")
        sys.exit(1)

    vdd_data_list = []
    vdd_has_star_list = []
    header_lines_common = None
    footer_lines_common = None

    for log_file in log_files:
        file_path = os.path.join(input_directory, log_file)
        try:
            header_lines, data_block, footer_lines, vdd_data, vdd_has_star = read_log_file(file_path)
            vdd_data_list.append(vdd_data)
            vdd_has_star_list.append(vdd_has_star)
            if header_lines_common is None:
                header_lines_common = header_lines
            if footer_lines_common is None:
                footer_lines_common = footer_lines
        except ValueError as e:
            print(f"Error processing '{log_file}': {e}")

    if not vdd_data_list:
        print("No valid data extracted from log files.")
        sys.exit(1)

    # Aggregate data based on the selected mode
    aggregated_data = aggregate(vdd_data_list, mode=mode)
    aggregated_star = aggregate_star_presence(vdd_has_star_list)

    # Create the aggregated log
    create_aggregated_log(header_lines_common, footer_lines_common, aggregated_data, aggregated_star, mode, output_file)

if __name__ == '__main__':
    main()'''