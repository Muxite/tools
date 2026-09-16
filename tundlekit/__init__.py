"""tundlekit: agent-agnostic tools distilled from the tundle transfer bundle.

See MANIFEST.md for the contract every module implements.
"""
__version__ = "0.1.0"

# Modules that register tools (tundlekit.<name>). Order is the order of `tundlekit tools`.
MODULES = ["bundle", "deck", "diagram", "chart", "palette", "textlint", "render", "papers", "translate"]
