import os
import re
from datetime import date
from pathlib import Path

# logfile handling
def create_yyyymmdd_today():
    today = date.today()
    return today.strftime("%Y%m%d")

def generate_basedir_name_with_date(filename):
    yyyymmdd = create_yyyymmdd_today()
    return f"{yyyymmdd}-{filename}"

def extract_logfilename_from_path(file_path):
    filename = os.path.splitext(os.path.basename(file_path))[0]
    return f"{filename}"

def generate_arcdir(arcroot,basedir):
    if not os.path.exists(arcroot):
        os.makedirs(arcroot)
    arcdir = generate_basedir_name_with_date(basedir)
    archive_basedir = os.path.join(arcroot, arcdir)
    return archive_basedir

def filter_original_dir_only(p:Path):
    excluded_suffixes = ('.AND_XOR', '.OR_XOR', '.MajorityVote_XOR')
    return not p.name.endswith(excluded_suffixes)

def collect_archived_logs(arcroot: str):
    arcroot_path = Path(arcroot)
    print(f"{arcroot}")
    if not arcroot_path.is_dir():
        raise FileNotFoundError(f"The specified arcroot directory does not exist or is not a directory: {arcroot}")
    subdirs = [str(p) for p in arcroot_path.iterdir() if p.is_dir() and not p.is_symlink() and filter_original_dir_only(p)]
    return subdirs

def generate_aggfile_name(input_directory,mode):
    out_dirname = Path(input_directory).parent
    out_basename = Path(input_directory).name
    out_filename = out_basename + "_aggregated_" + mode + ".log"
    output_file = os.path.join(out_dirname,out_filename)
    return output_file


# plot handling
VDD_PATTERNS = ["VDD", "Vvdd12", "Vvdd12_otp"]  # Add more patterns as needed

def sanitize_filename(filename):
    """
    Sanitizes the filename by replacing illegal characters with underscores.

    Args:
        filename (str): The original filename.

    Returns:
        str: The sanitized filename.
    """
    return re.sub(r'[\\/:"*?<>|]+', "_", filename)

def extract_y_axis_info(lines):
    """
    Extracts Max VDD, Min VDD, and Step from the Y-Axis meta information.

    Args:
        lines (list): List of lines from the log file.

    Returns:
        tuple: (max_vdd, min_vdd, step)
    """
    # Define acceptable VDD patterns
    vdd_patterns = VDD_PATTERNS

    # Create a regex pattern that matches any of the patterns in vdd_patterns
    # The re.escape ensures that any special characters in the patterns are escaped
    vdd_regex = "|".join(map(re.escape, vdd_patterns))

    y_axis_pattern = re.compile(
        rf"Y-Axis\s*:\s*(?:{vdd_regex})\s*\[\s*([\d.]+)\s*\.\.\s*([\d.]+)\s*V\s*\]\s*step\s*([-+]?\d*\.\d+|\d+)\s*V",
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

