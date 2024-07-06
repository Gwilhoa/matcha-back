import logging


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "RESET": "\033[0m",
        "DEBUG": "\033[1;35m",  # violet
        "INFO": "\033[1;32m",  # vert
        "WARNING": "\033[1;33m",  # jaune
        "ERROR": "\033[1;31m",  # rouge
        "CRITICAL": "\033[1;41m\033[1;37m",  # texte blanc sur fond rouge
    }

    def format(self, record):
        log_message = super().format(record)
        log_level_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        return "\n".join(f"{log_level_color}{line}{self.COLORS['RESET']}" for line in log_message.splitlines())
