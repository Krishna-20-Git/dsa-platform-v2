# 1. Import Blueprint
from flask import Blueprint, request, jsonify, render_template_string
import json, math

# 2. Create Blueprint
prims_bp = Blueprint(
'prims_bp' , __name__
)

# --- Default Graph ---
DEFAULT_MATRIX = """0,2,0,6,0
2,0,3,8,5
0,3,0,0,7
6,8,0,0,9
0,5,7,9,0"""

# -------------------------------
# Prim's Algorithm Implementation
# -------------------------------
def prim_mst(graph):
    n = len(graph)
    if n == 0:
        return [], [], 0
        
    selected = [False] * n
    selected[0] = True
    edges = []
    steps = []
    step_number = 1

    selected_nodes_list = [0] 

    while len(edges) < n - 1:
        minimum = math.inf
        x = y = 0
        
        for i in range(n):
            if selected[i]:
                for j in range(n):
                    if not selected[j] and graph[i][j]: 
                        if minimum > graph[i][j]:
                            minimum = graph[i][j]
                            x, y = i, j
        
        if minimum == math.inf:
            break
            
        selected[y] = True
        selected_nodes_list.append(y)
        edges.append((x, y, graph[x][y]))

        steps.append({
            "step": step_number,
            "selected_edge": (x, y, graph[x][y]),
            "selected_nodes": selected_nodes_list.copy() 
        })
        step_number += 1

    total_cost = sum(w for _, _, w in edges)
    return edges, steps, total_cost


