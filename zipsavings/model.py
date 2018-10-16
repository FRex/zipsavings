from collections import namedtuple


ArchiveInfo = namedtuple('ArchiveInfo', 'archive, unpacked, packed, saved, saved_percent, file_count, type')

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
    return ArchiveInfo('TOTAL', total_unpacked, total_packed, total_saved, total_saved_percent, total_file_count, 'SUM')

def binary_size(x):
    if x == 1: return "1 Byte"
    if x == -1: return "-1 Byte"
    if abs(x) < 1024: return f"{x} Bytes"
    UNIT = (None, 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB')
    i = 0
    n = abs(x)
    while n >= 1024:
        n //= 1024
        i += 1
    sign = '-' if x < 0 else ''
    divisor = 1024 ** i
    rest = abs(x) - n * divisor
    return f"{sign}{round(n + rest / divisor, 1)} {UNIT[i]}"

def pretty_print_info_fields(info):
    archive = info.archive
    unpacked = binary_size(info.unpacked)
    packed = binary_size(info.packed)
    saved = binary_size(info.saved)
    saved_percent = str(info.saved_percent) + '%'
    file_count = info.file_count
    atype = info.type
    return ArchiveInfo(archive, unpacked, packed, saved, saved_percent, file_count, atype)
