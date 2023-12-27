import datetime
import importlib.util
import os
import platform
import re
import subprocess
import textwrap

# List of required package dependencies
required_packages = ["os", "platform", "moviepy", "tkinter", "menu", "tqdm"]

# Check if the required packages are available
missing_packages = [package for package in required_packages if importlib.util.find_spec(package) is None]

if missing_packages:
    print("The following required packages are missing:")
    for package in missing_packages:
        print(package)

    install_missing = input("Do you want to install the missing packages? (y/n): ").strip().lower()
    if install_missing == 'y':
        # Install missing packages using pip
        for package in missing_packages:
            subprocess.run(["pip", "install", package])
        print("Missing packages have been installed.")
    else:
        print("Please install the missing packages manually and try running the script again.")
else:
    # All required packages are available, so you can run the application

    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
    import tkinter as tk
    from tkinter import filedialog

    timestamp_file = None
    video_file = None
    bitrate = None
    default_font = "./IRANYekanBold.ttf"

    # Script Running at
    current_datetime = datetime.datetime.now()


    def manual_progress_bar(total, current_index):
        bar_length = 30
        progress = min(1, current_index / total)  # Ensure progress is between 0 and 1
        block = int(round(bar_length * progress))

        progress_bar = "\033[93m[" + "#" * block + "-" * (bar_length - block) + "]\033[0m"
        percentage = round(progress * 100, 1)

        print(f"\033[93mItem: {current_index} out of {total}\033[0m")
        print(f"Progress: {progress_bar} {percentage}%")


    def clear_screen():
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')


    def read_var_from_file(file_path="./vars.txt"):
        with open(file_path, 'r') as file:
            # Read the content of the file
            file_content = file.read()
            file_paths = file_content.split('\n')

            # return variables
            txt_var = None
            mp4_var = None
            bit_var = None
            for file_path in file_paths:
                # Use regular expression to extract the file extension
                match_txt = re.search(r'\.txt$', file_path)
                match_mp4 = re.search(r'\.mp4$', file_path)
                match_bitrate = re.search(r'\d+k|Nonek$', file_path)
                if match_txt:
                    txt_var = file_path
                elif match_mp4:
                    mp4_var = file_path
                elif match_bitrate:
                    bit_var = file_path
            return [txt_var, mp4_var, bit_var]


    def write_var_on_file(variableDec, file_path="./vars.txt"):
        with open(file_path, 'a') as file:
            # Write the variables to the file
            file.write(variableDec)
            file.write('\n')


    def list_mp4_files_in_directory():
        mp4_files = [file for file in os.listdir() if file.endswith(".mp4")]
        if not mp4_files:
            print("No MP4 files found in the current directory.")
        else:
            print("MP4 files in the current directory:")
            for idx, mp4_file in enumerate(mp4_files, start=1):
                print(f"{idx}. {mp4_file}")
        return mp4_files


    def convert_to_seconds(hours, minutes, seconds):
        int_hours = int(hours)
        int_minutes = int(minutes)
        int_seconds = int(seconds.split('.')[0])
        return (int_hours * 3600) + (int_minutes * 60) + int_seconds


    def parse_timestamp(start_time_str, end_time_str):
        start_time_parts = start_time_str.split(':')
        end_time_parts = end_time_str.split(':')
        start_hours, start_minutes, start_seconds = start_time_parts
        end_hours, end_minutes, end_seconds = end_time_parts
        start_time = convert_to_seconds(start_hours, start_minutes, start_seconds)
        end_time = convert_to_seconds(end_hours, end_minutes, end_seconds)
        return start_time, end_time


    def timestamp_formatter(*args):
        formatted_timestamps = []

        for text in args:
            if isinstance(text, str):
                time_pattern = re.compile(r'\b\d{1,2}:\d{1,2}:\d{1,2}\.\d{1,3}\b')
                final_format = re.sub(f'[^{time_pattern.pattern}]', '', text)
                formatted_timestamps.append(final_format)
            else:
                print(f"Skipping non-string argument: {text}")

        return formatted_timestamps


    def choose_file():
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window
        file_path = filedialog.askopenfilename()
        write_var_on_file(file_path)
        return file_path


    def convert_time_format(time_string):
        # Split the time string by colons and period

        parts = time_string.split(':')
        hours, minutes, seconds_ms = parts[0], parts[1], parts[2]

        # Split seconds and milliseconds
        seconds, milliseconds = seconds_ms.split('.')

        # Format the parts in the desired format
        formatted_time = f"{hours}h{minutes}m{seconds}s"

        return formatted_time


    def position_subtitle(input_str, interval):
        # return '\n'.join(input_str[i:i + interval] for i in range(0, len(input_str), interval))
        return textwrap.fill(input_str, width=interval, break_long_words=False)


    def trim_video(video_file, timestamp_file):
        global bitrate
        global default_font
        subtitle_text = None
        if not os.path.isfile(video_file):
            print(f"Video file '{video_file}' not found.")
            return

        # Load the video
        try:
            with VideoFileClip(video_file) as video_clip:
                with open(timestamp_file, "r", encoding='utf-8') as file:
                    lines = file.readlines()

                for index, line in enumerate(lines):
                    # For empty lines don't waste time
                    if line == '\n':
                        continue

                    # Count Dashes to decide if text has subtitle
                    dash_counts = line.count("-")

                    if dash_counts == 1:
                        start_time_str, end_time_str = line.strip().split("-")
                    if dash_counts > 1:
                        start_time_str, end_time_str, subtitle_text = line.strip().split("-", 2)

                    # check for a long text
                    if subtitle_text:
                        subtitle_text = position_subtitle(subtitle_text, 62)

                    # if empty, put .
                    if subtitle_text == '':
                        subtitle_text = '.'

                    start_time, end_time = parse_timestamp(start_time_str, end_time_str)

                    output_file = f"clip_{convert_time_format(start_time_str)}_{convert_time_format(end_time_str)} [{bitrate}].mp4"

                    subclip = video_clip.subclip(start_time, end_time)
                    file_direname = os.path.dirname(video_file)

                    # Create the subdirectory first
                    sub_directory = os.path.splitext(os.path.basename(video_file))[0]
                    file_direname = file_direname.replace("/", "\\")
                    path_before_to_file = f"{file_direname}\\{sub_directory}"
                    whole_path = f"{file_direname}\\{sub_directory}\\{bitrate}"

                    # Check if directories exits
                    if not os.path.exists(path_before_to_file):
                        os.makedirs(path_before_to_file)
                    if not os.path.exists(whole_path):
                        os.makedirs(whole_path)

                    output = f"{whole_path}\\{output_file}"

                    # Check if file already exists
                    if os.path.exists(output):
                        continue

                    if os.access(file_direname, os.W_OK):
                        # Specify the temp directory for the video and audio files
                        if bitrate == 'Nonek':
                            if dash_counts == 1:
                                subclip.write_videofile(output)
                            if dash_counts > 1:
                                text_clip = TextClip(subtitle_text,
                                                     fontsize=52, color="white", bg_color="black", font=default_font)
                                text_clip = text_clip.set_opacity(0.4)
                                text_clip = text_clip.set_duration(subclip.duration)
                                text_clip = text_clip.set_position(("center", "bottom"))
                                final_clip = CompositeVideoClip([subclip, text_clip])
                                final_clip.write_videofile(output)
                        else:
                            if dash_counts == 1:
                                subclip.write_videofile(output, bitrate=bitrate)
                            if dash_counts > 1:
                                text_clip = TextClip(subtitle_text,
                                                     fontsize=52, bg_color="black", color="white",
                                                     font=default_font)
                                text_clip = text_clip.set_opacity(0.4)
                                text_clip = text_clip.set_duration(subclip.duration)
                                text_clip = text_clip.set_position(("center", "bottom"))
                                final_clip = CompositeVideoClip([subclip, text_clip])
                                final_clip.write_videofile(output, bitrate=bitrate)

                    # Progress ratio
                    print(f"\033[92mitem {index} out of {len(lines)} processing successful\033[0m")
                    manual_progress_bar(len(lines), index)

        except Exception as e:
            print(f"\n\033[91mERROR: {e}\033[0m")


    def start_trimming(timestamp_file, video_file):
        if timestamp_file is None or video_file is None:
            print("Both a timestamp file and an MP4 file must be selected before trimming.")
            input("")
        else:
            trim_video(video_file, timestamp_file)
            input("")


    def parse_text_file():
        global timestamp_file
        flag = False

        if not timestamp_file:
            print("No Timestamps File found.")

        with open(timestamp_file, 'r+', encoding='utf-8') as file:
            # Read the content of the file
            file_content = file.read()
            file_lines = file_content.split('\n')

            for index, line in enumerate(file_lines, start=1):
                if line == '' or line == '\n':
                    continue

                # Count Dashes to decide if text has subtitle
                dash_counts = line.count("-")

                if dash_counts == 1:
                    start_time_str, end_time_str = line.strip().split("-")
                if dash_counts > 1:
                    start_time_str, end_time_str, subtitle_text = line.strip().split("-", 2)
                    if subtitle_text == '':
                        file_lines[index - 1] = "*empty " + file_lines[index - 1]

                start_time_str, end_time_str = timestamp_formatter(start_time_str, end_time_str)
                start_time, end_time = parse_timestamp(start_time_str, end_time_str)
                if start_time >= end_time:
                    flag = True
                    print(f"\n\033[91mline {index} is wrong.\033[0m")
                    # Mark the line by adding a prefix
                    file_lines[index - 1] = "*time_diff " + file_lines[index - 1]
                    # Move the file pointer to the beginning
                    file.seek(0)
                    # Write the updated content back to the file
                    file.write('\n'.join(file_lines))
                    print(f"\n\033[91mline {index} is marked.\033[0m")

            if flag:
                print(f"\n\033[91mfile needs to be corrected.\033[0m")
            else:
                print(f"\033[92mfile is correct.\033[0m")
        input()


    def generate_file_sample():
        global timestamp_file
        global video_file
        file_name = os.path.splitext(os.path.basename(video_file))[0] + '.txt'
        root_path = os.path.dirname(video_file)
        whole_path = f"{root_path}\\{file_name}"
        if os.path.exists(whole_path):
            print('\033[93mTimestamp File Exists.\033[0m')

            delete = input('\033[93mwould you like to regenerate it? (y/n)\033[0m\n')
            if delete == 'y':
                try:
                    os.remove(whole_path)
                    print(f"The file '{whole_path}' has been successfully removed.")
                except Exception as e:
                    print(f"An error occurred: {e}")

        if not os.path.exists(whole_path):
            with open(whole_path, 'w') as file:
                for i in range(0, 25):
                    start_time = f"00:{i:02d}:00.00"
                    end_time = f"00:{i:02d}:00.00"
                    time_interval = f"{start_time}-{end_time}"
                    file.write(f'{time_interval}\n')

            print(f"\033[92m{file_name} generated.\033[0m")

        res = input('would you like to use it? (enter=y/n)')
        if res == 'y' or res == '':
            timestamp_file = whole_path
            write_var_on_file(timestamp_file)
            print(f"\033[92mit's been used.\033[0m")
        input()


    def main():
        global timestamp_file
        global video_file
        global bitrate
        while True:
            if os.path.isfile('./vars.txt'):
                timestamp_file, video_file, bitrate = read_var_from_file()
            clear_screen()
            print("Video Trimmer")
            print(f"==== {current_datetime.time()} | {current_datetime.date()} =========")
            print("Previous Selections:")
            print("* txt file:", timestamp_file)
            print("* mp4 file:", video_file)
            print("* bitrate:", bitrate, "\n")
            print("1-[l] List all the MP4 files in the current directory")
            print("2-[t] Use the following txt file for range timestamps")
            print("3-[v] Use the following MP4 file as input")
            print("4-[b] Set the bitrate")
            print("5-[s] Start Trimming")
            print("6-[p] Parse and Check Timestamps File")
            print("7-[e] Edit Timestamps File")
            print("8-[g] Generate Timestamp File Sample")
            print("9-[q] Exit")
            print("==============================")
            choice = input("Select an option: ")

            if choice == "1" or choice == "l":
                list_mp4_files_in_directory()
                input("")
            elif choice == "2" or choice == "t":
                timestamp_file = choose_file()
                if not timestamp_file:
                    print("No file selected. Returning to the main menu.")
                    input("")
            elif choice == "3" or choice == "v":
                video_file = choose_file()
                if not video_file:
                    print("No video file selected. Returning to the main menu.")
                    input("")
            elif choice == "4" or choice == "b":
                print("\033[93mIf Skipped, It Will Uses The Default (None)\033[0m")
                print("\033[93mbitrate: 1500k is moderate\033[0m")
                bitrate = input("Enter Bitrate: ")
                if not bitrate:
                    bitrate = None
                write_var_on_file(f"{bitrate}k")
            elif choice == "5" or choice == "s":
                start_trimming(timestamp_file, video_file)
            elif choice == "6" or choice == "p":
                parse_text_file()
            elif choice == "7" or choice == "e":
                try:
                    subprocess.Popen(["explorer", os.path.dirname(video_file).replace("/", "\\")], shell=True)
                    subprocess.run(["notepad.exe", timestamp_file], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error opening the file with Notepad: {e}")
            elif choice == "8" or choice == "g":
                generate_file_sample()
            elif choice == "9" or choice == "q":
                break
            else:
                print("Invalid choice. Please select a valid option.")
                input("")


    if __name__ == "__main__":
        main()
