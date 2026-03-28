#!/bin/bash
# ============================================================
# 大鱼 TT 系统一键恢复脚本
# 用法: bash setup.sh [选项]
# ============================================================
set -e

# -------------------- 颜色 --------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err() { echo -e "${RED}[ERR]${NC} $1"; exit 1; }

# -------------------- 检测 --------------------
IS_WSL=false
if grep -qi 'microsoft\|wsl' /proc/version 2>/dev/null; then
  IS_WSL=true
  warn "检测到 WSL，某些功能可能受限"
fi

# -------------------- 参数解析 --------------------
SKIP_NVIDIA=false
SKIP_OLLAMA=false
SKIP_ZSH=false
SKIP_OPENCLAW=false
SKIP_OPENVIKING=false
DRY_RUN=false

for arg in "$@"; do
  case $arg in
    --skip-nvidia) SKIP_NVIDIA=true ;;
    --skip-ollama) SKIP_OLLAMA=true ;;
    --skip-zsh) SKIP_ZSH=true ;;
    --skip-openclaw) SKIP_OPENCLAW=false ;;
    --skip-openviking) SKIP_OPENVIKING=true ;;
    --dry-run) DRY_RUN=true ;;
  esac
done

# -------------------- 预检 --------------------
check_cmd() {
  if ! command -v $1 &>/dev/null; then
    err "缺少命令: $1，请先安装"
  fi
}

check_cmd curl
check_cmd git

# -------------------- 1. 系统更新 --------------------
log "1/7 更新系统..."
if [ "$DRY_RUN" = true ]; then
  echo "[DRY RUN] sudo apt update && sudo apt upgrade -y"
else
  sudo apt update && sudo apt upgrade -y
fi

# -------------------- 2. NVIDIA 驱动 --------------------
if [ "$SKIP_NVIDIA" = false ]; then
  log "2/7 配置 NVIDIA 驱动..."

  if command -v nvidia-smi &>/dev/null; then
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null
    log "NVIDIA 驱动已安装: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null)"
  else
    log "安装闭源 NVIDIA 驱动..."
    if [ "$DRY_RUN" = true ]; then
      echo "[DRY RUN] sudo apt install -y nvidia-driver"
    else
      sudo apt install -y nvidia-driver
    fi

    # 禁用 nouveau
    if [ -f /etc/modprobe.d/blacklist.conf ]; then
      if ! grep -q "blacklist nouveau" /etc/modprobe.d/blacklist.conf 2>/dev/null; then
        echo "blacklist nouveau" | sudo tee -a /etc/modprobe.d/blacklist.conf > /dev/null
        echo "options nouveau modeset=0" | sudo tee -a /etc/modprobe.d/blacklist.conf > /dev/null
      fi
    fi

    if command -v update-initramfs &>/dev/null; then
      log "重建 initramfs（需要重启后生效）..."
      [ "$DRY_RUN" = false ] && sudo update-initramfs -u
    fi

    log "NVIDIA 驱动安装完成，重启后生效"
    warn "请运行: sudo reboot"
  fi
else
  warn "跳过 NVIDIA 驱动安装"
fi

# -------------------- 3. Ollama --------------------
if [ "$SKIP_OLLAMA" = false ]; then
  log "3/7 配置 Ollama..."

  if command -v ollama &>/dev/null; then
    log "Ollama 已安装: $(ollama --version)"
  else
    log "安装 Ollama..."
    if [ "$DRY_RUN" = true ]; then
      echo "[DRY RUN] curl -fsSL https://ollama.ai/install.sh | sh"
    else
      curl -fsSL https://ollama.ai/install.sh | sh
    fi
  fi

  # systemd 服务（用户级）
  OLLAMA_SERVICE="$HOME/.config/systemd/user/ollama.service"
  log "创建 Ollama systemd 服务..."
  if [ "$DRY_RUN" = false ]; then
    mkdir -p "$HOME/.config/systemd/user"
    cat > "$OLLAMA_SERVICE" << 'EOF'
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
Type=simple
Environment="CUDA_VISIBLE_DEVICES=0"
Environment="OLLAMA_HOST=0.0.0.0"
Environment="HTTP_PROXY=http://localhost:7893"
Environment="HTTPS_PROXY=http://localhost:7893"
ExecStart=/home/al/.local/bin/ollama serve
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable ollama
    systemctl --user start ollama
  fi

  # 拉取模型
  if [ "$DRY_RUN" = false ]; then
    log "拉取 llama3.1 模型（需要时间，首次会很久）..."
    ollama pull llama3.1 &
    log "llama3.1 正在后台拉取，可以继续其他步骤"

    log "拉取 nomic-embed-text 嵌入模型..."
    ollama pull nomic-embed-text &
    log "nomic-embed-text 正在后台拉取"
  fi
