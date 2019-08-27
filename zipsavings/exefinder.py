import os


PATH_DIR_SEPARATOR = ';' if os.name == 'nt' else ':'


def find_exe_in_env_path(exename):
    p = os.getenv('PATH') or ''
    p = [f"{i}/{exename}" for i in p.split(PATH_DIR_SEPARATOR)]
    p = [i for i in p if os.path.isfile(i)]
    return p


def exe_opt_name(exename):
    return f"exe_{exename}"


def exe_env_name(exename):
    return f"ZIPSAVINGS_{exename.upper()}EXE"


def find_exes(names, opts):
    opts = opts.__dict__
    ret = {}
    for n in names:
        oname = exe_opt_name(n)
        ename = exe_env_name(n)
        if oname in opts and opts[oname]:
            ret[n] = opts[oname]
        elif os.getenv(ename):
            ret[n] = os.getenv(ename)
        else:
            found = find_exe_in_env_path(n) + find_exe_in_env_path(n + '.exe')
            if n == '7z': #special case, 7z fallback to 7za
                found += find_exe_in_env_path('7za')
                found += find_exe_in_env_path('7za.exe')
            if found: ret[n] = found[0]
    return ret
