"""
Spanning Tree Visualizer + MST explanation
Single-file Flask Spanning_bp. Generates a random weighted graph.
"""
import json
import random
from flask import Blueprint, request, jsonify, render_template_string
import networkx as nx

Spanning_bp = Blueprint(
'Spanning_bp' , __name__
)
# -------------------------
# Graph & spanning tree utilities
# -------------------------
class GraphManager:
    def __init__(self):
        self.G = None
        self.n_nodes = 8
        self.edge_prob = 0.35
        self.min_w = 1
        self.max_w = 20
        self.last_mst = None
        self.last_trees = {}

    def generate_random_graph(self, n_nodes=None, edge_prob=None):
        if n_nodes:
            self.n_nodes = n_nodes
        if edge_prob:
            self.edge_prob = edge_prob
        while True:
            G = nx.Graph()
            G.add_nodes_from(range(self.n_nodes))
            for u in range(self.n_nodes):
                for v in range(u+1, self.n_nodes):
                    if random.random() < self.edge_prob:
                        w = random.randint(self.min_w, self.max_w)
                        G.add_edge(u, v, weight=w)
            if nx.is_connected(G):
                break
        self.G = G
        self.last_mst = None
        self.last_trees.clear()
        return G

    # Kruskal MST
    def kruskal_mst_with_steps(self):
        if not self.G: self.generate_random_graph()
        G = self.G
        steps = []
        edges = sorted(G.edges(data=True), key=lambda e: (e[2]['weight'], e[0], e[1]))
        parent = {v: v for v in G.nodes()}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(a,b):
            ra, rb = find(a), find(b)
            parent[rb] = ra

        mst_edges = []
        steps.append("Kruskal's algorithm: sort all edges by weight ascending.")
        for u,v,data in edges:
            w = data['weight']
            steps.append(f"Consider edge ({u} - {v}) weight={w}.")
            if find(u) != find(v):
                union(u,v)
                mst_edges.append((u,v,w))
                steps.append(f" -> Added to MST (no cycle created).")
            else:
                steps.append(f" -> Skipped (would form a cycle).")
            if len(mst_edges) >= self.n_nodes - 1:
                break
        self.last_mst = mst_edges
        tree = nx.Graph()
        tree.add_nodes_from(G.nodes(data=True))
        for u,v,w in mst_edges:
            tree.add_edge(u,v,weight=w)
        self.last_trees['kruskal'] = {'tree': tree, 'steps': steps}
        return tree, steps

    # Prim's algorithm
    def prim_with_steps(self, start=None):
        if not self.G: self.generate_random_graph()
        G = self.G
        if start is None:
            start = random.choice(list(self.G.nodes()))
        if start not in self.G.nodes():
             start = random.choice(list(self.G.nodes()))
             
        visited = set([start])
        steps = [f"Prim's algorithm: start at node {start}."]
        edges = []
        import heapq
        heap = []
        for v in self.G.neighbors(start):
            heapq.heappush(heap, (self.G[start][v]['weight'], start, v))
            steps.append(f"Push edge ({start}-{v}) weight={self.G[start][v]['weight']} to heap.")
        mst_edges = []
        while heap and len(visited) < self.n_nodes:
            w,u,v = heapq.heappop(heap)
            steps.append(f"Pop smallest edge ({u}-{v}) weight={w}.")
            if v in visited:
                steps.append(" -> Destination already visited; skip.")
                continue
            visited.add(v)
            mst_edges.append((u,v,w))
            steps.append(f" -> Add edge ({u}-{v}) to tree; mark node {v} visited.")
            for nb in self.G.neighbors(v):
                if nb not in visited:
                    heapq.heappush(heap, (self.G[v][nb]['weight'], v, nb))
                    steps.append(f"Push edge ({v}-{nb}) weight={self.G[v][nb]['weight']} to heap.")
        tree = nx.Graph()
        tree.add_nodes_from(G.nodes(data=True))
        for u,v,w in mst_edges:
            tree.add_edge(u,v,weight=w)
        key = f"prim_start_{start}"
        self.last_trees[key] = {'tree': tree, 'steps': steps}
        return tree, steps

    # Randomized Kruskal
    def randomized_kruskal(self):
        if not self.G: self.generate_random_graph()
        G = self.G
        steps = []
        edges = list(G.edges(data=True))
        random.shuffle(edges)
        edges.sort(key=lambda e: e[2]['weight'])
        parent = {v: v for v in G.nodes()}
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(a,b):
            parent[find(b)] = find(a)
        mst_edges = []
        steps.append("Randomized Kruskal: random tie-breaking among equal-weight edges.")
        for u,v,data in edges:
            w = data['weight']
            steps.append(f"Consider edge ({u}-{v}) weight={w}.")
            if find(u) != find(v):
                union(u,v)
                mst_edges.append((u,v,w))
                steps.append(" -> Added to spanning tree.")
            else:
                steps.append(" -> Skipped (cycle).")
            if len(mst_edges) >= self.n_nodes - 1:
                break
        tree = nx.Graph()
        tree.add_nodes_from(G.nodes(data=True))
        for u,v,w in mst_edges:
            tree.add_edge(u,v,weight=w)
        key = f"randkruskal_{random.randint(0,100000)}"
        self.last_trees[key] = {'tree': tree, 'steps': steps}
        return tree, steps

    # Random DFS spanning tree
    def random_dfs_tree(self):
        if not self.G: self.generate_random_graph()
        G = self.G
        start = random.choice(list(G.nodes()))
        steps = [f"Random DFS tree starting at {start}."]
        visited = set()
        stack = [start]
        parent = {}
        visited.add(start)
        while stack:
            u = stack.pop()
            neighbors = list(G.neighbors(u))
            random.shuffle(neighbors)
            for v in neighbors:
                if v not in visited:
                    visited.add(v)
                    parent[v] = u
                    steps.append(f"Visit {v} from {u} -> add edge ({u}-{v}).")
                    stack.append(v)
        tree = nx.Graph()
        tree.add_nodes_from(G.nodes(data=True))
        for v,u in parent.items():
            w = G[v][u]['weight']
            tree.add_edge(u,v,weight=w)
        key = f"dfs_{start}"
        self.last_trees[key] = {'tree': tree, 'steps': steps}
        return tree, steps

    # Return serializable graph
    def graph_to_serializable(self, highlight_edges=None):
        G = self.G
        if not G:
            return {'nodes': [], 'edges': []}
        data = {'nodes': [], 'edges': []}
        for n in G.nodes():
            data['nodes'].append({'id': n})
        for u,v,d in G.edges(data=True):
            w = d['weight']
            is_mst = False
            if highlight_edges and ((u,v) in highlight_edges or (v,u) in highlight_edges):
                is_mst = True
            data['edges'].append({'source': u, 'target': v, 'weight': w, 'mst': is_mst})
        return data