else
  warn "跳过 Ollama 安装"
fi

# -------------------- 4. Zsh 优化 --------------------
if [ "$SKIP_ZSH" = false ]; then
  log "4/7 配置 Zsh + Starship + 插件..."

  # 安装 Starship（如果未安装）
  if ! command -v starship &>/dev/null; then
    log "安装 Starship..."
    [ "$DRY_RUN" = false ] && curl -fsSL https://starship.rs/install.sh | sh
  fi

  # Starship 初始化
  if ! grep -q 'starship init zsh' "$HOME/.zshrc" 2>/dev/null; then
    [ "$DRY_RUN" = false ] && echo 'eval "$(starship init zsh)"' >> "$HOME/.zshrc"
  fi

  # Zsh 插件
  PLUGIN_DIR="$HOME/.oh-my-zsh/plugins"
  [ "$DRY_RUN" = false ] && mkdir -p "$PLUGIN_DIR"

  # zsh-autosuggestions
  if [ ! -d "$PLUGIN_DIR/zsh-autosuggestions" ]; then
    log "安装 zsh-autosuggestions..."
    [ "$DRY_RUN" = false ] && git clone https://github.com/zsh-users/zsh-autosuggestions "$PLUGIN_DIR/zsh-autosuggestions"
  fi

  # zsh-syntax-highlighting
  if [ ! -d "$PLUGIN_DIR/zsh-syntax-highlighting" ]; then
    log "安装 zsh-syntax-highlighting..."
    [ "$DRY_RUN" = false ] && git clone https://github.com/zsh-users/zsh-syntax-highlighting "$PLUGIN_DIR/zsh-syntax-highlighting"
  fi

  # 更新插件列表
  if ! grep -q "zsh-autosuggestions" "$HOME/.zshrc" 2>/dev/null; then
    [ "$DRY_RUN" = false ] && sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/' "$HOME/.zshrc"
  fi

  # Starship 配置文件
  STARSHIP_DIR="$HOME/.config/starship.toml"
  if [ ! -f "$STARSHIP_DIR" ] && [ "$DRY_RUN" = false ]; then
    mkdir -p "$HOME/.config"
    cat > "$STARSHIP_DIR" << 'EOF'
add_newline = false
command_timeout = 500

[character]
success_symbol = "[❯](bold green)"
error_symbol = "[❯](bold red)"

[directory]
truncation_length = 3
truncate_to_repo = true
style = "bold cyan"

[git_branch]
symbol = " "
style = "bold purple"
EOF
  fi

  # tmux 优化
  TMUX_CONF_LOCAL="$HOME/.config/tmux.conf.local"
  if [ -f "$TMUX_CONF_LOCAL" ] && ! grep -q "escape-time 2" "$TMUX_CONF_LOCAL" 2>/dev/null; then
    [ "$DRY_RUN" = false ] && sed -i 's/escape-time 10/escape-time 2/' "$TMUX_CONF_LOCAL"
  fi

  log "Zsh 配置完成，新开窗口或 source ~/.zshrc 生效"
else
  warn "跳过 Zsh 配置"
fi

