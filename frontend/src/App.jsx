import { useState, useRef, useEffect } from "react"
import PlexusBackground from "./PlexusBackground"

function normalizeGithubUrl(value) {
  if (!value) return ""
  const v = value.trim()
  const match = v.match(/(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38})/i)
  if (match) return `https://github.com/${match[1]}`
  if (/^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$/.test(v)) return `https://github.com/${v}`
  return ""
}

function normalizeLinkedinUrl(value) {
  if (!value) return ""
  const v = value.trim()
  const match = v.match(/(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_-]+)/i)
  if (!match) return ""
  return `https://linkedin.com/in/${match[1]}`
}

const themes = [
  {
    name: "Cue Default",
    background: "#f0ece6",
    heading_color: "#a47864",
    card_bg: "#ffffff",
    card_border: "#aaabca",
    body_text: "#2e2a3d",
    button_bg: "#6c6c9b",
    button_text: "#ffffff",
  },
  {
    name: "Rustic Charm",
    background: "#f5f0e8",
    heading_color: "#1a1a1a",
    card_bg: "#e8e4de",
    card_border: "#3d3d3d",
    body_text: "#3d3d3d",
    button_bg: "#c45c26",
    button_text: "#ffffff",
  },
  {
    name: "Ocean Blue Serenity",
    background: "#faf8f5",
    heading_color: "#5a6a7a",
    card_bg: "#d4eaf7",
    card_border: "#b8e0d2",
    body_text: "#5a6a7a",
    button_bg: "#e8b4a0",
    button_text: "#ffffff",
  },
  {
    name: "Oceanic Cactus",
    background: "#f0faf8",
    heading_color: "#006d77",
    card_bg: "#83c5be",
    card_border: "#f4e285",
    body_text: "#006d77",
    button_bg: "#e29578",
    button_text: "#ffffff",
  },
  {
    name: "Pastel Comfort",
    background: "#fdf8f0",
    heading_color: "#9c4a2e",
    card_bg: "#e8f5e9",
    card_border: "#c5e1a5",
    body_text: "#9c4a2e",
    button_bg: "#f4c4a8",
    button_text: "#ffffff",
  },
  {
    name: "Sunny Beach Day",
    background: "#fefae0",
    heading_color: "#001d3d",
    card_bg: "#2a6f7a",
    card_border: "#3d2314",
    body_text: "#3d2314",
    button_bg: "#ff6b35",
    button_text: "#ffffff",
  },
  {
    name: "Earthy Tones",
    background: "#faf8f5",
    heading_color: "#2e2e2e",
    card_bg: "#e8e0d5",
    card_border: "#8a9a7b",
    body_text: "#2e2e2e",
    button_bg: "#c9a0a0",
    button_text: "#ffffff",
  },
  {
    name: "Ocean Breeze",
    background: "#caf0f8",
    heading_color: "#03045e",
    card_bg: "#ffffff",
    card_border: "#0077b6",
    body_text: "#023e8a",
    button_bg: "#00b4d8",
    button_text: "#ffffff",
  },
  {
    name: "Warm Neutrals",
    background: "#fdf6f0",
    heading_color: "#c89f81",
    card_bg: "#ffffff",
    card_border: "#e1c6b1",
    body_text: "#a6a28e",
    button_bg: "#c89f81",
    button_text: "#ffffff",
  },
  {
    name: "Earthy Green",
    background: "#ced4da",
    heading_color: "#2d3a3a",
    card_bg: "#ffffff",
    card_border: "#82a68a",
    body_text: "#3c4e4b",
    button_bg: "#4a6d5a",
    button_text: "#ffffff",
  },
  {
    name: "Dark Sunset",
    background: "#fefae0",
    heading_color: "#2f3e46",
    card_bg: "#ffffff",
    card_border: "#dda15e",
    body_text: "#2f3e46",
    button_bg: "#bc6c25",
    button_text: "#ffffff",
  },
  {
    name: "Gradient Blues",
    background: "#e0fbfc",
    heading_color: "#3d5a80",
    card_bg: "#ffffff",
    card_border: "#98c1d9",
    body_text: "#293241",
    button_bg: "#3d5a80",
    button_text: "#ffffff",
  },
  {
    name: "Golden Twilight",
    background: "#000814",
    heading_color: "#ffc300",
    card_bg: "#001d3d",
    card_border: "#003566",
    body_text: "#ffd60a",
    button_bg: "#ffc300",
    button_text: "#000814",
  },
  {
    name: "Summer Dream",
    background: "#fefae0",
    heading_color: "#006d77",
    card_bg: "#ffffff",
    card_border: "#83c5be",
    body_text: "#006d77",
    button_bg: "#e29578",
    button_text: "#ffffff",
  },
  {
    name: "Coastal Vibes",
    background: "#edf2f4",
    heading_color: "#2b2d42",
    card_bg: "#ffffff",
    card_border: "#8d99ae",
    body_text: "#2b2d42",
    button_bg: "#ef233c",
    button_text: "#ffffff",
  },
  {
    name: "Fiery Palette",
    background: "#fdfcf0",
    heading_color: "#4d001d",
    card_bg: "#ffffff",
    card_border: "#ff4d00",
    body_text: "#4d001d",
    button_bg: "#900c3f",
    button_text: "#ffffff",
  },
  {
    name: "Neon Dark",
    background: "#0d0d0d",
    heading_color: "#39ff14",
    card_bg: "#1a1a1a",
    card_border: "#bc13fe",
    body_text: "#ffffff",
    button_bg: "#39ff14",
    button_text: "#000000",
  },
]

