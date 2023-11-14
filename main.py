import importlib.util
import os
import platform
import re
import subprocess
import datetime

# List of required package dependencies
required_packages = ["os", "platform", "moviepy", "tkinter", "menu"]

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

    from moviepy.editor import VideoFileClip
    import tkinter as tk
    from tkinter import filedialog

    timestamp_file = None
    video_file = None
    bitrate = None
    time = None

    # Script Running at
    current_datetime = datetime.datetime.now()


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
            txtVar = None
            mp4Var = None
            bitVar = None
            for file_path in file_paths:
                # Use regular expression to extract the file extension
                matchTxt = re.search(r'\.txt$', file_path)
                matchMp4 = re.search(r'\.mp4$', file_path)
                matchBitrate = re.search(r'\d+k|Nonek$', file_path)
                if matchTxt:
                    txtVar = file_path
                elif matchMp4:
                    mp4Var = file_path
                elif matchBitrate:
                    bitVar = file_path
            return [txtVar, mp4Var, bitVar]


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


    def trim_video(video_file, timestamp_file):
        if not os.path.isfile(video_file):
            print(f"Video file '{video_file}' not found.")
            return

        try:
            with VideoFileClip(video_file) as video_clip:
                with open(timestamp_file, "r") as file:
                    lines = file.readlines()

                for line in lines:
                    # For empty lines don't waste time
                    if line == '\n':
                        continue

                    start_time_str, end_time_str = line.strip().split("-")
                    start_time, end_time = parse_timestamp(start_time_str, end_time_str)

                    output_file = f"clip_{convert_time_format(start_time_str)}_{convert_time_format(end_time_str)} [{bitrate}].mp4"

                    subclip = video_clip.subclip(start_time, end_time)
                    root_path = os.path.dirname(video_file)

                    # Create the subdirectory first
                    sub_directory = os.path.splitext(os.path.basename(video_file))[0]
                    root_path = root_path.replace("/", "\\")

                    # Check if directory exits
                    if not os.path.exists(f"{root_path}\\{sub_directory}"):
                        os.makedirs(f"{root_path}\\{sub_directory}")
                    output = f"{root_path}\\{sub_directory}\\{output_file}"

                    print(f"\033[32mWriting File To: {output}\033[0m")

                    # Check if file already exists
                    if os.path.exists(output):
                        continue

                    if os.access(root_path, os.W_OK):
                        # Specify the temp directory for the video and audio files
                        if bitrate == 'Nonek':
                            subclip.write_videofile(output)
                        else:
                            subclip.write_videofile(output, bitrate=bitrate)

        except Exception as e:
            print(f"\n\033[91mAN ERROR OCCURRED : {e}\033[0m")

        print(f"Trimming complete. Trimmed videos saved as {output_file}.")


    def start_trimming(timestamp_file, video_file):
        if timestamp_file is None or video_file is None:
            print("Both a timestamp file and an MP4 file must be selected before trimming.")
            input("Press [Enter] to continue")
        else:
            trim_video(video_file, timestamp_file)
            input("Press [Enter] to continue")


    def parseTxtFile():
        global timestamp_file
        flag = False
        doItForAll = False
        if not timestamp_file:
            print("No Timestamps File found.")

        with open(timestamp_file, 'r+') as file:
            # Read the content of the file
            file_content = file.read()
            file_lines = file_content.split('\n')

            for index, line in enumerate(file_lines, start=1):
                start_time_str, end_time_str = line.strip().split("-")
                start_time_str, end_time_str = timestamp_formatter(start_time_str, end_time_str)
                start_time, end_time = parse_timestamp(start_time_str, end_time_str)
                if start_time > end_time:
                    flag = True
                    print(f"\n\033[91mline {index} is wrong\033[0m")
                    res = input(f"would you like me to mark it in the file? (enter=y/n | all)")
                    if res.lower() in {'', 'y', 'yes'}:
                        # Mark the line by adding a prefix
                        file_lines[index - 1] = "*" + file_lines[index - 1]
                        # Move the file pointer to the beginning
                        file.seek(0)
                        # Write the updated content back to the file
                        file.write('\n'.join(file_lines))

            if flag:
                print(f"\n\033[91mfile needs to be corrected.\033[0m")
            else:
                print(f"\033[92mfile is correct.\033[0m")
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
            print("8-[q]  Exit")
            print("==============================")
            choice = input("Select an option: ")

            if choice == "1" or choice == "l":
                list_mp4_files_in_directory()
                input("Press [Enter] to continue")
            elif choice == "2" or choice == "t":
                timestamp_file = choose_file()
                if not timestamp_file:
                    print("No file selected. Returning to the main menu.")
                    input("Press [Enter] to continue")
            elif choice == "3" or choice == "v":
                video_file = choose_file()
                if not video_file:
                    print("No video file selected. Returning to the main menu.")
                    input("Press [Enter] to continue")
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
                parseTxtFile()
            elif choice == "7" or choice == "e":
                try:
                    subprocess.run(["notepad.exe", timestamp_file], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error opening the file with Notepad: {e}")
            elif choice == "8" or choice == "q":
                break
            else:
                print("Invalid choice. Please select a valid option.")
                input("Press [Enter] to continue")


    if __name__ == "__main__":
        main()
