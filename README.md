# zipsavings
`zipsavings` is a simple Python script/module that uses `subprocess.Popen`
to invoke `7z l` on each given archive and print stats about it. See below for
an example of invoking and output.

Made on `Python 3.7.1 (v3.7.1:260ec2c36a, Oct 20 2018, 14:57:15) [MSC v.1915 64 bit (AMD64)] on win32`,
might work on older versions too. If you need it for older version of Python 3 feel free to open an issue for it.

I wrote it for personal use (to easily see how much space I save by using `7z` or
compare how well `xz` and `gz` compress a given tar) which shows (no
proper documentation, ad-hoc code, etc.) but I plan on improving it and make
it more general and usable by anyone as that (working as if I'm writing a
general purpose tool for wide audience) is for me the easiest way to put
quality and polish into it. It's already in quite a usable state as it is.

Run with `--help` or `-h` to get a help/usage message generated by argparse.

If you plan on using it or use it then please let me know and/or star this project so
that I know my work on making it usable by others is not in vain.

It should never hang (for example, on `7z` files with encrypted headers
which make `7z l` prompt for a password), crash or print garbage. On files
that are mangled, encrypted `7z`, files with not size info in the
headers `bz2`, directories, non-archive files, etc. it should print an error
and go on with processing and printing all the other files. The only was for it
to print garbage is if `7z l` itself got confused (see below
in `File formats` section for an example of where I found such a file).

Note: 'unpacked' and 'packed' fields show sizes of data files themselves
before and after packing, they don't take 'size on disk' into account
for 'unpacked' nor headers/archive format overhead for 'packed'. The 'size'
column shows the size of the archive itself in bytes (the size listed in
'Scanning the drive for archives:' part of `7z l` output, as far as I know
it's the same as the 'Physical Size' line but that line isn't present in
outputs for some formats like `gz`).

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
Use `-h` or `--help` to see the full arguments list help generated by `argparse`.

Use `--total` or `-t` to print another entry at the end that is sum of all others,
`--sort=field` or `-s field` to sort by a field (pass in wrong field name to get list of field names),
add `--reverse` or `-r` to reverse the sort. Total is not sorted and always last.

Use `--stdin-filelist` to pass list of files from stdin (like from running `find -type f` or similar)
due to bash/shell saying argument list is too long to contain all your files.

