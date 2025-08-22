import pathlib
from subprocess import run, PIPE

def test_context_sync_updates(tmp_path: pathlib.Path):
    repo = tmp_path
    run(['git','init','.'], cwd=repo, check=True)
    (repo/'context').mkdir(parents=True, exist_ok=True)
    dev = repo/'context'/'development.md'
    dev.write_text('# Development Log\n\n**Phase:** X\n**Primary Goal:** Y\n\n## Context Sync (AUTO-UPDATED)\n\n- **Overall goal is:**\n- **Last action was:**\n- **Next action will be:**\n- **Blockers:**\n')
    run(['git','add','-A'], cwd=repo, check=True)
    run(['git','commit','-m','init'], cwd=repo, check=True)
    r = run(['bpsai-pair','context-sync','--last','A','--next','B','--blockers','C'], cwd=repo, stdout=PIPE, stderr=PIPE, text=True)
    assert r.returncode == 0, r.stderr
    t = dev.read_text()
    assert "Last action was: A" in t
    assert "Next action will be: B" in t
    assert "Blockers: C" in t
