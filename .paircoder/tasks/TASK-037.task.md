# TASK-037: Implement Prompt Caching for Context Management

## Metadata
- **ID**: TASK-037
- **Plan**: paircoder-v2.2-features
- **Sprint**: sprint-9
- **Priority**: P0
- **Complexity**: 50
- **Status**: done
- **Created**: 2025-12-15
- **Tags**: feature, performance, caching
- **changelog_entry**: Added prompt caching for efficient context management

## Description

Implement prompt caching to reduce token usage when context is repeated across invocations. Static context (project.md, workflow.md, capabilities.yaml) rarely changes and should be cached rather than re-tokenized on every call.

## Objectives

1. Cache static context files with content-hash keys
2. Invalidate cache on file modification (mtime check)
3. Track cache hits/misses in metrics
4. Support configurable cache TTL
5. Integrate with headless mode and pack command

## Technical Requirements

### Cache Strategy

```
┌─────────────────────────────────────────────────────────┐
│                    Context Loading                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Check file mtime against cached mtime                │
│  2. If unchanged → return cached content                 │
│  3. If changed → load, hash, cache, return               │
│                                                          │
│  Cache Key: sha256(file_path + content)[:16]            │
│  Cache Location: .paircoder/cache/                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Files to Cache (Static Context)

| File | Change Frequency | Cache Priority |
|------|------------------|----------------|
| `.paircoder/context/project.md` | Rarely | High |
| `.paircoder/context/workflow.md` | Rarely | High |
| `.paircoder/capabilities.yaml` | Rarely | High |
| `.paircoder/config.yaml` | Occasionally | Medium |
| `AGENTS.md` | Rarely | High |
| `CLAUDE.md` | Rarely | High |

### Files NOT to Cache (Dynamic)

| File | Reason |
|------|--------|
| `.paircoder/context/state.md` | Changes frequently |
| Task files | Status changes |
| Plan files | Status changes |
| Metrics files | Appended constantly |

### Cache Implementation

```python
# tools/cli/bpsai_pair/context/__init__.py

from pathlib import Path
from hashlib import sha256
import json
from datetime import datetime, timedelta
from typing import Optional, Tuple

class ContextCache:
    """Cache for static context files."""
    
    def __init__(self, cache_dir: Path, ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.index_file = cache_dir / "index.json"
        self._index = self._load_index()
    
    def _load_index(self) -> dict:
        """Load cache index from disk."""
        if self.index_file.exists():
            return json.loads(self.index_file.read_text())
        return {}
    
    def _save_index(self) -> None:
        """Save cache index to disk."""
        self.index_file.write_text(json.dumps(self._index, indent=2))
    
    def _cache_key(self, file_path: Path) -> str:
        """Generate cache key from file path."""
        return sha256(str(file_path).encode()).hexdigest()[:16]
    
    def get(self, file_path: Path) -> Optional[Tuple[str, dict]]:
        """Get cached content if valid.
        
        Returns:
            Tuple of (content, metadata) or None if cache miss
        """
        key = self._cache_key(file_path)
        
        if key not in self._index:
            return None
        
        entry = self._index[key]
        
        # Check file mtime
        if file_path.exists():
            current_mtime = file_path.stat().st_mtime
            if current_mtime > entry["mtime"]:
                return None  # File changed
        
        # Check TTL
        cached_at = datetime.fromisoformat(entry["cached_at"])
        if datetime.now() - cached_at > self.ttl:
            return None  # Expired
        
        # Read cached content
        cache_file = self.cache_dir / f"{key}.txt"
        if not cache_file.exists():
            return None
        
        return cache_file.read_text(), entry
    
    def set(self, file_path: Path, content: str) -> dict:
        """Cache content for file.
        
        Returns:
            Cache entry metadata
        """
        key = self._cache_key(file_path)
        
        # Write content
        cache_file = self.cache_dir / f"{key}.txt"
        cache_file.write_text(content)
        
        # Update index
        entry = {
            "path": str(file_path),
            "mtime": file_path.stat().st_mtime if file_path.exists() else 0,
            "cached_at": datetime.now().isoformat(),
            "size_bytes": len(content),
            "content_hash": sha256(content.encode()).hexdigest()[:16],
        }
        self._index[key] = entry
        self._save_index()
        
        return entry
    
    def invalidate(self, file_path: Path) -> bool:
        """Invalidate cache for file."""
        key = self._cache_key(file_path)
        if key in self._index:
            del self._index[key]
            cache_file = self.cache_dir / f"{key}.txt"
            cache_file.unlink(missing_ok=True)
            self._save_index()
            return True
        return False
    
    def clear(self) -> int:
        """Clear entire cache. Returns count of cleared entries."""
        count = len(self._index)
        for key in list(self._index.keys()):
            cache_file = self.cache_dir / f"{key}.txt"
            cache_file.unlink(missing_ok=True)
        self._index = {}
        self._save_index()
        return count
    
    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            "entries": len(self._index),
            "total_bytes": sum(e.get("size_bytes", 0) for e in self._index.values()),
            "oldest": min((e["cached_at"] for e in self._index.values()), default=None),
            "newest": max((e["cached_at"] for e in self._index.values()), default=None),
        }
```

### Context Loader with Caching

```python
# tools/cli/bpsai_pair/context/loader.py

