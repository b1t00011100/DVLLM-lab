# DVLLM Lab (Deliberately Vulnerable LLM)

DVLLM Lab is a deliberately vulnerable web application designed to demonstrate security risks in LLM-integrated systems. Inspired by DVWA, it combines traditional web vulnerabilities with modern LLM-specific attack vectors.

---

## Overview

This project simulates real-world attack scenarios in applications that integrate Large Language Models (LLMs). It allows users to explore how insecure design choices can lead to vulnerabilities such as prompt injection, data leakage, and tool abuse.

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

### Security Modes
- **Low** – Fully vulnerable
- **Medium** – Partial protections
- **High** – Mitigations applied

---

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **LLM:** Mistral (via Ollama) / Mock fallback
- **Frontend:** HTML, CSS, JavaScript

---

## Attack Demonstration (Example Chain)

1. Exploit SQL Injection to bypass login
2. Access admin panel and view sensitive data
3. Use SSRF to query internal endpoints
4. Extract sensitive information (e.g., API keys)

---

## Project Structure

dvllm-lab/<br>
│── app.py <br>
│── templates/ <br>
│── static/<br>
│── database.db (excluded)<br>
│── README.md<br>


---

## Setup Instructions

### 1. Clone the repository
git clone https://github.com/b1t00011100/DVLLM-lab.git

cd DVLLM-lab

### 2. Install dependencies
pip install flask requests beautifulsoup4

### 3. (Optional) Run local LLM
Ensuer Ollama is running with Mistral (or any other model just change the model in def mistralllm()):<br>
ollama run mistral 

### 4. Run the application
python app.py

### 5. Access in browser
http://127.0.0.1:5000/


---

## Security Note

This application is intentionally vulnerable and is designed strictly for educational and testing purposes.

Do not deploy in production environments.

---

## Key Learnings

- Interaction between LLM context and traditional web vulnerabilities
- Risks of unvalidated tool execution (SSRF)
- Impact of prompt injection and memory poisoning
- Importance of input validation and output encoding
- Differences between vulnerable and secure implementations

---

## Future Improvements

- Advanced prompt injection scenarios
- Logging and monitoring of attacks
- Automated vulnerability testing scripts
- Enhanced UI for attack visualization

---

## Author

Aayush Bajpai<br>
Developed as part of a security-focused project to explore LLM and web application vulnerabilities.








