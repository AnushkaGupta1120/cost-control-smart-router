# ⚡ Cost-Control Smart Router

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20|%20React%20|%20MySQL-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## 📖 Overview
The **Cost-Control Smart Router** is an intelligent AI Gateway designed to optimize Large Language Model (LLM) usage costs. Instead of sending every query to an expensive model like GPT-4, this router analyzes the "difficulty" of a user's prompt and automatically routes it to the most cost-effective model capable of handling the task.

It simulates a real-world enterprise "FinOps" tool, tracking token usage, latency, and **money saved** compared to using a flagship model for everything.

## 🚀 Key Features
* **🧠 Intelligent Routing Logic:**
    * **Tier 1 (Simple):** Routes to *Llama 3.1 8B* (Free/Low Cost).
    * **Tier 2 (Medium):** Routes to *Llama 3.3 70B* (for reasoning).
    * **Tier 3 (Hard/Live):** Routes to *Gemini 2.0 Flash Lite* (with Internet Access) for complex queries or real-time data.
* **📊 Live Analytics Dashboard:** Real-time visualization of cost savings, model usage distribution, and request logs using **React** & **Recharts**.
* **🛡️ Smart Fallback System:** Automatically switches to backup models if a provider hits rate limits (Error 429) or goes offline.
* **💬 Modern Chat Interface:** A ChatGPT-style UI with auto-scrolling, typing indicators, and metadata tags showing which model was used.
* **💾 Robust Logging:** Stores detailed request logs in **MySQL** for auditing and analysis.

## 🛠️ Tech Stack
| Component | Technology |
| :--- | :--- |
| **Backend** | Python, FastAPI, SQLAlchemy |
| **Frontend** | React.js (Vite), Axios, Recharts, Lucide-React |
| **Database** | MySQL (with `cryptography` auth) |
| **AI Providers** | OpenRouter (Unified API for Llama & Gemini) |
| **Tools** | Uvicorn, Dotenv, Pydantic |

## 🏗️ Architecture
1.  **User Request:** React Frontend sends prompt to FastAPI.
2.  **Classification:** Router analyzes prompt length and keywords (e.g., "2025", "code", "latest").
3.  **Model Selection:**
    * *Simple* -> Llama 8B
    * *Complex* -> Gemini 2.0 (via OpenRouter)
4.  **Execution:** API Call is made; response is received.
5.  **Logging:** Request metadata (tokens, cost, savings) is saved to MySQL.
6.  **Response:** Answer is returned to the UI with a "Savings" badge.

<img width="1906" height="909" alt="image" src="https://github.com/user-attachments/assets/9caee9af-a188-48a7-ad4c-a85783a171a4" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/822d827b-1439-4b6a-bd6a-519a680f7cc1" />



## ⚙️ Installation & Setup

### Prerequisites
* Python 3.10+
* Node.js & npm
* MySQL Server

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/smart-router.git](https://github.com/yourusername/smart-router.git)
cd smart-router
