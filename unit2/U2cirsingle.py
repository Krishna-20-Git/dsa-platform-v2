# 1. Import Blueprint instead of Flask
from flask import Blueprint, request, jsonify, render_template_string

# 2. Create a Blueprint object
cirsingle_bp = Blueprint(
    'cirsingle_bp', __name__
)

# ------------------------------
# Data Structure: Singly Circular Linked List
# (Logic is unchanged)
# ------------------------------

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.addr = hex(id(self))  # Simulated memory address


class CircularLinkedList:
    def __init__(self):
        self.head = None

    def insert(self, data):
        """Insert a new node at the end of the circular linked list"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            new_node.next = new_node  # Point to itself
            return f"Inserted {data} as head node (circular link to itself)"
        current = self.head
        while current.next != self.head:
            current = current.next
        current.next = new_node
        new_node.next = self.head
        return f"Inserted node with value {data}"

    def delete(self, data):
        """Delete the first node with given data"""
        if not self.head:
            return "List is empty — nothing to delete."
        current = self.head
        prev = None

        # Case 1: deleting head
        if current.data == data:
            # If only one node in the list
            if current.next == self.head:
                deleted_addr = current.addr
                self.head = None
                return f"Deleted the only node {data} (addr: {deleted_addr})"
            else:
                # Find last node to update its next pointer
                while current.next != self.head:
                    current = current.next
                deleted_addr = self.head.addr
                current.next = self.head.next
                self.head = self.head.next
                return f"Deleted head node {data} (addr: {deleted_addr})"

        # Case 2: deleting non-head node
        prev = self.head
        current = self.head.next
        while current != self.head:
            if current.data == data:
                prev.next = current.next
                return f"Deleted node with value {data} (addr: {current.addr})"
            prev = current
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
                "next": current.next.addr if current.next else None
            })
            current = current.next
            if current == self.head:
                break
        return result


# Create global circular linked list instance
circular_list = CircularLinkedList()

# ------------------------------
# Flask Routes
# ------------------------------

@cirsingle_bp.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Singly Circular Linked List Visualizer</title>
        <style>
            body { font-family: Arial; text-align: center; background: #f8fafc; margin-top: 50px; }
            input, button { padding: 8px; margin: 5px; font-size: 16px; }
            
            /* FIX: Added scrolling canvas wrapper */
            .canvas-wrapper {
                width: 90%%;
                max-width: 1200px;
                overflow-x: auto;
                margin: 20px auto;
                border: 2px solid #333;
                background: white;
            }
            canvas { margin-top: 0; }
        </style>
    </head>
    <body>
        <h2>🔄 Singly Circular Linked List Visualization (Insert & Delete with Addresses)</h2>

        <div>
            <input type="text" id="nodeValue" placeholder="Enter node value">
            <button onclick="insertNode()">Insert Node</button>
            <button onclick="deleteNode()">Delete Node</button>
        </div>

        <p id="status"></p>
        
        <div class="canvas-wrapper">
            <canvas id="canvas" width="1200" height="450"></canvas>
        </div>

        <script>
            async function insertNode() {
                let val = document.getElementById("nodeValue").value;
                if(!val) return alert("Enter a value");
                let res = await fetch('insert?value=' + val);
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawList(data.list);
                
                // FIX: Clear input box
                document.getElementById("nodeValue").value = "";
            }

            async function deleteNode() {
                let val = document.getElementById("nodeValue").value;
                if(!val) return alert("Enter a value to delete");
                let res = await fetch('delete?value=' + val);
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawList(data.list);
                
                // FIX: Clear input box
                document.getElementById("nodeValue").value = "";
            }

            function drawList(list) {
                let canvas = document.getElementById("canvas");
                let ctx = canvas.getContext("2d");
                
                const nodeWidth = 170;
                const nodeSpacing = 220; // (170 width + 50 gap)
                const headX = 60;
                
                // FIX: Dynamically resize canvas
                let requiredWidth = headX + (list.length * nodeSpacing) + 100;
                canvas.width = Math.max(1200, requiredWidth);

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                if(list.length === 0) {
                    ctx.font = "20px Arial";
                    ctx.fillText("Circular Linked List is empty", 400, 200);
                    return;
                }

                let x = headX, y = 150;
                const nodeHeight = 100;

                for(let i=0; i<list.length; i++) {
                    let node = list[i];

                    ctx.strokeStyle = "#333";
                    ctx.lineWidth = 2;
                    ctx.strokeRect(x, y, nodeWidth, nodeHeight);

                    ctx.beginPath();
                    ctx.moveTo(x + 120, y);
                    ctx.lineTo(x + 120, y + nodeHeight);
                    ctx.stroke();

                    // Text with truncation
                    ctx.font = "14px Arial";
                    ctx.textAlign = "left";
                    ctx.fillText("Data: " + node.data, x + 10, y + 30);
                    
                    ctx.font = "13px Arial";
                    let shortAddr = node.addr ? "..." + node.addr.slice(-6) : "None";
                    ctx.fillText("Addr: " + shortAddr, x + 10, y + 65);
                    
                    ctx.font = "12px Arial";
                    ctx.fillText("Next →", x + 125, y + 30);
                    
                    let shortNext = node.next ? "..." + node.next.slice(-6) : "None";
                    ctx.fillText(shortNext, x + 125, y + 65);

                    if (i < list.length - 1) {
                        // Straight arrow
                        ctx.beginPath();
                        ctx.moveTo(x + nodeWidth, y + 50);
                        ctx.lineTo(x + nodeSpacing, y + 50);
                        ctx.stroke();
                        ctx.beginPath();
                        ctx.moveTo(x + nodeSpacing, y + 50);
                        ctx.lineTo(x + nodeSpacing - 10, y + 45);
                        ctx.moveTo(x + nodeSpacing, y + 50);
                        ctx.lineTo(x + nodeSpacing - 10, y + 55);
                        ctx.stroke();
                    } else {
                        // Circular arc
                        let startX = x + nodeWidth;
                        let startY = y + 50;
                        let endX = headX;
                        let endY = y + 50;
                        let arcHeight = Math.max(80, list.length * 10);

                        ctx.beginPath();
                        ctx.moveTo(startX, startY);
                        ctx.bezierCurveTo(
                            startX, startY - arcHeight,
                            endX, endY - arcHeight,
                            endX, endY
                        );
                        ctx.stroke();
                        
                        ctx.beginPath();
                        ctx.moveTo(endX, endY);
                        ctx.lineTo(endX + 10, endY - 5);
                        ctx.moveTo(endX, endY);
                        ctx.lineTo(endX + 10, endY + 5);
                        ctx.stroke();
                    }
                    x += nodeSpacing;
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

@cirsingle_bp.route('/insert')
def insert_node():
    value = request.args.get('value')
    if value:
        msg = circular_list.insert(value)
    else:
        msg = "No value provided."
    return jsonify({"message": msg, "list": circular_list.to_list()})

@cirsingle_bp.route('/delete')
def delete_node():
    value = request.args.get('value')
    if value:
        msg = circular_list.delete(value)
    else:
        msg = "No value provided for deletion."
    return jsonify({"message": msg, "list": circular_list.to_list()})

@cirsingle_bp.route('/status')
def status():
    """A new route just to get the current state of the list."""
    return jsonify({"list": circular_list.to_list()})