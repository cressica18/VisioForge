# VisioForge — AI Image Studio

> **From words to worlds — one prompt at a time.**

VisioForge is a professional AI image generation studio built with Python and Streamlit. Describe any scene, choose a visual aesthetic, and generate a high-quality image in seconds — powered by state-of-the-art diffusion models via the Hugging Face Inference API.

---

## Live Demo

| | |
|---|---|
| **Deployed App** | `https://visioforge-ai.streamlit.app/` |
| **GitHub Repository** | `https://github.com/cressica18/VisioForge.git`|


---

## Features

### Core
- **Text-to-image generation** powered by `black-forest-labs/FLUX.1-schnell` via Hugging Face
- **Eight visual styles**: Photorealistic, Cyberpunk, Anime, Watercolor, Oil Painting, Fantasy, Pixel Art, Minimalist Line Art
- **Style-conditioned prompting**: each style injects curated aesthetic descriptors and quality boosters automatically
- **Negative prompt support**: guide the model away from unwanted elements
- **Image size selector**: Square (1024×1024), Portrait (768×1024), Landscape (1024×768)

### UX
- **Random prompt generator**: seed your creativity with one click
- **Prompt remix**: regenerate the same subject in a different style instantly
- **Download button**: save any generated image as a PNG
- **Generation metadata card**: view the full constructed prompt, model, style, and timestamp for every image
- **Style previews**: see a description and keyword summary for each style before generating
- **Session gallery**: browse all images generated during your current session in a thumbnail grid
- **Clear history**: reset your session gallery at any time

### Engineering
- Cinematic dark theme with custom CSS — designed to match the quality of professional AI creative tools
- Fully modular architecture: UI, API, prompt logic, utilities, and configuration are completely separated
- Graceful API fallback: if the primary model fails, the app retries automatically with a fallback model
- Clean error messages for quota limits, cold-start delays, and unexpected failures

---

## Architecture

```
visioforge/
│
├── app.py                  # Streamlit UI — rendering and interaction only
├── api_client.py           # Hugging Face API integration — all HTTP logic
├── prompt_templates.py     # Style registry and prompt construction
├── utils.py                # Session state, formatting, download helpers
├── config.py               # Constants: model names, styles, sizes, seeds
├── styles.css              # Custom CSS injected at runtime
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── assets/
│   └── logo.png
│
└── .streamlit/
    └── config.toml         # Theme and server configuration
```

### Separation of Concerns

| File | Responsibility |
|---|---|
| `app.py` | Streamlit layout, user interaction, rendering — zero business logic |
| `api_client.py` | Resolves API token, calls HuggingFace, handles errors and fallback |
| `prompt_templates.py` | Style definitions, `build_styled_prompt()`, negative hints |
| `utils.py` | Session history CRUD, image encoding, filename generation |
| `config.py` | All constants — model IDs, size options, style list, random prompts |

---

## Installation

### Prerequisites
- Python 3.10 or higher
- A Hugging Face account with an API token ([get one here](https://huggingface.co/settings/tokens))

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/visioforge.git
cd visioforge

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key (see next section)

# 5. Run the app
streamlit run app.py
```

---

## Environment Variables

### Local Development

Copy `.env.example` to `.env` and set your token:

```bash
cp .env.example .env
```

Edit `.env`:

```env
HF_API_TOKEN=hf_your_actual_token_here
```

The app uses `python-dotenv` to load this automatically. **Never commit `.env` to version control.**

### Production (Streamlit Community Cloud)

In your Streamlit Cloud dashboard:

1. Open your app → **Settings → Secrets**
2. Add the following in TOML format:

```toml
HF_API_TOKEN = "hf_your_actual_token_here"
```

The app checks Streamlit Secrets first, then falls back to `os.environ`, so the same codebase works in both environments without modification.

---

## Running Locally

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` by default.

---

## Deployment (Streamlit Community Cloud)

1. Push your repository to GitHub (ensure `.env` is in `.gitignore` and not committed)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** → select your repository → set the main file to `app.py`
4. In **Advanced settings → Secrets**, add your `HF_API_TOKEN` in TOML format
5. Click **Deploy**

Streamlit Community Cloud will install dependencies from `requirements.txt` and serve the app. The URL is shareable immediately after deployment.

---

## How It Works

### Prompt Construction

Every generated image uses a three-part prompt:

```
[User Prompt]  +  [Style Descriptor]  +  [Quality Boosters]
```

**Example:**

| Part | Value |
|---|---|
| User prompt | `A futuristic Indian city at night` |
| Style (Cyberpunk) | `cyberpunk aesthetic, neon lights, rain-soaked streets, holographic signs, dystopian future` |
| Quality boosters | `cinematic lighting, highly detailed, sharp focus, professional digital art, 4K, atmospheric haze` |
| **Final prompt** | `A futuristic Indian city at night, cyberpunk aesthetic, neon lights, rain-soaked streets, holographic signs, dystopian future, cinematic lighting, highly detailed, sharp focus, professional digital art, 4K, atmospheric haze` |

All style definitions are in `prompt_templates.py` and are independently editable without touching the UI or API code.

### Model

| | |
|---|---|
| **Primary** | `black-forest-labs/FLUX.1-schnell` |
| **Fallback** | `stabilityai/stable-diffusion-xl-base-1.0` |

If the primary model fails (quota, rate limit, cold start), the app retries the fallback automatically before surfacing an error to the user.

---

## Known Limitations

1. **Hugging Face free-tier quota**: The Hugging Face Inference API free tier has monthly credit limits. If you generate many images in a short period or are on the free tier, requests may fail with a 429 (quota exceeded) error. The app surfaces a clear error message in this case.

2. **Cold-start latency**: The FLUX.1-schnell model may take 20–40 seconds to respond on the first request after a period of inactivity, as the inference provider spins up the model. Subsequent requests within the same session are typically much faster.

3. **No cross-session persistence**: The image gallery is stored in Streamlit session state and is cleared when the browser tab is closed or refreshed. Images should be downloaded before ending the session.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend / App | [Streamlit](https://streamlit.io) |
| Image Generation | [Hugging Face Inference API](https://huggingface.co/docs/inference-providers) |
| Model | [FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell) |
| HTTP Client | [huggingface-hub](https://pypi.org/project/huggingface-hub/) |
| Image Processing | [Pillow](https://pillow.readthedocs.io) |
| Secrets (local) | [python-dotenv](https://pypi.org/project/python-dotenv/) |
| Deployment | [Streamlit Community Cloud](https://share.streamlit.io) |

---

## License

MIT License. See `LICENSE` for details.