const fonts = [
  { name: "Georgia", value: 'Georgia, "Times New Roman", serif' },
  { name: "Times New Roman", value: '"Times New Roman", Times, serif' },
  { name: "Arial", value: "Arial, Helvetica, sans-serif" },
  { name: "Helvetica", value: "Helvetica, Arial, sans-serif" },
  { name: "Courier New", value: '"Courier New", Courier, monospace' },
  { name: "Palatino", value: 'Palatino, "Palatino Linotype", serif' },
  { name: "Garamond", value: 'Garamond, "Times New Roman", serif' },
  { name: "Verdana", value: "Verdana, Geneva, sans-serif" },
  { name: "Trebuchet MS", value: '"Trebuchet MS", Helvetica, sans-serif' },
  { name: "Lucida Sans", value: '"Lucida Sans", "Lucida Grande", sans-serif' },
]

function themeColors(theme) {
  if (!theme) return null
  return {
    background: theme.background,
    heading_color: theme.heading_color,
    card_bg: theme.card_bg,
    card_border: theme.card_border,
    body_text: theme.body_text,
    button_bg: theme.button_bg,
    button_text: theme.button_text,
  }
}

function qrHex(color) {
  return (color || "#2e2a3d").replace("#", "")
}

function portfolioQrSrc(portfolioUrl, theme) {
  const activeTheme = theme || themes.find((t) => t.name === "Cue Default")
  const params = new URLSearchParams({
    size: "120x120",
    data: portfolioUrl,
    color: qrHex(activeTheme?.button_bg),
    bgcolor: qrHex(activeTheme?.background),
  })
  return `https://api.qrserver.com/v1/create-qr-code/?${params.toString()}`
}

