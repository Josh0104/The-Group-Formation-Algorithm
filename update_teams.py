import csv
import argparse
import os
from dotenv import load_dotenv
from supabase import create_client


def load_supabase(env_path: str):
    if not os.path.exists(env_path):
        raise ValueError(f"Env file not found: {env_path}")

    load_dotenv(env_path)

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in env file")

    return create_client(url, key)


def update_teams(csv_path: str, env_path: str):
    supabase = load_supabase(env_path)

    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "id": row["ID"],
                "team_id": int(row["Team"]),
            })

    supabase.table("users").upsert(rows).execute()

    print(f"Updated {len(rows)} users using env file: {env_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update team_id from CSV")

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to CSV file"
    )

    parser.add_argument(
        "--env",
        default=".env",
        help="Path to .env file (default: .env)"
    )

    args = parser.parse_args()

    update_teams(args.input, args.env)
