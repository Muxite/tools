from view import LABELS, follow, header, tone, wrap


def render(directory, state, log, width, height, offset):
    lines = []
    for card in state["catalog"]:
        name = card["id"]
        records = [event for event in log if event["cc"] == name]
        successful = [event for event in records if event["status"] == "ok"]
        verified = next((e["status"] == "ok" for e in reversed(records)
                         if e["kind"] == "verify" and e["status"] in ("ok", "fail")), False)
        activation = any(e["kind"] == "activate" and e["data"].get("marker") for e in successful)
        diff = next((e["data"]["diff_stat"] for e in reversed(successful)
                     if e["data"].get("diff_stat")), "—")
        stage = next((e["stage"] for e in reversed(successful) if e["stage"]), None)
        tag = ("★ " if card.get("starred") else "  ") + card["name"] + " · " + diff
        if state["selected_cc"] == name:
            tag = tone(tag, "1;7")
        summary = f'{card["component"]} [{LABELS[stage]}] V:{"Y" if verified else "N"} A:{"Y" if activation else "N"}'
        lines.extend([tag, *wrap(summary, width)])
    room = max(1, height - 2)
    offset = min(offset, max(0, len(lines) - room))
    legend = "V verified · A activated"
    if len(lines) > room:
        legend += " · j/k scroll"
    return [header("CC  •  CAPABILITY CAPSULES"), legend] + lines[offset:offset + room], offset


if __name__ == "__main__":
    follow("cc", render)
