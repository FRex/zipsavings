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

ArchiveInfo = namedtuple('ArchiveInfo', 'archive unpacked packed saved saved_percent file_count')

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


def binary_size(x):
    return '-' + naturalsize(-x, True) if x < 0 else naturalsize(x, True)

def pretty_print_info_fields(info):
    archive = info.archive
    unpacked = binary_size(info.unpacked)
    packed = binary_size(info.packed)
    saved = binary_size(info.saved)
    saved_percent = str(info.saved_percent) + '%'
    file_count = info.file_count
    return ArchiveInfo(archive, unpacked, packed, saved, saved_percent, file_count)
