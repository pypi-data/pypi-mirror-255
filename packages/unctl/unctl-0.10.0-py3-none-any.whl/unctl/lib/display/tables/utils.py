from colorama import Fore, Style


def get_severity(severity: str):
    severity_color = (
        Fore.RED
        if severity == "Critical"
        else (Fore.YELLOW if severity == "Severe" else Fore.WHITE)
    )
    return severity_color + severity + Style.RESET_ALL
