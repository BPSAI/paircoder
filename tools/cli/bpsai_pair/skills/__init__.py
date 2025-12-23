"""Skills module for validating and managing Claude Code skills."""

from .validator import SkillValidator, find_skills_dir
from .installer import (
    SkillInstallerError,
    SkillSource,
    install_skill,
    install_from_path,
    install_from_url,
    parse_source,
    parse_github_url,
    check_conflicts,
    get_target_dir,
    extract_skill_name,
)
from .exporter import (
    SkillExporterError,
    ExportFormat,
    export_skill,
    export_all_skills,
    check_portability,
)
from .suggestion import (
    SkillSuggestionError,
    HistoryParser,
    PatternDetector,
    SkillSuggester,
    SkillDraftCreator,
    suggest_skills,
)
from .gap_detector import (
    SkillGap,
    SkillGapDetector,
    GapPersistence,
    detect_gaps_from_history,
    format_gap_notification,
)

__all__ = [
    "SkillValidator",
    "find_skills_dir",
    "SkillInstallerError",
    "SkillSource",
    "install_skill",
    "install_from_path",
    "install_from_url",
    "parse_source",
    "parse_github_url",
    "check_conflicts",
    "get_target_dir",
    "extract_skill_name",
    "SkillExporterError",
    "ExportFormat",
    "export_skill",
    "export_all_skills",
    "check_portability",
    "SkillSuggestionError",
    "HistoryParser",
    "PatternDetector",
    "SkillSuggester",
    "SkillDraftCreator",
    "suggest_skills",
    "SkillGap",
    "SkillGapDetector",
    "GapPersistence",
    "detect_gaps_from_history",
    "format_gap_notification",
]
