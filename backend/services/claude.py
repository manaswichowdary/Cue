import anthropic
import html
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
                "name": "web_search",
                "max_uses": 3,
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


DEFAULT_PORTFOLIO_THEME = {
    "background": "#f0ece6",
    "heading_color": "#a47864",
    "card_bg": "#ffffff",
    "card_border": "#aaabca",
    "body_text": "#2e2a3d",
    "button_bg": "#6c6c9b",
    "button_text": "#ffffff",
}

DEFAULT_PORTFOLIO_FONT = 'Georgia, "Times New Roman", serif'


def _resolve_portfolio_theme(theme: dict | None) -> dict:
    resolved = dict(DEFAULT_PORTFOLIO_THEME)
    if theme:
        for key in DEFAULT_PORTFOLIO_THEME:
            value = theme.get(key)
            if value:
                resolved[key] = str(value).strip()
    return resolved


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _rgba(hex_color: str, alpha: float) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    return f"rgba({r}, {g}, {b}, {alpha})"


def _relative_luminance(hex_color: str) -> float:
    r, g, b = (x / 255.0 for x in _hex_to_rgb(hex_color))

    def _linear(channel: float) -> float:
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    lr, lg, lb = _linear(r), _linear(g), _linear(b)
    return 0.2126 * lr + 0.7152 * lg + 0.0722 * lb


def _blend_toward_white(hex_color: str, amount: float) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    nr = int(r + (255 - r) * amount)
    ng = int(g + (255 - g) * amount)
    nb = int(b + (255 - b) * amount)
    return f"#{nr:02x}{ng:02x}{nb:02x}"


def _is_dark_theme(background: str) -> bool:
    return _relative_luminance(background) < 0.2


def _blend_toward_black(hex_color: str, amount: float) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    nr = int(r * (1 - amount))
    ng = int(g * (1 - amount))
    nb = int(b * (1 - amount))
    return f"#{nr:02x}{ng:02x}{nb:02x}"


def _contrast_ratio_hex(foreground: str, background: str) -> float:
    l1 = _relative_luminance(foreground)
    l2 = _relative_luminance(background)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _darken_for_contrast(color: str, background: str, min_ratio: float = 4.5) -> str:
    """Progressively darken a color until it meets contrast on the background."""
    if _contrast_ratio_hex(color, background) >= min_ratio:
        return color
    for amount in (0.18, 0.32, 0.48, 0.62, 0.78):
        candidate = _blend_toward_black(color, amount)
        if _contrast_ratio_hex(candidate, background) >= min_ratio:
            return candidate
    return "#1a1a28"


def _adjust_theme_contrast(colors: dict) -> dict:
    """Pull text colors toward readable dark-on-light or light-on-dark."""
    adjusted = dict(colors)
    bg = adjusted["background"]
    dark_bg = _is_dark_theme(bg)
    card_surface = adjusted["card_bg"]
    if not dark_bg:
        card_surface = _blend_toward_white(adjusted["card_bg"], 0.4)
        if _relative_luminance(card_surface) - _relative_luminance(bg) < 0.12:
            card_surface = "#ffffff"

    if dark_bg:
        if _contrast_ratio_hex(adjusted["body_text"], bg) < 4.5:
            adjusted["body_text"] = "#f4f4f4"
        if _contrast_ratio_hex(adjusted["heading_color"], bg) < 3.0:
            adjusted["heading_color"] = adjusted["button_bg"]
    else:
        adjusted["body_text"] = _darken_for_contrast(adjusted["body_text"], bg, 5.0)
        adjusted["heading_color"] = _darken_for_contrast(adjusted["heading_color"], bg, 4.5)
        adjusted["body_text"] = _darken_for_contrast(adjusted["body_text"], card_surface, 4.8)
        adjusted["heading_color"] = _darken_for_contrast(
            adjusted["heading_color"], card_surface, 4.2
        )
        btn_lum = _relative_luminance(adjusted["button_bg"])
        if btn_lum > 0.6 and _relative_luminance(adjusted["button_text"]) > 0.5:
            adjusted["button_text"] = "#1e1e2e"

    return adjusted


