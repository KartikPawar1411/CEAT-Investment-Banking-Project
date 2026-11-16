"""Build in isolation and promote only an entirely verified set of artifacts."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
MODEL='CEAT_Financial_Valuation_Model.xlsx'
def build():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish-only',action='store_true')
    parser.add_argument('--render',action='store_true')
    args=parser.parse_args()
    shell=shutil.which('pwsh') or shutil.which('powershell')
    if not shell:raise RuntimeError('PowerShell and Windows desktop Office are required.')
    with tempfile.TemporaryDirectory(prefix='.ceat-build-',dir=ROOT) as tmp:
        stage=Path(tmp)
        for folder in ['src','data']:
            shutil.copytree(ROOT/folder,stage/folder,ignore=shutil.ignore_patterns('__pycache__'))
        for folder in ['output','reports','charts','.qa']:(stage/folder).mkdir()
        env={**os.environ,'PYTHONUTF8':'1'}
        for key in ['CEAT_CHECK_MODEL','CEAT_CHECK_OUTPUT']:env.pop(key,None)
        def run(script):
            path=str(stage/'src'/script)
            cmd=[shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',path] if script.endswith('.ps1') else [sys.executable,path]
            subprocess.run(cmd,cwd=stage,env=env,check=True)
        run('validate_sources.py')
        if args.publish_only:
            for rel in ['output/'+MODEL,'.qa/threshold.xlsx','.qa/dashboard.pdf']:
                shutil.copy2(ROOT/rel,stage/rel)
        else:
            run('excel_generator.py');run('recalculate.ps1')
        run('verify_expansion.py')
        for script in ['chart_generator.py','powerpoint_generator.py','pdf_summary.py','research_report.py','data_validation.py','check_publication.py','verify_ncd.py','readme_publish.py']:run(script)
        run('render_slides.ps1')
        shutil.copy2(stage/'.qa/pitch_book.pdf',stage/'output/CEAT_Investment_Banking_Pitch_Book.pdf')
        from pypdf import PdfReader
        from openpyxl import load_workbook
        pages=PdfReader(stage/'.qa/pitch_book.pdf').pages
        if len(pages)!=19:raise ValueError('PowerPoint PDF page count')
        output_text=' '.join(page.extract_text() for page in pages[:3])
        cached=load_workbook(stage/'output'/MODEL,data_only=True,read_only=True)
        decision=cached['Funding Decision'];value=cached['Normalized DCF']['B36'].value
        figures=[decision['B10'].value,f"{decision['C4'].value:,.0f}",f"{decision['C8'].value:,.0f}",f'{value:,.0f}']
        if not all(figure in output_text for figure in figures):raise ValueError('Rendered decision pages disagree with the workbook')
        cached.close()
        if args.render:run('render_review.py')
        deliver=[Path('README.md'),Path('data/processed/input_register.csv'),Path('data/sources.csv')]
        for folder in ['output','reports','charts','.qa']:
            deliver.extend(p.relative_to(stage) for p in (stage/folder).iterdir() if p.is_file())
        backup=stage/'previous'
        replaced=[]
        try:
            for rel in deliver:
                live=ROOT/rel;live.parent.mkdir(parents=True,exist_ok=True)
                if live.exists():
                    (backup/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(live,backup/rel)
                os.replace(stage/rel,live);replaced.append(rel)
        except BaseException:
            for rel in reversed(replaced):
                if (backup/rel).exists():os.replace(backup/rel,ROOT/rel)
                else:(ROOT/rel).unlink()
            raise
        print('Validated model, pitch book, PDF, brief and report published.')

