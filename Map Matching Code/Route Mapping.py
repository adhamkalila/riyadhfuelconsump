import json
import networkx as nx
from numpy import sin, cos, arctan2, pi, sqrt
from sys import stdout
from time import clock
from heapq import heappush, heappop

# The directory containing all of the data (expects the graph file and a 'Trips' folder)
directory = "/Users/Zeyad/Downloads/Code/"
# The directory where results of the mapping will be saved
write_directory = directory + "Results/"

# A list of files in the 'Trips' folder containing the GPS trajectories to be mapped
filenames = [ 'SampleTrips.json' ]
# The name of the  custom-format JSON file describing the NetworkX graph
graph_filename = "full roads.json"

# The maximum length of any road edge (in km). Any longer edges are segmented into a sequence of edges.
resolution = 0.01
# A list of attributes that will be evenly split between segments (any other attributes are left unchanged)
split_attributes = ['dist', 'time', 'time_AM', 'time_MD', 'time_PM', 'time_RD']


def distance(A,B):
    """Calculates the distance (in km) between two lat/long pairs (in degrees, WGS84 projection)"""
    a = sin( (A[1]-B[1])*pi/360. )**2 + cos(A[1]*pi/180.)*cos(B[1]*pi/180.)*(sin((A[0]-B[0])*pi/360.)**2)
    return 6371.*2*arctan2(sqrt(a), sqrt(1-a))

def read_graph(filename = directory+graph_filename):
    """
    Reads a custom-format JSON file used to store and generate NetworkX graphs
        graph: a NetworkX graph containing the nodes to be matched
        nodes: a list of coordinate pairs 
        N: the number of cells to construct an NxN grid of nodes (to speed up the search)
        distanceLimit: the distance (in km) for the initial search. 
                       The function usually returns a list of all nodes within this radius.
        distanceLimit2: a secondary distance limit, used if nothing is found within the previous radius.
                        In this case, the function will only return the nearest node within this radius.
        layer: used to filter nodes by their "layer" attribute to properly handle multiplex networks
    """
    roads = nx.DiGraph()
    counter, coords = 0, {}
    with open(filename, "r") as f: 
        roadsJSON = json.loads( f.read() )
        for feature in roadsJSON['features']:
            prev = None
            points0 = [ tuple(p) for p in feature['geometry']['coordinates'] ]
            for i, point in enumerate(points0):
                if point not in coords: 
                    coords[point] = counter
                    roads.add_node(counter, pos = list(point), layer = 'street')
                    counter += 1
                if i > 0: 
                    roads.add_edge(coords[prev], coords[point], feature['properties']) 
                    roads.edge[coords[prev]][coords[point]]['dist'] = distance(prev, point)
                    roads.edge[coords[prev]][coords[point]]['time'] = feature['properties']['time']/len(points0)
                prev = point[:]
    return roads


def clean_graph(graph):
    """
    Removes artificial edges (identified by the capacity 9410) and marks all edges as part of the "street" layer
        graph: a NetworkX graph to be cleaned
    """
    for e1, e2 in graph.edges():
        if 9400 <= graph.edge[e1][e2]['capacity'] <= 9410:
            graph.remove_edge(e1,e2)
        else:
            graph.edge[e1][e2]['layer'] = 'street'


def routify(path):
    """
    Given a list of nodes representing a path, returns a list of edges
        path: a list of nodes in the graph representing a path 
    """
    return [ (path[i], path[i+1]) for i in range(len(path)-1) ] 

def dijkstra(network, origin, destinations, weight):
    q = [ (0, origin, None) ]
    seen = {}
    dest = { d: False for d in destinations }
    paths = {}
    counter = 0
    while q:
        dist, current, parent = heappop(q)
        if current in dest and not dest[current]:
            path = [current]
            node = parent
            while node != None:
                path.append(node)
                node = seen[node]
            path.reverse()
            paths[current] = (dist, routify(path) )
            counter += 1
            if len(paths) == len(dest): 
                return paths
        if current in seen: continue
        seen[current] = parent
        for nextNode, edge in network[current].items():
            if nextNode in seen: continue
            heappush(q, (dist + edge[weight], nextNode, current) )
    return paths

def dijkstra2(network, origin, destinations, weight, limit):
    q = [ (0, origin, None) ]
    seen = {}
    dest = { d: False for d in destinations }
    counter = 0
    while q:
        dist, current, parent = heappop(q)
        if dist > limit:
            return dest
        if current in dest and not dest[current]:
            path = [current]
            node = parent
            while node != None:
                path.append(node)
                node = seen[node]
            path.reverse()
            dest[current] = routify(path)
            counter += 1
            if counter == len(dest): 
                return dest
        if current in seen: continue
        seen[current] = parent
        for nextNode, edge in network[current].items():
            if nextNode in seen: continue
            heappush(q, (dist + edge[weight], nextNode, current) )
    return dest


