"""Package the published project and evidence archive; verify the zip before replacing it."""
import os
from pathlib import Path
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

def package():
    root=Path(__file__).resolve().parents[1]
    target=root.parent/(root.name+'.zip')
    members=[root/n for n in ['README.md','build.py','requirements.txt']]
    for name in ['src','data','output','reports','charts']:
        members.extend(p for p in (root/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    members.extend(root/'.qa'/n for n in ['threshold.xlsx','dashboard.pdf','slides-01.jpg','slides-07.jpg','slides-13.jpg','summary-01.png','dashboard-01.png'])
    with tempfile.NamedTemporaryFile(dir=target.parent,suffix='.zip',delete=False) as stream:temp=Path(stream.name)
    try:
        with ZipFile(temp,'w',compression=ZIP_DEFLATED,compresslevel=6) as archive:
            for path in sorted(members):archive.write(path,(Path(root.name)/path.relative_to(root)).as_posix())
        with ZipFile(temp) as archive:
            if archive.testzip() is not None or len(archive.namelist())!=len(members):raise ValueError('ZIP verification failed')
        os.replace(temp,target)
    finally:
        temp.unlink(missing_ok=True)
    print(f'{len(members)} verified files in {target.name}')
if __name__=='__main__':package()

