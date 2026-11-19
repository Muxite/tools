import os
import shutil
import shlex

from common import COMMAND, PANES, SESSION, ROOT, tmux

WINDOW = SESSION + ":demo"


def command(directory, name):
    return "exec " + shlex.join(["python3", "-B", str(ROOT / "panes" / (name + ".py")), str(directory)])


def setup(directory):
    names = ("TMUX", "TMUX_PANE", "SHELL")
    env = {name: os.environ.pop(name) for name in names if name in os.environ}
    os.environ["SHELL"] = shutil.which("bash")
    try:
        experiment = tmux("-f", "/dev/null", "new-session", "-d", "-s", SESSION, "-n", "demo",
                          "-x", "200", "-y", "55", "-P", "-F", "#{pane_id}",
                          command(directory, "experiment")).stdout.strip()
    finally:
        os.environ.pop("SHELL")
        os.environ.update(env)
    tmux("set-window-option", "-t", WINDOW, "remain-on-exit", "on")
    tmux("set-option", "-t", SESSION, "default-shell", shutil.which("bash"))
    tmux("set-window-option", "-t", WINDOW, "allow-rename", "off")
    tmux("set-window-option", "-t", WINDOW, "pane-border-status", "top")
    tmux("set-window-option", "-t", WINDOW, "pane-border-format", " #{pane_title} ")
    tmux("set-option", "-t", SESSION, "status-left-length", "23")
    tmux("set-option", "-t", SESSION, "status-left", " cockpit | C-b Space ")
    tmux("set-option", "-t", SESSION, "status-right", " C-b ?  ")
    tmux("set-option", "-t", SESSION, "status-style", "bg=colour235,fg=colour252")
    tmux("set-option", "-t", SESSION, "status-interval", "0")

    def split(name, target, *flags):
        return tmux("split-window", "-d", "-t", target, *flags, "-P", "-F", "#{pane_id}",
                    command(directory, name)).stdout.strip()

    plan = split("plan", experiment, "-h", "-b", "-l", "26%")
    cc = split("cc", experiment, "-h", "-l", "36%")
    data = split("data", plan, "-v", "-l", "35%")
    result = split("result", cc, "-v", "-l", "53%")
    panes = dict(plan=plan, data=data, experiment=experiment, cc=cc, result=result)
    for name, pane in panes.items():
        tmux("select-pane", "-t", pane, "-T", name.upper())
    tmux("select-pane", "-t", experiment)

    bindings = {"n": ["next"], "b": ["back"], "d": ["diff", "next"], "D": ["diff", "prev"],
                "r": ["view", "results"], "p": ["pause", "--toggle"], "q": ["_quiet"], "?": ["_help"]}
    tmux("bind-key", "-T", "prefix", "Space", "switch-client", "-T", "cockpit")
    tmux("bind-key", "-T", "cockpit", "Escape", "switch-client", "-T", "root")
    for key, args in bindings.items():
        action = shlex.join([str(COMMAND), *args]) + " >/dev/null"
        for table in ("prefix", "cockpit"):
            tmux("bind-key", "-T", table, key, "run-shell", "-b", action)
    caption("")
    return panes


def snapshot(panes):
    result = tmux("list-panes", "-t", WINDOW, "-F",
                  "#{pane_id} #{pane_pid} #{pane_dead} #{pane_active} #{pane_width} #{pane_height}",
                  check=False)
    found = {}
    for line in result.stdout.splitlines():
        key, pid, dead, selected, width, height = line.split()
        found[key] = {"id": key, "pid": int(pid), "dead": dead == "1", "active": selected == "1",
                      "width": int(width), "height": int(height)}
    return {name: found.get(pane, {"id": pane, "pid": None, "dead": True})
            for name, pane in panes.items()}


def caption(text):
    tmux("set-option", "-t", SESSION, "status-format[0]", (
        "#{?client_prefix,#[fg=colour223],} cockpit | C-b Space #[default]  "
        + text.replace("#", "##") + " #[align=right] C-b ? "
    ))


def pipe(directory, pane, name, enable):
    if enable:
        target = directory / "panes" / (name + ".log")
        action = shlex.join(["python3", "-B", str(ROOT / "recorder.py"), "pipe", str(target)])
        tmux("pipe-pane", "-O", "-t", pane, action)
    else:
        tmux("pipe-pane", "-t", pane, check=False)


def recover(directory, state):
    panes = snapshot(state["pane_ids"])
    restored = []
    for name in PANES:
        if panes[name]["dead"]:
            pane = state["pane_ids"][name]
            tmux("respawn-pane", "-t", pane, command(directory, name))
            if state.get("recording"):
                pipe(directory, pane, name, True)
            restored.append(name)
    return restored
