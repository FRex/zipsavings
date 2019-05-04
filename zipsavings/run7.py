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

def raise_on_headers_error(lines, fname):
    if 'ERRORS:' in lines and 'Headers Error' in lines and 'Unconfirmed start of archive' in lines:
        raise RuntimeError(f'ERROR: {fname} : Headers error, unconfirmed start of archive.')

    if 'ERRORS:' in lines and 'Headers Error' in lines:
        raise RuntimeError(f'ERROR: {fname} : Headers error.')

def raise_on_generic_error(lines, fname):
    if 'ERRORS:' in lines:
        raise RuntimeError(f'ERROR: {fname} : Other unexpected error.')

BIG_DASH_LINE = '------------------- ----- ------------ ------------  ------------------------'
def find_last_dash_line_index(lines):
    for i in range(len(lines) - 1, -1, -1):
        if lines[i] == BIG_DASH_LINE:
            return i

def get_ints_from_line(line):
    ret = []
    for x in line.split():
        try: ret.append(int(x))
        except ValueError: pass
    return ret

def parse_7z_result(output, fname):
    lines = list(filter(good_output_line, output.split('\n')))
    raise_on_trunc_archive(lines, fname)
    raise_on_headers_error(lines, fname)
    raise_on_generic_error(lines, fname)
    archive_type = get_type_from_output_lines(lines)
    size = get_size_from_output_lines(lines)
    dash_line_index = find_last_dash_line_index(lines)
    info_line = lines[dash_line_index + 1]
    info_line = info_line.replace(' folders', '@@@') #just to be safe in case we run on 'x files, y folders' line
    parts = get_ints_from_line(info_line)
    if len(parts) < 3: raise RuntimeError(f"ERROR: {fname} : No size data in {archive_type} format.")
    if len(parts) > 3: raise RuntimeError(f"ERROR: {fname} : Too many ints parsed in line: {info_line}")
    unpacked = parts[0]
    file_count = parts[2]
    saved = unpacked - size
    saved_percent = model.percent(unpacked, size)
    return model.ArchiveInfo(fname, size, unpacked, saved, saved_percent, file_count, archive_type)

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


PASSWORD_PROMPT_LIST = list('Enter password (will not be echoed):')
def throw_on_password_prompt(job, fname):
    ret = []
    dashes = list('\n--\n')
    while True:
        x = job.stdout.read(1)
        if len(x) == 0: break
        ret.append(x)
        if ret[-len(PASSWORD_PROMPT_LIST):] == PASSWORD_PROMPT_LIST: raise RuntimeError(f"ERROR: {fname} : Encrypted filenames.")
        if ret[-len(dashes):] == dashes: break
    #fix for Linux where doing jstdout.read causes j.communicate to later return no stdout at all
    ret.append(job.stdout.read())
    return ''.join(ret)


class SevenJob:
    def __init__(self, args):
        self.args = args
        self.job = Popen(args, errors='replace', stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    def join(self):
        fname = self.args[-1]
        startout = throw_on_password_prompt(self.job, fname)
        stdout, stderr = self.job.communicate()
        stdout = startout + stdout
        #check dir first to prevent printing stderr about bad files found in a dir
        #despite check in start7z this is here just in case
        if is_directory_output_lines(stdout.split('\n')): raise RuntimeError(f"ERROR: {fname} : A directory.")
        if len(stderr) > 0: raise RuntimeError(adjust_error_string(stderr))
        return parse_7z_result(stdout, fname)


class CsoInfoJob:
    def __init__(self, args):
        self.job = Popen(args, errors='replace', stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    def join(self):
        stdout = self.job.communicate()[0].strip()
        fname, info = stdout.rsplit(':', 1)
        if '/' not in info or not info.endswith(' byte blocks'): raise RuntimeError("ERROR: " + stdout + '.')
        ftype, sizes = info.split(',')[0:2]
        ftype = ftype.strip()
        sizes = sizes.strip().split('/')
        size = int(sizes[0])
        unpacked = int(sizes[1])
        saved = unpacked - size
        saved_percent = model.percent(unpacked, size)
        return model.ArchiveInfo(fname, size, unpacked, saved, saved_percent, 1, ftype)


def make_job(fname, exes):
    if os.path.isdir(fname): return ErrorJob(f"ERROR: {fname} : A directory.")
    if not os.path.isfile(fname): return ErrorJob(f"ERROR: {fname} : File doesn't exist.")

    if (fname.endswith('.cso') or fname.endswith('.zso')) and 'csoinfo' in exes:
        try:
            return CsoInfoJob([exes['csoinfo'], fname])
        except OSError as e:
            return ErrorJob(f"ERROR: {fname} : Popen('{exes['csoinfo']}') OSError - {str(e)}.")

    return SevenJob([exes['7z'], 'l', '--', fname])
