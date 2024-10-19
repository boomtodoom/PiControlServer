#!/bin/bash

# This script runs the C program with a specified directory and additional arguments.

DIRECTORY=$1  # First argument is the directory
shift          # Shift the arguments to remove the first one
CMD_ARGS=$@    # Store the rest of the arguments

# Path to the compiled C program
C_PROGRAM="./program"  # Adjust the path if necessary

# Run the C program with the directory and other arguments
$C_PROGRAM "$DIRECTORY" $CMD_ARGS
