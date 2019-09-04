import os
import sys
import argparse
from time import time
import model, run7, table, exefinder, gzipguess


if __name__ != '__main__':
    raise RuntimeError("This is a script, not a module.")

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
par.add_argument('--guess-gzip-unpacked', action='store_true', dest='guess_gzip_unpacked', help='guess gzip unpacked size from other files with same unpacked size modulo 2^32')
opts = par.parse_args(sys.argv[1:] or ['-h'])
exes = exefinder.find_exes(['7z', 'csoinfo'], opts)
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
for file_group in split_into_portions(files, 1):
    jobs = [run7.make_job(f, exes) for f in file_group]
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
    sys.stderr.flush() #to avoid problems with 2>&1 redirection to make sure errors print first

if opts.guess_gzip_unpacked:
    archive_infos = gzipguess.guess_gzip_infos(archive_infos)

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
    all_count = len(files)
    end_time = time()
    timetaken = end_time - start_time
    good_speed = round(good_count / timetaken, 2)
    all_speed = round(all_count / timetaken, 2)
    timetaken = round(timetaken, 3)
    sys.stdout.flush() #to avoid problems with 2>&1 redirection to make sure this msg is last
    msg = f"Processed {good_count} files ({good_speed}/s) out of {all_count} given ({all_speed}/s) in {timetaken} seconds."
    print(msg, file=sys.stderr)
