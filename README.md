# zipsavings
`zipsavings` is a simple Python script that uses `subprocess.Popen`
to invoke `7z l` on each given archive and print stats about it.

I wrote it for personal use which shows (no documentation, ad-hoc code, etc.) but
I plan on improving it and make it more general
and usable by anyone as that (working as if I'm writing a general purpose tool
for wide audience) is for me the easiest way to put quality and polish into it.

If you plan on using it or use it then please let me know and/or star this project so
that I know my work on making it usable by others is not in vain.


# 7z exe

Use `--7zexe=path` or set env var `ZIPSAVINGS_7ZEXE` to specify the `7z` exe.
If both are missing the fallback is `C:/mybin/7z.exe` since that's where I keep mine.


# Options
Use `--total` or `-t` to print another entry at the end that is sum of all others,
`--sort=field` or `-s field` to sort by a field (pass in wrong field name to get list of field names),
add `--reverse` or `-r` to reverse the sort. Total is not sorted and always last.


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
$ python zipsavings.py snek.7z  cmake-3.12.1-win64-x64.7z
Archive: snek.7z
Unpacked: 1.4 MiB (1.5 MB, 1 465 984 bytes)
Packed: 484.4 KiB (496.0 kB, 496 040 bytes)
Saved: 947.2 KiB (969.9 kB, 969 944 bytes)
Saved %: 66.16%
File count: 6

Archive: cmake-3.12.1-win64-x64.7z
Unpacked: 18.3 MiB (19.2 MB, 19 168 763 bytes)
Packed: 16.8 MiB (17.6 MB, 17 615 868 bytes)
Saved: 1.5 MiB (1.6 MB, 1 552 895 bytes)
Saved %: 8.1%
File count: 1
```
