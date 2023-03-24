"""
AUTHOR: Jose Stovall | oitsjustjose@git
LICENSE: MIT
"""

import json
from typing import Any, Dict, Union

from colorama import Fore

Quest: type = Dict[str, Any]


class Advancement:
    """An advancement as made from an FTB Quest"""

    def __init__(self, quest: Quest, namespace: str, id_map: Dict[str, str]):
        """
        Creates an Advancement from a Quest, Namespace and Mapping of
            Quest ID -> Advancement Filename
        """
        self.__quest = quest
        self.__namespace = namespace
        self.__idmp = id_map

    def get_parent(self) -> str:
        """
        Gets the parent for a self.__quest with a given ID mapping.
        Returns <self.__namespace>:root as fallback
        """
        if "dependencies" in self.__quest and self.__quest["dependencies"]:
            for dep in self.__quest["dependencies"]:
                if dep in self.__idmp:
                    return f"{self.__namespace}:{self.__idmp[dep]}"
        q_nm = self.get_title()
        print(
            f"{Fore.YELLOW}[i] Failed to detect parent for self.__quest {q_nm}{Fore.RESET}"
        )
        return f"{self.__namespace}:root"

    def get_title(self) -> Union[str, Dict[str, Any]]:
        """
        Attempts to get the title of a self.__quest.
        Returns the self.__quest ID as fallback
        """
        if "title" in self.__quest:
            try:  # some titles are json colored
                return json.loads(self.__quest["title"])
            except json.decoder.JSONDecodeError:
                return self.__quest["title"]
        else:  # attempt to salvage name by fancifying the unloc name
            for task in self.__quest["tasks"]:
                if "item" in task and isinstance(task["item"], str):
                    name = task["item"].split(":")[1].split("_")
                    name = " ".join(map(lambda x: x[0].upper() + x[1:], name))
                    return name
        print(
            f"{Fore.YELLOW}[i] Failed to detect advancement name from self.__quest {self.__quest['id']}{Fore.RESET}"
        )
        return f"{self.__quest['id']}"

    def get_icon_item(self) -> str:
        """
        Attempts to get the icon item from a self.__quest's icon or its dependencies.
        Returns 'minecraft:air' as fallback
        """
        # Icon is manually specified for self.__quest. Easy money
        if "icon" in self.__quest:
            return self.__quest["icon"]
        for task in self.__quest["tasks"]:
            if "item" in task and isinstance(task["item"], str):
                return task["item"]
            if "icon" in task and isinstance(task["icon"], str):
                return task["icon"]
        return "minecraft:air"

    def get_description(self) -> str:
        """
        Attempts to build the description (and fix FTBself.__quests's whack formatting)
        Returns Empty String as fallback
        """
        if "description" in self.__quest:
            return (
                " ".join(self.__quest["description"])
                .replace("&", "§")
                .replace("  ", " ")
            )
        return ""

    def get_criteria(self) -> str:
        """
        Attempts to get the criteria item (only the first one) from the quest
        Advanced critiera such as and|or *might* come soon, but I didn't need this personally
        Returns 'minecraft:air' as default
        """
        for task in self.__quest["tasks"]:
            if "item" in task and isinstance(task["item"], str):
                # yes, [task["item"]] is correct because the task expects multiple items
                return task["item"]
        return "minecraft:air"

    def is_valid(self) -> bool:
        """Verifies that self is valid and doesn't have any unintended defaults"""
        if self.get_parent() == "minecraft:root":
            return False
        if self.get_icon_item() == "minecraft:air":
            return False
        if self.get_title() == self.__quest["id"]:
            return False
        if not self.get_description():
            return False
        return self.get_criteria() != "minecraft:air"

    def to_json(self) -> Dict[str, Any]:
        """Returns self as json"""
        return {
            "parent": self.get_parent(),
            "display": {
                "icon": {"item": self.get_icon_item()},
                "title": {"text": self.get_title()},
                "description": {"text": self.get_description()},
            },
            "criteria": {
                "0": {
                    "conditions": {"items": [{"items": [[self.get_criteria()]]}]},
                    "trigger": "minecraft:inventory_changed",
                }
            },
            "requirements": [["0"]],
        }
