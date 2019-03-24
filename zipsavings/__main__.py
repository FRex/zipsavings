import os
import sys
import argparse
from time import time
from getopt import gnu_getopt
from . import model, run7, table


if __name__ != '__main__': raise RuntimeError("This is a script, not a module.")

par = argparse.ArgumentParser('zipsavings')
par.add_argument('-t', '--total', action='store_true', help='sum the files')
par.add_argument('-s', '--sort', action='store', help='sort by given field', choices=model.ArchiveInfo._fields)
par.add_argument('-r', '--reverse', action='store_true', help='reverse the sort')
par.add_argument('--exe-7z', action='store', help='specify 7z executable to use')
par.add_argument('--exe-csoinfo', action='store', help='specify csoinfo executable to use')
par.add_argument('--stdin-filelist', action='store_true', help='read lines from stdin as filenames')
par.add_argument('--time', action='store_const', const=time(), help='print runtime in seconds to stderr at the end')
par.add_argument('files', metavar='file', nargs='*', help='archive to scan')
par.add_argument('--list-dir', action='append', default=[], dest='list_dirs', metavar='dir', help='list dir for files')
par.add_argument('--walk-dir', action='append', default=[], dest='walk_dirs', metavar='dir', help='walk dir tree for files')
par.add_argument('--filelist', action='append', default=[], dest='filelists', metavar='filelist', help='file to read as lists of files to scan')
par.add_argument('--total-only', action='store_true', help='sum the files and print only that')
par.add_argument('--silent', action='store_true', help='print nothing to stdout')
par.add_argument('--raw', action='store_true', help='print raw numbers with no pretty printing')
opts = par.parse_args()

final_7z_exe = next(filter(None, [opts.exe_7z, os.getenv('ZIPSAVINGS_7ZEXE'), 'C:/mybin/7z.exe']))
final_csoinfo_exe = next(filter(None, [opts.exe_csoinfo, os.getenv('ZIPSAVINGS_CSOINFOEXE'), 'C:/mybin/csoinfo.exe']))
files = list(opts.files)

if opts.stdin_filelist:
    files.extend(filter(None, sys.stdin.read().splitlines()))

error_count = 0
for d in opts.list_dirs:
    if os.path.isdir(d):
        files.extend(filter(os.path.isfile, [d + '/' + f for f in os.listdir(d)]))
    else:
        error_count += 1
        print(f"ERROR: {d} : Tried to list a non-dir.", file=sys.stderr)

for d in opts.walk_dirs:
    if os.path.isdir(d):
        for path, dnames, fnames in os.walk(d):
            addfiles = [(path + '/' + f).replace('\\', '/') for f in fnames]
            files.extend(addfiles)
    else:
        error_count += 1
        print(f"ERROR: {d} : Tried to walk a non-dir.", file=sys.stderr)

for f in opts.filelists:
    try:
        with open(f, 'r') as f:
            files.extend(filter(None, f.read().splitlines()))
    except FileNotFoundError as e:
        error_count += 1
        print(f"ERROR: {f} : Filelist file not found.", file=sys.stderr)

def split_into_portions(data, most):
    return [data[i:i+most] for i in range(0, len(data), most)]

archive_infos = []
for file_group in split_into_portions(files, 8):
    jobs = [run7.make_job(f, exe7z=final_7z_exe, execsoinfo=final_csoinfo_exe) for f in file_group]
    for job in jobs:
        try:
            archive_infos.append(job.join())
        except RuntimeError as e:
            error_count += 1
            print(e, file=sys.stderr)

good_count = len(archive_infos)
if error_count > 0:
    print(f'There were {error_count} errors.', file=sys.stderr)
    print('END OF ERRORS.\n', file=sys.stderr)

pprinter = (lambda x: x) if opts.raw else model.pretty_print_info_fields
if opts.total_only:
    total = model.sum_archive_infos(archive_infos)
    total = pprinter(total)
    headers = model.ArchiveInfo._fields
    pretty = table.pretty_print_table([total], headers, False)
    if not opts.silent: print(pretty)
else:
    if opts.sort: archive_infos.sort(key=lambda x: getattr(x, opts.sort), reverse=opts.reverse)
    if opts.total: archive_infos.append(model.sum_archive_infos(archive_infos))
    infos = [pprinter(info) for info in archive_infos]
    headers = model.ArchiveInfo._fields
    pretty = table.pretty_print_table(infos, headers, opts.total)
    if not opts.silent: print(pretty)

if opts.time is not None:
    start_time = opts.time
    end_time = time()
    print(f"Processed {good_count} files out of {len(files)} given in {end_time - start_time} seconds.", file=sys.stderr)
