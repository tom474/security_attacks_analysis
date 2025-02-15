# Security Attacks Analysis  

A project analyzing and simulating **various cybersecurity attacks** on a web-based system, including **SQL Injection, Cross-Site Scripting (XSS), Command Injection, and Denial of Service (DoS)**. The project also implements **security countermeasures** to mitigate these threats.

## Tech Stack  

- Python
- Flask
- SQLite 

## Features  

### Attack Simulations  
- **SQL Injection**: Exploits database vulnerabilities to manipulate or extract sensitive data.  
- **Cross-Site Scripting (XSS)**: Injects malicious scripts that affect user interactions.  
- **Command Injection**: Executes unauthorized system commands through web inputs.  
- **Denial of Service (DoS)**: Overloads the system with excessive requests to disrupt service availability.  

### Security Implementations  
- **Parameterized Queries**: Prevents SQL Injection by using prepared statements.  
- **Input Validation & Output Encoding**: Blocks XSS attacks by sanitizing user inputs.  
- **Secure Command Execution**: Restricts unauthorized system command execution.  
- **Rate Limiting & IP Blocking**: Prevents DoS attacks by limiting excessive requests.  
- **Content Security Policy (CSP)**: Protects against client-side script injections.  
- **Logging & Monitoring**: Tracks suspicious activities for security analysis.  
