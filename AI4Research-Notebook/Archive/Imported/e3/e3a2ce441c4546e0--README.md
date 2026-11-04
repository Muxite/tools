# Linux setup

Files for setting up a Linux machine. Layout and rules are in [../README.md](../README.md).

| File | What it is | Install |
|---|---|---|
| `NVIDIA-Linux-x86_64-570.169.run` | NVIDIA driver 570.169, x86_64 | `chmod +x` then run as root, with the display stopped. Distro packages are usually the better route |
| `nvim-linux-x86_64.tar.gz` | Neovim, x86_64 | `tar -xzf` and put `bin/nvim` on your PATH |
| `nvim-linux-arm64.tar.gz` | Neovim, arm64 | same, for arm64 |

Note the architecture: `arm64` files won't run on an `x86_64` machine, or the other way round.

Files copied from phone storage or a Windows drive lose their executable bit, so run
`chmod +x <file>` on `.run` and AppImage files before using them.

## Not carried

The Ubuntu Server ISO was dropped on 2026-09-19 to keep the bundle phone-sized. Download it from ubuntu.com and write it with any USB writer.
