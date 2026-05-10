const store = require('../../lib/store');

Page({
  data: {
    rank: { name: '观察者', icon: '👁️', color: '#CD7F32' },
    score: 0,
    history: []
  },
  onShow() {
    const score = store.get('score') || 0;
    const rank = store.getRank();
    const history = (store.get('history') || []).map(h => ({
      ...h,
      date: new Date(h.date).toLocaleDateString('zh-CN')
    }));
    this.setData({ rank, score, history });
  }
});
