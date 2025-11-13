"""
azure_openai_analyzer_gui.py

A simple Tkinter GUI to:
 - pick a prompt file and a log file
 - run the existing script Azure_OpenAI_log_Analyzer_With_Token_Calculation.py
   by supplying the two file paths as stdin (the script currently reads inputs()
 - capture stdout/stderr from the script and display it live in the GUI
 - display the current contents of the selected log file and refresh it

Requirements:
 - Python 3.8+
 - The same environment used to run the analyzer script (i.e., packages like tiktoken, python-dotenv, openai/Azure SDK) must be installed.
 - Place this GUI file and Azure_OpenAI_log_Analyzer_With_Token_Calculation.py in the same directory OR update the "analyzer_script" path below.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import time

# If your analyzer script is in a different location, change this path
ANALYZER_SCRIPT = "Azure_OpenAI_log_Analyzer_With_Token_Calculation.py"


class AnalyzerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Azure OpenAI Log Analyzer - GUI Launcher")
        self.geometry("950x700")
        self.prompt_path = tk.StringVar()
        self.log_path = tk.StringVar()
        self.script_path = tk.StringVar(value=ANALYZER_SCRIPT)
        self.proc = None

        # Top frame: script path & file selectors
        top_frame = tk.Frame(self, padx=8, pady=8)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Analyzer script:").grid(row=0, column=0, sticky="w")
        tk.Entry(top_frame, textvariable=self.script_path, width=70).grid(row=0, column=1, sticky="we", padx=6)
        tk.Button(top_frame, text="Browse", command=self.browse_script).grid(row=0, column=2, padx=6)

        tk.Label(top_frame, text="Prompt file:").grid(row=1, column=0, sticky="w", pady=(8,0))
        tk.Entry(top_frame, textvariable=self.prompt_path, width=70).grid(row=1, column=1, sticky="we", padx=6, pady=(8,0))
        tk.Button(top_frame, text="Browse", command=self.browse_prompt).grid(row=1, column=2, padx=6, pady=(8,0))

        tk.Label(top_frame, text="Log file:").grid(row=2, column=0, sticky="w", pady=(8,0))
        tk.Entry(top_frame, textvariable=self.log_path, width=70).grid(row=2, column=1, sticky="we", padx=6, pady=(8,0))
        tk.Button(top_frame, text="Browse", command=self.browse_log).grid(row=2, column=2, padx=6, pady=(8,0))

        # Buttons
        btn_frame = tk.Frame(self, padx=8, pady=8)
        btn_frame.pack(fill="x")

        self.run_btn = tk.Button(btn_frame, text="Run Analyzer", command=self.run_analyzer, width=16)
        self.run_btn.pack(side="left", padx=(0,8))

        self.kill_btn = tk.Button(btn_frame, text="Kill Running Process", command=self.kill_process, width=18, state="disabled")
        self.kill_btn.pack(side="left", padx=(0,8))

        tk.Button(btn_frame, text="Open Log File (external)", command=self.open_log_external).pack(side="left", padx=(0,8))
        tk.Button(btn_frame, text="Refresh Log Preview", command=self.refresh_log_preview).pack(side="left", padx=(0,8))

        # Output panes
        panes_frame = tk.Frame(self, padx=8, pady=8)
        panes_frame.pack(fill="both", expand=True)

        # Left: Script stdout/stderr
        left_frame = tk.LabelFrame(panes_frame, text="Script Output (stdout / stderr)", padx=6, pady=6)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0,6))
        self.output_text = scrolledtext.ScrolledText(left_frame, wrap="word", height=30)
        self.output_text.pack(fill="both", expand=True)

        # Right: log file preview
        right_frame = tk.LabelFrame(panes_frame, text="Log File Preview", padx=6, pady=6)
        right_frame.pack(side="right", fill="both", expand=True)
        self.log_preview = scrolledtext.ScrolledText(right_frame, wrap="word", height=30)
        self.log_preview.pack(fill="both", expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief="sunken", anchor="w")
        status_bar.pack(fill="x", side="bottom")

    def browse_script(self):
        path = filedialog.askopenfilename(title="Select analyzer script",
                                          filetypes=[("Python files", "*.py"), ("All files", "*.*")],
                                          initialfile=self.script_path.get() or ANALYZER_SCRIPT)
        if path:
            self.script_path.set(path)

    def browse_prompt(self):
        path = filedialog.askopenfilename(title="Select prompt file",
                                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.prompt_path.set(path)

    def browse_log(self):
        path = filedialog.askopenfilename(title="Select log file",
                                          filetypes=[("Log files", "*.log;*.txt"), ("All files", "*.*")])
        if path:
            self.log_path.set(path)
            self.refresh_log_preview()

    def set_status(self, text):
        self.status_var.set(text)
        self.update_idletasks()

    def run_analyzer(self):
        script = self.script_path.get().strip()
        prompt = self.prompt_path.get().strip()
        log = self.log_path.get().strip()

        if not script or not os.path.isfile(script):
            messagebox.showerror("Missing script", "Please select the analyzer script file.")
            return
        if not prompt or not os.path.isfile(prompt):
            messagebox.showerror("Missing prompt file", "Please select a valid prompt file.")
            return
        if not log:
            messagebox.showerror("Missing log file", "Please select or enter a log file path.")
            return

        # Clear output
        self.output_text.delete("1.0", tk.END)
        self.set_status("Starting analyzer...")
        self.run_btn.config(state="disabled")
        self.kill_btn.config(state="normal")

        # Run in a separate thread to keep GUI responsive
        thread = threading.Thread(target=self._run_process_thread, args=(script, prompt, log), daemon=True)
        thread.start()

    def _run_process_thread(self, script, prompt_path, log_path):
        # Build command to run python script with the same interpreter
        python_executable = sys.executable  # reuse same python
        cmd = [python_executable, script]

        try:
            # Launch subprocess
            self.set_status("Process running...")
            # Provide the prompt_path and log_path as the two lines of stdin the script expects
            self.proc = subprocess.Popen(cmd,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT,
                                         bufsize=1,
                                         universal_newlines=True,
                                         env=os.environ.copy())

            # Send the two lines exactly as the original script expects, then a newline
            input_text = f"{prompt_path}\n{log_path}\n"
            try:
                self.proc.stdin.write(input_text)
                self.proc.stdin.flush()
                # close stdin to indicate no more input
                self.proc.stdin.close()
            except Exception:
                # If writing to stdin fails, still continue and try to capture output
                pass

            # Read stdout line by line and append to the text widget
            for line in self.proc.stdout:
                self.output_text.insert(tk.END, line)
                self.output_text.see(tk.END)

            # Wait for process to finish
            retcode = self.proc.wait()
            self.proc = None
            self.set_status(f"Process exited with code {retcode}")
        except FileNotFoundError:
            messagebox.showerror("Execution error", f"Python executable not found: {sys.executable}")
            self.set_status("Execution error")
        except Exception as e:
            messagebox.showerror("Execution error", f"Error running script:\n{e}")
            self.set_status("Execution error")
        finally:
            self.run_btn.config(state="normal")
            self.kill_btn.config(state="disabled")
            # Refresh log preview after completion (if a log path was provided)
            self.refresh_log_preview()

    def kill_process(self):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.set_status("Terminated process, waiting for shutdown...")
                time.sleep(0.2)
                if self.proc.poll() is None:
                    self.proc.kill()
                self.set_status("Process killed")
            except Exception as e:
                messagebox.showerror("Kill error", f"Failed to kill process: {e}")
            finally:
                self.run_btn.config(state="normal")
                self.kill_btn.config(state="disabled")
        else:
            self.set_status("No running process")

    def refresh_log_preview(self):
        path = self.log_path.get().strip()
        self.log_preview.delete("1.0", tk.END)
        if not path:
            self.log_preview.insert(tk.END, "<No log file selected>")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                self.log_preview.insert(tk.END, content)
        except FileNotFoundError:
            self.log_preview.insert(tk.END, f"<Log file not found: {path}>")
        except Exception as e:
            self.log_preview.insert(tk.END, f"<Error reading log file: {e}>")

    def open_log_external(self):
        path = self.log_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Cannot open", "Select a valid log file to open externally.")
            return
        try:
            if sys.platform.startswith("darwin"):
                subprocess.call(("open", path))
            elif os.name == "nt":
                os.startfile(path)
            elif os.name == "posix":
                subprocess.call(("xdg-open", path))
        except Exception as e:
            messagebox.showerror("Open error", f"Unable to open file externally: {e}")


if __name__ == "__main__":
    app = AnalyzerGUI()
    app.mainloop()
