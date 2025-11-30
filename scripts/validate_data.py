from pathlib import Path
import json
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'tasks.json'
IMG_DIR = ROOT / 'images' / 'antelope'

def main():
    tasks = json.loads(DATA.read_text(encoding='utf-8'))
    total = len(tasks)
    with_photos = [t for t in tasks if (t.get('photoURL') or '').strip()]
    n_with = len(with_photos)

    print(f"Tasks: {total}\nWith photos: {n_with} ({(n_with/total*100 if total else 0):.1f}%)\n")

    # Existence check
    missing_files = []
    normalized = []
    for t in with_photos:
        url = t['photoURL']
        fn = url.split('/')[-1]
        path = IMG_DIR / fn
        normalized.append((fn, t))
        if not path.exists():
            missing_files.append((t['id'], t['name'], fn))

    if missing_files:
        print('Missing image files:')
        for tid, name, fn in missing_files:
            print(f" - Task {tid}: {name} -> {fn} (not found)")
        print('')
    else:
        print('All referenced image files exist.\n')

    # Duplicates
    image_to_tasks = defaultdict(list)
    for fn, t in normalized:
        image_to_tasks[fn].append(t)
    dupes = {fn: lst for fn, lst in image_to_tasks.items() if len(lst) > 1}
    if dupes:
        print('Images assigned to multiple tasks:')
        for fn, lst in dupes.items():
            ids = ', '.join(str(t['id']) for t in lst)
            print(f" - {fn}: tasks {ids}")
        print('')
    else:
        print('No duplicate image assignments.\n')

    # Orphan images
    all_files = {p.name for p in IMG_DIR.glob('*') if p.is_file()}
    used_files = set(image_to_tasks.keys())
    orphans = sorted(all_files - used_files)
    print(f"Unused images in {IMG_DIR} ({len(orphans)}):")
    for fn in orphans[:50]:
        print(f" - {fn}")
    if len(orphans) > 50:
        print(f" ... and {len(orphans)-50} more")

    # Category counts
    cats = Counter((t.get('category') or 'Uncategorized') for t in tasks)
    print('\nCategory counts:')
    for cat, n in cats.most_common():
        print(f" - {cat}: {n}")

if __name__ == '__main__':
    main()

