import json
import sys
import re


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class HTTPError(Exception):
    def _new_line(self, header, data):
        return (
            "\n"
            + header
            + "\n"
            + str("=" * 50)
            + "\n"
            + data
            + "\n"
            + str("=" * 50)
            + "\n"
        )

    def __init__(self, message, payload=None, token=None):
        self.message = message
        self.payload = payload
        self.token = token


def __str__(self):
    # Filter the URL to remove sensitive tokens
    pattern = r"token=\d+-[A-Za-z\d\-]+"
    filtered_url = re.sub(pattern, "token=[FILTERED]", str(self.payload.get("url")))
    return (
        str(self.message)
        + "\n"
        + self._new_line(
            "Error returned from Client Central:",
            json.dumps(self.payload.get("json"), sort_keys=True, indent=4),
        )
        + self._new_line("URL called:", str(filtered_url))
        + self._new_line("HTTP Method:", str(self.payload.get("method")))
    )


class DateFormatInvalid(Exception):
    pass


class ButtonNotAvailable(Exception):
    pass


class ButtonRequiresComment(Exception):
    pass


class NoTokenProvided(Exception):
    pass
