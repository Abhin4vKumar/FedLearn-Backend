import math
import random

class P2PNetwork:
    def __init__(self, max_peers_in_ring=6):
        self.max_peers_in_ring = max_peers_in_ring
        self.network = {'0': ['0']}
        self.childs = {'0': 0}
        self.guid_of_address = {"000000": '0'}
        self.address_of_guid = {"0": "000000"}
        self.peers = ['0']
        self.level = []
        self.last_node_addr = 0

    def __get_parent(self, node):
        temp = node.split(".")
        temp.pop(-1)
        par = ".".join(temp)
        if len(par) > 0:
            par += "."
        return par

    def __add_peer(self, node, addr):
        if len(self.network[node]) != self.max_peers_in_ring:
            par = self.__get_parent(node)
            new_node = par + str(len(self.network[node]))
            self.network[node].append(new_node)
            self.childs[new_node] = 0
            self.network[new_node] = self.network[node]
            self.address_of_guid[new_node] = addr
            self.guid_of_address[addr] = new_node
            return new_node
        else:
            child_num = []
            par = self.__get_parent(node)
            for i in range(self.max_peers_in_ring):
                if self.childs.get(par + str(i), 0) % self.max_peers_in_ring != 0:
                    child_num.append(-1)
                else:
                    child_num.append(self.childs.get(par + str(i), 0) // self.max_peers_in_ring)

            cur_node = par + str(child_num.index(min(child_num)))
            self.childs[cur_node] += 1
            next_node = cur_node + ".0"

            if next_node not in self.network:
                self.childs[next_node] = 0
                self.network[next_node] = [next_node]
                self.address_of_guid[next_node] = addr
                self.guid_of_address[addr] = next_node
                return next_node

            return self.__add_peer(next_node, addr)

    def __delete_all_nodes(self):
        self.__init__(self.max_peers_in_ring)

    def __remove_connections_of_a_peer(self, node):
        temp_node = ""
        for i in node:
            if i == ".":
                self.childs[temp_node] -= 1
            temp_node += i

        if len(node) > 2 and node[-2:] == ".0":
            return

        par = self.__get_parent(node)
        cur_node = par + "0"
        temp = self.network[cur_node]
        if node in temp:
            temp.remove(node)

        self.network[cur_node] = temp
        for i in temp:
            self.network[i] = self.network[cur_node]

    def __remove_peer(self, addr):
        if addr not in self.guid_of_address:
            return 0

        last_peer_guid = self.peers[-1]
        last_peer_address = self.address_of_guid[last_peer_guid]

        removed_peer_address = addr
        removed_peer_guid = self.guid_of_address[addr]

        self.__remove_connections_of_a_peer(last_peer_guid)

        self.guid_of_address[last_peer_address] = removed_peer_guid
        self.address_of_guid[removed_peer_guid] = last_peer_address

        del self.address_of_guid[last_peer_guid]
        del self.guid_of_address[removed_peer_address]
        del self.network[last_peer_guid]
        del self.childs[last_peer_guid]
        self.peers.pop(-1)

        return 1

    def __route(self, cur_node, dest_node, full_route):
        cur_node_coordinates = cur_node.split(".")
        dest_node_coordinates = dest_node.split(".")

        lr = len(cur_node_coordinates)
        ld = len(dest_node_coordinates)
        m = 0

        full_route.append(cur_node)

        for i in range(min(lr, ld)):
            if cur_node_coordinates[i] == dest_node_coordinates[i]:
                m += 1
            else:
                break

        if m <= (lr - 2) or (m == (lr - 1) and ld == (lr - 1)):
            par = self.__get_parent(cur_node)
            if len(par) > 0:
                par = par[:-1]
            self.__route(par, dest_node, full_route)
            return

        if m == lr - 1 and ld >= lr:
            next_sibling = []
            for i in range(min(lr, ld)):
                next_sibling.append(dest_node_coordinates[i])
                if cur_node_coordinates[i] != dest_node_coordinates[i]:
                    break
            next_node = ".".join(next_sibling)
            self.__route(next_node, dest_node, full_route)
            return

        if m == lr and ld == lr:
            return

        if m == lr and ld > lr:
            next_node = cur_node + "." + str(dest_node_coordinates[lr])
            self.__route(next_node, dest_node, full_route)
            return

    def __get_next_circle_points(self, center, level, point_no):
        no_of_points = self.max_peers_in_ring ** (level + 1)
        radius = level * 400 + 100
        rnd = random.uniform(0, 1) + 1
        angle = 2 * math.pi / no_of_points
        theta = angle * point_no

        x = round(radius * math.cos(theta))
        y = round(radius * math.sin(theta))
        point = [center[0] + x * rnd, center[1] + y * rnd]
        return point

    def __get_coordinates(self, peers):
        rings = {}
        for node in peers:
            par = self.__get_parent(node)
            if par not in rings:
                rings[par] = []
            rings[par].append(node)

        coordinates = {}
        for node in peers:
            cur_lvl_of_node = len(node.split(".")) - 1
            if len(self.level) == cur_lvl_of_node:
                self.level.append(0)

            next_point = self.level[cur_lvl_of_node]
            coordinates[node] = self.__get_next_circle_points([0, 0], cur_lvl_of_node, next_point)
            self.level[cur_lvl_of_node] += 1

        return coordinates

    def __create_edges(self, peers):
        edges = []
        for node in peers:
            par = self.__get_parent(node)
            if len(par) > 0:
                og_par = par[:-1]
                edges.append([og_par, node])
            for sibling in self.network[node]:
                new_edge = [min(node, sibling), max(node, sibling)]
                if new_edge not in edges:
                    edges.append(new_edge)
        return edges

    # Functions for temporary nodes
    def get_node_data(self):
        peers_nodes = self.peers
        edges = self.__create_edges(peers_nodes)
        coordinates = self.__get_coordinates(peers_nodes)
        # guid_to_address = {node: self.address_of_guid[node] for node in peers_nodes}
        return edges, coordinates
    
    def add_n_nodes(self, n):
        for _ in range(n):
            self.last_node_addr+=1
            new_node = self.__add_peer('0', str(self.last_node_addr))
            self.peers.append(new_node)
        
        return self.get_node_data()
    
    def remove_node(self,guid):
        if(len(self.peers) == 0):
            return self.get_node_data()
        addr = self.address_of_guid[guid]
        self.__remove_peer(addr)
        return self.get_node_data()
    
    def get_route(self,start_guid, dest_guid):
        route_list = []
        self.__route(start_guid,dest_guid,route_list)
        return route_list

    def get_real_node_info(self,addr):
        guid = self.guid_of_address[addr]
        temp_neighbours = self.network[guid]
        neighbours = [self.address_of_guid[i] for i in temp_neighbours]

        par = self.__get_parent(guid)
        if len(par) > 0:
            og_par = self.address_of_guid[par[:-1]]
            neighbours.append(og_par)
        #returns a list of address of neighbours
        return neighbours

    # Functions for real nodes
    def add_real_node(self):
        self.last_node_addr+=1
        addr = str(self.last_node_addr)
        guid = self.__add_peer('0',addr)
        self.peers.append(guid)
        #return new node's address and list of its neighbours
        neighbours = self.get_real_node_info(addr)
        return addr, neighbours

    def remove_real_node(self,addr):
        neighbours = self.get_real_node_info(addr)
        self.__remove_peer(addr)
        return neighbours

    def get_real_route(self,start_addr,dest_addr):
        temp_route_list = []
        self.__route(self.guid_of_address[start_addr],self.guid_of_address[dest_addr],temp_route_list)
        route_list = [self.address_of_guid[i] for i in temp_route_list]
        return route_list

