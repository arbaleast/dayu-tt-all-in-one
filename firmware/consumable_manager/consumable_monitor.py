#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 耗材称重监控脚本 — HX711 传感器读取
# 文件路径: firmware/consumable_manager/consumable_monitor.py
# 对应子任务: 9bcbda5a-cc0a-44ce-b6ed-c6f87cc2ad85
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 【功能】
# 1. 从 HX711 称重传感器读取当前耗材重量
# 2. 通过 Moonraker API 实时更新 Klipper 显示变量
# 3. 通过 REST API 向 consumable_api.py 推送读数，触发预警判断
#
# 【硬件接线（HX711 → ESP32/树莓派）】
#   HX711 VCC  → 3.3V 或 5V
#   HX711 GND  → GND
#   HX711 DT   → ESP32 GPIO (如 D5 / GPIO14)
#   HX711 SCK  → ESP32 GPIO (如 D6 / GPIO12)
#   Load Cell Wires → HX711 E+/E- (激励电压) 和 A+/A- (测量)
#
# 【使用方式】
# python3 consumable_monitor.py --api http://localhost:5011 --consumable-id 1
# python3 consumable_monitor.py --moonraker http://192.168.1.100:7125 --display
# python3 consumable_monitor.py --simulate  # 测试模式

import argparse
import json
import math
import statistics
import time
import urllib.request
import urllib.error
from collections import deque

# ━━━ 依赖检测 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HAS_HX711 = False
try:
    from hx711 import HX711
    HAS_HX711 = True
except ImportError:
    pass

# ━━━ 材料密度表 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MATERIAL_DENSITY = {
    "PLA": 1.24, "ABS": 1.04, "PETG": 1.27, "TPU": 1.21,
    "PC": 1.20, "PA": 1.14, "ASA": 1.07, "DEFAULT": 1.24,
}

# ━━━ 卡尔曼滤波 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class KalmanFilter:
    """
    一维卡尔曼滤波器 — 消除称重传感器震动干扰
    """
    def __init__(self, process_noise: float = 0.1, measurement_noise: float = 1.0):
        self.estimate = 0.0
        self.error_covariance = 1.0
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise

    def update(self, measurement: float) -> float:
        # 预测
        self.error_covariance += self.process_noise
        # 更新
        kalman_gain = self.error_covariance / (self.error_covariance + self.measurement_noise)
        self.estimate += kalman_gain * (measurement - self.estimate)
        self.error_covariance *= (1 - kalman_gain)
        return self.estimate

    def reset(self, initial_estimate: float):
        self.estimate = initial_estimate
        self.error_covariance = 1.0


# ━━━ HX711 读取器 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class HX711Reader:
    def __init__(self, dto_pin: int, sck_pin: int, reference_unit: float = 1.0):
        if not HAS_HX711:
            raise RuntimeError("需要 RPi.GPIO + HX711 库: pip install hx711")
        self.hx = HX711(dout_pin=dto_pin, pd_sck_pin=sck_pin)
        self.hx.set_reference_unit(reference_unit)
        self.hx.reset()
        self.kalman = KalmanFilter(process_noise=0.1, measurement_noise=0.5)
        print(f"[HX711] 初始化完成，参考单位={reference_unit}")

    def read_raw(self, samples: int = 5) -> float:
        """读取原始值（多次采样取中位数）"""
        vals = []
        for _ in range(samples):
            try:
                v = self.hx.get_weight()  # 返回带正负的浮点数
                vals.append(v)
            except Exception:
                pass
            time.sleep(0.05)
        if not vals:
            return 0.0
        return statistics.median(vals)

    def read_filtered(self) -> float:
        """读取滤波后的值（卡尔曼滤波）"""
        raw = self.read_raw()
        return round(self.kalman.update(raw), 1)

    def tare(self, samples: int = 20):
        """归零（去除当前重量）"""
        self.hx.reset()
        time.sleep(0.2)
        vals = [self.read_raw() for _ in range(samples)]
        median = statistics.median(vals)
        self.kalman.reset(0.0)
        print(f"[HX711] 归零完成，偏置值={median:.1f}")
        return median


