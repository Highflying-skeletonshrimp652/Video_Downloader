# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project_root = Path(globals().get("SPECPATH", Path.cwd())).resolve()
datas = [('assets', 'assets')]
excluded_module_names = ['yt_dlp', 'cryptography', 'curl_cffi']
excluded_binary_names = {'opengl32sw.dll'}


def keep_toc_entry(entry) -> bool:
    candidate_names: list[str] = []
    if len(entry) > 0 and isinstance(entry[0], str):
        candidate_names.append(Path(entry[0]).name.lower())
    if len(entry) > 1 and isinstance(entry[1], str):
        candidate_names.append(Path(entry[1]).name.lower())
    for name in candidate_names:
        if name in excluded_binary_names:
            return False
    return True

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_module_names,
    noarchive=False,
    optimize=0,
)
a.binaries[:] = [entry for entry in a.binaries if keep_toc_entry(entry)]
a.datas[:] = [entry for entry in a.datas if keep_toc_entry(entry)]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VideoDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoDownloader',
)
