# 1. Import Blueprint
from flask import Blueprint, request, jsonify, render_template_string

# 2. Create Blueprint
stack_bp = Blueprint(
'stack_bp' , __name__
)

# ------------------------------
# Stack Data Structure
# (Logic is unchanged)
# ------------------------------

class Node:
    def __init__(self, data):
        self.data = data
        self.addr = hex(id(self))  # Simulated memory address
        self.next = None

class Stack:
    def __init__(self):
        self.top = None

    def push(self, data):
        """Push an element onto the stack"""
        new_node = Node(data)
        new_node.next = self.top
        self.top = new_node
        return f"Pushed {data} onto stack (addr: {new_node.addr})"

    def pop(self):
        """Pop the top element from the stack"""
        if not self.top:
            return "Stack Underflow — No element to pop."
        popped = self.top
        self.top = self.top.next
        return f"Popped {popped.data} from stack (addr: {popped.addr})"

    def to_list(self):
        """Return all stack elements from top to bottom"""
        result = []
        curr = self.top
        while curr:
            result.append({
                "data": curr.data,
                "addr": curr.addr,
                "next": curr.next.addr if curr.next else None
            })
            curr = curr.next
        return result


# Create global stack instance
stack = Stack()

# ------------------------------
# Flask Routes
# ------------------------------

@stack_bp.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stack Visualization</title>
        <style>
            body { font-family: Arial; text-align: center; background: #f8fafc; margin-top: 50px; }
            canvas { border: 2px solid #333; background: white; margin-top: 20px; }
            input, button { padding: 8px; margin: 5px; font-size: 16px; }
        </style>
    </head>
    <body>
        <h2>🧱 Stack Visualization (Push & Pop with Memory Addresses)</h2>

        <div>
            <input type="text" id="value" placeholder="Enter value">
            <button onclick="push()">Push</button>
            <button onclick="pop()">Pop</button>
        </div>

        <p id="status"></p>
        <canvas id="canvas" width="1000" height="600"></canvas>

        <script>
            async function push() {
                let valInput = document.getElementById("value");
                let val = valInput.value;
                if (!val) return alert("Enter a value to push");
                
                // Relative fetch path
                let res = await fetch('push?value=' + val);
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawStack(data.stack);
                
                // FIX: Clear input box
                valInput.value = "";
            }

            async function pop() {
                // Relative fetch path
                let res = await fetch('pop');
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawStack(data.stack);
            }

            function drawStack(stack) {
                let canvas = document.getElementById("canvas");
                let ctx = canvas.getContext("2d");
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                let x = 450, y = 500; // y=500 is the bottom-most position
                let boxHeight = 70;

                ctx.font = "14px Arial";
                ctx.textAlign = "center";

                if (stack.length === 0) {
                    ctx.fillText("Stack is empty", 510, 300);
                    return;
                }

                for (let i = 0; i < stack.length; i++) {
                    // stack[0] is top, stack[stack.length-1] is bottom
                    let node = stack[i];
                    let currentY = y - (i * boxHeight); // Draw from bottom up

                    // Draw stack box
                    ctx.strokeStyle = "#000";
                    ctx.lineWidth = 2;
                    ctx.strokeRect(x, currentY, 120, boxHeight);

                    // --- FIX: Truncate text ---
                    ctx.fillStyle = "#000";
                    ctx.textAlign = "left";
                    ctx.fillText("Data: " + node.data, x + 10, currentY + 25);
                    let shortAddr = node.addr ? "..." + node.addr.slice(-6) : "None";
                    ctx.fillText("Addr: " + shortAddr, x + 10, currentY + 50);
                    // --- END FIX ---

                    // Draw link (next pointer)
                    if (node.next) {
                        ctx.beginPath();
                        ctx.moveTo(x + 60, currentY); // Bottom-middle of current
                        ctx.lineTo(x + 60, currentY + boxHeight); // Top-middle of next
                        ctx.stroke();

                        // Arrowhead
                        ctx.beginPath();
                        ctx.fillStyle = "#000";
                        ctx.moveTo(x + 55, currentY + boxHeight - 10);
                        ctx.lineTo(x + 60, currentY + boxHeight);
                        ctx.lineTo(x + 65, currentY + boxHeight - 10);
                        ctx.fill(); // Use fill for a solid arrowhead
                    }
                }

                // Label top pointer
                ctx.fillStyle = "red";
                ctx.textAlign = "right";
                let topY = y - ((stack.length - 1) * boxHeight); // Y-coord of top-most box
                ctx.fillText("Top →", x - 10, topY + 35);
            }

            // Load current stack on page load
            window.onload = async function() {
                try {
                    let res = await fetch('status');
                    let data = await res.json();
                    document.getElementById("status").innerText = "Stack initialized.";
                    drawStack(data.stack);
                } catch (err) {
                    console.error("Error fetching initial status:", err);
                    document.getElementById("status").innerText = "Error loading stack.";
                }
            };
        </script>
    </body>
    </html>
    """)


@stack_bp.route('/push')
def push_value():
    value = request.args.get('value')
    msg = stack.push(value) if value else "No value provided."
    return jsonify({"message": msg, "stack": stack.to_list()})


@stack_bp.route('/pop')
def pop_value():
    msg = stack.pop()
    return jsonify({"message": msg, "stack": stack.to_list()})


@stack_bp.route('/status')
def get_status():
    return jsonify({"stack": stack.to_list()})


# ------------------------------
# Run the Server
# ------------------------------
# FIX: REMOVED the if __name__ == '__main__' block