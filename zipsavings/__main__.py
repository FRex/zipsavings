import os
import sys
from time import time
from getopt import gnu_getopt
from . import model, run7, table


if __name__ != '__main__': raise RuntimeError("This is a script, not a module.")

opts, files = gnu_getopt(sys.argv[1:], 'ts:r', ['total', 'sort=', 'reverse', '7zexe=', 'stdin-filelist', 'time'])

total = False
sort_by_field = None
reverse_sort = False
new_7z_exe = None
read_stdin_filelist = False
start_time = None

for o, v in opts:
    if o in ['--total', '-t']: total = True
    if o in ['--sort', '-s']: sort_by_field = v
    if o in ['--reverse', '-r']: reverse_sort = True
    if o in ['--7zexe']: new_7z_exe = v
    if o in ['--stdin-filelist']: read_stdin_filelist = True
    if o in ['--time']: start_time = time()

if sort_by_field is not None and sort_by_field not in model.ArchiveInfo._fields:
    print(f"'{sort_by_field}' is not a valid field name to sort by", file=sys.stderr)
    print("Try: " + ', '.join(model.ArchiveInfo._fields), file=sys.stderr)
    sys.exit(1)

archive_infos = []

final_7z_exe = next(filter(None, [new_7z_exe, os.getenv('ZIPSAVINGS_7ZEXE'), 'C:/mybin/7z.exe']))

all_files = files
if read_stdin_filelist:
    all_files = files + [l for l in sys.stdin.read().split('\n') if l]

def split_into_portions(data, most):
    return [data[i:i+most] for i in range(0, len(data), most)]

error_count = 0
for file_group in split_into_portions(all_files, 8):
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

if sort_by_field:
    archive_infos.sort(key=lambda x: getattr(x, sort_by_field), reverse=reverse_sort)

if total:
    archive_infos.append(model.sum_archive_infos(archive_infos))

infos = [model.pretty_print_info_fields(info) for info in archive_infos]
headers = model.ArchiveInfo._fields
print(table.pretty_print_table(infos, headers))

if start_time is not None:
    end_time = time()
    print(f"Processed {good_count} files out of {len(all_files)} given in {end_time - start_time} seconds.", file=sys.stderr)
