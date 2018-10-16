from subprocess import Popen, PIPE
from . import model

def percent(real, packed):
    if real == 0: return 0
    saved = real - packed
    return round(100 * saved / real, 2)

def start_7z(fname, exe7z):
    args = [exe7z, 'l', '--', fname]
    return Popen(args, errors='replace', stdout=PIPE, stderr=PIPE, universal_newlines=True)

def get_type_from_output_lines(lines):
    i = lines.index('--')
    for line in lines[i:]:
        if line.startswith('Type = '):
            return line[len('Type = '):]
    return '???'

def get_size_from_output_lines(lines):
    i = lines.index('Scanning the drive for archives:')
    x = lines[i + 1].split(',')[1].strip().split()[0]
    return int(x)

def parse_7z_result(output, fname):
    lines = [l for l in output.split('\n') if l and not l.startswith('Warnings:')]
    archive_type = get_type_from_output_lines(lines)
    size = get_size_from_output_lines(lines)
    info_line = lines[-1]
    dash_line = lines[-2]
    spaces = [i for i in range(len(dash_line)) if dash_line[i] == ' ']
    runs = zip([-1] + spaces, spaces + [len(dash_line)])
    parts = [info_line[1+run[0]:run[1]] for run in runs]
    parts = filter(None, parts)
    parts = list(map(str.strip, parts))
    if parts[2] == '': raise RuntimeError(f"ERROR: {fname} : No size data in {archive_type} format.")
    unpacked = int(parts[2])
    packed = int(parts[3])
    file_count = int(parts[4].split(' ')[0])
    saved = unpacked - packed
    saved_percent = percent(unpacked, packed)
    return model.ArchiveInfo(fname, unpacked, packed, saved, saved_percent, file_count, archive_type, size)

def adjust_error_string(stderr):
    lines = list(filter(None, stderr.split('\n')))
    if len(lines) == 4 and lines[0] == 'ERROR: The system cannot find the file specified.':
        return f"ERROR: {lines[1]} : The system cannot find the file specified.".replace('\\', '/')
    ret = ' '.join(stderr.split())
    if ret.endswith(': Can not open the file as archive'): ret += '.'
    return ret.replace('\\', '/')

def join_7z(job):
    stdout, stderr = job.communicate()
    if len(stderr) > 0: raise RuntimeError(adjust_error_string(stderr))
    return parse_7z_result(stdout, job.args[-1])
