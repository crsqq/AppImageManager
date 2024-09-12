#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

## ubuntu dependency
# sudo apt install libfuse2 -y


class AppImgApplication:
    def __init__(self, Exec="", Name="", Icon="", Desktop=""):
        self.Exec = Exec
        self.Name = Name
        self.Icon = Icon
        self.Desktop = Desktop

    def delete(self):
        to_remove = [self.Exec, self.Desktop]
        if self.Icon != "" and self.Icon != "application-x-executable":
            to_remove.append(self.Icon)

        for file_path in to_remove:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"File '{file_path}' has been deleted.")
                except Exception as e:
                    print(f"Error occurred while deleting the file: {e}")
            else:
                print(f"File '{file_path}' does not exist.")

    def __str__(self):
        return (
            f"AppImgApplication(\n"
            f"  Exec: {self.Exec},\n"
            f"  Name: {self.Name},\n"
            f"  Icon: {self.Icon},\n"
            f"  Desktop: {self.Desktop}\n"
            f")"
        )

    def __repr__(self):
        return self.__str__()


class AppImgManager:
    def __init__(self):
        self.path_desktop = os.path.expanduser("~/.local/share/applications")
        self._refresh()

    def _load_desktop_file(self, desktop_file):
        with open(desktop_file, "r") as f:
            AppImg = AppImgApplication(Desktop=desktop_file)

            for l in f.readlines():
                l = l.strip()
                start = l[:5]
                if start == "Name=" and AppImg.Name == "":
                    AppImg.Name = l[5:]
                elif start == "Exec=" and AppImg.Exec == "":
                    AppImg.Exec = l[5:].split(" ")[0]
                elif start == "Icon=" and AppImg.Icon == "":
                    AppImg.Icon = l[5:]
        return AppImg

    def _refresh_desktop_files(self):
        self.desktop_files = sorted(
            [f for f in self.list_files(self.path_desktop) if f[-8:] == ".desktop"]
        )

    def _refresh_installed_appimages(self):
        self.installed_appimages = [
            self._load_desktop_file(f) for f in self.desktop_files
        ]

        not_AppImage = {
            i
            for i in range(len(self.installed_appimages))
            if ".AppImage" not in self.installed_appimages[i].Exec
        }

        self.installed_appimages = [
            item
            for i, item in enumerate(self.installed_appimages)
            if i not in not_AppImage
        ]
        self.desktop_files = [
            item for i, item in enumerate(self.desktop_files) if i not in not_AppImage
        ]

    def _refresh(self):
        self._refresh_desktop_files()
        self._refresh_installed_appimages()

    def list(self):
        return [(idx, a.Name) for (idx, a) in enumerate(self.installed_appimages)]

    def delete(self, idx):
        try:
            app = self.installed_appimages.pop(idx)
            app.delete()
            self._refresh()
        except IndexError:
            print("invalid index")

    def show(self, idx):
        try:
            app = self.installed_appimages[idx]
            return str(app)
        except IndexError:
            return "invalid index"

    def list_files(self, directory):
        """List all files in a directory and its subdirectories."""
        file_list = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list

    def __str__(self):
        return " ".join([str(a) for a in self.installed_appimages])

    def __repr__(self):
        return self.__str__()


class AppImgManagerCLI:
    def __init__(self, Mgr: AppImgManager, subparsers: argparse._SubParsersAction):
        self.Mgr = Mgr
        self.subparsers = subparsers

        list_parser = self.subparsers.add_parser("list", help="List all installed AppImages")
        list_parser.set_defaults(func=self._list)

        show_parser = self.subparsers.add_parser("show", help="Show details of a specific AppImage")
        show_parser.add_argument("item_id", type=int, help="The ID of the AppImages to show")
        show_parser.set_defaults(func=self._show)

        delete_parser = self.subparsers.add_parser(
            "delete", help="Delete a specific AppImage"
        )
        delete_parser.add_argument(
            "item_id", type=int, help="The ID of the AppImage to be deleted"
        )
        delete_parser.set_defaults(func=self._delete)

        install_parser = self.subparsers.add_parser("install", help="Install AppImage")
        install_parser.add_argument(
            "file_path", type=str, help="The file path of the AppImage to be installed."
        )
        install_parser.set_defaults(func=self._install)

    def _list(self):
        max_str_width = 35
        print(f"{'ID':<5} | {'Name':<{max_str_width}}")
        print("-" * (5 + max_str_width + 3))  # Separator line

        for idx, name in self.Mgr.list():
            print(f"{idx:>2}    | {name:<{max_str_width}}")

    def _show(self, idx):
        print(self.Mgr.show(idx))

    def _delete(self, idx):
        print(f"delete {idx}")
        self.Mgr.delete(idx)

    def _install(self, file_path):
        installer = AppImgInstaller()
        installer.install(file_path)


