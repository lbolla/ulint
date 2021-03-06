#!/usr/bin/env python

import os
import sys
import subprocess
import operator
import inspect


def call(cmd):
    p = subprocess.Popen(cmd.split(),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out.decode('utf-8'), err.decode('utf-8')


class Lint(object):

    def __init__(self, cmd, extra_params=''):
        self.cmd = cmd
        self.extra_params = extra_params

    def exists(self):
        retcode, _, _ = call('which %s' % self.cmd)
        return retcode == 0

    def output(self, out, err):
        print(' * %s:\n%s\n%s' % (self.cmd, out, err))

    def run(self, filename):
        retcode, out, err = call('%s %s %s' %
                (self.cmd, self.extra_params, filename))
        if out or err:
            self.output(out, err)
        return retcode


class Checker(object):

    exts = []
    lints = []

    @classmethod
    def understands(cls, ext):
        return ext in cls.exts

    @classmethod
    def check(cls, filename):
        retcode = reduce(operator.or_,
                [lint.run(filename) for lint in cls.lints
                    if lint.exists()],
                0)
        if retcode != 0:
            sys.exit(retcode)


class PythonChecker(Checker):

    exts = ['.py']
    lints = [
            Lint('pep8'),
            Lint('pylint', '-E -d E1103'),
            Lint('pyflakes'),
            ]


class JavascriptChecker(Checker):

    exts = ['.js']
    lints = [Lint('gjslint')]


class HaskellChecker(Checker):

    exts = ['.hs']
    lints = [Lint('hlint')]


def guess_ext(filename):
    _, out, _ = call('file -b %s' % filename)
    if 'python' in out:
        return '.py'
    else:
        print('Cannot guess extension')
        return None


def main():
    if len(sys.argv) < 2:
        print('Usage: %s <filename>' % os.path.basename(sys.argv[0]))
        sys.exit(1)

    filename = os.path.abspath(sys.argv[1])

    _, ext = os.path.splitext(filename)
    ext = ext or guess_ext(filename) or sys.exit(1)

    checkers = [g for g in globals().values()
            if inspect.isclass(g) and issubclass(g, Checker)]

    for checker in checkers:
        if checker.understands(ext):
            checker.check(filename)


if __name__ == '__main__':
    main()
