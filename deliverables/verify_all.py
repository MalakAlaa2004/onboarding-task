"""
NovaGates Infrastructure Smoke Test & Verification Suite
Validates live Docker containers, MongoDB query plans, aggregations,
indexes, and Redis caching semantics.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import time
from typing import Callable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("SmokeTest")


class TestRunner:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.results: list[tuple[str, bool, float, str]] = []

    def run_test(self, name: str, test_func: Callable[[], str]) -> None:
        start = time.perf_counter()
        try:
            detail = test_func()
            duration = (time.perf_counter() - start) * 1000
            self.results.append((name, True, duration, detail))
            self.passed += 1
            logger.info("PASS: %s (%.1f ms) - %s", name, duration, detail)
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self.results.append((name, False, duration, str(e)))
            self.failed += 1
            logger.error("FAIL: %s (%.1f ms) - %s", name, duration, e)


def exec_docker(cmd: list[str]) -> str:
    res = subprocess.run(
        ["docker", "exec", "-i"] + cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {res.stderr.strip()}")
    return res.stdout.strip()


def test_docker_containers() -> str:
    out = subprocess.run(
        ["docker", "compose", "ps", "--format", "json"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if "novagates-mongodb" not in out or "novagates-redis" not in out:
        raise AssertionError("Required containers not found in docker compose ps")
    return "Both mongodb and redis containers are active"


def test_mongodb_connection() -> str:
    res = exec_docker(
        [
            "novagates-mongodb",
            "mongosh",
            "--quiet",
            "--eval",
            "print(JSON.stringify(db.adminCommand('ping')))",
        ]
    )
    data = json.loads(res)
    if data.get("ok") != 1:
        raise AssertionError(f"Unexpected ping response: {res}")
    return "MongoDB server responded to admin ping with ok: 1"


def test_mongodb_indexes() -> str:
    script = "JSON.stringify(db.projects.getIndexes().map(i => i.name));"
    res = exec_docker(["novagates-mongodb", "mongosh", "portfolio_db", "--quiet", "--eval", script])
    indexes = json.loads(res)
    expected = {"_id_", "uniq_project_slug", "idx_projects_status_stars", "idx_projects_fulltext"}
    if not expected.issubset(set(indexes)):
        raise AssertionError(f"Missing required indexes. Found: {indexes}")
    return f"Verified indexes: {indexes}"


def test_mongodb_aggregation() -> str:
    script = """
    const res = db.projects.aggregate([
      { $match: { featured: true } },
      { $lookup: { from: 'skills', localField: 'skill_ids', foreignField: '_id', as: 'skills' } },
      { $project: { title: 1, skill_count: { $size: '$skills' } } }
    ]).toArray();
    print(JSON.stringify(res));
    """
    res = exec_docker(["novagates-mongodb", "mongosh", "portfolio_db", "--quiet", "--eval", script])
    docs = json.loads(res)
    if len(docs) < 2:
        raise AssertionError(f"Expected at least 2 featured projects, got {len(docs)}")
    if docs[0]["skill_count"] < 1:
        raise AssertionError("Aggregation failed to populate joined skills array")
    return f"Successfully aggregated {len(docs)} projects with populated skills"


def test_mongodb_text_search() -> str:
    script = """
    const res = db.projects.find(
      { $text: { $search: "agent celery" } },
      { title: 1, score: { $meta: "textScore" } }
    ).sort({ score: { $meta: "textScore" } }).toArray();
    print(JSON.stringify(res));
    """
    res = exec_docker(["novagates-mongodb", "mongosh", "portfolio_db", "--quiet", "--eval", script])
    docs = json.loads(res)
    if not docs:
        raise AssertionError("Text search failed to return matching projects")
    return f"Text search matched '{docs[0]['title']}' with score {docs[0]['score']:.2f}"


def test_redis_strings_ttl() -> str:
    exec_docker(["novagates-redis", "redis-cli", "SET", "test:key", "senior-dev-val", "EX", "30"])
    val = exec_docker(["novagates-redis", "redis-cli", "GET", "test:key"])
    ttl = int(exec_docker(["novagates-redis", "redis-cli", "TTL", "test:key"]))
    if val != "senior-dev-val" or ttl <= 0 or ttl > 30:
        raise AssertionError(f"Redis string/TTL mismatch: val={val}, ttl={ttl}")
    return f"Value verified ('{val}'), TTL={ttl}s"


def test_redis_queue_semantics() -> str:
    queue = "test:work:queue"
    exec_docker(["novagates-redis", "redis-cli", "DEL", queue])
    exec_docker(["novagates-redis", "redis-cli", "RPUSH", queue, "job_1", "job_2", "job_3"])
    length = int(exec_docker(["novagates-redis", "redis-cli", "LLEN", queue]))
    popped = exec_docker(["novagates-redis", "redis-cli", "LPOP", queue])
    if length != 3 or popped != "job_1":
        raise AssertionError(f"FIFO Queue mismatch: len={length}, popped={popped}")
    return f"FIFO Queue verified: length={length}, popped head={popped}"


def test_redis_hashes() -> str:
    hash_key = "test:cache:project:11"
    exec_docker(["novagates-redis", "redis-cli", "DEL", hash_key])
    exec_docker(["novagates-redis", "redis-cli", "HSET", hash_key, "slug", "smart-job-matcher", "views", "120"])
    slug = exec_docker(["novagates-redis", "redis-cli", "HGET", hash_key, "slug"])
    if slug != "smart-job-matcher":
        raise AssertionError(f"Hash get returned: {slug}")
    return f"Hash key verified with slug: {slug}"


def main() -> int:
    print("\n" + "=" * 70)
    print("   NovaGates Backend & AI - Senior Engineer Smoke Test Suite    ")
    print("=" * 70)

    runner = TestRunner()
    runner.run_test("Docker Containers State", test_docker_containers)
    runner.run_test("MongoDB Ping & Health", test_mongodb_connection)
    runner.run_test("MongoDB Performance Indexes", test_mongodb_indexes)
    runner.run_test("MongoDB Relational Aggregation", test_mongodb_aggregation)
    runner.run_test("MongoDB Weighted Text Search", test_mongodb_text_search)
    runner.run_test("Redis String & TTL Expiry", test_redis_strings_ttl)
    runner.run_test("Redis FIFO Task Queue", test_redis_queue_semantics)
    runner.run_test("Redis Hash Data Structure", test_redis_hashes)

    print("\n" + "-" * 70)
    print(f" Summary: {runner.passed} Passed, {runner.failed} Failed")
    print("-" * 70)

    for name, status, duration, detail in runner.results:
        flag = "[PASS]" if status else "[FAIL]"
        print(f"{flag} {name:<32} ({duration:5.1f}ms) -> {detail}")
    print("=" * 70 + "\n")

    return 0 if runner.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
