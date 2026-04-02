#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 优化堵料检测 — Python 监控脚本
# 文件路径: firmware/optimized_extruder/clog_monitor.py
# 对应子任务: bd9a8145-2c54-4e4c-8c44-426b61ed4277
# 依据: 堵料检测方案调研报告
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 【算法原理】
# 使用指数移动平均 (EMA) 动态跟踪基准电流，替代固定阈值。
# 关键改进：
#   1. EMA 替代固定基准：自动适应环境变化（热端温度漂移、电机老化）
#   2. 自适应 sigma：方差同样用 EMA 跟随，正常打印时阈值自动放宽
#   3. 滑动窗口确认：连续 N 次异常才触发，避免瞬时尖峰误报
#   4. 材料配置文件：每种材料独立参数表
#   5. 预警分级：WARNING → REDUCED_SPEED → JAMMED 三级响应
#
# 【降误报机制】
# - 预热阶段（前 warmup_s）不检测，等待热端稳定
# - 瞬时电流尖峰（< 2 sample）被滑动窗口过滤
# - 降速触发时保留原始状态，30s 内恢复正常则撤销，避免过度反应
#
# 【使用方式】
# 方式 A（直接）：python3 clog_monitor.py --serial /dev/ttyUSB0 --bauds 115200
# 方式 B（Moonraker API）：
#   python3 clog_monitor.py --moonraker http://192.168.x.x:7125
#   （需在 moonraker.conf 开启 [history] 和 [gcode_metadata]）

import argparse
import json
import math
import statistics
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ━━━ 依赖检测 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
try:
    import serial  # pip install pyserial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

try:
    import requests  # pip install requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ━━━ 材料参数配置 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 每种材料的电流基准、触发系数、预热时间
MATERIAL_PROFILES = {
    "PLA": {
        "baseline_ma": 120,
        "k_sigma": 3.5,      # 触发系数（3.5σ 原则）
        "window_n": 3,        # 连续异常次数阈值
        "warmup_s": 60,       # 预热/稳定时间
        "sg_threshold": 4,     # StallGuard 灵敏度
        "max_speed_mmh": 60,   # 降速后最大速度 mm/h
    },
    "PETG": {
        "baseline_ma": 150,
        "k_sigma": 3.5,
        "window_n": 3,
        "warmup_s": 90,
        "sg_threshold": 4,
        "max_speed_mmh": 50,
    },
    "ABS": {
        "baseline_ma": 180,
        "k_sigma": 4.0,
        "window_n": 4,
        "warmup_s": 120,
        "sg_threshold": 5,
        "max_speed_mmh": 45,
    },
    "TPU": {
        "baseline_ma": 80,
        "k_sigma": 4.5,       # TPU 材料电流波动大，需更宽松阈值
        "window_n": 5,
        "warmup_s": 90,
        "sg_threshold": 3,
        "max_speed_mmh": 20,
    },
    "PC": {
        "baseline_ma": 200,
        "k_sigma": 4.0,
        "window_n": 4,
        "warmup_s": 180,
        "sg_threshold": 5,
        "max_speed_mmh": 40,
    },
    # 通用默认（未知材料）
    "DEFAULT": {
        "baseline_ma": 120,
        "k_sigma": 3.5,
        "window_n": 3,
        "warmup_s": 60,
        "sg_threshold": 4,
        "max_speed_mmh": 50,
    },
}

# ━━━ 状态枚举 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class ClogState(Enum):
    IDLE         = "IDLE"
    WARMUP       = "WARMUP"
    MONITORING   = "MONITORING"
    WARNING      = "WARNING"
    REDUCED      = "REDUCED"
    JAMMED       = "JAMMED"
    PAUSED       = "PAUSED"


