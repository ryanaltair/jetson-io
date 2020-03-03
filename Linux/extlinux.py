# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from Utils import fio
import os
import re
import shutil

_label_keywords = ['APPEND', 'FDT', 'FDTDIR', 'INITRD', 'LINUX', 'MENU']


def add_entry(extlinux, label, mlabel, dtb, default):
    fio.is_rw(extlinux)

    backup = extlinux + '.backup'
    if not os.path.exists(backup):
        shutil.copyfile(extlinux, backup)

    with open(extlinux, 'r') as fin:
        contents = fin.readlines()

    entry = 'LABEL %s' % label
    entry_skip = False
    out = []

    for line in contents:
        if default:
            line = re.sub(r'^DEFAULT .*', 'DEFAULT %s' % label, line)
        if entry == line.strip():
            entry_skip = True
            continue
        if entry_skip:
            words = line.strip().split()
            if not words:
                continue
            if words[0][0] == '#':
                continue
            if words[0] in _label_keywords:
                continue
            entry_skip = False
        out.append(line)

    # If last line is not blank, add one.
    if not out[-1].isspace():
        out.append('\n')

    out.append('LABEL %s' % label)
    out.append('\n\tMENU LABEL %s' % mlabel)
    out.append('\n\tLINUX /boot/Image')
    out.append('\n\tFDT %s' % dtb)
    out.append('\n\tINITRD /boot/initrd')
    out.append('\n\tAPPEND ${cbootargs}\n')

    with open(extlinux, 'w') as fout:
        for line in out:
            fout.write(line)