GM = GraphManager()
GM.generate_random_graph() # Generate one graph on startup

# -------------------------
# Flask HTML frontend (D3)
# -------------------------
HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Spanning Trees & MST Visualizer</title>
  <style>
    body { font-family: Arial; margin: 10px; }
    #controls { margin-bottom: 10px; }
    input, button, select { padding:6px; margin-right:6px; }
    #graph { width:100%; height:520px; border:1px solid #ccc; }
    #explain { background:#f9f9f9; border:1px solid #ddd; padding:8px; height:180px; overflow-y:auto; margin-top:8px;}
  </style>
</head>
<body>
  <h2>Spanning Tree Generator & MST (Kruskal)</h2>
  <div id="controls">
    Nodes: <input id="n_nodes" type="number" value="8" style="width:60px">
    EdgeProb: <input id="p_edge" type="number" value="0.35" step="0.05" style="width:70px">
    <button onclick="regen()">Regenerate Graph</button>
    <button onclick="computeKruskal()">Compute MST (Kruskal)</button>
    <button onclick="computePrim()">Compute Prim (random start)</button>
    <button onclick="randKruskal()">Randomized Kruskal (different tree)</button>
    <button onclick="dfsTree()">Random DFS Tree</button>
    <select id="primStart"></select>
  </div>

  <div id="graph"></div>
  <div id="explain">Explanations will appear here.</div>

  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script>
    let graphData = null;
    let svg = null, linkg, nodeg;
    let width = 800;
    let height = 520;

    async function regen(){
      const n = parseInt(document.getElementById('n_nodes').value);
      const p = parseFloat(document.getElementById('p_edge').value);
      
      // FIX: Relative fetch path
      const resp = await fetch('generate', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({n:n, p:p})});
      const res = await resp.json();
      showExplanation(["Graph regenerated — use the buttons to compute trees."]);
      drawGraph(res.graph);
      populatePrimStarts(res.nodes);
    }

    function populatePrimStarts(nodes){
      const sel = document.getElementById('primStart');
      sel.innerHTML = '';
      nodes.forEach(n => {
        const opt = document.createElement('option'); opt.value = n; opt.text = 'start '+n; sel.appendChild(opt);
      });
    }

    function showExplanation(lines){
        const exp = document.getElementById('explain');
        exp.innerHTML = lines.map(l=>`<div>➡️ ${l}</div>`).join('');
        exp.scrollTop = exp.scrollHeight;
    }

    async function computeKruskal(){
      // FIX: Relative fetch path
      const resp = await fetch('kruskal');
      const res = await resp.json();
      showExplanation(res.steps);
      drawGraph(res.graph, res.tree_edges);
    }

    async function computePrim(){
      const start = document.getElementById('primStart').value;
      // FIX: Relative fetch path
      const resp = await fetch('prim', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({start: parseInt(start)})});
      const res = await resp.json();
      showExplanation(res.steps);
      drawGraph(res.graph, res.tree_edges);
    }

    async function randKruskal(){
      // FIX: Relative fetch path
      const resp = await fetch('randkruskal');
      const res = await resp.json();
      showExplanation(res.steps);
      drawGraph(res.graph, res.tree_edges);
    }

    async function dfsTree(){
      // FIX: Relative fetch path
      const resp = await fetch('dfstree');
      const res = await resp.json();
      showExplanation(res.steps);
      drawGraph(res.graph, res.tree_edges);
    }

    function drawGraph(data, highlight_edges = []){
      graphData = data;
      const container = d3.select('#graph'); container.html('');
      
      // FIX: Responsive width
      width = container.node().getBoundingClientRect().width;
      
      svg = container.append('svg').attr('width', width).attr('height', height);
      
      const nodes = data.nodes.map(d => ({id: d.id}));
      const links = data.edges.map(d => ({source: d.source, target: d.target, weight: d.weight, mst: d.mst}));
      
      const sim = d3.forceSimulation(nodes)
                    .force('link', d3.forceLink(links).id(d=>d.id).distance(100))
                    .force('charge', d3.forceManyBody().strength(-400))
                    .force('center', d3.forceCenter(width/2, height/2));

      linkg = svg.append('g').attr('class','links');
      nodeg = svg.append('g').attr('class','nodes');

      const link = linkg.selectAll('line').data(links).join('line')
        .attr('stroke-width', d=>2)
        .attr('stroke', d => edgeColor(d, highlight_edges));

      const wlabel = linkg.selectAll('text').data(links).join('text')
        .text(d=>d.weight)
        .attr('font-size', 10)
        .attr('fill', '#333')
        .attr('text-anchor', 'middle');

      const node = nodeg.selectAll('g').data(nodes).join('g');
      node.append('circle').attr('r',14).attr('fill','#fff').attr('stroke','steelblue').attr('stroke-width',2);
      node.append('text').text(d=>d.id).attr('dy',4).attr('text-anchor','middle');
      
      node.call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));

      sim.on('tick', () => {
        link.attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
            .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
            
        node.attr('transform', d => `translate(${d.x},${d.y})`);
        
        wlabel.attr('x', d=> (d.source.x + d.target.x)/2 )
              .attr('y', d=> (d.source.y + d.target.y)/2 - 6);
      });
      
      function dragstarted(event) {
          if (!event.active) sim.alphaTarget(0.3).restart();
          event.subject.fx = event.subject.x;
          event.subject.fy = event.subject.y;
      }
      function dragged(event) {
          event.subject.fx = event.x;
          event.subject.fy = event.y;
      }
      function dragended(event) {
          if (!event.active) sim.alphaTarget(0);
          event.subject.fx = null;
          event.subject.fy = null;
      }

      function edgeColor(d, highlight){
        for (const e of highlight || []){
          if ((e[0] == d.source.id && e[1] == d.target.id) || (e[1] == d.source.id && e[0] == d.target.id)){
            return 'red'; // Highlight color
          }
        }
        return '#999'; // Default edge color
      }
    }

    // initial load
    // FIX: Use window.onload and fetch from 'status'
    window.onload = async () => {
      try {
        const res = await fetch('status'); // Renamed from /init
        const j = await res.json();
        if (j.error) throw new Error(j.error);
        drawGraph(j.graph);
        populatePrimStarts(j.nodes);
      } catch (err) {
          console.error("Error fetching initial status:", err);
          document.getElementById('explain').innerHTML = `<p style="color:red;"><b>Error:</b> ${err.message}</p>`;
      }
    };
  </script>
