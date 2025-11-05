# 1. Import Blueprint
from flask import Blueprint, request, jsonify, render_template_string

# 2. Create Blueprint
queuearray_bp = Blueprint(
'queuearray_bp' , __name__
)

# ------------------------------
# Data Structure: Queue using Array
# (Logic is unchanged)
# ------------------------------

class Queue:
    def __init__(self, size=7):
        self.queue = []
        self.max_size = size

    def enqueue(self, value):
        if len(self.queue) >= self.max_size:
            return "Queue Overflow! Cannot enqueue more elements."
        self.queue.append(value)
        return f"Enqueued value {value} to the queue."

    def dequeue(self):
        if not self.queue:
            return "Queue Underflow! Queue is empty."
        value = self.queue.pop(0)
        return f"Dequeued value {value} from the queue."

    def to_list(self):
        """Return structured data with index and address"""
        result = []
        for i, value in enumerate(self.queue):
            result.append({
                "index": i,
                "value": value,
                # Simulate a unique address for visualization
                "addr": hex(id(value)) 
            })
        return result

# Global queue instance
queue = Queue(size=7)

# ------------------------------
# Flask Routes
# ------------------------------

@queuearray_bp.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Queue Visualization (Array Implementation)</title>
        <style>
            body { font-family: Arial; text-align: center; background: #f8fafc; margin-top: 50px; }
            input, button { padding: 8px; margin: 5px; font-size: 16px; }
            #status { font-size: 16px; color: #222; margin-top: 10px; }
            
            /* FIX: Added scrolling canvas wrapper */
            .canvas-wrapper {
                width: 90%%;
                max-width: 1000px;
                overflow-x: auto;
                margin: 20px auto;
                border: 2px solid #333;
                background: white;
            }
            canvas { margin-top: 0; }
        </style>
    </head>
    <body>
        <h2>🚉 Queue Visualization (Array-Based Implementation)</h2>
        <div>
            <input type="text" id="queueValue" placeholder="Enter value">
            <button onclick="enqueueValue()">Enqueue</button>
            <button onclick="dequeueValue()">Dequeue</button>
        </div>

        <p id="status"></p>
        
        <div class="canvas-wrapper">
            <canvas id="canvas" width="1000" height="400"></canvas>
        </div>

        <script>
            async function enqueueValue() {
                let valInput = document.getElementById("queueValue");
                let val = valInput.value;
                if (!val) return alert("Enter a value to enqueue.");
                
                // Relative fetch path
                let res = await fetch('enqueue?value=' + val);
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawQueue(data.queue);
                
                // FIX: Clear input box
                valInput.value = "";
            }

            async function dequeueValue() {
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
                const startX = 80;

                // FIX: Dynamically resize canvas
                let requiredWidth = startX + (queue.length * (boxWidth + boxSpacing)) + 100;
                canvas.width = Math.max(1000, requiredWidth);

                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.textAlign = "left"; // Reset align

                if (queue.length === 0) {
                    ctx.font = "20px Arial";
                    ctx.textAlign = "center";
                    ctx.fillText("Queue is empty", canvas.width / 2, 200);
                    return;
                }
                
                let x = startX, y = 150;

                for (let i = 0; i < queue.length; i++) {
                    let node = queue[i];

                    // Draw box
                    ctx.strokeStyle = "#333";
                    ctx.lineWidth = 2;
                    ctx.strokeRect(x, y, boxWidth, boxHeight);

                    // --- FIX: Truncate text ---
                    ctx.fillStyle = "#000";
                    ctx.font = "14px Arial";
                    ctx.fillText("Value: " + node.value, x + 10, y + 30);
                    let shortAddr = node.addr ? "..." + node.addr.slice(-6) : "None";
                    ctx.fillText("Addr: " + shortAddr, x + 10, y + 55);
                    // --- END FIX ---

                    // Draw arrows between boxes
                    if (i < queue.length - 1) {
                        ctx.beginPath();
                        ctx.moveTo(x + boxWidth, y + boxHeight / 2);
                        ctx.lineTo(x + boxWidth + 30, y + boxHeight / 2);
                        ctx.stroke();
                        ctx.beginPath();
                        ctx.moveTo(x + boxWidth + 30, y + boxHeight / 2);
                        ctx.lineTo(x + boxWidth + 20, y + boxHeight / 2 - 5);
                        ctx.moveTo(x + boxWidth + 30, y + boxHeight / 2);
                        ctx.lineTo(x + boxWidth + 20, y + boxHeight / 2 + 5);
                        ctx.stroke();
                    }

                    // Front and Rear labels
                    ctx.textAlign = "center";
                    if (i === 0) {
                        ctx.fillStyle = "red";
                        ctx.fillText("Front", x + boxWidth / 2, y - 10);
                        ctx.fillStyle = "black";
                    }
                    if (i === queue.length - 1) {
                        ctx.fillStyle = "blue";
                        ctx.fillText("Rear", x + boxWidth / 2, y + boxHeight + 20);
                        ctx.fillStyle = "black";
                    }
                    ctx.textAlign = "left"; // Reset

                    x += boxWidth + boxSpacing;
                }
            }
            
            // FIX: Load initial queue state
            window.onload = async function() {
                try {
                    let res = await fetch('status');
                    let data = await res.json();
                    document.getElementById("status").innerText = "Queue initialized.";
                    drawQueue(data.queue);
                } catch (err) {
                    console.error("Error fetching initial status:", err);
                    document.getElementById("status").innerText = "Error loading queue.";
                }
            };
        </script>
    </body>
    </html>
    """)

@queuearray_bp.route('/enqueue')
def enqueue_value_route(): # Renamed function to avoid conflict
    value = request.args.get('value')
    if value:
        msg = queue.enqueue(value)
    else:
        msg = "No value provided for enqueue."
    return jsonify({"message": msg, "queue": queue.to_list()})

@queuearray_bp.route('/dequeue')
def dequeue_value_route(): # Renamed function to avoid conflict
    msg = queue.dequeue()
    return jsonify({"message": msg, "queue": queue.to_list()})

# FIX: Added status route
@queuearray_bp.route('/status')
def get_status():
    return jsonify({"queue": queue.to_list()})


# ------------------------------
# Run Flask App
# ------------------------------
# FIX: REMOVED the if __name__ == '__main__' block