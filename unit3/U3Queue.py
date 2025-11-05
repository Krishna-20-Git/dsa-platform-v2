# 1. Import Blueprint
from flask import Blueprint, request, jsonify, render_template_string

# 2. Create Blueprint (Keeping your uppercase 'Queue_bp')
Queue_bp = Blueprint(
    'Queue_bp', __name__
)
# ------------------------------
# Queue Data Structure
# (Logic is unchanged)
# ------------------------------

class Node:
    def __init__(self, data):
        self.data = data
        self.addr = hex(id(self))  # simulated memory address
        self.next = None

class Queue:
    def __init__(self):
        self.front = None
        self.rear = None

    def enqueue(self, data):
        """Add an element to the rear of the queue"""
        new_node = Node(data)
        if self.rear is None:
            self.front = self.rear = new_node
            return f"Enqueued {data} as the first node (addr: {new_node.addr})"
        self.rear.next = new_node
        self.rear = new_node
        return f"Enqueued {data} at rear (addr: {new_node.addr})"

    def dequeue(self):
        """Remove an element from the front of the queue"""
        if self.front is None:
            return "Queue Underflow — No element to dequeue."
        removed_node = self.front
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        return f"Dequeued {removed_node.data} (addr: {removed_node.addr})"

    def to_list(self):
        """Return all queue elements as list of dicts"""
        result = []
        curr = self.front
        while curr:
            result.append({
                "data": curr.data,
                "addr": curr.addr,
                "next": curr.next.addr if curr.next else None
            })
            curr = curr.next
        return result


# Create global queue instance
queue = Queue()

# ------------------------------
# Flask Routes
# (Using 'Queue_bp' as requested)
# ------------------------------

@Queue_bp.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Queue Visualization</title>
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
        <h2>📦 Queue Visualization (Enqueue & Dequeue with Front and Rear)</h2>

        <div>
            <input type="text" id="value" placeholder="Enter value">
            <button onclick="enqueue()">Enqueue</button>
            <button onclick="dequeue()">Dequeue</button>
        </div>

        <p id="status"></p>
        
        <div class="canvas-wrapper">
            <canvas id="canvas" width="1200" height="500"></canvas>
        </div>

        <script>
            async function enqueue() {
                let valInput = document.getElementById("value");
                let val = valInput.value;
                if (!val) return alert("Enter a value to enqueue");
                
                // Relative fetch path
                let res = await fetch('enqueue?value=' + val);
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawQueue(data.queue);
                
                // FIX: Clear input box
                valInput.value = "";
            }

            async function dequeue() {
                // Relative fetch path
                let res = await fetch('dequeue');
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawQueue(data.queue);
            }

            function drawQueue(queue) {
                let canvas = document.getElementById("canvas");
                let ctx = canvas.getContext("2d");
                
                const boxWidth = 150, boxHeight = 80;
                const boxSpacing = 40;
                const startX = 150;

                // FIX: Dynamically resize canvas
                let requiredWidth = startX + (queue.length * (boxWidth + boxSpacing)) + 200; // Padding
                canvas.width = Math.max(1200, requiredWidth);

                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.textAlign = "left"; // Reset alignment

                if (queue.length === 0) {
                    ctx.font = "20px Arial";
                    ctx.textAlign = "center";
                    ctx.fillText("Queue is empty", canvas.width / 2, 250);
                    return;
                }

                let x = startX, y = 200;

                ctx.font = "14px Arial";

                for (let i = 0; i < queue.length; i++) {
                    let node = queue[i];

                    // Draw node box
                    ctx.strokeStyle = "#000";
                    ctx.lineWidth = 2;
                    ctx.strokeRect(x, y, boxWidth, boxHeight);

                    // --- FIX: Truncate text ---
                    ctx.fillStyle = "#000";
                    ctx.fillText("Data: " + node.data, x + 15, y + 30);
                    let shortAddr = node.addr ? "..." + node.addr.slice(-6) : "None";
                    ctx.fillText("Addr: " + shortAddr, x + 15, y + 55);
                    // --- END FIX ---

                    // Draw arrow to next node
                    if (i < queue.length - 1) {
                        ctx.beginPath();
                        ctx.moveTo(x + boxWidth, y + boxHeight / 2);
                        ctx.lineTo(x + boxWidth + 30, y + boxHeight / 2);
                        ctx.stroke();

                        // Arrowhead
                        ctx.beginPath();
                        ctx.fillStyle = "#000";
                        ctx.moveTo(x + boxWidth + 30, y + boxHeight / 2);
                        ctx.lineTo(x + boxWidth + 20, y + boxHeight / 2 - 5);
                        ctx.lineTo(x + boxWidth + 20, y + boxHeight / 2 + 5);
                        ctx.fill();
                    }

                    x += boxWidth + boxSpacing;
                }

                // Draw Front and Rear labels
                ctx.fillStyle = "red";
                ctx.font = "16px Arial";
                ctx.textAlign = "center";
                // Point to the middle of the first box
                ctx.fillText("↑", startX + boxWidth / 2, y - 10);
                ctx.fillText("Front", startX + boxWidth / 2, y - 30);
                
                // Point to the middle of the last box
                let lastBoxX = startX + (queue.length - 1) * (boxWidth + boxSpacing);
                ctx.fillStyle = "blue";
                ctx.fillText("↑", lastBoxX + boxWidth / 2, y + boxHeight + 40);
                ctx.fillText("Rear", lastBoxX + boxWidth / 2, y + boxHeight + 20);
            }

            // Load initial queue state
            window.onload = async function() {
                // Relative fetch path
                let res = await fetch('status');
                let data = await res.json();
                drawQueue(data.queue);
            };
        </script>
    </body>
    </html>
    """)


@Queue_bp.route('/enqueue')
def enqueue_value():
    value = request.args.get('value')
    msg = queue.enqueue(value) if value else "No value provided."
    return jsonify({"message": msg, "queue": queue.to_list()})


@Queue_bp.route('/dequeue')
def dequeue_value():
    msg = queue.dequeue()
    return jsonify({"message": msg, "queue": queue.to_list()})


@Queue_bp.route('/status')
def get_status():
    return jsonify({"queue": queue.to_list()})


# ------------------------------
# Run Server
# ------------------------------
# FIX: REMOVED the if __name__ == '__main__' block