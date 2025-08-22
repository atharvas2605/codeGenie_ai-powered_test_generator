import openai
from datetime import datetime
import os
from openai import AzureOpenAI
from langchain_openai import AzureChatOpenAI
from pathlib import Path
from dotenv import load_dotenv
import subprocess

# Define the path to your .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# Load the environment variables from the specified file
load_dotenv(dotenv_path)

# Access the env variables
openai_azure_endpoint = os.getenv('API_ENDPOINT')
openai_api_key = os.getenv('API_KEY')
openai_api_version = os.getenv('API_VERSION')
model_temperature = float(os.getenv('MODEL_TEMPERATURE', '0.5'))  # Default to 0.5 if not set
model_type = os.getenv('MODEL_TYPE')
model_max_tokens = int(os.getenv('MODEL_MAX_TOKENS', '1500'))  # Default to 1500 if not set
functional_testcase = os.getenv('PROMPT_FUNCTIONAL_TESTCASE')
generate_ui_auto_script = os.getenv('PROMPT_GENERATE_UI_AUTO_SCRIPT')

# === Initialize OpenAI Client ===
client = AzureOpenAI(
    azure_endpoint=openai_azure_endpoint,
    api_key=openai_api_key,
    api_version=openai_api_version
)

# === Base directory where this script resides ===
BASE_DIR = Path(__file__).resolve().parent

#Set this path to use codegenie for your existing script
raw_script = "raw_script/generated_code.py"

#raw_script = BASE_DIR/"raw_script"/"generated_code.py"


