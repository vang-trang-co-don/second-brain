#!/usr/bin/env python3
"""
Session Distillation & Catalog Engine for Second Brain.
Multi-source ingestion (Pi & AGY), noise filtering, semantic titling, and SQLite FTS5 catalog.
"""

import os
import sys
import json
import re
import glob
import hashlib
import sqlite3
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

# Patterns to clean noise
_SKILL_TAG = re.compile(r"</?skill\b[^>]*>", re.IGNORECASE)
_USER_TAG = re.compile(r"</?USER_REQUEST>", re.IGNORECASE)
_UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE)

def strip_skills(text: str) -> str:
    """Remove skill injection blocks and user tags from prompts."""
    # First strip user tags
    text = _USER_TAG.sub("", text)
    parts, start, depth = [], 0, 0
    for match in _SKILL_TAG.finditer(text):
        if not depth:
            parts.append(text[start:match.start()])
        if match.group().startswith("</"):
            depth = max(0, depth - 1)
        elif not match.group().endswith("/>"):
            depth += 1
        start = match.end()
    if not depth:
        parts.append(text[start:])
    return "\n".join(parts).strip()

def compute_file_hash(path: Path) -> str:
    """Compute sha256 hash using mtime and file size for fast idempotency."""
    stat = path.stat()
    raw = f"{stat.st_mtime}-{stat.st_size}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

@dataclass(frozen=True)
class SessionEnvelope:
    source: str
    session_id: str
    workspace: str
    timestamp: str
    raw_path: str
    user_prompts: List[str]
    assistant_summaries: List[str]
    files_touched: List[str]
    file_hash: str

@dataclass(frozen=True)
class SessionCapsule:
    source: str
    session_id: str
    workspace: str
    timestamp: str
    semantic_title: str
    user_goal: str
    decisions: List[str]
    files_touched: List[str]
    raw_path: str
    capsule_text: str

