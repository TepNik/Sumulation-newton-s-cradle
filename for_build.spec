# -*- mode: python -*-

block_cipher = None


a = Analysis(['proga.py'],
             pathex=['D:\\Physics\\2semestr'],
             binaries=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
a.datas += [('newtons-cradle.ico', 'D:/Physics/2semestr/newtons-cradle.ico', 'DATA')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='proga',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='D:/Physics/2semestr/newtons-cradle.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='proga')
