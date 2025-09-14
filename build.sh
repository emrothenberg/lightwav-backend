#!/bin/bash

# Function to display usage instructions
show_usage() {
    echo "Usage: build.sh [option]"
    echo "Options:"
    echo "  -w    Build for Windows using WINE."
    echo "  -l    Build for Linux."
    echo "  -a    Build for all platforms."
    echo "  -h    Show this help message."
    echo "If no option is provided, the script defaults to building for all platforms."
}

build_windows() {
    echo "Building for Windows..."
    WINEPREFIX=~/winehome/py11 wine build.bat
    rm ../frontend-electron/usr/bin/lightwav.exe
    cp dist/lightwav.exe ../frontend-electron/usr/bin
    echo "Finished building for Windows."
}

build_linux() {
    echo "Building for Linux..."
    pyinstaller --clean -F __main__.py -n lightwav -y
    rm ../frontend-electron/usr/bin/lightwav
    cp dist/lightwav ../frontend-electron/usr/bin
    echo "Finished building for Linux."
}

# Check the argument
if [[ "$1" == "-w" ]]; then
    build_windows
elif [[ "$1" == "-l" ]]; then
    build_linux
elif [[ "$1" == "-a" || -z "$1" ]]; then
    echo "Building for all platforms..."
    build_linux & build_windows & wait
elif [[ "$1" == "-h" ]]; then
    show_usage
else
    echo "Invalid option. Use -h for help."
fi