# ━━━ Moonraker 客户端（更新 Klipper 显示变量）━━━━━━━━
class MoonrakerDisplay:
    """将耗材剩余百分比写入 Klipper display_status 变量"""

    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")

    def _post(self, endpoint: str, data: dict) -> bool:
        url = f"{self.base}{endpoint}"
        try:
            req = urllib.request.Request(
                url, data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status == 200
        except Exception as e:
            print(f"[Moonraker] 请求失败: {e}")
            return False

    def update_filament_display(self, remaining_pct: float, remaining_g: float, material: str = ""):
        """
        通过 Klipper 的 display_status gcode 变量更新屏幕显示
        等效 G-code: SET_GCODE_VARIABLE VARIABLE=filament_remaining VALUE={remaining_pct}
        """
        msg = f"FILL:{remaining_pct:.0f}%|{remaining_g:.0f}g"
        if material:
            msg = f"[{material}] {msg}"
        # 方式 1：通过 gcode script
        self._post("/api/gcode/script", {"script": f"M117 {msg}"})
        # 方式 2：通过 moonraker objects 更新自定义变量
        # （需要在 printer.cfg 中定义 [gcode_variables] filament_remaining = 100）


# ━━━ 主监控循环 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def monitor_loop(
    reader: "HX711Reader | None",
    api_url: str,
    consumable_id: int,
    spool_weight: float,
    net_weight: float,
    material: str,
    display: "MoonrakerDisplay | None",
    interval: float = 2.0,
):
    """
    主监控循环

    Args:
        reader: HX711Reader 或 None（模拟模式）
        api_url: consumable_api.py 的地址
        consumable_id: 耗材在数据库中的 ID
        spool_weight: 卷轴重量（g）
        net_weight: 耗材净重（g），用于计算百分比
        material: 材料类型（显示用）
        display: MoonrakerDisplay 或 None
        interval: 读取间隔（秒）
    """
    kalman = KalmanFilter()
    print(f"[Monitor] 🐟 耗材监控已启动，ID={consumable_id}, "
          f"净重={net_weight}g, 卷轴={spool_weight}g")

    last_tare = time.time()
    tare_interval = 300  # 每 5 分钟自动归零（消除漂移）

    while True:
        try:
            # 读取重量
            if reader:
                raw = reader.read_filtered()
            else:
                # 模拟模式
                import random
                # 模拟耗材缓慢减少（每次减少 0.1-0.3g）
                raw = spool_weight + net_weight - (time.time() % 3600) * 0.05
                raw = round(raw + random.gauss(0, 2), 1)
                raw = max(raw, spool_weight)

            # 卡尔曼滤波（额外一层）
            filtered = kalman.update(raw)

            # 计算剩余
            net_current = filtered - spool_weight
            remaining_g = max(net_current, 0.0)
            remaining_pct = round(remaining_g / net_weight * 100, 1) if net_weight > 0 else 0

            # 更新 Klipper 显示
            if display:
                display.update_filament_display(remaining_pct, remaining_g, material)

            # 推送到 API
            if api_url:
                url = f"{api_url}/api/consumables/{consumable_id}/weight"
                payload = json.dumps({"raw_weight": filtered}).encode()
                try:
                    req = urllib.request.Request(
                        url, data=payload,
                        headers={"Content-Type": "application/json"},
                        method="POST"
                    )
                    with urllib.request.urlopen(req, timeout=5) as r:
                        resp = json.loads(r.read())
                        if resp.get("is_low"):
                            print(f"[Monitor] 🔔 低库存预警！剩余 {remaining_pct}%")
                        elif resp.get("is_empty"):
                            print(f"[Monitor] 🔴 耗材耗尽！")
                except Exception as e:
                    print(f"[Monitor] ⚠️ API 推送失败: {e}")

            # 日志（每 30s）
            if int(time.time()) % 30 < interval:
                print(f"[Monitor] 耗材剩余: {remaining_pct}% ({remaining_g:.1f}g) | "
                      f"原始读数: {raw:.1f}g | 滤波后: {filtered:.1f}g")

            # 自动归零（防止 HX711 零点漂移）
            if time.time() - last_tare > tare_interval and reader:
                reader.tare()
                last_tare = time.time()

            time.sleep(interval)

        except KeyboardInterrupt:
            print("\n[Monitor] 👋 监控停止")
            break
        except Exception as e:
            print(f"[Monitor] ❌ 错误: {e}")
            time.sleep(2)


# ━━━ CLI 入口 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    parser = argparse.ArgumentParser(description="大鱼 TT 耗材称重监控")
    parser.add_argument("--api", type=str, default="http://localhost:5011",
                        help="consumable_api.py 地址")
    parser.add_argument("--id", type=int, default=1, dest="consumable_id",
                        help="耗材数据库 ID")
    parser.add_argument("--spool", type=float, default=220.0,
                        dest="spool_weight", help="卷轴重量（g）")
    parser.add_argument("--net", type=float, default=1000.0,
                        dest="net_weight", help="耗材净重（g）")
    parser.add_argument("--material", type=str, default="PLA",
                        help="材料类型")
    parser.add_argument("--moonraker", type=str, help="Moonraker 地址（用于更新屏幕显示）")
    parser.add_argument("--simulate", action="store_true", help="模拟模式（无硬件）")
    parser.add_argument("--interval", type=float, default=2.0, help="读取间隔（秒）")
    # HX711 引脚（需 RPi）
    parser.add_argument("--dout", type=int, default=5, help="HX711 DOUT 引脚（GPIO编号）")
    parser.add_argument("--sck", type=int, default=6, help="HX711 SCK 引脚（GPIO编号）")
    parser.add_argument("--ref-unit", type=float, default=1.0, dest="ref_unit",
                        help="HX711 参考单位（校准后值）")
    args = parser.parse_args()

    print(f"[Monitor] 耗材称重监控 v1.0")
    print(f"[Monitor] 材料: {args.material}, 净重: {args.net_weight}g, "
          f"卷轴: {args.spool_weight}g")
    print(f"[Monitor] 模式: {'模拟' if args.simulate else 'HX711' if not args.simulate and HAS_HX711 else 'Moonraker'}")

    reader = None
    if not args.simulate:
        if HAS_HX711:
            try:
                reader = HX711Reader(dto_pin=args.dout, sck_pin=args.sck,
                                     reference_unit=args.ref_unit)
                reader.tare()
            except Exception as e:
                print(f"[Monitor] ⚠️ HX711 初始化失败: {e}，切换到模拟模式")
                reader = None
        else:
            print(f"[Monitor] ⚠️ 未安装 hx711 库，切换到模拟模式")
            print(f"[Monitor]   安装: pip install hx711")

    display = None
    if args.moonraker:
        display = MoonrakerDisplay(args.moonraker)

    monitor_loop(
        reader=reader,
        api_url=args.api,
        consumable_id=args.consumable_id,
        spool_weight=args.spool_weight,
        net_weight=args.net_weight,
        material=args.material,
        display=display,
        interval=args.interval,
    )


if __name__ == "__main__":
    main()