# -------------------------------
# Flask Routes
# -------------------------------
@prims_bp.route('/')
def index():
    # Note: We must use f-strings and double-braces {{...}} to escape JS literals
    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Prim's Minimum Spanning Tree Visualization</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #eef2f3; text-align: center; padding: 20px; }}
            canvas {{ border: 2px solid #333; margin-top: 20px; background: white; }}
            textarea {{ margin: 5px; padding: 5px; width: 400px; height: 120px; }}
            button {{ padding: 8px 15px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }}
            button:hover {{ background: #45a049; }}
            button:disabled {{ background: #ccc; cursor: not-allowed; }}
            .step-info {{ background: #fff; margin: 10px auto; width: 60%; padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: left; }}
            #steps {{
                background: #f9f9f9; border:1px solid #ccc; padding:10px; 
                margin: 10px auto; height:180px; overflow-y:scroll; 
                width: 90%; max-width: 780px;
            }}
        </style>
    </head>
    <body>
        <h1>Prim's Minimum Spanning Tree (MST) Visualizer</h1>
        <p>Enter adjacency matrix (comma separated rows):</p>
        <textarea id="matrix"></textarea><br>
        <button id="runButton" onclick="computeMST()">Compute MST</button>
        <h3 id="status"></h3>
        <canvas id="graphCanvas" width="800" height="500"></canvas>
        <div id="steps"></div>

        <script>
            async function computeMST() {{
                const matrixInput = document.getElementById('matrix').value.trim();
                const runButton = document.getElementById('runButton');
                const status = document.getElementById('status');
                
                if (!matrixInput) return alert("Please enter adjacency matrix!");

                runButton.disabled = true;
                status.innerText = "Computing...";
                document.getElementById('steps').innerHTML = "";

                const rows = matrixInput.split("\\n").map(r => r.split(',').map(Number));
                
                try {{
                    const res = await fetch('run', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ graph: rows }})
                    }});
                    
                    if (!res.ok) {{
                        const err = await res.json();
                        throw new Error(err.error || "An error occurred.");
                    }}

                    const data = await res.json();
                    
                    const delay = 1000;
                    drawGraph(data.steps, rows.length, rows, delay);
                    showSteps(data.steps, data.total_cost);
                    status.innerText = "✅ MST Computed Successfully! Total Cost = " + data.total_cost;
                    
                    setTimeout(() => {{
                        runButton.disabled = false;
                    }}, delay * data.steps.length + 500);
                    
                }} catch (err) {{
                    status.innerText = `Error: ${{err.message}}`;
                    runButton.disabled = false;
                }}
            }}

            function drawStaticGraph(n, graph) {{
                const canvas = document.getElementById('graphCanvas');
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                const centerX = canvas.width / 2;
                const centerY = canvas.height / 2;
                const radius = 180;
                const nodes = [];

                for (let i = 0; i < n; i++) {{
                    const angle = (2 * Math.PI / n) * i - (Math.PI / 2);
                    const x = centerX + radius * Math.cos(angle);
                    const y = centerY + radius * Math.sin(angle);
                    nodes.push({{ x, y }});
                }}
                
                ctx.strokeStyle = '#ccc';
                ctx.lineWidth = 1;
                ctx.font = '13px Arial';
                for (let i = 0; i < n; i++) {{
                    for (let j = i + 1; j < n; j++) {{
                        if (graph[i][j] !== 0) {{
                            ctx.beginPath();
                            ctx.moveTo(nodes[i].x, nodes[i].y);
                            ctx.lineTo(nodes[j].x, nodes[j].y);
                            ctx.stroke();
                            const midX = (nodes[i].x + nodes[j].x) / 2;
                            const midY = (nodes[i].y + nodes[j].y) / 2;
                            ctx.fillStyle = "gray";
                            ctx.textAlign = "center";
                            ctx.fillText(graph[i][j], midX, midY - 5);
                        }}
                    }}
                }}
                
                ctx.fillStyle = 'black';
                ctx.font = '16px Arial';
                for (let i = 0; i < n; i++) {{
                    ctx.beginPath();
                    ctx.arc(nodes[i].x, nodes[i].y, 25, 0, 2 * Math.PI);
                    ctx.fillStyle = '#66ccff'; 
                    ctx.fill();
                    ctx.stroke();
                    ctx.fillStyle = 'black';
                    ctx.textAlign = "center";
                    ctx.fillText("V" + i, nodes[i].x, nodes[i].y + 5);
                }}
                return nodes;
            }}

            function drawGraph(steps, n, graph, delay) {{
                const nodes = drawStaticGraph(n, graph);
                
                steps.forEach((step, index) => {{
                    setTimeout(() => {{
                        const [x, y] = step.selected_edge;
                        ctx.strokeStyle = 'green';
                        ctx.lineWidth = 3;
                        ctx.beginPath();
                        ctx.moveTo(nodes[x].x, nodes[x].y);
                        ctx.lineTo(nodes[y].x, nodes[y].y);
                        ctx.stroke();

                        ctx.fillStyle = 'black';
                        ctx.font = '16px Arial';
                        for (let i = 0; i < n; i++) {{
                            ctx.beginPath();
                            ctx.arc(nodes[i].x, nodes[i].y, 25, 0, 2 * Math.PI);
                            if (step.selected_nodes.includes(i)) {{
                                ctx.fillStyle = 'lightgreen';
                            }} else {{
                                ctx.fillStyle = '#66ccff';
                            }}
                            ctx.fill();
                            ctx.stroke();
                            
                            ctx.fillStyle = 'black';
                            ctx.textAlign = "center";
                            ctx.fillText("V" + i, nodes[i].x, nodes[i].y + 5);
                        }}
                    }}, delay * (index + 1)); 
                }});
            }}

            // =================================================================
            // === THIS FUNCTION HAS BEEN UPDATED TO FIX F-STRING ERRORS ===
            // =================================================================
            function showSteps(steps, totalCost) {{
                const stepsDiv = document.getElementById('steps');
                stepsDiv.innerHTML = '<h3>Step-by-Step Process:</h3>';
                steps.forEach(st => {{
                    const div = document.createElement('div');
                    div.className = 'step-info';
                    // FIX: Use double-braces {{...}} to escape JS literals
                    div.innerHTML = `<b>Step ${{st.step}}</b>: Added Edge (V${{st.selected_edge[0]}}, V${{st.selected_edge[1]}}) ` +
                                    `with Weight ${{st.selected_edge[2]}}<br>` +
                                    `Selected Nodes: ${{st.selected_nodes.map(n => 'V'+n).join(', ')}}`;
                    stepsDiv.appendChild(div);
                }});
                const total = document.createElement('div');
                total.className = 'step-info';
                // FIX: Use double-braces {{...}}
                total.innerHTML = `<b style="font-size: 1.2em;">Total MST Cost: ${{totalCost}}</b>`;
                stepsDiv.appendChild(total);
            }}
            
            window.onload = async function() {{
                try {{
                    const res = await fetch('status');
                    const data = await res.json();
                    const matrixInput = document.getElementById('matrix');
                    matrixInput.value = data.matrix;
                    
                    const rows = data.matrix.split("\\n").map(r => r.split(',').map(Number));
                    drawStaticGraph(rows.length, rows);
                    
                    document.getElementById('status').innerText = "Default graph loaded. Ready to run.";
                }} catch (err) {{
                    console.error("Error loading initial graph:", err);
                    document.getElementById('status').innerText = "Error loading initial graph.";
                }}
            }};
        </script>
    </body>
    </html>
    """) # This is the end of the f-string

@prims_bp.route('/status')
def status():
    return jsonify({"matrix": DEFAULT_MATRIX})

@prims_bp.route('/run', methods=['POST'])
def run_prims():
    try:
        data = request.get_json()
        graph = data['graph']
        
        if not graph or not isinstance(graph, list) or len(graph) == 0:
            return jsonify({"error": "Invalid graph data provided."}), 400
        
        n = len(graph)
        for row in graph:
            if not isinstance(row, list) or len(row) != n:
                return jsonify({"error": "Graph must be a square matrix."}), 400
                
        edges, steps, total_cost = prim_mst(graph)
        return jsonify({"edges": edges, "steps": steps, "total_cost": total_cost})
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

# FIX: REMOVED the if __name__ == '__main__' block