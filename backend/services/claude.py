import anthropic
import json
import os
import re
from dotenv import load_dotenv

# Load the .env file so ANTHROPIC_API_KEY is available
load_dotenv()

# Create the Anthropic client — this is the object we use to call Claude
# It automatically reads ANTHROPIC_API_KEY from the environment
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def research_speaker(name: str) -> str:
    """
    Stage 1: Search the web for information about this speaker.
    Returns raw research findings as a string.
    """
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search"
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"""Research this person for the ai.engineer conference: {name}

Find:
- Their current role and company
- Their specific focus area in AI (agents, infra, LLMs, multimodal, reasoning, etc.)
- Any papers, blog posts, or talks from the last 12 months
- Their most notable recent project or contribution
- What they are known for in the AI community

Be specific. Include dates and titles where found.
If you cannot find this person, clearly say "PERSON NOT FOUND"."""
            }
        ]
    )
    
    # Extract the text from Claude's response
    # The response has multiple content blocks, we want the text ones
    result = ""
    for block in response.content:
        if block.type == "text":
            result += block.text
    
    return result


def generate_speaker_profile(name: str, research: str, user_background: str = "") -> dict:
    """
    Stage 2: Take the raw research and generate structured output.
    Returns a dictionary matching our SpeakerResponse schema.
    """

    background = (user_background or "").strip()
    has_background = bool(background)

    if has_background:
        intro_block = f"""USER BACKGROUND (the person who will say intro_line when meeting {name}):
---
{background}
---

For "intro_line": write in first person as this user. The intro_line should read as one continuous natural thought with this flow. Use the pattern below generically so it adapts to {name} and the user's background, not as literal text to copy:

1. Open with the user's name, then a brief natural mention of their role or status from the background above (like their school and what they study, or their job title), woven in conversationally, not announced like a formal title. Example pattern only, do not copy literally: "Hi, I am [name], I study computer science at [school]" or "Hi, I am [name], I am a software engineer at [company]".

2. Then immediately connect to something specific and real from {name}'s recent work or focus area, expressed as genuine interest, not generic enthusiasm.

3. Transition naturally into one relevant detail from the user's own background above, using a connecting phrase like "I actually built" or "I have been working on", described in plain simple terms, not a credential list.

4. Close by drawing a parallel between the user's experience and {name}'s work at a bigger scale, showing genuine understanding of why their problem matters in their specific context. Keep this part slightly more compact since the role mention adds length.

Before writing intro_line, identify the one point of genuine overlap first, then build the whole intro around that single connected idea rather than picking the most impressive detail from each side independently.

The specific detail about {name}'s recent work in part 2 and the user's own background detail in part 3 must be the SAME underlying theme or problem, not two separate unrelated facts connected only by a transition phrase. Pick the one detail from the speaker's research and the one detail from the user's background that genuinely overlap in subject matter, for example both relate to on device inference, or both relate to retrieval pipelines, or both relate to scaling a system. If no genuine overlap exists between the speaker's work and the user's background, skip the user's background entirely in parts 3 and 4 and keep the intro focused only on the speaker. Do not force an unrelated detail in just to include it.

Hard length rule: intro_line must be no more than 3 to 4 sentences total. Write it so it could realistically be said out loud in one breath when walking up to someone, not read like a written paragraph. Combine ideas into fewer, slightly longer sentences rather than many short ones. Keep the genuine interest and parallel parts compact to stay within the limit.

The whole thing should sound like one person talking naturally, not separate statements stapled together. Use simple words, no hyphens, no resume language, no generic small talk. Never list multiple projects. Do not invent details not in the background.
Do not use the name Manaswi unless it appears in the background above."""
        intro_line_placeholder = (
            "3 to 4 sentences max, one breath out loud: name plus brief conversational role or school, "
            "speaker detail and user background detail sharing one overlapping theme, "
            "brief parallel at bigger scale, or speaker only if no genuine overlap"
        )
    else:
        intro_block = f"""For "intro_line": write in first person as someone attending a tech conference meeting {name}. Open with specific genuine interest in something real from {name}'s recent work or focus area from the research above, not generic enthusiasm or small talk. Do not weave in any personal background since none was provided. Example pattern only, do not copy literally: "Hi, I have been looking forward to this because the work you are doing with [specific thing from speaker's research] is something I think about a lot."

Hard length rule: intro_line must be no more than 3 to 4 sentences total. Write it so it could realistically be said out loud in one breath when walking up to someone, not read like a written paragraph. No hyphens, simple plain language."""
        intro_line_placeholder = (
            "3 to 4 sentences max, one breath out loud: specific genuine interest in this speaker's work, "
            "no personal background, compact natural flow"
        )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Based on this research about {name}:

