from logging import Logger


def map_interpretation(status: str, log: Logger):
    if status == "Pathogenic":
        return "Pathogenic"
    elif "VUS" in status:
        return "Uncertain significance"
    else:
        log.error(f"Failed to resolve interpretation: {status}")
        return ""