</body>
</html>
"""

# -------------------------
# Flask endpoints
# -------------------------
# FIX: Renamed route to /status
@Spanning_bp.route('/status')
def status():
    try:
        if not GM.G:
            GM.generate_random_graph() # Ensure graph exists
        g = GM.G
        data = GM.graph_to_serializable()
        nodes = [n for n in g.nodes()]
        return jsonify({'graph': data, 'nodes': nodes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@Spanning_bp.route('/generate', methods=['POST'])
def generate():
    try:
        body = request.json or {}
        n = int(body.get('n', GM.n_nodes))
        p = float(body.get('p', GM.edge_prob))
        GM.generate_random_graph(n_nodes=n, edge_prob=p)
        data = GM.graph_to_serializable()
        nodes = [n for n in GM.G.nodes()]
        return jsonify({'graph': data, 'nodes': nodes})
    except ValueError:
        return jsonify({"error": "Invalid input. 'n' must be an integer and 'p' must be a float."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@Spanning_bp.route('/kruskal')
def kruskal_endpoint():
    try:
        tree, steps = GM.kruskal_mst_with_steps()
        tree_edges = [(u,v) for u,v in tree.edges()]
        graph = GM.graph_to_serializable(highlight_edges=tree_edges)
        return jsonify({'graph': graph, 'tree_edges': tree_edges, 'steps': steps})
    except Exception as e:
        return jsonify({"error": str(e), "steps": [f"An error occurred: {e}"]}), 500

@Spanning_bp.route('/prim', methods=['POST'])
def prim_endpoint():
    try:
        body = request.json or {}
        start = body.get('start', None)
        if start is not None:
            start = int(start)
        tree, steps = GM.prim_with_steps(start=start)
        tree_edges = [(u,v) for u,v in tree.edges()]
        graph = GM.graph_to_serializable(highlight_edges=tree_edges)
        return jsonify({'graph': graph, 'tree_edges': tree_edges, 'steps': steps})
    except ValueError:
        return jsonify({"error": "Invalid start node. Must be an integer."}), 400
    except Exception as e:
        return jsonify({"error": str(e), "steps": [f"An error occurred: {e}"]}), 500

@Spanning_bp.route('/randkruskal')
def randkruskal_endpoint():
    try:
        tree, steps = GM.randomized_kruskal()
        tree_edges = [(u,v) for u,v in tree.edges()]
        graph = GM.graph_to_serializable(highlight_edges=tree_edges)
        return jsonify({'graph': graph, 'tree_edges': tree_edges, 'steps': steps})
    except Exception as e:
        return jsonify({"error": str(e), "steps": [f"An error occurred: {e}"]}), 500

@Spanning_bp.route('/dfstree')
def dfstree_endpoint():
    try:
        tree, steps = GM.random_dfs_tree()
        tree_edges = [(u,v) for u,v in tree.edges()]
        graph = GM.graph_to_serializable(highlight_edges=tree_edges)
        return jsonify({'graph': graph, 'tree_edges': tree_edges, 'steps': steps})
    except Exception as e:
        return jsonify({"error": str(e), "steps": [f"An error occurred: {e}"]}), 500

# FIX: REMOVED the if __name__ == '__main__' block