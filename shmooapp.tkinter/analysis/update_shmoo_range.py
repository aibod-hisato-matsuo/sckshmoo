import re
import os

def calculate_ns_range(shmoo_str, start_ns=5.0, step_ns=5.0):
    """
    Calculates the minimum and maximum ns values where 'P' occurs in the shmoo string.

    :param shmoo_str: The string containing 'P' characters representing pass.
    :param start_ns: Starting ns value.
    :param step_ns: Step size in ns.
    :return: Tuple of (min_ns, max_ns) or None if no 'P' found.
    """
    min_ns = None
    max_ns = None
    for index, char in enumerate(shmoo_str):
        if char == 'P':
            current_ns = start_ns + index * step_ns
            if min_ns is None:
                min_ns = current_ns
            max_ns = current_ns
    if min_ns is not None and max_ns is not None:
        return (min_ns, max_ns)
    return None

#def update_shmoo_log(file_path, output_path):
def update_shmoo_log(file_path):
    """
    Reads the Shmoo Plot log file, updates the min and max ns values for each voltage line,
    and writes the changes back to the file.

    :param file_path: Path to the Shmoo Plot log file.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    shmoo_section = False
    updated_lines = []

    for line in lines:
        # Detect the start of the Shmoo Plot section
        if '**** Shmoo Plot' in line:
            shmoo_section = True
            updated_lines.append(line)
            continue

        if shmoo_section:
            # Detect the end of the Shmoo Plot section
            #        V   +---------+*--------+--------+
            end_matched = re.match(r'^\s*V\s++.*', line)
            if end_matched:
                shmoo_section = False
                updated_lines.append(line)
                continue

            # Match lines with voltage and shmoo data
            #    0.740   !......P.PPPPPPPPPPPPPPPPPPPPP (40.000..50.000)
            match = re.match(r'^(\s*\d+\.\d+)[\s*]+([!\.P]+)\s+\(([^)]+)\)', line)
            if match:
                voltage = match.group(1)
                shmoo_str = match.group(2)
                existing_range = match.group(3)

                # Calculate min and max ns
                ns_range = calculate_ns_range(shmoo_str)
                if ns_range:
                    min_ns, max_ns = ns_range
                    new_range = f"({min_ns:.3f}..{max_ns:.3f})"
                    
                    # Replace the existing range with the new range
                    new_line = re.sub(r'\([^)]+\)', new_range, line)
                    updated_lines.append(new_line)
                else:
                    # If no 'P' found, keep the line unchanged
                    updated_lines.append(line)
            else:
                # Lines that do not match the shmoo data pattern
                updated_lines.append(line)
        else:
            # Lines outside the Shmoo Plot section are kept unchanged
            updated_lines.append(line)

    # Write the updated lines back to the file
    #with open(output_path, 'w') as file:
    with open(file_path, 'w') as file:
        file.writelines(updated_lines)

    print(f"Updated Range: {os.path.basename(file_path)}")

def update_files_for_range(input_directory):
    # Process all .log files in the input directory
    for filename in sorted(os.listdir(input_directory)):
        if filename.endswith('.log'):
            file_path = os.path.join(input_directory, filename)
            update_shmoo_log(file_path)



'''def process_folder(input_folder, output_folder):
    """
    Processes all .log files in the input folder and writes updated files to the output folder.

    :param input_folder: Path to the input folder containing log files.
    :param output_folder: Path to the output folder where updated log files will be saved.
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)

    # Create the output folder if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Iterate over all .log files in the input folder
    for log_file in input_path.glob('*.log'):
        output_file = output_path / log_file.name
        print(f"Processing '{log_file}'...")
        update_shmoo_log(log_file, output_file)
        print(f"Updated file saved to '{output_file}'.\n")'''

'''if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Shmoo Plot log files with calculated min and max ns values.")
    parser.add_argument("input_folder", help="Path to the input folder containing Shmoo Plot log files.")
    parser.add_argument("output_folder", help="Path to the output folder where updated log files will be saved.")

    args = parser.parse_args()

    process_folder(args.input_folder, args.output_folder)
    print("All files have been processed successfully.")

if __name__ == "__main__":
    log_file_path = 'work/D5700_FF_CP1_SHMOO_d5700_ufunc_pg_d_imx224_v768_d3_40_m4_raw_k_v1_02_site4.log'
    update_shmoo_log(log_file_path)
    print(f"Shmoo Plot log '{log_file_path}' has been updated with calculated min and max ns values.")'''
