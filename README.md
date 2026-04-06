# DVLLM Lab (Deliberately Vulnerable LLM)

DVLLM Lab is a deliberately vulnerable web application designed to demonstrate security risks in LLM-integrated systems. Inspired by DVWA, it combines traditional web vulnerabilities with modern LLM-specific attack vectors.

---

## Overview

This project simulates real-world attack scenarios in applications that integrate Large Language Models (LLMs). It highlights how insecure design can lead to vulnerabilities such as prompt injection, data leakage, and tool abuse.

The application includes configurable security levels to demonstrate both vulnerable and secure implementations.

---

## Features

### LLM Vulnerabilities
- Prompt Injection
- Data Poisoning (context manipulation)
- Insecure Output Handling (XSS)
- SSRF via tool/function execution

### Web Vulnerabilities
- SQL Injection (authentication bypass)
- Broken Access Control
- IDOR (Insecure Direct Object Reference)
- Sensitive Data Exposure

### Security Levels
- **Low** – Fully vulnerable  
- **Medium** – Partial protections  
- **High** – Mitigations applied  

---

## Tech Stack

- Backend: Flask (Python)
- Database: SQLite
- LLM: Mistral (via Ollama) / Mock fallback
- Frontend: HTML, CSS, JavaScript

---

## Setup Instructions

### 1. Clone the repository

`git clone https://github.com/b1t00011100/DVLLM-lab.git`<br>
`cd DVLLM-lab`<br>

### 2. Install dependencies<br>
`pip install flask requests beautifulsoup4 python-dotenv`<br>

### 3. (Optional) Run local LLM

Ensure Ollama is running with Mistral (or any supported model):<br>

`ollama run mistral`<br>

You can change the model inside the mistral_llm() function if needed.

### 4. Setup environment variables<br>
`cp .env.example .env`<br>

Update values in .env if required.

### 5. Setup database
`python init_db.py`<br>
`python set_rolesdb.py`<br>

### 6. Run the application<br>
`python app.py`

### 7. Access the application

Open in browser:<br>

http://127.0.0.1:5000/

Default Credentials<br>

`admin:admin@123
`
<br>

Example Attack Chain
Exploit SQL Injection to bypass login<br>
Access admin panel<br>
View user data and chats<br>
Use SSRF to query internal endpoints<br>
Extract sensitive information (e.g., API key)<br>
Security Note

This application is intentionally vulnerable and designed strictly for educational and testing purposes.

Do not deploy in production environments.

Key Learnings
Interaction between LLM context and traditional web vulnerabilities
Risks of unvalidated tool execution (SSRF)
Impact of prompt injection and memory poisoning
Importance of input validation and output encoding
Differences between vulnerable and secure implementations
Project Structure
dvllm-lab/<br>
├── app.py<br>
├── templates/<br>
├── static/<br>
├── init_db.py<br>
├── set_rolesdb.py<br>
├── README.md<br>
├── .gitignore<br>
├── .env.example<br>

Author
Aayush Bajpai
Developed as part of a security-focused project to explore LLM and web application vulnerabilities.
