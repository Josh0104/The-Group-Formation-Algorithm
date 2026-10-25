"""Run: python3 generate_room_test_data.py data/people/2026_v2.csv"""

import argparse
import csv
import os
import sys
from datetime import date, datetime
from pathlib import Path

QUESTIONS = [
    ("Do they snore?", "ynk"),
    ("Can they sleep with someone who snores?", "ynk"),
    ("Do they sleep early?", "ymnk"),
    ("Do they need a bottom bunk?", "ynk"),
    ("Can they sleep in the same room with children?", "ynk"),
    ("Are they sensitive to noise while sleeping?", "ymnk"),
    ("Can they sleep outside in a tent if there is no room?", "ynk"),
]


def read_key(prompt):
    """Read one key without Enter, restoring terminal settings on every exit."""
    print(prompt, end="", flush=True)
    if not sys.stdin.isatty():
        key = sys.stdin.read(1)
    elif os.name == "nt":
        import msvcrt
        key = msvcrt.getwch()
        if key in ("\x00", "\xe0"):
            msvcrt.getwch()
            key = "\x00"
    else:
        import termios
        import tty
        descriptor = sys.stdin.fileno()
        previous = termios.tcgetattr(descriptor)
        try:
            tty.setcbreak(descriptor, termios.TCSANOW)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(descriptor, termios.TCSANOW, previous)
    if not key or key == "\x04":
        print()
        raise EOFError
    if key == "\x03":
        print()
        raise KeyboardInterrupt
    print(key if key.isprintable() else "")
    return key.lower()


def age_at(birthday, reference):
    try:
        born = datetime.strptime(birthday or "", "%m/%d/%Y").date()
    except ValueError:
        return ""
    if born > reference:
        return ""
    return reference.year - born.year - ((reference.month, reference.day) < (born.month, born.day))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--age-date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    required = {"First name", "Last name", "Birthday", "Country", "Gender"}
    if not required.issubset(fields):
        parser.error("Missing columns: " + ", ".join(sorted(required - set(fields))))
    extra = ["Room assignment age", "Age reference date"] + [q for q, _ in QUESTIONS]
    if set(extra) & set(fields):
        parser.error("Use the original CSV; questionnaire columns already exist")
    if len(set(fields)) != len(fields) or any(None in row for row in rows):
        parser.error("CSV contains duplicate headers or extra values")
    fields += extra
    for row in rows:
        row.update({q: "" for q, _ in QUESTIONS})
        row["Room assignment age"] = age_at(row["Birthday"], args.age_date)
        row["Age reference date"] = args.age_date.isoformat()
    directory = args.output_dir or args.input.parent
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output = directory / f"{args.input.stem}_room_test_{stamp}.csv"
    with output.open("x", encoding="utf-8"):
        pass

    def save():
        temporary = output.with_suffix(".csv.tmp")
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(output)

    save()
    print(f"Output: {output.resolve()}\nTotal people: {len(rows)}")
    print("y=yes, m=maybe, n=no, k=I don't know; q=save and quit")
    print("Press a single key; no Enter needed.")
    print("Blank answers mean not answered yet. All original rows are retained.")
    try:
        for index, row in enumerate(rows, 1):
            print(f"\nPerson {index}/{len(rows)} | {len(rows)-index} people after this person")
            print(f"{row['First name']} {row['Last name']} | Birthday: {row['Birthday']} | "
                  f"Age: {row['Room assignment age']} (on {args.age_date}) | "
                  f"Country: {row['Country']} | Gender: {row['Gender']}")
            for question, allowed in QUESTIONS:
                while True:
                    answer = read_key(f"{question} [{' / '.join(allowed)}; q=quit]: ")
                    if answer == "q":
                        print(f"Progress saved: {output.resolve()}")
                        return
                    if len(answer) == 1 and answer in allowed:
                        row[question] = answer
                        save()
                        break
                    print(f"Invalid character. Valid characters: {', '.join(allowed)}, q (quit)")
            print(f"Completed {index}/{len(rows)} | {len(rows)-index} remaining")
    except (EOFError, KeyboardInterrupt):
        print(f"\nProgress saved: {output.resolve()}")
        return
    print(f"Finished. Saved: {output.resolve()}")


if __name__ == "__main__":
    main()
