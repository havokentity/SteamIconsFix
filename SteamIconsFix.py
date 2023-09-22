"""
--------------------------------------------------------------------------------
Script Name: Steam Icons Fix
Author: Rajesh Peter Douglas D'Monte
Email: havokentity@gmail.com

This Python script downloads game icons for installed or specific Steam games.

MIT License

Copyright (c) 2023 Rajesh Peter Douglas D'Monte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
--------------------------------------------------------------------------------
"""

# No need for API key, or SteamID, or SteamDB
# It will auto download SteamCMD and place it in the Steam folder, if you don't have it already from
# https://developer.valvesoftware.com/wiki/SteamCMD#Downloading_SteamCMD

# This script will download the icons for all installed games in your Steam library
# It will also download the icons for all games you specify as arguments
# If any icons fail to download, it will print a list of the failed icons at the end
# You can then run the script again with the list of failed app IDs as arguments to retry downloading the icons for the failed games

# Usage:
# python SteamIconsFix.py [<app_id> ...] <list> <all>

# Example: python SteamIconsFix.py 730 440 570 228980
# Example: python SteamIconsFix.py list
# Example: python SteamIconsFix.py all


# Import necessary libraries
import os
import io
import time
import zipfile
import re
import sys
import requests
import subprocess
import winreg
from steam.client import SteamClient
from steam.enums import EResult
from steam.enums.emsg import EMsg

# Import progress bar library
from tqdm import tqdm

# Import ZIP file library
def download_and_extract(url, path):
    # Check if the directory exists and is writeable
    if not os.path.isdir(path) or not os.access(path, os.W_OK):
        raise Exception("The path is either not a directory or is not writeable: %s" % path)

    try:
        # Send GET request
        response = requests.get(url)

        # Check if the request is successful
        if response.status_code != 200:
            raise Exception("Failed to download the file. URL: %s" % url)

        # Read content of the request
        content = response.content

        # Convert content to a stream
        zip_stream = io.BytesIO(content)

        # Open the ZIP file
        zip_file = zipfile.ZipFile(zip_stream)

        # Check if zip file is valid
        if zip_file.testzip() is not None:
            raise Exception("The downloaded file is not a valid zip file: %s" % url)

        # Extract the ZIP file content to disk
        zip_file.extractall(path)

    except requests.RequestException as err:
        print ("A requests exception occurred: ",err)
    except zipfile.BadZipFile as err:
        print ("A zip file exception occurred: ",err)
    except Exception as err:
        print ("An exception occurred: ",err)


# Function to find Steam installation path
def find_steam_installation():
    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\Valve\\Steam"
        )
        steam_path, reg_type = winreg.QueryValueEx(registry_key, "InstallPath")
        winreg.CloseKey(registry_key)

        return steam_path
    except WindowsError:
        return None


