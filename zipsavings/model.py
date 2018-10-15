from collections import namedtuple
from humanize import naturalsize


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

def percent(real, packed):
    if real == 0: return 0
    saved = real - packed
    return round(100 * saved / real, 2)

def sum_archive_infos(archive_infos):
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
    return ArchiveInfo('TOTAL', total_unpacked, total_packed, total_saved, total_saved_percent, total_file_count)
