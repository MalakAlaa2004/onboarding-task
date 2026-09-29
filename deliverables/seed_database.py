"""
Seeds the local MongoDB container (portfolio_db) with sample data.
Runs directly via docker exec with zero external python dependencies.
"""

import json
from pathlib import Path
import subprocess
import sys


def seed():
    data_file = Path(__file__).parent / "sample_seed_data.json"
    if not data_file.exists():
        print(f"Error: {data_file} not found.")
        sys.exit(1)

    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Populating local MongoDB container (novagates-mongodb)...")

    for collection_name, docs in data.items():
        json_str = json.dumps(docs)
        # Use EJSON.parse so Extended JSON ($oid) converts to native ObjectId
        js_code = f"""
        const docs = EJSON.parse('{json_str}');
        db.{collection_name}.drop();
        db.{collection_name}.insertMany(docs);
        print('Collection {collection_name}: inserted ' + db.{collection_name}.countDocuments() + ' records.');
        """
        result = subprocess.run(
            [
                "docker",
                "exec",
                "-i",
                "novagates-mongodb",
                "mongosh",
                "portfolio_db",
                "--quiet",
                "--eval",
                js_code,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"Error seeding {collection_name}: {result.stderr.strip()}")

    print("\nDatabase seeding completed successfully.")


if __name__ == "__main__":
    seed()
