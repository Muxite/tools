from view import LABELS, header, ref_path


def selected_diff(state, log):
    for event in reversed(log):
        if event["cc"] == state["selected_cc"] and event["status"] == "ok" and event["ref"] and event["data"].get("diff_stat"):
            return event


def render(directory, state, log, width, height, offset):
    card = next(c for c in state["catalog"] if c["id"] == state["selected_cc"])
    lines = [header(f'DIFF  •  {card["name"]}')]
    event = selected_diff(state, log)
    if not event or not ref_path(event).is_file():
        return lines + ["Awaiting a recorded diff."], 0
    diff = ref_path(event).read_text(errors="replace").splitlines()
    room = max(1, height - 2)
    offset = min(offset, max(0, len(diff) - room))
    stage = LABELS[event["stage"]]
    lines.append(f'[{stage}] {offset + 1}–{min(len(diff), offset + room)}/{len(diff)}  j/k PgUp/PgDn g')
    return lines + diff[offset:offset + room], offset


if __name__ == "__main__":
    from view import follow
    follow("result", render)
