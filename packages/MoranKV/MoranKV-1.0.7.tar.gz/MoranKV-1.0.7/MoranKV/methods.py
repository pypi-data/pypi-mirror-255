import threading, os, time, base64, json, sys


def icons(search_value: str = ''):
    from kivymd.icon_definitions import md_icons
    print([icon for icon in list(md_icons.keys()) if search_value in icon])

def get_spec(name: str, icon: str = 'icon.ico', filename: str = 'main.py', path: str = os.getcwd()):
    path = path.replace("\\", r"\\")

    with open(filename.replace('.py', '.spec'), 'w') as f:
        f.write(fr"""from kivy_deps import sdl2, glew

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['{filename}'],
             pathex=['{path}'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={{}},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='{name}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None, icon='{icon}')

coll = COLLECT(exe, Tree('{path}'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='{name}')""")

def thread(func):
    def inner(*args, **kwargs):
        threading.Thread(target=lambda: func(*args, **kwargs), daemon=True).start()

    return inner

def measure_time(func):
    def inner(*args, **kwargs):
        tic = time.perf_counter()
        func(*args, **kwargs)
        toc = time.perf_counter()

        print(f'Duration of {func.__name__}: {round(toc - tic, 8)}')

    return inner

def get_base64(file_path: str):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def get_file(file_path, default=None, is_json=False, encoding='utf-8'):
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            value = f.read()

        if is_json:
            return json.loads(value)
        return value

    except FileNotFoundError:
        return default

def set_file(file_path, value, is_json=False, encoding='utf-8'):
    if is_json:
        value = json.dumps(value, indent=2, ensure_ascii=False)

    with open(file_path, 'w', encoding=encoding) as f:
        f.write(value)

@thread
def file_dialog(callback: callable):
    from tkinter import Tk, filedialog

    if sys.platform == "darwin":
        fd = os.popen("""osascript -e 'tell application (path to frontmost application as text)
set myFile to choose file
POSIX path of myFile
end'""")
        file_path = fd.read()
        fd.close()
        file_path = file_path[:-1]
    else:
        tk = Tk()
        tk.withdraw()
        file_path = filedialog.askopenfilename()

    if file_path:
        callback(file_path)

