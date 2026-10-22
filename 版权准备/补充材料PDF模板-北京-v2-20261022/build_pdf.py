#!/usr/bin/env python3
"""按配置生成图片/文字证据页；兼容已发表，支持未发表说明；不覆盖旧PDF。"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('config', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--font', type=Path, default=Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
    ap.add_argument('--max-mb', type=float, default=30)
    a = ap.parse_args()
    config_path = a.config.resolve(strict=True)
    cfg = json.loads(config_path.read_text())
    if '待填' in json.dumps(cfg, ensure_ascii=False) or '待补' in json.dumps(cfg, ensure_ascii=False):
        ap.error('配置尚有待填/待补信息')
    name = cfg['work_name']
    if not name.strip() or name != name.strip() or any(ch in name for ch in '/\\\r\n\x00') or name in {'.','..'}:
        ap.error('作品名称不能作为安全文件名')
    status = cfg.get('publication_status', 'published')
    if status not in ('published', 'unpublished'):
        ap.error('publication_status须为published或unpublished')
    if status == 'published' and not cfg.get('publication_url','').startswith(('https://','http://')):
        ap.error('已发表材料需要完整首次发表链接')
    if status == 'unpublished' and cfg.get('publication_url'):
        ap.error('未发表材料不能带首次发表网址')
    items = cfg['items']
    if not items or {p['section'] for p in items} != {1,2,3,4}:
        ap.error('配置须包括1至4部分')
    if [p['section'] for p in items] != sorted(p['section'] for p in items):
        ap.error('证据页须按四部分顺序排列')
    fourth = [p for p in items if p['section']==4]
    if status == 'unpublished' and any(p.get('image') or '首次发布' in p['title'] for p in fourth):
        ap.error('未发表第四部分应为无图片的发表状态说明')
    prepared=[]
    for item in items:
        if not item['title'].strip() or not item['caption'].strip():
            ap.error('每页需标题和简短说明')
        raw = item.get('image')
        path = (Path(raw) if Path(raw).is_absolute() else config_path.parent/raw).resolve(strict=True) if raw else None
        if path is None and not (status=='unpublished' and item['section']==4):
            ap.error('除未发表说明页外，证据页须包含图片')
        if path:
            with Image.open(path) as im: dims=im.size;im.verify()
        else: dims=None
        prepared.append((item,path,dims))
    pdfmetrics.registerFont(TTFont('CN',str(a.font)))
    output=a.output.resolve();output.mkdir(parents=True,exist_ok=True)
    pdf=output/f'{name}.pdf'
    if pdf.exists(): ap.error('PDF已存在，请使用新的输出目录')
    c=canvas.Canvas(str(pdf));c.setTitle(f'{name}-创作与发表补充材料');c.setAuthor(cfg['author'])
    def wrap(text,size,width):
        lines=[]
        for para in text.split('\n'):
            line=''
            for ch in para:
                if line and pdfmetrics.stringWidth(line+ch,'CN',size)>width:lines.append(line);line=ch
                else:line+=ch
            lines.append(line)
        return lines
    section_names=['原创摄影图（插画内容来源）','AI Skill开发过程','插画制作过程','首次发布记录' if status=='published' else '发表状态说明']
    manifest=[]
    for i,(item,path,dims) in enumerate(prepared):
        w=900 if dims and dims[0]>dims[1] else 700
        margin=32;dw=w-2*margin;dh=dw*dims[1]/dims[0] if dims else 0
        rows=[]
        def block(text,size=11,leading=17,gap=8):
            for line in wrap(text,size,dw):rows.append((line,size,leading))
            rows.append(('',size,gap))
        if i==0:
            block(f'本补充材料围绕《{name}》的创作与发表情况，共分为四部分：',12,21)
            for n,s in enumerate(section_names,1):block(f'{n}. {s}',12,21,0)
            block('以下依次展示具体内容。',12,21,16)
        block(item['title'],18,26)
        if i==0:block(f'作品：{name}    作者：{cfg["author"]}    著作权人：{cfg["copyright_owner"]}',10,16)
        block(item['caption'])
        head=32+sum(row[2] for row in rows)
        h=max(360,head+dh+38)
        c.setPageSize((w,h));y=h-32
        for line,size,leading in rows:
            c.setFont('CN',size);c.drawString(margin,y,line);y-=leading
        if path:c.drawImage(str(path),margin,h-head-dh,dw,dh)
        c.setFont('CN',9);c.setFillColorRGB(.4,.4,.4);c.drawString(margin,16,f'第{i+1}页 / 共{len(items)}页');c.setFillColorRGB(0,0,0)
        if item['section']==4 and cfg.get('publication_url'):
            url=cfg['publication_url'];size=min(8,(dw-125)/max(1,pdfmetrics.stringWidth(url,'Helvetica',1)))
            c.setFont('Helvetica',size);c.drawRightString(w-margin,16,url)
        c.showPage()
        manifest.append({'page':i+1,'title':item['title'],'caption':item['caption'],'image':str(path) if path else None,'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest() if path else None})
    c.save();r=PdfReader(pdf)
    if len(r.pages)!=len(items):raise RuntimeError('页数不符')
    for page,(item,path,_) in zip(r.pages,prepared):
        if len(page.images)!=(1 if path else 0):raise RuntimeError('图片数量不符')
        norm=lambda s:''.join(s.split())
        if norm(item['caption']) not in norm(page.extract_text()):raise RuntimeError('说明文字不完整')
    if pdf.stat().st_size>a.max_mb*1024*1024:raise RuntimeError('超出指定文件大小上限，停止上传')
    record={'file':str(pdf),'pages':len(r.pages),'bytes':pdf.stat().st_size,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'source_config':str(config_path),'publication_status':status,'items':manifest,'visual_review':'pending','uploaded':False}
    (output/'生成校验.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(pdf)


if __name__=='__main__':main()
