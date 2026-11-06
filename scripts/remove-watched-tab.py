#!/usr/bin/env python3
"""Remove the conversation-header "watched videos" tab from client.js.

This fork intentionally keeps the WatchTab component and the /watched data
endpoint (the settings page still uses them); it only removes the
conversation.view registration and the workspace scope probe.

Run after merging upstream/main:

    python3 scripts/remove-watched-tab.py

The script is idempotent: if the block is already gone it exits 0 without
changing anything. If upstream moved or rewrote the block, it exits non-zero
and leaves client.js untouched so the conflict can be resolved by hand.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
CLIENT = ROOT / "client.js"

# The block starts at the try that owns `viewOff` and ends at its catch.
START_MARKER = "  try {\n    let viewOff = null"
END_MARKER = "  } catch (e) { /* 没有这些槽位就算了 */ }"
REPLACEMENT = (
    "  // 2026-11-07: 移除会话头的「刷过的视频」tab。\n"
    "  // WatchTab 组件与 /watched 数据接口保留，设置页列表仍可用；\n"
    "  // 仅不再向 conversation.view 注册，也不装 workspace 探针。\n"
)


def main() -> int:
    source = CLIENT.read_text()
    start = source.find(START_MARKER)
    if start == -1:
        if "id: 'bili-watched'" not in source:
            print("watched tab already removed; nothing to do")
            return 0
        print(
            "found bili-watched but not the expected try block; "
            "upstream changed the registration — resolve manually",
            file=sys.stderr,
        )
        return 2

    end = source.find(END_MARKER, start)
    if end == -1:
        print(
            "found the watched-tab try block but not its catch marker; "
            "upstream changed the block — resolve manually",
            file=sys.stderr,
        )
        return 2

    end += len(END_MARKER)
    CLIENT.write_text(source[:start] + REPLACEMENT + source[end:])
    print("removed watched-videos conversation tab from client.js")
    return 0


if __name__ == "__main__":
    sys.exit(main())
