# Interactive Data Structures & Algorithms (DSA) Learning Platform

A full-stack educational SaaS platform designed to help students visualize and track their mastery of complex computer science concepts. This application transforms static algorithm scripts into an interactive, gamified learning experience with a modern "Midnight Onyx" UI.

## Key Features

### Comprehensive Visualizers
* **23+ Interactive Modules:** Covers 5 distinct units including Memory Management, Linear Data Structures, Stacks/Queues, Trees (AVL, BST, B-Tree), and Graph Algorithms (Dijkstra, Prim’s, Kruskal’s).
* **Dynamic Rendering:** Real-time generation of graphs and trees using NetworkX and Matplotlib integration.

### User Experience & SaaS Features
* **User Authentication:** Secure Signup and Login system using `Flask-Login` and `Bcrypt` hashing.
* **Progress Tracking:** Persistent database (SQLite/SQLAlchemy) that tracks completed modules per user.
* **Interactive Dashboard:** A personalized user dashboard featuring a dynamic progress bar, completion statistics, and a chronological activity log.
* **Modern UI/UX:** Custom-built "Midnight Onyx" dark theme featuring:
  * Glassmorphism (frosted glass) cards and navigation.
  * Animated CSS background particles.
  * Responsive Grid Layouts.
  * Toast notifications and Flash messaging for user feedback.

## Tech Stack

* **Backend:** Python 3, Flask (Blueprints architecture).
* **Database:** SQLite, SQLAlchemy ORM.
* **Frontend:** HTML5, CSS3 (Custom Variables, Animations), JavaScript (Fetch API).
* **Libraries:** NetworkX, Matplotlib, Gunicorn.
* **Deployment:** Render / Gunicorn.

## Screenshots

**HOME PAGE:**
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/50e67fc0-68be-4a3b-900b-634f1a7e06aa" />

**LOGIN PAGE:**
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/507ce83d-a743-45c9-b99e-cf3854a7a44c" />

**DASHBOARD:**
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/424533c9-50a0-497f-8a96-409b8e0b2ccd" />

**TOWER OF HANOI:**
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6f97efd0-4c23-412c-a9a6-9ab971137364" />

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/dsa-platform-v2.git](https://github.com/YOUR_USERNAME/dsa-platform-v2.git)
   cd dsa-platform-v2

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

3. **Run the application:**
   ```bash
   python app.py
4. **Access the app:** Open your browser and navigate to http://127.0.0.1:5000.

