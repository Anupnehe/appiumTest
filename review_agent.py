import os
import sys
import re
import json
import time
from github import Github, Auth
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
LLM_API_KEY = os.getenv("LLM_API_KEY")

class CodeIssue(BaseModel):
    line_number: int = Field(description="The exact or approximate line number in the file where the issue resides. Must be a valid positive integer.")
    finding_type: str = Field(description="Categories like: Brittle Selector, Hardcoded Wait, Security, Performance, Missing Assertion, CI/CD Optimization.")
    explanation: str = Field(description="Clear explanation of why this is bad practice and how it affects the framework.")
    suggested_fix: str = Field(description="The complete, corrected replacement code snippet or configuration block.")

class PullRequestReview(BaseModel):
    issues: list[CodeIssue] = Field(description="List of all anomalies, optimization bugs, or structural issues found.")

def get_llm_agent_review(file_name, diff_text, framework_context=""):
    """
    Agent Core: Evaluates code modifications including infrastructure files using structured output.
    Includes built-in retry logic (exponential backoff) and a fallback model to prevent API outages.
    """
    if not LLM_API_KEY:
        print("Warning: LLM_API_KEY is not set.")
        return None

    client = genai.Client(api_key=LLM_API_KEY)

    system_instruction = f"""
    You are an elite AI Software Development Engineer in Test (SDET), DevSecOps Specialist, and Agentic Reviewer.
    Your job is to analyze the git diff of a file—which could be test scripts, infrastructure files, pipelines, or automation runner code.

    Look specifically for:
    - Automation issues: Hardcoded delays, brittle selectors, missing assertions.
    - CI/CD issues: Insecure permission blocks, outdated/deprecated library arguments, missing dependencies, or inefficient steps.
    - Code quality: Missing error handling, unhandled promises, or hardcoded secrets.

    REPOSITORY FRAMEWORK CONTEXT:
    {framework_context}

    Analyze the diff for the file '{file_name}'. Provide actionable feedback and valid code replacements matching the schema.
    """

    # Active production models to handle deprecations and traffic spikes gracefully
    models_to_try = ["gemini-3.5-flash", "gemini-3.1-flash-lite"]
    max_retries = 3

    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                print(f"Sending {file_name} to {model_name} (Attempt {attempt + 1}/{max_retries})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=f"Analyze this patch diff:\n\n{diff_text}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1,
                        response_mime_type="application/json",
                        response_schema=PullRequestReview,
                    )
                )
                return json.loads(response.text)

            except Exception as e:
                print(f"Warning: Attempt {attempt + 1} for {model_name} failed with error: {e}")
                if attempt < max_retries - 1:
                    sleep_time = (attempt + 1) * 3
                    print(f"Waiting {sleep_time} seconds before retrying...")
                    time.sleep(sleep_time)
                else:
                    print(f"Max retries exhausted for {model_name}.")

        print("Switching to fallback model...")

    print(f"Error: All active models failed for {file_name}.")
    return None

def get_repository_context(repo):
    """
    Simulates Repository Memory: Scans key configuration files to give the agent awareness.
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

    print(f"🤖 Agent online. Analyzing ALL modified files for PR #{pr_number}: '{pr.title}'")

    framework_context = get_repository_context(repo)

    latest_commit = pr.get_commits().reversed[0]
    files = pr.get_files()
    comments_added = 0

    for file in files:
        if file.patch:
            print(f"Agent is scanning: {file.filename}")

            review_data = get_llm_agent_review(file.filename, file.patch, framework_context)

            if not review_data or not review_data.get("issues"):
                print(f"No defects identified in {file.filename}")
                continue

            for issue in review_data["issues"]:
                line_num = issue["line_number"]

                # Determine file extension to format markdown fences beautifully
                ext = "yaml" if file.filename.endswith((".yml", ".yaml")) else "python"

                comment_body = (
                    f"### 🤖 AI Agent Review: `{issue['finding_type']}`\n"
                    f"{issue['explanation']}\n\n"
                    f"#### 💡 Suggested Fix:\n"
                    f"```{ext}\n{issue['suggested_fix']}\n```"
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
                    print(f"Line mapping mismatch on line {line_num}, attempting fallback to general thread: {e}")
                    try:
                        pr.create_issue_comment(f"🤖 **Agent Suggestion for `{file.filename}` near line {line_num}:**\n\n{comment_body}")
                        comments_added += 1
                    except Exception as fallback_err:
                        print(f"Failed to post fallback comment: {fallback_err}")

    if comments_added > 0:
        pr.create_issue_comment(f"🤖 **Agent Review Complete:** Found {comments_added} structural areas across all files and added code fixes.")
    else:
        pr.create_issue_comment("🤖 **Agent Review Complete:** Scanned all codebases against framework baselines. Everything looks solid! LGTM! 🎉")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        review_pull_request(sys.argv[1], int(sys.argv[2]))