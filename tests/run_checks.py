"""Run the checks of one lab and print one friendly line per TODO.

    python3 tests/run_checks.py 1        (this is what ./lab check 1 does)
"""

import collections
import contextlib
import os
import re
import sys
import pathlib

import pytest

HERE = pathlib.Path(__file__).resolve().parent


class Collector:
    def __init__(self):
        self.results = collections.OrderedDict()     # 'todo3' -> [(name, ok, message)]

    def pytest_runtest_logreport(self, report):
        if report.when != 'call' and not (report.when == 'setup' and report.failed):
            return
        m = re.search(r'test_(todo\d+b?|clusters)', report.nodeid)
        key = m.group(1) if m else 'other'
        message = ''
        if report.failed:
            crash = getattr(report.longrepr, 'reprcrash', None)
            message = crash.message if crash else str(report.longrepr).splitlines()[-1]
            message = message.split('\nassert')[0].replace('AssertionError: ', '').strip()
            message = ' | '.join(line.strip() for line in message.splitlines() if line.strip())
            if message.startswith('NotImplementedError'):
                message = 'not written yet (' + message.split(': ', 1)[-1] + ')'
        self.results.setdefault(key, []).append((report.nodeid.split('::')[-1], report.passed, message))


def main():
    lab = sys.argv[1] if len(sys.argv) > 1 else '1'
    c = Collector()
    with open(os.devnull, 'w') as quiet, contextlib.redirect_stdout(quiet):
        pytest.main(['-q', '--tb=short', '-p', 'no:cacheprovider',
                     str(HERE / f'test_lab{lab}.py')], plugins=[c])
    if not c.results:
        print('  The checks could not run at all. Is there a Python error in your file?')
        print(f'  Try:  python3 -m pytest tests/test_lab{lab}.py')
        return 1
    all_ok = True
    for key, rows in c.results.items():
        ok = sum(1 for _, passed, _ in rows if passed)
        label = key.replace('todo', 'TODO ') if key.startswith('todo') else key
        if ok == len(rows):
            print(f'  PASS  {label:8s} {ok}/{len(rows)} checks')
        else:
            all_ok = False
            first = next(msg for _, passed, msg in rows if not passed)
            print(f'  FAIL  {label:8s} {ok}/{len(rows)} checks -- {first}')
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
