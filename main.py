import importlib.util
import os
import platform
import re
import subprocess

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
            for file_path in file_paths:
                # Use regular expression to extract the file extension
                matchTxt = re.search(r'\.txt$', file_path)
                matchMp4 = re.search(r'\.mp4$', file_path)
                if matchTxt:
                    txtVar = file_path
                elif matchMp4:
                    mp4Var = file_path
            return [txtVar, mp4Var]


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


    def choose_file():
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window
        file_path = filedialog.askopenfilename()
        write_var_on_file(file_path)
        return file_path


    def trim_video(video_file, timestamp_file):
        if not os.path.isfile(video_file):
            print(f"Video file '{video_file}' not found.")
            return

        try:
            with VideoFileClip(video_file) as video_clip:
                with open(timestamp_file, "r") as file:
                    lines = file.readlines()

                for line in lines:
                    start_time_str, end_time_str = line.strip().split("-")
                    start_time, end_time = parse_timestamp(start_time_str, end_time_str)
                    output_file = f"trimmed_{start_time_str}_{end_time_str}.mp4"

                    subclip = video_clip.subclip(start_time, end_time)
                    rootPath = os.path.dirname(video_file)
                    output = f"{rootPath}/{output_file}"
                    print(f"\033[32mWriting File To: {output}\033[0m")

                    if os.access(rootPath, os.W_OK):
                        # Specify the temp directory for the video and audio files
                        subclip.write_videofile(output)

        except Exception as e:
            print(f"\n\033[91mAN ERROR OCCURRED : {e}\033[0m")

        print("Trimming complete. Trimmed videos saved as 'trimmed_<start_time>_<end_time>.mp4'.")


    def start_trimming(timestamp_file, video_file):
        if timestamp_file is None or video_file is None:
            print("Both a timestamp file and an MP4 file must be selected before trimming.")
            input("Press Enter to continue...")
        else:
            trim_video(video_file, timestamp_file)
            input("Press Enter to continue...")


    def main():
        global timestamp_file
        global video_file
        if os.path.isfile('./vars.txt'):
            timestamp_file, video_file = read_var_from_file()
        while True:
            clear_screen()
            print("Welcome to Video Trimmer")
            print("==============================")
            print("I can use previous files, if so just use 4")
            print("* txt file:", timestamp_file)
            print("* mp4 file:", video_file)
            print("1- List all the MP4 files in the current directory")
            print("2- Use the following txt file for range timestamps")
            print("3- Use the following MP4 file as input")
            print("4- Start Trimming")
            print("5- Exit")
            print("==============================")
            choice = input("Select an option: ")

            if choice == "1":
                list_mp4_files_in_directory()
                input("Press Enter to continue...")
            elif choice == "2":
                timestamp_file = choose_file()
                if not timestamp_file:
                    print("No file selected. Returning to the main menu.")
                    input("Press Enter to continue...")
            elif choice == "3":
                video_file = choose_file()
                if not video_file:
                    print("No video file selected. Returning to the main menu.")
                    input("Press Enter to continue...")
            elif choice == "4":
                start_trimming(timestamp_file, video_file)
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please select a valid option.")
                input("Press Enter to continue...")


    if __name__ == "__main__":
        main()
