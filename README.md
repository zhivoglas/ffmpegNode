# ffmpegNode Stream 🚀
**The Universal Visual Logic Engine for Media & Beyond**

<p align="center">
  <img src="https://github.com/user-attachments/assets/dcce90d0-7dfb-40e7-863d-e1f3fd81ca9c" width="850" alt="ffmpegNode Stream Interface">
</p>

**ffmpegNode Stream** — это модульный, независимый от движка оркестратор для обработки медиа. Он превращает сложный код и логику CLI в интуитивно понятный **визуальный граф узлов**. Создан для творцов, разработчиков и опытных пользователей, которые ценят мощь и эстетику.

---

### 🎨 Visual & Immersive Experience
Мы верим, что профессиональные инструменты не должны быть скучными.
*   **🌌 Animated Workspaces:** Выбирайте из множества потрясающих анимированных фонов, чтобы вдохновение не покидало вас.
*   **🤝 Sponsorship Hub:** В интерфейсе выделены специальные места для отображения **Спонсоров и Меценатов** — прямо в заголовке и на фонах приложения.
*   **💎 Modern UI:** Гладкий и высокопроизводительный интерфейс на базе React 19, Vite и Framer Motion.

### 🧩 Engine-Agnostic Architecture
Проект построен по модели **"Plugin-Worker"**. Хотя в него глубоко интегрирован FFmpeg, ядро может принять **любой движок**:
*   **Multi-Engine Support:** Запускайте FFmpeg, OpenCV, AI Upscalers или кастомные скрипты в одной цепочке.
*   **Manifest-Driven UI:** Ноды и элементы управления создаются автоматически на основе простого `manifest.json`.
*   **Modular Backend:** Расширяйте возможности, просто добавляя папку в директорию `/plugins`.

---

### 🚀 How to Run

#### 1. Prerequisites
*   **Node.js** (v18.0.0+)
*   **Python** (v3.10+)
*   **FFmpeg** (Рекомендуется для стандартных плагинов)

#### 2. Installation
```bash
# Клонируйте репозиторий
git clone https://github.com
cd ffmpegNode

# Настройка фронтенда
cd frontend
npm install
```

#### 3. Launching the App (Выберите вариант)

**🔵 Option A: The Fast Way (Рекомендуется)**
*Запуск интерфейса и окна Electron одной командой:*
```bash
# В папке /frontend
npm run start
```
*Затем запустите движок логики (в отдельном терминале из корня проекта):*
```bash
python main.py
```

**🟣 Option B: Manual Control (Для разработчиков)**
1. **Start Vite:** `cd frontend && npm run dev`
2. **Start Electron:** `cd frontend && npm run electron`
3. **Start Backend:** `python main.py`

---

### ❤️ Support & Acknowledgments
**ffmpegNode Stream** — это открытый проект, созданный с любовью. Мы предлагаем приоритетное размещение логотипов спонсоров внутри UI приложения.

> **Special Acknowledgement:**
> *Я хотел бы выразить искреннюю благодарность и уважение разработчикам ИИ, который помогал мне в создании этого проекта. Спасибо за создание такого мощного и полезного помощника — ваш труд делает невозможное возможным.*
>
> *Отдельная благодарность разработчикам Microsoft, Google, FFmpeg и всем, кто прямо или косвенно помог реализовать этот проект. Слава Богу за таланты и возможность творить во благо!*

---

### 📜 License
This project is licensed under the **MIT License**.
*FFmpeg is a trademark of Fabrice Bellard. This project is not affiliated with the FFmpeg team.*
