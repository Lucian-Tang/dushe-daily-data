const store = require('../../lib/store');
const dataLoader = require('../../lib/question-loader');

const ONBOARDING_KEY = 'dongjian_onboarded_v2';

// 每日精选鉴赏内容（Phase 1 本地占位图，Phase 2 接入CMS+合规图库）
const IMG_BASE = '/images/curated';
const DAILY_FEED = [
  {
    id: 1, type: 'art',
    title: '《星月夜》· 梵高',
    source: 'MoMA 馆藏',
    image: `${IMG_BASE}/curated_1_starry.png`,
    caption: '1889年，圣雷米精神病院窗外。漩涡般的星空不是疯狂，是一个人在最黑暗的地方看见的光。',
    question: '你觉得梵高画这幅画时的心情是？'
  },
  {
    id: 2, type: 'design',
    title: 'Apple Park 访客中心',
    source: 'Foster + Partners',
    image: `${IMG_BASE}/curated_2_apple.png`,
    caption: '碳纤维屋顶，没有一根柱子。极简到只剩光和空间，这才是"少即是多"的真正含义。',
    question: '这个空间给你什么感觉？'
  },
  {
    id: 3, type: 'photo',
    title: '阿富汗少女 · Steve McCurry',
    source: '国家地理 1985',
    image: `${IMG_BASE}/curated_3_afghan.png`,
    caption: '一张照片改变了世界对难民的看法。那双眼睛说的比任何一篇文章都多。',
    question: '你从她的眼睛里读到了什么？'
  }
];

Page({
  data: {
    showOnboarding: false,
    currentSlide: 0,
    rank: { name: '观察者', icon: '👁️', color: '#CD7F32' },
    score: 0,
    streakDays: 0,
    nextRankScore: 500,
    progressPercent: 0,
    dailyFeed: DAILY_FEED,
    currentFeedIdx: 0,
    categories: [
      { id: 'ai_vs_real', emoji: '🤖', name: 'AI鉴定', count: 0 },
      { id: 'design_compare', emoji: '🎨', name: '审美对决', count: 0 },
      { id: 'prompt_compare', emoji: '💬', name: '提示词PK', count: 0 }
    ]
  },

  onLoad() {
    const onboarded = wx.getStorageSync(ONBOARDING_KEY);
    if (!onboarded) {
      this.setData({ showOnboarding: true });
    }
  },

  onShow() {
    if (!this.data.showOnboarding) {
      this.loadUserState();
      this.loadCategoryCounts();
    }
  },

  onSlideChange(e) {
    this.setData({ currentSlide: e.detail.current });
  },

  startChallenge() {
    wx.setStorageSync(ONBOARDING_KEY, true);
    this.setData({ showOnboarding: false });
    this.loadUserState();
    this.loadCategoryCounts();
  },

  loadUserState() {
    const score = store.get('score') || 0;
    const streakDays = store.get('streakDays') || 0;
    const rank = store.getRank();
    const tiers = [{ min: 0 }, { min: 500 }, { min: 1500 }, { min: 3500 }, { min: 7000 }, { min: 12000 }, { min: 99999 }];
    const currentTier = tiers.findIndex(t => t.min === rank.min);
    const nextTier = tiers[currentTier + 1];
    const nextScore = nextTier ? nextTier.min : score + 1000;
    const tierStart = rank.min;
    const tierRange = nextScore - tierStart;
    const progressPercent = tierRange > 0 ? ((score - tierStart) / tierRange * 100) : 0;
    this.setData({ rank, score, streakDays, nextRankScore: nextScore, progressPercent });
  },

  async loadCategoryCounts() {
    try {
      const questions = await dataLoader.fetchQuestions();
      const counts = { ai_vs_real: 0, design_compare: 0, prompt_compare: 0 };
      (questions || []).forEach(q => {
        if (counts[q.type] !== undefined) counts[q.type]++;
      });
      const categories = this.data.categories.map(cat => ({ ...cat, count: counts[cat.id] || 0 }));
      this.setData({ categories });
    } catch (e) {
      // 题库未加载时静默
    }
  },

  // 鉴赏内容滑动
  onFeedChange(e) {
    this.setData({ currentFeedIdx: e.detail.current });
  },

  // 鉴赏反馈
  onFeedReact(e) {
    const reaction = e.currentTarget.dataset.reaction;
    const item = this.data.dailyFeed[this.data.currentFeedIdx];
    wx.showToast({ title: reaction === 'like' ? '✨ 品味收录' : reaction === 'insight' ? '💡 洞察记录' : '👌 已记录', icon: 'none', duration: 1000 });
  },

  // 进入答题
  startDaily() {
    wx.navigateTo({ url: '/pages/challenge/challenge?mode=daily' });
  },

  startCategory(e) {
    const cat = e.currentTarget.dataset.cat;
    wx.navigateTo({ url: `/pages/challenge/challenge?mode=category&cat=${cat}` });
  },

  goCard() {
    wx.switchTab({ url: '/pages/card/card' });
  },

  onShareAppMessage() {
    return {
      title: '琢光 · AI时代，你的品味段位有多高？',
      path: '/pages/index/index'
    };
  }
});
