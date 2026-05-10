const dataLoader = require('../../lib/question-loader');
const store = require('../../lib/store');

const TAG_MAP = {
  'ai_vs_real': { label: 'AI 鉴定', color: '#4A90D9' },
  'prompt_compare': { label: 'Prompt 对决', color: '#8B00FF' },
  'design_compare': { label: '设计审美', color: '#E85D75' },
  'copy_judge': { label: '文案评判', color: '#00D4AA' }
};

Page({
  data: {
    questions: [], currentIndex: 0, totalCount: 0, question: null,
    answerIdx: -1, selectedOption: null, showResult: false, isCorrect: false,
    earnedPoints: 0, score: 0, correctCount: 0, isLast: false,
    loading: true, mode: 'daily', category: ''
  },

  onLoad(options) {
    const mode = options.mode || 'daily';
    const cat = options.cat || '';
    // Tab入口无参数时，默认daily模式
    this.setData({ mode, category: cat });
    this.loadQuestions();
  },

  async loadQuestions() {
    wx.showLoading({ title: '准备题目...' });
    let questions;
    if (this.data.mode === 'category' && this.data.category) {
      questions = await dataLoader.getCategoryQuestions(this.data.category, 5);
    } else {
      questions = await dataLoader.getDailyQuestions();
    }
    wx.hideLoading();
    if (!questions || !questions.length) {
      wx.showToast({ title: '题库加载失败', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1500);
      return;
    }
    this.setData({ questions, totalCount: questions.length, loading: false });
    this.showQuestion(0);
  },

  showQuestion(index) {
    const q = this.data.questions[index];
    if (!q) return;
    const answerIdx = this.resolveAnswer(q.answer, q.options || []);
    this.setData({
      currentIndex: index, question: q, answerIdx,
      selectedOption: null, showResult: false, isCorrect: false,
      earnedPoints: 0, isLast: index >= this.data.questions.length - 1
    });
  },

  selectOption(e) {
    if (this.data.showResult) return;
    const idx = parseInt(e.currentTarget.dataset.idx);
    if (isNaN(idx)) return;
    const correct = idx === this.data.answerIdx;
    const points = correct ? this.calcPoints(this.data.question.difficulty) : 0;
    this.setData({
      selectedOption: idx, showResult: true, isCorrect: correct,
      earnedPoints: points, score: this.data.score + points,
      correctCount: this.data.correctCount + (correct ? 1 : 0)
    });
  },

  nextQuestion() { this.showQuestion(this.data.currentIndex + 1); },

  finishChallenge() {
    store.addScore(this.data.score);
    store.recordGame(this.data.correctCount, this.data.totalCount);
    wx.redirectTo({ url: `/pages/result/result?score=${this.data.score}&correct=${this.data.correctCount}&total=${this.data.totalCount}` });
  },

  calcPoints(difficulty) { return { easy: 10, medium: 20, hard: 30 }[difficulty] || 10; },

  resolveAnswer(answer, options) {
    if (typeof answer === 'number') return answer;
    if (/^[A-C]$/.test(answer)) return answer.charCodeAt(0) - 65;
    let idx = options.findIndex(o => o === answer);
    if (idx >= 0) return idx;
    return options.findIndex(o => o.includes(answer));
  },

  getTagLabel(type) { return (TAG_MAP[type] || {}).label || type; },
  getTagColor(type) { return (TAG_MAP[type] || {}).color || '#888'; }
});