class PiSessionAdapter:
    """Parses ~/.pi/agent/sessions/--<workspace>--/*.jsonl."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(os.path.expanduser("~/.pi/agent/sessions"))

    def parse_workspace_slug(self, folder_name: str) -> str:
        name = folder_name.strip("-")
        if name.startswith("home-dungcq-projects-"):
            return name[len("home-dungcq-projects-"):]
        elif name == "home-dungcq-projects":
            return "projects-root"
        elif name == "home-dungcq":
            return "home"
        return name

    def discover_sessions(self) -> List[Path]:
        if not self.base_dir.exists():
            return []
        files = list(self.base_dir.glob("*/*.jsonl"))
        # Sort by mtime descending
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return files

    def parse_envelope(self, session_path: Path) -> Optional[SessionEnvelope]:
        workspace = self.parse_workspace_slug(session_path.parent.name)
        session_id = session_path.stem.split("_")[-1] if "_" in session_path.stem else session_path.stem

        user_prompts: List[str] = []
        assistant_summaries: List[str] = []
        files_touched_set = set()
        timestamp = ""

        try:
            with open(session_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue

                    entry_type = d.get("type")
                    if entry_type == "session":
                        timestamp = d.get("timestamp", "")
                    elif entry_type == "message":
                        msg = d.get("message", {})
                        role = msg.get("role")
                        content = msg.get("content")

                        if role == "user":
                            text = ""
                            if isinstance(content, list):
                                text = " ".join([c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"])
                            elif isinstance(content, str):
                                text = content
                            clean = strip_skills(text).strip()
                            if clean:
                                user_prompts.append(clean)

                        elif role == "assistant":
                            # Check for toolCall
                            if isinstance(content, list):
                                for item in content:
                                    if not isinstance(item, dict):
                                        continue
                                    if item.get("type") == "toolCall":
                                        tool_name = item.get("name", "")
                                        args = item.get("arguments", {})
                                        if tool_name in {"write", "edit", "write_file", "edit_file", "patch"}:
                                            target_path = args.get("path") or args.get("file") or args.get("target") or args.get("filePath")
                                            if target_path:
                                                files_touched_set.add(os.path.basename(str(target_path)))
                                    elif item.get("type") == "text":
                                        txt = item.get("text", "").strip()
                                        if txt and len(txt) > 40:
                                            assistant_summaries.append(txt)
                            elif isinstance(content, str) and len(content.strip()) > 40:
                                assistant_summaries.append(content.strip())

        except Exception as e:
            print(f"[WARN] Error reading {session_path}: {e}", file=sys.stderr)
            return None

        if not user_prompts and not assistant_summaries:
            return None

        if not timestamp:
            timestamp = datetime.fromtimestamp(session_path.stat().st_mtime).isoformat()

        return SessionEnvelope(
            source="pi",
            session_id=session_id,
            workspace=workspace,
            timestamp=timestamp,
            raw_path=str(session_path.resolve()),
            user_prompts=user_prompts,
            assistant_summaries=assistant_summaries,
            files_touched=sorted(list(files_touched_set)),
            file_hash=compute_file_hash(session_path)
        )

class AgySessionAdapter:
    """Parses ~/.gemini/antigravity-cli/brain/<uuid>/.system_generated/logs/transcript.jsonl."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(os.path.expanduser("~/.gemini/antigravity-cli/brain"))

    def discover_sessions(self) -> List[Path]:
        if not self.base_dir.exists():
            return []
        files = list(self.base_dir.glob("*/.system_generated/logs/transcript.jsonl"))
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return files

    def parse_envelope(self, session_path: Path) -> Optional[SessionEnvelope]:
        session_id = session_path.parent.parent.parent.name
        workspace = "projects"
        timestamp = datetime.fromtimestamp(session_path.stat().st_mtime).isoformat()
        user_prompts: List[str] = []
        assistant_summaries: List[str] = []
        files_touched_set = set()

        try:
            with open(session_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue

                    step_type = d.get("type")
                    if step_type == "USER_INPUT":
                        content = d.get("content", "")
                        clean = strip_skills(content).strip()
                        if clean and not clean.startswith("<SYSTEM_MESSAGE>"):
                            user_prompts.append(clean)
                    elif step_type == "PLANNER_RESPONSE":
                        content = d.get("content", "")
                        if content and len(content.strip()) > 40:
                            assistant_summaries.append(content.strip())
                        tool_calls = d.get("tool_calls", [])
                        for tc in tool_calls:
                            name = tc.get("name", "")
                            args = tc.get("args", {}) or tc.get("arguments", {})
                            if name in {"write_file", "edit_file", "write", "edit"}:
                                p = args.get("Path") or args.get("path")
                                if p:
                                    clean_p = os.path.basename(str(p).strip('"\';:, '))
                                    if clean_p:
                                        files_touched_set.add(clean_p)
        except Exception:
            return None

        if not user_prompts and not assistant_summaries:
            return None

        return SessionEnvelope(
            source="agy",
            session_id=session_id,
            workspace=workspace,
            timestamp=timestamp,
            raw_path=str(session_path.resolve()),
            user_prompts=user_prompts,
            assistant_summaries=assistant_summaries,
            files_touched=sorted(list(files_touched_set)),
            file_hash=compute_file_hash(session_path)
        )

class Distiller:
    """Mines human-meaningful semantic titles, goals, and decisions."""

    def derive_semantic_title(self, envelope: SessionEnvelope) -> str:
        # Find the first real, non-empty, substantive prompt
        substantive_prompts = []
        for p in envelope.user_prompts:
            clean = p.strip()
            # Skip noise like single words or path references
            if clean in {"continue", "ok", "yes", "tiếp", "tiếp tục", "hi", "hello"}:
                continue
            if clean.startswith("~/.pi/agent/sessions/"):
                continue
            substantive_prompts.append(clean)

        main_topic = ""
        if substantive_prompts:
            first_sub = substantive_prompts[0]
            # Strip markdown formatting
            first_sub = re.sub(r"[#*`_]", "", first_sub)
            first_line = first_sub.split("\n")[0].strip()
            if len(first_line) > 80:
                first_line = first_line[:77] + "..."
            main_topic = first_line
        elif envelope.user_prompts:
            main_topic = envelope.user_prompts[0][:60]
        else:
            main_topic = "General engineering tasks"

        # If files were touched, append prominent files
        if envelope.files_touched:
            top_files = ", ".join(envelope.files_touched[:2])
            return f"[{envelope.workspace}] {main_topic} ({top_files})"
        return f"[{envelope.workspace}] {main_topic}"

    def extract_decisions(self, envelope: SessionEnvelope) -> List[str]:
        decisions: List[str] = []
        decision_patterns = [
            re.compile(r"(?:quy định|thống nhất|quyết định|nguyên tắc|bất biến|lưu ý|chốt):\s*(.*)", re.IGNORECASE),
            re.compile(r"^\s*[-*]\s*(.*\b(?:phải|không được|cần|chỉ|dùng|luôn)\b.*)", re.IGNORECASE | re.MULTILINE),
            re.compile(r"^\s*([0-9]+\.\s*.*\b(?:database|schema|api|model|config|account)\b.*)", re.IGNORECASE | re.MULTILINE),
        ]

        # Scan user prompts for explicit instructions
        for p in envelope.user_prompts:
            for pat in decision_patterns:
                for match in pat.finditer(p):
                    text = match.group(1).strip()
                    if 15 < len(text) < 160 and text not in decisions:
                        decisions.append(text)
                    if len(decisions) >= 5:
                        break

        # Scan assistant text if decisions are few
        if len(decisions) < 3 and envelope.assistant_summaries:
            last_text = envelope.assistant_summaries[-1]
            for pat in decision_patterns:
                for match in pat.finditer(last_text):
                    text = match.group(1).strip()
                    if 15 < len(text) < 160 and text not in decisions:
                        decisions.append(text)
                    if len(decisions) >= 5:
                        break

        return decisions[:5]

    def distill(self, envelope: SessionEnvelope) -> SessionCapsule:
        semantic_title = self.derive_semantic_title(envelope)
        user_goal = envelope.user_prompts[0][:200] if envelope.user_prompts else "No explicit prompt"
        decisions = self.extract_decisions(envelope)

        # Build clean capsule markdown
        lines = [
            f"# {semantic_title}",
            "",
            f"- **Source:** `{envelope.source}`",
            f"- **Session ID:** `{envelope.session_id}`",
            f"- **Workspace:** `{envelope.workspace}`",
            f"- **Timestamp:** `{envelope.timestamp}`",
            f"- **Raw Path:** `{envelope.raw_path}`",
            "",
            "## 1. User Goal",
            f"{user_goal}",
            ""
        ]

        if decisions:
            lines.append("## 2. Key Decisions & Invariants")
            for d in decisions:
                lines.append(f"- {d}")
            lines.append("")

        if envelope.files_touched:
            lines.append("## 3. Files Touched")
            for f in envelope.files_touched:
                lines.append(f"- `{f}`")
            lines.append("")

        capsule_text = "\n".join(lines).strip()

        return SessionCapsule(
            source=envelope.source,
            session_id=envelope.session_id,
            workspace=envelope.workspace,
            timestamp=envelope.timestamp,
            semantic_title=semantic_title,
            user_goal=user_goal,
            decisions=decisions,
            files_touched=envelope.files_touched,
            raw_path=envelope.raw_path,
            capsule_text=capsule_text
        )

class CatalogStore:
    """Manages SQLite FTS5 database and markdown storage."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.sessions_dir = self.root_dir / "sessions"
        self.capsules_dir = self.sessions_dir / "capsules"
        self.db_path = self.sessions_dir / "catalog.sqlite3"

        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.capsules_dir.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    def get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self.get_conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                source TEXT,
                workspace TEXT,
                timestamp TEXT,
                semantic_title TEXT,
                user_goal TEXT,
                capsule_path TEXT,
                raw_path TEXT,
                file_hash TEXT,
                created_at TEXT
            )
            """)
            conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
                id UNINDEXED,
                source,
                workspace,
                semantic_title,
                user_goal,
                decisions_text,
                files_text,
                capsule_text
            )
            """)
            conn.commit()

    def get_existing_hash(self, session_id: str) -> Optional[str]:
        with self.get_conn() as conn:
            cur = conn.execute("SELECT file_hash FROM sessions WHERE id = ?", (session_id,))
            row = cur.fetchone()
            return row["file_hash"] if row else None

    def save_capsule(self, capsule: SessionCapsule, file_hash: str) -> Path:
        capsule_file = self.capsules_dir / f"{capsule.session_id}.md"
        with open(capsule_file, "w", encoding="utf-8") as f:
            f.write(capsule.capsule_text + "\n")

        decisions_str = " ".join(capsule.decisions)
        files_str = " ".join(capsule.files_touched)
        now_iso = datetime.now().isoformat()

        with self.get_conn() as conn:
            conn.execute("""
            INSERT INTO sessions (id, source, workspace, timestamp, semantic_title, user_goal, capsule_path, raw_path, file_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                semantic_title = excluded.semantic_title,
                user_goal = excluded.user_goal,
                capsule_path = excluded.capsule_path,
                raw_path = excluded.raw_path,
                file_hash = excluded.file_hash,
                created_at = excluded.created_at
            """, (
                capsule.session_id, capsule.source, capsule.workspace,
                capsule.timestamp, capsule.semantic_title, capsule.user_goal,
                str(capsule_file.resolve()), capsule.raw_path, file_hash, now_iso
            ))

            # Delete old FTS row if exists
            conn.execute("DELETE FROM sessions_fts WHERE id = ?", (capsule.session_id,))
            conn.execute("""
            INSERT INTO sessions_fts (id, source, workspace, semantic_title, user_goal, decisions_text, files_text, capsule_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                capsule.session_id, capsule.source, capsule.workspace,
                capsule.semantic_title, capsule.user_goal, decisions_str,
                files_str, capsule.capsule_text
            ))
            conn.commit()

        return capsule_file

    def list_sessions(self, workspace: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_conn() as conn:
            if workspace:
                cur = conn.execute(
                    "SELECT * FROM sessions WHERE workspace = ? ORDER BY timestamp DESC LIMIT ?",
                    (workspace, limit)
                )
            else:
                cur = conn.execute(
                    "SELECT * FROM sessions ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
            return [dict(r) for r in cur.fetchall()]

    def search(self, query: str, workspace: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        clean_q = re.sub(r"[^\w\s]", " ", query).strip()
        if not clean_q:
            return []
        tokens = clean_q.split()
        fts_query = " ".join([f'"{t}"*' for t in tokens])

        with self.get_conn() as conn:
            if workspace:
                sql = """
                SELECT s.*, snippet(sessions_fts, 7, '>>>', '<<<', '...', 15) as snippet
                FROM sessions_fts f
                JOIN sessions s ON f.id = s.id
                WHERE sessions_fts MATCH ? AND s.workspace = ?
                ORDER BY rank LIMIT ?
                """
                cur = conn.execute(sql, (fts_query, workspace, limit))
            else:
                sql = """
                SELECT s.*, snippet(sessions_fts, 7, '>>>', '<<<', '...', 15) as snippet
                FROM sessions_fts f
                JOIN sessions s ON f.id = s.id
                WHERE sessions_fts MATCH ?
                ORDER BY rank LIMIT ?
                """
                cur = conn.execute(sql, (fts_query, limit))
            return [dict(r) for r in cur.fetchall()]

    def sync_markdown_index(self) -> Path:
        """Regenerate second-brain/sessions/SESSIONS.md."""
        sessions = self.list_sessions(limit=500)
        index_file = self.sessions_dir / "SESSIONS.md"

        lines = [
            "# Second Brain - Session History Archive",
            "",
            "> Lịch sử các session của Pi và AGY đã được chưng cất thành semantic capsules.",
            "",
            f"**Tổng số session đã lập chỉ mục:** {len(sessions)}",
            "",
            "| Nguồn | Ngày | Dự án | Tiêu đề Ngữ Nghĩa | Capsule |",
            "| :---: | :---: | :---: | :--- | :---: |"
        ]

        for s in sessions:
            date_str = s["timestamp"][:10] if len(s["timestamp"]) >= 10 else s["timestamp"]
            cid = s["id"]
            short_id = cid[:8]
            title = s["semantic_title"]
            ws = s["workspace"]
            src = s["source"]
            rel_path = f"capsules/{cid}.md"
            lines.append(f"| `{src}` | {date_str} | `{ws}` | {title} | [Capsule]({rel_path}) |")

        lines.append("")
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return index_file
