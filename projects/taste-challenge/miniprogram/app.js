// 品味挑战 - 应用入口
const dataLoader = require('./lib/question-loader');
const store = require('./lib/store');

App({
  onLaunch() {
    // 初始化本地缓存
    store.init();
    // 预加载题库索引（低优先级）
    dataLoader.preloadIndex();
  },

  globalData: {
    user: {
      openId: null,
      nickname: null,
      avatarUrl: null,
      rank: 'observer',
      score: 0,
      streakDays: 0,
      tasteProfile: {
        visual: 0,
        prompt: 0,
        design: 0,
        writing: 0
      }
    },
    session: null
  }
});
