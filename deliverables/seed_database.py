"""
NovaGates Onboarding - Production Database Seeder & Index Provisioner
Seeds local MongoDB container (portfolio_db) with initial schemas and creates
optimal compound, unique, and text indexes.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DatabaseSeeder")

CONTAINER_NAME = "novagates-mongodb"
DATABASE_NAME = "portfolio_db"


def run_mongosh_command(js_code: str) -> tuple[int, str, str]:
    """Executes JavaScript code inside the MongoDB container via mongosh."""
    cmd = [
        "docker",
        "exec",
        "-i",
        CONTAINER_NAME,
        "mongosh",
        DATABASE_NAME,
        "--quiet",
        "--eval",
        js_code,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def validate_seed_data(data: dict[str, Any]) -> None:
    """Ensures input JSON conforms to expected schema root collections."""
    required_collections = {"skills", "projects", "experiences"}
    missing = required_collections - set(data.keys())
    if missing:
        raise ValueError(f"Seed file is missing expected collections: {missing}")


def seed_collections(data: dict[str, list[dict[str, Any]]]) -> None:
    """Drops existing collections and loads validated documents with native ObjectId conversion."""
    logger.info("Starting collection provisioning on '%s'...", DATABASE_NAME)

    for collection_name, docs in data.items():
        json_payload = json.dumps(docs)
        js_script = f"""
        const docs = EJSON.parse('{json_payload}');
        db.{collection_name}.drop();
        const res = db.{collection_name}.insertMany(docs);
        print(JSON.stringify({{
            collection: '{collection_name}',
            inserted: Object.keys(res.insertedIds).length
        }}));
        """
        code, stdout, stderr = run_mongosh_command(js_script)
        if code != 0:
            logger.error("Failed to seed collection '%s': %s", collection_name, stderr)
            raise RuntimeError(f"Seeding failed for {collection_name}")

        try:
            summary = json.loads(stdout)
            logger.info(
                "Populated '%s' with %d records.",
                summary["collection"],
                summary["inserted"],
            )
        except json.JSONDecodeError:
            logger.info("Populated '%s': %s", collection_name, stdout)


def provision_indexes() -> None:
    """Builds performance indexes: unique, compound, and full-text search indexes."""
    logger.info("Provisioning collection indexes...")

    index_script = """
    // 1. Projects: Unique slug index
    db.projects.createIndex({ slug: 1 }, { unique: true, name: "uniq_project_slug" });

    // 2. Projects: Compound index for status filtering and star sorting
    db.projects.createIndex({ status: 1, stars: -1 }, { name: "idx_projects_status_stars" });

    // 3. Projects: Full-text search with relevance weighting
    db.projects.createIndex(
        { title: "text", summary: "text", description: "text" },
        {
            weights: { title: 10, summary: 5, description: 1 },
            name: "idx_projects_fulltext"
        }
    );

    // 4. Skills: Compound index on category and proficiency
    db.skills.createIndex({ category: 1, proficiency: -1 }, { name: "idx_skills_category_proficiency" });

    // 5. Experiences: Index on is_current
    db.experiences.createIndex({ is_current: -1 }, { name: "idx_exp_is_current" });

    print(JSON.stringify({
        project_indexes: db.projects.getIndexes().map(i => i.name),
        skill_indexes: db.skills.getIndexes().map(i => i.name),
        experience_indexes: db.experiences.getIndexes().map(i => i.name)
    }));
    """
    code, stdout, stderr = run_mongosh_command(index_script)
    if code != 0:
        logger.error("Index creation failed: %s", stderr)
        raise RuntimeError("Failed to provision indexes")

    try:
        report = json.loads(stdout)
        logger.info("Project Indexes: %s", report["project_indexes"])
        logger.info("Skill Indexes: %s", report["skill_indexes"])
        logger.info("Experience Indexes: %s", report["experience_indexes"])
    except json.JSONDecodeError:
        logger.info("Indexes built: %s", stdout)


def main() -> int:
    seed_file = Path(__file__).parent / "sample_seed_data.json"
    if not seed_file.is_file():
        logger.critical("Seed data file not found at: %s", seed_file)
        return 1

    try:
        with open(seed_file, encoding="utf-8") as f:
            data = json.load(f)

        validate_seed_data(data)
        seed_collections(data)
        provision_indexes()
        logger.info("Database provisioning & indexing completed successfully.")
        return 0
    except Exception as e:
        logger.exception("Database provisioning aborted: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
