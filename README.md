# Steam Icons Fix

This Python script is used to download icons for all installed games in your Steam library. The script also allows downloading icons for specific games by specifying their app IDs as command-line arguments. If any icons fail to download, the script will print a list of the failed icons at the end. You can then run the script again with the list of failed app IDs as arguments to retry downloading the icons for the failed games.

## Prerequisites
- [Python](https://www.python.org/downloads/)
- [Requests](https://docs.python-requests.org/en/master/user/install/#install)

## How to use this script
1. Clone this repository and navigate to the directory in the terminal.
2. Run this command to install the necessary Python packages: `pip install requests tqdm`
3. Run the script using Python with the desired app IDs as arguments:

   a. Download icons for specific games: `python SteamIconsFix.py 730 440 570 228980`

   b. Print the list of installed games: `python SteamIconsFix.py list`

   c. Download icons for all installed games: `python SteamIconsFix.py all`

## Troubleshooting
If any icons fail to download, the program will print a list of the failed icons at the end. You can then retry downloading the icons for these games by running the command `python SteamIconsFix.py <failed_app_ids>`.

Note: Replace `<failed_app_ids>` with the space-separated list of failed app IDs.

## License
This project is under an [MIT license](https://opensource.org/licenses/MIT).