# Pixabay 搜索关键词库（按金句情绪分类）

> A 线·金句流 Step Q4 使用。根据金句的情绪基调选择搜索词。
> 搜索词用英文（Pixabay 英文内容最丰富）。URL 编码后拼到 `pixabay.com/videos/search/{query}/`。

## 素材硬性要求（2026-08 起）

1. **素材方向：自然风光、山水（首选）**——山水/森林/湖泊/日出/云雾等自然场景；
   不选城市街景、人群、室内静物（下方室内/静物分类仅作自然风光实在搜不到时的备选）。
2. **分辨率 720p-1080p**（竖边高度 720-1080px）。
3. **单文件体积 ≤10MB**（pixabay-fetch.py 自动过滤并降档重试）。

## 情绪 → 关键词映射

### 自然风光·山水（首选）
金句调性：内省、清醒、人生感悟——适配绝大多数心理励志金句
```
mountain lake reflection calm
misty forest morning fog
mountain sunrise golden light
clouds flowing mountain peak
river flowing forest sunlight
ocean waves sunset golden
waterfall mountain mist
autumn forest aerial golden
```

### 温暖治愈
金句调性：温暖、陪伴、被理解、有人在乎
```
cozy reading book warm
warm lamp book tea
candlelight book cozy
reading nook warm light
coffee book morning sunlight
```

### 深夜思考
金句调性：孤独、自我对话、深夜感悟
```
rain window lamp night
night city lights bokeh
dark room candle warm
moon night window quiet
late night desk lamp
```

### 释怀放下
金句调性：放下、释然、重新开始
```
sunset book pages wind
autumn leaves falling warm
open window breeze curtain
beach sunset calm peaceful
field sunset golden hour
```

### 孤独平静
金句调性：一个人也挺好、内心平静
```
candle bokeh dark cozy
single cup tea table quiet
empty bench park autumn
fog forest soft light
rain drops window glass
```

### 人生感悟
金句调性：人生短暂、珍惜当下、活出自己
```
book pages wind viewpoint
old book antique pages
tree sunlight through leaves
path forest morning mist
river flowing calm nature
```

### 情感关系
金句调性：爱、关系、离别、牵挂
```
two cups coffee table warm
window rain two chairs
flowers vase warm light
hand holding book gentle
letter candle old paper
```

## 选择规则

1. 读金句稿（quote-script.md），判断整体情绪基调
2. **首选"自然风光·山水"分类**；只有其自然风光搜不到合适素材时，才落到下方室内/静物分类
3. 如果 3-5 句金句情绪混合，以**第一句（最扎心那句）**的情绪为准
4. 从对应分类里选 1 个搜索词
5. 如果搜出来的素材不理想，换同分类里的另一个词
6. 每个搜索词下载 3-5 个素材（对应金句数）

## Pixabay 筛选偏好

- 优先竖屏素材（手机拍摄的原生竖屏）
- 横屏素材也可用（hyperframes 会裁切到 9:16）
- 每个素材 5-15 秒最佳
- 暖调、有光影、有景深虚化的素材优先
- 避免有人脸正面的素材（和"严禁人物"原则一致）
- 分辨率 720p-1080p、单文件 ≤10MB（脚本自动强制）
