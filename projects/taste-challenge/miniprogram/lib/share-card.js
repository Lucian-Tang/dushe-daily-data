/**
 * 品味挑战 - 分享卡片生成器
 * 使用微信小程序 Canvas 2D API 离屏绘制分享卡片
 *
 * 支持模板类型:
 *   - 'challenge': 挑战结果卡（得分 + 段位 + 击败百分比）
 *   - 'promotion': 段位晋升卡（旧段位 → 新段位）
 *   - 'pk_win':     PK 胜利卡（比分 + 双方信息）
 *
 * 使用示例:
 *   const generator = new ShareCardGenerator();
 *   const filePath = await generator.generate({
 *     type: 'challenge',
 *     nickname: '小明',
 *     avatarUrl: 'https://example.com/avatar.png',
 *     tier: '品鉴师',
 *     tierIcon: '✨',
 *     score: 2500,
 *     defeatedPercent: 85,
 *     oldTier: '鉴赏者',
 *     newTier: '品鉴师',
 *     pkScore: { mine: 3, opponent: 1 },
 *     opponentNickname: '小红',
 *     opponentAvatarUrl: 'https://example.com/opponent.png'
 *   });
 */

const W = 430;
const H = 600;

// 颜色
const C = {
  bgStart: '#1A1A4E',       // 深蓝紫
  bgEnd: '#4A1028',         // 深酒红
  white: '#FFFFFF',
  gold: '#FFD700',
  goldDark: '#C9A000',
  muted: 'rgba(255,255,255,0.5)',
  dashed: 'rgba(255,255,255,0.6)',
};

// 字体配置（以 430 宽为基准，逻辑分辨率 750 换算）
function font(size) {
  return `${size * (750 / W)}rpx`;
}

class ShareCardGenerator {
  constructor() {
    this.canvas = null;
    this.ctx = null;
  }

  /**
   * 创建离屏 Canvas
   */
  _createOffscreenCanvas() {
    this.canvas = wx.createCanvasNode ? wx.createCanvasNode('share_card_canvas') : null;
    if (!this.canvas) {
      this.canvas = wx.createCanvas('share_card_canvas');
    }
    this.canvas.width = W;
    this.canvas.height = H;
    this.ctx = this.canvas.getContext('2d');
  }

  /**
   * 加载图片并返回 local path
   * @param {string} url  图片 URL
   * @returns {Promise<string>}  local 临时文件路径
   */
  _loadImage(url) {
    return new Promise((resolve) => {
      if (!url) return resolve(null);
      wx.getImageInfo({
        src: url,
        success: (res) => resolve(res.path),
        fail: () => resolve(null),
      });
    });
  }

