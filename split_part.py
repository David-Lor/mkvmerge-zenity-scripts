import subprocess

DESCRIPTION = "Outputs a single chunk of the source video.\nTime format: \"hh:mm:ss\".\nIf Start Time is empty, start from beginning.\nIf End Time is empty, end when the video ends."
DEBUG_COMMAND = False
HAS_YAD = None  # Set to True/False to force using yad/zenity. If None, autodetect yad


def has_yad():
    try:
        status_code = subprocess.call(["yad", "--version"])
        return status_code in (0, 252)
    except Exception:
        return False


HAS_YAD = has_yad() if HAS_YAD is None else HAS_YAD


def debug_command(command, bypass_setting=False):
    if DEBUG_COMMAND or bypass_setting:
        print(*["\"{}\"".format(chunk) if " " in chunk else chunk for chunk in command])


def run_zenity(*args):
    command = ["yad" if HAS_YAD else "zenity", *args]
    if HAS_YAD:
        command.append("--center")
    debug_command(command)
    output = subprocess.check_output(command)
    return output.decode().strip()


def do_question(title, text, failure=False):
    image = "dialog-warning" if failure else "dialog-question"
    if HAS_YAD:
        command = ["--image", image, "--title", title, "--text", text, "--button=gtk-yes:0", "--button=gtk-no:1"]
    else:
        command = ["--question", "--image", image, "--title", title, "--text", text]

    try:
        run_zenity(*command)
        return True
    except subprocess.CalledProcessError:
        return False


def get_filename():
    return run_zenity("--file-selection", "--title", "Select a video file")


def normalize_time(time_str):
    """Clean and normalize time inputs.
    Allows inputs of format: "ss", "mm:ss", "hh:mm:ss" - and partial numbers without leading zeros.
    The output is always "hh:mm:ss".
    Empty strings are directly returned, as they mean use the start/end time of the video.
    """
    time_str = time_str.strip()
    if not time_str:
        return time_str
    
    chunks = time_str.split(":")    
    chunks = [chunk.zfill(2) for chunk in chunks]

    while len(chunks) < 3:
        chunks.insert(0, "00")
    
    return ":".join(chunks)


def get_time_range():
    delimiter = "#"
    form = "--form" if HAS_YAD else "--forms"
    add_entry = "--field" if HAS_YAD else "--add-entry"
    output = run_zenity(form, "--title", "mkvmerge split parts",
                        "--text", DESCRIPTION, "--separator", delimiter,
                        add_entry, "Start time",
                        add_entry, "End time"
                       )
    chunks = output.split(delimiter)
    start_time = normalize_time(chunks[0])
    end_time = normalize_time(chunks[1])
    return start_time, end_time


def get_video_output_filename(input_filename):
    # TODO Remove original extension
    return input_filename + ".cut.mkv"


def run_split(input_filename, start, end):
    parts = "parts:" + start + "-" + end
    output_filename = get_video_output_filename(input_filename)

    command = ["mkvmerge", "--split", parts, input_filename, "-o", output_filename]
    debug_command(command, bypass_setting=True)
    output = subprocess.check_output(command)
    return output.decode().strip()


def show_result(output, failure=False):
    result_text = "failed - output" if failure else "output"
    text = "mkvmerge {}:\n\n{}\n\nDo you want to process another video?".format(result_text, output)
    return do_question(title="mkvmerge result", text=text, failure=failure)


def main():
    while True:
        try:
            filename = get_filename()
            start, end = get_time_range()
        except subprocess.CalledProcessError:
            print("zenity failed or closed")
            break

        try:
            output = run_split(filename, start, end)
            failed = False
        except subprocess.CalledProcessError as ex:
            output = ex.output.decode().strip()
            failed = True
        except FileNotFoundError:
            show_result("mkvmerge not found!", failure=True)
            exit(1)

        keep_running = show_result(output, failure=failed)

        if not keep_running:
            break


if __name__ == "__main__":
    main()
