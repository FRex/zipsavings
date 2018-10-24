import os.path
from subprocess import Popen, PIPE
from . import model


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

def is_directory_output_lines(lines):
    i = lines.index('Scanning the drive for archives:')
    return ' folder,' in lines[i + 1] or ' folders,' in lines[i + 1]

def good_output_line(line):
    return line and not line.startswith('Warnings:')

def raise_on_trunc_archive(lines, fname):
    if 'ERRORS:' in lines and 'Unexpected end of archive' in lines:
        raise RuntimeError(f'ERROR: {fname} : Unexpected end of archive.')

def parse_7z_result(output, fname):
    lines = list(filter(good_output_line, output.split('\n')))
    raise_on_trunc_archive(lines, fname)
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
    saved_percent = model.percent(unpacked, packed)
    return model.ArchiveInfo(fname, unpacked, packed, saved, saved_percent, file_count, archive_type, size)

def adjust_error_string(stderr):
    lines = list(filter(None, stderr.split('\n')))
    if len(lines) == 4 and lines[0] == 'ERROR: The system cannot find the file specified.':
        return f"ERROR: {lines[1]} : The system cannot find the file specified.".replace('\\', '/')
    ret = ' '.join(stderr.split())
    if ret.endswith(': Can not open the file as archive'): ret += '.'
    return ret.replace('\\', '/')

class ErrorJob:
    def __init__(self, message):
        self.message = message

    def join(self):
        raise RuntimeError(self.message)

class SevenJob:
    def __init__(self, args):
        self.args = args
        self.job = Popen(args, errors='replace', stdout=PIPE, stderr=PIPE, universal_newlines=True)

    def join(self):
        stdout, stderr = self.job.communicate()
        fname = self.args[-1]
        #check dir first to prevent printing stderr about bad files found in a dir
        #despite check in start7z this is here just in case
        if is_directory_output_lines(stdout.split('\n')): raise RuntimeError(f"ERROR: {fname} : A directory.")
        if len(stderr) > 0: raise RuntimeError(adjust_error_string(stderr))
        return parse_7z_result(stdout, fname)

def make_job(fname, exe7z):
    if os.path.isdir(fname): return ErrorJob(f"ERROR: {fname} : A directory.")
    return SevenJob([exe7z, 'l', '--', fname])
