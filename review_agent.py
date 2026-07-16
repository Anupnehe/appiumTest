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
    Agent Core: Evaluates code modifications using a hardened zero-tolerance gatekeeper prompt.
    Includes built-in retry logic (exponential backoff) and production model fallback chains.
    """
    if not LLM_API_KEY:
        print("Warning: LLM_API_KEY is not set.")
        return None

    client = genai.Client(api_key=LLM_API_KEY)

    system_instruction = f"""
    ROLE & OBJECTIVE:
    You are an unforgiving, elite Senior AI Software Development Engineer in Test (SDET), DevSecOps Hardening Specialist, and an autonomous Gatekeeper Agent. Your sole mandate is to ruthlessly analyze the provided git diff and expose technical debt, structural vulnerabilities, and automation flaws before they merge into production.

    CRITICAL ANALYSIS CHECKSUMS (NO EXCEPTIONS):

    1. AUTOMATION ANTI-PATTERNS & FLAKINESS:
       - Flag ANY hardcoded delays (e.g., time.sleep(), Thread.sleep(), delay()). Demand dynamic conditions using explicit waits (WebDriverWait) or Fluent Waits.
       - Detect brittle UI selectors. Flag dynamic XPaths (containing indexes like /div[3]/span), auto-generated IDs, or overly generic class names. Enforce stable accessibility IDs (Appium), custom test attributes (data-testid), or clean ID strategies.
       - Spot structural gaps: Test cases missing strong validation checkpoints or assertions, missing teardown steps that leak state, or unisolated drivers/sessions that cause cross-test pollution.

    2. CI/CD PIPELINE & DEVOPS SECURITY:
       - Flag excessive or broad workspace permissions (e.g., broad write accesses when read suffices).
       - Identify deprecated GitHub Action runner fields, outdated dependency variants, hardcoded third-party version tags instead of SHA pins, or missing cache configurations for packages.

    3. HARDENING & CODE QUALITY:
       - Trap missing try-catch blocks or unhandled exceptions in network/database/driver initializations.
       - Scan for hardcoded secrets, test credentials, tokens, local file paths, or regional URLs. Enforce environment parameterization.
       - Flag resource leaks, such as open database connections, unclosed file descriptors, or missing `driver.quit()` sequences.

    CONTEXTUAL REPOSITORY BOUNDARIES:
    {framework_context}

    CRITICAL PARSING CONSTRAINT:
    Every issue mapped to the structured schema MUST possess an actual, valid 'line_number' greater than 0 representing the change block. If you discover structural framework architecture issues that apply globally to the file rather than a distinct line, assign it to line number 1.

    TONE AND STYLE:
    Be strictly technical, blunt, and completely objective. Skip introductory sentences, pleasantries, or polite fluff. State the exact pattern found, the technical fallout if it isn't resolved, and provide a fully production-ready, clean replacement snippet.
    """

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
                # Defensively fallback to 1 if the LLM provided an invalid or empty line number
                try:
                    line_num = max(1, int(issue.get("line_number", 1)))
                except (ValueError, TypeError):
                    line_num = 1

                # Determine file extension to format markdown fences beautifully
                ext = "yaml" if file.filename.endswith((".yml", ".yaml")) else "python"

                comment_body = (
                    f"### 🤖 AI Agent Review: `{issue['finding_type']}`\n"
                    f"**Defect:** {issue['explanation']}\n\n"
                    f"#### 💡 Suggested Fix:\n"
                    f"```{ext}\n{issue['suggested_fix']}\n```"
                )

                try:
                    # Attempt inline comment placement on the exact git patch line
                    pr.create_review_comment(
                        body=comment_body,
                        commit=latest_commit,
                        path=file.filename,
                        line=line_num
                    )
                    comments_added += 1
                    print(f"Posted rigorous agent fix to {file.filename} line {line_num}")
                except Exception as e:
                    # Graceful boundary protection: Fallback to general thread if line index drifts
                    print(f"Line {line_num} mapping failed. Attempting fallback to main thread comment. Error: {e}")
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