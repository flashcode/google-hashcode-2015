#!/usr/bin/python
#
# Google Hash Code 2015 - Qualification round (extended run)
#
# (c) 2015 Team Jambonneau
#
# Version: 12.0
#

"""Google Hash Code 2015."""

from __future__ import print_function

import sys


# pylint: disable=too-few-public-methods
class Server(object):
    """A server in the data center."""

    def __init__(self, number, size, capacity):
        self.number = number
        self.size = size
        self.capacity = capacity
        self.slot = -1
        self.row = -1
        self.pool = -1

    def __str__(self):
        return 'size: %d, cap: %d, ratio: %.02f, (%d,%d), pool=%d' % (
            self.size, self.capacity, self.ratio, self.slot, self.row,
            self.pool)

    @property
    def ratio(self):
        """Get the ratio between capacity and size (used to sort servers)."""
        return float(self.capacity) / float(self.size)


# pylint: disable=too-many-instance-attributes
class DataCenter(object):
    """The data center."""

    # pylint: disable=too-many-arguments
    def __init__(self, rows, slots, unavailable, pools, n_servers):
        self.rows = rows
        self.slots = slots
        self.unavailable = unavailable
        self.pools = pools
        self.n_servers = n_servers
        self.grid = []
        self.grid_avail = []
        self.servers = []

    def __str__(self):
        """Display a map of servers in the data center."""
        return '\n'.join(['<%s>' % ''.join(row) for row in self.grid])

    def get_best_avail_pos(self, srv, row):
        """Get best available pos for a server in a row."""
        best_slot = -1
        best_avail = -1
        for slot, avail in self.grid_avail[row]:
            if srv.size <= avail and (best_slot < 0 or avail < best_avail):
                best_slot = slot
                best_avail = avail
        return best_slot

    def get_servers_in_row(self, row):
        """Get all servers belonging to a given row."""
        srv_in_row = [srv for srv in self.servers if srv.row == row]
        return sorted(srv_in_row, key=lambda srv: srv.slot)

    def get_servers_in_slot(self, slot):
        """Get all servers belonging to a given slot."""
        srv_in_slot = [srv for srv in self.servers if srv.slot == slot]
        return sorted(srv_in_slot, key=lambda srv: srv.row)

    def get_best_server_not_used_in_row(self, row):
        """Get the server without pool and highest capacity for a row."""
        srv_in_row = [srv for srv in self.servers
                      if srv.row == row and srv.pool < 0]
        _servers = sorted(srv_in_row, key=lambda srv: srv.capacity,
                          reverse=True)
        return _servers[0] if _servers else None

    def count_servers_used(self):
        """Count the number of servers used."""
        return len([srv for srv in self.servers if srv.slot >= 0])

    def count_servers_used_without_pool(self):
        """Count the number of servers with no pool set."""
        return len([srv for srv in self.servers
                    if srv.slot >= 0 and srv.pool < 0])

    def get_list_avail_for_row(self, row):
        """Get a list of tuple (x, avail) for a given row."""
        slot = 0
        list_avail = []
        num_avail = 0
        slot_avail = -1
        while slot < self.slots:
            if self.grid[row][slot] in 'xO':
                if slot_avail >= 0:
                    list_avail.append((slot_avail, num_avail))
                num_avail = 0
                slot_avail = -1
            else:
                if slot_avail < 0:
                    slot_avail = slot
                num_avail += 1
            slot += 1
        if slot_avail >= 0:
            list_avail.append((slot_avail, num_avail))
        return list_avail

    def compute_grid_avail(self):
        """Compute available positions in grid."""
        self.grid_avail = [self.get_list_avail_for_row(y)
                           for y in range(len(self.grid))]

    def put_server(self, srv, slot, row):
        """Put a server at (slot,row)."""
        for i in range(srv.size):
            self.grid[row][slot + i] = 'O'
        self.grid_avail[row] = self.get_list_avail_for_row(row)
        srv.slot = slot
        srv.row = row

    def put_servers(self):
        """Put servers in the datacenter."""

        # basic positions (not optimized)
        # row = 0
        # for srv in self.servers:
        #     for i in range(self.rows):
        #         cur_row = (row + i) % self.rows
        #         for slot, num_avail in self.grid_avail[cur_row]:
        #             if srv.size <= num_avail:
        #                 self.put_server(srv, slot, cur_row)
        #                 break
        #         if srv.slot >= 0:
        #             break
        #     row = (row + 1) % self.rows

        # get best available position on each row
        row = 0
        for srv in self.servers:
            for i in range(self.rows):
                cur_row = (row + i) % self.rows
                best_slot = self.get_best_avail_pos(srv, cur_row)
                if best_slot >= 0:
                    self.put_server(srv, best_slot, cur_row)
                    break
            row = (row + 1) % self.rows

    def set_pools(self):
        """Set the pool for each server."""

        # set pools by row
        # pool = 0
        # for row in range(self.rows):
        #     srv_in_row = self.get_servers_in_row(row)
        #     for srv in srv_in_row:
        #         srv.pool = pool
        #         pool = (pool + 1) % self.pools

        # set pools by slot
        # pool = 0
        # for slot in range(self.slots):
        #     srv_in_slot = self.get_servers_in_slot(slot)
        #     for srv in srv_in_slot:
        #         srv.pool = pool
        #         pool = (pool + 1) % self.pools

        # set pools by row and best capacity
        # pool = 0
        # while True:
        #     for row in range(self.rows):
        #         srv = self.get_best_server_not_used_in_row(row)
        #         if srv:
        #             srv.pool = pool
        #             pool = (pool + 1) % self.pools
        #     if self.count_servers_used_without_pool() == 0:
        #         break

        # set pools by row and best capacity (2 index)
        pool = 0
        pool1 = True
        while True:
            for row in range(self.rows):
                srv = self.get_best_server_not_used_in_row(row)
                if srv:
                    srv.pool = pool if pool1 else self.pools - pool - 1
                    pool = (pool + 1) % self.pools
                    pool1 = not pool1
            if self.count_servers_used_without_pool() == 0:
                break

    def get_score(self):
        """Get score for current grid/servers."""
        min_range = []
        for row in range(self.rows):
            min_pool = [0] * self.pools
            for srv in self.servers:
                if srv.slot >= 0 and srv.row != row:
                    min_pool[srv.pool] += srv.capacity
            min_range.append(min(min_pool))
        return min(min_range)


