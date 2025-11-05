# 1. Import Blueprint
from flask import Blueprint, request, jsonify, render_template_string
from collections import deque

# 2. Create Blueprint
TreeTravel_bp = Blueprint(
'TreeTravel_bp' , __name__
)
# ----------------------------
# Binary Search Tree Structure
# (Logic is unchanged)
# ----------------------------
class Node:
    def __init__(self, key):
        self.left = None
        self.right = None
        self.key = key


class BST:
    def __init__(self):
        self.root = None

    # ---------- INSERT ----------
    def insert(self, key):
        explanation = []
        if self.root is None:
            self.root = Node(key)
            explanation.append(f"Tree is empty. Inserting {key} as root node.")
            return True, explanation
        result, explanation = self._insert(self.root, key, explanation)
        return result, explanation

    def _insert(self, node, key, explanation):
        explanation.append(f"At node {node.key}.")
        if key == node.key:
            explanation.append(f"{key} already exists — skipping insertion.")
            return False, explanation
        elif key < node.key:
            explanation.append(f"{key} < {node.key}: moving LEFT.")
            if node.left:
                return self._insert(node.left, key, explanation)
            else:
                node.left = Node(key)
                explanation.append(f"Inserted {key} as LEFT child of {node.key}.")
                return True, explanation
        else:
            explanation.append(f"{key} > {node.key}: moving RIGHT.")
            if node.right:
                return self._insert(node.right, key, explanation)
            else:
                node.right = Node(key)
                explanation.append(f"Inserted {key} as RIGHT child of {node.key}.")
                return True, explanation

    # ---------- DELETE ----------
    def delete(self, key):
        explanation = []
        self.root, deleted, explanation = self._delete(self.root, key, explanation)
        return deleted, explanation

    def _delete(self, node, key, explanation):
        if not node:
            explanation.append(f"Traversal ended: {key} not found.")
            return node, False, explanation

        if key < node.key:
            explanation.append(f"{key} < {node.key}: moving LEFT subtree.")
            node.left, deleted, explanation = self._delete(node.left, key, explanation)
        elif key > node.key:
            explanation.append(f"{key} > {node.key}: moving RIGHT subtree.")
            node.right, deleted, explanation = self._delete(node.right, key, explanation)
        else:
            explanation.append(f"Node {key} found — starting deletion process.")
            deleted = True
            if not node.left:
                explanation.append(f"{key} has no LEFT child — replacing with RIGHT child.")
                return node.right, deleted, explanation
            elif not node.right:
                explanation.append(f"{key} has no RIGHT child — replacing with LEFT child.")
                return node.left, deleted, explanation
            else:
                explanation.append(f"{key} has TWO children — finding inorder successor.")
                succ = node.right
                while succ.left:
                    succ = succ.left
                explanation.append(f"Inorder successor of {key} is {succ.key}. Replacing {key} with {succ.key}.")
                node.key = succ.key
                node.right, _, explanation = self._delete(node.right, succ.key, explanation)
        return node, deleted, explanation

    # ---------- TRAVERSALS ----------
    def inorder(self):
        res, steps = [], []
        steps.append("Starting Inorder Traversal (Left → Root → Right).")
        self._inorder(self.root, res, steps)
        steps.append(f"Inorder result: {', '.join(map(str, res))}")
        return res, steps

    def _inorder(self, node, res, steps):
        if node:
            self._inorder(node.left, res, steps)
            res.append(node.key)
            steps.append(f"Visited node {node.key}.")
            self._inorder(node.right, res, steps)

    def preorder(self):
        res, steps = [], []
        steps.append("Starting Preorder Traversal (Root → Left → Right).")
        self._preorder(self.root, res, steps)
        steps.append(f"Preorder result: {', '.join(map(str, res))}")
        return res, steps

    def _preorder(self, node, res, steps):
        if node:
            res.append(node.key)
            steps.append(f"Visited node {node.key}.")
            self._preorder(node.left, res, steps)
            self._preorder(node.right, res, steps)

    def postorder(self):
        res, steps = [], []
        steps.append("Starting Postorder Traversal (Left → Right → Root).")
        self._postorder(self.root, res, steps)
        steps.append(f"Postorder result: {', '.join(map(str, res))}")
        return res, steps

    def _postorder(self, node, res, steps):
        if node:
            self._postorder(node.left, res, steps)
            self._postorder(node.right, res, steps)
            res.append(node.key)
            steps.append(f"Visited node {node.key}.")

    def bfs(self):
        res, steps = [], []
        if not self.root:
            steps.append("Tree is empty.")
            return res, steps
        steps.append("Starting Breadth-First Search (Level Order).")
        q = deque([self.root])
        while q:
            node = q.popleft()
            res.append(node.key)
            steps.append(f"Visited node {node.key}.")
            if node.left:
                steps.append(f"Enqueue LEFT child {node.left.key}.")
                q.append(node.left)
            if node.right:
                steps.append(f"Enqueue RIGHT child {node.right.key}.")
                q.append(node.right)
        steps.append(f"BFS result: {', '.join(map(str, res))}")
        return res, steps

    def dfs(self):
        res, steps = [], []
        if not self.root:
            steps.append("Tree is empty.")
            return res, steps
        steps.append("Starting Depth-First Search (using Stack, similar to Preorder).")
        stack = [self.root]
        while stack:
            node = stack.pop()
            res.append(node.key)
            steps.append(f"Visited node {node.key}.")
            if node.right:
                steps.append(f"Pushed RIGHT child {node.right.key}.")
                stack.append(node.right)
            if node.left:
                steps.append(f"Pushed LEFT child {node.left.key}.")
                stack.append(node.left)
        steps.append(f"DFS result: {', '.join(map(str, res))}")
        return res, steps

    # ---------- CONVERT TREE ----------
    def to_dict(self):
        def node_to_dict(n):
            if not n:
                return None
            d = {"name": str(n.key)}
            children = []
            if n.left:
                children.append(node_to_dict(n.left))
            if n.right:
                children.append(node_to_dict(n.right))
            if children:
                d["children"] = children
            return d
        
        # FIX: Return None for an empty tree
        if not self.root:
            return None
        return node_to_dict(self.root)


