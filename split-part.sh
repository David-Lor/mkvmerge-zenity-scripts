#!/bin/bash

set -e

DESCRIPTION="Outputs a single chunk of the source video.\nTime format: \"hh:mm:ss\".\nIf Start Time is empty, start from beginning.\nIf End Time is empty, end when the video ends."

FILE="$1"

if [ -z "$FILE" ]
then
    FILE=$(zenity --file-selection --title="Select a video file")
fi

OUTPUT=$(zenity --forms \
            --title="mkvmerge split parts" \
            --text="$DESCRIPTION" \
            --separator="_" \
            --add-entry="Start time" \
            --add-entry="End time")

START_TIME=$(echo $OUTPUT | cut -f1 -d"_")
END_TIME=$(echo $OUTPUT | cut -f2 -d"_")

if [ -z $START_TIME ]
then
    START_TIME="-"
fi
if [ -z $END_TIME ]
then
    END_TIME="-"
fi

TIME_PART="$START_TIME$END_TIME"

if [ $TIME_PART == "--" ]
then
    echo "No time parts given!"
    exit 1
fi

FILE_NO_EXTENSION=${FILE%%.*}
OUTPUT_FILE="$FILE_NO_EXTENSION.cut.mkv"

set -ex
mkvmerge --split parts:$TIME_PART "$FILE" -o "$OUTPUT_FILE"
