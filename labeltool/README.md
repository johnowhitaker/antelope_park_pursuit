# Label Tool (temporary)

A simple Flask app to assign photos from `images/antelope/` to tasks in `data/tasks.json`.

Views
- Image view (default `/`): Browse images, see current assignment, assign an image to a task, or clear the assignment. Filters: filename search, assigned/unassigned.
- Task view (`/tasks`): Original view listing tasks with per-task assignment controls.

## Setup

1. Create a virtualenv (optional) and install deps:
   - `python3 -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`

2. Run the app:
   - `python app.py`
   - Open http://127.0.0.1:5001

## Usage

- Filter by category or search text.
- For each task:
  - Use the image dropdown (filterable) and click Assign.
  - Unassign removes the current photo.
  - Open button previews the currently assigned image.

Changes are saved immediately to `../data/tasks.json` (a `.bak` backup is created on first write).

Images are served from `../images/antelope/`.