def segmentEdges(graph, edge, A, B, size, layer, edgeAttr, split = split_attributes ):
    """
    A function used by the HDNet function to segment an edge into a series of shorter edges 
    """
    bidirectional = edge[0] in graph[edge[1]]
    dist = distance(A,B)
    if dist <= size: segments = 1
    else: 
        segments = int(dist/size)
        if ((dist/size) - segments) > 0.5: segments += 1
    dx,dy = (B[0]-A[0])/segments, (B[1]-A[1])/segments
    graph.add_node( edge[0], pos = A, layer = layer )
    nodes = [ edge[0] ]
    i = 0
    for i in range(1,segments):
        nodes.append( (str(A[0]+i*dx),str(A[1]+i*dy)) )
        graph.add_node( nodes[-1], pos = ( A[0]+i*dx, A[1]+i*dy), layer = layer)
        dist2 = distance(graph.node[nodes[-2]]['pos'],graph.node[nodes[-1]]['pos'])
        graph.add_edge( nodes[-2], nodes[-1], edgeAttr)
        for weight in split:
            if weight in edgeAttr:
                graph.edge[nodes[-2]][nodes[-1]][weight] = edgeAttr[weight]*dist2/dist
        graph.edge[nodes[-2]][nodes[-1]]["index"] = i-1
        if bidirectional:
            graph.add_edge( nodes[-1], nodes[-2], edgeAttr)
            for weight in split:
                if weight in edgeAttr:
                    graph.edge[nodes[-1]][nodes[-2]][weight] = edgeAttr[weight]*dist2/dist
            graph.edge[nodes[-1]][nodes[-2]]["index"] = i-1
    graph.add_node( edge[1], pos = B, layer = layer)
    dist2 = distance(graph.node[nodes[-1]]['pos'],graph.node[edge[1]]['pos'])
    graph.add_edge( nodes[-1], edge[1], edgeAttr )
    graph.edge[nodes[-1]][edge[1]]["index"] = i
    for weight in split:
        if weight in edgeAttr:
            graph.edge[nodes[-1]][edge[1]][weight] = edgeAttr[weight]*dist2/dist
    if bidirectional:
        graph.add_edge( edge[1], nodes[-1], edgeAttr )
        for weight in split:
            if weight in edgeAttr:
                graph.edge[edge[1]][nodes[-1]][weight] = edgeAttr[weight]*dist2/dist
        graph.edge[edge[1]][nodes[-1]][weight] = i

def HDNet(graph0, size):
    """
    This function segments longer edges of a graph into a series of nodes and edges.
    This is used to ensure that the nodes are dense enough to be accurately mapped to GPS trajectories.
        graph0: the initial NetworkX graph to be segmented
        size: the maximum length of any edge. Any longer edges are segmented.
    """
    graph = nx.DiGraph()
    for n in graph0.node:
        graph.add_node(n, graph0.node[n])
    for e1, e2 in graph0.edges():
        segmentEdges(graph, (e1,e2), graph.node[e1]['pos'], graph.node[e2]['pos'], size, graph.node[e1]['layer'], graph0.edge[e1][e2])
    graph2 = nx.DiGraph()
    index = {}
    nodeCounter = 0
    for n in graph.node:
        index[n] = 'r' + str(nodeCounter)
        graph2.add_node( index[n], graph.node[n])
        nodeCounter += 1
    for e1, e2 in graph.edges():
        graph2.add_edge( index[e1], index[e2] )
        for attr in graph.edge[e1][e2]: graph2.edge[index[e1]][index[e2]][attr] = graph.edge[e1][e2][attr]  
    return graph2


