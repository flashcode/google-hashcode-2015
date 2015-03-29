#!/usr/bin/python
#
# Google Hash Code 2015 - Final
#
# (c) 2015 Team Jambonneau
#
# Version: 1.0
#

"""Google Hash Code 2015."""

from __future__ import print_function

import math
import random
import sys


def get_distance(y1, x1, y2, x2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class Ballon(object):

    def __init__(self, id, y, x, a):
        self.id = id
        self.y = y
        self.x = x
        self.a = a
        self.lost = False
        self.target_x = -1
        self.target_y = -1

    def __str__(self):
        return 'ballon: y,x=(%d,%d), a=%d, lost=%s, target=(%d,%d)' % (
            self.y, self.x, self.a, self.lost, self.target_y, self.target_x)


class Ballons(object):

    def __init__(self, r, c, a, l, v, b, t, r1, c1):
        self.r = r
        self.c = c
        self.a = a
        self.l = l
        self.v = v
        self.b = b
        self.t = t
        self.r1 = r1
        self.c1 = c1
        self.ballons = []
        self.cibles = []
        self.vents = []
        self.rounds = []
        self.delta_cells = self.compute_delta_cells(self.v)
        self.targets_covered = []
        self.init_targets_covered()

    def __str__(self):
        return 'r=%d, c=%d, a=%d, l=%d, v=%d, b=%d, t=%d, r1=%d, c1=%d' % (
            self.r, self.c, self.a, self.l, self.v, self.b, self.t,
            self.r1, self.c1)

    def disperse_cibles(self):
        x2 = self.c / 3
        x3 = (self.c / 3) * 2
        cibles1 = [cible for cible in self.cibles
                   if cible[1] <= x2]
        cibles2 = [cible for cible in self.cibles
                   if cible[1] > x2 and cible[1] <= x3]
        cibles3 = [cible for cible in self.cibles
                   if cible[1] > x3]
        self.cibles = [cibles1[:], cibles2[:], cibles3[:]]

    def compute_delta_cells(self, radius):
        covered_delta = []
        for r in range(-radius, radius + 1):
            for c in range(-radius, radius + 1):
                covered_delta.append((r, c))
        result = []
        for cell in covered_delta:
            if get_distance(cell[0], cell[1], 0, 0) <= radius:
                result.append(cell)
        return result

    def get_targets_covered_at_pos(self, y, x):
        number = 0
        for cible in self.cibles:
            if cible in self.targets_covered[y][x]:
                number += 1
        return number

    def init_targets_covered(self):
        for y in range(0, self.r):
            line = []
            for x in range(0, self.c):
                cells = []
                for delta in self.delta_cells:
                    y += delta[0]
                    x += delta[1]
                    if y >= 0 and y <= self.r - 1:
                        if x < 0:
                            x = self.c + x
                        else:
                            x = x % self.c
                        cells.append((y, x))
                line.append(cells)
            self.targets_covered.append(line)

    def get_best_targets(self):
        best_targets = {}
        for y in range(self.r):
            for x in range(self.c):
                best_targets[(y, x)] = self.get_targets_covered_at_pos(y, x)
        return sorted(best_targets, key=lambda v: best_targets[v],
                      reverse=True)

    def select_ballons_targets(self):
        best_targets = self.get_best_targets()
        for b in self.ballons:
            b.target_y, b.target_x = best_targets.pop(0)

    def select_ballons_targets_random(self):
        i = 0
        for b in self.ballons:
            index = random.randint(0, len(self.cibles[i]) - 1)
            b.target_y, b.target_x = self.cibles[i][index]
            self.cibles[i].pop(index)
            i = (i + 1) % 3

    def can_move_down(self, ballon):
        return ballon.a > 1

    def can_move_up(self, ballon):
        return ballon.a < self.a - 1

    def move_down(self, ballon):
        if self.can_move_down(ballon):
            ballon.a -= 1
            return True
        return False

    def move_up(self, ballon):
        if self.can_move_up(ballon):
            ballon.a += 1
            return True
        return False

    def move_west(self, ballon):
        ballon.x = self.c - 1 if ballon.x == 0 else ballon.x - 1

    def move_east(self, ballon):
        ballon.x = (ballon.x + 1) % self.c

    def move_north(self, ballon):
        if ballon.y >= 0:
            ballon.y -= 1
            if ballon.y < 0:
                ballon.lost = True
            return True
        return False

    def move_south(self, ballon):
        if ballon.y <= self.r - 1:
            ballon.y += 1
            if ballon.y == self.r:
                ballon.lost = True
            return True
        return False

    def apply_wind(self):
        for b in self.ballons:
            if b.a > 0 and not b.lost:
                vents_a = self.vents[b.a]
                delta_y = vents_a[b.y][b.x][0]
                delta_x = vents_a[b.y][b.x][1]
                for i in range(abs(delta_x)):
                    if delta_x > 0:
                        self.move_east(b)
                    else:
                        self.move_west(b)
                for i in range(abs(delta_y)):
                    if delta_y > 0:
                        self.move_south(b)
                    else:
                        self.move_north(b)

    def get_best_move(self, b):
        distances = []
        moves = [0, -1, 1]
        random.shuffle(moves)
        for move in moves:
            distance = (999999, 999999)
            alt = b.a + move
            if alt >= 1 and alt <= self.a - 1:
                vents_a = self.vents[alt]
                delta_y = vents_a[b.y][b.x][0]
                delta_x = vents_a[b.y][b.x][1]
                print("delta: %d, %d" % (delta_y, delta_x))
                future_x = b.x + delta_x
                if future_x < 0:
                    future_x = self.c + future_x
                elif future_x >= self.c:
                    future_x = future_x - self.c
                future_y = b.y + delta_y
                if future_y >= 0 or future_y <= self.r - 1:
                    # if b.target_x >= 0:
                    #     distance = int(get_distance(future_y, future_x,
                    #                                 b.target_y, b.target_x))
                    #     #print("future: %d,%d" % (future_y, future_x))
                    #     #print("dist alt %d == %d" % (alt, distance))
                    # else:
                    #     distance = delta_y #random.randint(0, 10)

                    # distance = abs(b.id - future_y)

                    num = self.get_targets_covered_at_pos(b.y, b.x)
                    if num == 0:
                        distance = -1 * get_distance(future_y, future_x,
                                                     b.y, b.x)
                    else:
                        distance = get_distance(future_y, future_x,
                                                b.y, b.x)
                    distance = (distance, future_y)
            distances.append(distance)
        print(distances)
        index = distances.index(min(distances))
        return moves[index]

    def play_rounds(self):
        for tour in range(self.t):
            moves = []
            for i, b in enumerate(self.ballons):
                if b.lost:
                    moves.append(0)
                else:
                    if b.a == 0:
                        if tour == i * 2:
                            self.move_up(b)
                            moves.append(1)
                        else:
                            moves.append(0)
                    else:
                        best = self.get_best_move(b)
                        print("best: %d" % best)
                        if best == -1:
                            self.move_down(b)
                            moves.append(-1)
                        elif best == 1:
                            self.move_up(b)
                            moves.append(1)
                        else:
                            moves.append(0)
            self.rounds.append(moves)
            self.apply_wind()

            # re-affect targets
            # index = 0
            # for b in self.ballons:
            #     if b.target_x < 0:
            #         for i, cible in enumerate(self.cibles[index]):
            #             if cible in self.targets_covered[b.y][b.x]:
            #                 b.target_y = cible[0]
            #                 b.target_x = cible[1]
            #                 self.cibles[index].pop(i)
            #                 break
            #     index = (index + 1) % 3

            # for b in self.ballons:
            #     if b.x <= 5 and b.target_x >= 0:
            #         self.cibles[0].append((b.y, b.x))
            #         b.target_x = -1
            #         b.target_y = -1

    def get_score(self):
        score = 0
        return score


def read_file(filename):
    """Read the input file."""
    with open(filename, 'r') as fin:
        line1 = [int(num) for num in fin.readline().split()]
        line2 = [int(num) for num in fin.readline().split()]
        line3 = [int(num) for num in fin.readline().split()]
        _b = Ballons(*(line1 + line2 + line3))
        for i in range(_b.l):
            r, c = [int(num) for num in fin.readline().split()]
            _b.cibles.append((r, c))
        # vents
        for i in range(_b.a):
            grid = []
            for j in range(_b.r):
                vectors = []
                for k in range(_b.c):
                    vectors.append([0, 0])
                fline = [int(num) for num in fin.readline().split()]
                for k in range(_b.c):
                    vectors[k][0] = fline[k*2]
                    vectors[k][1] = fline[(k*2)+1]
                grid.append(vectors)
            _b.vents.append(grid)
        # ballons
        for i in range(_b.b):
            id = i
            if id >= 43:
                id = id + 10
            _b.ballons.append(Ballon(id, _b.r1, _b.c1, 0))

    return _b


def write_file(obj, filename):
    """Write output file."""
    with open(filename, 'w') as fout:
        for r in obj.rounds:
            fout.write(' '.join(['%d' % v for v in r]) + '\n')


def main():
    """Main function."""

    if len(sys.argv) < 3:
        sys.exit('Syntax: %s <filename> <output>' % sys.argv[0])

    # read input file
    ballons = read_file(sys.argv[1])

    # ballons.disperse_cibles()

    # ballons.select_ballons_targets_random()

    ballons.play_rounds()

    # write output file
    write_file(ballons, sys.argv[2])


if __name__ == '__main__':
    main()
