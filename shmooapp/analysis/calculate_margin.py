
import os


# Plot starts at pos12
#0000000000111
#0123456789012
#    0.980  *!.PPPPPPPPPPPPPPPPPPPPPPPPPPPP (15.000..150.000)
RowPositionAjust = 12

class ShmooMarginCalculator:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.x_operation_center = None
        self.y_operation_center = None
        self.x_operation_outofrange = False
        self.x_step = None
        self.y_step = None
        self.x_margin = None
        self.y_margin = None
        self.plot_lines = []
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None

    def parse_header(self, lines):
        # expect the following:
        #  X-Axis:   Period    [   5.000 .. 150.000 ns  ] step   5.000 ns  (  60.000 ns  )
        #  Y-Axis:   VDD       [   1.300 ..   0.600 V   ] step  -0.020 V   (   0.971 V   )
        # not expect the follwong:
        #       ----- X-Axis: Period -----
        for line in lines:
            if "  X-Axis:" in line:
                # Extract X min and max
                range_part = line.split('[')[1].split(']')[0]
                self.x_min, self.x_max = map(float, range_part.replace('ns', '').split('..'))
                
                # Extract X step
                step_part = line.split("step")[1].split('ns')[0].strip()
                self.x_step = float(step_part)
                
                # Extract X operation center
                #op_center_part = line.split('(')[1].split('ns')[0].strip()
                op_center_part = line.split('(')[1].split('ns')[0].split(')')[0].strip()
                self.x_operation_center = float(op_center_part)
            
                # set flag for out of range
                # case 1) x_operation_center = 0.000
                #   X-Axis:   Period    [  10.000 .. 100.000 ns  ] step   5.000 ns  (   0.000     )
                # else?
                if self.x_min > self.x_operation_center:
                    self.x_operation_outofrange = True

                ## Clamp x_operation_center within [x_min, x_max] based on step direction
                #if self.x_step > 0:
                #    self.x_operation_center = max(self.x_min, min(self.x_max, self.x_operation_center))
                #else:
                #    self.x_operation_center = min(self.x_min, max(self.x_max, self.x_operation_center))

            elif "  Y-Axis:" in line:
                # Extract Y min and max
                range_part = line.split('[')[1].split(']')[0]
                self.y_min, self.y_max = map(float, range_part.replace('V', '').split('..'))
                
                # Extract Y step
                step_part = line.split("step")[1].split('V')[0].strip()
                self.y_step = float(step_part)
                
                # Extract raw Y operation center
                raw_y_center = float(line.split('(')[1].split('V')[0].strip())
                
                # Round Y operation center to the nearest step
                self.y_operation_center = self.round_to_step(raw_y_center, self.y_min, self.y_step)

                # Clamp y_operation_center within [y_min, y_max] based on step direction
                if self.y_step > 0:
                    self.y_operation_center = max(self.y_min, min(self.y_max, self.y_operation_center))
                else:
                    self.y_operation_center = min(self.y_min, max(self.y_max, self.y_operation_center))

        print(f" OpCenter X:{self.x_operation_center}, Y:{self.y_operation_center}")

    def round_to_step(self, value, min_val, step):
        """
        Rounds the given value to the nearest step based on min_val and step size.
        """
        steps = round((value - min_val) / step)
        rounded_value = min_val + steps * step
        return rounded_value

    def parse_plot(self, lines):
        plot_started = False
        for line in lines:
            if "**** Shmoo Plot" in line:
                plot_started = True
                continue
            if plot_started:
                if line.strip().startswith("---"):
                    continue
                if line.strip() == "":
                    continue
                self.plot_lines.append(line.rstrip('\n'))

    def calculate_x_margin(self):
        # Find the line with Y-axis operation center
        operation_center_line = None
        for line in self.plot_lines:
            if f"{self.y_operation_center:.3f}" in line:
                operation_center_line = line
                break
        if not operation_center_line:
            raise ValueError("Y-axis operation center line not found in plot.")

        # Find the position of the first 'P'
        #p_index = operation_center_line.find('P')
        if self.x_operation_outofrange:
            p_index = RowPositionAjust
        else:
            p_index = operation_center_line.find('P')
        if p_index == -1:
            raise ValueError("No 'P' found in Y-axis operation center line.")

        # Calculate the corresponding X value
        # Assuming the plot starts after some fixed columns, e.g., voltage label and symbols
        # You may need to adjust the starting index based on actual file format
        x_start = self.x_min
        step = self.x_step
        num_steps = (self.x_max - self.x_min) / step
        # Calculate the X value based on position
        # This is a simplistic approach; adjust based on actual spacing
        first_p_x = self.x_min + (p_index - RowPositionAjust) * step  # Adjust 10 based on actual indentation
        self.x_margin = self.x_operation_center - first_p_x

    def calculate_y_margin(self):
        # Find the column index for X operation center
        # First, find the X-axis line with '*'
        x_axis_line = None
        for line in self.plot_lines:
            if '*' in line and "X-Axis" not in line:
                x_axis_line = line
                break
            if self.x_operation_outofrange and '+---' in line:
                x_axis_line = line
                break
        if not x_axis_line:
            raise ValueError("X-axis operation center line not found.")

        x_center_index = x_axis_line.find('*')
        if self.x_operation_outofrange:
            x_center_index = x_axis_line.find('+')
        if x_center_index == -1:
            raise ValueError("X-axis operation center '*' not found.")

        # Now, traverse from Y operation center line downwards to count 'P's
        y_margin_count = 0
        start_counting = False
        for line in self.plot_lines:
            if f"{self.y_operation_center:.3f}" in line:
                start_counting = True
            if start_counting:
                # Check the character at x_center_index
                if len(line) > x_center_index and line[x_center_index] == 'P':
                    y_margin_count += 1
                else:
                    break
        self.y_margin = y_margin_count * abs(self.y_step)
        print(f" Margin Y:{self.x_margin}    {x_center_index}")

    def calculate_margins(self):
        with open(self.log_file_path, 'r') as file:
            lines = file.readlines()

        self.parse_header(lines)
        self.parse_plot(lines)
        self.calculate_x_margin()
        self.calculate_y_margin()

        return self.x_margin, self.y_margin
        '''return {
            'X Margin (ns)': self.x_margin,
            'Y Margin (V)': self.y_margin
        }'''

def calculate_files_for_margin(input_directory):
    # Process all .log files in the input directory
    margin_list : list[list[float,float,float,float]] = []
    for filename in sorted(os.listdir(input_directory)):
        if filename.endswith('.log'):
            file_path = os.path.join(input_directory, filename)
            calculator = ShmooMarginCalculator(file_path)
            margin_x, margin_y = calculator.calculate_margins()
            margin_data = [
                calculator.x_operation_center,
                calculator.y_operation_center,
                margin_x,
                margin_y
            ]
            #print(f"X Margin: {margins['X Margin (ns)']} ns")
            #print(f"Y Margin: {margins['Y Margin (V)']} V")
            margin_list.append(margin_data)
    return margin_list