# Create global, EMPTY BST
bst = BST()
# FIX: Removed pre-population loop

# ----------------------------
# Flask Routes
# ----------------------------
HTML_PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>BST Traversal Visualizer with Explanation</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 10px; }
    input, button { padding: 6px; margin: 4px; }
    #tree { width: 100%; height: 600px; border: 1px solid #ddd; margin-top:10px; }
    #explanation { background: #f9f9f9; border: 1px solid #ccc; padding: 10px; margin-top: 10px; height: 180px; overflow-y: scroll; }
    .node circle { fill: #fff; stroke: steelblue; stroke-width: 2px; }
    .node text { font: 12px sans-serif; }
    .link { fill: none; stroke: #ccc; stroke-width: 2px; }
  </style>
</head>
<body>
  <h2>Binary Search Tree Visualizer (Insert, Delete, Traversals)</h2>
  <div>
    <input id="keyInput" type="number" placeholder="Enter key" />
    <button onclick="insertKey()">Insert</button>
    <button onclick="deleteKey()">Delete</button>
    <button onclick="traverse('inorder')">Inorder</button>
    <button onclick="traverse('preorder')">Preorder</button>
    <button onclick="traverse('postorder')">Postorder</button>
    <button onclick="traverse('bfs')">BFS</button>
    <button onclick="traverse('dfs')">DFS</button>
  </div>
  <div id="explanation">Explanation will appear here...</div>
  <div id="tree"></div>

  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script>
    // FIX: Renamed to getStatus
    async function getStatus() {
      const resp = await fetch('status');
      return await resp.json();
    }

    async function insertKey(){
      const keyInput = document.getElementById('keyInput');
      const val = keyInput.value;
      if(!val){ alert('Enter a key'); return; }
      
      const resp = await fetch('insert', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({key: parseInt(val)})});
      const res = await resp.json();
      showExplanation(res.explanation);
      refreshTree();
      
      // FIX: Clear input
      keyInput.value = "";
    }

    async function deleteKey(){
      const keyInput = document.getElementById('keyInput');
      const val = keyInput.value;
      if(!val){ alert('Enter a key'); return; }

      const resp = await fetch('delete', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({key: parseInt(val)})});
      const res = await resp.json();
      showExplanation(res.explanation);
      refreshTree();
      
      // FIX: Clear input
      keyInput.value = "";
    }

    async function traverse(type){
      const resp = await fetch(`traverse/${type}`);
      const res = await resp.json();
      showExplanation(res.steps);
      // We show the result in the explanation box now, so an alert is not needed
      // alert(`${type.toUpperCase()} Traversal: ${res.result.join(', ')}`);
    }

    function showExplanation(lines){
      const exp = document.getElementById('explanation');
      exp.innerHTML = lines.map(l => `<div>➡️ ${l}</div>`).join('');
      // Scroll to the bottom
      exp.scrollTop = exp.scrollHeight;
    }

    async function refreshTree(){
      // FIX: Fetches from getStatus
      const data = await getStatus();
      renderTree(data);
    }

    function renderTree(data){
      const container = document.getElementById('tree');
      container.innerHTML = '';
      
      // FIX: Check for null
      if(!data){
        container.innerHTML = '<p style="padding:20px; text-align:center; color:#666">Tree is empty</p>';
        return;
      }

      const width = container.clientWidth;
      const height = container.clientHeight || 600;
      const svg = d3.select('#tree').append('svg').attr('width', width).attr('height', height);
      const g = svg.append('g').attr('transform', 'translate(40,40)');
      const root = d3.hierarchy(data);
      const treeLayout = d3.tree().size([width - 80, height - 120]);
      treeLayout(root);

      g.selectAll('.link')
        .data(root.links())
        .join('path')
        .attr('class', 'link')
        .attr('d', d3.linkVertical().x(d => d.x).y(d => d.y));

      const node = g.selectAll('.node')
        .data(root.descendants())
        .join('g')
        .attr('class', 'node')
        .attr('transform', d => `translate(${d.x},${d.y})`);

      node.append('circle').attr('r', 18);
      node.append('text').attr('dy', 4).attr('text-anchor', 'middle').text(d => d.data.name);
    }

    // FIX: Use window.onload
    window.onload = refreshTree;
  </script>
