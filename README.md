# 🧠 Azure OpenAI Log Analysis Tool

A Python utility for analyzing large system log files and generating insights using **Azure OpenAI GPT models**.  
This tool reads a **prompt file** and a **log file**, checks their combined token usage using `tiktoken`, and then performs an in-depth AI-based analysis if the total token count is within a safe limit (default: 13K tokens).

---

## 🚀 Features

- ✅ Reads prompt and log files dynamically  
- ✅ Uses `.env` for secure environment variable management  
- ✅ Calculates token usage via **tiktoken** before making API calls  
- ✅ Prevents exceeding token limits (13,000 by default)  
- ✅ Logs every step with timestamps  
- ✅ Integrates directly with **Azure OpenAI Service**

---

## 📁 Project Structure

```
.
├── .env
├── analyzer.py
├── README.md
├── prompt_example.json
└── sample_log.txt
```

---

## ⚙️ Setup Instructions

### 1️⃣ Prerequisites
- Python **3.9+**
- Azure OpenAI resource deployed with GPT model (e.g., `gpt-4.1` or `gpt-4o`)
- `.env` file configured with your Azure credentials

---

### 2️⃣ Install Dependencies

```bash
pip install openai python-dotenv tiktoken
```

---

### 3️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```ini
AZURE_OPENAI_ENDPOINT=https://<your-resource-name>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-azure-api-key>
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

---

### 4️⃣ Prepare Input Files

- **Prompt file:** Contains your question or instructions for the model (plain text or JSON).  
- **Log file:** Contains system or application logs to be analyzed.

Example:

`prompt_example.json`
```json
{
  "instruction": "Analyze the following log for OOM (Out Of Memory) errors and summarize key causes.",
  "focus": ["memory usage", "process IDs", "kernel messages"]
}
```

`sample_log.txt`
```
[2025-11-05 12:15:42] kernel: Out of memory: Kill process 1123 (java) score 945 or sacrifice child
[2025-11-05 12:15:43] Killed process 1123 (java) total-vm: 1023456kB, anon-rss: 965000kB
```

---

### 5️⃣ Run the Script

```bash
python analyzer.py
```

You’ll be prompted to enter:
- Path to the prompt file  
- Path to the log file  

Example:
```
Enter path to prompt file: ./prompt_example.json
Enter path to log file: ./sample_log.txt
```

---

## 🧮 Token Management

Before sending data to Azure OpenAI, the script:
- Calculates token usage for both the **prompt** and **log** using `tiktoken`
- Displays detailed token usage summary:
  ```
  [Token Usage]
  Prompt file tokens: 250
  Log file tokens: 800
  Total tokens: 1050
  ```
- Aborts automatically if token usage exceeds the limit (default 13,000)

You can adjust the token limit by modifying:

```python
TOKEN_LIMIT = 13000
```

---

## 🪵 Log Output Example

The script writes logs with timestamps to your specified log file:

```
[2025-11-06 12:30:10] Starting analysis...
[2025-11-06 12:30:11] Token count - Prompt: 250, Log: 800, Total: 1050
[2025-11-06 12:30:13] Analysis completed successfully.
[2025-11-06 12:30:13] Response:
Root cause: OOM error triggered by excessive Java heap memory usage...
```

---

## 🧰 Key Functions

| Function | Purpose |
|-----------|----------|
| `read_file_content()` | Reads content from prompt/log file safely |
| `write_log()` | Appends timestamped messages to the log file |
| `count_tokens()` | Counts token usage using `tiktoken` |
| `check_token_limits()` | Checks and validates total token usage |
| `main()` | Orchestrates the workflow and calls Azure OpenAI API |

---

## 🧩 Notes

- Recommended models: `gpt-4.1` or `gpt-4o`
- Update `deployment` variable with your Azure OpenAI model deployment name
- Handles both text and JSON prompt inputs seamlessly

---

## 📜 License

This project is released under the **MIT License** — feel free to use and modify it for your needs.
