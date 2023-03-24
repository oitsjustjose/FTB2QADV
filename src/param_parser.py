"""
AUTHOR: Jose Stovall | oitsjustjose@git
LICENSE: MIT
"""
import sys
from typing import Any, Dict, List

from colorama import Fore


class CommandlineConfigParser:
    def __init__(
        self,
        required_args: Dict[str, Any],
        optional_args: Dict[str, Any] = {},
        singleflags: List[str] = [],
    ) -> None:
        # Saved for future querying
        self.__args: Dict[str, Any] = {}
        # Unknown args will be marked as junk and printed later.
        self.__junk: Dict[str, Any] = {}

        for arg in sys.argv[1:]:
            # Case for \-[a-zA-Z],
            if (
                arg.startswith("-")
                and not arg.startswith("--")
                and arg[1:] in singleflags
            ):
                self.__args[arg[1:]] = True
            elif arg.startswith("--"):  # arg is a key
                plain_arg = arg[2:]
                if plain_arg in required_args or plain_arg in optional_args:
                    self.__args[plain_arg] = None
                else:  # it's a junk param, but don't trash it
                    self.__junk[plain_arg] = None
            else:  # arg is a val
                # get last unintialized arg and set it
                k = self.__get_last_key(self.__args)
                if not k:
                    continue
                # Last key is uninitialized, must be it
                if self.__args[k] is None:
                    argtype = str
                    if k in required_args:
                        argtype = required_args[k]
                    elif k in optional_args:
                        argtype = optional_args[k]
                    self.__args[k] = self.__try_cast(arg, argtype)
                else:  # It's junk, no attempted dyncasting
                    k = self.__get_last_key(self.__junk)
                    self.__junk[k] = arg
        self.__validate(required_args, optional_args, singleflags)

    def get_argument(self, key: str) -> Any:
        try:
            return self.__args[key]
        except KeyError:
            return None

    def get_all_args(self) -> Dict[str, Any]:
        return self.__args

    def __validate(self, required, optional, single):
        for key in required:
            if key not in self.__args:
                print(f"{Fore.RED}[!] Missing required parameter --{key}{Fore.RESET}")
                sys.exit(0)
        for key in optional:
            if key not in self.__args:
                print(
                    f"{Fore.LIGHTBLACK_EX}[i] Optional key {key} missing from args{Fore.RESET}"
                )
        for key in single:
            if key not in self.__args:
                print(
                    f"{Fore.LIGHTBLACK_EX}[i] Optional key {key} missing from args{Fore.RESET}"
                )
        for key in self.__junk:
            print(
                f"{Fore.YELLOW}Unrecognized key {key} was provided. Ignoring.{Fore.RESET}"
            )

    def __get_last_key(self, dict_in: Dict[str, Any]) -> str:
        k = ""
        for key in dict_in:
            k = key
        return k

    def __try_cast(self, var: Any, t: Any) -> Any:
        try:
            return t(var)
        except (TypeError, ValueError):
            print(f"'{var}' could not be cast to type {t}")
            sys.exit(1)


if __name__ == "__main__":
    cls = CommandlineConfigParser(
        required_args={"passcode": int},
        optional_args={"beans": bool},
        singleflags=["shmeef"],
    )
