# 1. Import Blueprint instead of Flask
from flask import Blueprint, request, jsonify, render_template_string

# 2. Create a Blueprint object
doublelinked_bp = Blueprint(
    'doublelinked_bp', __name__
)

# ------------------------------
# Data Structure: Doubly Linked List
# (Logic is unchanged)
# ------------------------------

class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None
        self.addr = hex(id(self))  # Simulated memory address

class DoublyLinkedList:
    def __init__(self):
        self.head = None

    def insert(self, data):
        """Insert a new node at the end"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return f"Inserted {data} as head node"
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
        new_node.prev = current
        return f"Inserted node with value {data}"

    def delete(self, data):
        """Delete the first node with given data"""
        if not self.head:
            return "List is empty — nothing to delete."
        current = self.head
        while current and current.data != data:
            current = current.next
        if not current:
            return f"Node with value {data} not found."
        if current.prev:
            current.prev.next = current.next
        else:
            self.head = current.next
        if current.next:
            current.next.prev = current.prev
        return f"Deleted node with value {data} (addr: {current.addr})"

    def to_list(self):
        """Return structured list with data + address info"""
        result = []
        current = self.head
        while current:
            result.append({
                "data": current.data,
                "addr": current.addr,
                "prev": current.prev.addr if current.prev else None,
                "next": current.next.addr if current.next else None
            })
            current = current.next
        return result


# Create global doubly linked list instance
dll = DoublyLinkedList()

# ------------------------------
# Flask Routes
# ------------------------------

@doublelinked_bp.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Doubly Linked List Visualizer</title>
        <style>
            body { font-family: Arial; text-align: center; background: #f8fafc; margin-top: 50px; }
            input, button { padding: 8px; margin: 5px; font-size: 16px; }
            .info { font-size: 14px; color: #333; }
            
            /* --- THIS IS THE FIX --- */
            /* This div will contain our canvas and allow scrolling */
            .canvas-wrapper {
                width: 90%%; /* Or any width you prefer */
                max-width: 1600px;
                overflow-x: auto; /* Allows horizontal scrolling */
                margin: 20px auto;
                border: 2px solid #333;
                background: white;
            }
            /* --- END FIX --- */
            
            canvas { 
                /* Canvas no longer needs a border, its wrapper has one */
                margin-top: 0; 
            }
        </style>
    </head>
    <body>
        <h2>🔗 Doubly Linked List Visualization (Data on Top, Address Below)</h2>

        <div>
            <input type="text" id="nodeValue" placeholder="Enter node value">
            <button onclick="insertNode()">Insert Node</button>
            <button onclick="deleteNode()">Delete Node</button>
        </div>

        <p id="status"></p>

        <div class="canvas-wrapper">
            <canvas id="canvas" width="1600" height="500"></canvas>
        </div>

        <script>
            async function insertNode() {
                let val = document.getElementById("nodeValue").value;
                if(!val) return alert("Enter a value");
                
                let res = await fetch('insert?value=' + val);
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawList(data.list);
                
                // Clear the input box after insertion
                document.getElementById("nodeValue").value = "";
            }

            async function deleteNode() {
                let val = document.getElementById("nodeValue").value;
                if(!val) return alert("Enter a value to delete");
                let res = await fetch('delete?value=' + val);
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawList(data.list);
                
                // Clear the box after deletion
                document.getElementById("nodeValue").value = "";
            }

            // =================================================================
            // === THIS FUNCTION HAS BEEN UPDATED TO RESIZE THE CANVAS ===
            // =================================================================
            function drawList(list) {
                let canvas = document.getElementById("canvas");
                let ctx = canvas.getContext("2d");
                
                // --- THIS IS THE FIX ---
                // Calculate the required width and resize the canvas
                const nodeDrawWidth = 280; // (220 width + 60 arrow)
                const startX = 50;
                let requiredWidth = startX + (list.length * nodeDrawWidth) + 100; // Add padding
                
                // Only resize if it's wider than the default
                canvas.width = Math.max(1600, requiredWidth);
                // --- END FIX ---

                ctx.clearRect(0, 0, canvas.width, canvas.height);
                let x = 50, y = 150;

                if(list.length === 0) {
                    ctx.font = "22px Arial";
                    ctx.fillText("Doubly Linked List is empty", 600, 250);
                    return;
                }

                for(let i=0; i<list.length; i++) {
                    let node = list[i];
                    let nodeWidth = 220;
                    let nodeHeight = 100;

                    ctx.strokeStyle = "#333";
                    ctx.lineWidth = 2;
                    ctx.strokeRect(x, y, nodeWidth, nodeHeight);

                    // Dividers
                    ctx.beginPath();
                    ctx.moveTo(x + 60, y);
                    ctx.lineTo(x + 60, y + nodeHeight);
                    ctx.moveTo(x + 160, y);
                    ctx.lineTo(x + 160, y + nodeHeight);
                    ctx.stroke();

                    // Center-align Data and Main Addr
                    ctx.font = "18px Arial";
                    ctx.textAlign = "center";
                    ctx.fillText(node.data, x + 110, y + 35);
                    ctx.font = "14px Arial";
                    let shortAddr = node.addr ? "..." + node.addr.slice(-6) : "None";
                    ctx.fillText(shortAddr, x + 110, y + 65);

                    // Left-align Prev and Next pointers
                    ctx.font = "14px Arial";
                    ctx.textAlign = "left";
                    ctx.fillText("Prev", x + 5, y + 30);
                    let shortPrev = node.prev ? "..." + node.prev.slice(-4) : "None";
                    ctx.font = "13px Arial";
                    ctx.fillText(shortPrev, x + 5, y + 65);
                    ctx.font = "14px Arial";
                    ctx.fillText("Next", x + 165, y + 30);
                    let shortNext = node.next ? "..." + node.next.slice(-4) : "None";
                    ctx.font = "13px Arial";
                    ctx.fillText(shortNext, x + 165, y + 65);
                    ctx.textAlign = "left";

                    // Forward arrow (next)
                    if (i < list.length - 1) {
                        ctx.beginPath();
                        ctx.moveTo(x + nodeWidth, y + 40);
                        ctx.lineTo(x + nodeWidth + 60, y + 40);
                        ctx.strokeStyle = "#333";
                        ctx.stroke();
                        ctx.beginPath();
                        ctx.moveTo(x + nodeWidth + 60, y + 40);
                        ctx.lineTo(x + nodeWidth + 50, y + 35);
                        ctx.moveTo(x + nodeWidth + 60, y + 40);
                        ctx.lineTo(x + nodeWidth + 50, y + 45);
                        ctx.stroke();
                    }

                    // Backward arrow (prev)
                    if (i > 0) {
                        ctx.beginPath();
                        ctx.moveTo(x, y + 60);
                        ctx.lineTo(x - 60, y + 60);
                        ctx.strokeStyle = "#777";
                        ctx.stroke();
                        ctx.beginPath();
                        ctx.moveTo(x - 60, y + 60);
                        ctx.lineTo(x - 50, y + 55);
                        ctx.moveTo(x - 60, y + 60);
                        ctx.lineTo(x - 50, y + 65);
                        ctx.strokeStyle = "#777";
                        ctx.stroke();
                    }

                    x += nodeDrawWidth; // Use the fixed spacing
                    ctx.strokeStyle = "#333";
                }
            }
            
            window.onload = async function() {
                try {
                    let res = await fetch('status'); 
                    let data = await res.json();
                    document.getElementById("status").innerText = "List initialized.";
                    drawList(data.list);
                } catch (err) {
                    console.error("Error fetching initial status:", err);
                    document.getElementById("status").innerText = "Error loading list.";
                }
            };
        </script>
    </body>
    </html>
    """)


@doublelinked_bp.route('/insert')
def insert_node():
    value = request.args.get('value')
    if value:
        msg = dll.insert(value)
    else:
        msg = "No value provided."
    return jsonify({"message": msg, "list": dll.to_list()})


@doublelinked_bp.route('/delete')
def delete_node():
    value = request.args.get('value')
    if value:
        msg = dll.delete(value)
    else:
        msg = "No value provided for deletion."
    return jsonify({"message": msg, "list": dll.to_list()})

@doublelinked_bp.route('/status')
def status():
    """A new route just to get the current state of the list."""
    return jsonify({"list": dll.to_list()})