def within(graph, nodes, N, distanceLimit, distanceLimit2, layer):
    """
    Identifies all the nodes in a specified layer within a given distance
        graph: a NetworkX graph containing the nodes to be matched
        nodes: a list of coordinate pairs 
        N: the number of cells to construct an NxN grid of nodes (to speed up the search)
        distanceLimit: the distance (in km) for the initial search. 
                       The function usually returns a list of all nodes within this radius.
        distanceLimit2: a secondary distance limit, used if nothing is found within the previous radius.
                        In this case, the function will only return the nearest node within this radius.
        layer: used to filter nodes by their "layer" attribute to properly handle multiplex networks
    """
    coordinates = [ (graph.node[n]['pos'][0], graph.node[n]['pos'][1], n) for n in graph.node ]
    xmin, xmax, ymin, ymax = 46.25, 47.25, 24.25, 25.25 #min(coordinates)[0], max(coordinates)[0], min(coordinates, key = lambda t: t[1])[1], max(coordinates, key = lambda t: t[1])[1] 
    dx, dy = (xmax-xmin)/N, (ymax-ymin)/N
    grid = [ [ [] for n in range(N+1) ] for m in range(N+1) ]
    for c in coordinates: grid[int((c[0]-xmin)/dx)][int((c[1]-ymin)/dy)].append(c[2])
    result = {}
    for x, y in nodes:
        i, j = int((x-xmin)/dx), int((y-ymin)/dy)
        cells = { (i+di, j+dj) for di in range(-1,2) if 0 <= i+di < len(grid) for dj in range(-1,2) if 0 <= j+dj < len(grid[0]) }
        nodes = []
        for c in cells: 
            if 0 <= c[0] < len(grid) and 0 <= c[1] < len(grid[0]): nodes += grid[c[0]][c[1]]
        closest = (float("inf"), None)
        nearby = []
        for n in nodes:
            if graph.node[n]['layer'] == layer:
                dist = distance( (x,y), graph.node[n]['pos'] ) #np.sqrt( (x-graph.node[n]['pos'][0])**2 + (y-graph.node[n]['pos'][1])**2 )
                if dist < closest[0]: 
                        closest = (dist, n)
                if dist <= distanceLimit: 
                    nearby.append((dist, n))
        if len(nearby) > 0: result[(x,y)] = nearby
        else: 
            if closest[0] <= distanceLimit2: result[(x,y)] = [ closest ]
            else: result[(x,y)] = []
    return result


def extractNodes(route, N, distanceLimit, distanceLimit2, layer):
    """
    Identifies all the nodes in a specified layer within a given distance
        route: a list describing the GPS trajectory
        N: the number of cells to construct an NxN grid of nodes (to speed up the search)
        distanceLimit: the distance (in km) for the initial search. 
                       The function usually returns a list of all nodes within this radius.
        distanceLimit2: a secondary distance limit, used if nothing is found within the previous radius.
                        In this case, the function will only return the nearest node within this radius.
        layer: used to filter nodes by their "layer" attribute to properly handle multiplex networks
    """
    points = [ r['start'] for r in route if r != None ] 
    if route[-1] != None: 
        points.append( route[-1]['end'] )
    nodes = within(graph, points, N, distanceLimit, distanceLimit2, layer)
    nodeDistance= [ { n[1]: n[0]-min(nodes[p])[0] for n in nodes[p] } for p in points ]
    nodes2 = [ set(zip(*nodes[p])[1]) if len(nodes[p])>0 else set() for p in points ]
    allNodes = []
    for nodeSet in nodes2: 
        allNodes += list(nodeSet)
    return nodeDistance, nodes2, allNodes


def pathNetwork(graph, allNodes, nodeDistance, nodes2, weight, routeLimit):
    """
    Generates a network of (simplified) possible paths through the graph using the output of the extractNodes function
        graph: a NetworkX graph that the trajectories will be mapped to
        allNodes: a list containing all the nodes that potentially match at least one GPS point 
        nodeDistance: a dictionary of candidate nodes and their distance to the matched GPS point (subtracted by the closest node)
        nodes2: a list of sets identifying which nodes were matched with each GPS point (sequentially)
        routeLimit: the maximum allowable time between subsequent points in a path.
                    If nothing is found within the limit, a gap will be left in the path.
    """
    graph2 = nx.DiGraph()
    for i, nodes in enumerate(nodes2):
        for n in nodes: 
            graph2.add_node(n, graph.node[n] )
            graph2.node[n]['original'] = True
            graph2.node[n]['counter'] = i
    gaps = [ True for n in nodes2 ]
    last = 0
    prev = set()
    for i in range(1,len(nodes2)):
        gap = True
        if len(nodes2[i]) == 0: continue 
        current, nextNodes = set(), set()
        for origin in nodes2[last]:
            path = dijkstra2(graph, origin, nodes2[i], weight, routeLimit ) 
            path2 = { key: value for key, value in path.items() if value }
            if len(path2) > 0: 
                gap = False
                current.add(origin)
                for key, edges in path2.items():
                    nextNodes.add(key)
                    for e1, e2 in edges:
                        if e1 not in graph2: 
                            graph2.add_node( e1, graph.node[e1] )
                            graph2.node[e1]['original'] = False
                            graph2.node[e1]['counter'] = last
                        if e2 not in graph2:
                            graph2.add_node( e2, graph.node[e2] )
                            graph2.node[e2]['original'] = False 
                            graph2.node[e2]['counter'] = i
                        graph2.add_edge( e1, e2, graph.edge[e1][e2] )
                        graph2.edge[e1][e2]['counter'] = last
                        if e2 in nodeDistance[i]:
                            scale = 1000. if weight == 'time' else 1.
                            graph2.edge[e1][e2][weight] += nodeDistance[i][e2]*scale
        continuous = bool( prev.intersection(current) )
        last = i
        gaps[i] = gap
        if not continuous: gaps[i] = 2 
        prev = nextNodes.copy()
    return graph2, gaps

