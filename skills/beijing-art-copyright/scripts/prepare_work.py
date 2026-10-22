#!/usr/bin/env python3
"""复制原始PNG并生成登记作品JPG；不上传，不覆盖已有目录。"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--name', required=True)
    p.add_argument('--author', required=True)
    p.add_argument('--owner', required=True)
    p.add_argument('--output', required=True, type=Path, help='必须尚不存在的新目录')
    p.add_argument('--labels', action='store_true', help='在原图外加作品名、作者和著作权人')
    p.add_argument('--font', type=Path, default=Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
    p.add_argument('--max-mb', type=float, default=10, help='JPG大小上限，按当前页面调整')
    a = p.parse_args()
    if not a.name.strip() or a.name != a.name.strip() or any(c in a.name for c in '/\\\r\n\x00') or a.name in {'.', '..'}:
        p.error('作品名称为空、含路径分隔符/换行或首尾空白')
    if not a.author.strip() or not a.owner.strip() or a.max_mb <= 0:
        p.error('作者、著作权人和大小上限必须有效')
    if a.output.exists():
        p.error('输出目录已存在；使用新的版本目录，保留旧件')
    source = a.source.resolve(strict=True)
    before = digest(source)
    with Image.open(source) as opened:
        if opened.format != 'PNG':
            p.error('源文件必须是真实PNG格式')
        art = ImageOps.exif_transpose(opened).convert('RGBA')
    rgb = Image.new('RGB', art.size, 'white')
    rgb.paste(art, mask=art.getchannel('A'))
    width, height = rgb.size
    header = 0
    if a.labels:
        if not a.font.is_file():
            p.error('中文字体不存在，请指定--font')
        size = max(12, round(width * .016))
        font = ImageFont.truetype(str(a.font), size)
        margin = max(12, round(width * .02))
        if width < 100:
            p.error('图片太窄，无法排版标注')
        lines = []
        for value in (f'作品名称：{a.name}', f'作者：{a.author}', f'著作权人：{a.owner}'):
            line = ''
            for ch in value:
                if line and font.getlength(line + ch) > width - 2 * margin:
                    lines.append(line)
                    line = ch
                else:
                    line += ch
            lines.append(line)
        row = round(size * 1.5)
        header = margin * 2 + len(lines) * row
        output_image = Image.new('RGB', (width, height + header), 'white')
        output_image.paste(rgb, (0, header))
        draw = ImageDraw.Draw(output_image)
        for i, line in enumerate(lines):
            draw.text((margin, margin + i * row), line, font=font, fill='black')
    else:
        output_image = rgb
    # 独占创建新目录，避免覆盖；发生错误保留现场供排查。
    a.output.mkdir(parents=True, exist_ok=False)
    original_dir = a.output / '原图'
    original_dir.mkdir()
    copy = original_dir / f'{a.name}.png'
    shutil.copy2(source, copy)
    jpg = a.output / f'{a.name}.jpg'
    output_image.save(jpg, 'JPEG', quality=95, subsampling=0, optimize=True)
    if digest(copy) != before or digest(source) != before:
        raise RuntimeError('源件或副本hash不一致，停止后续上传')
    with Image.open(jpg) as check:
        check.load()
        if check.format != 'JPEG' or check.size != output_image.size or check.mode != 'RGB':
            raise RuntimeError('JPG读回不符')
    if jpg.stat().st_size > a.max_mb * 1024 * 1024:
        raise RuntimeError('JPG超过指定上限；保留输出供检查，不标为通过。需调整压缩方案并目视验证')
    record = {
        'source': str(source), 'source_sha256': before,
        'work_name': a.name, 'source_dimensions': [width, height],
        'output_dimensions': list(output_image.size), 'header_height': header,
        'watermark_added': False, 'alpha_background': 'white',
        'files': [{'path': str(f.resolve()), 'bytes': f.stat().st_size, 'sha256': digest(f)} for f in (copy, jpg)],
        'structural_validation': 'passed', 'visual_review': 'pending', 'uploaded': False,
    }
    (a.output / '文件校验.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(jpg.resolve())


if __name__ == '__main__':
    main()