def _accent_color(button_bg: str, heading: str, body: str, background: str) -> str:
    """Pick a link/label accent with enough contrast on the page background."""
    if _is_dark_theme(background):
        for candidate in (heading, body, button_bg, "#2e2a3d", "#e8e8e8"):
            if _contrast_ratio_hex(candidate, background) >= 3.0:
                return candidate
        return "#e8e8e8"

    for candidate in (
        body,
        _darken_for_contrast(heading, background, 4.5),
        _darken_for_contrast(button_bg, background, 4.5),
        "#2e2a3d",
    ):
        if _contrast_ratio_hex(candidate, background) >= 4.5:
            return candidate
    return "#2e2a3d"


def _palette_button_colors(
    background: str,
    heading: str,
    body: str,
    border: str,
    button_bg: str,
    button_text: str,
    card_surface: str,
) -> dict[str, str]:
    """Derive primary and outline button colors from the theme palette."""
    btn_hover = (
        _blend_toward_white(button_bg, 0.14)
        if _is_dark_theme(background)
        else _blend_toward_black(button_bg, 0.18)
    )

    outline_text = heading
    if _contrast_ratio_hex(outline_text, background) < 3.0:
        outline_text = body
    if _contrast_ratio_hex(outline_text, background) < 3.0:
        outline_text = "#f4f4f4" if _is_dark_theme(background) else "#1e1e2e"

    outline_hover_text = heading
    if _contrast_ratio_hex(outline_hover_text, card_surface) < 3.0:
        outline_hover_text = body
    if _contrast_ratio_hex(outline_hover_text, card_surface) < 3.0:
        outline_hover_text = outline_text

    primary_hover_text = button_text
    if _contrast_ratio_hex(primary_hover_text, btn_hover) < 3.0:
        primary_hover_text = (
            "#1e1e2e" if _relative_luminance(btn_hover) > 0.55 else "#ffffff"
        )

    return {
        "btn_hover": btn_hover,
        "btn_hover_text": primary_hover_text,
        "outline_text": outline_text,
        "outline_border": border,
        "outline_hover_bg": card_surface,
        "outline_hover_text": outline_hover_text,
        "outline_hover_border": heading,
    }


def _portfolio_surface_colors(background: str, card: str, border: str) -> tuple[str, str, str]:
    """On light backgrounds, lift cards/tags so content stays readable."""
    if _is_dark_theme(background):
        return card, _rgba(border, 0.25), border

    surface = _blend_toward_white(card, 0.4)
    if _relative_luminance(surface) - _relative_luminance(background) < 0.12:
        surface = "#ffffff"
    tag_bg = _blend_toward_white(border, 0.72)
    tag_border = _blend_toward_white(border, 0.45)
    return surface, tag_bg, tag_border


def _format_education_year(edu: dict) -> str:
    grad = (edu.get("grad_year") or edu.get("graduation_year") or "").strip()
    if grad:
        return grad
    years = (edu.get("years") or edu.get("duration") or "").strip()
    if not years:
        return ""
    if re.search(r"present", years, re.I):
        return years
    range_match = re.search(r"(\d{4})\s*[-–—]\s*(\d{4})", years)
    if range_match:
        return range_match.group(2)
    found_years = re.findall(r"\b(\d{4})\b", years)
    if found_years:
        return found_years[-1]
    return years


