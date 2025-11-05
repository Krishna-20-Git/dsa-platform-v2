# 1. Import Blueprint
from flask import Blueprint, request, jsonify, render_template_string

# 2. Create Blueprint
stackarray_bp = Blueprint(
'stackarray_bp' , __name__
)

# ------------------------------
# Data Structure: Stack using Array
# (Logic is unchanged)
# ------------------------------

class Stack:
    def __init__(self, size=7): # Set max size to 7 as in original
        self.stack = []
        self.max_size = size

    def push(self, value):
        if len(self.stack) >= self.max_size:
            return "Stack Overflow! Cannot push more elements."
        self.stack.append(value)
        return f"Pushed value {value} onto the stack."

    def pop(self):
        if not self.stack:
            return "Stack Underflow! Stack is empty."
        value = self.stack.pop()
        return f"Popped value {value} from the stack."

    def to_list(self):
        """Return stack representation with index and address"""
        result = []
        for i, value in enumerate(self.stack):
            result.append({
                "index": i,
                "value": value,
                "addr": hex(id(value))
            })
        return result


# Global stack instance
stack = Stack(size=7)

# ------------------------------
# Flask Routes
# ------------------------------

@stackarray_bp.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stack Visualization (Array Implementation)</title>
        <style>
            body { font-family: Arial; text-align: center; background: #f8fafc; margin-top: 50px; }
            canvas { border: 2px solid #333; background: white; margin-top: 20px; }
            input, button { padding: 8px; margin: 5px; font-size: 16px; }
            #status { font-size: 16px; color: #222; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h2>📦 Stack Visualization (Array-Based Implementation)</h2>
        <div>
            <input type="text" id="stackValue" placeholder="Enter value">
            <button onclick="pushValue()">Push</button>
            <button onclick="popValue()">Pop</button>
        </div>

        <p id="status"></p>
        <canvas id="canvas" width="600" height="500"></canvas>

        <script>
            async function pushValue() {
                let valInput = document.getElementById("stackValue");
                let val = valInput.value;
                if (!val) return alert("Enter a value to push.");
                
                // Relative fetch path
                let res = await fetch('push?value=' + val);
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawStack(data.stack, data.message);
                
                // FIX: Clear input box
                valInput.value = "";
            }

            async function popValue() {
                // Relative fetch path
                let res = await fetch('pop');
                let data = await res.json();
                document.getElementById("status").innerText = data.message;
                drawStack(data.stack, data.message);
            }

            // =================================================================
            // === THIS FUNCTION HAS BEEN UPDATED FOR TEXT AND DRAWING LOGIC ===
            // =================================================================
            function drawStack(stack, message) {
                let canvas = document.getElementById("canvas");
                let ctx = canvas.getContext("2d");
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                let boxHeight = 60;
                let boxWidth = 200;
                let x = canvas.width / 2 - (boxWidth / 2); // Center the stack
                let startY = 450; // Bottom of the canvas
                let maxStackHeight = 7 * boxHeight; // Based on new Stack(size=7)

                ctx.textAlign = "left";

                if (stack.length === 0 && !message.includes("Underflow")) {
                    ctx.font = "20px Arial";
                    ctx.textAlign = "center";
                    ctx.fillText("Stack is empty", canvas.width / 2, 250);
                }

                // Draw stack container
                ctx.strokeStyle = "#333";
                ctx.lineWidth = 2;
                ctx.strokeRect(x, startY - maxStackHeight, boxWidth, maxStackHeight);

                // Loop from 0 (bottom) to stack.length - 1 (top)
                for (let i = 0; i < stack.length; i++) {
                    let node = stack[i];
                    let y = startY - (i * boxHeight); // y-position from bottom

                    // Draw box
                    ctx.fillStyle = "#87CEEB";
                    ctx.fillRect(x, y - boxHeight, boxWidth, boxHeight);
                    ctx.strokeRect(x, y - boxHeight, boxWidth, boxHeight);

                    // --- FIX: Truncate text ---
                    ctx.fillStyle = "#000";
                    ctx.font = "14px Arial";
                    ctx.fillText("Value: " + node.value, x + 10, y - 35);
                    
                    let shortAddr = node.addr ? "..." + node.addr.slice(-6) : "None";
                    ctx.fillText("Addr: " + shortAddr, x + 10, y - 15);
                    // --- END FIX ---

                    // Label Top
                    if (i === stack.length - 1) {
                        ctx.fillStyle = "red";
                        ctx.font = "16px Arial";
                        ctx.fillText("← Top", x + boxWidth + 10, y - 30);
                    }
                }
            }
            
            // FIX: Load initial stack state
            window.onload = async function() {
                try {
                    let res = await fetch('status'); 
                    let data = await res.json();
                    document.getElementById("status").innerText = "Stack initialized.";
                    drawStack(data.stack, "Stack initialized.");
                } catch (err) {
                    console.error("Error fetching initial status:", err);
                    document.getElementById("status").innerText = "Error loading stack.";
                }
            };
        </script>
    </body>
    </html>
    """)

@stackarray_bp.route('/push')
def push_value():
    value = request.args.get('value')
    if value:
        msg = stack.push(value)
    else:
        msg = "No value provided for push."
    return jsonify({"message": msg, "stack": stack.to_list()})

@stackarray_bp.route('/pop')
def pop_value():
    msg = stack.pop()
    return jsonify({"message": msg, "stack": stack.to_list()})

# FIX: Added status route
@stackarray_bp.route('/status')
def get_status():
    return jsonify({"stack": stack.to_list()})

# ------------------------------
# Run Flask App
# ------------------------------
# FIX: REMOVED the if __name__ == '__main__' block