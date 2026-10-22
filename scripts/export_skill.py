#!/usr/bin/env python3
"""从本机唯一维护源导出Skill发布副本；仅复制明确列出的文本文件。"""
import argparse
import hashlib
from pathlib import Path

FILES = (
    'SKILL.md', 'agents/openai.yaml', 'references/materials.md',
    'references/browser.md', 'references/lessons.md', 'scripts/prepare_work.py',
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path.home()/'.codex/skills/beijing-art-copyright')
    parser.add_argument('--check', action='store_true', help='仅比较维护源与发布副本')
    args = parser.parse_args()
    dest = Path(__file__).resolve().parents[1]/'skills/beijing-art-copyright'
    # 先完整读取并校验文本，避免遇缺文件时只更新一部分。
    data = {name: (args.source/name).read_bytes() for name in FILES}
    for value in data.values():
        value.decode('utf-8')
    differences = []
    for name, value in data.items():
        target = dest/name
        if args.check:
            if not target.is_file() or target.read_bytes() != value:
                differences.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(value)
        print(f'{name}: {hashlib.sha256(value).hexdigest()}')
    if differences:
        parser.error('发布副本与维护源不同：' + ', '.join(differences))
    print('CHECK_OK' if args.check else 'EXPORTED')


if __name__ == '__main__':
    main()