{research}

Write everything below in simple, conversational, natural sounding language. No corporate phrasing, no resume language, no hyphens anywhere in the output. Write the way a real person actually talks when explaining something to a friend.

For "why_they_matter": explain it like you are casually telling someone why this person is worth knowing, in 2 to 3 plain sentences, no jargon-heavy phrasing.

For "questions": write 5 questions that lead to an actual easy conversation, not interview style questions. Each question should reference something concrete and specific from their recent work, but phrase it the way you would naturally ask a person face to face, curious and relaxed, not formal or academic. Avoid vague questions like "what is your opinion on AI" or "tell me about your journey". Make each one easy for the speaker to answer in a relaxed way and easy for the asker to follow up on.

{intro_block}

Generate a JSON object with exactly this structure. Return ONLY the JSON, no explanation, no markdown backticks:

{{
  "name": "{name}",
  "role": "their current job title",
  "company": "their current company or organization",
  "why_they_matter": "2 to 3 plain sentences, casual and concrete, like explaining to a friend why this person is worth knowing",
  "questions": [
    "a natural curious question about something specific they did recently, phrased casually",
    "another relaxed face to face question about their recent work, specific and easy to answer",
    "a casual question that picks up on something concrete from their research, not vague or interviewy",
    "a natural question about where their current project or company is headed, phrased like real conversation",
    "a curious question that shows you noticed something specific in their work, asked in a friendly relaxed way"
  ],
  "intro_line": "{intro_line_placeholder}",
  "found": true
}}

