# 1. Import Blueprint
from flask import Blueprint, request, jsonify, render_template_string

# 2. Create Blueprint
infixtopost_bp = Blueprint(
    'infixtopost_bp', __name__
)

# ------------------------------
# Infix to Postfix Conversion Logic
# (Logic is unchanged)
# ------------------------------

precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}

def infix_to_postfix(expression):
    """Convert infix expression to postfix and return each step"""
    stack = []
    output = []
    steps = []

    for char in expression:
        if char == ' ':
            continue
        if char.isalnum():  # Operand
            output.append(char)
            steps.append({
                "symbol": char,
                "action": "Added to output (operand)",
                "stack": stack.copy(),
                "output": output.copy()
            })
        elif char == '(':
            stack.append(char)
            steps.append({
                "symbol": char,
                "action": "Pushed '(' onto stack",
                "stack": stack.copy(),
                "output": output.copy()
            })
        elif char == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
            steps.append({
                "symbol": char,
                "action": "Popped until '('",
                "stack": stack.copy(),
                "output": output.copy()
            })
        else:
            # Operator
            # FIX: Handle potential missing key for non-operators (though input is alphanumeric)
            if char in precedence:
                while stack and stack[-1] != '(' and stack[-1] in precedence and precedence[stack[-1]] >= precedence[char]:
                    output.append(stack.pop())
                stack.append(char)
                steps.append({
                    "symbol": char,
                    "action": f"Pushed operator '{char}' onto stack",
                    "stack": stack.copy(),
                    "output": output.copy()
                })
            else:
                # Handle non-alphanumeric, non-operator, non-parenthesis chars if any
                steps.append({
                    "symbol": char,
                    "action": f"Ignored unknown symbol '{char}'",
                    "stack": stack.copy(),
                    "output": output.copy()
                })


    while stack:
        output.append(stack.pop())
        steps.append({
            "symbol": "-",
            "action": "Popped remaining operators",
            "stack": stack.copy(),
            "output": output.copy()
        })

    return "".join(output), steps


# ------------------------------
# Flask Routes
# ------------------------------

@infixtopost_bp.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Infix to Postfix Visualizer</title>
        <style>
            body { font-family: Arial; background: #f8fafc; text-align: center; margin-top: 40px; }
            input, button { padding: 8px; margin: 5px; font-size: 16px; }
            #status { font-size: 16px; color: #333; margin: 10px; }
            
            /* FIX: Added scrolling canvas wrapper */
            .canvas-wrapper {
                width: 90%%;
                max-width: 1100px;
                overflow-x: auto;
                margin: 20px auto;
                border: 2px solid #333;
                background: white;
            }
            canvas { margin-top: 0; }
        </style>
    </head>
    <body>
        <h2>🧠 Infix to Postfix Conversion Visualization</h2>
        <input type="text" id="expression" placeholder="Enter infix expression (e.g. A+B*(C-D))" size="40">
        <button onclick="convert()">Convert</button>
        <p id="status"></p>
        
        <div class="canvas-wrapper">
            <canvas id="canvas" width="1100" height="500"></canvas>
        </div>

        <script>
            async function convert() {
                let exprInput = document.getElementById("expression");
                let expr = exprInput.value;
                if (!expr) return alert("Enter an infix expression");
                
                // FIX: Relative fetch path (already correct)
                let res = await fetch('convert?expr=' + encodeURIComponent(expr));
                let data = await res.json();
                
                document.getElementById("status").innerText = "Postfix Expression: " + data.postfix;
                animateSteps(data.steps);
                
                // FIX: Clear input box for better UX
                exprInput.value = "";
            }

            async function animateSteps(steps) {
                let canvas = document.getElementById("canvas");
                let ctx = canvas.getContext("2d");
                
                // FIX: Dynamically resize canvas
                let requiredWidth = 200; // Start
                if (steps.length > 0) {
                    let lastStep = steps[steps.length - 1];
                    requiredWidth = 200 + (lastStep.output.length * 50) + 50; // Output width
                }
                canvas.width = Math.max(1100, requiredWidth);
                
                let i = 0;

                function drawStep(step) {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    ctx.font = "18px Arial";
                    ctx.textAlign = "left";
                    ctx.fillText("Processing Symbol: " + (step.symbol || "N/A"), 50, 40);
                    ctx.fillText("Action: " + step.action, 50, 70);

                    // Draw Stack
                    ctx.font = "16px Arial";
                    ctx.fillText("Stack:", 50, 120);
                    for (let j = 0; j < step.stack.length; j++) {
                        ctx.strokeRect(50, 150 + j * 40, 60, 40);
                        ctx.textAlign = "center";
                        ctx.fillText(step.stack[j], 80, 178 + j * 40);
                    }

                    // Draw Output
                    ctx.textAlign = "left";
                    ctx.fillText("Output:", 200, 120);
                    for (let j = 0; j < step.output.length; j++) {
                        ctx.strokeRect(200 + j * 50, 150, 50, 40);
                        ctx.textAlign = "center";
                        ctx.fillText(step.output[j], 225 + j * 50, 178);
                    }
                }

                function stepThrough() {
                    if (i < steps.length) {
                        drawStep(steps[i]);
                        i++;
                        setTimeout(stepThrough, 1500); // Animation speed
                    }
                }
                stepThrough();
            }
        </script>
    </body>
    </html>
    """)

@infixtopost_bp.route('/convert')
def convert_expression():
    expr = request.args.get('expr', '')
    postfix, steps = infix_to_postfix(expr)
    return jsonify({"postfix": postfix, "steps": steps})


# ------------------------------
# Run Flask App
# ------------------------------
# FIX: REMOVED the if __name__ == '__main__' block