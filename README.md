# Steam Icons Fix

(Windows only, might be helpful for doing other things though)

This Python script is used to download icons for all the installed games in your Steam library. The script also allows downloading icons for specific games by specifying their app IDs as command-line arguments. If any icons fail to download, the script will print a list of the failed icons at the end. You can then run the script again with the list of failed app IDs as arguments to retry downloading the icons for the failed games.



My Steam Icons were blank on my desktop after a fresh windows 10 / windows 11 re-install. The icons were missing and it was painful to have to download them one by one so I made this script to do it for me. 

I hope it helps you too.

(After running the script, you might need to refresh your desktop/restart PC or clear icon cache to see the icons, it worked for me after a refresh)

## Prerequisites

- [Python](https://www.python.org/downloads/)
- [Steam](https://store.steampowered.com/about/)


The below are required Python packages. You can install them by running the following commands in terminal:

```bash
pip install -r requirements.txt
```
- [Requests](https://docs.python-requests.org/en/master/user/install/#install)
- [tqdm](https://github.com/tqdm/tqdm#installation) 
- [Python Steam](https://github.com/ValvePython/steam) [This is largely unused but I've added it as a requirement for future updates]

This is downloaded and installed by the script if it is not already installed:
- [SteamCMD](https://developer.valvesoftware.com/wiki/SteamCMD#Downloading_SteamCMD)



## Installation

Clone this repository and navigate to the repository directory in the terminal. Run this command to install the necessary Python packages:

## Usage

Run the script with the following commands in terminal:

1. To download icons for specific games, provide the app IDs:
   ```bash
   python SteamIconsFix.py 730 440 570 228980
   ```

2. To print the list of installed games, run:
   ```bash
   python SteamIconsFix.py list
   ```

3. To download icons for all installed games, run:
   ```bash
   python SteamIconsFix.py all
   ```

## Troubleshooting

If any icons fail to download, the script will print a list of failed icons at the end. To retry downloading the icons for these games, use the following command (replace `<failed_app_ids>` with the space-separated list of failed app IDs):
```bash
   python SteamIconsFix.py <failed_app_ids>
   ```

## License

This project is under an [MIT License](https://opensource.org/licenses/MIT). Detailed information can be found in the script source code.

## Contact

If you have any specific inquiries, problems, or suggestions, feel free to reach out on:

- Issues: [GitHub Issues](https://github.com/havokentity/SteamIconsFix/issues)


All feedback and contribution to improve the project are welcomed.

## Acknowledgements

This project makes use of the following software:

- Python 3.10.9: An interpreted high-level general-purpose programming language. (Will probably work on any Python 3 version)
- Requests: A simple, yet powerful, HTTP library for Python.
- tqdm: A fast, extensible progress bar for Python.
- SteamCMD: A command-line version of the Steam client which can be used to download icons for Steam games.
- Steam: A digital distribution platform developed by Valve Corporation for purchasing and playing video games.
- ValvePython/steam: A Python library for interacting with Steam.