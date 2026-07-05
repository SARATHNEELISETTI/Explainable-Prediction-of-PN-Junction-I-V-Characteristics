# Put the app online — free, permanent link (works from any device, anytime)

This folder is a **self-contained** version of the app. Deploy it once to
**Streamlit Community Cloud** and you get a public link like
`https://your-app-name.streamlit.app` that:
- opens on **any phone or laptop** with internet, anywhere in the world,
- works **even when your computer is switched off**,
- can be **shared with your guide** so they use it independently, anytime.

Everything needed is already here: `app.py`, `model.joblib` (only ~13 MB),
`TCAD_AI_PNJunc_Dataset.csv`, and `requirements.txt`.

---

## What you need (both free, 5 minutes to create)
1. A **GitHub** account → https://github.com/signup
2. A **Streamlit Community Cloud** account → https://share.streamlit.io
   (just click "Continue with GitHub" — no separate password).

---

## Step-by-step

### Step 1 — Put this folder on GitHub
Easiest way (no commands needed):
1. Go to https://github.com/new and create a new repository, e.g. `pn-junction-ai`.
   Keep it **Public**, click **Create repository**.
2. On the new repo page click **“uploading an existing file”**.
3. Drag-and-drop the **four files from this `8_DEPLOY` folder**:
   `app.py`, `model.joblib`, `TCAD_AI_PNJunc_Dataset.csv`, `requirements.txt`.
4. Click **Commit changes**.

> The model is only ~13 MB, so it uploads fine (GitHub's limit is 100 MB).

### Step 2 — Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **Create app → Deploy a public app from GitHub**.
3. Fill in:
   - **Repository:** `your-username/pn-junction-ai`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **Deploy**. Wait 1–2 minutes while it installs the libraries.
5. You now have a permanent public URL (e.g. `https://pn-junction-ai.streamlit.app`).

### Step 3 — Share it
Send that URL to your guide. They can open it on a phone or laptop, enter the
design inputs, and get the IV graph — **no installation, no need for your PC to be
on.** The link keeps working.

---

## Notes
- **Editing later:** change `app.py` on GitHub → Streamlit redeploys automatically.
- **Sleeping apps:** free apps “sleep” after a few days of no use; the first visitor
  just clicks **“wake up”** and it starts in ~30 seconds. It never expires.
- **Keep it private?** Cloud apps from public repos are public. If you need access
  control, that's a paid feature — for a college project a public link is normal.
- This deployed version has the **Generate** and **About** tabs. The full model
  comparison / XAI figures live in the main project and the paper.

---

## Just want it on your own phone on the same WiFi (no internet deploy)?
1. Run the app on your computer: `streamlit run app.py`
2. Read the **Network URL** it prints (e.g. `http://172.22.x.x:8501`).
3. On your phone (same WiFi), open that address in a browser.
   (Allow Python through Windows Firewall if prompted.)
This needs your computer on and the same network — the cloud deploy above is the
“anywhere, anytime, independent” option.
