from importlib.resources import read_text


def usage():
    from setux.main import banner
    tpl = read_text('setux.cli', 'usage.tpl')
    txt = tpl.strip().format(**locals())
    return txt
