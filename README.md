# PatentApply｜美术作品登记材料工程

北京原创摄影衍生插画的材料模板、生成工具和办理约定。复用已确认内容，只改本件必要事实；文字简洁，证据完整。模板不保证登记通过。

## 新作品最短路线

1. 读 [项目规则](AGENTS.md)，复制 [信息卡](docs/新作品信息卡.md) 到本地 `cases/<作品名称>/`。已有身份、研发与授权事实可沿用，只补缺项。
2. 以 [三栏文字模板](templates/作品说明书.md) 为起点；固定段落不重写，本件画面一至两句、真实调整一句，交作者确认。
3. 复制 [已发表配置](templates/published.example.json) 或 [未发表配置](templates/unpublished.example.json) 到本地。填写本件事实和证据路径，第二部分保留九张共用研发图，每图一句；单件过程图数量据实变化，总页数不固定。
4. 生成并核验文件，在当前授权内办理。各审核点、本人打印及签字交接见AGENTS；不能因生成或上传成功就标为已提交。

## PDF生成

复用已安装的Python环境，依赖见 `requirements.txt`：

```sh
python3 版权准备/补充材料PDF模板-北京-v2-20261022/build_pdf.py \
  本地配置.json 本地新输出目录
```

配置中的相对图片路径以配置所在目录解析。默认中文字体为macOS Arial Unicode；其他系统使用 `--font /path/to/chinese.ttf`。生成器拒绝待填项、发表冲突、缺图及覆盖已有PDF；生成后检查渲染、证据可读性、页数和大小。九图是本项目复用约定，不是所有北京申请的官方固定要求。

作品PNG转JPG使用 [prepare_work.py](skills/beijing-art-copyright/scripts/prepare_work.py)，先读 `--help`；原画不覆盖，必要标注放画外。

## 文档与Skill

| 入口 | 用途 |
|---|---|
| [AGENTS.md](AGENTS.md) | 长期规则、授权边界和审核停点 |
| [项目维护说明](docs/项目维护说明.md) | 唯一维护来源、历史冻结与发布方法 |
| [Skill](skills/beijing-art-copyright/SKILL.md) | 按需加载的办理流程 |
| [问题与解法](skills/beijing-art-copyright/references/lessons.md) | 返工经验及对应核验办法 |
| [仓库管理说明](docs/仓库管理说明.md) | 精确白名单与公开检查 |

本机业务入口为 `docs/模板与资料索引.md`、`docs/申请台账.md`、`cases/<作品名称>/README.md`；这些仅本地保留，克隆仓库不会带来个人材料。

Skill正式维护源是本机 `~/.codex/skills/beijing-art-copyright/`；仓库 `skills/` 为脚本导出的发布副本，不手工双线编辑。调用示例：`使用 $beijing-art-copyright，为《作品名称》准备北京美术作品登记材料，复用当前项目模板，先核对本件缺项。`

原图、成品图、PDF、OCR、会话记录、身份与签字、申请台账、回执、真实配置和校验产物均不入库；排除Git不会删除本地文件。
