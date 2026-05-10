// 品味挑战 - 数据存储层（本地缓存）
const CACHE_KEY = 'taste_store';

module.exports = {
  init() {
    const cached = wx.getStorageSync(CACHE_KEY);
    if (!cached) {
      wx.setStorageSync(CACHE_KEY, {
        score: 0,
        streakDays: 0,
        lastChallengeDate: null,
        tasteProfile: { visual: 0, prompt: 0, design: 0, writing: 0 },
        achievements: [],
        history: []
      });
    }
  },

  get(key) {
    const store = wx.getStorageSync(CACHE_KEY) || {};
    return key ? store[key] : store;
  },

  set(key, val) {
    const store = wx.getStorageSync(CACHE_KEY) || {};
    store[key] = val;
    wx.setStorageSync(CACHE_KEY, store);
  },

  /** 获取段位信息 */
  getRank() {
    const score = this.get('score') || 0;
    const tiers = [
      { min: 0, name: '观察者', icon: '👁️', color: '#CD7F32' },
      { min: 500, name: '鉴赏者', icon: '🎨', color: '#C0C0C0' },
      { min: 1500, name: '品鉴师', icon: '✨', color: '#FFD700' },
      { min: 3500, name: '审美家', icon: '💎', color: '#4169E1' },
      { min: 7000, name: '品味大师', icon: '👑', color: '#8B00FF' },
      { min: 12000, name: '灯塔', icon: '🗼', color: '#FF4500' }
    ];
    // 从最高段位往下找
    for (let i = tiers.length - 1; i >= 0; i--) {
      if (score >= tiers[i].min) return tiers[i];
    }
    return tiers[0];
  },

  /** 累加总分 */
  addScore(points) {
    const current = this.get('score') || 0;
    this.set('score', current + points);
  },

  /** 记录一局游戏 */
  recordGame(correct, total) {
    this.addHistory({
      date: new Date().toISOString().slice(0, 10),
      correct,
      total,
      percent: Math.round((correct / (total || 1)) * 100),
      time: Date.now()
    });
  },

  /** 记录答题历史 */
  addHistory(entry) {
    const history = this.get('history') || [];
    history.unshift(entry);
    if (history.length > 50) history.pop();
    this.set('history', history);
  }
};
