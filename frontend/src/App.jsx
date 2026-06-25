import { useState, useRef } from "react"
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
  const resumeInputRef = useRef(null)

  async function handleResumeUpload(event) {
    const file = event.target.files[0]
    if (!file) return

    if (resumeUrl) URL.revokeObjectURL(resumeUrl)
    setResumeUrl(URL.createObjectURL(file))

    const formData = new FormData()
    formData.append("file", file)
    setUploadingResume(true)
    try {
      const res = await fetch("https://cue-production-b6e2.up.railway.app/api/extract-resume", {
        method: "POST",
        body: formData,
      })
      const data = await res.json()
      setMyProfile(data)
    } catch (e) {
      console.error(e)
    } finally {
      setUploadingResume(false)
    }
  }

  function handleRemoveProfile() {
    setMyProfile(null)
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
      const res = await fetch("https://cue-production-b6e2.up.railway.app/api/research", {
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
                        This takes about 15 seconds
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
                      Upload your resume
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
                    <h2 className="text-xl font-bold" style={{ color: palette.mocha }}>
                      {myProfile?.name || "Your name"}
                    </h2>
                    <p className="text-sm mt-1" style={{ color: palette.indigo }}>
                      {myProfile?.role || "Upload your resume to get started"}
                    </p>
                    {myProfile?.skills_summary && (
                      <p className="text-xs mt-1" style={{ color: palette.ink }}>
                        {myProfile.skills_summary}
                      </p>
                    )}
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

                  <div className="space-y-3">
                    {myProfile ? (
                      myProfile.projects?.length > 0 ? (
                        myProfile.projects.map(function (project) {
                          return (
                            <div key={project.name} className="cue-card rounded-2xl p-5">
                              <h3 className="font-semibold text-sm" style={{ color: palette.mocha }}>
                                {project.name}
                              </h3>
                              <p className="text-xs mt-1 leading-relaxed" style={{ color: palette.ink }}>
                                {project.desc}
                              </p>
                              <div className="flex gap-2 mt-2 flex-wrap">
                                {project.tech.map(function (t) {
                                  return (
                                    <span
                                      key={t}
                                      className="text-xs px-2 py-0.5 rounded-full"
                                      style={{
                                        background: "rgba(170, 171, 202, 0.45)",
                                        color: palette.indigo,
                                      }}
                                    >
                                      {t}
                                    </span>
                                  )
                                })}
                              </div>
                            </div>
                          )
                        })
                      ) : (
                        <p className="text-sm text-center py-6" style={{ color: palette.indigo }}>
                          No projects found on your resume.
                        </p>
                      )
                    ) : (
                      <p className="text-sm text-center py-6" style={{ color: palette.indigo }}>
                        Upload your resume to build your profile
                      </p>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  )
}
