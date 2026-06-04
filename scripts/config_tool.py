#!/usr/bin/env python3

import argparse
import ast
from pathlib import Path

CONFIG_PATH = Path("/root/scripts/tg_migrator/config.py")

ALLOWED_SET_KEYS = {
    "OLD_CHANNEL_ID",
    "OLD_GROUP_ID",
    "NEW_GROUP_ID",
    "CHANNEL_TOPIC_ID",
    "GROUP_TOPIC_ID",
}


def load_config_text():
    if not CONFIG_PATH.exists():
        raise SystemExit(f"Config not found: {CONFIG_PATH}")
    return CONFIG_PATH.read_text()


def save_config_text(text):
    CONFIG_PATH.write_text(text)


def parse_ignored_usernames(text):
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, "id", None) == "IGNORED_USERNAMES":
                    return set(ast.literal_eval(node.value))
    return set()


def replace_ignored_usernames(text, usernames):
    usernames = sorted(usernames)
    block = "IGNORED_USERNAMES = {\n"
    for username in usernames:
        block += f'    "{username}",\n'
    block += "}\n"

    lines = text.splitlines()
    out = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith("IGNORED_USERNAMES"):
            out.append(block.rstrip("\n"))
            i += 1
            while i < len(lines) and not lines[i].startswith("}"):
                i += 1
            if i < len(lines):
                i += 1
        else:
            out.append(line)
            i += 1

    return "\n".join(out) + "\n"


def show_config():
    text = load_config_text()
    for line in text.splitlines():
        if line.startswith("API_HASH"):
            print('API_HASH = "***hidden***"')
        else:
            print(line)


def add_bot(username):
    username = username.lstrip("@").lower()
    text = load_config_text()
    usernames = parse_ignored_usernames(text)
    usernames.add(username)
    save_config_text(replace_ignored_usernames(text, usernames))
    print(f"Added ignored bot: @{username}")


def remove_bot(username):
    username = username.lstrip("@").lower()
    text = load_config_text()
    usernames = parse_ignored_usernames(text)
    usernames.discard(username)
    save_config_text(replace_ignored_usernames(text, usernames))
    print(f"Removed ignored bot: @{username}")


def set_value(key, value):
    if key not in ALLOWED_SET_KEYS:
        allowed = ", ".join(sorted(ALLOWED_SET_KEYS))
        raise SystemExit(f"Unsupported key: {key}. Allowed: {allowed}")

    try:
        int_value = int(value)
    except ValueError:
        raise SystemExit(f"Value must be integer: {value}")

    text = load_config_text()
    lines = text.splitlines()
    out = []
    changed = False

    for line in lines:
        if line.startswith(f"{key} ="):
            out.append(f"{key} = {int_value}")
            changed = True
        else:
            out.append(line)

    if not changed:
        raise SystemExit(f"Key not found in config.py: {key}")

    save_config_text("\n".join(out) + "\n")
    print(f"Updated {key} = {int_value}")


def main():
    parser = argparse.ArgumentParser(description="Manage tg-migr-copier config")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("show")

    add = sub.add_parser("add-bot")
    add.add_argument("username")

    remove = sub.add_parser("remove-bot")
    remove.add_argument("username")

    set_cmd = sub.add_parser("set")
    set_cmd.add_argument("key")
    set_cmd.add_argument("value")

    args = parser.parse_args()

    if args.command == "show":
        show_config()
    elif args.command == "add-bot":
        add_bot(args.username)
    elif args.command == "remove-bot":
        remove_bot(args.username)
    elif args.command == "set":
        set_value(args.key, args.value)


if __name__ == "__main__":
    main()
