#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# soundloc utils
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2013/IIMAS/UNAM
# ----------------------------------------------------------------------
# compare.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------------

import re

re_sep =re.compile("^---$")
re_sam =re.compile("^Sample: (\d+)$")
re_doa =re.compile("^DOAS:$")
re_str =re.compile("^Stream Info:$")

def read(filename):
    state=1
    acc=[]
    samples=[]
    doas=[]
    stream=[]
    sample=None
    doa=None
    with open(filename,"r") as fn:
        for line in fn:
            line=line.strip()
            if re_sep.match(line):
                state=1
                samples.append(sample)
                doas.append(doa)
                stream.append(acc)
            if state==1:
                m=re_sam.match(line)
                if m:
                    sample=int(m.group(1))
                    state=2
            elif state==2:
                if re_doa.match(line):
                    state=3
                    acc=[]
            elif state==3:
                if re_str.match(line):
                    doa=acc
                    state=4
                    acc=[]
                elif len(line)>0:
                    acc.append(float(line))
            elif state==4:
                if len(line)>0:
                    acc.append(float(line))
 
                
    return samples,doas,stream



