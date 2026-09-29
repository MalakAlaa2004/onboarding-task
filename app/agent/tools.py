from __future__ import annotations

import json

from langchain_core.tools import tool

from app.models.experience import Experience
from app.models.project import Project
from app.models.skill import Skill


@tool
async def search_skills(category: str = "") -> str:
    """Search developer skills in portfolio. Optionally filter by category (e.g. Backend, AI / ML, Database)."""
    if category:
        skills = await Skill.find(Skill.category == category).to_list()
    else:
        skills = await Skill.find().to_list()

    items = [
        {
            "name": s.name,
            "category": s.category,
            "proficiency": s.proficiency,
            "years_experience": s.years_experience,
            "tags": s.tags,
        }
        for s in skills
    ]
    return json.dumps(items)


@tool
async def search_projects(query: str = "", featured_only: bool = False) -> str:
    """Search developer projects in portfolio. Optionally specify a query string or filter by featured projects only."""
    if query:
        projects = await Project.find({"$text": {"$search": query}}).to_list()
    elif featured_only:
        projects = await Project.find(Project.featured == True).to_list()  # noqa: E712
    else:
        projects = await Project.find().to_list()

    items = [
        {
            "title": p.title,
            "slug": p.slug,
            "summary": p.summary,
            "status": p.status,
            "stars": p.stars,
        }
        for p in projects
    ]
    return json.dumps(items)


@tool
async def get_career_experience() -> str:
    """Retrieve full work experience and timeline from the developer's portfolio."""
    experiences = await Experience.find().sort("-is_current").to_list()
    items = [
        {
            "company": e.company,
            "role": e.role,
            "start_date": e.start_date,
            "end_date": e.end_date,
            "is_current": e.is_current,
            "technologies": e.technologies,
            "responsibilities": e.responsibilities,
        }
        for e in experiences
    ]
    return json.dumps(items)


PORTFOLIO_TOOLS = [search_skills, search_projects, get_career_experience]
