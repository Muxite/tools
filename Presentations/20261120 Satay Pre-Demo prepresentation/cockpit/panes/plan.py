from view import LABELS, follow, header, tone, wrap


def render(directory, state, log, width, height, offset):
    current = state["current_step"]
    symbols = {"ok": "✓", "start": "▶", "fail": "!", "skip": "–"}
    statuses = {event["step"]: event["status"] for event in log if event["kind"] == "task"}
    graph = []
    section = None
    for step in state["script"]:
        if step["section"] != section:
            section = step["section"]
            graph.append(tone(section.upper(), 90))
        sid = step["id"]
        text = f'{symbols.get(statuses.get(sid), "○")} {sid} {step["title"]}'
        graph.append(tone(text, "1;7") if sid == current else text)

    hypothesis = []
    reasons = []
    for event in reversed(log):
        if event["kind"] not in ("plan", "decision"):
            continue
        details = event["data"]
        stage = LABELS[event["stage"]]
        if not hypothesis and details.get("hypothesis"):
            hypothesis = wrap(f'H [{stage}] {details["hypothesis"]}', width)
        if details.get("reason"):
            label = details.get("decision", "reason")
            reasons.extend(wrap(f'{event["step"]} {label} [{stage}] {details["reason"]}', width))

    goal = min(len(hypothesis) + len(reasons) + 1, max(0, height // 3))
    graph_room = max(1, height - goal - 1)
    if len(graph) > graph_room:
        index = next((i for i, line in enumerate(graph) if "\x1b[1;7m" in line), 0)
        start = min(max(0, index - graph_room // 2), len(graph) - graph_room)
        graph = graph[start:start + graph_room]
    lines = [header("PLAN  •  TASK GRAPH")] + graph
    room = max(0, height - len(lines) - len(hypothesis) - 1)
    offset = min(offset, max(0, len(reasons) - room))
    if hypothesis or reasons:
        lines += [""] + hypothesis + reasons[offset:offset + room]
    return lines, offset


if __name__ == "__main__":
    follow("plan", render)
