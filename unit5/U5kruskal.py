# 1. Import Blueprint
from flask import Blueprint, request, jsonify, render_template_string

# 2. Create Blueprint
kruskal_bp = Blueprint(
'kruskal_bp' , __name__
)

# --- Default Graph ---
DEFAULT_EDGES = "A B 4, A C 2, B C 5, B D 10, C E 3, D E 4, B E 7"

# HTML Template with visualization and input form
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Kruskal's Minimum Spanning Tree Visualizer</title>
    <style>
        body { font-family: Arial; background: #f0f4f8; text-align: center; }
        .container { margin-top: 20px; }
        canvas { border: 2px solid #333; background: #fff; margin-top: 20px; }
        input, button { padding: 10px; margin: 5px; }
        .edge-step { font-size: 16px; margin: 5px; text-align: left; }
        #steps { 
            background: #f9f9f9; border:1px solid #ccc; padding:10px; 
            margin: 10px auto; height:180px; overflow-y:scroll; 
            width: 90%; max-width: 780px; 
        }
        button:disabled { background: #ccc; cursor: not-allowed; }
    </style>
</head>
<body>
    <h1>🌳 Kruskal's Minimum Spanning Tree Visualizer</h1>
    <div class="container">
        <p>Enter edges as (u, v, weight) separated by commas.</p>
        <input type="text" id="edgesInput" size="60" placeholder="Enter graph edges">
        <button id="runButton" onclick="startKruskal()">Run Kruskal</button>
        <div id="steps"></div>
        <canvas id="graphCanvas" width="800" height="500"></canvas>
    </div>

    <script>
        const canvas = document.getElementById("graphCanvas");
        const ctx = canvas.getContext("2d");

        let positions = {};
        const radius = 20;

        function drawNode(name, x, y, color = "#66ccff") {
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, 2 * Math.PI);
            ctx.fillStyle = color;
            ctx.fill();
            ctx.strokeStyle = "#000";
            ctx.stroke();
            ctx.fillStyle = "#000";
            ctx.font = "bold 16px Arial";
            ctx.textAlign = "center";
            ctx.fillText(name, x, y + 5);
        }

        function drawEdge(u, v, w, color = "#aaa", lineWidth = 2) {
            if (!positions[u] || !positions[v]) return;
            const [x1, y1] = positions[u];
            const [x2, y2] = positions[v];
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.strokeStyle = color;
            ctx.lineWidth = lineWidth;
            ctx.stroke();
            
            // Draw weight
            ctx.fillStyle = color === '#bbb' ? '#888' : 'black';
            ctx.font = "12px Arial";
            ctx.textAlign = "center";
            ctx.save();
            ctx.translate((x1 + x2) / 2, (y1 + y2) / 2);
            ctx.rotate(Math.atan2(y2 - y1, x2 - x1));
            ctx.fillText(w, 0, -5);
            ctx.restore();
        }

        function clearCanvas() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
        
        function calculatePositions(nodesList) {
            const angleStep = (2 * Math.PI) / nodesList.length;
            const centerX = 400, centerY = 250, radiusCircle = 180;
            positions = {};
            nodesList.forEach((node, i) => {
                const angle = i * angleStep - (Math.PI / 2); // Start from top
                positions[node] = [centerX + radiusCircle * Math.cos(angle),
                                   centerY + radiusCircle * Math.sin(angle)];
            });
        }
        
        // New function to draw a static state
        function drawGraphState(nodesList, allEdges, mstEdges = [], highlightEdge = null, highlightColor = null) {
            clearCanvas();
            if (nodesList.length === 0) return;

            const mstSet = new Set(mstEdges.map(e => [e[0], e[1]].sort().join('-')));

            // Draw all edges (gray or green)
            allEdges.forEach(e => {
                let color = "#bbb";
                let edgeKey = [e[0], e[1]].sort().join('-');
                if (mstSet.has(edgeKey)) {
                    color = "#28a745"; // Green for MST
                }
                drawEdge(e[0], e[1], e[2], color, color === "#bbb" ? 2 : 3);
            });
            
            // Draw the single edge being considered
            if (highlightEdge) {
                drawEdge(highlightEdge[0], highlightEdge[1], highlightEdge[2], highlightColor, 4);
            }

            // Draw nodes
            nodesList.forEach(n => drawNode(n, positions[n][0], positions[n][1]));
        }

        async function startKruskal() {
            const input = document.getElementById("edgesInput").value.trim();
            const runButton = document.getElementById("runButton");
            const stepDiv = document.getElementById("steps");
            
            if (!input) return alert("Please enter graph edges.");
            
            runButton.disabled = true;
            stepDiv.innerHTML = "";
            
            try {
                // FIX: Renamed fetch path to 'run'
                const response = await fetch("run", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({edges: input})
                });
                
                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.error || "An unknown error occurred.");
                }
                
                const data = await response.json();
                await visualizeSteps(data);
                
            } catch (err) {
                 stepDiv.innerHTML = `<p style="color:red;"><b>Error:</b> ${err.message}</p>`;
            } finally {
                runButton.disabled = false;
            }
        }

        async function visualizeSteps(data) {
            const {nodesList, allEdges, steps} = data;
            const stepDiv = document.getElementById("steps");
            
            // Draw initial graph
            drawGraphState(nodesList, allEdges);
            stepDiv.innerHTML = '<div class="edge-step">Starting Kruskal. Edges are sorted by weight.</div>';
            await new Promise(r => setTimeout(r, 1500)); // Pause on initial graph

            for (let s of steps) {
                await new Promise(r => setTimeout(r, 1200)); // Animation speed
                
                // Redraw graph, highlighting current edge
                let highlightColor = s.status === 'accepted' ? '#28a745' : '#ff4444';
                drawGraphState(nodesList, allEdges, s.mst, s.edge, highlightColor);
                
                const msg = document.createElement("div");
                msg.className = "edge-step";
                if (s.status === 'accepted') {
                    msg.innerHTML = `✅ <b>Accept Edge:</b> (${s.edge[0]}, ${s.edge[1]}) - Weight ${s.weight}. No cycle.`;
                    msg.style.color = "green";
                } else {
                    msg.innerHTML = `❌ <b>Reject Edge:</b> (${s.edge[0]}, ${s.edge[1]}) - Weight ${s.weight}. (Forms cycle)`;
                    msg.style.color = "red";
                }
                stepDiv.appendChild(msg);
                stepDiv.scrollTop = stepDiv.scrollHeight;
            }

            const total = steps.filter(s => s.status === 'accepted').reduce((sum, s) => sum + s.weight, 0);
            const msg = document.createElement("h3");
            msg.innerHTML = "🌟 MST Complete! Total Weight = " + total;
            stepDiv.appendChild(msg);
            stepDiv.scrollTop = stepDiv.scrollHeight;
        }
        
        // FIX: Load initial graph on page load
        window.onload = async function() {
            try {
                const res = await fetch('status');
                const data = await res.json();
                document.getElementById("edgesInput").value = data.raw_edges;
                calculatePositions(data.nodesList);
                drawGraphState(data.nodesList, data.edges);
            } catch (err) {
                console.error("Error loading initial graph:", err);
                document.getElementById("steps").innerText = "Error loading initial graph.";
            }
        };
    </script>
