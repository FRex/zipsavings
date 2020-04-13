import pytest


@pytest.mark.parametrize("headers, infos, ret", (
    (
        ('archive', 'size', 'unpacked', 'saved', 'saved_percent', 'file_count', 'type'),
        [
            ['./test/dracula.7z', '268.38 KiB', '846.86 KiB', '578.48 KiB', '68.31%', '1', '7z'],
            ['./test/dracula.zip','310.59 KiB', '846.86 KiB', '536.27 KiB', '63.32%', '1', 'zip']
        ],
        (18, 10, 10, 10, 13, 10, 4)
    ),
    (
        ('a', 'b'*2, 'c'*3),
        [
            ['a'*3, 'b', 'c'],
            ['a', 'b', 'c'],
        ],
        (3, 2, 3)
    ),
    (
        ('a', 'b'*2, 'c'*3),
        [
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
        ],
        (1, 2, 3)
    )
))
def test_calculate_fields_widths(infos, headers, ret):
    import table
    assert table.calculate_fields_widths(infos, headers) == ret


@pytest.mark.parametrize("unpacked, unpacked_sizes, ret",
(
    (1, (1, 2, 2**32+1, 10, 11), 2**32+1),
    (10, (1, 2, 10), 10),
    (20, (1, 2), 20)
))
def test_gzipguess_find_size(unpacked, unpacked_sizes, ret):
    import gzipguess
    assert gzipguess.find_size(unpacked, unpacked_sizes) == ret