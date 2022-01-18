"""
common > logger > hierarchy

Contains a formal definition of the logging hierarchy, used to verify
logging into particular categories

Authors:
* Miguel Guthridge [hdsq@outlook.com.au, HDSQ#2154]
"""

HIERARCHY = {
    "bootstrap": {
        "initialize": {},
        "context": {
            "reset": {},
            "create": {}
        },
        "device": {
            "type_detect": {}
        }
    },
    "device": {
        "event": {
            "in": {},
            "out": {},
        }
    },
    "plugins": {
        "special": {
            "window": {},
            "performance": {}
        },
        "general": {
            "instrument": {},
            "effect": {}
        }
    },
    "general": {}
}