export default function App() {
  const [name, setName] = useState("")
  const [loading, setLoading] = useState(false)
  const [speaker, setSpeaker] = useState(null)
  const [error, setError] = useState(null)
  const [tab, setTab] = useState("research")
  const [landingDismissed, setLandingDismissed] = useState(false)
  const [myProfile, setMyProfile] = useState(null)
  const [uploadingResume, setUploadingResume] = useState(false)
  const [resumeUrl, setResumeUrl] = useState(null)
  const [portfolioUrl, setPortfolioUrl] = useState(null)
  const [selectedTheme, setSelectedTheme] = useState(null)
  const [selectedFont, setSelectedFont] = useState(null)
  const [regeneratingPortfolio, setRegeneratingPortfolio] = useState(false)
  const resumeInputRef = useRef(null)
  const hasPortfolioRef = useRef(false)

  const apiBase = "https://cue-production-b6e2.up.railway.app"
  const activeTheme = selectedTheme || themes.find((t) => t.name === "Cue Default")
  const qrCodeSrc = portfolioUrl ? portfolioQrSrc(portfolioUrl, activeTheme) : null

  async function requestPortfolio(profile, theme, font) {
    const payload = { ...profile }
    const colors = themeColors(theme)
    if (colors) payload.theme = colors
    if (font) payload.font = font.value

    const portfolioRes = await fetch(`${apiBase}/api/generate-portfolio`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    const result = await portfolioRes.json()
    console.log("Portfolio generation response:", result)
    if (!portfolioRes.ok) {
      console.error("Portfolio generation failed:", portfolioRes.status, result)
      return null
    }
    if (result.portfolio_id) {
      return `${apiBase}/api/portfolio/${result.portfolio_id}`
    }
    return null
  }

  async function handleRegeneratePortfolio() {
    if (!myProfile) return
    setRegeneratingPortfolio(true)
    try {
      const url = await requestPortfolio(myProfile, selectedTheme, selectedFont)
      if (url) {
        hasPortfolioRef.current = true
        setPortfolioUrl(url)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setRegeneratingPortfolio(false)
    }
  }

  useEffect(() => {
    if (!myProfile || !hasPortfolioRef.current) return

    const timer = setTimeout(async () => {
      setRegeneratingPortfolio(true)
      try {
        const url = await requestPortfolio(myProfile, selectedTheme, selectedFont)
        if (url) setPortfolioUrl(url)
      } catch (e) {
        console.error(e)
      } finally {
        setRegeneratingPortfolio(false)
      }
    }, 400)

    return () => clearTimeout(timer)
  }, [selectedTheme, selectedFont])

  async function handleResumeUpload(event) {
    const file = event.target.files[0]
    if (!file) return

    if (resumeUrl) URL.revokeObjectURL(resumeUrl)
    setResumeUrl(URL.createObjectURL(file))

    const formData = new FormData()
    formData.append("file", file)
    setUploadingResume(true)
    setPortfolioUrl(null)
    hasPortfolioRef.current = false
    try {
      const res = await fetch(`${apiBase}/api/extract-resume`, {
        method: "POST",
        body: formData,
      })
      const data = await res.json()
      setMyProfile(data)

      console.log("Sending portfolio profile:", data)
      const url = await requestPortfolio(data, selectedTheme, selectedFont)
      if (url) {
        hasPortfolioRef.current = true
        setPortfolioUrl(url)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setUploadingResume(false)
    }
  }

  function handleRemoveProfile() {
    setMyProfile(null)
    setPortfolioUrl(null)
    hasPortfolioRef.current = false
    setSelectedTheme(null)
    setSelectedFont(null)
    if (resumeUrl) {
      URL.revokeObjectURL(resumeUrl)
      setResumeUrl(null)
    }
  }

  const profileInitial = myProfile?.name?.charAt(0)?.toUpperCase() || "?"
  const githubUrl = normalizeGithubUrl(myProfile?.github)
  const linkedinUrl = normalizeLinkedinUrl(myProfile?.linkedin)
  const profileLinks = [
    linkedinUrl ? { label: "LinkedIn", href: linkedinUrl } : null,
    githubUrl ? { label: "GitHub", href: githubUrl } : null,
    resumeUrl ? { label: "Resume", href: resumeUrl } : null,
  ].filter(Boolean)

  async function handleResearch() {
    if (!name.trim()) return
    setLoading(true)
    setError(null)
    setSpeaker(null)
    try {
      const res = await fetch(`${apiBase}/api/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          user_background: myProfile
            ? `${myProfile.name}, ${myProfile.role}. Projects: ${(myProfile.projects || []).map((p) => p.name + " - " + p.desc).join("; ")}`
            : "",
        }),
      })
      const data = await res.json()
      setSpeaker(data)
    } catch (e) {
      setError("Something went wrong. Is the backend running?")
    }
    setLoading(false)
  }

  const palette = {
    cream: "#f0ece6",
    sand: "#f0ece6",
    card: "#f8f5f1",
    mocha: "#a47864",
    lavender: "#8a8bb3",
    purple: "#6c6c9b",
    indigo: "#4f4d84",
    ink: "#2e2a3d",
    periwinkle: "#aaabca",
  }

  const patternColor = "164, 120, 100"
  const shadowColor = "46, 42, 61"

  const networkingTips = [
    "Ask one specific question instead of five generic ones",
    "A good exit line is as important as a good opener",
    "People remember how you made them feel, not your title",
    "Listen more than you talk in the first thirty seconds",
    "It is okay to say you do not know something",
    "Follow up within 48 hours while the conversation is still fresh",
    "The best icebreaker references something they actually said",
    "Confidence is preparation in disguise",
    "Silence is not failure, it is a pause",
    "You do not need a perfect pitch, you need a genuine one",
    "A brief note beats a long follow-up email you never send",
    "Curiosity sounds smarter than certainty",
  ]

  const marqueeSeparator = "      |      "
  const marqueeLine = networkingTips.join(marqueeSeparator)
  const marqueeContent = `${marqueeLine}${marqueeSeparator}${marqueeLine}`

  return (
    <>
      <style>{`
        html {
          font-size: 16px;
          -webkit-text-size-adjust: 100%;
          text-size-adjust: 100%;
        }

        .cue-content {
          position: relative;
          z-index: 10;
        }

        @keyframes slide-in-left {
          from { opacity: 0; transform: translateX(-100px); }
          to { opacity: 1; transform: translateX(0); }
        }

        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .landing-title {
          animation: slide-in-left 1.8s ease-out forwards;
          opacity: 0;
        }

        .landing-hero {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          width: 100%;
          max-width: 36rem;
        }

        .landing-tagline {
          animation: fade-in 0.8s ease-out 1.5s forwards;
          opacity: 0;
          width: 100%;
          line-height: 1.65;
        }

        .landing-buttons {
          animation: fade-in 0.8s ease-out 2s forwards;
          opacity: 0;
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 1rem;
          width: 100%;
        }

        .cue-page {
          max-width: 42rem;
          margin-left: auto;
          margin-right: auto;
          padding-left: 1.5rem;
          padding-right: 1.5rem;
          padding-top: 2.5rem;
          padding-bottom: 2.5rem;
        }

        .cue-topbar {
          border-bottom: 1px solid rgba(${patternColor}, 0.25);
          padding: 1rem 1.5rem;
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .cue-topbar-brand {
          font-size: 1.5rem;
          font-weight: 700;
          font-style: italic;
          line-height: 1;
          color: ${palette.mocha};
        }

        .cue-topbar-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-height: 2.25rem;
          padding: 0.5rem 1rem;
          border-radius: 9999px;
          font-size: 0.875rem;
          font-weight: 600;
          line-height: 1;
          cursor: pointer;
          border: 1px solid rgba(${patternColor}, 0.3);
          box-sizing: border-box;
          transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
        }

        .cue-topbar-tabs {
          margin-left: auto;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .cue-tab-active {
          background: ${palette.purple};
          color: ${palette.cream};
          border-color: rgba(108, 108, 155, 0.4);
        }

        .cue-tab-inactive {
          background: transparent;
          color: ${palette.indigo};
        }

        .cue-tab-inactive:hover {
          background: rgba(170, 171, 202, 0.25);
          color: ${palette.indigo};
        }

        .cue-topbar-back {
          background: transparent;
          color: ${palette.indigo};
          padding: 0.5rem 0.75rem;
          min-width: 2.25rem;
        }

        .cue-topbar-back:hover {
          background: rgba(170, 171, 202, 0.25);
          color: ${palette.indigo};
          border-color: rgba(${patternColor}, 0.4);
        }

        .cue-topbar-back svg {
          width: 1.125rem;
          height: 1.125rem;
        }

        .cue-btn {
          background: ${palette.purple};
          color: ${palette.cream};
          display: inline-flex;
          align-items: center;
          justify-content: center;
          box-sizing: border-box;
          border: 1px solid rgba(108, 108, 155, 0.45);
          transition: background 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        }

        .cue-btn:hover:not(:disabled) {
          background: ${palette.indigo};
          box-shadow: 0 2px 8px rgba(79, 77, 132, 0.28);
          border-color: rgba(79, 77, 132, 0.55);
        }

        .cue-btn:disabled {
          opacity: 0.55;
        }

        .cue-btn-ghost {
          background: transparent;
          color: ${palette.indigo};
          border: 1px solid rgba(${patternColor}, 0.35);
          transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
        }

        .cue-btn-ghost:hover {
          background: rgba(170, 171, 202, 0.2);
          color: ${palette.mocha};
          border-color: rgba(164, 120, 100, 0.45);
        }

        .cue-link-muted {
          color: ${palette.indigo};
          background: none;
          border: none;
          cursor: pointer;
          transition: color 0.15s ease;
        }

        .cue-link-muted:hover {
          color: ${palette.mocha};
          text-decoration: underline;
          text-underline-offset: 2px;
        }

        .cue-input {
          background: ${palette.card};
          border: 1px solid rgba(${patternColor}, 0.4);
          color: ${palette.ink};
          box-shadow: inset 0 1px 3px rgba(${shadowColor}, 0.06);
          transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }

        .cue-input::placeholder {
          color: rgba(79, 77, 132, 0.55);
        }

        .cue-input:focus {
          outline: none;
          border-color: rgba(164, 120, 100, 0.5);
          box-shadow: inset 0 1px 3px rgba(${shadowColor}, 0.06), 0 0 0 2px rgba(170, 171, 202, 0.55);
        }

        .cue-spinner {
          border: 2px solid rgba(164, 120, 100, 0.25);
          border-top-color: ${palette.mocha};
          border-right-color: ${palette.purple};
        }

        .cue-btn-landing {
          width: 10rem;
        }

        .cue-btn-research {
          width: 9.5rem;
          flex-shrink: 0;
        }

        .cue-btn-profile-link {
          width: 5.75rem;
        }

        .cue-card {
          background: ${palette.card};
          border: 1px solid rgba(${patternColor}, 0.32);
          box-shadow:
            0 2px 10px rgba(${shadowColor}, 0.06),
            0 1px 3px rgba(108, 108, 155, 0.12);
        }

        .cue-card-label {
          color: ${palette.lavender};
          font-size: 0.75rem;
          font-weight: 600;
          letter-spacing: 0.06em;
          text-transform: uppercase;
        }

        .cue-card-title {
          color: ${palette.indigo};
        }

        .cue-question-num {
          color: ${palette.mocha};
          font-weight: 700;
          min-width: 1.25rem;
        }

        .landing-marquee {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          width: 100%;
          overflow: hidden;
          background: ${palette.purple};
          border-top: 1px solid rgba(108, 108, 155, 0.4);
          padding: 0.75rem 0;
          z-index: 20;
        }

        .landing-marquee-track {
          display: inline-block;
          white-space: nowrap;
          animation: marquee-scroll 85s linear infinite;
          letter-spacing: 0.01em;
        }

        @keyframes marquee-scroll {
          from { transform: translateX(0); }
          to { transform: translateX(-50%); }
        }
      `}</style>

      <div className="min-h-screen" style={{ color: palette.ink }}>
        <PlexusBackground
          sand={palette.sand}
          sage={palette.lavender}
          olive={palette.mocha}
          bark={palette.indigo}
        />

        <div className="cue-content min-h-screen">
          {!landingDismissed ? (
            <>
              <div className="min-h-screen flex flex-col items-center justify-center px-6">
                <div className="landing-hero">
                  <h1
                    className="landing-title text-8xl font-bold italic w-full"
                    style={{ color: palette.mocha }}
                  >
                    Cue.
                  </h1>
                  <p
                    className="landing-tagline mt-4 text-lg"
                    style={{ color: palette.indigo }}
                  >
                    Know who you are meeting & Show who you are!
                  </p>
                  <div className="landing-buttons mt-10">
                  <button
                    onClick={() => {
                      setLandingDismissed(true)
                      setTab("research")
                    }}
                    className="cue-btn cue-btn-landing py-3 rounded-full text-base font-semibold transition-opacity"
                  >
                    Research
                  </button>
                  <button
                    onClick={() => {
                      setLandingDismissed(true)
                      setTab("profile")
                    }}
                    className="cue-btn cue-btn-landing py-3 rounded-full text-base font-semibold transition-opacity"
                  >
                    Profile
                  </button>
                  </div>
                </div>
              </div>
              <div className="landing-marquee" aria-hidden="true">
                <div
                  className="landing-marquee-track text-sm"
                  style={{ color: palette.cream }}
                >
                  {marqueeContent}
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="cue-topbar">
                <button
                  onClick={() => setLandingDismissed(false)}
                  className="cue-topbar-btn cue-topbar-back"
                  aria-label="Back to home"
                >
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M19 12H5M12 19l-7-7 7-7" />
                  </svg>
                </button>
                <span className="cue-topbar-brand">Cue.</span>
                <div className="cue-topbar-tabs">
                  <button
                    type="button"
                    onClick={() => setTab("research")}
                    className={
                      "cue-topbar-btn " +
                      (tab === "research" ? "cue-tab-active" : "cue-tab-inactive")
                    }
                  >
                    Research
                  </button>
                  <button
                    type="button"
                    onClick={() => setTab("profile")}
                    className={
                      "cue-topbar-btn " +
                      (tab === "profile" ? "cue-tab-active" : "cue-tab-inactive")
                    }
                  >
                    My Profile
                  </button>
                </div>
              </div>

              {tab === "research" && (
                <div className="cue-page">
                  <h2 className="text-2xl font-bold mb-2" style={{ color: palette.mocha }}>
                    Who are you about to talk to?
                  </h2>
                  <p className="mb-8 text-sm" style={{ color: palette.indigo }}>
                    Type their name. Get their background, why they matter, and a few good questions worth asking.
                  </p>

                  <div className="flex gap-3 mb-10">
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleResearch()}
                      placeholder="e.g. Andrej Karpathy"
                      className="cue-input flex-1 rounded-xl px-4 py-3 text-sm"
                    />
                    <button
                      onClick={handleResearch}
                      disabled={loading}
                      className="cue-btn cue-btn-research py-3 rounded-xl text-sm font-semibold disabled:opacity-50"
                    >
                      {loading ? "Researching..." : "Research"}
                    </button>
                  </div>

                  {loading && (
                    <div className="text-center py-16">
                      <div
                        className="cue-spinner inline-block w-8 h-8 rounded-full animate-spin mb-4"
                      />
                      <p className="text-sm font-medium" style={{ color: palette.indigo }}>
                        Searching the web for {name}...
                      </p>
                      <p className="text-xs mt-1" style={{ color: palette.indigo }}>
                        This takes about 45 seconds
                      </p>
                    </div>
                  )}

                  {error && (
                    <div
                      className="rounded-xl p-4 text-sm"
                      style={{
                        background: "rgba(164, 120, 100, 0.1)",
                        border: "1px solid rgba(164, 120, 100, 0.3)",
                        color: palette.mocha,
                      }}
                    >
                      {error}
                    </div>
                  )}

                  {speaker && !loading && (
                    <div className="space-y-4">
                      <div className="cue-card rounded-2xl p-5">
                        <p className="cue-card-label mb-3">Speaker</p>
                        <h3 className="text-xl font-bold cue-card-title">
                          {speaker.name}
                        </h3>
                        <p className="text-sm mt-1" style={{ color: palette.indigo }}>
                          {speaker.role} at {speaker.company}
                        </p>
                        <p className="text-sm mt-3 leading-relaxed" style={{ color: palette.ink }}>
                          {speaker.why_they_matter}
                        </p>
                      </div>

                      <div className="cue-card rounded-2xl p-5">
                        <div className="flex items-center justify-between mb-3">
                          <p className="cue-card-label">Your intro line</p>
                          <button
                            onClick={() => navigator.clipboard.writeText(speaker.intro_line)}
                            className="cue-btn-ghost text-xs px-2.5 py-1 rounded-lg"
                          >
                            Copy
                          </button>
                        </div>
                        <p className="text-sm leading-relaxed italic" style={{ color: palette.ink }}>
                          "{speaker.intro_line}"
                        </p>
                      </div>

                      <div className="cue-card rounded-2xl p-5">
                        <p className="cue-card-label mb-4">5 questions to ask</p>
                        <div className="space-y-3">
                          {speaker.questions.map(function (q, i) {
                            return (
                              <div key={i} className="flex gap-3 group">
                                <span className="cue-question-num text-sm mt-0.5">
                                  {i + 1}.
                                </span>
                                <div className="flex-1">
                                  <p className="text-sm leading-relaxed" style={{ color: palette.ink }}>
                                    {q}
                                  </p>
                                </div>
                                <button
                                  onClick={() => navigator.clipboard.writeText(q)}
                                  className="cue-btn-ghost text-xs px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 shrink-0"
                                >
                                  Copy
                                </button>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {tab === "profile" && (
                <div className="cue-page">
                  <div className="cue-card rounded-2xl p-5 mb-4 text-center">
                    <input
                      ref={resumeInputRef}
                      id="resume-upload"
                      type="file"
                      accept=".pdf"
                      onChange={handleResumeUpload}
                      style={{ display: "none" }}
                    />
                    <button
                      onClick={() => resumeInputRef.current?.click()}
                      disabled={uploadingResume}
                      className="cue-btn px-6 py-2.5 rounded-full text-sm font-semibold disabled:opacity-50"
                    >
                      {myProfile ? "Update resume" : "Upload your resume"}
                    </button>
                    {myProfile && (
                      <button
                        type="button"
                        onClick={handleRemoveProfile}
                        className="cue-link-muted block mx-auto mt-2 text-xs"
                      >
                        Remove resume
                      </button>
                    )}
                    {uploadingResume && (
                      <p className="text-sm mt-3" style={{ color: palette.indigo }}>
                        Reading your resume...
                      </p>
                    )}
                  </div>

                  <div className="cue-card rounded-2xl p-6 text-center mb-4">
                    <div
                      className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center text-2xl font-bold"
                      style={{ background: palette.purple, color: palette.cream }}
                    >
                      {profileInitial}
                    </div>
                    <h2 className="text-3xl font-bold" style={{ color: palette.mocha }}>
                      {myProfile?.name || "Your Name"}
                    </h2>
                    <p className="text-sm mt-1" style={{ color: palette.mocha }}>
                      {myProfile?.tagline || "Upload your resume to get started"}
                    </p>
                    {profileLinks.length > 0 && (
                      <div className="flex gap-3 justify-center items-stretch mt-4">
                        {profileLinks.map(function (link) {
                          return (
                            <a
                              key={link.label}
                              href={link.href}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="cue-btn cue-btn-profile-link text-xs py-2 rounded-lg"
                            >
                              {link.label}
                            </a>
                          )
                        })}
                      </div>
                    )}
                  </div>

                  {myProfile && (
                    <div className="cue-card rounded-2xl p-5 mb-4">
                      <h3 className="text-sm font-semibold mb-3" style={{ color: palette.mocha }}>
                        Customize your portfolio
                      </h3>
                      <p className="text-xs mb-3" style={{ color: palette.indigo }}>
                        Theme
                      </p>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {themes.map(function (theme) {
                          const isSelected =
                            selectedTheme?.name === theme.name ||
                            (!selectedTheme && theme.name === "Cue Default")
                          return (
                            <button
                              key={theme.name}
                              type="button"
                              title={theme.name}
                              onClick={() => setSelectedTheme(theme.name === "Cue Default" ? null : theme)}
                              className="relative w-9 h-9 rounded-full shrink-0 transition-transform"
                              style={{
                                background: `linear-gradient(135deg, ${theme.background} 50%, ${theme.heading_color} 50%)`,
                                border: isSelected
                                  ? `2px solid ${palette.mocha}`
                                  : `2px solid ${theme.card_border}`,
                                boxShadow: isSelected ? `0 0 0 2px ${palette.cream}, 0 0 0 4px ${palette.mocha}` : "none",
                              }}
                              aria-label={theme.name}
                              aria-pressed={isSelected}
                            />
                          )
                        })}
                      </div>
                      <p className="text-xs mb-2" style={{ color: palette.indigo }}>
                        Font
                      </p>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {fonts.map(function (font) {
                          const isSelected =
                            selectedFont?.name === font.name ||
                            (!selectedFont && font.name === "Georgia")
                          return (
                            <button
                              key={font.name}
                              type="button"
                              onClick={() => setSelectedFont(font.name === "Georgia" ? null : font)}
                              className="text-xs px-3 py-1.5 rounded-full transition-colors"
                              style={{
                                fontFamily: font.value,
                                background: isSelected ? palette.purple : "rgba(170, 171, 202, 0.25)",
                                color: isSelected ? palette.cream : palette.ink,
                                border: isSelected
                                  ? `1px solid ${palette.purple}`
                                  : `1px solid ${palette.periwinkle}`,
                              }}
                              aria-pressed={isSelected}
                            >
                              {font.name}
                            </button>
                          )
                        })}
                      </div>
                      <button
                        type="button"
                        onClick={handleRegeneratePortfolio}
                        disabled={regeneratingPortfolio}
                        className="cue-btn px-5 py-2 rounded-full text-sm font-semibold disabled:opacity-50"
                      >
                        {regeneratingPortfolio ? "Regenerating..." : "Regenerate portfolio"}
                      </button>
                    </div>
                  )}

                  {(portfolioUrl || uploadingResume || regeneratingPortfolio) && (
                    <div className="cue-card rounded-2xl p-6 mb-4 text-center">
                      <h3 className="text-sm font-semibold mb-1" style={{ color: palette.mocha }}>
                        Share your portfolio
                      </h3>
                      <p className="text-xs mb-4" style={{ color: palette.indigo }}>
                        Scan to open your live portfolio — updates when you change theme or font
                      </p>
                      {qrCodeSrc ? (
                        <div
                          className="p-3 rounded-xl relative inline-block"
                          style={{
                            background: activeTheme.background,
                            border: `1px solid ${activeTheme.card_border}`,
                          }}
                        >
                          <img
                            key={`${portfolioUrl}-${activeTheme.name}-${selectedFont?.name || "Georgia"}`}
                            src={qrCodeSrc}
                            alt="QR code linking to portfolio"
                            width={120}
                            height={120}
                            className={regeneratingPortfolio ? "opacity-50" : ""}
                          />
                          {regeneratingPortfolio && (
                            <span
                              className="absolute inset-0 flex items-center justify-center text-[10px] font-semibold uppercase tracking-wide"
                              style={{ color: activeTheme.heading_color }}
                            >
                              Updating
                            </span>
                          )}
                        </div>
                      ) : (
                        <p className="text-xs" style={{ color: palette.indigo }}>
                          Generating portfolio QR code...
                        </p>
                      )}
                      {portfolioUrl && (
                        <a
                          href={portfolioUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs mt-3 block break-all hover:underline"
                          style={{ color: palette.mocha }}
                        >
                          {portfolioUrl}
                        </a>
                      )}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  )
}
