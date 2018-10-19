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
par.add_argument('--stdin-filelist', action='store_true', help='read lines from stdin as filenames')
par.add_argument('--time', action='store_const', const=time(), help='print runtime in seconds to stderr at the end')
par.add_argument('files', metavar='file', nargs='*', help='archive to scan')
opts = par.parse_args()

final_7z_exe = next(filter(None, [opts.exe_7z, os.getenv('ZIPSAVINGS_7ZEXE'), 'C:/mybin/7z.exe']))
files = list(opts.files)

if opts.stdin_filelist:
    files.extend([l for l in sys.stdin.read().split('\n') if l])

def split_into_portions(data, most):
    return [data[i:i+most] for i in range(0, len(data), most)]

archive_infos = []
error_count = 0
for file_group in split_into_portions(files, 8):
    jobs = [run7.make_job(f, exe7z=final_7z_exe) for f in file_group]
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

if opts.sort:
    archive_infos.sort(key=lambda x: getattr(x, opts.sort), reverse=opts.reverse)

if opts.total:
    archive_infos.append(model.sum_archive_infos(archive_infos))

infos = [model.pretty_print_info_fields(info) for info in archive_infos]
headers = model.ArchiveInfo._fields
print(table.pretty_print_table(infos, headers))

if opts.time is not None:
    start_time = opts.time
    end_time = time()
    print(f"Processed {good_count} files out of {len(files)} given in {end_time - start_time} seconds.", file=sys.stderr)
