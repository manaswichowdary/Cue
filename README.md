# Cue

**Know who you are meeting. Show who you are.**

Cue is a networking toolkit built for conferences and professional events. Enter a name and get real-time research on who you're about to meet—plus tailored conversation questions and a natural intro line you can actually say out loud. Upload your resume and Cue instantly builds a shareable personal portfolio you can customize and hand off via QR code.

## Live Demo

**[https://cue-sepia-omega.vercel.app](https://cue-sepia-omega.vercel.app)**

## Features

- **Real-time web search powered research** : Claude searches the web for current role, recent work, and why someone matters in the AI community
- **Personalized conversational intro lines** : first-person openers that connect your background to the speaker's work when you've uploaded a resume
- **Five tailored questions per person** : specific, relaxed questions based on their recent projects and focus area
- **Resume upload and AI extraction** : PDF in, structured profile out (name, role, experience, projects, skills, links)
- **Auto-generated portfolio website** : multi-section site with hero, about, skills, experience, projects, and contact
- **15+ themes and 10 fonts** : customize colors and typography, then regenerate in one click
- **QR code sharing** : scan-to-open portfolio link that updates when you change theme or font
- **Opt-in local device persistence** : save your profile to this browser only when you choose; privacy-first by default

## Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) on [Railway](https://railway.app/)
- **AI:** [Anthropic Claude API](https://docs.anthropic.com/) with the web search tool
- **Frontend:** [React](https://react.dev/) + [Vite](https://vitejs.dev/)
- **Styling:** Tailwind-free custom CSS
- **Frontend hosting:** [Vercel](https://vercel.com/)

## How It Works

### Speaker research (two-stage AI pipeline)

1. **Research** : Claude Sonnet runs live web search on the speaker's name and returns structured findings (role, company, recent work, community reputation).
2. **Generate** : A second Claude call turns that research into a JSON profile: why they matter, five questions, and an intro line. If you've uploaded a resume, your background is woven into the intro when there's genuine overlap.

### Resume → portfolio

1. **Extract** : Upload a PDF resume; Claude extracts structured profile data and the backend stores the PDF.
2. **Generate** : Profile data is passed to a portfolio HTML builder (themes, fonts, contrast tuning) and served at a unique URL.
3. **Share** : The app displays a theme-colored QR code linking to your live portfolio. Change theme or font and the portfolio regenerates automatically.

## Running Locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
ANTHROPIC_API_KEY=your_key_here
```

Start the API:

```bash
uvicorn main:app --reload --port 8000
```

API runs at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at [http://localhost:5173](http://localhost:5173).

For local development, set `apiBase` in `frontend/src/App.jsx` to `http://127.0.0.1:8000`. Switch it back to the Railway production URL before deploying.

---

Built solo in under two weeks.
