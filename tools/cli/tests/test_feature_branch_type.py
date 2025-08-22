import pathlib
from subprocess import run, PIPE

def test_feature_branch_types(tmp_path: pathlib.Path):
    repo = tmp_path
    run(['git','init','.'], cwd=repo, check=True)
    (repo/'context').mkdir(parents=True, exist_ok=True)
    (repo/'scripts').mkdir(parents=True, exist_ok=True)
    # minimal script to simulate branch creation; we don't actually change git here
    (repo/'scripts'/'new_feature.sh').write_text('#!/usr/bin/env bash\necho \"OK\"\n')
    run(['chmod','+x', str(repo/'scripts'/'new_feature.sh')], check=True)

    r = run(['bpsai-pair','feature','login','--type','refactor','--primary','x','--phase','y'],
            cwd=repo, stdout=PIPE, stderr=PIPE, text=True)
    assert r.returncode == 0, r.stderr