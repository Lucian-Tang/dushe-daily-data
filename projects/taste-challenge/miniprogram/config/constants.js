// 品味挑战 - 常量配置
module.exports = {
  DATA_URL: 'https://lucian-tang.github.io/taste-challenge-data/questions.json',
  
  TIERS: [
    { name: '观察者', icon: '👁️', color: '#CD7F32', min: 0 },
    { name: '鉴赏者', icon: '🎨', color: '#C0C0C0', min: 500 },
    { name: '品鉴师', icon: '✨', color: '#FFD700', min: 1500 },
    { name: '审美家', icon: '💎', color: '#4169E1', min: 3500 },
    { name: '品味大师', icon: '👑', color: '#8B00FF', min: 7000 },
    { name: '灯塔', icon: '🗼', color: '#FF4500', min: 12000 }
  ],

  CATEGORIES: [
    { id: 'image', name: 'AI鉴定师', emoji: '🖼️' },
    { id: 'text', name: '文字猎手', emoji: '✍️' },
    { id: 'design', name: '审美官', emoji: '🎨' }
  ],

  COLORS: {
    bg: '#0A0A12',
    surface: '#111122',
    gold: '#FFD700',
    correct: '#00D4AA',
    wrong: '#E85D75',
    text: '#E8E8E8',
    muted: '#888'
  }
};
