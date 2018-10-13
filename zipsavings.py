import re
import sys
from subprocess import Popen, PIPE
from humanize import naturalsize
from getopt import gnu_getopt
from collections import namedtuple


if __name__ != '__main__': raise RuntimeError("This is a script, not a module.")

def chunkinize(s, n):
    s = s[::-1]
    ret = [s[i:i+n][::-1] for i in range(0, len(s), n)]
    return ' '.join(ret[::-1])

def size(x):
    nicebytes = chunkinize(str(abs(x)), 3)
    if x < 0:
        return f"-{naturalsize(-x, True)} (-{naturalsize(-x)}, -{nicebytes} bytes)"
    else:
        return f"{naturalsize(x, True)} ({naturalsize(x)}, {nicebytes} bytes)"

Field = namedtuple('Field', 'name display_name pretty_print')

fields = [
    Field('archive', 'Archive', lambda x: x),
    Field('unpacked', 'Unpacked', size),
    Field('packed', 'Packed', size),
    Field('saved', 'Saved', size),
    Field('saved_percent', 'Saved %', lambda x: str(x) + '%'),
    Field('file_count', 'File count', lambda x: x),
]

field_names = [f.name for f in fields]
ArchiveInfo = namedtuple('ArchiveInfo', field_names)

opts, files = gnu_getopt(sys.argv[1:], 'ts:r', ['total', 'sort=', 'reverse'])

total = False
sort_by_field = None
reverse_sort = False

for o, v in opts:
    if o in ['--total', '-t']: total = True
    if o in ['--sort', '-s']: sort_by_field = v
    if o in ['--reverse', '-r']: reverse_sort = True

if sort_by_field is not None and sort_by_field not in field_names:
    print(f"'{sort_by_field}' is not a valid field name to sort by", file=sys.stderr)
    print("Try: " + ', '.join(field_names), file=sys.stderr)
    sys.exit(1)

archive_infos = []

def percent(real, packed):
    if real == 0: return 0
    saved = real - packed
    return round(100 * saved / real, 2)


for f in files:
    args = ['C:/mybin/7z.exe', 'l', '--', f]
    p = Popen(args, errors='replace', stdout=PIPE, stderr=PIPE, universal_newlines=True)
    x, y = p.communicate()
    if len(y) > 0:
        print(y, file=sys.stderr)
    else:
        lines = [l for l in x.split('\n') if len(l) > 0 and not l.startswith('Warnings:')]
        info_line = lines[-1]
        dash_line = lines[-2]
        spaces = [i for i in range(len(dash_line)) if dash_line[i] == ' ']
        runs = zip([-1] + spaces, spaces + [len(dash_line)])
        parts = [info_line[1+run[0]:run[1]] for run in runs]
        parts = filter(None, parts)
        parts = list(map(str.strip, parts))
        if parts[2] == '':
            print(f"{f}: no uncompressed size info\n", file=sys.stderr)
            continue
        unpacked = int(parts[2])
        packed = int(parts[3])
        file_count = int(parts[4].split(' ')[0])
        saved = unpacked - packed
        saved_percent = percent(unpacked, packed)
        archive_infos.append(ArchiveInfo(f, unpacked, packed, saved, saved_percent, file_count))

if sort_by_field:
    sort_field_index = field_names.index(sort_by_field)
    archive_infos.sort(key=lambda x: x[sort_field_index], reverse=reverse_sort)

if total:
    total_unpacked = 0
    total_packed = 0
    total_saved = 0
    total_file_count = 0
    for info in archive_infos:
        total_unpacked += info.unpacked
        total_packed += info.packed
        total_saved += info.saved
        total_file_count += info.file_count

    total_saved_percent = percent(total_unpacked, total_packed)
    archive_infos.append(ArchiveInfo('TOTAL', total_unpacked, total_packed, total_saved, total_saved_percent, total_file_count))

for info in archive_infos:
    x = zip(info, [f.display_name for f in fields], [f.pretty_print for f in fields])
    y = ['{}: {}'.format(xx[1], xx[2](xx[0])) for xx in x] + ['']
    print('\n'.join(y))