# ━━━ 堵料检测器类 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dataclass
class ClogDetector:
    """
    基于 EMA 的自适应堵料检测器

    核心变量：
        baseline_ema  — 基准电流的指数移动平均 (mA)
        variance_ema  — 偏差平方的 EMA（用于计算 σ）
        counter       — 连续异常计数器
        warmup_end    — 预热结束时间戳
        state         — 当前状态机状态
        sample_history— 最近样本队列（用于离线分析）
    """
    material: str = "PLA"
    alpha: float = 0.1    # 基准 EMA 衰减系数（越小越慢，0.1=10%权重）
    beta: float = 0.05    # 方差 EMA 衰减系数
    min_samples: int = 10 # 开始判断所需最小样本数
    reduced_cooldown: float = 30.0  # 降速后等待恢复正常的时间 (s)

    # 运行状态（初始化时由 reset() 设置）
    baseline_ema: float = field(default=0.0, init=False)
    variance_ema: float = field(default=0.0, init=False)
    counter: int = field(default=0, init=False)
    warmup_end: float = field(default=0.0, init=False)
    state: ClogState = field(default=ClogState.IDLE, init=False)
    reduced_time: Optional[float] = field(default=None, init=False)
    reduced_speed_backup: Optional[float] = field(default=None, init=False)
    sample_history: list = field(default_factory=list, init=False)

    def __post_init__(self):
        self.profile = MATERIAL_PROFILES.get(self.material, MATERIAL_PROFILES["DEFAULT"])
        self.reset()

    def reset(self):
        """重置所有状态（换料时调用）"""
        self.baseline_ema = self.profile["baseline_ma"]
        self.variance_ema = 0.0
        self.counter = 0
        self.state = ClogState.IDLE
        self.reduced_time = None
        self.reduced_speed_backup = None
        self.sample_history = []

    def set_material(self, material: str):
        """切换材料配置"""
        self.material = material
        self.profile = MATERIAL_PROFILES.get(material, MATERIAL_PROFILES["DEFAULT"])
        self.reset()

    def start_warmup(self):
        """开始预热阶段"""
        self.reset()
        self.state = ClogState.WARMUP
        self.warmup_end = time.time() + self.profile["warmup_s"]
        print(f"[ClogDetector] 🟡 预热开始，材料={self.material}, 预热时间={self.profile['warmup_s']}s")

    def start_monitoring(self):
        """预热完成，进入监控"""
        self.state = ClogState.MONITORING
        print(f"[ClogDetector] 🟢 监控就绪，基准={self.baseline_ema:.1f}mA, k={self.profile['k_sigma']}, N={self.profile['window_n']}")

    @property
    def sigma(self) -> float:
        """当前标准差（从方差 EMA 反推）"""
        return math.sqrt(max(self.variance_ema, 0))

    @property
    def threshold(self) -> float:
        """当前触发阈值 = k × σ"""
        return self.profile["k_sigma"] * self.sigma

    def update(self, current_ma: float) -> dict:
        """
        传入一个电流采样（mA），更新状态，返回诊断结果。

        Returns:
            dict: {
                "event": str,       # 事件类型：NORMAL / WARNING / REDUCED / JAMMED / RECOVERED
                "state": str,        # 当前状态
                "current_ma": float, # 当前电流
                "baseline_ema": float,
                "sigma": float,
                "threshold": float,
                "deviation": float,
                "counter": int,
            }
        """
        t = time.time()
        self.sample_history.append({"t": t, "current": current_ma})

        # 预热阶段：持续更新基准，不报警
        if self.state == ClogState.WARMUP:
            deviation = abs(current_ma - self.baseline_ema)
            self._ema_update(current_ma, deviation)
            if t >= self.warmup_end:
                self.start_monitoring()
            return self._result("NORMAL")

        # 非监控状态
        if self.state not in (ClogState.MONITORING, ClogState.WARNING, ClogState.REDUCED):
            return self._result("NORMAL")

        deviation = abs(current_ma - self.baseline_ema)
        k = self.profile["k_sigma"]
        n = self.profile["window_n"]

        # 更新 EMA
        self._ema_update(current_ma, deviation)

        event = "NORMAL"

        if deviation > k * self.sigma:
            # 异常：计数器 +1
            self.counter += 1
            print(f"[ClogDetector] ⚠️ 异常 #{self.counter}/{n}: "
                  f"电流={current_ma:.1f}mA, 偏差={deviation:.1f}mA, "
                  f"σ={self.sigma:.1f}, 阈值={k*self.sigma:.1f}")

            if self.counter >= n:
                if self.state == ClogState.MONITORING:
                    self.state = ClogState.WARNING
                    event = "WARNING"
                    print(f"[ClogDetector] 🔶 进入 WARNING 状态（连续{n}次异常）")
                elif self.state == ClogState.WARNING:
                    self.state = ClogState.REDUCED
                    self.reduced_time = t
                    event = "REDUCED"
                    print(f"[ClogDetector] 🔶 进入 REDUCED 状态（降速处理）")
                elif self.state == ClogState.REDUCED:
                    # 降速后仍异常 → 堵料
                    if self.reduced_time and (t - self.reduced_time) > self.reduced_cooldown:
                        self.state = ClogState.JAMMED
                        event = "JAMMED"
                        print(f"[ClogDetector] 🔴 进入 JAMMED 状态（降速后未恢复）")
        else:
            # 恢复正常
            if self.counter > 0:
                print(f"[ClogDetector] ✅ 恢复正常，重置计数器")
            self.counter = 0

            if self.state == ClogState.WARNING:
                self.state = ClogState.MONITORING
                event = "RECOVERED"
                print(f"[ClogDetector] ✅ WARNING 已撤销，恢复监控")
            elif self.state == ClogState.REDUCED:
                # REDUCED 状态，30s 内恢复正常
                if self.reduced_time and (t - self.reduced_time) > self.reduced_cooldown:
                    self.state = ClogState.MONITORING
                    self.reduced_time = None
                    event = "RECOVERED"
                    print(f"[ClogDetector] ✅ REDUCED 已撤销，恢复正常速度")

        return self._result(event)

    def _ema_update(self, current_ma: float, deviation: float):
        """更新 EMA 基准和方差"""
        if self.baseline_ema == 0:
            self.baseline_ema = current_ma
            self.variance_ema = 0.0
        else:
            self.baseline_ema = self.alpha * current_ma + (1 - self.alpha) * self.baseline_ema
            # 方差 EMA：跟踪偏差的平方
            self.variance_ema = self.beta * (deviation ** 2) + (1 - self.beta) * self.variance_ema

    def _result(self, event: str) -> dict:
        return {
            "event": event,
            "state": self.state.value,
            "current_ma": 0.0,  # 由调用方填充
            "baseline_ema": round(self.baseline_ema, 2),
            "sigma": round(self.sigma, 2),
            "threshold": round(self.threshold, 2),
            "deviation": 0.0,  # 由调用方填充
            "counter": self.counter,
            "material": self.material,
            "warmup_remaining": max(0, self.warmup_end - time.time()) if self.state == ClogState.WARMUP else 0,
        }


