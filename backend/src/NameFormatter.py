import re

class NameFormatter:
    def __init__(self, match_object):
        self.match = match_object
        self.raw_last = match_object.group(1).strip()
        self.raw_first_middle = match_object.group(2).strip()
        self.middle_initial = ""
        self.clean_name = ""

        # Detect and remove (M) or (m)
        self.has_minor_tag = False
        if re.search(r"\(m\)", self.raw_first_middle, flags=re.IGNORECASE):
            self.has_minor_tag = True
            self.raw_first_middle = re.sub(r"\(m\)", "", self.raw_first_middle, flags=re.IGNORECASE).strip()

        # Extract middle initial (single char at end of name)
        middle_match = re.search(r"\b([A-Za-z])\.?$", self.raw_first_middle)
        if middle_match:
            self.middle_initial = middle_match.group(1).lower()
            self.raw_first_middle = re.sub(r"\b([A-Za-z])\.?$", "", self.raw_first_middle).strip()

        # Clean redundant last name
        if self.raw_last.lower() in self.raw_first_middle.lower():
            self.raw_first_middle = self.raw_first_middle.replace(self.raw_last, "").strip()

        # Capitalize
        self.raw_last = re.sub(r"\s*-\s*", "-", self.raw_last) # Clean up spaces around hyphens in last name
        self.first_name = self._smart_capitalize(self.raw_first_middle)
        self.last_name = self._smart_capitalize(self.raw_last)

        # Build final clean name (append minor tag if needed)
        self.clean_name = f"{self.first_name} {self.last_name}"
        if self.has_minor_tag:
            self.clean_name += " (M)"

    def _smart_capitalize(self, name):
        if not name:
            return ""
        name = name.title()
        # Fix specific prefixes
        name = re.sub(r"\bMc([a-z])", lambda m: "Mc" + m.group(1).upper(), name)
        name = re.sub(r"\bMac([a-z])", lambda m: "Mac" + m.group(1).upper(), name)
        name = re.sub(r"\bO'([a-z])", lambda m: "O'" + m.group(1).upper(), name)
        for part in ["Von", "Van", "De", "Di", "Le", "La"]:
            name = re.sub(rf"\b{part}\b", part.lower(), name)
        return name