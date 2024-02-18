def display(hub, data):
    """
    Format results to send to the screen for the user
    """
    lines = []
    if not data:
        data = []
    for target in data:
        success = target.get("retvalue") == 0
        for key, value in target.items():
            if success:
                lines.append(
                    f"{hub.lib.colorama.Fore.GREEN} {key}: {value}{hub.lib.colorama.Fore.RESET}"
                )
            else:
                lines.append(
                    f"{hub.lib.colorama.Fore.RED} {key}: {value}{hub.lib.colorama.Fore.RESET}"
                )
    return "\n".join(lines)
