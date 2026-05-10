/**
 * 鉴赏页 — 精选内容浏览
 * Phase 1: 本地占位图，Phase 2: CMS驱动+合规图库
 */

const IMG_BASE = '/images/curated';

const FEED_ITEMS = [
  { id: 1, type: 'art', typeLabel: '经典艺术', typeEmoji: '🎨', source: 'MoMA 馆藏',
    title: '星月夜', subtitle: '文森特·梵高 · 1889',
    image: `${IMG_BASE}/curated_1_starry.png`,
    description: '在精神病院的窗边，梵高画下了有史以来最动人心魄的星空。那些旋转的笔触不是疯狂的证据，而是一个被困在黑暗里的人，对光最极致的渴望。',
    insight: '真正的品味不是知道这幅画值多少钱，是你能感受到那些漩涡里藏着的孤独。' },
  { id: 2, type: 'design', typeLabel: '建筑设计', typeEmoji: '🏛️', source: 'Foster + Partners',
    title: 'Apple Park 访客中心', subtitle: 'Norman Foster · 2017',
    image: `${IMG_BASE}/curated_2_apple.png`,
    description: '没有一根柱子的碳纤维屋顶，让整个空间只剩光和空气。极简不是省材料，是让每一条线都有理由存在。',
    insight: '好的设计不是加东西，是拿掉一切不需要的。这个道理不只适用于建筑。' },
  { id: 3, type: 'photo', typeLabel: '经典摄影', typeEmoji: '📷', source: '国家地理',
    title: '阿富汗少女', subtitle: 'Steve McCurry · 1985',
    image: `${IMG_BASE}/curated_3_afghan.png`,
    description: '1985年，一张照片让全世界看见了战争的代价。那双眼睛里没有眼泪，但有比任何文字都更有力的控诉。',
    insight: '真正有力量的东西，不需要解释。你的品味也应该如此——看一眼就知道对不对。' },
  { id: 4, type: 'writing', typeLabel: '经典文案', typeEmoji: '✍️', source: '耐克',
    title: 'Just Do It', subtitle: 'Dan Wieden · 1988',
    image: `${IMG_BASE}/curated_4_nike.png`,
    description: '三个单词。30年。一个品牌。最好的文案不需要形容词，不需要解释，甚至不需要语法。它只需要说中人心里那个"我知道我该做"的开关。',
    insight: '好的表达不是"说出你想说的"，是"说出对方想说但没说出口的"。' },
  { id: 5, type: 'art', typeLabel: '当代艺术', typeEmoji: '🖼️', source: 'Tate Modern',
    title: '气球狗', subtitle: 'Jeff Koons · 1994-2000',
    image: `${IMG_BASE}/curated_5_balloon.png`,
    description: '一个看起来像气球做的狗，卖了5840万美元。有人说这是当代艺术的泡沫，有人说这是波普的终极表达。你怎么看？',
    insight: '品味不只关乎"喜欢"，更关乎"知道为什么有人喜欢"。' }
];

Page({
  data: { feedItems: FEED_ITEMS, currentIdx: 0 },

  onSwiperChange(e) {
    this.setData({ currentIdx: e.detail.current });
  }
});
