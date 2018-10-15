import os
import sys
from subprocess import Popen, PIPE
from getopt import gnu_getopt
from collections import namedtuple
from . import model


if __name__ != '__main__': raise RuntimeError("This is a script, not a module.")

opts, files = gnu_getopt(sys.argv[1:], 'ts:r', ['total', 'sort=', 'reverse', '7zexe=', 'stdin-filelist'])

total = False
sort_by_field = None
reverse_sort = False
new_7z_exe = None
read_stdin_filelist = False

for o, v in opts:
    if o in ['--total', '-t']: total = True
    if o in ['--sort', '-s']: sort_by_field = v
    if o in ['--reverse', '-r']: reverse_sort = True
    if o in ['--7zexe']: new_7z_exe = v
    if o in ['--stdin-filelist']: read_stdin_filelist = True

if sort_by_field is not None and sort_by_field not in model.ArchiveInfo._fields:
    print(f"'{sort_by_field}' is not a valid field name to sort by", file=sys.stderr)
    print("Try: " + ', '.join(model.ArchiveInfo._fields), file=sys.stderr)
    sys.exit(1)

archive_infos = []

def percent(real, packed):
    if real == 0: return 0
    saved = real - packed
    return round(100 * saved / real, 2)

final_7z_exe = next(filter(None, [new_7z_exe, os.getenv('ZIPSAVINGS_7ZEXE'), 'C:/mybin/7z.exe']))


all_files = files
if read_stdin_filelist:
    all_files = files + [l for l in sys.stdin.read().split('\n') if l]

def split_into_portions(data, most):
    return [data[i:i+most] for i in range(0, len(data), most)]

def start_7z_job(fname):
    args = [final_7z_exe, 'l', '--', fname]
    return Popen(args, errors='replace', stdout=PIPE, stderr=PIPE, universal_newlines=True)

def parse_7z_result(output):
    lines = [l for l in output.split('\n') if l and not l.startswith('Warnings:')]
    info_line = lines[-1]
    dash_line = lines[-2]
    spaces = [i for i in range(len(dash_line)) if dash_line[i] == ' ']
    runs = zip([-1] + spaces, spaces + [len(dash_line)])
    parts = [info_line[1+run[0]:run[1]] for run in runs]
    parts = filter(None, parts)
    parts = list(map(str.strip, parts))
    if parts[2] == '': raise RuntimeError(f"{f}: no uncompressed size info")
    unpacked = int(parts[2])
    packed = int(parts[3])
    file_count = int(parts[4].split(' ')[0])
    saved = unpacked - packed
    saved_percent = percent(unpacked, packed)
    return model.ArchiveInfo(f, unpacked, packed, saved, saved_percent, file_count)

for file_group in split_into_portions(all_files, 8):
    jobs = [(start_7z_job(f), f) for f in file_group]
    for p, f in jobs:
        output, y = p.communicate()
        if len(y) > 0:
            print(y, file=sys.stderr)
        else:
            try:
                archive_infos.append(parse_7z_result(output))
            except RuntimeError as e:
                print(e)

if sort_by_field: archive_infos.sort(key=lambda x: getattr(x, sort_by_field), reverse=reverse_sort)

if total: archive_infos.append(model.sum_archive_infos(archive_infos))

for info in archive_infos:
    x = zip(info, [f.display_name for f in model.fields], [f.pretty_print for f in model.fields])
    y = ['{}: {}'.format(xx[1], xx[2](xx[0])) for xx in x] + ['']
    print('\n'.join(y))
