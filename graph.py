from collections import deque

class NetworkGraph:
    def __init__(self):
        # nodes: { "DeviceA": {"type": "Server"}, "DeviceB": {"type": "PC"} }
        self.nodes = {}
        # edges: { "DeviceA": ["DeviceB"], "DeviceB": ["DeviceA"] }
        self.edges = {}

    def add_device(self, name, device_type):
        if name not in self.nodes:
            self.nodes[name] = {"type": device_type}
            self.edges[name] = []

    def remove_device(self, name):
        if name in self.nodes:
            # Remove all connections to this device
            for neighbor in self.edges.get(name, []):
                if name in self.edges.get(neighbor, []):
                    self.edges[neighbor].remove(name)
            
            # Remove the device itself
            del self.edges[name]
            del self.nodes[name]

    def add_connection(self, name1, name2):
        if name1 in self.nodes and name2 in self.nodes and name1 != name2:
            if name2 not in self.edges[name1]:
                self.edges[name1].append(name2)
            if name1 not in self.edges[name2]:
                self.edges[name2].append(name1)

    def remove_connection(self, name1, name2):
        if name1 in self.edges and name2 in self.edges[name1]:
            self.edges[name1].remove(name2)
        if name2 in self.edges and name1 in self.edges[name2]:
            self.edges[name2].remove(name1)

    def get_devices(self):
        return list(self.nodes.keys())
    
    def get_connections(self):
        connections = []
        visited_pairs = set()
        for u in self.edges:
            for v in self.edges[u]:
                pair = tuple(sorted((u, v)))
                if pair not in visited_pairs:
                    visited_pairs.add(pair)
                    connections.append((u, v))
        return connections

    def bfs(self, start, target=None):
        """
        Busca em Largura (Breadth-First Search).
        Retorna (caminho, ordem_visita) se um target for especificado.
        Se target for None, retorna apenas a ordem_visita.
        """
        if start not in self.nodes:
            return [], []

        visited = set([start])
        queue = deque([start])
        visit_order = []
        
        # parent dictionary para reconstruir o caminho
        parent = {start: None}
        found = False

        while queue:
            current = queue.popleft()
            visit_order.append(current)

            if target and current == target:
                found = True
                break

            for neighbor in self.edges.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        path = []
        if target and found:
            curr = target
            while curr is not None:
                path.append(curr)
                curr = parent.get(curr)
            path.reverse()
            
        return path, visit_order

    def dfs(self, start):
        """
        Busca em Profundidade (Depth-First Search).
        Retorna a ordem de visita.
        """
        if start not in self.nodes:
            return []

        visited = set()
        visit_order = []

        def dfs_recursive(node):
            if node not in visited:
                visited.add(node)
                visit_order.append(node)
                for neighbor in self.edges.get(node, []):
                    dfs_recursive(neighbor)

        dfs_recursive(start)
        return visit_order

    def connected_components(self):
        """
        Retorna o numero de componentes conectadas e uma lista das componentes 
        (onde cada componente é uma lista de nomes de nós).
        """
        visited = set()
        components = []

        for node in self.nodes:
            if node not in visited:
                # Usa BFS ou DFS para achar a componente conectada desse nó
                component = self.dfs(node)
                components.append(component)
                visited.update(component)

        return components
