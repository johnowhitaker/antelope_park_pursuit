# Antelope Park Pursuit

Family challenge app for Antelope Park. Offline-capable PWA.

How to run
- Open `index.html` with a static server (e.g., VSCode Live Preview) to enable service worker and fetch of `data/tasks.json`.

GitHub Pages
- Host from the repo root. Manifest `start_url` is set to `/antelope-park-pursuit/`.
- Service worker and asset paths are relative, so subpath hosting works.

Content
- Source docs: `Categories.docx` and `Challlenges.docx` are parsed into `data/tasks.json` via `scripts/build_antelope_tasks.py`.
- Photos extracted from `Pursuit slide show of photos.pptx` into `images/antelope/`. Photo mapping to tasks is not automatic yet; tasks currently have blank `photoURL`.

Development
- Rebuild tasks JSON: `python3 scripts/build_antelope_tasks.py`
- Reset progress in-app using the “Reset progress” button.