</body>
</html>
"""

# ---- Kruskal Algorithm ----
def find(parent, i):
    if parent[i] == i:
        return i
    return find(parent, parent[i])

def union(parent, rank, x, y):
    xroot = find(parent, x)
    yroot = find(parent, y)
    if rank[xroot] < rank[yroot]:
        parent[xroot] = yroot
    elif rank[xroot] > rank[yroot]:
        parent[yroot] = xroot
    else:
        parent[yroot] = xroot
        rank[xroot] += 1

@kruskal_bp.route("/")
def home():
    return render_template_string(html_template)

# FIX: Added status route
@kruskal_bp.route("/status")
def status():
    """Returns the default graph to display on load."""
    edges_parsed = []
    nodes = set()
    try:
        for part in DEFAULT_EDGES.split(","):
            u, v, w = part.strip().split()
            w = int(w)
            edges_parsed.append((u, v, w))
            nodes.add(u)
            nodes.add(v)
    except Exception:
        pass # Default data is assumed to be valid
    
    return jsonify({
        "nodesList": sorted(list(nodes)),
        "edges": edges_parsed,
        "raw_edges": DEFAULT_EDGES
    })

# FIX: Renamed route to /run and added error handling
@kruskal_bp.route("/run", methods=["POST"])
def run_kruskal():
    try:
        data = request.get_json()
        raw_edges = data["edges"]
        edges = []
        nodes = set()

        if not raw_edges:
            return jsonify({"error": "No edges provided."}), 400

        for part in raw_edges.split(","):
            parts = part.strip().split()
            if len(parts) != 3:
                raise ValueError(f"Invalid edge format: '{part.strip()}'. Use 'U V W'.")
            u, v, w = parts
            w = int(w)
            edges.append((u, v, w))
            nodes.add(u)
            nodes.add(v)

        # Sort all edges by weight
        edges_sorted = sorted(edges, key=lambda e: e[2])
        
        parent = {}
        rank = {}
        nodes_list = sorted(list(nodes))
        for node in nodes_list:
            parent[node] = node
            rank[node] = 0

        mst = []
        steps = []
        # Go through all sorted edges
        for u, v, w in edges_sorted:
            x = find(parent, u)
            y = find(parent, v)
            if x != y:
                # Add to MST
                mst.append((u, v, w))
                union(parent, rank, x, y)
                steps.append({"edge": (u, v), "weight": w, "status": "accepted", "mst": mst.copy()})
            else:
                # FIX: Add rejected edges to steps
                steps.append({"edge": (u, v), "weight": w, "status": "rejected", "mst": mst.copy()})

        return jsonify({
            "nodesList": nodes_list,
            "allEdges": edges, # Send all original edges for drawing
            "steps": steps
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

# FIX: REMOVED the if __name__ == '__main__' block