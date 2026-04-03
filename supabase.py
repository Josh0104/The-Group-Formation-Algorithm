import csv
import argparse
import os
from dotenv import load_dotenv
from supabase import create_client

def load_supabase():
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env")

    return create_client(url, key)


def update_teams(csv_path: str):
    supabase = load_supabase()

    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "id": row["ID"],
                "team_id": int(row["Team"]),
            })

    result = supabase.table("users").upsert(rows).execute()

    print(f"Updated {len(rows)} users")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update team_id from CSV")

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to CSV file"
    )

    parser.add_argument(
        "--use-env",
        action="store_true",
        help="Use environment variables from .env"
    )

    args = parser.parse_args()

    if args.use_env:
        update_teams(args.input)
    else:
        raise ValueError("You must use --use-env to load credentials securely")
