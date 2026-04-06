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

`git clone https://github.com/b1t00011100/DVLLM-lab.git`
`cd DVLLM-lab`
2. Install dependencies
`pip install flask requests beautifulsoup4 python-dotenv`
3. (Optional) Run local LLM

Ensure Ollama is running with Mistral (or any supported model):

`ollama run mistral`

You can change the model inside the mistral_llm() function if needed.

4. Setup environment variables
`cp .env.example .env`

Update values in .env if required.

5. Setup database
`python init_db.py`
`python set_rolesdb.py`

7. Run the application
`python app.py`

8. Access the application

Open in browser:

http://127.0.0.1:5000/

Default Credentials

`Username: admin
Password: admin@123
`

Example Attack Chain
Exploit SQL Injection to bypass login
Access admin panel
View user data and chats
Use SSRF to query internal endpoints
Extract sensitive information (e.g., API key)
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
dvllm-lab/
├── app.py
├── templates/
├── static/
├── init_db.py
├── set_rolesdb.py
├── README.md
├── .gitignore
├── .env.example
Author

Developed as part of a security-focused project to explore LLM and web application vulnerabilities.
