from diff import render as render_diff, selected_diff
from view import LABELS, follow, header, read, ref_path, tone, wrap


def receipts(log):
    arms = {}
    for event in log:
        arm = event["data"].get("arm")
        if event["kind"] == "result" and event["status"] == "ok" and arm:
            arms[arm] = event
    return arms


def paths(directory, state, log):
    if state["view"] == "diff":
        event = selected_diff(state, log)
        return [ref_path(event)] if event else []
    return [ref_path(event) for event in receipts(log).values() if event["ref"]]


def render(directory, state, log, width, height, offset):
    if state["view"] == "diff":
        return render_diff(directory, state, log, width, height, offset)
    lines = [header("RESULTS  •  PAIRED COMPARISON")]
    arms = receipts(log)
    if not arms:
        return lines + ["Awaiting arm receipts."], 0
    lines.extend(["TTFT ms | Prefill ms | Decode t/s | MiB", "Native prefill · peak memory"])
    for arm, event in arms.items():
        path = ref_path(event)
        selected = state.get("result_arm") == arm
        tag = f'{arm} [{LABELS[event["stage"]]}]'
        lines.append(tone(tag, "1;7" if selected else "1;33" if event["stage"] == "fixture" else "1;32"))
        if not path or not path.is_file():
            lines.append("Receipt unavailable")
            continue
        try:
            receipt = read(path)
            if not isinstance(receipt, dict):
                raise ValueError("Expected a receipt object")
        except (OSError, ValueError):
            lines.append("Receipt unreadable")
            continue
        lines.append("  |  ".join(str(receipt.get(key, "—")) for key in
                                 ("ttft_ms", "native_prefill_ms", "decode_tps", "memory_mib")))
        lines.extend(wrap(f'Output {receipt.get("output_check", "—")} · {receipt.get("verdict", "—")}', width))
        lines.extend(wrap(event["ref"], width))
    body = lines[3:]
    room = max(1, height - 3)
    offset = min(offset, max(0, len(body) - room))
    return lines[:3] + body[offset:offset + room], offset


if __name__ == "__main__":
    follow("result", render, paths)
