#!/usr/bin/env python3
"""
Architect Sketch: Multi-Source Session Distillation & Catalog Engine.
Module map and typed contracts before implementation.
"""

from dataclasses import dataclass, field
from typing import Protocol, Literal, Optional, List, Dict, Any
from pathlib import Path

AgentSource = Literal["pi", "agy"]

@dataclass(frozen=True)
class SessionEnvelope:
    """Normalized multi-source session payload extracted from raw log files."""
    source: AgentSource
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
    """Distilled compact representation for indexation and agent consumption."""
    source: AgentSource
    session_id: str
    workspace: str
    timestamp: str
    semantic_title: str
    user_goal: str
    decisions: List[str]
    files_touched: List[str]
    raw_path: str
    capsule_text: str

class SessionAdapter(Protocol):
    """Protocol for reading raw session logs across different agent runtimes."""
    def discover_sessions(self, base_path: Optional[str] = None) -> List[Path]:
        """Find all session files for this runtime."""
        raise NotImplementedError

    def parse_envelope(self, session_path: Path) -> Optional[SessionEnvelope]:
        """Parse raw log file into normalized SessionEnvelope, filtering out noise."""
        raise NotImplementedError

class PiSessionAdapter:
    """Adapter for ~/.pi/agent/sessions/--<workspace>--/*.jsonl."""
    def discover_sessions(self, base_path: Optional[str] = None) -> List[Path]:
        raise NotImplementedError

    def parse_envelope(self, session_path: Path) -> Optional[SessionEnvelope]:
        raise NotImplementedError

class AgySessionAdapter:
    """Adapter for ~/.gemini/antigravity-cli/brain/<uuid>/.system_generated/logs/transcript.jsonl."""
    def discover_sessions(self, base_path: Optional[str] = None) -> List[Path]:
        raise NotImplementedError

    def parse_envelope(self, session_path: Path) -> Optional[SessionEnvelope]:
        raise NotImplementedError

class Distiller:
    """Heuristic & model distillation engine to produce titles and capsules."""
    def distill(self, envelope: SessionEnvelope) -> SessionCapsule:
        """Derive clean semantic title, extract core decisions, and build 200-token capsule."""
        raise NotImplementedError

    def derive_semantic_title(self, workspace: str, prompts: List[str], files: List[str]) -> str:
        """Generate human-readable title without tool/hook noise."""
        raise NotImplementedError

class CatalogStore:
    """SQLite FTS5 repository and Markdown exporter in second-brain."""
    def __init__(self, db_path: Path, capsules_dir: Path):
        self.db_path = db_path
        self.capsules_dir = capsules_dir

    def init_schema(self) -> None:
        """Create tables: sessions and sessions_fts."""
        raise NotImplementedError

    def get_existing_hash(self, session_id: str) -> Optional[str]:
        """Check if session is already indexed and unchanged."""
        raise NotImplementedError

    def save_capsule(self, capsule: SessionCapsule, file_hash: str) -> None:
        """Save capsule markdown file and index into SQLite FTS5."""
        raise NotImplementedError

    def search(self, query: str, workspace: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform full-text search against session capsules."""
        raise NotImplementedError

    def list_sessions(self, workspace: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List sessions ordered by timestamp descending."""
        raise NotImplementedError

    def sync_markdown_index(self, output_path: Path) -> None:
        """Generate clean markdown table of all indexed sessions."""
        raise NotImplementedError

class SessionCLI:
    """CLI handler wired into `brain session <subcommand>`."""
    def handle_ingest(self, source: str = "pi", force: bool = False) -> None:
        raise NotImplementedError

    def handle_list(self, workspace: Optional[str] = None, limit: int = 50) -> None:
        raise NotImplementedError

    def handle_search(self, query: str, workspace: Optional[str] = None) -> None:
        raise NotImplementedError

    def handle_info(self, session_id: str) -> None:
        raise NotImplementedError

    def handle_promote(self, session_id: str, title: Optional[str] = None) -> None:
        """Promote a session's decisions into a draft entry in entries/."""
        raise NotImplementedError
