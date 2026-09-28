import re


class MessageManager:
    _COLOR_PATTERN = re.compile(r"&([0-9a-fk-or])")

    def __init__(self, config):
        self._messages = config.messages
        self._prefix = config.config.get("messages", {}).get(
            "prefix",
            "&8[&bKGAcid&8] ",
        )

    def get(self, path: str, **placeholders) -> str:
        value = self._messages

        for key in path.split("."):
            if not isinstance(value, dict):
                return ""

            value = value.get(key, "")

        if not isinstance(value, str):
            return ""

        message = self._prefix + value

        for key, replacement in placeholders.items():
            message = message.replace(
                "{" + key + "}",
                str(replacement),
            )

        return self._colorize(message)

    @classmethod
    def _colorize(cls, message: str) -> str:
        return cls._COLOR_PATTERN.sub(
            lambda match: f"§{match.group(1)}",
            message,
        )