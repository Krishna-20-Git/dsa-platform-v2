# 1. Import Blueprint
from flask import Blueprint, request, jsonify, render_template_string
import math

# 2. Create Blueprint
dijkstra_bp = Blueprint(
'dijkstra_bp' , __name__
)

# --- Default Graph ---
# We provide a default graph to show on page load
DEFAULT_EDGES = "A B 4, A C 2, B C 5, B D 10, C E 3, D E 4"
DEFAULT_SOURCE = "A"

# --- Helper function to parse graph ---
def parse_graph(raw_edges, source):
    edges = []
    nodes = set()
    adj = {}

    if not raw_edges:
        return list(nodes), edges, adj, {n: (0 if n == source else float("inf")) for n in nodes}

    for part in raw_edges.split(","):
        parts = part.strip().split()
        if len(parts) != 3:
            raise ValueError("Invalid edge format. Use 'U V W'.")
        u, v, w = parts
        w = int(w)
        
        edges.append((u, v, w))
        nodes.add(u)
        nodes.add(v)
        
        if u not in adj: adj[u] = []
        if v not in adj: adj[v] = []
        adj[u].append((v, w))
        adj[v].append((u, w)) # Undirected graph

    nodes = sorted(list(nodes))
    dist = {n: (0 if n == source else float("inf")) for n in nodes}
    return nodes, edges, adj, dist


