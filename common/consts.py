"""
common > consts

Constants used within the script
"""

# Version info
VERSION = (0, 0, 1)

VERSION_MAJOR = VERSION[0]
VERSION_MINOR = VERSION[1]
VERSION_REVISION = VERSION[2]

def getVersionString():
    return ".".join(map(str, VERSION))

# Website
WEBSITE = "https://github.com/MiguelGuthridge/Universal-Controller-Script"
DISCORD = "https://discord.gg/6vpfJUF"

# Contributor information
AUTHORS = {
    "Designers": [
        "Miguel Guthridge"
    ],
    "Primary Developers": [
        "Miguel Guthridge"
    ],
    "Plugin Contributors": [
    ],
    "Device Contributors": [
    ]
}