def build_datacenter(filename):
    """Read the input file."""
    with open(filename, 'r') as dcin:
        _dc = DataCenter(*[int(num) for num in dcin.readline().split()])
        # build grid
        for i in range(_dc.rows):
            _dc.grid.append(['.'] * _dc.slots)
        # read unavailable
        for i in range(_dc.unavailable):
            line = dcin.readline()
            row, slot = [int(num) for num in line.split()]
            _dc.grid[row][slot] = 'x'
        # read servers
        for i in range(_dc.n_servers):
            line = dcin.readline()
            size, capacity = [int(num) for num in line.split()]
            _dc.servers.append(Server(i, size, capacity))

    _dc.servers = sorted(_dc.servers,
                         key=lambda srv: (srv.ratio, srv.size), reverse=True)
    _dc.compute_grid_avail()

    # put the servers
    _dc.put_servers()

    # assign a pool to each server used
    _dc.set_pools()

    return _dc


def write_servers(datacenter, filename):
    """Write output file."""
    with open(filename, 'w') as dcout:
        for srv in sorted(datacenter.servers, key=lambda x: x.number):
            if srv.slot >= 0:
                dcout.write('%d %d %d\n' % (srv.row, srv.slot, srv.pool))
            else:
                dcout.write('x\n')


def main():
    """Main function."""

    if len(sys.argv) < 3:
        sys.exit('Syntax: %s <filename> <output>' % sys.argv[0])

    # read data and initialize the data center
    dcenter = build_datacenter(sys.argv[1])

    # display some info about servers, data center and score
    print('\n'.join([str(_srv) for _srv in dcenter.servers]))
    print(dcenter)
    print('%d/%d servers used' % (dcenter.count_servers_used(),
                                  len(dcenter.servers)))
    print('--')
    print('score: %d' % dcenter.get_score())

    # write output file with position of servers
    write_servers(dcenter, sys.argv[2])


if __name__ == '__main__':
    main()