class AppImgInstaller:
    def __init__(self):
        # Define the directory where AppImages and misc files are stored
        self.APPIMAGE_DIR = os.path.expanduser("~/appimages")
        self.INSTALL_DIR = os.path.expanduser("~/.local/share/applications")
        self.THUMBNAIL_DIR = os.path.expanduser("~/.local/share/icons/")

    def install(self, input_appimage_location):
        # Create the directories if they do not exist
        os.makedirs(self.THUMBNAIL_DIR, exist_ok=True)
        os.makedirs(self.APPIMAGE_DIR, exist_ok=True)
        os.makedirs(self.INSTALL_DIR, exist_ok=True)

        # Check if the AppImage file exists
        if os.path.exists(input_appimage_location):
            # Copy the AppImage to the APPIMAGE_DIR
            shutil.copy(input_appimage_location, self.APPIMAGE_DIR)
            print(f"Copied {input_appimage_location} to {self.APPIMAGE_DIR}.")

            appimage_path = os.path.join(
                self.APPIMAGE_DIR, os.path.basename(input_appimage_location)
            )
            # Now install the AppImage
            self._install_appimage(appimage_path)
            print(f"Installed {input_appimage_location} to {appimage_path}")
        else:
            print(f"AppImage '{input_appimage_location}' does not exist.")

    def _install_appimage(self, appimage_path):
        """Install the AppImage."""
        appimage_name = os.path.basename(appimage_path).replace(".AppImage", "")
        subprocess.run(["chmod", "u+x", appimage_path])

        # Create a temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the AppImage to the temporary directory
            subprocess.run(
                [appimage_path, "--appimage-extract"], cwd=temp_dir, check=True
            )

            # Extract the thumbnail
            icon_path = self._extract_thumbnail(temp_dir, appimage_name)

            if icon_path is None:
                icon_path = "application-x-executable"

            # extract_desktop_file
            desktop_file = self._extract_desktop_file(
                temp_dir, appimage_path, icon_path
            )

        if desktop_file == "":
            desktop_file = self._default_desktop_file(
                appimage_name, appimage_path, icon_path
            )

        desktop_filename = appimage_name

        for line in desktop_file.split("\n"):
            if line[:5] == "Name=":
                desktop_filename = line[5:]
                break

        desktop_file_path = os.path.join(
            self.INSTALL_DIR, f"{desktop_filename}.desktop"
        )

        with open(desktop_file_path, "w") as f:
            f.write(desktop_file)

        print(f"Desktop file created at {desktop_file_path}.")

    def _extract_desktop_file(self, temp_dir, appimage_path, icon_path):
        temp_dir = os.path.join(temp_dir, "squashfs-root")
        desktop_files = [f for f in os.listdir(temp_dir) if f[-8:] == ".desktop"]
        if len(desktop_files) == 0:
            return ""
        elif len(desktop_files) > 1:
            print("more than one .desktop file found in AppImage")

        with open(os.path.join(temp_dir, desktop_files[0]), "r") as f:
            desktop_file_lines = f.readlines()

        for idx, line in enumerate(desktop_file_lines):
            start = line[:5]
            if start == "Exec=":
                split = line.split(" ")
                split[0] = f"Exec={appimage_path}"
                desktop_file_lines[idx] = " ".join(split)
            elif start == "Icon=":
                split = line.split(" ")
                split[0] = f"Icon={icon_path}"
                desktop_file_lines[idx] = " ".join(split)

            if desktop_file_lines[idx][-1:] != "\n":
                desktop_file_lines[idx] += "\n"

        return "".join(desktop_file_lines)

    def _extract_thumbnail(self, temp_dir, appimage_name):
        """Extract the first thumbnail from the AppImage's extracted contents."""
        icon_sources = [
            os.path.join(temp_dir, p)
            for p in [
                "squashfs-root",
                "squashfs-root/usr/share/icons/hicolor/1024x1024/apps",
                "squashfs-root/usr/share/icons/hicolor/512x512/apps",
                "squashfs-root/usr/share/icons/hicolor/256x256/apps",
                "squashfs-root/usr/share/icons/hicolor/scalable/apps",
                "squashfs-root/usr/bin/share/icons/hicolor/1024x1024/apps",
                "squashfs-root/usr/bin/share/icons/hicolor/512x512/apps",
                "squashfs-root/usr/bin/share/icons/hicolor/256x256/apps",
                "squashfs-root/usr/bin/share/icons/hicolor/scalable/apps",
            ]
        ]

        # Check if the icon directory exists
        for icon_source_dir in icon_sources:
            if os.path.exists(icon_source_dir):
                for filename in os.listdir(icon_source_dir):
                    if filename.endswith(".png") or (
                        filename.endswith(".svg") and "tray" not in filename
                    ):
                        # Copy the icon to the thumbnail directory
                        thumbnail_path = os.path.join(self.THUMBNAIL_DIR, filename)
                        shutil.copy(
                            os.path.join(icon_source_dir, filename), thumbnail_path
                        )
                        print(
                            f"Thumbnail for {appimage_name} copied to {thumbnail_path}."
                        )
                        return thumbnail_path  # Return the full path of the icon

        print(f"No thumbnail found for {appimage_name} in the extracted contents.")
        return None  # Return None if no icon was found

    def _default_desktop_file(self, appimage_name, exec_path, icon_path):
        """Create a new .desktop file for the application."""

        content = (
            "[Desktop Entry]\n"
            f"Name={appimage_name}\n"
            f"Exec={exec_path}\n"
            f"Icon={icon_path}\n"
            "Type=Application\n"
            "Categories=Utility;\n"
        )

        return content


def main():
    parser = argparse.ArgumentParser(description="A simple CLI to manage AppImage applications.")
    subparsers = parser.add_subparsers(dest="command")

    Mgr = AppImgManager()
    MgrCLI = AppImgManagerCLI(Mgr, subparsers)

    # Parse the arguments
    args = parser.parse_args()

    # Check if a command was provided
    if args.command is None:
        parser.print_help()
    elif args.command in {"show", "delete"}:
        # Call the appropriate function based on the command
        args.func(args.item_id)
    elif args.command == "install":
        args.func(args.file_path)
    else:
        args.func()


if __name__ == "__main__":
    main()
