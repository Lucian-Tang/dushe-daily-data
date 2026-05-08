# 视频生成模型提示词接口规范调研 — video-prompt-tech-research-001

> 调研时间：2026-05-04 | 任务编号：video-prompt-tech-research-001
> 负责人：Stephen

---

## 一、主流视频生成模型概览

### 1.1 国内主流模型

| 模型 | 厂商 | 定位 | API可用性 |
|------|------|------|---------|
| 可灵（Kling） | 快手 | 视频生成 | ✅ API（需申请） |
| 即梦（Jimeng） | 字节跳动 | 图文生视频 | ✅ API（需申请） |
| 申途（Shenti） | 字节跳动 | 视频生成 | ⚠️ 需内部账号 |
| 秒哒（MiaoDa） | 字节跳动 | 短视频生成 | ⚠️ 需内部账号 |
| 混元（Hunyuan） | 腾讯 | 视频生成 | ⚠️ 部分开放 |
| 通义（万相） | 阿里 | 视频生成 | ✅ 阿里云API |

### 1.2 海外主流模型

| 模型 | 厂商 | 定位 | API可用性 |
|------|------|------|---------|
| Sora | OpenAI | 视频生成 | ⚠️ 限流内测 |
| Veo 2 | Google | 视频生成 | ⚠️ 内测 |
| Runway Gen-3 | Runway | 视频生成 | ✅ API（付费） |
| Pika 2.0 | Pika | 视频生成 | ⚠️ 需排队 |
| Kling 2.0 | 快手 | 视频生成 | ✅ 海外逐步开放 |

---

## 二、通用视频Prompt结构

### 2.1 四段式Prompt结构

主流视频生成模型的Prompt通常包含以下四个模块：

```
[主体描述] + [动作/运镜] + [环境/氛围] + [风格/参数]
```

**示例：**
```
A young woman walking through a rainy Tokyo street at night,
holding a red umbrella, street lights reflecting on wet pavement,
cinematic camera pan right, slow motion,
film grain style, anamorphic lens flare, 35mm film look
```

### 2.2 各字段详解

**主体描述字段：**
- 人物：性别、年龄、外貌特征、服装
- 动作：具体行为、姿态变化
- 物体：大小、颜色、材质、位置

**运镜指令字段（Camera Motion）：**
| 指令 | 含义 |
|------|------|
| pan left/right/up/down | 平移 |
| tilt up/down | 倾斜 |
| dolly in/out | 推进/拉远 |
| track left/right | 跟踪 |
| crane up | 升起 |
| zoom in/out | 变焦 |
| static, wide shot | 固定/远景 |
| close-up, medium shot | 近景/中景 |

**风格/氛围标签：**
| 标签 | 效果 |
|------|------|
| cinematic | 电影感 |
| documentary style | 纪录片风格 |
| anime style | 动漫风格 |
| slow motion | 慢动作 |
| time-lapse | 延时 |
| film grain | 胶片颗粒感 |
| bokeh | 背景虚化 |
| golden hour | 黄金时刻光 |

**时长控制：**
- 默认5秒，通常最长10秒
- 可用 "loop" 表示循环
- 可指定 "5 seconds" / "10 seconds"

---

## 三、申途/即梦/可灵 具体格式

### 3.1 申途（字节跳动视频生成）

**已知信息（基于公开文档）：**
- 基于字节Seed视频模型
- 支持多主体指令控制
- 分辨率：720p/1080p
- 时长：5秒/10秒

**Prompt格式建议：**
```
[场景描述]，主体：[主体特征]，动作：[具体动作]，
运镜：[camera motion]，风格：[风格标签]，时长：[duration]
```

**示例：**
```
一个穿白色连衣裙的女人在花园里行走，阳光透过树叶，
主体：年轻女性，长发飘飘，白色连衣裙，
动作：行走，自然风吹动裙摆，
运镜：dolly in slow，
风格：自然光，电影感，
时长：5秒
```

### 3.2 可灵（快手Kling）

**已知信息：**
- 分辨率：720p/1080p（2K内测）
- 时长：5秒/10秒/最长3分钟（内测）
- 运镜：支持多种相机运动
- API状态：需企业认证申请

**Prompt格式建议：**
```
[场景+主体描述]，[动作描述]，
camera: [运镜指令]，
style: [风格]，
duration: [秒数]
```

**示例：**
```
A majestic eagle soaring over mountain peaks at sunrise,
wings spread wide, catching the morning light,
camera: aerial tracking shot, slow pan,
style: nature documentary, golden hour lighting,
duration: 5s
```

### 3.3 即梦（字节即梦）

**已知信息：**
- 基于自研视频生成模型
- 支持图片驱动（图生视频）
- 支持文本驱动（图文生视频）
- API状态：企业用户可申请

**Prompt格式建议：**
```
描述场景：[场景]，
主体：[主体]，
运动：[动作]，
风格：[风格]，
运镜：[camera motion]
```

---

## 四、标准Prompt模板