def generate_ui_test_cases_refactor_codegen_script(prompt_type: str = "testcases"):
    # ===Read generated base script ===
    with open(raw_script, "r",encoding="utf-8") as f:
        base_script = f.read()
    if prompt_type == "testcases":
        # ===Prepare prompt for OpenAI ===
        prompt = f"""
        {functional_testcase}
        Script:
        {base_script}
        """
        # ===Save the generated test cases to a file ===
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #output_dir = BASE_DIR/"ai_generated_tests"/"codeGenie_generated_testcases"
        output_dir = "ai_generated_tests/codeGenie_generated_testcases"
        os.makedirs(output_dir, exist_ok=True)
        #output_file = output_dir/f"ai_generated_ui_testcases_{timestamp}.txt"
        output_file = f"{output_dir}/ai_generated_ui_testcases_{timestamp}.txt"
    
    elif prompt_type == "refactor":
        prompt =f"""
            {generate_ui_auto_script}
            
            ### Here is the code to refactor: {base_script}

            """

        # === Save the generated test cases to a file ===
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #output_dir = BASE_DIR/"ai_generated_tests"/"codeGenie_generated_testcases"
        output_dir = "ai_generated_tests/codeGenie_generated_code"
        os.makedirs(output_dir, exist_ok=True)
        #output_file = output_dir/f"ai_refactored_script_{timestamp}.py"
        output_file = f"{output_dir}/ai_refactored_script_{timestamp}.py"
    else:
        raise ValueError("Invalid prompt_type. Use 'testcases' or 'refactor'.")


    response = client.chat.completions.create(
        model=model_type,
        temperature=model_temperature,
        max_tokens=model_max_tokens,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    # print(response)
    generated_code = response.choices[0].message.content


    # ===Create Output Directory (if not exists) ===
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # === Write Generated Content to File ===
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(generated_code)

    print(f"codeGenie Generated output saved to: {output_file}")
    return output_file


#generate_ui_test_cases_refactor_codegen_script(prompt_type="testcases")
#generate_ui_test_cases_refactor_codegen_script(prompt_type="refactor")

def retry_fix_codegenie_script_with_logs(
    script_path: str,
    initial_script_code: str,
    initial_logs: str,
    max_retries: int = 3
):
    """
    Retry mechanism:
    - Accepts initial script & logs
    - Calls LLM to fix the script
    - Runs script - If fails, captures new logs & script, retries until success or max_retries
    """
    print(f"\nStarting retry mechanism for script: {script_path}")
    # Create folder if not exists
    os.makedirs("autofix_code_and_logs", exist_ok=True)

    #refactored_script_failure_log=BASE_DIR/"autofix_code_and_logs"/"refactored_script_failure.log"
    refactored_script_failure_log = "autofix_code_and_logs/refactored_script_execution.log"

    # Save initial logs
    with open(refactored_script_failure_log, "w", encoding="utf-8") as f:
        f.write(initial_logs)
    print("Initial logs saved to: autofix_code_and_logs/refactored_script_execution.log")

    # Save initial script before starting retries
    #retry_script_file = BASE_DIR/"autofix_code_and_logs"/"ai_fixed_script_attempt.py"
    retry_script_file = "autofix_code_and_logs/ai_fixed_script_attempt.py"
    with open(retry_script_file, "w", encoding="utf-8") as f:
        f.write(initial_script_code)
    print(f"Initial script saved to: {retry_script_file}")
    def build_retry_prompt(script_code: str, logs: str) -> str:
        return f"""
Role: You are a senior SDET expert with deep expertise in Python, Playwright, and robust UI automation practices.
Task: Analyze the provided Python Playwright script and its corresponding failure log. Your objective is to identify the root cause of the error documented in the log and apply a precise fix to the script.

Input:
    Failing Refactored Python Playwright Script: {script_code}
    Corresponding Failure Log: {logs}
    Script with correct locators: {raw_script}

Output Requirements:
   - Do **not** include markdown formatting, fenced code blocks (like python ``` code ```), or any explanation in the output — provide **only** the final, complete, runnable Python script.
   - Your response must be only the complete, corrected, and runnable Python script.
   - Do not provide any explanations, analysis, or comments about the changes.
   - Keep and reuse the existing/raw Playwright locators and functions as provided.
   - Do not replace the original locators or functions with AI-generated ones.
   - Do not include any introductory or concluding sentences.
   - The final output must be a single, clean code block, ready for CI/CD pipeline execution.
"""

    current_script_code = initial_script_code
    current_logs = initial_logs

    for attempt in range(1, max_retries + 1):
        print(f"\nAttempt #{attempt}: calling OpenAI to fix the script...")

        # Build prompt & call OpenAI
        prompt = build_retry_prompt(current_script_code, current_logs)
        try:
            response = client.chat.completions.create(
                model=model_type,
                temperature=model_temperature,
                max_tokens=model_max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            fixed_code = response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            return False

        # Overwrite script with fixed code
        try:
            with open(retry_script_file, "w", encoding="utf-8") as f:
                f.write(fixed_code)
            print(f"Script updated from LLM fix (attempt #{attempt})")
        except Exception as e:
            print(f"Failed to overwrite script: {e}")
            return False

        print(f"Running fixed script in headless mode...")

        # Run script in headless mode
        run_result = subprocess.run(
            ["python", retry_script_file],
            capture_output=True,
            text=True,
            env={**os.environ, "PLAYWRIGHT_HEADLESS": "1"}
        )

        if run_result.returncode == 0:
            print("Script executed successfully!")
            return True

        print(f"Script failed again (exit code: {run_result.returncode})")

        # Capture new logs & script for next attempt
        current_logs = f"STDOUT:\n{run_result.stdout}\n\nSTDERR:\n{run_result.stderr}"

        # Save logs for debugging
        #log_file = BASE_DIR / "autofix_code_and_logs" / f"retry_failure_attempt_{attempt}.log"
        log_file = f"autofix_code_and_logs/retry_failure_attempt_{attempt}.log"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(current_logs)
        print(f"Saved failure logs to: {log_file}")

        try:
            with open(retry_script_file, "r", encoding="utf-8") as f:
                current_script_code = f.read()
        except Exception as e:
            print(f"Failed to read updated script: {e}")
            return False

    print(f"Script failed after {max_retries} retries.")
    return False





