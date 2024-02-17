import os
from rinch_sql.__version__ import __version__

v_version = f"v{__version__}"

path_version = "rinch_sql/__version__.py"

output = os.popen("git status --porcelain").read()
target = f" M {path_version}\n"
if output != target:
    raise Exception(f"please push your commits. run 'git status --porcelain', {output=}, {target=}")

os.system(f"git add {path_version}")
os.system(f"git commit {v_version}")
os.system(f"git add {path_version}")
os.system(f"git push --tags")
