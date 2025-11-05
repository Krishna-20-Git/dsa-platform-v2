import os
from flask import Flask, render_template

# --- Import all your Blueprints using the ORIGINAL filenames ---

# Unit 1
from unit1.U1DMA import dma_bp

# Unit 2
from unit2.U2cirsingle import cirsingle_bp
from unit2.U2DblCir import dblcir_bp
from unit2.U2DoubleLinked import doublelinked_bp
from unit2.U2linked_list_visual import linkedlist_bp
from unit2.U2sparesematrix import sparesematrix_bp

# Unit 3
from unit3.U3balancingsymbol import balancingsymbol_bp
from unit3.U3infixtopost import infixtopost_bp
from unit3.U3postfixevaluation import postfixevaluation_bp
from unit3.U3Queue import Queue_bp
from unit3.U3queuearray import queuearray_bp
from unit3.U3stack import stack_bp
from unit3.U3stackarray import stackarray_bp
from unit3.U3towerofhanoi import towerofhanoi_bp

# Unit 4
from unit4.U4AVL import AVL_bp
from unit4.U4BST import BST_bp
from unit4.U4Btree import Btree_bp
from unit4.U4TreeRotation import TreeRotation_bp
from unit4.U4TreeTravel import TreeTravel_bp

# Unit 5
from unit5.U5dijkstra import dijkstra_bp
from unit5.U5kruskal import kruskal_bp
from unit5.U5prims import prims_bp
from unit5.U5Spanning import Spanning_bp


# --- Create the Main App ---
app = Flask(__name__)

# --- Register Blueprints with URL Prefixes ---
# (These prefixes do not need to change, they are just URLs)

# Unit 1
app.register_blueprint(dma_bp, url_prefix='/unit1/U1DMA')

# Unit 2
app.register_blueprint(cirsingle_bp, url_prefix='/unit2/U2cirsingle')
app.register_blueprint(dblcir_bp, url_prefix='/unit2/U2DblCir')
app.register_blueprint(doublelinked_bp, url_prefix='/unit2/U2DoubleLinked')
app.register_blueprint(linkedlist_bp, url_prefix='/unit2/U2linked_list_visual')
app.register_blueprint(sparesematrix_bp, url_prefix='/unit2/U2sparesematrix')

# Unit 3
app.register_blueprint(balancingsymbol_bp, url_prefix='/unit3/U3balancingsymbol')
app.register_blueprint(infixtopost_bp, url_prefix='/unit3/U3infixtopost')
app.register_blueprint(postfixevaluation_bp, url_prefix='/unit3/U3postfixevaluation')
app.register_blueprint(Queue_bp, url_prefix='/unit3/U3Queue')
app.register_blueprint(queuearray_bp, url_prefix='/unit3/U3queuearray')
app.register_blueprint(stack_bp, url_prefix='/unit3/U3stack')
app.register_blueprint(stackarray_bp, url_prefix='/unit3/U3stackarray')
app.register_blueprint(towerofhanoi_bp, url_prefix='/unit3/U3towerofhanoi')

# Unit 4
app.register_blueprint(AVL_bp, url_prefix='/unit4/U4AVL')
app.register_blueprint(BST_bp, url_prefix='/unit4/U4BST')
app.register_blueprint(Btree_bp, url_prefix='/unit4/U4Btree')
app.register_blueprint(TreeRotation_bp, url_prefix='/unit4/U4TreeRotation')
app.register_blueprint(TreeTravel_bp, url_prefix='/unit4/U4TreeTravel')

# Unit 5
app.register_blueprint(dijkstra_bp, url_prefix='/unit5/U5dijkstra')
app.register_blueprint(kruskal_bp, url_prefix='/unit5/U5kruskal')
app.register_blueprint(prims_bp, url_prefix='/unit5/U5prims')
app.register_blueprint(Spanning_bp, url_prefix='/unit5/U5Spanning')


# --- Main Homepage Route ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Run the App ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)