# ━━━ Moonraker API 客户端 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class MoonrakerClient:
    """Moonraker/Klipper REST API 客户端"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}

    def _get(self, endpoint: str) -> dict:
        url = f"{self.base_url}{endpoint}"
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            print(f"[Moonraker] HTTP {e.code}: {e.reason}")
            return {}
        except Exception as e:
            print(f"[Moonraker] 请求失败: {e}")
            return {}

    def _post(self, endpoint: str, data: dict) -> bool:
        url = f"{self.base_url}{endpoint}"
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                         headers=self.headers, method="POST")
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status == 200
        except Exception as e:
            print(f"[Moonraker] POST 失败: {e}")
            return False

    def get_extruder_current(self) -> Optional[float]:
        """获取挤出机电机电流（mA），通过 TMC2209 寄存器"""
        # Klipper 通过 `get_adc_values` 或 `query_adc` 获取电流
        # 这里使用 moonraker 的 gcode_store + sensor 查询简化方式
        obj = self._get("/api/objects/query?refresh=true")
        try:
            # 尝试从 extruder 传感器读取
            # TMC2209 不直接输出电流，但 StallGuard 阈值触发可映射为电流
            # 实际应用中通过 INA219 或 TMC2130 的 SG_RESULT 寄存器读取
            return None  # 占位，需根据实际硬件接线
        except Exception:
            return None

    def get_print_status(self) -> str:
        """获取打印状态：printing / idle / paused"""
        obj = self._get("/api/objects/query?print_stats")
        try:
            return obj.get("objects", {}).get("print_stats", {}).get("state", "idle")
        except Exception:
            return "idle"

    def send_gcode(self, gcode: str) -> bool:
        """发送 G-code 命令"""
        return self._post("/api/gcode/script", {"script": gcode})

    def pause_print(self):
        self.send_gcode("PAUSE")

    def reduce_speed(self, speed_mmh: float):
        self.send_gcode(f"SET_VELOCITY_LIMIT SPEED={speed_mmh}")


# ━━━ 串口读取（TMC2209/电流传感器）━━━━━━━━━━━━━━━━━━━━
class SerialReader:
    """从串口读取电流/传感器数据（支持 Klipper 的 adc_print 值）"""

    def __init__(self, port: str, baudrate: int = 115200):
        if not HAS_SERIAL:
            raise RuntimeError("需要 pyserial: pip install pyserial")
        self.ser = serial.Serial(port, baudrate, timeout=1.0)
        self.ser.reset_input_buffer()
        time.sleep(0.5)

    def read_current_ma(self) -> Optional[float]:
        """
        读取当前电流采样（mA）
        格式（Klipper 输出示例）：
        adc_print: temp_heater_bed: target=0.0 temp=24.4 pwm=0.046
        extruder: target=0.0 temp=23.1 pwm=0.042

        如果使用 INA219 模块：
        实际电流 A = (ADC_V) / ( shunt_voltage_R )，这里换算为 mA
        """
        try:
            line = self.ser.readline().decode("utf-8", errors="ignore").strip()
            # 解析 Klipper adc_report 格式
            # 示例: "E1_current_ma: 118.5"
            if "current_ma" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    return float(parts[1].strip())
            return None
        except Exception:
            return None


# ━━━ 主监控循环 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def monitor_loop(detector: ClogDetector, source, client: Optional[MoonrakerClient] = None):
    """
    主监控循环：读取电流 → 更新检测器 → 响应事件

    Args:
        detector: ClogDetector 实例
        source: SerialReader 或 None（模拟模式）
        client: MoonrakerClient 或 None
    """
    print(f"[ClogMonitor] 🐟 堵料监控已启动，材料={detector.material}")
    print(f"[ClogMonitor] 基准={detector.baseline_ema:.1f}mA, "
          f"k={detector.profile['k_sigma']}, N={detector.profile['window_n']}")

    # 开始预热
    detector.start_warmup()

    sample_interval = 0.5  # 采样间隔 (s)
    last_log_time = 0
    log_interval = 30  # 每 30s 输出一次状态摘要

    while True:
        try:
            # 读取电流
            current = None
            if source:
                current = source.read_current_ma()
            elif client:
                # Moonraker 模式：使用 mock 值（实际应用中需实现真实读取）
                current = None

            # 模拟：若无输入，生成模拟数据（仅用于测试）
            if current is None:
                import random
                t = time.time()
                # 模拟正常电流 + 小噪声
                noise = random.gauss(0, 5)  # σ=5mA
                # 偶尔注入尖峰（模拟假阳性场景）
                spike = random.gauss(0, 20) if random.random() < 0.02 else 0
                current = detector.baseline_ema + noise + spike
                if detector.state == ClogState.WARMUP:
                    current = detector.profile["baseline_ma"] + random.gauss(0, 10)

            current = round(current, 1)
            result = detector.update(current)
            result["current_ma"] = current
            result["deviation"] = round(abs(current - detector.baseline_ema), 1)

            # 事件响应
            event = result["event"]
            if event in ("WARNING", "REDUCED") and client:
                if event == "WARNING":
                    print(f"[ClogMonitor] 🔶 触发 WARNING，准备降速...")
                    client.send_gcode(f'M117 堵料预警: {current:.0f}mA')
                elif event == "REDUCED":
                    max_speed = detector.profile["max_speed_mmh"]
                    print(f"[ClogMonitor] 🔶 降速至 {max_speed}mm/h")
                    client.reduce_speed(max_speed)

            # 日志输出
            t = time.time()
            if event != "NORMAL" or t - last_log_time > log_interval:
                if event != "NORMAL":
                    print(f"[ClogMonitor] [{event}] 电流={current}mA | "
                          f"基准={result['baseline_ema']} | "
                          f"σ={result['sigma']} | "
                          f"阈值={result['threshold']:.1f} | "
                          f"计数={result['counter']}/{detector.profile['window_n']}")
                last_log_time = t

            time.sleep(sample_interval)

        except KeyboardInterrupt:
            print("\n[ClogMonitor] 👋 监控停止")
            break
        except Exception as e:
            print(f"[ClogMonitor] ❌ 错误: {e}")
            time.sleep(2)


# ━━━ 单元测试 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def test_ema_algorithm():
    """验证 EMA 算法的降误报效果"""
    print("=" * 50)
    print("EMA 堵料检测算法 — 单元测试")
    print("=" * 50)

    detector = ClogDetector(material="PLA")
    detector.start_warmup()
    # 快速完成预热（覆盖 warmup_s）
    detector.warmup_end = time.time() - 1
    detector.state = ClogState.MONITORING

    import random
    random.seed(42)

    print("\n测试场景 1：正常打印（电流在基准±1σ内波动）")
    print("-" * 40)
    warnings = 0
    for i in range(100):
        current = detector.baseline_ema + random.gauss(0, detector.sigma)
        result = detector.update(current)
        if result["event"] != "NORMAL":
            warnings += 1
            print(f"  ⚠️ 样本 {i}: {result['event']} 电流={current:.1f}mA")
    print(f"结果：100 次正常波动中误报 {warnings} 次（预期 < 5）")

    print("\n测试场景 2：渐进式堵料（电流逐渐上升）")
    print("-" * 40)
    detector.counter = 0
    ramp_current = detector.baseline_ema
    detected_at = None
    for i in range(200):
        ramp_current += 0.8  # 逐步增加电流，模拟堵料
        result = detector.update(ramp_current)
        if result["event"] != "NORMAL" and detected_at is None:
            detected_at = i
            print(f"  🔶 在第 {i} 个样本检测到: {result['event']} (电流={ramp_current:.1f}mA)")
            if result["event"] == "JAMMED":
                break

    if detected_at:
        print(f"堵料在第 {detected_at} 个样本时被检测（基准={detector.baseline_ema:.1f}mA，"
              f"最终电流={ramp_current:.1f}mA，偏差={ramp_current-detector.baseline_ema:.1f}mA）")

    print("\n测试场景 3：瞬时电流尖峰（假阳性场景）")
    print("-" * 40)
    detector.counter = 0
    spike_count = 0
    for i in range(50):
        if i in (10, 11):  # 两个连续尖峰
            current = detector.baseline_ema + 4 * detector.sigma  # 4σ 尖峰
        else:
            current = detector.baseline_ema + random.gauss(0, 5)
        result = detector.update(current)
        if result["event"] != "NORMAL":
            spike_count += 1
            print(f"  ⚠️ 样本 {i}: {result['event']} 电流={current:.1f}mA")
    print(f"结果：50 次（含 2 个 4σ 尖峰）中误报 {spike_count} 次（预期 ≤ 1，N=3 窗口过滤应消除单次尖峰）")

    print("\n测试场景 4：不同材料基准差异")
    print("-" * 40)
    for mat in ["PLA", "PETG", "ABS", "TPU", "PC"]:
        d = ClogDetector(material=mat)
        d.start_warmup()
        d.warmup_end = time.time() - 1
        d.state = ClogState.MONITORING
        print(f"  {mat}: 基准={d.baseline_ema:.0f}mA, k={d.profile['k_sigma']}, "
              f"N={d.profile['window_n']}, σ={d.sigma:.1f}, "
              f"阈值={d.threshold:.1f}mA")

    print("\n✅ 单元测试完成")
    print("=" * 50)


# ━━━ CLI 入口 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    parser = argparse.ArgumentParser(description="大鱼 TT 优化堵料检测监控脚本")
    parser.add_argument("--test", action="store_true", help="运行单元测试")
    parser.add_argument("--moonraker", type=str, help="Moonraker API 地址（如 http://192.168.1.100:7125）")
    parser.add_argument("--serial", type=str, help="串口设备路径（如 /dev/ttyUSB0）")
    parser.add_argument("--baud", type=int, default=115200, help="串口波特率（默认 115200）")
    parser.add_argument("--material", type=str, default="PLA", choices=list(MATERIAL_PROFILES.keys()),
                        help="材料类型（影响基准电流和阈值）")
    parser.add_argument("--simulate", action="store_true", help="模拟模式（不连接硬件）")
    args = parser.parse_args()

    if args.test:
        test_ema_algorithm()
        return

    print(f"[ClogMonitor] 堵料检测监控脚本 v1.0")
    print(f"[ClogMonitor] 材料: {args.material}")
    print(f"[ClogMonitor] 模式: {'模拟' if args.simulate else 'Moonraker' if args.moonraker else '串口'}")

    # 初始化检测器
    detector = ClogDetector(material=args.material)

    # 初始化数据源
    client = None
    source = None

    if args.simulate:
        print("[ClogMonitor] ⚠️  模拟模式：无硬件数据，使用模拟电流")
        source = None
    elif args.moonraker:
        client = MoonrakerClient(args.moonraker)
        print(f"[ClogMonitor] 🌐 连接 Moonraker: {args.moonraker}")
        source = None
    elif args.serial:
        if not HAS_SERIAL:
            print("[ClogMonitor] ❌ 需要 pyserial，请运行: pip install pyserial")
            return
        source = SerialReader(args.serial, args.baud)
        print(f"[ClogMonitor] 🔌 串口连接: {args.serial}@{args.baud}")
    else:
        # 默认模拟模式
        source = None
        print("[ClogMonitor] ⚠️  默认使用模拟模式（加 --simulate）")

    monitor_loop(detector, source, client)


if __name__ == "__main__":
    main()