</body>
</html>
"""

@TreeTravel_bp.route('/')
def index():
    return render_template_string(HTML_PAGE)

# FIX: Renamed route to /status
@TreeTravel_bp.route('/status')
def get_status():
    return jsonify(bst.to_dict())

# FIX: Added try/except
@TreeTravel_bp.route('/insert', methods=['POST'])
def insert():
    try:
        key = int(request.json['key'])
        ok, explanation = bst.insert(key)
    except ValueError:
        explanation = ["Error: Input must be an integer."]
    except Exception as e:
        explanation = [f"An error occurred: {e}"]
    return jsonify({'explanation': explanation})

# FIX: Added try/except
@TreeTravel_bp.route('/delete', methods=['POST'])
def delete():
    try:
        key = int(request.json['key'])
        deleted, explanation = bst.delete(key)
    except ValueError:
        explanation = ["Error: Input must be an integer."]
    except Exception as e:
        explanation = [f"An error occurred: {e}"]
    return jsonify({'explanation': explanation})

@TreeTravel_bp.route('/traverse/<mode>')
def traverse(mode):
    if mode == 'inorder':
        res, steps = bst.inorder()
    elif mode == 'preorder':
        res, steps = bst.preorder()
    elif mode == 'postorder':
        res, steps = bst.postorder()
    elif mode == 'bfs':
        res, steps = bst.bfs()
    elif mode == 'dfs':
        res, steps = bst.dfs()
    else:
        return jsonify({'error': 'Invalid mode', 'steps': ['Invalid traversal type selected.']})
    return jsonify({'result': res, 'steps': steps})

# FIX: REMOVED the if __name__ == '__main__' block