def generate_portfolio_html(
    profile: dict,
    theme: dict | None = None,
    font: str | None = None,
) -> str:
    """
    Build a self-contained portfolio website from extracted resume profile data.
    Inspired by modern personal portfolio layouts with anchored sections and a hero landing.
    """
    raw_name = (profile.get("name") or "Your Name").strip()
    name = html.escape(raw_name)
    raw_role = (profile.get("role") or "").strip()
    role = html.escape(raw_role)
    skills_summary = (profile.get("skills_summary") or "").strip()
    tagline_raw = (profile.get("tagline") or "").strip()
    about_raw = (profile.get("about") or "").strip()
    email = (profile.get("email") or "").strip()
    location = html.escape((profile.get("location") or "").strip())
    linkedin = (profile.get("linkedin") or "").strip()
    github = (profile.get("github") or "").strip()
    projects = profile.get("projects") or []
    experience = profile.get("experience") or []
    education = profile.get("education") or []
    resume_id = (profile.get("resume_id") or "").strip()
    has_resume = bool(re.fullmatch(r"[a-f0-9]{8}", resume_id))

    display_name = name
    initials = html.escape(raw_name[:1].upper() if raw_name else "?")

    if tagline_raw:
        tagline = html.escape(tagline_raw)
    elif raw_role:
        tagline = html.escape(f"Focused on meaningful work as a {raw_role.lower()}.")
    else:
        tagline = "Building thoughtful work, one project at a time."

    if about_raw:
        about_body = html.escape(about_raw)
    else:
        about_parts = [f"I'm {name}"]
        if raw_role:
            about_parts.append(f", {role}")
        if location:
            about_parts.append(f", based in {location}")
        about_parts.append(".")
        if skills_summary:
            about_parts.append(f" {skills_summary}")
        about_body = html.escape("".join(about_parts).strip())

    about_info_lines = []
    for edu in education:
        if isinstance(edu, str):
            if edu.strip():
                about_info_lines.append(html.escape(edu.strip()))
        else:
            degree = (edu.get("degree") or "").strip()
            school = (edu.get("school") or "").strip()
            grad_year = _format_education_year(edu)
            line = " · ".join(x for x in [degree, school, grad_year] if x)
            if line:
                about_info_lines.append(html.escape(line))
    about_info_html = ""
    if about_info_lines:
        about_info_html = '<div class="about-info">' + "".join(
            f"<p>{line}</p>" for line in about_info_lines
        ) + "</div>"

    # Collect distinct skills from projects and experience
    skill_map: dict[str, str] = {}
    for project in projects:
        for tag in project.get("tech") or []:
            label = str(tag).strip()
            if label:
                skill_map[label.lower()] = label
    for entry in experience:
        for tag in entry.get("tech") or []:
            label = str(tag).strip()
            if label:
                skill_map[label.lower()] = label

    has_skills = bool(skill_map)
    has_experience = bool(experience)
    has_projects = bool(projects)

    nav_items: list[tuple[str, str]] = [("about", "About")]
    if has_skills:
        nav_items.append(("skills", "Skills"))
    if has_experience:
        nav_items.append(("experience", "Experience"))
    nav_items.append(("projects", "Projects"))
    if has_resume:
        nav_items.append(("resume", "Resume"))
    nav_items.append(("contact", "Contact"))

    nav_html = "".join(
        f'<a href="#{section_id}">{label}</a>' for section_id, label in nav_items
    )

    hero_ctas = '<a class="btn btn-primary" href="#projects">View My Work</a>'
    hero_ctas += '<a class="btn btn-outline" href="#contact">Get In Touch</a>'

    def section_header(title: str, subtitle: str = "") -> str:
        sub = f'<p class="section-sub">{subtitle}</p>' if subtitle else ""
        return f"""
      <div class="section-head">
        <h2 class="section-title">{title}</h2>
        {sub}
      </div>"""

    about_header = section_header("About Me")

    skills_section = ""
    if has_skills:
        skill_tags = "".join(
            f'<span class="tag">{html.escape(label)}</span>'
            for label in skill_map.values()
        )
        skills_section = f"""
    <section id="skills" class="panel reveal">
      {section_header("Skills &amp; Expertise", "Technologies and tools from your resume")}
      <div class="skill-cloud">{skill_tags}</div>
    </section>"""

    experience_section = ""
    if has_experience:
        exp_items = ""
        for entry in experience:
            title = html.escape((entry.get("title") or "Role").strip())
            company = html.escape((entry.get("company") or "").strip())
            duration = html.escape((entry.get("duration") or "").strip())
            highlights = entry.get("highlights") or []
            highlight_items = "".join(
                f"<li>{html.escape(str(point).strip())}</li>"
                for point in highlights
                if str(point).strip()
            )
            highlights_html = (
                f"<ul>{highlight_items}</ul>" if highlight_items else ""
            )
            company_line = f" · {company}" if company else ""
            exp_items += f"""
        <article class="timeline-item reveal">
          <div class="timeline-when">{duration or "Present"}</div>
          <div class="timeline-body">
            <h3>{title}<span class="timeline-org">{company_line}</span></h3>
            {highlights_html}
          </div>
        </article>"""
        experience_section = f"""
    <section id="experience" class="panel reveal">
      {section_header("Experience", "Recent roles and impact")}
      <div class="timeline">{exp_items}</div>
    </section>"""

    projects_section = ""
    if has_projects:
        project_cards = ""
        for project in projects:
            project_name = html.escape((project.get("name") or "Project").strip())
            project_desc = html.escape((project.get("desc") or "").strip())
            tech_tags = "".join(
                f'<span class="tag">{html.escape(str(tag))}</span>'
                for tag in (project.get("tech") or [])
            )
            project_cards += f"""
        <article class="project-card reveal">
          <h3>{project_name}</h3>
          <p>{project_desc}</p>
          <div class="tags">{tech_tags}</div>
        </article>"""
        projects_section = f"""
    <section id="projects" class="panel reveal">
      {section_header("Projects", "Selected work from your resume")}
      <div class="project-grid">{project_cards}</div>
    </section>"""
    else:
        projects_section = f"""
    <section id="projects" class="panel reveal">
      {section_header("Projects")}
      <p class="placeholder">Project highlights will appear here when they are listed on your resume.</p>
    </section>"""

    resume_section = ""
    if has_resume:
        safe_resume_id = html.escape(resume_id, quote=True)
        resume_filename = html.escape(
            f"{re.sub(r'[^a-zA-Z0-9_-]+', '_', raw_name).strip('_') or 'resume'}_Resume.pdf",
            quote=True,
        )
        resume_section = f"""
    <section id="resume" class="panel reveal">
      {section_header("Resume", "Download a PDF copy of my resume")}
      <div class="resume-download-wrap">
        <a class="btn btn-primary resume-download" href="/api/resume/{safe_resume_id}" download="{resume_filename}">
          Download Resume PDF
        </a>
      </div>
    </section>"""

    contact_lines = []
    if email:
        safe_email = html.escape(email, quote=True)
        contact_lines.append(
            f'<p class="contact-line"><span class="contact-label">Email</span> '
            f'<a href="mailto:{safe_email}">{html.escape(email)}</a></p>'
        )
    if location:
        contact_lines.append(
            f'<p class="contact-line"><span class="contact-label">Location</span> '
            f'<span class="contact-value">{location}</span></p>'
        )
    if linkedin:
        safe_linkedin = html.escape(linkedin, quote=True)
        contact_lines.append(
            f'<p class="contact-line"><span class="contact-label">LinkedIn</span> '
            f'<a href="{safe_linkedin}" target="_blank" rel="noopener noreferrer">{html.escape(linkedin)}</a></p>'
        )
    if github:
        safe_github = html.escape(github, quote=True)
        contact_lines.append(
            f'<p class="contact-line"><span class="contact-label">GitHub</span> '
            f'<a href="{safe_github}" target="_blank" rel="noopener noreferrer">{html.escape(github)}</a></p>'
        )

    contact_body = (
        "".join(contact_lines)
        if contact_lines
        else '<p class="placeholder">Add email, LinkedIn, or GitHub to your resume to populate contact details.</p>'
    )

    colors = _adjust_theme_contrast(_resolve_portfolio_theme(theme))
    c_bg = colors["background"]
    c_heading = colors["heading_color"]
    c_card = colors["card_bg"]
    c_border = colors["card_border"]
    c_text = colors["body_text"]
    c_btn = colors["button_bg"]
    c_btn_text = colors["button_text"]
    c_accent = _accent_color(c_btn, c_heading, c_text, c_bg)
    c_font = (font or DEFAULT_PORTFOLIO_FONT).replace("<", "").replace("}", "")
    border_r, border_g, border_b = _hex_to_rgb(c_border)
    heading_r, heading_g, heading_b = _hex_to_rgb(c_heading)
    c_card_surface, c_tag_bg, c_tag_border_line = _portfolio_surface_colors(c_bg, c_card, c_border)
    c_contact_label = c_btn
    if _contrast_ratio_hex(c_contact_label, c_card_surface) < 3.5:
        c_contact_label = (
            c_heading
            if _contrast_ratio_hex(c_heading, c_card_surface) >= 3.5
            else c_text
        )
    c_subtext = c_text
    dark_bg = _is_dark_theme(c_bg)
    if dark_bg:
        c_hero_eyebrow = c_accent
        c_hero_tagline = c_text
        c_nav = c_accent
    else:
        hero_surface = _blend_toward_white(c_card, 0.35)
        if _relative_luminance(hero_surface) - _relative_luminance(c_bg) < 0.08:
            hero_surface = _blend_toward_white(c_bg, 0.1)
        c_hero_eyebrow = _darken_for_contrast(c_heading, hero_surface, 5.2)
        c_hero_tagline = _darken_for_contrast(c_text, hero_surface, 5.0)
        c_nav = _darken_for_contrast(c_heading, c_bg, 4.8)
    btn_palette = _palette_button_colors(
        c_bg, c_heading, c_text, c_border, c_btn, c_btn_text, c_card_surface
    )
    c_btn_hover = btn_palette["btn_hover"]
    c_btn_hover_text = btn_palette["btn_hover_text"]
    c_outline_text = btn_palette["outline_text"]
    c_outline_border = btn_palette["outline_border"]
    c_outline_hover_bg = btn_palette["outline_hover_bg"]
    c_outline_hover_text = btn_palette["outline_hover_text"]
    c_outline_hover_border = btn_palette["outline_hover_border"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{name} — Portfolio</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    html {{
      font-size: 16px;
      -webkit-text-size-adjust: 100%;
      text-size-adjust: 100%;
      scroll-behavior: smooth;
      scroll-padding-top: 4.5rem;
    }}
    @keyframes fade-up {{
      from {{
        opacity: 0;
        transform: translateY(28px);
      }}
      to {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}
    @keyframes fade-in {{
      from {{ opacity: 0; }}
      to {{ opacity: 1; }}
    }}
    body {{
      background: {c_bg};
      color: {c_text};
      font-family: {c_font};
      font-size: 1rem;
      font-weight: 500;
      line-height: 1.65;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}
    #bg-canvas {{
      position: fixed;
      inset: 0;
      z-index: 0;
      pointer-events: none;
    }}
    .site-nav,
    .hero,
    .page-wrap,
    .site-footer {{
      position: relative;
      z-index: 1;
    }}
    a {{
      color: {c_accent};
    }}
    .site-nav {{
      position: sticky;
      top: 0;
      z-index: 20;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding: 0.85rem 1.25rem;
      background: {_rgba(c_bg, 0.88)};
      backdrop-filter: blur(8px);
      animation: fade-in 0.6s ease-out both;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
      text-decoration: none;
      color: {c_text};
      font-weight: 700;
      white-space: nowrap;
    }}
    .brand-mark {{
      width: 2rem;
      height: 2rem;
      border-radius: 999px;
      background: {c_btn};
      color: {c_btn_text};
      display: grid;
      place-items: center;
      font-size: 0.85rem;
      font-weight: 700;
    }}
    .nav-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem 1rem;
      justify-content: flex-end;
    }}
    .nav-links a {{
      text-decoration: none;
      color: {c_nav};
      font-size: 0.88rem;
      font-weight: 600;
    }}
    .nav-links a:hover {{
      color: {c_heading};
    }}
    .hero {{
      position: relative;
      min-height: calc(100vh - 4.5rem);
      display: grid;
      place-items: center;
      padding: 3rem 1.25rem 4rem;
      text-align: center;
      background: transparent;
    }}
    .hero::before {{
      content: "";
      position: absolute;
      inset: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 100vw;
      z-index: -1;
      background: {_rgba(c_card, 0.55)};
    }}
    .hero-inner {{
      max-width: 46rem;
    }}
    .hero-inner .eyebrow {{
      animation: fade-up 0.85s ease-out both;
    }}
    .hero-inner h1 {{
      animation: fade-up 0.85s ease-out 0.12s both;
    }}
    .hero-inner .hero-tagline {{
      animation: fade-up 0.85s ease-out 0.24s both;
    }}
    .hero-inner .hero-actions {{
      animation: fade-up 0.85s ease-out 0.36s both;
    }}
    .eyebrow {{
      color: {c_hero_eyebrow};
      font-size: 0.95rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 1rem;
      font-weight: 800;
    }}
    .hero h1 {{
      color: {c_heading};
      font-size: clamp(2.5rem, 8vw, 4.5rem);
      line-height: 1.05;
      font-weight: 700;
      margin-bottom: 1rem;
      letter-spacing: -0.03em;
    }}
    .hero-tagline {{
      font-size: clamp(1.05rem, 2.5vw, 1.35rem);
      max-width: 38rem;
      margin: 0 auto 1.75rem;
      color: {c_hero_tagline};
      font-weight: 700;
    }}
    .hero-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      justify-content: center;
    }}
    .page-wrap {{
      max-width: 980px;
      margin: 0 auto;
      padding: 0 1.25rem 4rem;
    }}
    .panel {{
      position: relative;
      padding: 5rem 0 4rem;
      margin-bottom: 0;
    }}
    .panel::before {{
      content: "";
      position: absolute;
      inset: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 100vw;
      z-index: -1;
    }}
    .panel:nth-of-type(odd)::before {{
      background: {_rgba(c_card, 0.82)};
    }}
    .panel:nth-of-type(even)::before {{
      background: {_rgba(c_border, 0.16)};
    }}
    .panel:first-of-type {{
      padding-top: 3.5rem;
    }}
    .reveal {{
      opacity: 0;
      transform: translateY(22px);
      transition: opacity 0.65s ease, transform 0.65s ease;
    }}
    .reveal.visible {{
      opacity: 1;
      transform: translateY(0);
    }}
    .section-head {{
      margin-bottom: 1.75rem;
    }}
    .section-title {{
      color: {c_heading};
      font-size: clamp(1.6rem, 4vw, 2.2rem);
      font-weight: 700;
      margin-bottom: 0.35rem;
    }}
    .section-sub {{
      color: {c_subtext};
      font-size: 0.98rem;
      font-weight: 600;
    }}
    .about-copy {{
      font-size: 1.05rem;
      max-width: 42rem;
      margin-bottom: 1.25rem;
      font-weight: 500;
    }}
    .about-info {{
      max-width: 42rem;
      margin-top: 0.5rem;
    }}
    .about-info p {{
      font-size: 0.95rem;
      color: {c_subtext};
      font-weight: 600;
      margin-bottom: 0.35rem;
    }}
    .skill-cloud,
    .tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.55rem;
    }}
    .tag {{
      background: {c_tag_bg};
      color: {c_text};
      font-size: 0.8rem;
      font-weight: 600;
      padding: 0.35rem 0.75rem;
      border-radius: 999px;
      border: 1px solid {c_tag_border_line};
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .tag:hover {{
      transform: translateY(-2px);
      box-shadow: 0 4px 12px {_rgba(c_text, 0.08)};
    }}
    .project-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1rem;
    }}
    .project-card,
    .info-card {{
      background: {c_card_surface};
      border: 1px solid {c_border};
      border-radius: 1rem;
      padding: 1.35rem;
      box-shadow: 0 8px 24px {_rgba(c_text, 0.05)};
      transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    .project-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 12px 28px {_rgba(c_text, 0.08)};
    }}
    .project-card h3,
    .info-card h3,
    .timeline-body h3 {{
      color: {c_heading};
      font-size: 1.08rem;
      margin-bottom: 0.55rem;
      font-weight: 700;
    }}
    .project-card p,
    .info-card p {{
      font-size: 0.95rem;
      margin-bottom: 0.85rem;
      font-weight: 500;
    }}
    .timeline {{
      display: grid;
      gap: 1rem;
    }}
    .timeline-item {{
      display: grid;
      grid-template-columns: minmax(9rem, 12rem) 1fr;
      gap: 1rem;
      background: {c_card_surface};
      border: 1px solid {c_border};
      border-radius: 1rem;
      padding: 1.25rem 1.35rem;
      box-shadow: 0 6px 18px {_rgba(c_text, 0.04)};
      transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    .timeline-item:hover {{
      transform: translateY(-2px);
      box-shadow: 0 10px 24px {_rgba(c_text, 0.07)};
    }}
    .timeline-when {{
      color: {c_heading};
      font-size: 1.08rem;
      font-weight: 700;
      letter-spacing: 0.01em;
      line-height: 1.35;
      padding-top: 0.1rem;
    }}
    .timeline-org {{
      color: {c_text};
      font-weight: 600;
    }}
    .timeline-body ul {{
      margin-left: 1.1rem;
      font-size: 0.93rem;
      font-weight: 500;
    }}
    .timeline-body li {{
      margin-bottom: 0.35rem;
    }}
    .contact-panel {{
      text-align: center;
      padding-bottom: 2rem;
    }}
    .resume-download-wrap {{
      display: flex;
      justify-content: center;
      margin-top: 0.5rem;
    }}
    .resume-download {{
      min-width: 12rem;
      text-align: center;
    }}
    .contact-panel .section-head {{
      text-align: center;
      margin-bottom: 2rem;
    }}
    .contact-wrap {{
      max-width: 28rem;
      margin: 0 auto;
    }}
    .contact-list {{
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
      padding: 2rem 2.25rem;
      background: {c_card_surface};
      border: 1px solid {c_border};
      border-radius: 1.25rem;
      box-shadow: 0 10px 32px {_rgba(c_text, 0.06)};
    }}
    .contact-line {{
      font-size: 0.98rem;
      margin-bottom: 0;
      word-break: break-word;
      text-align: center;
      width: 100%;
    }}
    .contact-line a,
    .contact-value {{
      color: {c_text};
      text-decoration: none;
      font-weight: 700;
      font-size: 0.98rem;
    }}
    .contact-line a:hover {{
      color: {c_heading};
    }}
    .contact-label {{
      display: block;
      min-width: auto;
      color: {c_contact_label};
      font-size: 0.72rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 700;
      margin-right: 0;
      margin-bottom: 0.35rem;
    }}
    .btn {{
      display: inline-block;
      text-decoration: none;
      padding: 0.65rem 1.2rem;
      border-radius: 999px;
      font-size: 0.9rem;
      font-weight: 700;
      transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
    }}
    .btn-primary {{
      background: {c_btn};
      color: {c_btn_text};
      border: 1px solid {c_btn};
    }}
    .btn-primary:hover {{
      background: {c_btn_hover};
      border-color: {c_btn_hover};
      color: {c_btn_hover_text};
    }}
    .btn-outline {{
      background: transparent;
      color: {c_outline_text};
      border: 1px solid {c_outline_border};
    }}
    .btn-outline:hover {{
      background: {c_outline_hover_bg};
      color: {c_outline_hover_text};
      border-color: {c_outline_hover_border};
    }}
    .placeholder {{
      opacity: 0.75;
      font-style: italic;
      max-width: 36rem;
    }}
    .site-footer {{
      position: relative;
      z-index: 1;
      padding: 1.5rem 1.25rem 2rem;
      text-align: center;
      color: {c_accent};
      font-size: 0.85rem;
    }}
    .site-footer::before {{
      content: "";
      position: absolute;
      inset: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 100vw;
      z-index: -1;
      background: {_rgba(c_card, 0.72)};
    }}
    @media (max-width: 720px) {{
      .site-nav {{
        flex-direction: column;
        align-items: flex-start;
      }}
      .nav-links {{
        justify-content: flex-start;
      }}
      .timeline-item {{
        grid-template-columns: 1fr;
      }}
      .hero {{
        min-height: auto;
        padding-top: 2.5rem;
      }}
    }}
  </style>
</head>
<body>
  <canvas id="bg-canvas" aria-hidden="true"></canvas>
  <nav class="site-nav">
    <a class="brand" href="#top">
      <span class="brand-mark">{initials}</span>
      <span>{name}</span>
    </a>
    <div class="nav-links">{nav_html}</div>
  </nav>

  <header id="top" class="hero">
    <div class="hero-inner">
      {f'<p class="eyebrow">{role}</p>' if role else '<p class="eyebrow">Portfolio</p>'}
      <h1>{display_name}</h1>
      <p class="hero-tagline">{tagline}</p>
      <div class="hero-actions">{hero_ctas}</div>
    </div>
  </header>

  <main class="page-wrap">
    <section id="about" class="panel reveal">
      {about_header}
      <p class="about-copy">{about_body}</p>
      {about_info_html}
    </section>
    {skills_section}
    {experience_section}
    {projects_section}
    {resume_section}
    <section id="contact" class="panel contact-panel reveal">
      <div class="contact-wrap">
        {section_header("Contact")}
        <div class="contact-list">{contact_body}</div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <p>&copy; 2026 {name}. Built with Cue.</p>
  </footer>
  <script>
  (function () {{
    const canvas = document.getElementById("bg-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const sand = "{c_bg}";
    const sage = "{c_border}";
    const olive = "{c_heading}";
    const config = {{
      areaPerParticle: 12000,
      minCount: 50,
      maxCount: 90,
      linkDist: 158,
      maxLinks: 5,
      lineOpacity: 0.22,
      nodeOpacity: 0.65,
      speed: 0.14,
      margin: 24,
    }};
    let particles = [];
    let animationId;

    function resize() {{
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = window.innerWidth + "px";
      canvas.style.height = window.innerHeight + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }}

    function init() {{
      const w = window.innerWidth;
      const h = window.innerHeight;
      const n = Math.max(
        config.minCount,
        Math.min(config.maxCount, Math.floor((w * h) / config.areaPerParticle))
      );
      particles = Array.from({{ length: n }}, () => ({{
        x: config.margin + Math.random() * (w - config.margin * 2),
        y: config.margin + Math.random() * (h - config.margin * 2),
        vx: (Math.random() - 0.5) * config.speed,
        vy: (Math.random() - 0.5) * config.speed,
        r: 1.2 + Math.random() * 1.4,
      }}));
    }}

    function move(p, w, h) {{
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < config.margin || p.x > w - config.margin) {{
        p.vx *= -1;
        p.x = Math.max(config.margin, Math.min(w - config.margin, p.x));
      }}
      if (p.y < config.margin || p.y > h - config.margin) {{
        p.vy *= -1;
        p.y = Math.max(config.margin, Math.min(h - config.margin, p.y));
      }}
    }}

    function linksFor(i) {{
      const a = particles[i];
      const found = [];
      for (let j = 0; j < particles.length; j++) {{
        if (j === i) continue;
        const b = particles[j];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        if (d < config.linkDist) found.push({{ j, d }});
      }}
      found.sort((x, y) => x.d - y.d);
      return found.slice(0, config.maxLinks);
    }}

    function draw() {{
      const w = window.innerWidth;
      const h = window.innerHeight;
      ctx.fillStyle = sand;
      ctx.fillRect(0, 0, w, h);
      for (const p of particles) move(p, w, h);
      const drawn = new Set();
      ctx.lineCap = "round";
      for (let i = 0; i < particles.length; i++) {{
        const a = particles[i];
        for (const {{ j, d }} of linksFor(i)) {{
          const key = i < j ? i + "-" + j : j + "-" + i;
          if (drawn.has(key)) continue;
          drawn.add(key);
          const b = particles[j];
          const alpha = (1 - d / config.linkDist) * config.lineOpacity;
          ctx.strokeStyle = "rgba({border_r}, {border_g}, {border_b}, " + alpha + ")";
          ctx.lineWidth = 0.8;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }}
      }}
      for (const p of particles) {{
        ctx.fillStyle = "rgba({heading_r}, {heading_g}, {heading_b}, " + config.nodeOpacity + ")";
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }}
      animationId = requestAnimationFrame(draw);
    }}

    function onResize() {{
      resize();
      init();
    }}

    resize();
    init();
    animationId = requestAnimationFrame(draw);
    window.addEventListener("resize", onResize);

    document.querySelectorAll(".reveal").forEach((el, i) => {{
      el.style.setProperty("--i", String(i % 6));
    }});
    const revealObserver = new IntersectionObserver((entries) => {{
      entries.forEach((entry) => {{
        if (entry.isIntersecting) {{
          entry.target.classList.add("visible");
          revealObserver.unobserve(entry.target);
        }}
      }});
    }}, {{ threshold: 0.12, rootMargin: "0px 0px -40px 0px" }});
    document.querySelectorAll(".reveal").forEach((el) => revealObserver.observe(el));
  }})();
  </script>
</body>
</html>"""


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
        max_tokens=1536,
        messages=[
            {
                "role": "user",
                "content": f"""Extract structured information from this resume text.

Return ONLY valid JSON with this exact structure, no markdown backticks, no explanation:

{{
  "name": "full name",
  "role": "current role or status, e.g. CS student at ASU or Software Engineer at Company",
  "tagline": "short punchy hero hook, max 15 words, inspirational and distinct from the about paragraph",
  "about": "2 to 3 sentence personal introduction with name, major or field, school or background, and what they are working toward",
  "email": "email address if visible in the resume, otherwise empty string",
  "location": "city and state if visible, otherwise empty string",
  "education": [
    {{
      "degree": "degree and major, e.g. B.S. in Computer Science",
      "school": "university or school name",
      "grad_year": "2026"
    }}
  ],
  "experience": [
    {{
      "title": "job title",
      "company": "company name",
      "duration": "Jun 2025 - Aug 2025",
      "highlights": [
        "short plain sentence about what they did",
        "another short plain sentence in simple conversational language"
      ]
    }}
  ],
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

Rules for tagline and about:
- tagline is a short hero hook, not the same text as about or skills_summary
- about is a fuller personal introduction covering background, major or field, and goals
- Extract education entries when visible on the resume, otherwise return an empty array
- For education, set grad_year to the graduation year only (e.g. 2026). Do not include a start year unless both start and end years are explicitly stated on the resume

Rules for experience:
- Extract up to 3 of the most recent or most significant work experience entries
- Each entry must have title, company, duration, and highlights
- Duration should look like "Jun 2025 - Aug 2025" or "Jan 2024 - Present"
- highlights must be an array of 2 to 3 short plain sentence bullet points describing what they did
- Write highlights in simple conversational language with no hyphens

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