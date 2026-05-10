const store = require('../../lib/store');
const praise = require('../../lib/praise');

Page({
  data: {
    score: 0,
    correct: 0,
    total: 0,
    correctPercent: 0,
    praiseText: '',
    praiseEmoji: '',
    praiseTag: '',
    rankName: '观察者',
    rankIcon: '👁️',
    showCanvas: false
  },

  onLoad(options) {
    const score = parseInt(options.score) || 0;
    const correct = parseInt(options.correct) || 0;
    const total = parseInt(options.total) || 1;
    const correctPercent = Math.round((correct / total) * 100);

    // 获取彩虹屁
    const p = praise.getPraise(correctPercent);

    this.setData({
      score,
      correct,
      total,
      correctPercent,
      praiseText: p.text,
      praiseEmoji: p.emoji,
      praiseTag: p.tag,
      rankName: p.name,
      rankIcon: p.emoji
    });
  },

  shareResult() {
    this.setData({ showCanvas: true });
  },

  onShareAppMessage() {
    return {
      title: praise.getShareText(this.data.correctPercent),
      path: '/pages/index/index'
    };
  },

  challengeAgain() {
    wx.redirectTo({ url: '/pages/challenge/challenge?mode=daily' });
  },

  goHome() {
    wx.switchTab({ url: '/pages/index/index' });
  }
});
