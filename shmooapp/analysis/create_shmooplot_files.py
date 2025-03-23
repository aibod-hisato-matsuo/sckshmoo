import os
import re

def sanitize_filename(filename):
    """
    Sanitizes the filename by replacing illegal characters with underscores.

    Args:
        filename (str): The original filename.

    Returns:
        str: The sanitized filename.
    """
    return re.sub(r'[\\/:"*?<>|]+', "_", filename)

def extract_test_results(log_file_path, output_dir) -> list:
    """
    Extracts test results from the log file and saves each result to a separate file
    named using the input file name, TITLE information, and site number.
    It also removes unwanted rows after a specific separator.

    Args:
        log_file_path (str): Path to the input log file.
        output_dir (str): Directory where the extracted files will be saved.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the base name of the log file without extension
    base_filename = os.path.splitext(os.path.basename(log_file_path))[0]

    basedir = f"{base_filename}"
    output_basedir = os.path.join(output_dir, basedir)
    if not os.path.exists(output_basedir):
        os.makedirs(output_basedir)

    with open(log_file_path, 'r') as file:
        content = file.read()

    # Define the main separator for test sections
    test_separator_regex = r'[-]{10,}\s*TestMethod\s+Shmoo\s*[-]{10,}'
    
    # Define the unwanted separators
    unwanted_separator_v = r'^\s*V\s+\+.*$'
    unwanted_separator_site = r'^Site\s+\d+:.*$'
    lines_to_remove_after_v = 3  # Existing rule for 'V' lines
    unwanted_warning = r'^WARNING'
    unwanted_comment = r'^#'

    # Split the content into individual test sections based on the main separator, do not contain the first, as it is header
    test_sections = re.split(test_separator_regex, content)[1:]

    # Initialize a list to hold cleaned test sections
    cleaned_test_sections = []

    # subdirs
    subdirs = set()

    for section in test_sections:
        lines = section.splitlines()
        cleaned_lines = []
        skip_lines = 0
        skip_mode = False  # Flag to control skipping after 'Site' separator

        for line in lines:
            if skip_lines > 0:
                skip_lines -= 1
                #continue

            if re.match(unwanted_separator_v, line):
                # Found the 'V' unwanted separator; skip this line and the next three lines
                skip_lines = lines_to_remove_after_v
                #continue

            if re.match(unwanted_separator_site, line):
                # Found the 'Site' unwanted separator; stop processing further lines in this section
                skip_mode = True
                break  # Exit the loop as the rest of the lines are unwanted

            if re.match(unwanted_warning, line):
                continue

            if re.match(unwanted_comment, line):
                continue

            cleaned_lines.append(line)

        # Reconstruct the section after removing unwanted lines
        cleaned_section = "\n".join(cleaned_lines).rstrip()

        # Proceed only if the section is not empty after removing unwanted content
        if cleaned_section.strip():
            cleaned_test_sections.append(cleaned_section)

    for section in cleaned_test_sections:
        # Search for the TITLE line
        title_match = re.search(r'TITLE\s+:\s+([^\s]+)', section)
        if title_match:
            title = title_match.group(1).strip()
            # Sanitize the title to create a valid filename part
            sanitized_title = sanitize_filename(title)
        else:
            # If TITLE not found, use a default placeholder
            print('Warning: TITLE not found in a section. Using "NoTitle".')
            sanitized_title = "NoTitle"

        # Search for the Site number
        site_match = re.search(r'---\s+site\s+(\d+)\s+/\s+\d+\s+\(', section, re.IGNORECASE)
        if site_match:
            site_number = site_match.group(1)
        else:
            # If site number not found, skip this section
            print('Warning: Site number not found in a section. Skipping...')
            continue

        subdir = f"{sanitized_title}"
        output_subdir = os.path.join(output_basedir, subdir)
        if not os.path.exists(output_subdir):
            os.makedirs(output_subdir)
        
        subdirs.add(output_subdir) #

        # Create the filename using the base filename, sanitized title, and site number
        filename = f"{base_filename}_{sanitized_title}_site{site_number}.log"
        output_path = os.path.join(output_subdir, filename)

        # Write the section to the new file
        with open(output_path, 'w') as outfile:
            #outfile.write(cleaned_section.strip())
            outfile.write(section.strip())

        print(f'Extracted: {filename}')
    
    for subdir in subdirs:
        print(f"{subdir}")
    return list(subdirs)