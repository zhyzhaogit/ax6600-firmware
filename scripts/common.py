from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def write_text(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def github_request(url: str) -> bytes:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ax6600-firmware-control-plane",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=30) as response:
            return response.read()
    except HTTPError as exc:
        raise RuntimeError(f"GitHub request failed for {url}: HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"GitHub request failed for {url}: {exc.reason}") from exc


def github_json(url: str) -> Any:
    return json.loads(github_request(url).decode("utf-8"))


def github_commit(repo: str, branch: str) -> dict[str, Any]:
    try:
        payload = github_json(f"https://api.github.com/repos/{repo}/commits/{branch}")
        return {
            "sha": payload["sha"],
            "date": payload["commit"]["committer"]["date"],
            "message": payload["commit"]["message"].splitlines()[0],
            "html_url": payload["html_url"],
        }
    except RuntimeError:
        result = subprocess.run(
            ["git", "ls-remote", f"https://github.com/{repo}.git", f"refs/heads/{branch}"],
            check=True,
            capture_output=True,
            text=True,
        )
        sha = result.stdout.strip().split()[0]
        return {
            "sha": sha,
            "date": "unknown",
            "message": "resolved-via-git-ls-remote",
            "html_url": f"https://github.com/{repo}/tree/{branch}",
        }


def github_raw(repo: str, branch: str, path: str) -> str:
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
    return github_request(url).decode("utf-8")


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, divider, *body])
