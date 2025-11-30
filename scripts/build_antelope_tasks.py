import re
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_CATEGORIES = ROOT / 'Categories.docx'
DOC_CHALLENGES = ROOT / 'Challlenges.docx'
OUT_JSON = ROOT / 'data' / 'tasks.json'


def extract_paragraphs_from_docx(docx_path: Path):
    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read('word/document.xml').decode('utf-8', errors='ignore')
    xml = xml.replace('</w:p>', '\n')
    text = re.sub(r'<[^>]+>', '', xml)
    text = (
        text.replace('&amp;', '&')
        .replace('&lt;', '<')
        .replace('&gt;', '>')
        .replace('\r', '')
    )
    lines = [re.sub(r'\s+', ' ', l).strip() for l in text.split('\n')]
    return [l for l in lines if l]


def normalize(s: str) -> str:
    return re.sub(r'\s+', ' ', s.strip())


def main():
    categories_lines = extract_paragraphs_from_docx(DOC_CATEGORIES)
    # The categories doc includes a few headings; we only want the list items
    # After the word "Categories." and before end
    # Also there is likely a line "Challenges" which is the general category
    # Build a mapping from uppercase headings in challenges to nice-cased names from categories
    nice_categories = []
    seen = set()
    for l in categories_lines:
        if l.lower() in { 'antelope park pursuit.', 'categories.' }:
            continue
        key = normalize(l)
        if key and key not in seen:
            seen.add(key)
            nice_categories.append(key)

    # Map of challenge section headers to nice category names
    # Derive from typical known headings
    header_to_category = {
        'MAMMAL SIGHTINGS.': 'Mammal sightings',
        'MAMMAL ACTIONS.': 'Mammal action',
        'BIRD SIGHTINGS': 'Bird sightings',
        'BIRD ACTION.': 'Bird action',
        'BIRD SOUNDS.': 'Bird songs',
        'REPTILE SIGHTINGS.': 'Reptile sightings',
        'VOLUNTEERS ONLY.': 'Volunteers Only',
    }

    lines = extract_paragraphs_from_docx(DOC_CHALLENGES)
    tasks = []
    current_category = 'Challenges'
    order = 1
    # Simple scoring rubric
    default_points = {
        'Challenges': 10,
        'Mammal sightings': 5,
        'Mammal action': 10,
        'Bird sightings': 5,
        'Bird action': 10,
        'Bird songs': 5,
        'Reptile sightings': 5,
        'Volunteers Only': 20,
    }

    for raw in lines:
        line = normalize(raw)
        up = line.upper()
        if up in header_to_category:
            current_category = header_to_category[up]
            continue
        # Skip doc headings
        if up in {'ANTELOPE PARK PURSUIT.', 'CHALLENGES.'}:
            continue
        if not line:
            continue
        # Treat any other line as a challenge entry
        tid = str(order)
        tasks.append({
            'id': tid,
            'name': line,
            'description': '',
            'points': default_points.get(current_category, 5),
            'category': current_category,
            'photoURL': ''
        })
        order += 1

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    print(f'Wrote {OUT_JSON} with {len(tasks)} tasks across categories.')


if __name__ == '__main__':
    main()

