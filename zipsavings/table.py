def calculate_fields_widths(infos, headers):
    return tuple(max(map(len,column)) for column in zip(headers, *infos))

def make_row(row_data, field_widths):
    return '|'.join(str(r).ljust(w) for r, w in zip(row_data, field_widths))

def make_separator(field_widths):
    return '|'.join('-' * w for w in field_widths)

def pretty_print_table(infos, headers, total):
    field_widths = calculate_fields_widths(infos, headers)
    headers = make_row(headers, field_widths)
    separator = make_separator(field_widths)
    ret = [headers, separator]
    for info in infos:
        ret.append(make_row(info, field_widths))
    if total:
        ret = ret[:-1] + [separator, ret[-1]]
    return '\n'.join(ret)
