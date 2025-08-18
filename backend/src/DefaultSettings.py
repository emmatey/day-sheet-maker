default_settings = {
    "TIME_BLOCKS": {
        "Center Store": [
            ["04:00", "12:00", "Load & Stock"],
            ["12:00", "18:00", "Repack"],
            ["18:00", "07:00", "Overnight"]
        ],
        "Produce": [
            ["04:00", "08:00", "Morning"],
            ["08:00", "15:00", "Midday"],
            ["15:00", "19:00", "Close"]
        ],
        "Meat": [
            ["04:00", "11:00", "Production"],
            ["11:00", "16:00", "Maintenance"],
            ["16:00", "20:00", "Close"]
        ],
        "Seafood": [
            ["04:00", "11:00", "Prep"],
            ["11:00", "16:00", "Service"],
            ["16:00", "20:00", "Close"]
        ],
        "Deli": [
            ["04:00", "11:00", "Prep"],
            ["11:00", "17:00", "Service"],
            ["17:00", "20:00", "Close"]
        ],
        "Bakery": [
            ["04:00", "11:00", "Production"],
            ["11:00", "16:00", "Service"],
            ["16:00", "20:00", "Clean"]
        ],
        "Customer Service": [
            ["07:00", "12:00", "Morning"],
            ["12:00", "17:00", "Midday"],
            ["17:00", "23:00", "Evening"]
        ],
        "Pharmacy": [
            ["07:00", "11:00", "Morning"],
            ["11:00", "15:00", "Midday"],
            ["15:00", "19:00", "Evening"]
        ],
         "Hannaford to Go": [
            ["05:00", "10:00", "Morning Crew"],
            ["10:00", "15:00", "Mid-Day"],
            ["15:00", "20:00", "Evening"]
        ],
        "Hannaford to Go ESH": [
            ["05:00", "06:00", "05:00 - 06:00"],
            ["06:00", "07:00", "06:00 - 07:00"],
            ["07:00", "08:00", "07:00 - 08:00"],
            ["08:00", "09:00", "08:00 - 09:00"],
            ["09:00", "10:00", "09:00 - 10:00"],
            ["10:00", "11:00", "10:00 - 11:00"],
            ["11:00", "12:00", "11:00 - 12:00"],
            ["12:00", "13:00", "12:00 - 13:00"],
            ["13:00", "14:00", "13:00 - 14:00"],
            ["14:00", "15:00", "14:00 - 15:00"],
            ["15:00", "16:00", "15:00 - 16:00"],
            ["16:00", "17:00", "16:00 - 17:00"],
            ["17:00", "18:00", "17:00 - 18:00"],
            ["18:00", "19:00", "18:00 - 19:00"],
            ["19:00", "20:00", "19:00 - 20:00"]
        ]
    },
    "ROLE_MAP": {
        "Blacklists": {
            "departments": ["Authorized Hours RX", "Authorized Hrs", "Default", "Light Duty", "Management", "Pre-Opening", "Storm Loss", "Support Employment", "Training"],
            "roles": ["Asst ARM", "Scan File"]
            },
        "Hannaford to Go": {
            "roles": ["Expeditor", "Shopper"],
            "clean_roles": ["Expeditor", "Shopper"],
            "labor_tracker_enabled": [1, 1],
            "default": "Shopper"
        },
        "Center Store": {
            "roles": ["Ctr Str Mgmt", "Ctr Str Lead", "Ctr Str Clerk", "Stock Crew Assoc", "Maintenance"],
            "clean_roles": ["Management", "Management", "Clerk", "Overnight", "Maintenance"],
            "labor_tracker_enabled": [1, 1, 1, 1, 1],
            "default": "Clerk"
        },
        "Produce": {
            "roles": ["Associate"],
            "clean_roles": ["Produce Associate"],
            "labor_tracker_enabled": [1],
            "default": "Associate"
        },
        "Meat": {
            "roles": ["Meat Associate"],
            "clean_roles": ["Meat Associate"],
            "labor_tracker_enabled": [1],
            "default": "Associate"
        },
        "Seafood": {
            "roles": ["Seafood Associate", "Meat Associate"],
            "clean_roles": ["Seafood Associate", "Meat Associate"],
            "labor_tracker_enabled": [1, 1],
            "default": "Associate"
        },
        "Deli": {
            "roles": ["Deli Associate"],
            "clean_roles": ["Deli Associate"],
            "labor_tracker_enabled": [1],
            "default": "Associate"
        },
        "Bakery": {
            "roles": ["Associate"],
            "clean_roles": ["Bakery Associate"],
            "labor_tracker_enabled": [1],
            "default": "Associate"
        },
        "Customer Service": {
            "roles": ["ServiceLeadr", "Service Desk Assoc", "Cashier Exp", "ServiceClerk", "SL SelfScan"],
            "clean_roles": ["Lead", "Service Desk", "Register Team", "Register Team", "Service Desk"],
            "labor_tracker_enabled": [1, 1, 1, 1, 1],
            "default": "Register Team"
        },
        "Pharmacy": {
            "roles": ["Pharmacist", "Pharmacy Tech", "Tech"],
            "clean_roles": ["Pharmacist", "Pharmacy Tech", "Tech"],
            "labor_tracker_enabled": [1, 1, 1],
            "default": "Associate"
        },
    },
    "EXPEDITOR_REQUIREMENTS": {
        "0": 1,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 3,
        "5": 3,
        "6": 3,
        "7": 3,
        "8": 3,
        "9": 3,
        "10": 3,
        "11": 3,
        "12": 3,
        "13": 2,
        "14": 1
    },
    "SAVE_LOCATION": {
        "save_location_string" : "DEFAULT_PLACEHOLDER"
    },
    "OUTPUT_SETTINGS": {
    "copy_input_to_archive": True,
    "enable_esh": True,
    "daily_notes_override": False,
    "combined_labor_tracker": False
    }
}
