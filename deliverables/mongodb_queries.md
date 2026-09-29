# NovaGates Onboarding — Milestone: MongoDB Query Notebook
**Author:** Junior Backend & AI Developer  
**Reviewer:** Onboarding Buddy / Engineering Lead  
**Topic:** MongoDB CRUD, Indexing, Aggregation Pipelines, Text Search, and Atlas Vector Search  
**Reference Domain:** Portfolio API (`skills`, `projects`, `experiences`)

---

## 1. Overview & Setup

This query notebook fulfills the **Day 3 Milestone** of the NovaGates 2-Week Onboarding Programme. All queries operate on the `portfolio_db` database using the sample schema provided in [`sample_seed_data.json`](file:///d:/Work-orientation/deliverables/sample_seed_data.json).

### Connecting to MongoDB
From `mongosh`, MongoDB Compass, or Studio 3T:
```javascript
// Select the database
use portfolio_db;
```

---

## Part 1: CRUD Operations

### Query 1: Single & Bulk Insert (`insertOne`, `insertMany`)
**Objective:** Populate skills and verify BSON document structure.
```javascript
// 1.1 Insert a single new skill
db.skills.insertOne({
  name: "Celery",
  category: "Backend",
  proficiency: 82,
  years_experience: 2,
  tags: ["async", "queue", "distributed", "python"]
});

// 1.2 Insert multiple skills in a single round-trip
db.skills.insertMany([
  {
    name: "PostgreSQL",
    category: "Database",
    proficiency: 78,
    years_experience: 2,
    tags: ["relational", "sql", "acid"]
  },
  {
    name: "Tavily API",
    category: "AI / ML",
    proficiency: 85,
    years_experience: 1,
    tags: ["search", "ai", "rag", "agents"]
  }
]);
```

### Query 2: Finding Documents with Projection
**Objective:** Fetch all active projects without returning large vector embedding fields to save network bandwidth.
```javascript
db.projects.find(
  { status: "completed" },
  { title: 1, slug: 1, stars: 1, status: 1, _id: 1 } // Projection mask: exclude embedding
);
```

### Query 3: Atomic Updates (`updateOne`, `updateMany`)
**Objective:** Increment project stars atomically and push a new tag into a skill.
```javascript
// 3.1 Increment stars using $inc and update status using $set
db.projects.updateOne(
  { slug: "smart-job-matcher" },
  {
    $inc: { stars: 1 },
    $set: { last_reviewed_at: new Date() }
  }
);

// 3.2 Add a tag to all AI / ML skills without duplicates using $addToSet
db.skills.updateMany(
  { category: "AI / ML" },
  { $addToSet: { tags: "generative-ai" } }
);
```

### Query 4: Safe Document Deletion (`deleteOne`, `deleteMany`)
**Objective:** Remove deprecated test skills safely.
```javascript
db.skills.deleteMany({
  category: "Draft",
  proficiency: { $lt: 50 }
});
```

---

## Part 2: Filtering & Cursor Operations

### Query 5: Comprehensive Filtering
**Objective:** Find high-proficiency Backend or Database skills using `$and`, `$or`, `$in`, `$gt`, and `$regex`.
```javascript
db.skills.find({
  $and: [
    { proficiency: { $gte: 80 } },
    {
      $or: [
        { category: { $in: ["Backend", "Database"] } },
        { tags: { $regex: /^ai/i } }
      ]
    },
    { years_experience: { $exists: true, $ne: null } }
  ]
});
```

### Query 6: Cursor Pagination (Sort, Limit, Skip)
**Objective:** Retrieve the top featured projects ordered by stars descending, paginated for a web view (Page 1, 2 items per page).
```javascript
db.projects.find({ featured: true })
  .sort({ stars: -1, title: 1 })
  .skip(0)
  .limit(2);
```

---

## Part 3: Indexes & Query Plans (`explain`)

### Query 7: Creating Single-Field and Compound Indexes
**Objective:** Accelerate queries filtering by project status and ordering by stars.
```javascript
// 7.1 Single-field index on slug for unique lookups
db.projects.createIndex({ slug: 1 }, { unique: true });

// 7.2 Compound index on category + proficiency for skills filtering
db.skills.createIndex({ category: 1, proficiency: -1 });

// 7.3 Compound index on status + stars for leaderboard queries
db.projects.createIndex({ status: 1, stars: -1 });
```

### Query 8: Analyzing Execution Plans (`explain("executionStats")`)
**Objective:** Verify that the query engine performs an `IXSCAN` (Index Scan) rather than an expensive `COLLSCAN` (Collection Scan).
```javascript
db.projects.find({ status: "completed" })
  .sort({ stars: -1 })
  .explain("executionStats");
```
*Expected Execution Verification:*
- `winningPlan.inputStage.stage`: `"IXSCAN"`
- `totalDocsExamined` should match `nReturned`, proving zero wasted document reads.

---

## Part 4: Advanced Aggregation Pipelines

### Query 9: Skill Distribution & Statistical Breakdown
**Objective:** Group skills by category to calculate average proficiency, total count, and a list of all distinct tags using `$unwind`, `$group`, `$sort`, and `$project`.
```javascript
db.skills.aggregate([
  // Stage 1: Unwind tags array to analyze individual tags
  { $unwind: "$tags" },

  // Stage 2: Group by category
  {
    $group: {
      _id: "$category",
      total_skills: { $addToSet: "$name" },
      avg_proficiency: { $avg: "$proficiency" },
      all_tags: { $addToSet: "$tags" }
    }
  },

  // Stage 3: Reshape output for API consumption
  {
    $project: {
      _id: 0,
      category: "$_id",
      skill_count: { $size: "$total_skills" },
      skills: "$total_skills",
      average_proficiency: { $round: ["$avg_proficiency", 1] },
      tags: "$all_tags"
    }
  },

  // Stage 4: Sort by skill count descending
  { $sort: { skill_count: -1 } }
]);
```

### Query 10: Relational Join with `$lookup` and `$unwind`
**Objective:** Populate each project with full details of its referenced `skill_ids` (simulating foreign key relationship in document DB).
```javascript
db.projects.aggregate([
  // Stage 1: Match only featured projects
  { $match: { featured: true } },

  // Stage 2: Join with skills collection
  {
    $lookup: {
      from: "skills",
      localField: "skill_ids",
      foreignField: "_id",
      as: "skill_details"
    }
  },

  // Stage 3: Add calculated fields
  {
    $addFields: {
      skill_names: "$skill_details.name",
      primary_skill_count: { $size: "$skill_details" }
    }
  },

  // Stage 4: Clean projection
  {
    $project: {
      title: 1,
      slug: 1,
      status: 1,
      stars: 1,
      skill_names: 1,
      primary_skill_count: 1
    }
  },

  // Stage 5: Sort by popularity
  { $sort: { stars: -1 } }
]);
```

### Query 11: Experience Duration & Technology Cloud Aggregation
**Objective:** Aggregate work history to determine tenure and extract consolidated technology stacks.
```javascript
db.experiences.aggregate([
  // Stage 1: Match active or past career experiences
  { $match: { company: { $exists: true } } },

  // Stage 2: Project formatted company summary
  {
    $project: {
      company: 1,
      role: 1,
      is_current: 1,
      tech_count: { $size: "$technologies" },
      technologies: 1,
      responsibilities_count: { $size: "$responsibilities" }
    }
  },

  // Stage 3: Sort by current jobs first
  { $sort: { is_current: -1, company: 1 } }
]);
```

---

## Part 5: Full-Text Search

### Query 12: Creating Text Index and Searching with Score Relevance
**Objective:** Enable full-text search across project titles and summaries, ranking results by BM25/text score.
```javascript
// 12.1 Create compound text index with field weights
db.projects.createIndex(
  {
    title: "text",
    summary: "text",
    description: "text"
  },
  {
    weights: {
      title: 10,       // Matches in title are 10x more relevant
      summary: 5,       // Matches in summary are 5x more relevant
      description: 1
    },
    name: "project_fulltext_idx"
  }
);

// 12.2 Query using $text and sort by textScore
db.projects.find(
  { $text: { $search: "agent celery background" } },
  { score: { $meta: "textScore" }, title: 1, summary: 1 }
).sort({ score: { $meta: "textScore" } });
```

---

## Part 6: MongoDB Atlas Vector Search

### What are Embeddings?
Embeddings are dense numerical vector representations of textual or multimodal concepts (e.g. 768 or 1536 floating point numbers). Semantically similar concepts reside close to one another in multi-dimensional vector space, enabling semantic retrieval beyond literal keyword matches.

### Vector Search Index Definition (MongoDB Atlas)
In MongoDB Atlas UI or via Atlas CLI:
```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 8,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "status"
    }
  ]
}
```

### Query 13: Semantic Search using `$vectorSearch`
**Objective:** Match user search queries (e.g. "Find an autonomous AI worker that automates tasks") against projects using their vector embeddings.
```javascript
db.projects.aggregate([
  {
    $vectorSearch: {
      index: "vector_index",
      path: "embedding",
      queryVector: [0.480, 0.190, -0.090, 0.620, 0.410, -0.080, 0.290, 0.490],
      numCandidates: 50,
      limit: 3,
      filter: {
        status: { $in: ["completed", "in-progress"] }
      }
    }
  },
  {
    $project: {
      _id: 1,
      title: 1,
      summary: 1,
      status: 1,
      similarity_score: { $meta: "vectorSearchScore" }
    }
  }
]);
```

---

## Summary Checklist for Pull Request Review

- [x] CRUD operations (`insertOne`, `insertMany`, `find`, `updateOne`, `updateMany`, `deleteMany`).
- [x] Filtering with `$and`, `$or`, `$in`, `$gt`, `$exists`, `$regex`.
- [x] Cursor methods (`sort`, `skip`, `limit`, projection).
- [x] Performance indexing (`createIndex` and `explain("executionStats")`).
- [x] 3+ Aggregation pipelines with `$group`, `$lookup`, `$unwind`, `$addFields`, `$project`.
- [x] Full-text index with weighted fields and `$meta: "textScore"`.
- [x] Atlas `$vectorSearch` pipeline query with embeddings explanation.
- [x] Sample data file [`sample_seed_data.json`](file:///d:/Work-orientation/deliverables/sample_seed_data.json) included for instant testing.
