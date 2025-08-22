import subprocess
import os
import sys
import openai
from pathlib import Path
from OpenAI_UI_TestGenerator import *

# === Load .env file ===
load_dotenv()

# === Get Target URL from .env ===
url = os.getenv("TARGET_URL")

# === Base directory where this script resides ===
BASE_DIR = Path(__file__).resolve().parent

# Output file for the recorded script
#output_file = BASE_DIR/"codegen_script"/"codegen_generated_code.py"
output_file = "raw_script/generated_code.py"

# Ensure directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

print("Workflow started.")

# Ask the user whether to generate a new raw script or use the existing one
choice = input("\nDo you want to generate a new raw script using Playwright Codegen? (Y/N): ")

if choice.strip().lower() == "y":
    # Run Playwright's codegen with output redirected
    process = subprocess.Popen(
        ["playwright", "codegen", f"--target=python", f"--output={output_file}", url]
    )
    print("Playwright codegen started. Perform your actions in the browser window.")
    process.wait()

else:
    print("You opted to use the existing raw script instead of generating a new one.\n")

print(f"Raw script is saved to: {output_file}")


# Run the OpenAI_UI_TestGenerator.py script
print("Running the AI agent to generate functional test cases...\n")
#subprocess.run(["python", "OpenAI_UI_TestGenerator.py"])

# Call the function with desired mode
generate_ui_test_cases_refactor_codegen_script(prompt_type="testcases")


# Run the codegen generated script
print("\nTesting the Raw script. \nPlease wait...\n")
run_result = subprocess.run(["python", output_file])

# Check exit code
if run_result.returncode != 0:
    #print("Codegen generated code has failures... kindly check logs and fix the failure and try again.")
    print("Warning: The raw script did not pass validation.")
    print("Initiating AI-powered refactoring... please wait.")

    #sys.exit(1)
else:
    print("Raw generated script has no failures.")
    print("Initiating AI-powered refactoring... please wait.")

# Run AI enhancement script and capture the generated script filename
refactored_script = generate_ui_test_cases_refactor_codegen_script(prompt_type="refactor")

# Test the refactored script and capture logs
print("\nTesting the AI-refactored script. Please wait...")
run_refined = subprocess.run(["python", refactored_script],
    capture_output=True,
    text=True)

# Collect logs for failed refactor script
initial_logs = f"STDOUT:\n{run_refined.stdout}\n\nSTDERR:\n{run_refined.stderr}"

#logs_dir = BASE_DIR / "autofix_code_and_logs"
logs_dir = "autofix_code_and_logs"
# Ensure the folder exists
os.makedirs(logs_dir, exist_ok=True)

#logs_file = logs_dir / "refactored_script_execution.log"
logs_file = f"{logs_dir}/refactored_script_execution.log"

# Save logs to file (optional, for debugging)
with open(logs_file, "w", encoding="utf-8") as f:
    f.write(initial_logs)
print("Initial logs saved to: ",logs_file)

if run_refined.returncode != 0:
    print("\nThe AI-refactored script failed and requires your attention. Please review the generated script.")
    choice = input("\nDo you want to send this code to codeGenie to fix the issue? (press Y to continue, N to fix manually): ")
    if choice.strip().lower() == 'y':
        print("Sending code to codeGenie AI agent to fix the issue...")
        # Read initial script content
        with open(refactored_script, "r", encoding="utf-8") as f:
            initial_script_code = f.read()
        # Function or subprocess call to trigger the AI fix
        print("Running retry mechanism...")
        success = retry_fix_codegenie_script_with_logs(
            script_path=refactored_script,
            initial_script_code=initial_script_code,
            initial_logs=initial_logs,
            max_retries=3
        )
        if success:
            print("Retry mechanism fixed and script passed!")
            print("\nHooray! The AI-refactored script executed successfully — you just automated a flow without writing any code!")
        else:
            print("Retry mechanism couldn't fix the script automatically.")
    else:
        print("You chose to fix the error manually.")
else:
    print("\nHooray! The AI-refactored script executed successfully — you just automated a flow without writing any code!")

