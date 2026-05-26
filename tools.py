import json
import pathlib
import datetime

JOBS_DATA: dict = json.loads(
    (pathlib.Path(__file__).parent / "DOCS" / "Supplied" / "sample-jobtread.json").read_text()
)

TOOLS: list[dict] = [
    {
        "name": "get_jobs",
        "description": (
            "Returns a filtered list of LUX jobs from the database. "
            "Use this first to identify which jobs need attention before drilling into specifics. "
            "Filter 'over_budget' returns jobs where actual_cost exceeds estimated_cost. "
            "Filter 'behind_schedule' returns jobs where projected_completion is later than estimated_completion. "
            "Filter 'active' returns only jobs with status equal to active. "
            "Filter 'all' returns every job in the dataset."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "enum": ["all", "over_budget", "behind_schedule", "active"],
                    "description": "Which subset of jobs to return."
                }
            },
            "required": ["filter"]
        }
    },
    {
        "name": "get_job_details",
        "description": (
            "Returns the complete record for a specific job including notes. "
            "Use this after get_jobs when Brad asks about a named job or requests a snapshot."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "The job ID, for example LUX-001. Case-insensitive."
                }
            },
            "required": ["job_id"]
        }
    }
]


def _compute_fields(job: dict) -> dict:
    """Return a copy of job augmented with budget_variance and schedule_slip_days."""
    augmented = job.copy()
    augmented["budget_variance"] = job["actual_cost"] - job["estimated_cost"]
    projected = datetime.date.fromisoformat(job["projected_completion"])
    estimated = datetime.date.fromisoformat(job["estimated_completion"])
    augmented["schedule_slip_days"] = (projected - estimated).days
    return augmented


def _build_job_summary(job: dict) -> dict:
    """Return a summary dict with key fields only, computed from the raw job record."""
    augmented = _compute_fields(job)
    return {
        "job_id": augmented["job_id"],
        "job_name": augmented["job_name"],
        "status": augmented["status"],
        "phase": augmented["phase"],
        "pm": augmented["pm"],
        "estimated_cost": augmented["estimated_cost"],
        "actual_cost": augmented["actual_cost"],
        "budget_variance": augmented["budget_variance"],
        "estimated_completion": augmented["estimated_completion"],
        "projected_completion": augmented["projected_completion"],
        "schedule_slip_days": augmented["schedule_slip_days"],
    }


def get_jobs(filter: str) -> list[dict] | dict:
    """Return a filtered list of job summaries from the dataset."""
    jobs = JOBS_DATA["jobs"]

    if filter == "all":
        return [_build_job_summary(job) for job in jobs]

    if filter == "active":
        return [_build_job_summary(job) for job in jobs if job["status"] == "active"]

    if filter == "over_budget":
        return [_build_job_summary(job) for job in jobs if job["actual_cost"] > job["estimated_cost"]]

    if filter == "behind_schedule":
        matching = []
        for job in jobs:
            projected = datetime.date.fromisoformat(job["projected_completion"])
            estimated = datetime.date.fromisoformat(job["estimated_completion"])
            if projected > estimated:
                matching.append(_build_job_summary(job))
        return matching

    return {"error": "Unknown filter. Valid values: all, over_budget, behind_schedule, active"}


def get_job_details(job_id: str) -> dict:
    """Return the full record for a job by ID, case-insensitive."""
    normalized = job_id.upper()
    for job in JOBS_DATA["jobs"]:
        if job["job_id"].upper() == normalized:
            return _compute_fields(job)
    return {"error": f"Job {job_id} not found. Use get_jobs to list available jobs."}


def execute_tool(name: str, tool_input: dict) -> list | dict:
    """Dispatch a tool call by name and return its result."""
    if name == "get_jobs":
        try:
            return get_jobs(tool_input["filter"])
        except (ValueError, KeyError, TypeError) as e:
            return {"error": str(e)}

    elif name == "get_job_details":
        try:
            return get_job_details(tool_input["job_id"])
        except (ValueError, KeyError, TypeError) as e:
            return {"error": str(e)}

    else:
        return {"error": f"Unknown tool: {name}"}
