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
**Join our community:** [Telegram Channel] https://t.me/zhivoglas
### 📜 License
This project is licensed under the **MIT License**.
*FFmpeg is a trademark of Fabrice Bellard.*

*FFmpeg is a trademark of Fabrice Bellard. This project is not affiliated with the FFmpeg team.*

#The philosophy of this program and the idea of ​​creation
It's not just a tool, but a philosophy. This project isn't just another wrapper, but a manifesto for commercial freedom and a new, flexible approach to automation. ffmpegNode was born out of admiration for the power and pace of development of FFmpeg. It's a great tool, created by enthusiasts who wanted to share their capabilities and their idea with the world. However, the rigid limitations of the GPL license often become a barrier to its full and complete development, as well as its use in commercial ecosystems by aspiring developers with limited infrastructure. We believe that every idea should have its reward and resources for development. We were saddened by the closure of the Arthenica project due to a lack of necessary support. Its closure was a severe blow to the community. Aspiring developers around the world suddenly lost reliable support and encouragement. When such key tools disappear from the scene, it doesn't just break someone's workflow—it literally hinders the evolution of technology and hinders the growth of young professionals, who no longer have anything to learn from or anyone to turn to for help. Because of this (the education of young people), the entire industry suffers: technology development slows, developers lose a high-quality code base to learn from, and they lose the support of an experienced community. Our project aims to give developers the stability, predictability, and independence that are sorely lacking. Thanks to the plugin architecture and MIT license, the tool will survive even if one of the underlying engines stops developing—you can simply replace it with another. We are building not just a utility, but a stable environment for the continuous growth of technology and the engineers themselves. We want to support FFmpeg and give it a new path for growth, freeing developers from legal risks. ffmpegNode separates any engine from your application's codebase. It interacts with it as an external, isolated plugin via the command line interface (CLI). This allows you to legally use the full power of heavyweight open-source engines in commercial products, while keeping the automation tool code completely open under the MIT license. The word Node in the name refers not only to the runtime environment but also to the nodes in the program architecture. The project is built on the concept of data processing nodes. This approach allows for visualization, flexible configuration, and execution of complex, multi-threaded batch automation of any process. ffmpegNode is a universal batch data processing automation tool. It was conceived as a bridge for FFmpeg into the world of commercial software, but has grown into a flexible system capable of using any command-line utilities as plugins. We take the best of open source and make it accessible to start-up businesses and young talents without restrictions. ffmpegNode is a Node.js wrapper for managing external command-line processes, automating utility launches, log collection, and shutdown monitoring. Despite its name, the library is universal: in the constructor, you can specify the path to any program (for example, tar, ImageMagick) and pass arguments using the standard child_process.spawn method.
ffmpegNode offers tremendous potential in three key areas: technical, commercial, and industrial. Engine-Agnostic: The program is not tightly tied to FFmpeg. Its JSON-schema-based architecture allows for on-the-fly integration with any command-line interface (CLI) tools, be they neural network tools, document converters, or archivers. Any CLI program becomes a plugin. Infinite scalability via nodes: The node concept allows for the construction of complex, branched data processing pipelines. You can feed the output of one command-line interface into another, creating automation chains of any complexity. True Batch Processing: Potential for automating hundreds and thousands of parallel tasks. The architecture allows for efficient resource allocation during heavy processing (for example, simultaneous rendering, transcoding, or analysis of large data sets). Type Safety and Validation: By generating arguments based on strict schemas, potential syntax errors are caught before the process is launched, which is critical for production systems. Commercial Integrity (GPL Bypass): The main legal advantage is the exclusion of heavy-duty open-source engines (such as FFmpeg under the GPL/LGPL) in an isolated outer layer. Your main application remains commercially closed or uses the free MIT license, without infringing the copyrights of the engine developers. Business Resilience (On-the-Fly Replacement): Potential protection against the closure of third-party projects (as happened with Arthenica). If one of your tools is discontinued, your business does not lose the product—the ffmpegNode architecture allows you to quickly rewrite the schema and replace the failed engine with a similar one without rewriting the entire core system. Creative space for software architects: The tool frees developers from the tedious task of writing repetitive wrappers and concatenating command-line strings (which AI can already do). It transfers control to architects, allowing them to design fundamentally new, flexible, and independent automation systems that AI cannot devise on its own. Standardization of open-source tools: The project has the potential to become a universal standard (hub) for Node.js interaction with the entire world of command-line software, uniting disparate utilities into a single, understandable ecosystem of schemes.
