import base64
import json
import os
from datetime import datetime, timezone

import httpx
from fastmcp import FastMCP

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")

API = "https://api.github.com"
QUEUE_PATH = "queue.json"
STATUS_PATH = "status.json"

mcp = FastMCP("NX Cloud Test")


def _headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _file_url(path: str) -> str:
    return f"{API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"


async def _write_json(path: str, data: dict) -> dict:
    if not all([GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO]):
        raise ValueError("GitHub environment variables are not configured")

    url = _file_url(path)
    params = {"ref": GITHUB_BRANCH}
    sha = None

    async with httpx.AsyncClient(timeout=30) as client:
        existing = await client.get(url, headers=_headers(), params=params)

        if existing.status_code == 200:
            sha = existing.json().get("sha")
        elif existing.status_code != 404:
            existing.raise_for_status()

        payload = {
            "message": f"Update {path}",
            "content": base64.b64encode(
                json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            ).decode("ascii"),
            "branch": GITHUB_BRANCH,
        }

        if sha:
            payload["sha"] = sha

        response = await client.put(url, headers=_headers(), json=payload)
        response.raise_for_status()

    return data


@mcp.tool
async def set_nx_task(
    action: str,
    parameters: dict | None = None,
    task_id: str = "",
) -> dict:
    """Заменить текущее задание для NX. Старое задание стирается."""
    if not action:
        raise ValueError("action is required")

    task_id = task_id or datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    task = {
        "task_id": task_id,
        "action": action,
        "parameters": parameters or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
    }

    await _write_json(QUEUE_PATH, task)

    await _write_json(
        STATUS_PATH,
        {
            "task_id": task_id,
            "state": "queued",
            "result": {},
            "error": "",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    return {"status": "queued", "task_id": task_id, "action": action}


@mcp.tool
async def clear_nx_task(task_id: str = "") -> dict:
    """Очистить очередь после выполнения задания."""
    cleared = {
        "task_id": "",
        "action": "",
        "parameters": {},
        "created_at": "",
        "status": "empty",
    }

    await _write_json(QUEUE_PATH, cleared)
    return {"status": "cleared", "task_id": task_id}


@mcp.tool
def cloud_ping(message: str = "hello") -> dict:
    """Проверить связь с облачным MCP. Не обращается к Siemens NX."""
    return {
        "status": "ok",
        "message": message,
        "nx_connected": False,
    }


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        stateless_http=True,
    )
