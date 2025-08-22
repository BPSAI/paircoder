import pathlib
from subprocess import run, PIPE

def test_pack_preview_and_list(tmp_path: pathlib.Path):
    repo = tmp_path
    run(['git','init','.'], cwd=repo, check=True)
    (repo/'context').mkdir(parents=True, exist_ok=True)
    (repo/'context'/'development.md').write_text('# Development Log\n\n## Context Sync (AUTO-UPDATED)\n')
    (repo/'.agentpackignore').write_text('.git/\n.venv/\n')
    (repo/'scripts').mkdir(parents=True, exist_ok=True)
    (repo/'scripts'/'agent_pack.sh').write_text('#!/usr/bin/env bash\necho \"Created agent_pack.tgz\"\n')
    run(['chmod','+x', str(repo/'scripts'/'agent_pack.sh')], check=True)

    r = run(['bpsai-pair','pack','--dry-run'], cwd=repo, stdout=PIPE, stderr=PIPE, text=True)
    assert r.returncode == 0, r.stderr

    r = run(['bpsai-pair','pack','--list'], cwd=repo, stdout=PIPE, stderr=PIPE, text=True)
    assert r.returncode == 0, r.stderr

    r = run(['bpsai-pair','pack','--json'], cwd=repo, stdout=PIPE, stderr=PIPE, text=True)
    assert r.returncode == 0, r.stderr
    assert 'archive' in r.stdout