# Function to retrieve Steam library folders
def get_steam_library_folders(steamPath):
    # Empty list to store library folder paths
    library_folders = []

    # Path to the Steam library folder VDF file
    # vdf_file_path = os.path.join(
    #     os.getenv("ProgramFiles(x86)"), "Steam", "steamapps", "libraryfolders.vdf"
    # )
    vdf_file_path = steamPath + "\\steamapps\\libraryfolders.vdf"

    # If the VDF file exists, read it and extract library folder paths
    if os.path.exists(vdf_file_path):
        with open(vdf_file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Loop over each line in the VDF file
        for line in lines:
            # If the line contains the string "path", extract the path
            if "path" in line:
                path = line.strip()

                # Extract the path value in the second pair of quotation marks
                path = path.split('"')[3]

                # Remove escape characters in the path
                path = path.replace("\\\\", "\\")

                # Append "/steamapps" to the path
                path = os.path.join(path, "steamapps")

                # Add the path to the list of library folders
                library_folders.append(path)

    # Return the list of library folders
    return library_folders


# Function to fetch an icon by app ID
def fetch_icon_by_app_id(client, steamPath, app_id, game_name=None, failed_icons=[]):
    # Define the default installation directory for SteamCMD
    # steamcmd_install_dir = os.path.join(
    #     os.getenv("ProgramFiles(x86)"), "Steam"
    # )

    steamcmd_install_dir = steamPath

    # Get the app info from the Steam API
    if client.connected:
        try:
            app_info = client.get_product_info(apps=[int(app_id)])
            if app_info:
                app = app_info['apps'][int(app_id)]
                if 'common' in app and 'clienticon' in app['common']:
                    client_icon_filename = app['common']['clienticon']
                    client_icon_url = f"https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/{app_id}/{client_icon_filename}.ico"

                    # Print the icon URL
                    print(
                        f"[FAST] Client Icon URL for {game_name} - {app_id}: {client_icon_url}"
                    )

                    download_icon(app_id, client_icon_filename, client_icon_url, failed_icons, game_name,
                                  steamcmd_install_dir)
                else:
                    print("[FAST] Unable to find 'clienticon' in the app info")
            else:
                print("[FAST] Unable to get product info for app ID: ", app_id)
        except Exception as err:
            print(f"[FAST] An error occurred: {err}")

        return
    else:
        print("[FAST] Not connected to Steam. Will use SteamCMD to get the app info")

    # steamcmd.exe path
    steamcmd_exe_path = os.path.join(steamcmd_install_dir, "steamcmd.exe")

    # Output file path
    output_file = "steamcmd_output.txt"

    # If the steamcmd.exe directory does not exist, print an error message and exit
    if not os.path.exists(steamcmd_exe_path):
        print(f"SteamCMD not found in the following path: {steamcmd_install_dir}")

        print("Downloading SteamCMD...")
        # Download SteamCMD

        try:
            download_and_extract(
                "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip",
                steamcmd_install_dir,
            )

            print("SteamCMD downloaded successfully")

            steamcmd_command = (
                f'"{steamcmd_exe_path}" +quit > {output_file} 2>&1'
            )

            try:
                # Run SteamCMD command and send the output to a file to force it to update
                print("Updating SteamCMD...")
                subprocess.run(steamcmd_command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"[Probably Ignore]Error: {e}")

        except Exception as err:
            print ("An exception occurred: ",err)
            print("Failed to download SteamCMD. Exiting...")
            exit(1)
    else:
        print(f"SteamCMD found in the following path: {steamcmd_install_dir}")


    #Prepare a string of +ggs with a fixed count of n. This is to let SteamCMD update itself
    #and then update the app_info_print command to get the latest info

    n = 10
    ggs = ""
    for i in range(n):
        ggs += "+gg "

    # Define the SteamCMD command and output file path
    # f'"{steamcmd_exe_path}" +login anonymous +app_info_update 1 +app_info_print {app_id} +quit > {output_file} 2>&1'
    steamcmd_command = (
        # f'"{steamcmd_exe_path}" +app_info_print {app_id} +quit > {output_file} 2>&1'
        f'"{steamcmd_exe_path}" {ggs} +app_info_update 1 +app_info_print {app_id} {ggs} +quit > {output_file} 2>&1'
    )

    try:
        # Run SteamCMD command and send the output to a file
        subprocess.run(steamcmd_command, shell=True, check=True, close_fds=True, start_new_session=True)

        # introduced a delay to allow the file to be written
        time.sleep(1.5)

        # Read the output file
        with open(output_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
            #close file
            file.close()


        foundClientIcon = False

        # Loop over each line in the output
        for line in lines:
            # If the line contains the string "clienticon", extract the icon file name
            if '"clienticon"' in line:
                parts = line.strip().split('"')
                if len(parts) > 1:
                    # Extract the icon file name
                    client_icon_filename = parts[3]

                    # Create the URL to download the icon from
                    client_icon_url = f"https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/{app_id}/{client_icon_filename}.ico"

                    # Print the icon URL
                    print(
                        f"Client Icon URL for {game_name} - {app_id}: {client_icon_url}"
                    )

                    foundClientIcon = True

                    download_icon(app_id, client_icon_filename, client_icon_url, failed_icons, game_name,
                                  steamcmd_install_dir)

                    break

        if not foundClientIcon:
            print(
                f"Client Icon URL for {game_name} - {app_id} not found in the SteamCMD output."
            )
            failed_icons.append(
                {"appid": app_id, "name": game_name, "reason": "icon_not_found"}
            )

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def download_icon(app_id, client_icon_filename, client_icon_url, failed_icons, game_name, steamcmd_install_dir):
    # Download the icon
    response = requests.get(client_icon_url)
    if response.status_code == 200:
        client_icon_filename = f"{client_icon_filename}.ico"
        icon_file_path = os.path.join(
            steamcmd_install_dir, "steam", "games", client_icon_filename
        )
        os.makedirs(os.path.dirname(icon_file_path), exist_ok=True)

        # Save the icon to a file
        with open(icon_file_path, "wb") as icon_file:
            icon_file.write(response.content)
        print(f"Client Icon saved to: {icon_file_path}")
    else:
        print(
            f"Failed to download Client Icon from URL: {client_icon_url}"
        )
        failed_icons.append(
            {
                "appid": app_id,
                "name": game_name,
                "reason": "failed_to_download",
            }
        )


# Function to get list of Steam games in local libraries
def get_steam_games(steamPath, printFullList=True):
    # Retrieve Steam library folders
    library_folders = get_steam_library_folders(steamPath)
    if not library_folders:
        print("No Steam library folders found.")
        return []

    # Empty list to store games
    all_games = []

    # Loop over each library folder
    for folder in library_folders:
        # Get list of .acf files (Steam app manifest files) in the folder
        file_list = os.listdir(folder)
        acf_files = [file for file in file_list if file.endswith(".acf")]

        # If there are .acf files, extract app IDs and game names
        if acf_files:
            for acf_file in acf_files:
                # Open the .acf file and read its contents
                game_info_path = os.path.join(folder, acf_file)
                with open(game_info_path, "r", encoding="utf-8") as file:
                    acf_content = file.read()

                    # Extract the app ID and game name from the file contents
                    match_name = re.search(r'"name"\s+"(.*?)"', acf_content)
                    match_appid = re.search(r'"appid"\s+"(\d+)"', acf_content)

                    # If both the app ID and game name were found, store them in the game list
                    if match_name and match_appid:
                        all_games.append(
                            {"name": match_name.group(1), "appid": match_appid.group(1)}
                        )

    # If no games were found, print a message
    if not all_games:
        print("No Steam games found in your local libraries.")
    # If games were found and printFullList is True, print the list of games
    elif printFullList:
        print("List of Steam games found in your local libraries:")
        for game in all_games:
            print(f" - {game['appid']}: {game['name']}")

    # Return the list of games
    return all_games

# Main function
def main():

    # Usage message if no arguments were provided
    if len(sys.argv) < 2:
        print("Usage: python script.py [<app_id> ...] <list> <all>")
        return

    steam_path = find_steam_installation()
    if steam_path:
        print(f"Steam is installed in this path: {steam_path}")
    else:
        print("Steam installation not found. Exiting...")
        return

    client = SteamClient()

    if client.anonymous_login() == EResult.OK:
        print("Logged in to Steam anonymously and successfully")
    else:
        print("Could not log in to Steam anonymously. Will use SteamCMD to get the app info")

    # List to store failed icons
    failed_icons = []

    # List and function to process all given appid arguments
    app_ids = sys.argv[1:]

    noIcon = False

    # If 'list' is specified, print list of installed games
    if "list" in app_ids and len(app_ids) == 1:
        all_games = get_steam_games(steam_path)

        # Print total number of games installed
        print(f"\nTotal number of games installed: {len(all_games)}")

        noIcon = True
    # If 'all' is specified, fetch icons for all installed games
    elif "all" in app_ids and len(app_ids) == 1:
        all_games = get_steam_games(steam_path)

        # Print total number of games installed
        print(f"\nTotal number of games installed: {len(all_games)}")

        # Use tqdm to wrap the for loop and create a progress bar
        for game in tqdm(all_games, desc="Downloading icons"):
            fetch_icon_by_app_id(client, steam_path, game["appid"], game["name"], failed_icons)
    else:
        games = get_steam_games(steam_path, False)

        # Fetch icon for each given app_id
        for app_id in tqdm(app_ids, desc="Downloading icons"):
            # Check if the app_id is 228980, which is the app_id for Steam Common Redistributables (required by some games), if so, skip it

            if app_id == "228980":
                print(
                    f"Skipping app_id={app_id} (Steam Common Redistributables) as it is not a game/app."
                )
                continue

            game = next((game for game in games if game["appid"] == app_id), None)

            if game:
                fetch_icon_by_app_id(client, steam_path, game["appid"], game["name"], failed_icons)
            else:
                print(
                    f"A game with app_id={app_id} was not found in your Steam libraries but I will try to download the icon anyway."
                )
                fetch_icon_by_app_id(client, steam_path, app_id, "", failed_icons)

    # Check if there were any failed icons
    if not failed_icons:
        if noIcon:
            print(
                "No icons were downloaded as you did not specify any app_id or were only listing games"
            )
        else:
            print("All icons were downloaded successfully")
    else:
        print("\nFailed icons: ")
        failed_app_ids = []
        for game in failed_icons:
            print(
                f"AppID: {game['appid']}, Name: {game['name']}, Reason: {game['reason']}"
            )
            failed_app_ids.append(game["appid"])
        print(
            "\nTo retry downloading icons for the failed games, run the following command:"
        )
        print(f"python .\\SteamIconsFix.py {' '.join(failed_app_ids)}")

    client.logout()


if __name__ == "__main__":
    print("SteamFix icons for all installed games")
    main()


    print("Done")
