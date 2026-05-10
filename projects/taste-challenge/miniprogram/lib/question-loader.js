// 琢光 - 题库加载器
const DATA_BASE = 'https://lucian-tang.github.io/dushe-daily-data/';
const DATA_FILE = `${DATA_BASE}taste-questions.json`;
// 内置题库（直接 require JS 模块，避免 JSON require 兼容问题）
const BUILTIN_QUESTIONS = require('./questions-data.js');

module.exports = {
  preloadIndex() {
    this.fetchQuestions().catch(() => {});
  },

  async fetchQuestions() {
    try {
      const res = await this.request(DATA_FILE);
      const questions = res.questions || [];
      if (questions.length > 0) return questions;
    } catch (e) {
      console.warn('远端题库不可用，使用内置题库');
    }
    return BUILTIN_QUESTIONS;
  },

  async getDailyQuestions(count = 5) {
    const all = await this.fetchQuestions();
    return this._randomPick(all, count);
  },

  async getCategoryQuestions(category, count = 5) {
    const all = await this.fetchQuestions();
    const filtered = all.filter(q => q.tags && q.tags.includes(category));
    return this._randomPick(filtered, count);
  },

  _randomPick(arr, count) {
    const shuffled = [...arr].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, Math.min(count, arr.length));
  },

  request(url) {
    return new Promise((resolve, reject) => {
      wx.request({
        url,
        success: res => {
          if (res.statusCode === 200) resolve(res.data);
          else reject(new Error(`HTTP ${res.statusCode}`));
        },
        fail: reject
      });
    });
  }
};