Use `--walk-dir` or `--list-dir` to walk a dir tree for files or use all files in a dir (but not it's subdirs).

# File formats

It works fully (both compression stats and file
count) for `rar`, `7z`, `zip`, some `exe` (NSIS installers), etc.

In case of `iso` and `tar` (without additional compression around it) the file
count is accurate but compression will be 0 or slightly negative.

In case of `xz` and `gzip` the file count will be 1 (since these aren't archives
but simple compression layers around single file, just usually used with `tar`) but compression will be accurate.

In case of `bzip2` (another compression often used with `tar`) an error will be
printed as `compressed` column in `7z l` output is empty (`bz2` file format
has no header field saying how big the original uncompressed file was).

Some files give **very** unusual results if they confuse `7z` itself.
For example, running `zipsavings` on an entire tree of files using `--walk-dir` I
ran across a `.o` file made by `GHC` (Glasgow Haskell Compiler) on `Windows 10`
that `7z l` reports as being a bit over `50 TiB` (`54975648497664` bytes,
exactly `50 TiB` and `64 MiB`) unpacked. It even broke a certain fragile part
of `7z l` output parsing code due to how wide that number is in the output (and
I never ran across an archive that had such crazy sizes in them and thus don't
have such an archive in files I test zipsavings on each commit with).

It doesn't unpack the archive nor looks at filenames to warn about possible
archive-in-archive scenarios that will make savings look really small (because
the real savings are in inner archives, not the outer one that this tool analyzes).

In case of a split archive the file contains the first part will work, with the
type listed as `Split` and all other fields except `size` (which will be the size
of just the first file) being accurate. Other parts will error out
with `Can not open the file as archive.` or (sometimes) `Headers error, unconfirmed start of archive.`


# Example usage

```
$ python -m zipsavings ./test/snek.7z
archive       |unpacked|packed   |saved    |saved_percent|file_count|type|size
--------------|--------|---------|---------|-------------|----------|----|---------
./test/snek.7z|1.4 MiB |484.4 KiB|947.2 KiB|66.16%       |6         |7z  |484.8 KiB
```

```
$ python -m zipsavings --list-dir test --total --sort file_count --reverse --time
ERROR: test/a.bz2 : No size data in bzip2 format.
ERROR: test/b.notarchive : Can not open the file as archive.
ERROR: test/dracula-encrypted.7z : Encrypted filenames.
ERROR: test/dracula.txt : Can not open the file as archive.
ERROR: test/FreeDOS-FD12CD.7z.002 : Headers error, unconfirmed start of archive.
ERROR: test/FreeDOS-FD12CD.7z.003 : Headers error, unconfirmed start of archive.
ERROR: test/FreeDOS-FD12CD.7z.004 : Headers error, unconfirmed start of archive.
ERROR: test/FreeDOS-FD12CD.7z.005 : Headers error, unconfirmed start of archive.
ERROR: test/FreeDOS-FD12CD.cso : Headers error, unconfirmed start of archive.
ERROR: test/FreeDOS-FD12CD.zip.002 : Headers error, unconfirmed start of archive.
ERROR: test/FreeDOS-FD12CD.zip.003 : Headers error, unconfirmed start of archive.
ERROR: test/FreeDOS-FD12CD.zip.004 : Headers error, unconfirmed start of archive.
ERROR: test/FreeDOS-FD12CD.zip.005 : Headers error, unconfirmed start of archive.
ERROR: test/random10megs.7z.002 : Can not open the file as archive.
ERROR: test/random10megs.7z.003 : Can not open the file as archive.
ERROR: test/random10megs.binary : Can not open the file as archive.
ERROR: test/random10megs.zip.002 : Can not open the file as archive.
ERROR: test/random10megs.zip.003 : Can not open the file as archive.
ERROR: test/wat.txt.bz2 : No size data in bzip2 format.
There were 19 errors.
END OF ERRORS.

archive                                |unpacked |packed   |saved     |saved_percent|file_count|type |size
---------------------------------------|---------|---------|----------|-------------|----------|-----|---------
test/million-files.7z                  |5.7 MiB  |155.5 KiB|5.6 MiB   |97.35%       |1000000   |7z   |6.4 MiB
test/d8krhj4kasdu3~.swf                |11.4 MiB |11.4 MiB |0 Bytes   |0.0%         |2628      |SWF  |11.4 MiB
test/FreeDOS-FD12CD.iso                |417.5 MiB|417.5 MiB|0 Bytes   |0.0%         |553       |Iso  |418.5 MiB
test/NorthBuryGrove.rar                |2.2 GiB  |966.2 MiB|1.2 GiB   |56.55%       |198       |Rar5 |966.2 MiB
test/Fedora-Xfce-Live-x86_64-28-1.1.iso|1.4 GiB  |1.4 GiB  |0 Bytes   |0.0%         |39        |Iso  |1.3 GiB
test/windirstat1_1_2_setup.exe         |2.2 MiB  |591.6 KiB|1.6 MiB   |73.24%       |23        |Nsis |630.6 KiB
test/snek.7z                           |1.4 MiB  |484.4 KiB|947.2 KiB |66.16%       |6         |7z   |484.8 KiB
test/showframe.cab                     |2.3 KiB  |1.3 KiB  |990 Bytes |42.15%       |2         |Cab  |1.3 KiB
test/x.tar                             |54 Bytes |1.0 KiB  |-970 Bytes|-1796.3%     |2         |tar  |10.0 KiB
test/d.gz                              |0 Bytes  |22 Bytes |-22 Bytes |0%           |1         |gzip |22 Bytes
test/d8krhj4kasdu3.swf                 |11.4 MiB |9.9 MiB  |1.5 MiB   |13.29%       |1         |SWFc |9.9 MiB
test/dracula.7z                        |846.9 KiB|268.2 KiB|578.6 KiB |68.32%       |1         |7z   |268.4 KiB
test/dracula.zip                       |846.9 KiB|310.4 KiB|536.4 KiB |63.34%       |1         |zip  |310.6 KiB
test/dracula.zip.7z                    |310.6 KiB|310.6 KiB|-19 Bytes |-0.01%       |1         |7z   |310.7 KiB
test/fixpdfmag.tar.lzma                |10.0 KiB |1.3 KiB  |8.7 KiB   |87.14%       |1         |lzma |1.3 KiB
test/FreeDOS-FD12CD.7z.001             |418.5 MiB|400.7 MiB|17.8 MiB  |4.25%        |1         |Split|100.0 MiB
test/FreeDOS-FD12CD.zip.001            |418.5 MiB|411.9 MiB|6.5 MiB   |1.55%        |1         |Split|100.0 MiB
test/random10megs.7z.001               |10.0 MiB |10.0 MiB |-559 Bytes|-0.01%       |1         |Split|4.0 MiB
test/random10megs.zip.001              |10.0 MiB |10.0 MiB |0 Bytes   |0.0%         |1         |Split|4.0 MiB
test/wat.txt.gz                        |1.0 MiB  |1.0 MiB  |-186 Bytes|-0.02%       |1         |gzip |1.0 MiB
test/xz.xz                             |4.8 MiB  |492.9 KiB|4.3 MiB   |89.96%       |1         |xz   |492.9 KiB
---------------------------------------|---------|---------|----------|-------------|----------|-----|---------
TOTAL                                  |4.8 GiB  |3.6 GiB  |1.3 GiB   |26.24%       |1003463   |SUM  |2.9 GiB
Processed 21 files out of 40 given in 2.8770182132720947 seconds.
```

# Efficiency

Despite using lots of unoptimized list, tuple and string happy Python 3 code this tool's main
bottleneck is actual disk access and starting and running `7z` processes themselves (one for each archive given).

All of the timings below are from repeated runs on a quad core (8 thread) Intel CPU on a laptop
with plenty free RAM (for OS to cache into) with `7z.exe` and Python 3 on an SSD and archives and this tool's code on an HDD.

Running with more cores or without OS caching the exes, code and archives into RAM will give different results
but the point of `7z` being the bottleneck and Python code being irrelevant still stands.

The above 8 analyzable archives among 11 files takes literally no time to run:

```
$ python -m zipsavings test/* -t -s file_count -r --time  2>&1 | tail -n 1
Processed 8 files out of 11 given in 0.06281304359436035 seconds.
```

Running it on a very large list of files (MiKTex local package repo) show that `7z` is the real bottleneck:

```
$ find D:/MiKTexDownloadFiles -type f | python -m zipsavings --stdin-filelist -t -s file_count -r --time 2>&1 | tail -n 1
Processed 3463 files out of 3530 given in 15.60750675201416 seconds.
```

Changing code to run and wait for 1 `7z` process at a time (by
changing `for file_group in split_into_portions(all_files, 8):` to `for file_group in split_into_portions(all_files, 1):`)
causes the tool to take predictably longer:

```
$ find D:/MiKTexDownloadFiles -type f  | python -m zipsavings --stdin-filelist -t -s file_count -r  --time 2>&1 | tail
-n 1
Processed 3463 files out of 3530 given in 50.39897918701172 seconds.
```
