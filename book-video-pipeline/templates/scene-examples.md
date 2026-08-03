# 场景提示词范文（few-shot 校准 · 细节密度）

> 收录社区 GPT Image 2 提示词库（YouMind-OpenLab/awesome-gpt-image-2，CC BY 4.0）中
> 与本地风格（日系动漫水彩 / 治愈居家）契合的写法模式。**学的不是文案，是结构**——
> 每条拆解"结构 / 细节密度 / 一致性约束"三方面，供 DeepSeek 写 scene.md 和人工调
> 提示词时校准。配合 `scene-content.en.md`（字段骨架）使用。
>
> ⚠️ 仅收录结构拆解与短引用，完整提示词见原仓库；新写提示词不得整段照搬他人文案。

---

## 范文 1：治愈系多镜场景（角色一致性写法）

> 来源：awesome-gpt-image-2 No. 80「治愈系日式四格漫画」（Derek Wen，2026-07，zh）

**结构拆解**：

```
[全局] 画风 + 色板 + 氛围一句话锁定
[每格] 逐格描述：场景 + 人物姿态 + 表情 + 动作
[一致性强制段] 跨镜角色必须完全相同：面部/发型/服装/身体比例；严禁走样
[风格与质感段] 笔触/色板/阴影风格重申
[避免段] 写实摄影、3D、鲜艳色彩、角色崩坏、乱码文字
```

**细节密度示范**（短引用）：
- 姿态写到动作链：「男性站在女性身后，双手轻轻搭在她的肩膀上，两人都对着镜头微笑」
- 表情+环境合写：「并肩站在炉灶前，男性在搅拌，女性在帮忙，表情专注而幸福」
- 角色锁定用**可复用标签**：『男性：短发，长相温柔，穿着简单的毛衣或衬衫』
  『女性：中长发，长相温柔，穿着居家风格的衣服』

**对本地场景镜的启示**：
1. 本地 `scene-content.en.md` 的 Subject 应写**动作链**（谁在做什么动作+表情），不是静态站位
2. 多镜重复角色用"标签式"外貌描述（对应规则 3），跨镜不换描述
3. 色板/画风一句话重申即可，不用每镜重写（本地风格卡已物理保证）

---

## 范文 2：写实生活感人像（细节密度写法）

> 来源：awesome-gpt-image-2 No. 6「RAW 智能手机生活感人像」（2026-08，en）

**细节密度示范**（短引用）：
- 面部逐项：『白皙如瓷的皮肤、明亮且富有神采的深褐色双眸、小巧挺直的鼻梁、
  自然柔嫩的粉色嘴唇、精致年轻的五官』
- 发型+动态：『中长栗棕色头发扎成低侧马尾，柔和的八字刘海修饰脸型』
- 服装+配饰逐件：『修身的浅米色圆领短袖 T 恤，佩戴微型星星吊坠的银项链和细金手镯，
  肩背小巧的黑色皮革链条包』
- 光影+质感收尾：『自然午后日光，柔和漫射光，真实皮肤纹理，轻微传感器噪点，
  自动白平衡，真实的曝光』
- 负面：『无专业灯光，无美颜滤镜，无 AI 生成感』

**对本地场景镜的启示**：`Detail` 字段的每一条 = 「材质/状态/动态」三要素齐备；
光线写在 `Lighting` 字段，写到「光源 + 方向 + 质感」。

---

## 范文 3：动漫食谱海报（分区布局写法）

> 来源：awesome-gpt-image-2 No. 41「日式动漫风大黄芝士蛋糕食谱海报」（トクツー，2026-07）

**结构拆解**（与封面分区写法同源）：
```
画布：比例 + 整体风格 + 主色调 + 背景 → 主体布局：主角位置/动作/表情
→ 中心前景：主体物 3 层结构逐层描述 → 左侧区/底部条：分区内容
→ 文字风格：字体/颜色/装饰 → 限制条件：不添加 logo/水印/严格保持 N 个元素
```

**对本地场景镜的启示**：
1. 多元素场景（书桌/书架/街角）按「画布 → 主体 → 分区 → 限制」组织，元素不丢
2. 「严格保持 N 个元素」式计数约束可防 AI 添乱加戏（如"严格保持 1 本书 2 个马克杯"）
3. 结构描述复用 = 封面 P1 验收过的分区写法，场景镜同样适用

---

## 范文 4：无主角情绪场景（characters: false，主角按需出镜）

> 对应新规则 1"内容优先，主角按需出镜"。口播主体不是主角时，主角退场，画面直接呈现口播内容。

口播："你有没有过这样的时刻？加班到深夜，整栋楼都黑了，只剩你一个人。"

```
✅ 正确写法（主角退场，画面就是口播描述的场景本身）

Scene: Night exterior, a corporate office building seen from the street.
  Most windows dark, only one window on the 12th floor still lit.
Subject: An empty desk with a glowing laptop, a cold takeaway box,
  a crumpled coffee cup. No person visible — just the aftermath of long work.
Props: laptop (screen glow), takeaway box (open, chopsticks resting),
  coffee cup (crumpled, ring stain on desk), a phone face-down.
Lighting: cold blue night from the window, warm yellow from the laptop
  screen only, deep shadows in the cubicles behind.
Detail:
  - rows of empty desks fading into darkness
  - a single desk lamp left on, casting a lonely circle of light
  - city lights blurred through rain-streaked glass
  - a calendar on the wall with too many red marks
Emotion: isolation, exhaustion
Tone: cool
characters: false
```

```
❌ 错误写法（强行塞主角旁观）

Subject: The young woman (protagonist) sits alone at the desk typing,
  looking tired. ← 口播说的是"你"（泛指观众/现象），不是主角的具体故事，
  强行塞主角反而限制了共鸣感，也浪费了一个本该纯粹的"氛围帧"
```

**要点**：
1. 口播主语是泛指"你"（现象描述）→ 不是主角自述 → `characters: false`
2. 无主角帧靠**道具和光影讲故事**：发亮笔电、冷外卖、揉皱的咖啡杯——"加班到深夜"
   不需要一个人坐在那里才成立
3. `Lighting` / `Detail` 字段必须填足（openrouter 通道吃细节密度）

---

## 校准标准（新写 scene.md 对照自检）

1. **先判口播主体**：主角自己→`true`；他人/现象/概念→`false`（内容优先，主角按需）
2. **Subject 是动作链**：姿态 + 动作 + 表情，不是静态站位
3. **Detail 每条三要素**：材质 / 状态 / 动态（3-5 条）
4. **Lighting 三要素**：光源 + 方向 + 质感
5. **多镜角色标签一致**：重复角色用同一条外貌描述
6. **负面项**：至少写「写实摄影 / 3D / 角色崩坏 / 乱码文字」四个（动漫通道）
