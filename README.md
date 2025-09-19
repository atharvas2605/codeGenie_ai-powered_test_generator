### codeGenie: LLM-powered UI Test-case and automation script generator ###
 
### Objective
- To enhance the playwright based UI Test Framework by integrating an AI-powered automated workflow that automatically generates and refines UI test cases and automation script based on user-recorded actions.

### Overview
- An initiative taken to build and integrate an AI-powered UI test case and automation script generator. The workflow uses Playwright Codegen to capture user actions and then leverages AI agents to generate and refine test cases based on those actions.

### Workflow Steps
    1. **Set Up Your `.env` File**
        - Before starting, configure your `.env` file with OpenAI credentials and model parameters.
          This file will be automatically loaded by the scripts to securely authenticate and interact with the OpenAI API model.

    2. **Generate or Use Existing Raw Script**  
        The workflow will ask whether you want to generate a new raw script (Y) or use an existing one (N):  
        - **Generate New Script (Y):** Playwright Codegen starts on the Target URL in a new browser window.  
     
            A. User Records UI Actions
                - Users interact with the UI, and Codegen captures these actions.
            B. Generate Base Script
                - The recorded actions are saved as a Python script in:
                    raw_script/generated_script.py

        - **Use Existing Script (N):** If you already have a raw script in the above path, the workflow will skip Codegen and continue with it.
            Note: If you want to use your existing script, then make sure it is stored at raw_script/generated_script.py before starting the workflow.


    3. Generate Functional Test Cases
        - AI Agent uses the captured actions to create test cases and saves them in:
                ai_generated_tests/ai_generated_ui_testcases_<timestamp>.txt

    4. Execute and Validate Generated Code
        - The script is tested.
            If exit code == 0 (i.e., no test failures), the flow proceeds.
            If exit code != 0, the user gets a warning that the raw script validation has failed.
            The flow proceeds regardless of the status of validation whether pass or failed.

    5. Refine generated code with AI Agent
        - Further, AI Agent refines the generated code, applies enhancements, and adds additional test cases using prompt-based inputs.

    6. Final Output
        - The refined code is saved into a Python script for integration into the framework.
            codeGenie_generated_code/ai_refactored_script_<timestamp>.py
    
    7. Execute and Validate CodeGenie refactored code
        - The final AI-refactored script is executed and tested automatically.
        - If the exit code is not zero (indicating failure), the user is prompted to choose:
            Press **Y** to send the script to AI agent for automated fixing with re-try mechanism
            Press **N** to review and fix the script manually.
    
    8. On each retry attempt:
        - AI-fixed script is saved (overwritten) as: 
            autofix_code_and_logs/ai_fixed_script_attempt.py
        - Logs for each attempt are saved to track the refactored script’s failure and retry attempts.

### Result
- This initiative has been successfully integrated into the UI Test Framework and offers a scalable way to:
        - Automatically generates test scripts and test cases from real user actions.
        - Reduces manual effort in writing UI test automation.
        - Improves test coverage by refining scripts with AI-generated logic.
        - Easily integrates into existing UI automation frameworks.
        - Helps quickly create test cases for core application functionalities.
        - Built-in retry mechanism to handle script failures automatically.
        - Keeps a traceable history of logs and retry attempts for troubleshooting.


### Folder Structure 
📁 Project Directory: codeGenie_agentic_ui_test_generator/
 
codeGenie_agentic_ui_test_generator/
├── .env
├── start_workflow.py
├── OpenAI_UI_TestGenerator.py
├── codeGenie_chatbot.py
├── ai_generated_tests/
│   ├── codeGenie_generated_testcases/
│   │   ├── ai_generated_ui_testcases_<DATETIME>.txt
│   ├── codeGenie_generated_code/
│   │   ├── ai_refactored_script_<DATETIME>.py
├── raw_script/
│   ├── generated_code.py
├── autofix_code_and_logs/
│   ├── ai_fixed_script_attempt.py
│   ├── refactored_script_failure.log
│   ├── retry_failure_attempt_1.log
│   ├── retry_failure_attempt_2.log
│   ├── retry_failure_attempt_3.log
 

### Files

/.env
- Stores OpenAI credentials (like API key, Azure Open-AI endpoint, Target URL). Loaded automatically by the script for secure configuration.

/start_workflow.py
- Entry point script to trigger the complete workflow:
    Launches Codegen.
    Invokes AI for test case generation and refinement.
    Manages flow control based on code execution results.

/OpenAI_UI_TestGenerator.py
- Contains the core logic to:
    Initialize OpenAI agents.
    Generate test cases from recorded actions.
    Refactor and enhance generated code using AI.

/raw_script/generated_code.py
- This is the output of Playwright Codegen—raw code generated by recording user interactions on the UI.

/ai_generated_tests/codeGenie_generated_testcases/
- Stores AI-generated test case definitions in .txt format based on recorded UI actions.

/ai_generated_tests/codeGenie_generated_code/
- Stores AI-refined Playwright automation scripts based on the initially generated code.

/autofix_code_and_logs/
- ai_fixed_script_attempt.py → script generated by AI auto-fix, overwritten on each retry.
- Log files for failures in refactored scripts and retry scripts, kept by timestamp.
 
 
 