from pathlib import Path
from typing import Dict, Optional
from .cache import ContextCache

class ContextLoader:
    """Load context files with caching."""
    
    # Files eligible for caching (static)
    CACHEABLE = {
        ".paircoder/context/project.md",
        ".paircoder/context/workflow.md",
        ".paircoder/capabilities.yaml",
        ".paircoder/config.yaml",
        "AGENTS.md",
        "CLAUDE.md",
    }
    
    # Files that should NOT be cached (dynamic)
    NON_CACHEABLE = {
        ".paircoder/context/state.md",
        ".paircoder/history/metrics.jsonl",
    }
    
    def __init__(self, project_root: Path, cache: Optional[ContextCache] = None):
        self.project_root = project_root
        self.cache = cache or ContextCache(project_root / ".paircoder" / "cache")
        self.hits = 0
        self.misses = 0
    
    def load(self, relative_path: str) -> str:
        """Load file content, using cache if eligible."""
        file_path = self.project_root / relative_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"Context file not found: {relative_path}")
        
        # Check if cacheable
        if relative_path not in self.CACHEABLE:
            return file_path.read_text()
        
        # Try cache
        cached = self.cache.get(file_path)
        if cached:
            self.hits += 1
            return cached[0]
        
        # Cache miss - load and cache
        self.misses += 1
        content = file_path.read_text()
        self.cache.set(file_path, content)
        return content
    
    def load_all_context(self) -> Dict[str, str]:
        """Load all standard context files."""
        context = {}
        for path in self.CACHEABLE:
            full_path = self.project_root / path
            if full_path.exists():
                context[path] = self.load(path)
        return context
    
    def get_stats(self) -> dict:
        """Get loader statistics."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0,
            "cache": self.cache.stats(),
        }
```

### Configuration

```yaml
# .paircoder/config.yaml
cache:
  enabled: true
  ttl_hours: 24
  directory: .paircoder/cache
  
  # Files to cache (override defaults)
  cacheable:
    - .paircoder/context/project.md
    - .paircoder/context/workflow.md
    - .paircoder/capabilities.yaml
    
  # Files to never cache
  non_cacheable:
    - .paircoder/context/state.md
    - "*.jsonl"
```

### CLI Commands

```bash
# View cache stats
bpsai-pair cache stats

# Clear cache
bpsai-pair cache clear

# Invalidate specific file
bpsai-pair cache invalidate .paircoder/context/project.md
```

### Integration Points

1. **pack command** - Use cached context when packing
2. **headless mode** - Leverage cache for repeated context
3. **metrics** - Track cache hit rate as metric

```python
# In orchestration/headless.py
def invoke(self, prompt: str, context_loader: ContextLoader = None):
    if context_loader:
        # Pre-load context using cache
        context = context_loader.load_all_context()
        # Structure prompt with cached prefix
        full_prompt = self._build_prompt(context, prompt)
```

### Metrics Integration

```python
# Track cache metrics
from bpsai_pair.metrics.collector import MetricsCollector

def record_cache_stats(collector: MetricsCollector, loader: ContextLoader):
    stats = loader.get_stats()
    collector.record_event({
        "type": "cache_stats",
        "hits": stats["hits"],
        "misses": stats["misses"],
        "hit_rate": stats["hit_rate"],
    })
```

## Claude API Considerations

For Claude API prompt caching (if using API directly):

1. **System prompt caching** - Put static context in system prompt
2. **Cache control headers** - Use `anthropic-beta: prompt-caching-2024-07-31`
3. **Structure prompts** - Static prefix + dynamic suffix

```python
# Example with Claude API caching
headers = {
    "anthropic-beta": "prompt-caching-2024-07-31"
}

# Mark static content for caching
system_prompt = [
    {
        "type": "text",
        "text": cached_context,
        "cache_control": {"type": "ephemeral"}
    }
]
```

## Acceptance Criteria

- [ ] ContextCache class implemented with mtime validation
- [ ] ContextLoader uses cache for eligible files
- [ ] Cache index persisted to disk
- [ ] `bpsai-pair cache stats` command works
- [ ] `bpsai-pair cache clear` command works
- [ ] Cache hit rate tracked in metrics
- [ ] pack command uses cached context
- [ ] Configurable via config.yaml
- [ ] Unit tests for cache logic
- [ ] Integration test for full flow

## Dependencies

- Existing metrics system (TASK-030)
- Config loading system

## Files to Create/Modify

**Create:**
- `tools/cli/bpsai_pair/context/__init__.py`
- `tools/cli/bpsai_pair/context/cache.py`
- `tools/cli/bpsai_pair/context/loader.py`
- `tools/cli/bpsai_pair/commands/cache.py`
- `tools/cli/tests/test_cache.py`

**Modify:**
- `tools/cli/bpsai_pair/cli.py` (add cache commands)
- `tools/cli/bpsai_pair/ops.py` (use loader in pack)
- `tools/cli/bpsai_pair/orchestration/headless.py` (use loader)
- `.paircoder/config.yaml` (add cache section)

## Notes

- Cache is local to each project (not shared)
- .paircoder/cache/ should be in .gitignore
- Consider adding cache warming on project init
- Future: Could extend to cache API responses (with care)
