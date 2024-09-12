# AppImageManager

AppImageManager is a simple command-line interface (CLI) application written in Python that allows you to manage AppImage applications efficiently. This tool provides GNOME integration by handling `.desktop` files, making it easier to install, list, show details of, and delete AppImage applications.

## Features

- **GNOME Integration**: Automatically handles `.desktop` files for seamless integration with your GNOME desktop environment.
- **Self-Contained**: The entire application is contained within a single Python file with no external dependencies (only requires Python 3).
- **Simple CLI**: Easy-to-use command-line interface for managing your AppImage applications.

## Installation

To use AppImageManager, simply download the `AppImageManager.py` file and ensure you have Python 3 installed on your system. You can run the application directly from the command line.

## Usage

To get started, you can view the help message by running:

```bash
./AppImageManager.py --help
```

### Command Overview

The following commands are available:

```plaintext
usage: AppImageManager.py [-h] {list,show,delete,install} ...

A simple CLI to manage AppImage applications.

positional arguments:
  {list,show,delete,install}
    list                List all installed AppImages
    show                Show details of a specific AppImage
    delete              Delete a specific AppImage
    install             Install AppImage

options:
  -h, --help            show this help message and exit
```

### Commands

**Install an AppImage**:
   To install a new AppImage, use the `install` command:
   ```bash
   ./AppImageManager.py install <path_to_appimage>
   ```
**List Installed AppImages**:
To list all installed AppImages, use the `list` command:
```bash
./AppImageManager.py list
```
**Show Details of a Specific AppImage**:
To view details of a specific AppImage, use the `show` command followed by the ID obtained from the `list` command:
```bash
./AppImageManager.py show <ID>
```
**Delete a Specific AppImage**:
To delete a specific AppImage, use the `delete` command followed by the ID obtained from the `list` command:
```bash
./AppImageManager.py delete <ID>
```

### Important Notes

- The `delete` and `show` commands require the ID provided by the `list` command, not the AppImage name.

### File Locations

- **AppImage Directory**: All AppImages are stored in `~/appimages`.
- **Desktop Files**: The `.desktop` files for the installed applications are located in `~/.local/share/applications`.
- **Icons**: Application icons are stored in `~/.local/share/icons/`.
