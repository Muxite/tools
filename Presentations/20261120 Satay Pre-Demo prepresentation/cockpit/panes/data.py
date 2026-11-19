from pathlib import PurePosixPath

from view import COLORS, LABELS, follow, header, tone


def render(directory, state, log, width, height, offset):
    lines = [header("DATA  •  EVENT & RECEIPT FEED")]
    for event in log[-max(1, height - 1):]:
        color = COLORS.get(event["kind"], COLORS.get(event["stage"], 37))
        tag = f'{event["seq"]:>3} {event["step"] or "—"} {event["kind"]} {event["status"]}'
        details = event["data"]
        detail = event["ref"] or details.get("text") or details.get("title") or event["cc"] or ""
        label = f'[{LABELS[event["stage"]]}] '
        if event["ref"] and len(label) + len(tag) + len(detail) + 1 > width:
            detail = PurePosixPath(detail).name
        lines.append(tone(label, COLORS.get(event["stage"], 37)) + tone(tag, color) + " " + detail)
    return lines, 0


if __name__ == "__main__":
    follow("data", render)
