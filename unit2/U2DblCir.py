# 1. Import Blueprint instead of Flask
from flask import Blueprint, request, jsonify, render_template_string

# 2. Create a Blueprint object
dblcir_bp = Blueprint(
    'dblcir_bp', __name__
)

# ------------------------------
# Data Structure: Doubly Circular Linked List
# (Logic is unchanged)
# ------------------------------

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None
        self.addr = hex(id(self))  # Simulated memory address


class DoublyCircularLinkedList:
    def __init__(self):
        self.head = None

    def insert(self, data):
        """Insert a new node at the end of the circular doubly linked list"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            new_node.next = new_node
            new_node.prev = new_node
            return f"Inserted {data} as head node (circular doubly linked)"
        current = self.head
        while current.next != self.head:
            current = current.next
        current.next = new_node
        new_node.prev = current
        new_node.next = self.head
        self.head.prev = new_node
        return f"Inserted node with value {data}"

    def delete(self, data):
        """Delete a node by value"""
        if not self.head:
            return "List is empty — nothing to delete."
        current = self.head

        # Case 1: deleting head
        if current.data == data:
            if current.next == self.head:
                deleted_addr = current.addr
                self.head = None
                return f"Deleted the only node {data} (addr: {deleted_addr})"
            else:
                deleted_addr = current.addr
                tail = self.head.prev
                self.head = self.head.next
                self.head.prev = tail
                tail.next = self.head
                return f"Deleted head node {data} (addr: {deleted_addr})"

        # Case 2: deleting non-head
        current = self.head.next
        while current != self.head:
            if current.data == data:
                current.prev.next = current.next
                current.next.prev = current.prev
                return f"Deleted node with value {data} (addr: {current.addr})"
            current = current.next
        return f"Node with value {data} not found."

    def to_list(self):
        """Return structured list with data + address info"""
        result = []
        if not self.head:
            return result
        current = self.head
        while True:
            result.append({
                "data": current.data,
                "addr": current.addr,
                "next": current.next.addr if current.next else None,
                "prev": current.prev.addr if current.prev else None
            })
            current = current.next
            if current == self.head:
                break
        return result


# Create global circular doubly linked list instance
dll = DoublyCircularLinkedList()

# ------------------------------
# Flask Routes
# ------------------------------

@dblcir_bp.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Doubly Circular Linked List Visualizer</title>
        <style>
            body { font-family: Arial; text-align: center; background: #f8fafc; margin-top: 50px; }
            input, button { padding: 8px; margin: 5px; font-size: 16px; }
            
            /* FIX: Added scrolling canvas wrapper */
            .canvas-wrapper {
                width: 90%%;
                max-width: 1400px;
                overflow-x: auto;
                margin: 20px auto;
                border: 2px solid #333;
                background: white;
            }
            canvas { margin-top: 0; }
        </style>
    </head>
    <body>
        <h2>🔁 Doubly Circular Linked List Visualization (Insert & Delete with Addresses)</h2>

        <div>
            <input type="text" id="nodeValue" placeholder="Enter node value">
            <button onclick="insertNode()">Insert Node</button>
            <button onclick="deleteNode()">Delete Node</button>
        </div>

        <p id="status"></p>
        
        <div class="canvas-wrapper">
            <canvas id="canvas" width="1400" height="500"></canvas>
        </div>

        <script>
            async function insertNode() {
                let valInput = document.getElementById("nodeValue");
                let val = valInput.value;
                if(!val) return alert("Enter a value");
                
                let res = await fetch('insert?value=' + val);
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawList(data.list);
                
                // FIX: Clear input
                valInput.value = "";
            }

            async function deleteNode() {
                let valInput = document.getElementById("nodeValue");
                let val = valInput.value;
                if(!val) return alert("Enter a value to delete");
                
                let res = await fetch('delete?value=' + val);
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawList(data.list);
                
                // FIX: Clear input
                valInput.value = "";
            }

            function drawList(list) {
                let canvas = document.getElementById("canvas");
                let ctx = canvas.getContext("2d");
                
                const nodeWidth = 200;
                const nodeSpacing = 250; // (200 width + 50 gap)
                const headX = 60;
                
                // FIX: Dynamically resize canvas
                let requiredWidth = headX + (list.length * nodeSpacing) + 100;
                canvas.width = Math.max(1400, requiredWidth);

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                if(list.length === 0) {
                    ctx.font = "20px Arial";
                    ctx.textAlign = "center";
                    ctx.fillText("Doubly Circular Linked List is empty", canvas.width / 2, 250);
                    return;
                }

                let x = headX, y = 180;

                for(let i=0; i<list.length; i++) {
                    let node = list[i];
                    let nodeHeight = 100;

                    ctx.strokeStyle = "#333";
                    ctx.lineWidth = 2;
                    ctx.strokeRect(x, y, nodeWidth, nodeHeight);

                    // Dividers
                    ctx.beginPath();
                    ctx.moveTo(x + 60, y);
                    ctx.lineTo(x + 60, y + 100);
                    ctx.moveTo(x + 140, y);
                    ctx.lineTo(x + 140, y + 100);
                    ctx.stroke();

                    // --- Text Fixes ---
                    ctx.font = "14px Arial";
                    ctx.textAlign = "center";
                    ctx.fillStyle = "#000";
                    ctx.fillText("Data: " + node.data, x + 100, y + 35);
                    
                    let shortAddr = node.addr ? "..." + node.addr.slice(-6) : "None";
                    ctx.font = "13px Arial";
                    ctx.fillText("Addr: " + shortAddr, x + 100, y + 70);

                    ctx.font = "11px Arial";
                    ctx.textAlign = "left"; 
                    
                    ctx.fillText("Prev", x + 5, y + 25);
                    let shortPrev = node.prev ? "..." + node.prev.slice(-4) : "None";
                    ctx.fillText(shortPrev, x + 5, y + 70);
                    
                    ctx.fillText("Next", x + 145, y + 25);
                    let shortNext = node.next ? "..." + node.next.slice(-4) : "None";
                    ctx.fillText(shortNext, x + 145, y + 70);
                    // --- End Text Fixes ---
                    
                    ctx.textAlign = "left";

                    // Forward arrow (next)
                    if (i < list.length - 1) {
                        ctx.beginPath();
                        ctx.moveTo(x + 200, y + 40); // Top arrow
                        ctx.lineTo(x + 240, y + 40);
                        ctx.stroke();
                        ctx.beginPath();
                        ctx.moveTo(x + 240, y + 40);
                        ctx.lineTo(x + 230, y + 35);
                        ctx.moveTo(x + 240, y + 40);
                        ctx.lineTo(x + 230, y + 45);
                        ctx.stroke();

                        // Backward arrow (prev)
                        ctx.beginPath();
                        ctx.moveTo(x + 240, y + 60); // Bottom arrow
                        ctx.lineTo(x + 200, y + 60);
                        ctx.stroke();
                        ctx.beginPath();
                        ctx.moveTo(x + 200, y + 60);
                        ctx.lineTo(x + 210, y + 55);
                        ctx.moveTo(x + 200, y + 60);
                        ctx.lineTo(x + 210, y + 65);
                        ctx.stroke();
                    } else {
                        // Circular Arrows
                        let startX = x + nodeWidth;
                        let endX = headX;
                        let arcHeight = Math.max(80, list.length * 10);
                        
                        ctx.beginPath();
                        ctx.moveTo(startX, y + 40); // Top
                        ctx.bezierCurveTo(startX + 50, y + 40 - arcHeight, endX - 50, y + 40 - arcHeight, endX, y + 40);
                        ctx.stroke();
                        ctx.beginPath();
                        ctx.moveTo(endX, y + 40);
                        ctx.lineTo(endX + 10, y + 35);
                        ctx.moveTo(endX, y + 40);
                        ctx.lineTo(endX + 10, y + 45);
                        ctx.stroke();

                        ctx.beginPath();
                        ctx.moveTo(endX, y + 60); // Bottom
                        ctx.bezierCurveTo(endX - 50, y + 60 + arcHeight, startX + 50, y + 60 + arcHeight, startX, y + 60);
                        ctx.stroke();
                        ctx.beginPath();
                        ctx.moveTo(startX, y + 60);
                        ctx.lineTo(startX - 10, y + 55);
                        ctx.moveTo(startX, y + 60);
                        ctx.lineTo(startX - 10, y + 65);
                        ctx.stroke();
                    }

                    x += nodeSpacing;
                }
            }
            
            // FIX: Load status on window load
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

@dblcir_bp.route('/insert')
def insert_node():
    value = request.args.get('value')
    if value:
        msg = dll.insert(value)
    else:
        msg = "No value provided."
    return jsonify({"message": msg, "list": dll.to_list()})

@dblcir_bp.route('/delete')
def delete_node():
    value = request.args.get('value')
    if value:
        msg = dll.delete(value)
    else:
        msg = "No value provided for deletion."
    return jsonify({"message": msg, "list": dll.to_list()})

# FIX: Added status route
@dblcir_bp.route('/status')
def status():
    """A new route just to get the current state of the list."""
    return jsonify({"list": dll.to_list()})