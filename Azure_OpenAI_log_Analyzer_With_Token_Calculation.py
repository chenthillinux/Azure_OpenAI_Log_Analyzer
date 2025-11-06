import os
import datetime
import tiktoken
from dotenv import load_dotenv
from openai import AzureOpenAI

# === Load environment variables ===
load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

# === Azure OpenAI client ===
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_KEY,
    api_version=API_VERSION
)

deployment = "gpt-4.1"  # Model deployment name
TOKEN_LIMIT = 13000  # Max allowed tokens (13K)


# === Utility functions ===

def read_file_content(file_path, file_type="prompt"):
    """Read the content of a file safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"[ERROR] {file_type.capitalize()} file not found: {file_path}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to read {file_type} file: {e}")
        return None


def write_log(message, log_file_path):
    """Append a timestamped log message to the log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"[{timestamp}] {message}\n")


def count_tokens(text, model="gpt-4o"):
    """Count the number of tokens in a given text using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback if model not found
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def check_token_limits(prompt_text, log_text, log_file_path):
    """Check total tokens and warn if exceeding limits."""
    prompt_tokens = count_tokens(prompt_text)
    log_tokens = count_tokens(log_text)
    total_tokens = prompt_tokens + log_tokens

    print(f"\n[Token Usage]")
    print(f"Prompt file tokens: {prompt_tokens}")
    print(f"Log file tokens: {log_tokens}")
    print(f"Total tokens: {total_tokens}")

    write_log(f"Token count - Prompt: {prompt_tokens}, Log: {log_tokens}, Total: {total_tokens}", log_file_path)

    if total_tokens > TOKEN_LIMIT:
        warning = f"[WARNING] Total tokens ({total_tokens}) exceed limit ({TOKEN_LIMIT})!"
        print(warning)
        write_log(warning, log_file_path)
        return False
    return True


# === Main function ===

def main():
    prompt_file_path = input("Enter path to prompt file: ").strip()
    log_file_path = input("Enter path to log file: ").strip()

    prompt_content = read_file_content(prompt_file_path, "prompt")
    if not prompt_content:
        return

    log_content = read_file_content(log_file_path, "log") or ""

    write_log("Starting analysis...", log_file_path)

    # === Token check ===
    if not check_token_limits(prompt_content, log_content, log_file_path):
        print("Aborting: token limit exceeded.")
        return

    try:
        # === API Request ===
        response = client.chat.completions.create(
            model=deployment,
            max_completion_tokens=4096,  # model output limit
            messages=[
                {"role": "system", "content": "Expert Linux debugging engineer"},
                {"role": "user", "content": prompt_content}
            ]
        )

        answer = response.choices[0].message.content
        print("\n=== Response ===\n")
        print(answer)

        write_log("Analysis completed successfully.", log_file_path)
        write_log("Response:\n" + answer, log_file_path)

    except Exception as e:
        error_msg = f"Error during API call: {e}"
        print(error_msg)
        write_log(error_msg, log_file_path)


if __name__ == "__main__":
    main()
