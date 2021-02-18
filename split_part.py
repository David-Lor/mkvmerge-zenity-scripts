import subprocess

DESCRIPTION = "Outputs a single chunk of the source video.\nTime format: \"hh:mm:ss\".\nIf Start Time is empty, start from beginning.\nIf End Time is empty, end when the video ends."
INFINITE_LOOPING = True  # if True, keep asking for files after processing one, until closing any modal window


def has_yad():
    try:
        subprocess.check_call(["yad", "--version"])
        return True
    except Exception:
        return False


HAS_YAD = has_yad()  # TODO Not working


def run_zenity(*args):
    output = subprocess.check_output(["yad" if HAS_YAD else "zenity", *args])
    return output.decode().strip()


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
    delimiter = "$$$"
    add_entry = "--field" if HAS_YAD else "--add-entry"
    output = run_zenity("--forms", "--title", "mkvmerge split parts",
                        "--text", DESCRIPTION, "--separator", delimiter,
                        add_entry, "Start time",
                        add_entry, "End time"
                       )
    start_time, end_time = output.split(delimiter)
    start_time = normalize_time(start_time)
    end_time = normalize_time(end_time)
    return start_time, end_time


def get_video_output_filename(input_filename):
    # TODO Remove original extension
    return input_filename + ".cut.mkv"


def run_split(input_filename, start, end):
    parts = "parts:" + start + "-" + end
    output_filename = get_video_output_filename(input_filename)

    command = ["mkvmerge", "--split", parts, input_filename, "-o", output_filename]
    print(*["\"{}\"".format(chunk) if " " in chunk else chunk for chunk in command])
    subprocess.call(command)


def main():
    while True:
        try:
            filename = get_filename()
            start, end = get_time_range()
        except subprocess.CalledProcessError:
            print("zenity failed or closed")
            break
        
        run_split(filename, start, end)
        
        if not INFINITE_LOOPING:
            break


if __name__ == "__main__":
    main()
