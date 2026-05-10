/**
 * 名片页 — AI身份名片
 * Phase 1: 基础名片（答题数据驱动）
 */

const store = require('../../lib/store');

Page({
  data: {
    rank: { name: '观察者', icon: '👁️', color: '#CD7F32' },
    score: 0,
    totalGames: 0,
    totalCorrect: 0,
    accuracy: 0,
    dimensions: [
      { name: '品味', score: 0, icon: '🎨' },
      { name: '判断', score: 0, icon: '⚡' },
      { name: '表达', score: 0, icon: '💬', locked: true }
    ],
    vibeTags: [],
    shareEnabled: true
  },

  onShow() {
    this.loadUserData();
  },

  loadUserData() {
    const score = store.get('score') || 0;
    const history = store.get('history') || [];
    const rank = store.getRank();

    const totalGames = history.length;
    const totalCorrect = history.reduce((sum, g) => sum + (g.correct || 0), 0);
    const totalQuestions = history.reduce((sum, g) => sum + (g.total || 0), 0);
    const accuracy = totalQuestions > 0 ? Math.round((totalCorrect / totalQuestions) * 100) : 0;

    // 品味分 = 段位映射
    const tasteScore = Math.min(100, Math.round((score / 12000) * 100));
    // 判断分 = 正确率
    const judgeScore = accuracy;

    const dimensions = [
      { name: '品味', score: tasteScore, icon: '🎨' },
      { name: '判断', score: judgeScore, icon: '⚡' },
      { name: '表达', score: 0, icon: '💬', locked: true }
    ];

    // Vibe标签
    const tags = [];
    if (accuracy >= 70) tags.push('火眼金睛');
    else if (accuracy >= 50) tags.push('渐入佳境');
    else if (totalGames > 0) tags.push('初出茅庐');
    if (totalGames >= 7) tags.push('持之以恒');
    if (rank.name === '灯塔') tags.push('品味标杆');
    if (totalGames === 0) tags.push('等待启程');

    this.setData({ rank, score, totalGames, totalCorrect, accuracy, dimensions, vibeTags: tags });
  },

  onShareAppMessage() {
    return {
      title: `我的AI品味段位：${this.data.rank.name} ${this.data.rank.icon}，来看看你的？`,
      path: '/pages/index/index'
    };
  }
});
