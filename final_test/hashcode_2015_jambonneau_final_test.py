#!/usr/bin/python
#
# Google Hash Code 2015 - Final test
#
# (c) 2015 Team Jambonneau
#
# Version: 1.0
#

"""Google Hash Code 2015."""

from __future__ import print_function

import sys


class Part(object):

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class Pizza(object):
    """The pizza matrix."""

    def __init__(self, r, c, h, s):
        self.r = r
        self.c = c
        self.h = h
        self.s = s
        self.grid = []
        self.parts = []

    def __str__(self):
        """Display the pizza matrix."""
        return '\n'.join(['<%s>' % ''.join(row) for row in self.grid])

    def create(self):
        for y in range(self.r):
            num_h = 0
            x1 = -1
            x = 0
            while x < self.c:
                print("x,y = %d,%d" % (x, y))
                if self.grid[y][x] == 'H':
                    if num_h == 0:
                        x1 = x
                    num_h += 1
                    if num_h == self.h:
                        xl = x1
                        xr = x
                        size = x - x1 + 1
                        if size <= self.s:
                            # left
                            if x1 > 0:
                                while (xl > 0) and (size < self.s) and \
                                      (self.grid[y][xl - 1] in ('TH')):
                                    xl -= 1
                                    size += 1
                            # right
                            if x < self.c - 1:
                                while (xr < self.c - 1) and (size < self.s) and \
                                      (self.grid[y][xr + 1] in ('TH')):
                                    xr += 1
                                    size += 1
                            print("xl = %d, xr = %d" % (xl, xr))
                            self.parts.append(Part(xl, y, xr, y))
                            for xx in range(xl, xr + 1):
                                self.grid[y][xx] = ' '
                        x = xr + 1
                        print("set x : %d" % x)
                        num_h = 0
                        continue
                x += 1

    def get_score_xy(self, x, y, width, height):
        print("get score %d %d ==> %d %d" % (x, y, width, height))
        if width * height > self.s:
            return -1
        if x + width - 1 >= self.c:
            return -1
        if y + height - 1 >= self.r:
            return -1
        num_h = 0
        for j in range(y, y + height):
            for i in range(x, x + width):
                if self.grid[j][i] == ' ':
                    return -1
                if self.grid[j][i] == 'H':
                    num_h += 1
        if num_h < self.h:
            return -1
        return 1

    def create_combs(self):
        combs = ((4, 3), (3, 4), (3, 3), (6, 2), (2, 6), (12, 1), (1, 12))
        for y in range(self.r):
            for x in range(self.c):
                scores = []
                for comb in combs:
                    scores.append(self.get_score_xy(x, y, comb[0], comb[1]))
                best = scores.index(max(scores))
                if scores[best] > 0:
                    self.parts.append(
                        Part(x, y,
                             x + combs[best][0] - 1, y + combs[best][1] - 1))
                    for yy in range(y, y + combs[best][1]):
                        for xx in range(x, x + combs[best][0]):
                            self.grid[yy][xx] = ' '

    def get_score(self):
        return sum([(p.x2 - p.x1 + 1) * (p.y2 - p.y1 + 1)
                    for p in self.parts])


def read_matrix(filename):
    """Read the input file."""
    with open(filename, 'r') as fin:
        _pizza = Pizza(*[int(num) for num in fin.readline().split()])
        # read matrix
        for i in range(_pizza.r):
            str_line = fin.readline().strip()
            line = []
            for c in str_line:
                line.append(c)
            _pizza.grid.append(line)

    return _pizza


def write_matrix(pizza, filename):
    """Write output file."""
    with open(filename, 'w') as fout:
        fout.write('%d\n' % len(pizza.parts))
        for p in pizza.parts:
            fout.write('%d %d %d %d\n' % (p.y1, p.x1, p.y2, p.x2))


def main():
    """Main function."""

    if len(sys.argv) < 3:
        sys.exit('Syntax: %s <filename> <output>' % sys.argv[0])

    # read data and initialize the matrix
    pizza = read_matrix(sys.argv[1])

    pizza.create_combs()

    print(pizza)

    print('score: %d' % pizza.get_score())

    # write output file
    write_matrix(pizza, sys.argv[2])


if __name__ == '__main__':
    main()
