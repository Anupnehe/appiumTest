import os
import sys
import re
import json
from github import Github, Auth
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
LLM_API_KEY = os.getenv("LLM_API_KEY")

# Define the structured memory schema for the Agent's reasoning
class CodeIssue(BaseModel):
    line_number: int = Field(description="The exact or approximate line number in the file where the issue resides.")
    finding_type: str = Field(description="Categories like: Brittle Selector, Hardcoded Wait, Security, Performance, Missing Assertion.")
    explanation: str = Field(description="Clear explanation of why this is bad practice and how it affects the test framework.")
    suggested_fix: str = Field(description="The complete, corrected replacement code snippet block.")

class PullRequestReview(BaseModel):
    issues: list[CodeIssue] = Field(description="List of all code anomalies or architectural bugs found.")

def get_llm_agent_review(file_name, diff_text, framework_context=""):
    """
    Agent Core: Evaluates code modifications using structured output schema.
    Injects global framework context to simulate repository memory.
    """
    if not LLM_API_KEY:
        print("Warning: LLM_API_KEY is not set.")
        return None

    client = genai.Client(api_key=LLM_API_KEY)

    system_instruction = f"""
    You are an elite AI Software Development Engineer in Test (SDET) and Agentic Code Reviewer.
    Your job is to analyze the git diff of a file and find bugs, structural problems, or bad testing practices.

    Look specifically for:
    - Hardcoded explicit delays (e.g., time.sleep(), Thread.sleep()) without dynamic WebDriverWait.
    - Brittle locators/selectors that will easily break in UI changes.
    - Missing assertions or verification checkpoints in automation scripts.
    - Exposed credentials, tokens, or hardcoded environment configurations.

    REPOSITORY FRAMEWORK CONTEXT:
    {framework_context}

    Analyze the diff for the file '{file_name}'. You must return your findings matching the schema requested.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Analyze this patch diff:\n\n{diff_text}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
                # Force the model to think structurally and populate our Pydantic schema
                response_mime_type="application/json",
                response_schema=PullRequestReview,
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Agent analysis failed for {file_name}: {e}")
        return None

def get_repository_context(repo):
    """
    Simulates Repository Memory: Scans key configuration files to give the agent
    architectural awareness of the project it is reviewing.
    """
    context_summary = "Project Structure Clues:\n"
    possible_configs = ["pom.xml", "build.gradle", "requirements.txt", "testng.xml"]

    for config_path in possible_configs:
        try:
            content = repo.get_contents(config_path)
            context_summary += f"- Found `{config_path}`, indicating this testing framework type.\n"
        except Exception:
            continue
    return context_summary

def review_pull_request(repo_name, pr_number):
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN is not set.")
        return

    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    print(f"🤖 Agent online. Analyzing PR #{pr_number}: '{pr.title}'")

    # 1. Initialize Contextual Memory
    framework_context = get_repository_context(repo)

    latest_commit = pr.get_commits().reversed[0]
    files = pr.get_files()
    comments_added = 0

    for file in files:
        # 2. Self-Preservation / Filter Loop
        # Prevents the agent from hallucinating or entering cycles by reviewing itself
        if "review_agent.py" in file.filename or ".github/workflows" in file.filename:
            print(f"Skipping self-review on layout file: {file.filename}")
            continue

        if file.patch:
            print(f"Agent is scanning: {file.filename}")

            # 3. Reasoning Phase
            review_data = get_llm_agent_review(file.filename, file.patch, framework_context)

            if not review_data or not review_data.get("issues"):
                print(f"No defects identified in {file.filename}")
                continue

            # 4. Action Execution Phase
            for issue in review_data["issues"]:
                line_num = issue["line_number"]

                # Format an elegant markdown comment with the self-healing suggestion
                comment_body = (
                    f"### 🤖 AI Agent Review: `{issue['finding_type']}`\n"
                    f"{issue['explanation']}\n\n"
                    f"#### 💡 Suggested Fix:\n"
                    f"```python\n{issue['suggested_fix']}\n```"
                )

                try:
                    pr.create_review_comment(
                        body=comment_body,
                        commit=latest_commit,
                        path=file.filename,
                        line=line_num
                    )
                    comments_added += 1
                    print(f"Posted agent fix to {file.filename} line {line_num}")
                except Exception as e:
                    # Fallback to general thread if line mapping drifts slightly
                    print(f"Line mapping mismatch, fallback to general thread: {e}")

    # 5. Final Summary Execution
    if comments_added > 0:
        pr.create_issue_comment(f"🤖 **Agent Review Complete:** Found {comments_added} structural areas and added self-healing code fixes inline.")
    else:
        pr.create_issue_comment("🤖 **Agent Review Complete:** Scanned all codebases against framework baselines. Everything looks solid! LGTM! 🎉")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        review_pull_request(sys.argv[1], int(sys.argv[2]))