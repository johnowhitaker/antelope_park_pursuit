import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / 'data' / 'tasks.json'
IMAGES_DIR = ROOT / 'images' / 'antelope'

app = Flask(__name__)


def load_tasks():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_tasks(tasks):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    backup = DATA_FILE.with_suffix('.json.bak')
    if DATA_FILE.exists():
        backup.write_text(DATA_FILE.read_text(encoding='utf-8'), encoding='utf-8')
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def list_images():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for p in sorted(IMAGES_DIR.iterdir()):
        if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'} and p.is_file():
            files.append(p.name)
    return files


def image_to_tasks_map(tasks):
    mapping = {}
    for t in tasks:
        url = (t.get('photoURL') or '').strip()
        if not url:
            continue
        # extract filename
        name = url.split('/')[-1]
        mapping.setdefault(name, []).append(t)
    return mapping


@app.get('/')
def index():
    # Image-centric gallery
    q = (request.args.get('q') or '').strip().lower()
    assigned_filter = (request.args.get('assigned') or 'all').lower()  # all|yes|no
    page = int(request.args.get('page') or 1)
    per_page = 36

    images = list_images()
    tasks = load_tasks()
    img_map = image_to_tasks_map(tasks)

    # Build image records with assignment info
    records = []
    for img in images:
        assigned_to = img_map.get(img, [])
        rec = {
            'name': img,
            'assigned_to': [
                {'id': t.get('id'), 'name': t.get('name'), 'category': t.get('category')}
                for t in assigned_to
            ]
        }
        records.append(rec)

    # Filtering
    if q:
        records = [r for r in records if q in r['name'].lower()]
    if assigned_filter == 'yes':
        records = [r for r in records if r['assigned_to']]
    elif assigned_filter == 'no':
        records = [r for r in records if not r['assigned_to']]

    total = len(records)
    start = (page - 1) * per_page
    end = start + per_page
    page_records = records[start:end]
    last_page = max(1, (total + per_page - 1) // per_page)

    # For picker
    task_options = [
        {
            'id': t.get('id'),
            'label': f"{t.get('id')} • {t.get('category')} • {t.get('name')}",
        }
        for t in tasks
    ]

    return render_template('index.html',
                           images=page_records,
                           tasks=task_options,
                           total=total,
                           page=page,
                           last_page=last_page,
                           q=q,
                           assigned=assigned_filter)


@app.get('/tasks')
def tasks_view():
    # Original task-centric view
    q = (request.args.get('q') or '').strip().lower()
    category = (request.args.get('category') or '').strip()
    page = int(request.args.get('page') or 1)
    per_page = 25

    tasks = load_tasks()
    categories = sorted({t.get('category') or '' for t in tasks if t.get('category')})

    if category:
        tasks = [t for t in tasks if (t.get('category') or '') == category]
    if q:
        tasks = [t for t in tasks if q in (t.get('name','') + ' ' + t.get('description','')).lower()]

    total = len(tasks)
    start = (page - 1) * per_page
    end = start + per_page
    page_tasks = tasks[start:end]
    last_page = max(1, (total + per_page - 1) // per_page)

    images = list_images()

    return render_template('tasks.html',
                           tasks=page_tasks,
                           total=total,
                           page=page,
                           last_page=last_page,
                           q=q,
                           category=category,
                           categories=categories,
                           images=images)


@app.get('/gallery')
def gallery():
    return jsonify({'images': list_images()})


@app.post('/assign')
def assign():
    data = request.get_json(force=True)
    task_id = str(data.get('task_id'))
    image = data.get('image')  # filename only
    if not task_id or not image:
        return jsonify({'ok': False, 'error': 'task_id and image required'}), 400
    tasks = load_tasks()
    found = False
    for t in tasks:
        if str(t.get('id')) == task_id:
            t['photoURL'] = f"images/antelope/{image}"
            found = True
            break
    if not found:
        return jsonify({'ok': False, 'error': 'task not found'}), 404
    save_tasks(tasks)
    return jsonify({'ok': True})


@app.post('/assign_image')
def assign_image():
    data = request.get_json(force=True)
    task_id = str(data.get('task_id') or '')
    image = data.get('image')  # filename only
    exclusive = data.get('exclusive', True)
    if not task_id or not image:
        return jsonify({'ok': False, 'error': 'task_id and image required'}), 400
    tasks = load_tasks()
    # Optionally clear from any other tasks first (one-to-one mapping)
    if exclusive:
        for t in tasks:
            if (t.get('photoURL') or '').endswith('/' + image):
                t['photoURL'] = ''
    found = False
    for t in tasks:
        if str(t.get('id')) == task_id:
            t['photoURL'] = f"images/antelope/{image}"
            found = True
            break
    if not found:
        return jsonify({'ok': False, 'error': 'task not found'}), 404
    save_tasks(tasks)
    return jsonify({'ok': True})


@app.post('/unassign')
def unassign():
    data = request.get_json(force=True)
    task_id = str(data.get('task_id'))
    tasks = load_tasks()
    found = False
    for t in tasks:
        if str(t.get('id')) == task_id:
            t['photoURL'] = ''
            found = True
            break
    if not found:
        return jsonify({'ok': False, 'error': 'task not found'}), 404
    save_tasks(tasks)
    return jsonify({'ok': True})


@app.post('/clear_image')
def clear_image():
    data = request.get_json(force=True)
    image = data.get('image')
    if not image:
        return jsonify({'ok': False, 'error': 'image required'}), 400
    tasks = load_tasks()
    changed = False
    for t in tasks:
        if (t.get('photoURL') or '').endswith('/' + image):
            t['photoURL'] = ''
            changed = True
    if changed:
        save_tasks(tasks)
    return jsonify({'ok': True, 'changed': changed})


@app.get('/images/<path:filename>')
def serve_image(filename):
    # Support both /images/<name> and /images/antelope/<name>
    fn = filename
    if fn.startswith('antelope/'):
        fn = fn.split('/', 1)[1]
    return send_from_directory(IMAGES_DIR, fn)

@app.get('/images/antelope/<path:filename>')
def serve_image_antelope(filename):
    return send_from_directory(IMAGES_DIR, filename)


if __name__ == '__main__':
    # Run on localhost:5001 by default
    app.run(host='127.0.0.1', port=5001, debug=True)