If the research says PERSON NOT FOUND, return this instead:
{{
  "name": "{name}",
  "role": "Unknown",
  "company": "Unknown", 
  "why_they_matter": "Could not find information about this person.",
  "questions": [],
  "intro_line": "",
  "found": false
}}"""
            }
        ]
    )
    
    # Get the text response (concatenate all text blocks)
    raw = ""
    for block in response.content:
        if block.type == "text":
            raw += block.text

    if not raw.strip():
        raise ValueError("Claude returned an empty response when generating speaker profile")
    
    # Parse the JSON string into a Python dictionary
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # If Claude added extra text around the JSON, try to extract it
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])


def get_speaker_profile(name: str, user_background: str = "") -> dict:
    """
    Main function that combines both stages.
    This is what our route will call.
    """
    # Stage 1: research
    research = research_speaker(name)
    
    # Stage 2: generate structured output from research
    profile = generate_speaker_profile(name, research, user_background)
    
    return profile


_GITHUB_USERNAME = r"[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}"


def _github_username_from_value(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    match = re.search(rf"github\.com/({_GITHUB_USERNAME})", value, re.IGNORECASE)
    if match:
        return match.group(1)
    if re.fullmatch(_GITHUB_USERNAME, value):
        return value
    return ""


def _score_github_username(username: str, position: int, text: str, source: str) -> int:
    score = 0
    text_len = max(len(text), 1)

    if position < text_len * 0.35:
        score += 12

    if source == "labeled":
        score += 30
    elif source == "profile_url":
        score += 25
    elif source == "repo_url":
        score -= 20

    before = text[max(0, position - 50) : position].lower()
    if re.search(r"github\s*[:\-]", before):
        score += 18

    if re.search(r"\d", username):
        score += 4

    if len(username) >= 10:
        score += 3

    return score


def _collect_github_candidates(text: str) -> dict[str, int]:
    scores: dict[str, int] = {}
    normalized = text.replace("\n", " ")

    def add(username: str, position: int, source: str, source_text: str) -> None:
        if username.lower() in {"github", "www"} or len(username) < 3 or "." in username:
            return
        key = username.lower()
        points = _score_github_username(username, position, source_text, source)
        scores[key] = max(scores.get(key, 0), points)

    for source_text in (text, normalized):
        for match in re.finditer(
            rf"(?:https?://)?(?:www\.)?github\.com/({_GITHUB_USERNAME})",
            source_text,
            re.IGNORECASE,
        ):
            username = match.group(1)
            after = source_text[match.end() : match.end() + 1]
            source = "repo_url" if after == "/" else "profile_url"
            add(username, match.start(), source, source_text)

        for match in re.finditer(
            rf"(?:GitHub|GITHUB)\s*[:\-]?\s*(?:https?://)?(?:www\.)?github\.com/({_GITHUB_USERNAME})",
            source_text,
            re.IGNORECASE,
        ):
            add(match.group(1), match.start(), "labeled", source_text)

        for match in re.finditer(
            rf"(?:GitHub|GITHUB)\s*[:\-]\s*@?({_GITHUB_USERNAME})(?:\s|,|$)",
            source_text,
            re.IGNORECASE,
        ):
            add(match.group(1), match.start(), "labeled", source_text)

    return scores


def _best_github_username(claude_username: str, resume_text: str) -> str:
    scores = _collect_github_candidates(resume_text)

    if claude_username:
        claude_key = claude_username.lower()
        scores[claude_key] = scores.get(claude_key, 0) + 6

    if not scores:
        return ""

    return max(scores.items(), key=lambda item: item[1])[0]


def _extract_github_from_text(text: str) -> str:
    username = _best_github_username("", text)
    return f"https://github.com/{username}" if username else ""


def _extract_linkedin_from_text(text: str) -> str:
    patterns = [
        r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?",
        r"(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group(0)
            if not url.startswith("http"):
                url = "https://" + url.lstrip("/")
            return url.rstrip("/")
    return ""


def _normalize_github_url(value: str, resume_text: str) -> str:
    claude_username = _github_username_from_value(value)
    best_username = _best_github_username(claude_username, resume_text)
    return f"https://github.com/{best_username}" if best_username else ""


def _normalize_linkedin_url(value: str, resume_text: str) -> str:
    value = (value or "").strip()

    if value:
        if not value.startswith("http"):
            value = "https://" + value.lstrip("/")
        match = re.search(r"linkedin\.com/in/[a-zA-Z0-9_-]+", value, re.IGNORECASE)
        if match:
            return "https://" + match.group(0).lstrip("/").rstrip("/")

    return _extract_linkedin_from_text(resume_text)


def extract_profile_from_resume(resume_text: str) -> dict:
    """
    Takes raw resume text and extracts structured profile data using Claude.
    """
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Extract structured information from this resume text.

Return ONLY valid JSON with this exact structure, no markdown backticks, no explanation:

{{
  "name": "full name",
  "role": "current role or status, e.g. CS student at ASU or Software Engineer at Company",
  "projects": [
    {{
      "name": "project name",
      "desc": "one plain sentence description, no jargon, no metrics list",
      "tech": ["tech1", "tech2", "tech3"]
    }}
  ],
  "skills_summary": "one sentence summary of overall technical strengths",
  "linkedin": "full LinkedIn profile URL starting with https://, or empty string",
  "github": "full GitHub profile URL starting with https://github.com/username only (not a repo URL), or empty string"
}}

Rules for links:
- Search the entire resume for contact info, headers, and footers
- The GitHub profile URL is usually in the contact/header section, NOT in project repo links
- Project entries may list repo URLs like github.com/some-org/repo-name — do NOT use the repo owner as the person's GitHub profile
- Prefer the username shown next to a GitHub label or in the contact block (e.g. github.com/mrudulaeluri29)
- GitHub may appear as a full URL, github.com/username, or GitHub: username — always return https://github.com/username
- LinkedIn may appear as linkedin.com/in/handle — always return the full https URL
- Never return a link to a specific repository, only the user's profile

Extract at most the 4 most significant projects. Resume text:

{resume_text}"""
            }
        ]
    )

    raw = response.content[0].text

    try:
        profile = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        profile = json.loads(raw[start:end])

    profile["github"] = _normalize_github_url(profile.get("github", ""), resume_text)
    profile["linkedin"] = _normalize_linkedin_url(profile.get("linkedin", ""), resume_text)
    return profile