# zipsavings
`zipsavings` is a simple Python script/module that uses `subprocess.Popen`
to invoke `7z l` on each given archive and print stats about it.

Requires packages `humanize` and `tablib`, and a `7z` exe.

I wrote it for personal use which shows (no documentation, ad-hoc code, etc.) but
I plan on improving it and make it more general
and usable by anyone as that (working as if I'm writing a general purpose tool
for wide audience) is for me the easiest way to put quality and polish into it.

If you plan on using it or use it then please let me know and/or star this project so
that I know my work on making it usable by others is not in vain.

Note: 'unpacked' and 'packed' fields show sizes of data files themselves
before and after packing, they don't take 'size on disk' into account
for 'unpacked' nor headers/archive format overhead for 'packed'.

Best way to run it is to zip up the `zipsavings` directory contents
and run it directly with python or (to keep tinkering with it) via a help
script placed in `PATH` like:

```
#!/bin/bash
export PYTHONPATH='PATH_TO_THIS_REPO'
python -B -m zipsavings "$@"
```

# 7z exe

Use `--7zexe=path` or set env var `ZIPSAVINGS_7ZEXE` to specify the `7z` exe.
If both are missing the fallback is `C:/mybin/7z.exe` since that's where I keep mine.


# Options
Use `--total` or `-t` to print another entry at the end that is sum of all others,
`--sort=field` or `-s field` to sort by a field (pass in wrong field name to get list of field names),
add `--reverse` or `-r` to reverse the sort. Total is not sorted and always last.

Use `--stdin-filelist` to pass list of files from stdin (like from running `find -type f` or similar)
due to bash/shell saying argument list is too long to contain all your files.


# File formats

It works fully (both compression stats and file
count) for `rar`, `7z`, `zip`, some `exe` (NSIS installers), etc.

In case of `iso` and `tar` (without additional compression around it) the file
count is accurate but compression will be 0 or slightly negative.

In case of `xz` and `gzip` the file count will be 1 (since these aren't archives
but simple compression layers around single file, just usually used with `tar`) but compression will be accurate.

In case of `bzip2` (another compression often used with `tar`) an error will be
printed as `compressed` column in `7z l` output is empty.

It doesn't unpack the archive (and won't in the future as that'd be way too prohibitive with
regards to CPU and disk access) nor looks at filenames (yet, but maybe later) to warn
about possible archive-in-archive scenario (like compressing `exe` NSIS installer that
already has 30-80% compression into a `7z` which will look like marginal 1-5% gain
even on top ultra 7zip settings or compressing with `7z` already compressed video and audio formats).


# Example usage

```
$ python -m zipsavings test/* -t -s file_count -r
ERROR: test/a.bz2 : No size data in bzip2 format.
ERROR: test/b.notarchive : Can not open the file as archive.
ERROR: test/wat.txt.bz2 : No size data in bzip2 format.
END OF ERRORS

archive                       |unpacked|packed   |saved     |saved_percent|file_count
------------------------------|--------|---------|----------|-------------|----------
test/NorthBuryGrove.rar       |2.2 GiB |966.2 MiB|1.2 GiB   |56.55%       |198
test/windirstat1_1_2_setup.exe|2.2 MiB |591.6 KiB|1.6 MiB   |73.24%       |23
test/snek.7z                  |1.4 MiB |484.4 KiB|947.2 KiB |66.16%       |6
test/x.tar                    |54 Bytes|1.0 KiB  |-970 Bytes|-1796.3%     |2
test/d.gz                     |0 Bytes |22 Bytes |-22 Bytes |0%           |1
test/wat.txt.gz               |1.0 MiB |1.0 MiB  |-186 Bytes|-0.02%       |1
TOTAL                         |2.2 GiB |968.2 MiB|1.2 GiB   |56.55%       |231
```
