# 🏛️ AI Interior Designer Pro

**Design Beautiful Spaces with AI**

An AI-powered web application that turns room preferences — or a free-text
description — into photorealistic interior design visualizations, complete
with a conversational design assistant, a curated gallery, and full
history/favorites management. Built with Streamlit and Groq, deployable to
Streamlit Community Cloud in minutes.

---

## ✨ Features

- **AI Design Generator** — Configure room type, color theme, furniture
  style, lighting, ceiling, wall material, flooring, plants, décor, and
  budget tier. Selections are automatically compiled into an optimized,
  photorealistic prompt (refined by a Groq LLM when configured).
- **AI Design Assistant ("Aura")** — A Groq-powered chatbot for furniture
  ideas, color palettes, lighting plans, budget planning, renovation
  advice, Vastu Shastra, Feng Shui, and space/storage optimization.
- **Pinterest-Style Gallery** — Masonry-style curated inspiration with
  category filters and search.
- **Saved Designs & History** — Favorite any generated design and revisit
  your complete generation history at any time.
- **Modular Image Generation** — Ships with a zero-config demo renderer so
  the app runs immediately, and swaps to Hugging Face, Stability AI,
  Replicate, or Fal.ai with a single configuration value — no code changes.
- **Premium Glassmorphism UI** — Animated gradients, glass cards, gradient
  typography, hover glow, shimmer loading states, and a fully responsive
  layout.
- **Before/After Comparison** — Interactive slider to compare design
  iterations.

---

## 📸 Screenshots

> Add screenshots of the Home, Design Generator, Gallery, and Assistant
> pages here once deployed, e.g.:
>
> `docs/screenshots/home.png` · `docs/screenshots/generator.png` ·
> `docs/screenshots/gallery.png` · `docs/screenshots/assistant.png`

---

## 🧱 Architecture

```
┌─────────────┐      ┌────────────────┐      ┌───────────────────────┐
│  Streamlit   │ ───▶ │  prompt_builder │ ───▶ │   ai_service (Groq)    │
│  UI Pages    │      │  (utils/)       │      │   refines the prompt   │
└─────────────┘      └────────────────┘      └───────────┬───────────┘
       │                                                   ▼
       │                                       ┌───────────────────────┐
       └─────────────────────────────────────▶ │  image_service         │
                                                 │  (demo / HF / Stability│
                                                 │   / Replicate / Fal)   │
                                                 └───────────────────────┘
```

Session state + lightweight JSON files (`data/history.json`,
`data/favorites.json`) persist generation history and favorites.

---

## 📂 Folder Structure

```
AI_Interior_Designer/
│
├── app.py                     # Home page + shared session state bootstrap
├── requirements.txt
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── .gitignore
├── .env.example
│
├── .streamlit/
│   ├── config.toml            # Theme configuration
│   └── secrets.toml.example   # Template for local/Cloud secrets
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/ci.yml       # Lint + import/syntax check on push/PR
│
├── assets/                    # Static brand/UI assets
├── css/
│   └── style.css              # Global glassmorphism theme
├── images/                    # Local image cache (gitignored contents)
├── prompts/
│   └── sample_prompts.json    # Seed data for the Gallery page
│
├── services/
│   ├── ai_service.py          # Groq LLM: prompt refinement + chatbot
│   └── image_service.py       # Modular image generation providers
│
├── pages/
│   ├── 2_🎨_Design_Generator.py
│   ├── 3_🖼️_Gallery.py
│   ├── 4_💾_Saved_Designs.py
│   ├── 5_🤖_AI_Design_Assistant.py
│   ├── 6_📜_History.py
│   ├── 7_ℹ️_About.py
│   └── 8_⚙️_Settings.py
│
├── utils/
│   ├── helpers.py              # Session state, persistence, formatting
│   ├── theme.py                # Page config + CSS injection helpers
│   └── prompt_builder.py       # Structured options → optimized prompt
│
└── data/                        # history.json / favorites.json (gitignored)
```

> Note: `app.py` serves as the **Home** page (page `1`). Streamlit's native
> multipage navigation automatically lists everything under `pages/` in the
> sidebar in numeric-prefix order.

---

## 🚀 Installation (Local)

```bash
git clone https://github.com/<your-username>/ai-interior-designer-pro.git
cd ai-interior-designer-pro/AI_Interior_Designer

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml with your real API keys

streamlit run app.py
```

The app runs immediately even without any API keys — the image generator
falls back to a styled **demo** placeholder and the AI Assistant surfaces a
helpful fallback message until `GROQ_API_KEY` is set.

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo, branch, and set the main file path to:
   `AI_Interior_Designer/app.py` (or `app.py` if it's the repo root).
4. Under **Advanced settings → Secrets**, paste the contents of
   `.streamlit/secrets.toml.example` with your real keys filled in.
5. Click **Deploy**. No further configuration is required — the app never
   hardcodes secrets and reads everything via `st.secrets` / environment
   variables.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Recommended | Enables AI prompt refinement + the AI Design Assistant chatbot. |
| `GROQ_MODEL` | Optional | Defaults to `llama-3.3-70b-versatile`. Any supported Groq-hosted model works (e.g. `moonshotai/kimi-k2-instruct`). |
| `IMAGE_PROVIDER` | Optional | `demo` (default, no key needed) / `huggingface` / `stability` / `replicate` / `fal`. |
| `HF_API_KEY`, `HF_MODEL` | If using Hugging Face | Hugging Face Inference API credentials. |
| `STABILITY_API_KEY` | If using Stability | Stability AI REST API key. |
| `REPLICATE_API_TOKEN`, `REPLICATE_MODEL_VERSION` | If using Replicate | Replicate prediction API credentials. |
| `FAL_API_KEY` | If using Fal.ai | Fal.ai API key. |

See `.env.example` and `.streamlit/secrets.toml.example` for a ready-to-copy
template.

---

## 🔌 Swapping the Image Generation Provider

The entire image pipeline is routed through a single function,
`services/image_service.generate_image(prompt)`, dispatched via the
`IMAGE_PROVIDER` config value. To add a new provider:

1. Implement `_generate_with_<provider>(prompt: str) -> bytes` in
   `services/image_service.py`.
2. Register it in the `_PROVIDERS` dict at the bottom of the file.
3. Set `IMAGE_PROVIDER=<provider>` in your secrets/env.

No other file in the project needs to change.

---

## 🛣️ Future Scope

- 3D walkthrough / panoramic room previews
- Multi-room design boards saved as a single project
- Public shareable design links
- Team/collaborative workspaces
- Fine-tuned, style-specific image models

---

## 🤝 Contributing

Contributions are welcome! Please read [`CONTRIBUTING.md`](CONTRIBUTING.md)
for setup instructions, coding standards, and the pull request process.
Bug reports and feature requests should use the templates under
[`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/).

---

## 📄 License

Released under the [MIT License](LICENSE).
