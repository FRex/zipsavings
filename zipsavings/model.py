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
