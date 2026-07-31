# 通用封面设计规格（Canva MCP）

> 视频封面职责分离：**AI 出画（无字主视觉），Canva 出字（书名/钩子/排版）**。
> 封面是小红书笔记首图，决定点击率；文字必须 100% 保真，不交给生图模型。
> 本文件是封面的唯一规格源；`cover-prompt.md` 只负责 AI 主视觉图的 prompt。

## 尺寸矩阵

| 渠道 | 尺寸 | 用途 | 导出方式 |
|------|------|------|----------|
| 小红书（主） | 1080×1440 (3:4) | 笔记首图 | 主画布 |
| 抖音/视频号 | 1080×1920 (9:16) | 视频封面 | resize 导出 |
| 朋友圈（可选） | 1080×1080 (1:1) | 分享图 | resize 导出 |

- 主画布固定 1080×1440。Canva 导出时按矩阵做 resize，不重新排版。

## 版式分区（1080×1440 坐标）

```
y=0    ┌────────────────────────────────────┐
       │ 顶部品牌区 (0–108)                   │  左：系列名 SERIES_NAME（40px）
       │                                     │  右：EP 集数 EP_NUM（40px）
y=108  ├────────────────────────────────────┤
       │                                     │
       │ 主视觉区 (108–828)                   │  BG_FILL = AI 封面主视觉
       │  AI 插画，无字，顶部 40% 留白（软约束）  │  （主角 + 书 + 场景）
       │                                     │
y=828  ├────────────────────────────────────┤
       │ 书名区 (828–1440)                    │  渐变 scrim（上端透明 →
       │                                     │  底端深色 0.8），文字 100% 可读
       │   BOOK_TITLE   y≈880–1060  120px 粗  │  书名 ≤10 字
       │   HOOK         y≈1080–1180  62px    │  钩子 ≤12 字
       │   META         y≈1220–1320  42px    │  作者 / 副标题 / 系列标签
       │   底部安全边距 ≥80px                 │
y=1440 └────────────────────────────────────┘
```

## 元素命名规范（master 模板里的占位元素）

| 元素名（占位文本） | 类型 | 每集填充内容 |
|-------------------|------|--------------|
| `BG_FILL` | 图片 fill | AI 封面主视觉（cover-art.png） |
| `SERIES_NAME` | 文本 | 系列名（固定，如「好书慢读」） |
| `EP_NUM` | 文本 | 集数（如 EP03） |
| `BOOK_TITLE` | 文本 | 书名（≤10 字，不含书名号） |
| `HOOK` | 文本 | 钩子文案（≤12 字） |
| `META` | 文本 | 作者 / 副标题（如「马歇尔·卢森堡」） |

> 占位文本即元素标识：master 建好后文本内容 = 元素名，方便用
> `replace_text` 精确命中。每集填充时替换占位文本为真实文案。

## 字体与配色

- **字体**：Canva 中文优先（思源黑体 / 站酷快乐体等），字号层级
  书名(120) > 钩子(62) > 品牌区(40) > 元信息(42)≈品牌区。
- **配色**：取该集 `video-spec.md` 色板主色做品牌区/强调；书名区文字
  白 + scrim 深色底，保证任意主视觉下可读。禁止色板外 hex。

## 文案规则（每集）

- **书名**：≤10 字，不加《》；超长截断 + 省略号（如《非暴力沟通》→ 非暴力沟通）。
- **钩子**：≤12 字；优先取 `01-profile/book-profile.md` 选定带货角度的钩子。
- **元信息**：作者名，超长取姓 + 头衔缩写（如「马歇尔·卢森堡」）。
- 全部文案在填充前过一遍 ≤N 字校验，超限自动截断（脚本或人工）。

## 每集流程（Canva MCP，Pro 账号 = edit 事务路径）

### 一次性准备（本仓库做一次）

1. 用 Canva MCP 建 master 模板：1080×1440 空白设计 + 按上表放占位元素。
   - 若 MCP 的 create 能力只支持空白画布、不支持新增文本框：文本占位元素
     由人工在 Canva 编辑器按本规格补一次（约 2 分钟，只做一次）。
2. 记录 master 的 `design_id`，写入 `pipeline.yaml`（`cover.master_design_id`）。

### 每集（自动化）

```
1. 生图主视觉（Step 7 顺手做）：cover-prompt.md → cover/cover-art.png
2. Canva:upload-asset-from-url        # cover-art.png → asset_id
3. Canva:start-editing-transaction    # design_id = master，拿 thumbnail + pages
4. Canva:perform-editing-operations   # 一次批量：
     update_fill  → BG_FILL 换 cover-art
     replace_text → SERIES_NAME / EP_NUM / BOOK_TITLE / HOOK / META
     format_text  → 字号/字重/颜色对齐色板（若占位元素默认值不符）
5. Canva:get-design-thumbnail         # 预览，检查文案可读 + 无溢出
6. Canva:commit-editing-transaction   # 人工确认后提交
7. 导出：3:4 主图 cover/cover.png + resize 9:16 cover/cover-9x16.png
```

### 认证红线

- Canva MCP 走 OAuth，由宿主端 **Settings → MCP** 管理，授权一次即可。
- 不读 token、不缓存凭证；OAuth 状态变化时在宿主端重新连接。

## 回退方案

Canva 未授权 / MCP 不可用时，回退到纯 AI 封面（`cover-prompt.md` 旧版直接
带字生成），两者互不阻塞。回退时在 run-manifest 里标注 `cover_source: ai`。