def generatePath(graph2, gaps, nodes2, weight):
    """
    Identifies a single "best" path in the path network generated by the previous function.
    This is often the shortest path, but not always (since nodes closer to the original GPS trace are preferred)
        graph: a NetworkX graph that the trajectories will be mapped to
        gaps: a list identifying where gaps occur (these are skipped over)
        nodeDistance: a dictionary of candidate nodes and their distance to the matched GPS point (subtracted by the closest node)
        nodes2: a list of sets identifying which nodes were matched with each GPS point (sequentially)
        weight: the weight used by the Dijkstra algorithm
    """
    startIndex = 0
    for i in range(1, len(gaps)):
        if not gaps[i]:
            startIndex = i-1
            break
    finalPaths = []
    for i in range(startIndex+1,len(nodes2)):
        if gaps[i] or i+1 == len(nodes2):
            if i - startIndex > 2:
                paths = []
                for origin in nodes2[startIndex]:
                    path = dijkstra(graph2, origin, nodes2[i-1], weight)
                    if len(path) > 0:
                        paths.append( min(path.values()) )
                finalPaths.append( min(paths)[1] )
            startIndex = i
    fullPath = []
    for path in finalPaths: 
        fullPath += path
    stdout.flush()
    return fullPath

def map_routes(graph, filePath, weight = 'time', routeLimit = 145., N = 300, distanceLimit = 0.025, distanceLimit2 = 0.04, layer = 'street'):
    """
    Generates a network of (simplified) possible paths through the graph using the output of the extractNodes function
        graph: a NetworkX graph that the trajectories will be mapped to
        filePath: the path to a properly formatted file containing the GPS trajectories 
        weight: the weight used by the Dijkstra algorithm
        routeLimit: the maximum allowable time between subsequent points in a path.
                    If nothing is found within the limit, a gap will be left in the path.
        N: the number of cells to construct an NxN grid of nodes (to speed up the search)
        distanceLimit: the distance (in km) for the initial search. 
                       The function usually returns a list of all nodes within this radius.
        distanceLimit2: a secondary distance limit, used if nothing is found within the previous radius.
                        In this case, the function will only return the nearest node within this radius.
        layer: used to filter nodes by their "layer" attribute to properly handle multiplex networks
    """
    edges = {}
    failed = []
    counter = 0
    with open(filePath, 'r') as f:
        for r, line in enumerate(f):   
            if len(line) < 2: continue 
            data = json.loads(line) 
            tripID = data.keys()[0]
            route = data.values()[0]
            for i in range(len(route)):
                route[i]['start'], route[i]['end'] = tuple(route[i]['start']), tuple(route[i]['end'])
            try:
                nodeDistance, nodes2, allNodes = extractNodes(route, N, distanceLimit, distanceLimit2, layer)
                graph2, gaps = pathNetwork(graph, allNodes, nodeDistance, nodes2, weight, routeLimit)
                fullPath = generatePath(graph2, gaps, nodes2, weight)
                for j, edge in enumerate(fullPath):
                    e1, e2 = edge
                    i = graph2.edge[e1][e2]['counter']
                    info = { "speed": route[i]['speed'], "TripID": tripID, "route index": j, "GPS index": i, "time": { "pickup": route[i]['Pickup Time'], "offset(s)": route[i]['time'] } }
                    edge = str((e1,e2))
                    if edge not in edges: edges[edge] = []
                    edges[edge].append( info )
                counter += 1
            except: failed.append( tripID )
    return edges, failed, counter

G = read_graph()
clean_graph(G)
graph = HDNet( G, resolution)

for filename in filenames:
    print "Starting to map:", filename
    start = clock()
    filePath = directory + "Trips/" + filename
    edges, failed, nRoutes = map_routes( graph, filePath, 'dist', 1., distanceLimit = 0.025, distanceLimit2 = 0.04)
    time = clock()-start
    print "\tTime to map", nRoutes, "trajectories", time, "(" + str(len(failed)) + " failed)"
    
    with open(directory + "Results/" + filename, "w+") as f:
        f.write( json.dumps( edges ) )
    