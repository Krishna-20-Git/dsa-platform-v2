# 1. Import Blueprint
from flask import Blueprint, request, jsonify, render_template_string

# 2. Create Blueprint
postfixevaluation_bp = Blueprint(
    'postfixevaluation_bp', __name__
)

# ------------------------------
# Postfix Evaluation Logic
# ------------------------------

def evaluate_postfix(expression):
    """Evaluate a postfix expression and record visualization steps"""
    stack = []
    steps = []

    for char in expression:
        if char == ' ':
            continue
        if char.isdigit():
            stack.append(int(char))
            steps.append({
                "symbol": char,
                "action": f"Pushed {char} to stack (operand)",
                "stack": stack.copy()
            })
        elif char in "+-*/^":
            if len(stack) < 2:
                steps.append({
                    "symbol": char,
                    "action": "Error: insufficient operands",
                    "stack": stack.copy()
                })
                # Return None for result on error
                return None, steps 
            
            b = stack.pop()
            a = stack.pop()
            result = 0 # Initialize result

            if char == '+': result = a + b
            elif char == '-': result = a - b
            elif char == '*': result = a * b
            # FIX: Use integer division for standard postfix evaluation
            elif char == '/': 
                if b == 0:
                    steps.append({
                        "symbol": char,
                        "action": f"Error: Division by zero ({a} / {b})",
                        "stack": [a, b] # Show what was popped
                    })
                    return None, steps
                result = a // b 
            elif char == '^': result = a ** b

            stack.append(result)
            steps.append({
                "symbol": char,
                "action": f"Applied operator {char}: {a} {char} {b} = {result}",
                "stack": stack.copy()
            })
        else:
            steps.append({
                "symbol": char,
                "action": f"Ignored invalid symbol '{char}'",
                "stack": stack.copy()
            })

    final_result = stack.pop() if len(stack) == 1 else "Error: Invalid Expression"
    
    # Final step to show empty stack
    steps.append({
        "symbol": "Done",
        "action": f"Final result: {final_result}",
        "stack": stack.copy()
    })
    
    return final_result, steps


# ------------------------------
# Flask Routes
# ------------------------------

@postfixevaluation_bp.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Postfix Evaluation Visualizer</title>
        <style>
            body { font-family: Arial; background: #f8fafc; text-align: center; margin-top: 40px; }
            input, button { padding: 8px; margin: 5px; font-size: 16px; }
            #status { font-size: 16px; color: #222; margin: 10px; font-weight: bold; }
            canvas { border: 2px solid #333; background: white; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h2>🧮 Postfix Expression Evaluation Visualization</h2>
        <input type="text" id="expression" placeholder="Enter postfix (e.g., 231*+9-)" size="40">
        <button onclick="evaluate()">Evaluate</button>
        <p id="status"></p>
        <canvas id="canvas" width="1000" height="500"></canvas>

        <script>
            async function evaluate() {
                let exprInput = document.getElementById("expression");
                let expr = exprInput.value;
                if (!expr) return alert("Enter a postfix expression");
                
                // FIX: Relative fetch path (already correct)
                let res = await fetch('evaluate?expr=' + encodeURIComponent(expr));
                let data = await res.json();
                
                document.getElementById("status").innerText = "Final Result: " + data.result;
                animateSteps(data.steps);
                
                // FIX: Clear input box
                exprInput.value = "";
            }

            function animateSteps(steps) {
                let canvas = document.getElementById("canvas");
                let ctx = canvas.getContext("2d");
                let i = 0;

                function drawStep(step) {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.textAlign = "left";

                    ctx.font = "18px Arial";
                    ctx.fillText("Processing Symbol: " + step.symbol, 50, 40);
                    ctx.fillText("Action: " + step.action, 50, 70);

                    // --- FIX: Draw stack from bottom-up ---
                    ctx.font = "16px Arial";
                    ctx.fillText("Stack:", 450, 120);
                    
                    // Draw stack container
                    ctx.strokeStyle = "#333";
                    ctx.lineWidth = 2;
                    let stackBaseY = 450;
                    let stackHeight = 300;
                    ctx.strokeRect(450, stackBaseY - stackHeight, 100, stackHeight);
                    
                    let y = stackBaseY; // Start drawing from the bottom
                    
                    for (let j = 0; j < step.stack.length; j++) {
                        let itemY = y - (j * 50); // Calculate y-position upwards
                        ctx.fillStyle = "#87CEEB";
                        ctx.fillRect(450, itemY - 50, 100, 50); // Draw item
                        ctx.strokeRect(450, itemY - 50, 100, 50); // Draw border
                        
                        ctx.fillStyle = "#000";
                        ctx.textAlign = "center";
                        ctx.fillText(step.stack[j], 500, itemY - 20);
                    }
                    
                    if (step.stack.length > 0) {
                         ctx.textAlign = "left";
                         ctx.fillText("← TOP", 560, y - (step.stack.length - 1) * 50 - 20);
                    }
                    // --- END FIX ---
                }

                function stepThrough() {
                    if (i < steps.length) {
                        drawStep(steps[i]);
                        i++;
                        setTimeout(stepThrough, 1500);
                    }
                }
                stepThrough();
            }
        </script>
    </body>
    </html>
    """)

@postfixevaluation_bp.route('/evaluate')
def evaluate_expression():
    expr = request.args.get('expr', '')
    result, steps = evaluate_postfix(expr)
    return jsonify({"result": result, "steps": steps})


# ------------------------------
# Run Flask App
# ------------------------------
# FIX: REMOVED the if __name__ == '__main__' block