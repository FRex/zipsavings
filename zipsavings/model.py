from collections import namedtuple


ArchiveInfo = namedtuple('ArchiveInfo', 'archive, size, unpacked, saved, saved_percent, file_count, type')

def percent(real, packed):
    if real == 0: return 0
    saved = real - packed
    return 100 * saved / real

def create_solid_info(archive, size, unpacked, type):
    saved = unpacked - size
    saved_percent = percent(unpacked, size)
    return ArchiveInfo(archive, size, unpacked, saved, saved_percent, 1, type)

def sum_archive_infos(archive_infos):
    total_unpacked = 0
    total_saved = 0
    total_file_count = 0
    total_size = 0
    for info in archive_infos:
        total_unpacked += info.unpacked
        total_saved += info.saved
        total_file_count += info.file_count
        total_size += info.size

    total_saved_percent = percent(total_unpacked, total_size)
    totalname = f"TOTAL({len(archive_infos)})"
    return ArchiveInfo(totalname, total_size, total_unpacked, total_saved, total_saved_percent, total_file_count, 'SUM')

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
    return f"{sign}{round(n + rest / divisor, 2)} {UNIT[i]}"

def pretty_print_info_fields(info):
    archive = info.archive
    unpacked = binary_size(info.unpacked)
    saved = binary_size(info.saved)
    saved_percent = str(round(info.saved_percent, 2)) + '%'
    file_count = info.file_count
    atype = info.type
    size = binary_size(info.size)
    return ArchiveInfo(archive, size, unpacked, saved, saved_percent, file_count, atype)
