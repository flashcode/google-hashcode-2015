#!/usr/bin/python
#
# Google Hash Code 2015 - Qualification round
#
# (c) 2015 Team Jambonneau
#
# Version: 4.0
#

import sys


grid = []
grid_avail = []
servers = []
r, s, u, p, m = (0, 0, 0, 0, 0)


class Server(object):

    def __init__(self, id, size, capacity):
        self.id = id
        self.size = size
        self.capacity = capacity
        self.ratio = float(self.capacity) / float(self.size)
        self.x = -1
        self.y = -1
        self.group = -1

    def __str__(self):
        return 'size: %d, cap: %d, ratio: %.02f, (%d,%d), grp=%d' % (
            self.size, self.capacity, self.ratio, self.x, self.y, self.group)


def get_servers_in_line(list_srv, y):
    srv_in_line = [srv for srv in list_srv if srv.y == y]
    return sorted(srv_in_line, key=lambda srv: srv.x)


def get_servers_in_col(list_srv, x):
    srv_in_col = [srv for srv in list_srv if srv.x == x]
    return sorted(srv_in_col, key=lambda srv: srv.y)


def get_best_server_not_used_in_line(list_srv, y):
    srv_in_line = [srv for srv in list_srv if srv.y == y and srv.group < 0]
    s = sorted(srv_in_line, key=lambda srv: srv.capacity, reverse=True)
    return s[0] if s else None


def count_servers_not_used(list_srv):
    s = [srv for srv in list_srv if srv.x >= 0 and srv.group < 0]
    return len(s)


def read_file(filename):
    global grid, servers, r, s, u, p, m
    with open(filename, 'r') as dcin:
        line = dcin.readline()
        r, s, u, p, m = [int(num) for num in line.split()]
        # build grid
        grid = []
        for i in range(r):
            grid.append(['.'] * s)
        # read unavailable
        for i in range(u):
            line = dcin.readline()
            y, x = [int(num) for num in line.split()]
            grid[y][x] = 'x'
        # read servers
        for i in range(m):
            line = dcin.readline()
            size, capacity = [int(num) for num in line.split()]
            servers.append(Server(i, size, capacity))


def print_grid():
    for line in grid:
        print('<%s>' % ''.join(line))


def print_servers(srv_list):
    for server in srv_list:
        print(server)


def get_list_avail(y):
    x = 0
    list_avail = []
    num_avail = 0
    x_avail = -1
    while x < s:
        if grid[y][x] in 'xO':
            if x_avail >= 0:
                list_avail.append((x_avail, num_avail))
            num_avail = 0
            x_avail = -1
        else:
            if x_avail < 0:
                x_avail = x
            num_avail += 1
        x += 1
    if x_avail >= 0:
        list_avail.append((x_avail, num_avail))
    return list_avail


def put_server(srv, x, y):
    global grid, grid_avail
    for i in range(srv.size):
        grid[y][x + i] = 'O'
    grid_avail[y] = get_list_avail(y)
    srv.x = x
    srv.y = y


def write_file(list_srv, filename):
    with open(filename, 'w') as dcout:
        for srv in list_srv:
            if srv.x >= 0:
                dcout.write('%d %d %d\n' % (srv.y, srv.x, srv.group))
            else:
                dcout.write('x\n')


def get_score(servers):
    min_range = []
    for y in range(r):
        min_grp = [0] * p
        for srv in servers:
            if srv.x >= 0 and srv.y != y:
                min_grp[srv.group] += srv.capacity
        min_range.append(min(min_grp))
    return min(min_range)


if __name__ == '__main__':
    read_file(sys.argv[1])

    s_servers = sorted(servers, key=lambda x: (x.ratio, x.size), reverse=True)
    print_servers(s_servers)

    grid_avail = [get_list_avail(y) for y in range(len(grid))]

    y = 0
    for srv in s_servers:
        for i in range(r):
            for x, num_avail in grid_avail[y]:
                if srv.size <= num_avail:
                    put_server(srv, x, y)
                    break
            if srv.x >= 0:
                break
        y = (y + 1) % r

    print_grid()

    print('%d servers used (on %d)' %
          ([True if srv.x >= 0 else False for srv in s_servers].count(True),
           len(s_servers)))

    grp = 0

    # by line
    # for y in range(r):
    #     srv_in_line = get_servers_in_line(s_servers, y)
    #     for srv in srv_in_line:
    #         srv.group = grp
    #         grp = (grp + 1) % p

    # by column
    # for x in range(s):
    #     srv_in_col = get_servers_in_col(s_servers, x)
    #     for srv in srv_in_col:
    #         srv.group = grp
    #         grp = (grp + 1) % p

    # by line (best capacity)
    while True:
        for y in range(r):
            srv = get_best_server_not_used_in_line(s_servers, y)
            if srv:
                srv.group = grp
                grp = (grp + 1) % p
        if count_servers_not_used(s_servers) == 0:
            break

    servers_by_id = sorted(s_servers, key=lambda x: x.id)
    write_file(servers_by_id, 'dc.out')

    print('--')
    print('score: %d' % get_score(s_servers))
