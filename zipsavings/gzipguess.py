import model


def find_size(unpacked, unpacked_sizes):
    for s in unpacked_sizes:
        if s != unpacked and s % (2 ** 32) == unpacked:
            return s
    return unpacked


def adjust_gzip_info(info, unpacked_sizes):
    if info.type != 'gzip':
        return info

    fname = info.archive
    size = info.size
    unpacked = find_size(info.unpacked, unpacked_sizes)
    saved = unpacked - size
    saved_percent = model.percent(unpacked, size)
    file_count = info.file_count
    return model.ArchiveInfo(fname, size, unpacked, saved, saved_percent, file_count, 'gzip')


def guess_gzip_infos(infos):
    unpacked_sizes = [x.unpacked for x in infos]
    return [adjust_gzip_info(i, unpacked_sizes) for i in infos]