# -------------------- 5. OpenClaw --------------------
if [ "$SKIP_OPENCLAW" = false ]; then
  log "5/7 配置 OpenClaw..."

  if command -v openclaw &>/dev/null; then
    log "OpenClaw 已安装"
  else
    log "安装 OpenClaw..."
    [ "$DRY_RUN" = false ] && npm install -g openclaw
  fi

  # OpenClaw 配置
  OPENCLAW_CONF="$HOME/.openclaw/openclaw.json"
  if [ -f "$OPENCLAW_CONF" ]; then
    log "OpenClaw 配置文件已存在，跳过"
  else
    warn "未找到 OpenClaw 配置文件，请先在控制界面配置"
  fi

  # Telegram bot 配置（如有 token）
  log "检查 Telegram Bot 配置..."
  if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    log "Telegram Bot Token 已设置，将写入配置"
  fi

else
  warn "跳过 OpenClaw 安装"
fi

# -------------------- 6. OpenViking --------------------
if [ "$SKIP_OPENVIKING" = false ]; then
  log "6/7 配置 OpenViking..."

  if [ -d "$HOME/.local/venv-openviking" ]; then
    log "OpenViking 环境已存在"
  else
    log "创建 OpenViking Python 虚拟环境..."
    [ "$DRY_RUN" = false ] && python3 -m venv "$HOME/.local/venv-openviking"
  fi

  if [ -f "$HOME/.local/venv-openviking/bin/openviking-server" ]; then
    log "OpenViking 已安装"
  else
    [ "$DRY_RUN" = false ] && pip install openviking -i https://pypi.tuna.tsinghua.edu.cn/simple
  fi

  # OpenViking systemd 服务
  VK_SERVICE="$HOME/.config/systemd/user/openviking.service"
  if [ "$DRY_RUN" = false ]; then
    mkdir -p "$HOME/.config/systemd/user"
    cat > "$VK_SERVICE" << 'EOF'
[Unit]
Description=OpenViking Service
After=network-online.target

[Service]
Type=simple
Environment="HTTP_PROXY=http://localhost:7893"
Environment="HTTPS_PROXY=http://localhost:7893"
ExecStart=/home/al/.local/venv-openviking/bin/openviking-server
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable openviking
    systemctl --user start openviking
  fi

  # OpenViking 配置文件
  VK_CONF="$HOME/.openviking/ov.conf"
  if [ ! -f "$VK_CONF" ] && [ "$DRY_RUN" = false ]; then
    mkdir -p "$HOME/.openviking"
    cat > "$VK_CONF" << 'EOF'
{
  "storage": {
    "workspace": "/home/al/.openviking/workspace"
  },
  "log": {
    "level": "INFO",
    "output": "stdout"
  },
  "embedding": {
    "dense": {
      "api_base": "http://localhost:11434",
      "api_key": "ollama",
      "provider": "litellm",
      "dimension": 768,
      "model": "ollama/nomic-embed-text"
    },
    "max_concurrent": 10
  },
  "vlm": {
    "api_base": "http://localhost:11434",
    "api_key": "ollama",
    "provider": "litellm",
    "model": "ollama/llama3.1",
    "max_concurrent": 100
  }
}
EOF
  fi

  log "OpenViking 配置完成"

else
  warn "跳过 OpenViking 安装"
fi

# -------------------- 7. 大鱼 TT 项目索引 --------------------
log "7/7 索引大鱼 TT 项目文档..."
if [ "$DRY_RUN" = false ] && [ -d "/vol1/1000/projects/3d-printing/dayu-tt-all-in-one" ]; then
  log "大鱼 TT 项目已存在于 /vol1，跳过克隆"
else
  warn "未找到大鱼 TT 项目，请先克隆仓库"
fi

# -------------------- 完成 --------------------
echo ""
echo "=============================================="
echo -e "${GREEN}✅ 安装完成！${NC}"
echo "=============================================="
echo ""
echo "下一步："
echo "  1. 重启系统（如果安装了 NVIDIA 驱动）"
echo "  2. source ~/.zshrc  加载新的 zsh 配置"
echo "  3. 配置 Telegram Bot Token 和 TAVILY_API_KEY"
echo "  4. 访问 http://localhost:18789 验证 OpenClaw"
echo ""
echo "脚本路径: $0"
echo "支持参数: --skip-nvidia --skip-ollama --skip-zsh --skip-openclaw --skip-openviking --dry-run"