  /**
   * 圆形裁剪头像
   * @param {string} path  图片本地路径
   * @param {number} cx    圆心 x
   * @param {number} cy    圆心 y
   * @param {number} r     半径
   */
  _drawCircleAvatar(path, cx, cy, r) {
    if (!path) {
      // 无头像时绘制占位圆
      this.ctx.beginPath();
      this.ctx.arc(cx, cy, r, 0, Math.PI * 2);
      this.ctx.fillStyle = 'rgba(255,255,255,0.15)';
      this.ctx.fill();
      this.ctx.strokeStyle = 'rgba(255,255,255,0.3)';
      this.ctx.lineWidth = 2;
      this.ctx.stroke();
      return;
    }
    this.ctx.save();
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r, 0, Math.PI * 2);
    this.ctx.closePath();
    this.ctx.clip();
    this.ctx.drawImage(path, cx - r, cy - r, r * 2, r * 2);
    this.ctx.restore();
  }

  /**
   * 绘制渐变背景
   */
  _drawBackground() {
    const ctx = this.ctx;
    const g = ctx.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, C.bgStart);
    g.addColorStop(1, C.bgEnd);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  }

  /**
   * 绘制 Luxmind 品牌文字（左上角）
   */
  _drawBrand() {
    const ctx = this.ctx;
    ctx.save();
    ctx.font = `bold ${font(13)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.muted;
    ctx.fillText('Luxmind', 20, 30);
    ctx.restore();
  }

  /**
   * 绘制底部小程序码占位区（白色虚线框）
   */
  _drawQRPlaceholder() {
    const ctx = this.ctx;
    const size = 120;
    const lx = (W - size) / 2;
    const ly = H - 30 - size;

    ctx.save();
    ctx.setLineDash([8, 6]);
    ctx.strokeStyle = C.dashed;
    ctx.lineWidth = 1.5;
    ctx.strokeRect(lx, ly, size, size);

    // 小程序码图标文字
    ctx.setLineDash([]);
    ctx.font = `${font(11)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.muted;
    ctx.textAlign = 'center';
    ctx.fillText('小程序码', W / 2, ly + size / 2 + 5);
    ctx.restore();
  }

  /**
   * 绘制虚线分隔线
   * @param {number} y  y 坐标
   */
  _drawDashedLine(y) {
    const ctx = this.ctx;
    ctx.save();
    ctx.setLineDash([6, 5]);
    ctx.strokeStyle = 'rgba(255,255,255,0.12)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(40, y);
    ctx.lineTo(W - 40, y);
    ctx.stroke();
    ctx.restore();
  }

  /**
   * ---------- 模板1: 挑战结果卡 ----------
   * 得分 + 段位 + 击败百分比
   */
  _drawChallengeTemplate(data) {
    const ctx = this.ctx;
    const { nickname, avatarUrl, tier, tierIcon, score, defeatedPercent } = data;
    const centerX = W / 2;

    // 昵称
    ctx.save();
    ctx.font = `bold ${font(24)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.white;
    ctx.textAlign = 'center';
    ctx.fillText(nickname, centerX, 95);
    ctx.restore();

    // 段位标签
    ctx.save();
    ctx.font = `${font(14)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.gold;
    ctx.textAlign = 'center';
    ctx.fillText(`${tierIcon} ${tier}`, centerX, 120);
    ctx.restore();

    // 头像
    const avatarY = 200;
    this._loadImage(avatarUrl).then((path) => {
      this._drawCircleAvatar(path, centerX, avatarY, 55);
      this.canvas.draw(); // 头像异步完成后重绘
    });

    // 得分大字
    ctx.save();
    ctx.font = `bold ${font(72)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.gold;
    ctx.textAlign = 'center';
    ctx.shadowColor = 'rgba(255, 215, 0, 0.4)';
    ctx.shadowBlur = 20;
    ctx.fillText(score, centerX, 360);
    ctx.restore();

    // 得分标签
    ctx.save();
    ctx.font = `${font(13)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.muted;
    ctx.textAlign = 'center';
    ctx.fillText('总得分', centerX, 385);
    ctx.restore();

    // 击败百分比
    this._drawDashedLine(415);
    ctx.save();
    ctx.font = `bold ${font(20)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.white;
    ctx.textAlign = 'center';
    ctx.fillText(`击败了 ${defeatedPercent}% 的玩家`, centerX, 448);
    ctx.restore();

    // 底部标语
    ctx.save();
    ctx.font = `${font(12)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.muted;
    ctx.textAlign = 'center';
    ctx.fillText('— 品味挑战 —', centerX, H - 165);
    ctx.restore();
  }

  /**
   * ---------- 模板2: 段位晋升卡 ----------
   * 旧段位 → 新段位
   */
  _drawPromotionTemplate(data) {
    const ctx = this.ctx;
    const { nickname, avatarUrl, oldTier, oldTierIcon, newTier, newTierIcon } = data;
    const centerX = W / 2;

    // 标题
    ctx.save();
    ctx.font = `${font(13)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.gold;
    ctx.textAlign = 'center';
    ctx.fillText('🎉 段位晋升', centerX, 75);
    ctx.restore();

    // 昵称
    ctx.save();
    ctx.font = `bold ${font(22)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.white;
    ctx.textAlign = 'center';
    ctx.fillText(nickname, centerX, 110);
    ctx.restore();

    // 头像
    const avatarY = 180;
    this._loadImage(avatarUrl).then((path) => {
      this._drawCircleAvatar(path, centerX, avatarY, 50);
      this.canvas.draw();
    });

    // 旧段位
    ctx.save();
    ctx.font = `${font(16)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.muted;
    ctx.textAlign = 'right';
    ctx.fillText(`${oldTierIcon} ${oldTier}`, centerX - 30, 310);
    ctx.restore();

    // 箭头
    ctx.save();
    ctx.font = `${font(24)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.gold;
    ctx.textAlign = 'center';
    ctx.fillText('→', centerX, 315);
    ctx.restore();

    // 新段位
    ctx.save();
    ctx.font = `bold ${font(16)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.gold;
    ctx.textAlign = 'left';
    ctx.fillText(`${newTierIcon} ${newTier}`, centerX + 30, 310);
    ctx.restore();

    // 底部装饰线
    this._drawDashedLine(345);
    ctx.save();
    ctx.font = `${font(12)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.muted;
    ctx.textAlign = 'center';
    ctx.fillText('— 品味挑战 —', centerX, H - 165);
    ctx.restore();
  }

  /**
   * ---------- 模板3: PK 胜利卡 ----------
   * 比分 + 双方信息
   */
  _drawPKTemplate(data) {
    const ctx = this.ctx;
    const { nickname, avatarUrl, pkScore, opponentNickname, opponentAvatarUrl } = data;
    const centerX = W / 2;
    const scoreY = 260;
    const vsX = centerX;

    // 标题
    ctx.save();
    ctx.font = `bold ${font(14)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.gold;
    ctx.textAlign = 'center';
    ctx.fillText('⚔️ PK 胜利', centerX, 70);
    ctx.restore();

    // 昵称（上方两个）
    ctx.save();
    ctx.font = `bold ${font(18)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.white;
    ctx.textAlign = 'center';
    ctx.fillText(nickname, centerX - 100, 115);
    ctx.restore();

    ctx.save();
    ctx.font = `bold ${font(18)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.white;
    ctx.textAlign = 'center';
    ctx.fillText(opponentNickname || '对手', centerX + 100, 115);
    ctx.restore();

    // 头像（上方两个）
    const leftAvatarY = 165;
    const rightAvatarY = 165;
    this._loadImage(avatarUrl).then((path) => {
      this._drawCircleAvatar(path, centerX - 100, leftAvatarY, 42);
      this.canvas.draw();
    });
    this._loadImage(opponentAvatarUrl).then((path) => {
      this._drawCircleAvatar(path, centerX + 100, rightAvatarY, 42);
      this.canvas.draw();
    });

    // VS 文字
    ctx.save();
    ctx.font = `bold ${font(20)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.muted;
    ctx.textAlign = 'center';
    ctx.fillText('VS', vsX, scoreY + 10);
    ctx.restore();

    // 比分（中间突出显示）
    // 自己的比分
    ctx.save();
    ctx.font = `bold ${font(56)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.gold;
    ctx.textAlign = 'right';
    ctx.shadowColor = 'rgba(255, 215, 0, 0.3)';
    ctx.shadowBlur = 15;
    ctx.fillText(pkScore.mine, centerX - 50, scoreY + 10);
    ctx.restore();

    // 对手比分
    ctx.save();
    ctx.font = `bold ${font(56)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = 'rgba(255,255,255,0.55)';
    ctx.textAlign = 'left';
    ctx.shadowBlur = 0;
    ctx.fillText(pkScore.opponent, centerX + 50, scoreY + 10);
    ctx.restore();

    // 分割线
    this._drawDashedLine(scoreY + 40);

    // 底部标语
    ctx.save();
    ctx.font = `${font(12)} "Helvetica Neue", Helvetica, Arial, sans-serif`;
    ctx.fillStyle = C.muted;
    ctx.textAlign = 'center';
    ctx.fillText('— 品味挑战 —', centerX, H - 165);
    ctx.restore();
  }

  /**
   * 核心方法：生成分享卡片
   * @param {Object} data  卡片数据
   * @param {string} data.type  模板类型：'challenge' | 'promotion' | 'pk_win'
   * @returns {Promise<string>}  临时图片文件路径
   */
  generate(data) {
    return new Promise((resolve, reject) => {
      try {
        this._createOffscreenCanvas();

        // 基础绘制（所有模板共用）
        this._drawBackground();
        this._drawBrand();
        this._drawQRPlaceholder();

        // 根据模板类型分发
        switch (data.type) {
          case 'challenge':
            this._drawChallengeTemplate(data);
            break;
          case 'promotion':
            this._drawPromotionTemplate(data);
            break;
          case 'pk_win':
            this._drawPKTemplate(data);
            break;
          default:
            reject(new Error(`未知的模板类型: ${data.type}，支持: challenge / promotion / pk_win`));
            return;
        }

        // 导出为临时图片
        // 先做一次 draw 再延迟导出，确保异步头像绘制完成
        this.canvas.draw({
          success: () => {
            setTimeout(() => {
              wx.canvasToTempFilePath({
                canvasId: this.canvas.canvasId || 'share_card_canvas',
                quality: 1,
                success: (res) => {
                  resolve(res.tempFilePath);
                },
                fail: (err) => {
                  reject(new Error(`canvasToTempFilePath 失败: ${JSON.stringify(err)}`));
                },
              });
            }, 300);
          },
          fail: (err) => {
            reject(new Error(`canvas draw 失败: ${JSON.stringify(err)}`));
          },
        });
      } catch (e) {
        reject(e);
      }
    });
  }
}

module.exports = ShareCardGenerator;
