# PatentApply｜美术作品登记材料工程

北京原创摄影衍生插画的登记材料工具与工作约定。此仓库保存通用代码和模板；真实申请材料在本地管理。模板不保证登记通过。

## 快速使用

Python依赖为 `requirements.txt` 中的Pillow、reportlab和pypdf。在独立环境安装依赖后：

1. 将 `templates/published.example.json` 或 `templates/unpublished.example.json` 复制到本地未跟踪目录。
2. 填写本件事实与图片路径；可按证据数量增减同一部分的页面，保持1至4部分顺序。未发表配置第四部分为纯文字说明。
3. 运行：

```sh
python3 版权准备/补充材料PDF模板-北京-v2-20261022/build_pdf.py \
  本地配置.json 本地新输出目录
```

默认中文字体为macOS Arial Unicode；其他系统用 `--font /path/to/chinese.ttf` 指定已安装中文字体。输出文件名与作品名称一致。生成器拒绝待填项、发表信息冲突与同名PDF覆盖；生成后还需目视检查排版和证据可读性，不自动上传或提交。

## 工程文档

| 入口 | 用途 |
|---|---|
| [AGENTS.md](AGENTS.md) | 项目长期规则与逐页协作边界 |
| [项目维护说明](docs/项目维护说明.md) | 文档分层与维护来源 |
| [新作品信息卡](docs/新作品信息卡.md) | 每件必要差异和确认记录 |
| [仓库管理说明](docs/仓库管理说明.md) | 跟踪范围、提交检查及本地文件保护 |

## 本机业务入口（不上传GitHub）

以下链接只在原工作目录及已有材料环境有效：

- [已确认模板与资料索引](docs/模板与资料索引.md)
- [申请台账](docs/申请台账.md)
- [小鹿已提交档案](cases/好事在鹿上原创插画/README.md)
- [个人Skill](/Users/pony/.codex/skills/beijing-art-copyright/SKILL.md)

可在原工作环境调用：`使用 $beijing-art-copyright，为《作品名称》准备北京美术作品登记材料，复用本项目模板。先核对本件缺项，暂不提交。`

原图、成品图、PDF、个人证件、签字件、会话/OCR、台账和生成输出均留本地，Git不跟踪也不删除。当前 `.gitignore` 默认忽略新文件，扩展公开范围需先检查内容。
