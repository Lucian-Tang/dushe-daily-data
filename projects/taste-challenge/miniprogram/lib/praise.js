// 琢光 - 彩虹屁文案库
// Thomas 设计 | 2026-05-09

const PRAISE_MATRIX = {
  // 段位0: 青铜·蒙眼玩家 (0-20%)
  bronze: {
    name: '蒙眼玩家', emoji: '🤦',
    low:    { text: '没关系，AI生成的图连专业摄影师都会踩坑。你只是还没开始练习而已。', tag: '鼓励' },
    mid:    { text: '踩坑是成为高手的必经之路。来，再来一轮，让AI知道你不是吃素的。', tag: '激将' },
    high:   { text: '比想象中好一点。青铜也有尊严，继续练，下一关等着你。', tag: '鼓励' },
  },
  // 段位1: 白银·雷达校准中 (21-40%)
  silver: {
    name: '雷达校准中', emoji: '🔭',
    low:    { text: '你的审美雷达正在搜索信号……没搜到。别急，AI的伪装技术也在进化。', tag: '激将' },
    mid:    { text: '有感觉了，但还差一点精准度。你的眼睛值得更好的训练。', tag: '鼓励' },
    high:   { text: '白银段位的你已经开始看出门道了。黄金在向你招手。', tag: '夸' },
  },
  // 段位2: 黄金·有点东西 (41-60%)
  gold: {
    name: '有点东西', emoji: '👀',
    low:    { text: '能对一半，说明你有点直觉。但AI在笑你："就差一点，我就骗到你了。"', tag: '激将' },
    mid:    { text: '这个成绩说明你的审美底子不错。再练几关，AI就骗不了你了。', tag: '鼓励' },
    high:   { text: '不错，你已经超过了50%的参与者。继续挑战，向铂金进发。', tag: '夸' },
  },
  // 段位3: 铂金·火眼金睛 (61-80%)
  platinum: {
    name: '火眼金睛', emoji: '🔥',
    low:    { text: 'AI生成的内容，你大部分都能看穿。但那剩下的30%，才是真正的高手战场。', tag: '鼓励' },
    mid:    { text: '你的判断力已经能让大多数AI露馅。再快一点，就能进入钻石队列了。', tag: '夸' },
    high:   { text: '铂金守门员，你已经站在前20%了。钻石在等你，不要停下来。', tag: '夸' },
  },
  // 段位4: 钻石·审美霸权 (81-95%)
  diamond: {
    name: '审美霸权', emoji: '💎',
    low:    { text: 'AI碰到你算是踢到铁板了。但别得意，剩下15%的细节还在考验你。', tag: '夸+激将' },
    mid:    { text: '你的审美已经超越了85%的用户。AI生成的内容在你眼里几乎是透明的。', tag: '夸' },
    high:   { text: '钻石段位的你，是AI最难骗的那批人。再冲一下，就是王者了。', tag: '夸' },
  },
  // 段位5: 王者·洞察原力 (96-100%)
  king: {
    name: '洞察原力', emoji: '👑',
    low:    { text: '王者，你还有3%的提升空间。AI在角落里瑟瑟发抖。', tag: '激将' },
    mid:    { text: '98分。AI生成的内容在你面前无所遁形。你是天生的审美裁判。', tag: '夸' },
    high:   { text: '💯 满分。你的眼睛是AI最害怕的武器。这台机器在你面前是透明的。', tag: '夸' },
  }
};

const TIER_KEYS = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'king'];
const TIER_PERCENT = [20, 40, 60, 80, 95, 100];

/**
 * 根据正确率获取对应的彩虹屁
 * @param {number} percent - 0-100 的正确率
 * @returns {{ name, emoji, text, tag, tierIndex, percentile }}
 */
function getPraise(percent) {
  const p = Math.max(0, Math.min(100, percent));
  let tierIndex = 0;
  for (let i = 0; i < TIER_PERCENT.length; i++) {
    if (p <= TIER_PERCENT[i]) { tierIndex = i; break; }
  }
  const key = TIER_KEYS[tierIndex];
  const tier = PRAISE_MATRIX[key];
  
  // 档位：每段位内按百分比细分
  const tierLow = tierIndex > 0 ? TIER_PERCENT[tierIndex - 1] : 0;
  const tierHigh = TIER_PERCENT[tierIndex];
  const tierRange = tierHigh - tierLow;
  const inTier = p - tierLow;
  const ratio = tierRange > 0 ? inTier / tierRange : 0.5;
  
  let band;
  if (ratio < 0.33) band = tier.low;
  else if (ratio < 0.66) band = tier.mid;
  else band = tier.high;

  return {
    name: tier.name,
    emoji: tier.emoji,
    text: band.text,
    tag: band.tag,
    tierIndex,
    percentile: p
  };
}

/**
 * 获取分享文案
 */
function getShareText(percent) {
  const p = getPraise(percent);
  const tierNames = ['青铜','白银','黄金','铂金','钻石','王者'];
  return `我在琢光的段位是${tierNames[p.tierIndex]}「${p.name}」${p.emoji}\n${p.text}\n\n来测测你的AI审美段位？`;
}

module.exports = { getPraise, getShareText, PRAISE_MATRIX, TIER_KEYS };
