import sqlite3
from typing import List, Tuple

from config import HISTORY_DB_PATH
from services.schemas import CanonicalizationResult, DistortionReport


def init_history_db():
    with sqlite3.connect(HISTORY_DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                original_text TEXT NOT NULL,
                canonicalized_text TEXT NOT NULL,
                semantic_similarity REAL NOT NULL,
                token_overlap REAL NOT NULL,
                entity_preservation REAL NOT NULL,
                length_ratio REAL NOT NULL,
                overall_score REAL NOT NULL,
                distortion_level TEXT NOT NULL,
                explanation TEXT NOT NULL
            )
            """
        )


def save_analysis(
    original_text: str,
    canonicalization: CanonicalizationResult,
    report: DistortionReport,
):
    with sqlite3.connect(HISTORY_DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO analysis_history (
                original_text,
                canonicalized_text,
                semantic_similarity,
                token_overlap,
                entity_preservation,
                length_ratio,
                overall_score,
                distortion_level,
                explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                original_text,
                canonicalization.canonicalized_text,
                report.semantic_similarity,
                report.token_overlap,
                report.entity_preservation,
                report.length_ratio,
                report.overall_score,
                report.distortion_level,
                canonicalization.explanation,
            ),
        )


def load_recent_history(limit: int = 10) -> List[Tuple]:
    with sqlite3.connect(HISTORY_DB_PATH) as connection:
        cursor = connection.execute(
            """
            SELECT
                created_at,
                original_text,
                canonicalized_text,
                overall_score,
                distortion_level
            FROM analysis_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()
