# ffmpegNode Stream 🚀
**The Universal Visual Logic Engine for Media & Beyond**

<p align="center">
  <img src="https://github.com/user-attachments/assets/dcce90d0-7dfb-40e7-863d-e1f3fd81ca9c" width="850" alt="ffmpegNode Stream Interface">
</p>

**ffmpegNode Stream** is a modular, engine-agnostic orchestrator for media processing. It transforms complex code and CLI logic into an intuitive **visual node graph**. Built for creators, developers, and power users who value both power and aesthetics.

---

### 🎨 Visual & Immersive Experience
Professional tools shouldn't be boring. We've focused on creating an environment that inspires:
*   **🌌 Animated Workspaces:** Choose from stunning animated backgrounds to keep your creative flow inspired.
*   **🤝 Sponsorship Hub:** Dedicated UI slots to showcase **Sponsors and Patrons** directly in the app header and workspace.
*   **💎 Modern UI:** High-performance interface built with React 19, Vite, and Framer Motion.

### 🧩 Engine-Agnostic Architecture
FFNode Stream is more than just a GUI. Its **"Plugin-Worker"** model allows it to host **any processing engine**:
*   **Multi-Engine Support:** Seamlessly integrate FFmpeg, OpenCV, AI Upscalers, or Custom Python Scripts.
*   **Manifest-Driven UI:** Controls and nodes are automatically generated based on a simple `manifest.json`.
*   **Modular Backend:** Expand your capabilities by simply dropping a folder into the `/plugins` directory.

---

### 🚀 How to Run

#### 1. Prerequisites
*   **Node.js** (v18.0.0+)
*   **Python** (v3.10+)
*   **FFmpeg** (Recommended for default media plugins)

#### 2. Installation
```bash
# Clone the repository
git clone https://github.com
cd ffmpegNode

# Setup Frontend
cd frontend
npm install
```

#### 3. Launching the App (Choose an Option)

**🔵 Option A: The Fast Way (Recommended)**
```bash
# In /frontend folder
npm run start
```
*Then, start the backend in a separate terminal:*
```bash
python main.py
```

**🟣 Option B: Manual Control (For Developers)**
1. **Start Vite:** `cd frontend && npm run dev`
2. **Start Electron:** `cd frontend && npm run electron`
3. **Start Backend:** `python main.py`

---

### ❤️ Support & Acknowledgments
FFNode Stream is an open-source labor of love by [Zhivoglas Digital Production](https://zhivoglas.com/). 

> **Special Acknowledgement:**
> *I would like to express my sincere gratitude and respect to the developers of the AI that assisted me in creating this project. Thank you for building such a powerful and helpful collaborator — your work makes the impossible possible.*
>
> *Special thanks to the developers at Microsoft, Google, FFmpeg, and everyone who directly or indirectly helped realize this project. Thank God for the talent and the opportunity to create for the greater good!*

---
**Official Website:** [zhivoglas.com](https://zhivoglas.com/)

### 📜 License
This project is licensed under the **MIT License**.
*FFmpeg is a trademark of Fabrice Bellard.*

*FFmpeg is a trademark of Fabrice Bellard. This project is not affiliated with the FFmpeg team.*