# --- HTML and Visualization Template ---
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Dijkstra's Shortest Path Visualizer</title>
    <style>
        body { font-family: Arial; background: #eef3f9; text-align: center; }
        .container { margin-top: 20px; }
        canvas { border: 2px solid #333; background: #fff; margin-top: 20px; }
        input, button { padding: 10px; margin: 5px; }
        .step-info { font-size: 16px; margin: 5px; text-align: left; }
        #steps { 
            background: #f9f9f9; border:1px solid #ccc; padding:10px; 
            margin: 10px auto; height:180px; overflow-y:scroll; 
            width: 90%; max-width: 780px; 
        }
        button:disabled { background: #ccc; cursor: not-allowed; }
    </style>
</head>
<body>
    <h1>🚦 Dijkstra's Shortest Path Visualizer</h1>
    <div class="container">
        <p>Enter edges as (u, v, weight), comma-separated.</p>
        <input type="text" id="edgesInput" size="60" placeholder="Enter graph edges">
        <input type="text" id="sourceInput" size="10" placeholder="Source Node">
        <button id="runButton" onclick="runDijkstra()">Run Dijkstra</button>
        <div id="steps">Steps will appear here...</div>
        <canvas id="graphCanvas" width="800" height="500"></canvas>
    </div>

    <script>
        const canvas = document.getElementById("graphCanvas");
        const ctx = canvas.getContext("2d");
        let positions = {};
        const nodeRadius = 25; // Made nodes slightly bigger

        // FIX: Updated drawNode to show distance
        function drawNode(name, x, y, dist, color = "#66ccff", textColor = "#000") {
            ctx.beginPath();
            ctx.arc(x, y, nodeRadius, 0, 2 * Math.PI);
            ctx.fillStyle = color;
            ctx.fill();
            ctx.strokeStyle = "#000";
            ctx.stroke();
            ctx.fillStyle = textColor;
            ctx.font = "bold 14px Arial";
            ctx.textAlign = "center";
            // Show distance (inf symbol or number)
            let distText = dist === Infinity ? "∞" : dist;
            ctx.fillText(name, x, y - 5);
            ctx.font = "12px Arial";
            ctx.fillText(`(${distText})`, x, y + 15);
        }

        function drawEdge(u, v, w, color = "#bbb", lineWidth = 2) {
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
            ctx.fillStyle = "#000";
            ctx.font = "12px Arial";
            ctx.textAlign = "center";
            ctx.save();
            ctx.translate((x1 + x2) / 2, (y1 + y2) / 2);
            ctx.rotate(Math.atan2(y2 - y1, x2 - x1));
            ctx.fillStyle = color === '#bbb' ? '#888' : 'black'; // Dim weight on inactive
            ctx.fillText(w, 0, -5);
            ctx.restore();
        }
        
        function calculatePositions(nodes) {
            const angleStep = (2 * Math.PI) / nodes.length;
            const centerX = 400, centerY = 250, radiusCircle = 180;
            positions = {};
            nodes.forEach((node, i) => {
                const angle = i * angleStep - (Math.PI / 2); // Start from top
                positions[node] = [centerX + radiusCircle * Math.cos(angle),
                                   centerY + radiusCircle * Math.sin(angle)];
            });
        }
        
        // FIX: New function to draw a static graph state
        function drawGraphState(nodes, edges, distances, source) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (nodes.length === 0) return;
            
            if (Object.keys(positions).length === 0) {
                calculatePositions(nodes);
            }
            
            edges.forEach(e => drawEdge(e[0], e[1], e[2], "#ccc"));
            nodes.forEach(n => {
                let color = (n === source) ? "#FFD700" : "#66ccff"; // Highlight source
                drawNode(n, positions[n][0], positions[n][1], distances[n], color);
            });
        }

        async function runDijkstra() {
            const edges = document.getElementById("edgesInput").value.trim();
            const source = document.getElementById("sourceInput").value.trim();
            const stepDiv = document.getElementById("steps");
            const runButton = document.getElementById("runButton");
            
            if (!edges || !source) return alert("Please enter edges and a source node.");
            
            stepDiv.innerHTML = ""; // Clear previous steps
            runButton.disabled = true; // Disable button
            
            try {
                // FIX: Renamed fetch path to 'run'
                const response = await fetch("run", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({edges: edges, source: source})
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
                runButton.disabled = false; // Re-enable button
            }
        }

        async function visualizeSteps(data) {
            const {nodes, edges, steps, distances: finalDistances, source} = data;
            const stepDiv = document.getElementById("steps");
            
            // Calculate positions if not already set
            if (Object.keys(positions).length === 0) {
                 calculatePositions(nodes);
            }
            
            let currentDistances = {};
            nodes.forEach(n => currentDistances[n] = (n === source ? 0 : Infinity));
            
            // Draw initial graph
            drawGraphState(nodes, edges, currentDistances, source);
            stepDiv.innerHTML = '<div class="step-info">Starting with source node ' + source + ' (Dist = 0)</div>';
            
            let visited = new Set();
            let finalPaths = {}; // To draw the final shortest path tree

            for (let step of steps) {
                await new Promise(r => setTimeout(r, 1200)); // Animation speed
                
                currentDistances[step.v] = step.newDist;
                visited.add(step.u); // Mark the 'from' node as visited
                
                // Store the edge that formed this new shortest path
                finalPaths[step.v] = step.u;

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Redraw all edges
                edges.forEach(e => {
                    let color = "#ccc";
                    // Highlight edges in the final path tree
                    if (finalPaths[e[0]] === e[1] || finalPaths[e[1]] === e[0]) {
                        color = "#28a745"; // Green
                    }
                    drawEdge(e[0], e[1], e[2], color, color === "#ccc" ? 2 : 3);
                });
                
                // Highlight current processing edge
                drawEdge(step.u, step.v, step.weight, "#ff4444", 4);

                // Draw nodes with color coding
                nodes.forEach(n => {
                    let color = "#66ccff"; // Default
                    if (n === source) color = "#FFD700"; // Source
                    if (visited.has(n)) color = "#90ee90"; // Visited (light green)
                    if (n === step.u) color = "#ffcc00"; // Current node (yellow)
                    if (n === step.v) color = "#ff8888"; // Neighbor being updated (light red)
                    
                    drawNode(n, positions[n][0], positions[n][1], currentDistances[n], color);
                });

                // Step info
                const msg = document.createElement("div");
                msg.className = "step-info";
                msg.innerHTML = `🔹 Visit <b>${step.u}</b> (Dist=${currentDistances[step.u]}). Check neighbor <b>${step.v}</b>. <br> &nbsp;&nbsp;&nbsp; New path: ${currentDistances[step.u]} + ${step.weight} = <b>${step.newDist}</b>. Updated Dist(${step.v}).`;
                stepDiv.appendChild(msg);
                stepDiv.scrollTop = stepDiv.scrollHeight;
            }
            
            // Final draw with correct distances
            drawGraphState(nodes, edges, finalDistances, source);

            const msg = document.createElement("h3");
            msg.innerHTML = "✅ Final Shortest Distances from " + source + ": " + JSON.stringify(finalDistances);
            stepDiv.appendChild(msg);
            stepDiv.scrollTop = stepDiv.scrollHeight;
        }
        
        // FIX: Load initial graph on page load
        window.onload = async function() {
            try {
                const res = await fetch('status');
                const data = await res.json();
                document.getElementById("edgesInput").value = data.raw_edges;
                document.getElementById("sourceInput").value = data.source;
                calculatePositions(data.nodes);
                drawGraphState(data.nodes, data.edges, data.distances, data.source);
            } catch (err) {
                console.error("Error loading initial graph:", err);
                document.getElementById("steps").innerText = "Error loading initial graph.";
            }
        };
    </script>
</body>
</html>
"""

# --- Dijkstra Algorithm Backend ---
@dijkstra_bp.route("/")
def home():
    return render_template_string(html_template)

# FIX: Added status route to load default graph
@dijkstra_bp.route("/status")
def status():
    try:
        nodes, edges, adj, dists = parse_graph(DEFAULT_EDGES, DEFAULT_SOURCE)
        return jsonify({
            "nodes": nodes,
            "edges": edges,
            "distances": dists,
            "source": DEFAULT_SOURCE,
            "raw_edges": DEFAULT_EDGES
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# FIX: Renamed route to /run and added error handling
@dijkstra_bp.route("/run", methods=["POST"])
def run_dijkstra():
    try:
        data = request.get_json()
        raw_edges = data["edges"]
        source = data["source"].strip()

        if not raw_edges or not source:
            return jsonify({"error": "Edges and source node are required."}), 400

        nodes, edges, graph, dist = parse_graph(raw_edges, source)
        
        if source not in nodes:
            return jsonify({"error": f"Source node '{source}' not found in graph."}), 400

        visited = set()
        steps = []
        
        # Priority queue (min-heap) simulation using a list
        pq = [(0, source)]
        dist[source] = 0

        while pq:
            # Get node with smallest distance
            pq.sort()
            d, u = pq.pop(0)

            if u in visited:
                continue
            
            visited.add(u)
            
            if d > dist[u]:
                continue # Stale entry in priority queue

            for v, w in graph.get(u, []):
                if v not in visited and dist[u] + w < dist[v]:
                    new_dist = dist[u] + w
                    dist[v] = new_dist
                    steps.append({"u": u, "v": v, "weight": w, "newDist": new_dist})
                    pq.append((new_dist, v))
        
        # Filter out unreachable nodes from final distance dict
        final_dist = {k: (v if v != float("inf") else "∞") for k, v in dist.items()}

        return jsonify({
            "nodes": nodes,
            "edges": edges,
            "steps": steps,
            "distances": final_dist,
            "source": source
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

# FIX: REMOVED the if __name__ == '__main__' block