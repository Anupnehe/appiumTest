import os
import sys
import re
from github import Github, Auth
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
LLM_API_KEY = os.getenv("LLM_API_KEY")

def get_llm_review(diff_text):
    """
    Sends the git diff patch directly to Gemini to get targeted code reviews.
    """
    if not LLM_API_KEY:
        print("Warning: LLM_API_KEY is not set.")
        return "LGTM"

    client = genai.Client(api_key=LLM_API_KEY)
    
    system_instruction = """
    You are an expert Senior QA Automation Engineer and Software Developer. 
    Analyze the following git diff (patch format). Identify bugs, security issues, performance problems, or poor automation practices.
    
    You must find and comment on issues in the changed lines.
    
    For every issue you find, output exactly this format:
    LINE: [approximate line number from the patch]
    COMMENT: [Concise, actionable feedback]
    ---
    
    If the changes are fully optimized and correct, output ONLY 'LGTM'. Do not include any other text.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Review this git diff:\n\n{diff_text}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,  # Lower temperature makes it follow formatting rules strictly
            )
        )
        print("--- Raw Gemini Response ---")
        print(response.text)
        print("---------------------------")
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "LGTM"

def parse_comments(llm_output):
    """
    Parses structured LLM output looking for LINE and COMMENT blocks.
    """
    comments = []
    # Split by the separator defined in the system instruction
    blocks = llm_output.split("---")
    for block in blocks:
        line_match = re.search(r"LINE:\s*(\d+)", block)
        comment_match = re.search(r"COMMENT:\s*(.*)", block, re.DOTALL)
        
        if line_match and comment_match:
            try:
                line_num = int(line_match.group(1).strip())
                comment_text = comment_match.group(1).strip()
                comments.append((line_num, comment_text))
            except ValueError:
                continue
    return comments

def review_pull_request(repo_name, pr_number):
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN is not set.")
        return

    # Using the updated non-deprecated Auth method
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    print(f"Analyzing PR #{pr_number}: '{pr.title}'")
    
    # Get the latest commit to bind inline comments to
    latest_commit = pr.get_commits().reversed[0]
    files = pr.get_files()
    
    comments_added = 0

    for file in files:
        if file.patch: # Only review files that have actual code modifications
            print(f"Reviewing file: {file.filename}")
            
            # Send the diff patch directly to Gemini
            review_feedback = get_llm_review(file.patch)
            
            if "LGTM" in review_feedback:
                print(f"No issues found for {file.filename}")
                continue
                
            # Parse the feedback into structured (line_number, comment) tuples
            parsed_issues = parse_comments(review_feedback)
            
            for line_num, comment_text in parsed_issues:
                try:
                    # Post the comment to the specific line of the file in the PR
                    pr.create_review_comment(
                        body=f"🤖 **AI Feedback:** {comment_text}",
                        commit=latest_commit,
                        path=file.filename,
                        line=line_num
                    )
                    comments_added += 1
                    print(f"Added comment on {file.filename} line {line_num}")
                except Exception as e:
                    print(f"Couldn't add comment on line {line_num}: {e}")
                    
    # Post a final summary comment on the general PR thread
    if comments_added > 0:
        pr.create_issue_comment(f"🤖 **Agent Review Complete:** Found {comments_added} issues that need attention.")
    else:
        pr.create_issue_comment("🤖 **Agent Review Complete:** Code looks great! No issues detected. LGTM! 🎉")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        review_pull_request(sys.argv[1], int(sys.argv[2]))
