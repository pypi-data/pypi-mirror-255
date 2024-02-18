# -------------------
def loader_init():
    import os
    import inspect

    # get caller's name
    caller = 'unknown'
    for frame in inspect.stack()[1:]:
        if frame.filename[0] != '<':
            caller = os.path.basename(frame.filename)
            break

    # ensure using local or venv as requestted
    if 'VER_LOCAL' in os.environ:
        # assumes that PYTHONPATH has prepended '.'
        print(f'==== using local: {caller}')
    else:
        print(f'==== using venv: {caller}')
        import sys

        # override the PYTHONPATH setting
        sys.path.insert(0, os.path.join('venv', 'lib', 'site-packages'))