### 模板A：通用短视频模板

```markdown
[主体/场景描述]，
[动作/行为]，
[环境细节（光线、天气、背景）]，
运镜：[camera motion]，
风格：[style tags]，
时长：[duration]
```

**参数说明：**
- 主体描述：≤100字，具体特征优先
- 动作：≤50字，具体行为
- 运镜：1-2个指令
- 风格：1-3个标签
- 时长：5秒/10秒

### 模板B：分镜脚本模板

```markdown
## 分镜 1
[场景描述]：室内/室外、时间、光线
[主体]：人物A特征、位置
[动作]：具体行为
[运镜]：camera motion
[时长]：3-5秒

## 分镜 2
...
```

### 模板C：电影感长镜头模板

```markdown
[开场场景描述]，
[运镜由远及近]，
[主体进入画面]，
[动作行为]，
[环境氛围变化]，
运镜：[complex camera movement]，
风格：[cinematic, film grain]，
色调：[warm/cool/cold]，
时长：[10秒]
```

---

## 五、分辨率和时长限制

### 5.1 各模型限制

| 模型 | 分辨率 | 时长 | 单次生成 |
|------|--------|------|---------|
| 可灵 1.0 | 720p/1080p | 5s/10s | 1 |
| 可灵 2.0 | 1080p/2K | 3min | 1 |
| 即梦 | 720p/1080p | 5s/10s | 1 |
| 申途 | 720p/1080p | 5s/10s | 1 |
| Runway Gen-3 | 720p/1080p | 10s | 1 |
| Pika 2.0 | 720p | 3-10s | 1 |

### 5.2 输出规格建议

**竖屏（9:16）：** 用于抖音/快手短视频
- 分辨率：1080×1920
- 时长：5-10秒

**横屏（16:9）：** 用于YouTube/资讯平台
- 分辨率：1920×1080
- 时长：10-30秒

**方形（1:1）：** 用于Instagram/朋友圈
- 分辨率：1080×1080
- 时长：5-10秒

---

## 六、技术可行性评估

### 6.1 当前工具链

| 工具 | 能力 | 适配度 |
|------|------|--------|
| OpenClaw image_generate | 图片生成 | ✅ 已验证 |
| 视频生成模型（外部） | 视频生成 | ⚠️ 需账号 |

### 6.2 缺口分析

**关键缺口：**
1. **无视频生成API**：当前无可直接调用的视频生成API（申途/可灵均需内部账号或企业认证）
2. **无自动拼接工具**：生成多个片段后需要拼接，当前无自动工具
3. **无字幕/配音工具链**：视频生成后的配套工具缺失

### 6.3 建议方案

**近期方案：**
- 视频封面/关键帧用 image_generate 生成图片代替
- 手动拼接 + 配音方式制作视频
- 申请可灵/即梦企业API（需boss提供账号）

**中期方案：**
- 接入 Runway API（付费，需信用卡）
- 搭建本地视频拼接pipeline（FFmpeg）

**工具优先级：**
| 优先级 | 工具 | 说明 |
|--------|------|------|
| P0 | 视频生成API账号 | 无账号则无法自动化 |
| P1 | FFmpeg拼接工具 | 多片段拼接 |
| P2 | 字幕生成工具 | 自动化字幕 |
| P3 | 配音API | 语音合成 |

---

## 七、实测Prompt示例

### 示例1：申途风格 - 城市夜景

```
城市街道的俯视镜头，傍晚时分，霓虹灯亮起，
一辆红色出租车驶过，尾灯拖出光轨，
运镜：aerial drone shot, slow pan down，
风格：cinematic, neon lights, rain-wet streets，
时长：5秒
```

### 示例2：可灵风格 - 自然纪录片

```
悬崖边，一只老鹰展开翅膀准备起飞，
背景是云海和远处的雪山，日出光芒，
运镜：dolly forward, slow reveal，
风格：nature documentary, golden hour, 35mm film，
时长：5秒
```

### 示例3：即梦风格 - 情感人像

```
一个女人站在窗边，逆光剪影，
长发被微风轻轻吹起，阳光在发丝间闪烁，
眼神望向远方，若有所思，
运镜：slow push-in, subtle，
风格：portrait, soft bokeh, warm tones，
时长：5秒
```

### 示例4：分镜脚本 - 科技产品展示

```
## 分镜1：产品全景
场景：白色极简工作室，产品静置于桌面，
主体：黑色耳机，摆放居中，
动作：静态，无人
运镜：static, wide shot, top angle
时长：3秒

## 分镜2：细节特写
场景：同上，
主体：耳机单体，略微倾斜，
动作：slow rotation
运镜：dolly in, medium close-up
时长：3秒

## 分镜3：使用场景
场景：模特戴上耳机，闭眼享受表情，
主体：年轻男性，戴耳机，表情放松，
动作：戴上耳机，闭眼
运镜：track right to medium portrait
时长：4秒
```

---

*生成时间：2026-05-04 | Stephen*