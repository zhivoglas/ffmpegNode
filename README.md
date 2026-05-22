# FFNode Stream 🚀
**The Universal Visual Logic Engine for Media & Beyond**

**FFNode Stream** is a modular, engine-agnostic orchestrator for media processing. It transforms complex code and CLI logic into an intuitive **visual node graph**. Built for creators, developers, and power users who value both power and aesthetics.

### 🎨 Visual & Immersive Experience
We believe that professional tools shouldn't be boring. 
*   **Animated Workspaces:** Choose from a variety of stunning animated backgrounds to keep your creative flow inspired.
*   **Sponsorship Hub:** Our interface features dedicated spaces to showcase **Sponsors and Patrons**. Your support directly fuels the development of this engine.
*   **Modern UI:** A sleek, high-performance interface built with React 19 and Framer Motion.

### 🧩 Engine-Agnostic Architecture
The project is built on a **"Plugin-Worker"** model. While it has deep FFmpeg integration, the core can host **any engine**:
*   **Multi-Engine Support:** Run FFmpeg, OpenCV, AI Upscalers, or Custom Scripts in a single pipeline.
*   **Manifest-Driven UI:** Nodes are automatically generated from a simple `manifest.json`.
*   **Modular Backend:** Add new capabilities by just dropping a folder into `/plugins`.

### 🚀 Getting Started
  1. Prerequisites
  Before you begin, ensure you have the following installed:
  Node.js (v18.0.0 or higher)
  Python (v3.10 or higher)
  FFmpeg (Optional, but recommended for the default media plugin)
  2. Installation & Setup
  Clone the repository:
  bash
  git clone [https://github.com](https://github.com/zhivoglas/ffmpegNode.git)
  cd ffmpegNode

  Frontend Setup (React + Electron):
  bash
  cd frontend
  npm install

  Backend Setup (Python):
  bash
  # Return to the root folder
  cd ..
  # (Optional) Create a virtual environment
  python -m venv venv
  source venv/bin/scripts/activate  # On Windows: venv\Scripts\activate
  # Install dependencies (if you have a requirements.txt, or install manually)
  pip install -r requirements.txt 

  3. Running the Application
  To run the app in development mode (with Hot Module Replacement for the UI):
  Start the Frontend & Electron:
  bash
  cd frontend
  npm run start

  This command uses concurrently to launch the Vite dev server and the Electron window simultaneously.
  Start the Backend Orchestrator:
  bash
  # In a separate terminal
  python main.py

  🛠 How to add a New Engine/Plugin
  FFNode Stream is designed for easy expansion. To add a new processing engine (AI, OpenCV, etc.):
  Create a new folder in /plugins.
  Add a manifest.json to define your nodes.
  Write your logic in worker.py.
  The UI will automatically detect and render your new engine!

### ❤️ Support & Sponsorship
Help us build the future of visual media processing! We offer prominent placement for sponsors within the app's UI:
*   **Showcase:** Your logo on the main workspace header.
*   **Themes:** Exclusive animated backgrounds for top-tier patrons.

### ❤️ Support & Acknowledgments
FFNode Stream is an open-source labor of love. We offer prominent placement for sponsors within the app's UI:
*   **Showcase:** Your logo on the main workspace header.
*   **Immersive Themes:** Exclusive animated backgrounds for top-tier patrons.

---
**Special Acknowledgement:**
I express my deep gratitude to the developers at Microsoft, Google, ffmpeg, and everyone else who directly or indirectly helped create and implement this project. 
Thank God for the talent and opportunity to create for the greater good!
---

### 📜 License
Licensed under **MIT**. 
