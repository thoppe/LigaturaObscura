'''
Build TTX files out of source font files.
'''

import bs4
import sys, os, glob

load_dest = 'data/source'
F_WOFF = glob.glob(f'{load_dest}/*.woff')
F_TTF = glob.glob(f'{load_dest}/*.ttf')

save_dest = 'data/ttx'
os.system(f'mkdir -p {save_dest}')

for f in F_WOFF+F_TTF:
    f_save = os.path.join(save_dest, os.path.basename(f))
    f_save = '.'.join(f_save.split('.')[:-1]) + '.ttx'
    if os.path.exists(f_save):
        continue

    cmd = f'ttx -o {f_save} {f}'
    os.system(cmd)
    print(f_save)
