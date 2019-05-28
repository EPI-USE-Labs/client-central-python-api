from typing import List


def bold(val: str) -> str:
    val = "<strong>" + val + "</strong>"
    return val


def heading(val: str, size: int = 1) -> str:
    val = "<h" + str(size) + ">" + val + "</h" + str(size) + ">"
    return val


def italics(val: str) -> str:
    val = "<i>" + val + "</i>"
    return val


def list(vals: List[str], ordered: bool = False) -> str:
    """
    :param vals: list values
    :param ordered: true = return ordered list, false = return unordered list
    :return: formatted html text (string)
    """
    html = ""
    for val in vals:
        html += "<li>" + val + "</li>"
    if ordered:
        html = "<ol>" + html + "</ol>"
    else:
        html = "<ul>" + html + "</ul>"

    return html


def underline(val: str) -> str:
    val = "<ins>" + val + "</ins>"
    return val


def strikethrough(val: str) -> str:
    val = "<del>" + val + "</del>"
    return val


def link(val: str, url: str) -> str:
    val = '<a href="' + url + '" target="_blank">' + val + "</a>"
    return val


def blockquote(val: str) -> str:
    val = "<blockquote>" + val + "</blockquote>"
    return val


def formatted(val: str) -> str:
    val = '<pre class="ql-syntax hljs">' + val + "</pre>"
    return val
