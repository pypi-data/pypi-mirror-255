import re
import tkinter as tk
from tkinter import filedialog
from datetime import datetime


def two_files_compare_strings(str1, str2):
    lines1 = str1.strip().split('\n')
    lines2 = str2.strip().split('\n')
    min_lines = min(len(lines1), len(lines2))

    output_str = ""
    for i in range(min_lines):
        seconds1 = extract_seconds(lines1[i])
        seconds2 = extract_seconds(lines2[i])
        if seconds1 is not None and seconds2 is not None:
            difference = abs(seconds1 - seconds2)
            if difference > 1:
                output_str += f"{i + 1}: {difference} seconds difference\n"
        else:
            output_str += f"Line {i + 1}: Unable to extract seconds from one or both strings\n"
    return output_str


def two_files_process_file(filepath):
    pattern1 = re.compile(r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})")
    pattern2 = re.compile(r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}) (AM|PM)")

    output_str = ""
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            previous_timestamp = None
            for index, line in enumerate(lines, 1):
                if 'msg' not in line and 'Matrix' not in line:
                    continue

                match1 = pattern1.search(line)
                match2 = pattern2.search(line)

                if match1:
                    if 'movement' in line:
                        continue
                    current_timestamp = datetime.strptime(match1.group(1), '%Y-%m-%d %H:%M:%S')
                elif match2:
                    if 'Arduino' in line:
                        continue
                    current_timestamp = datetime.strptime(match2.group(1) + " " + match2.group(2),
                                                          "%m/%d/%Y %I:%M:%S %p")
                else:
                    output_str += f"Could not parse time from line {index}: {line}\n"
                    continue

                if previous_timestamp:
                    delta = (current_timestamp - previous_timestamp).total_seconds()
                    output_str += f"{index - 1}. {int(delta)} seconds\n"
                previous_timestamp = current_timestamp
    except Exception as e:
        output_str += str(e)
    return output_str


def extract_seconds(line):
    match = re.search(r'(\d+(?:\.\d+)?)\s*seconds', line)
    if match:
        return float(match.group(1))
    return None


def compare_strings(str1, str2):
    lines1 = str1.strip().split('\n')
    lines2 = str2.strip().split('\n')
    min_lines = min(len(lines1), len(lines2))

    output_str = ""
    for i in range(min_lines):
        seconds1 = extract_seconds(lines1[i])
        seconds2 = extract_seconds(lines2[i])
        if seconds1 is not None and seconds2 is not None:
            difference = abs(seconds1 - seconds2)
            if difference > 1:
                output_str += f"{i + 1}: {difference} seconds difference\n"
    return output_str


def process_file(filepath):
    output_str = ""
    lines_list = []
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            previous_timestamp = None
            for index, line in enumerate(lines, 1):
                match = re.search(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})', line)
                if match:
                    current_timestamp = datetime.strptime(match.group(1), '%m/%d/%Y %H:%M:%S')
                    if previous_timestamp:
                        delta = (current_timestamp - previous_timestamp).total_seconds()
                        output_str += f"{index - 1}. {int(delta)} seconds\n"
                    previous_timestamp = current_timestamp
                    lines_list.append(line)
    except Exception as e:
        output_str += str(e)
    return output_str, lines_list


def post_process_file(lines_list):
    for i in range(len(lines_list) - 1):
        line1 = lines_list[i]
        line2 = lines_list[i + 1]
        match1 = re.search(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})', line1)
        match2 = re.search(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})', line2)
        if match1 and match2:
            timestamp1 = datetime.strptime(match1.group(1), '%m/%d/%Y %H:%M:%S')
            timestamp2 = datetime.strptime(match2.group(1), '%m/%d/%Y %H:%M:%S')
            delta = (timestamp2 - timestamp1).total_seconds()
            if delta > 50:
                print(
                    f"{i + 1}-{i + 2}: {delta} secs [{timestamp1.strftime('%H:%M:%S')} to "
                    f"{timestamp2.strftime('%H:%M:%S')}]")


def browse_file(file_var):
    filepath = filedialog.askopenfilename()
    file_var.set(filepath)


def main():
    root = tk.Tk()
    root.title('File Comparison')

    yield_run_file = tk.StringVar()
    arduino_run_file = tk.StringVar()

    tk.Label(root, text='Select arduino_run file').pack()
    tk.Entry(root, textvariable=yield_run_file, width=50).pack()
    tk.Button(root, text='Browse', command=lambda: browse_file(yield_run_file)).pack()

    tk.Label(root, text='Select yield_run file').pack()
    tk.Entry(root, textvariable=arduino_run_file, width=50).pack()
    tk.Button(root, text='Browse', command=lambda: browse_file(arduino_run_file)).pack()

    tk.Button(root, text='Compare two Arduino triggers',
              command=lambda: print(compare_strings(two_files_process_file(yield_run_file.get()),
                                                    two_files_process_file(arduino_run_file.get())))).pack()

    tk.Button(root, text='Check machine stops',
              command=lambda: (print(compare_strings(process_file(yield_run_file.get())[0],
                                                     process_file(arduino_run_file.get())[0])),
                               post_process_file(process_file(yield_run_file.get())[1]))).pack()

    root.mainloop()


if __name__ == "__main__":
    main()

