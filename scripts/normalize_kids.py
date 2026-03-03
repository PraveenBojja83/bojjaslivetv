import os
import json
import re

root = os.path.join(os.path.dirname(__file__), '..')
livedir = os.path.join(root, 'LiveTV')

def normalize_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print('skip json parse error', path, e)
            return
    if not isinstance(data, dict):
        # unexpected JSON structure
        return
    channels = data.get('channels')
    if not isinstance(channels, dict):
        return
    new_channels = {}
    kids_list = []
    changed = False
    for key, lst in channels.items():
        if 'kids' in key.lower():
            # move into Kids
            for ch in lst:
                ch['group'] = 'Kids'
                kids_list.append(ch)
            changed = True
        else:
            new_channels[key] = lst
    if kids_list:
        # merge existing Kids key if present
        if 'Kids' in new_channels:
            # ensure group normalized
            for ch in new_channels['Kids']:
                ch['group'] = 'Kids'
            new_channels['Kids'].extend(kids_list)
        else:
            new_channels['Kids'] = kids_list
    if changed:
        data['channels'] = new_channels
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print('updated', path)


def normalize_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    new_text = re.sub(r'(?im)^Group:\s*.*kids.*$', 'Group: Kids', text)
    if new_text != text:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_text)
        print('updated txt', path)


def normalize_m3u(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    # replace group-title="...kids..." -> group-title="Kids"
    new_text = re.sub(r'(?i)group-title="[^"]*kids[^"]*"', 'group-title="Kids"', text)
    if new_text != text:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_text)
        print('updated m3u', path)


for dirpath, dirnames, filenames in os.walk(livedir):
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        if fn.lower().endswith('.json') and fn.lower().endswith('livetv.json'):
            # our file names are like LiveTV.json
            normalize_json(p)
        elif fn.lower().endswith('.json'):
            # also consider other jsons
            normalize_json(p)
        elif fn.lower().endswith('.txt'):
            normalize_txt(p)
        elif fn.lower().endswith('.m3u') or fn.lower().endswith('.m3u8'):
            normalize_m3u(p)

print('done')
