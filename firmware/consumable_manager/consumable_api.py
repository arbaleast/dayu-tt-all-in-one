#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 耗材管理与预警系统 — Flask API 服务
# 文件路径: firmware/consumable_manager/consumable_api.py
# 对应子任务: 9bcbda5a-cc0a-44ce-b6ed-c6f87cc2ad85
# 依据: 耗材管理方案调研报告
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 【功能模块】
# 1. 耗材 CRUD — 录入/查询/更新/删除耗材卷信息
# 2. 重量记录 — 称重传感器数据采集，实时更新库存
# 3. 预警提醒 — 低于阈值（默认 20%）自动飞书提醒
# 4. 用量统计 — 每次打印后记录消耗，预测耗尽日期
#
# 【数据库】
# SQLite（轻量，单机部署，无需配置）
# 数据库路径: data/consumables.db
#
# 【API 端口】
# http://<host>:5011

import argparse
import json
import math
import os
import sqlite3
import threading
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ━━━ 数据模型 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 材料密度表（g/cm³），1.75mm 线径每米重量
MATERIAL_DENSITY = {
    "PLA":  1.24,
    "ABS":  1.04,
    "PETG": 1.27,
    "TPU":  1.21,
    "PC":   1.20,
    "PA":   1.14,   # Nylon
    "ASA":  1.07,
    "PP":   0.90,
    "PE":   0.95,
    "DEFAULT": 1.24,
}

def weight_per_meter(material: str, diameter_mm: float = 1.75) -> float:
    """计算给定材料和直径的线材每米重量（g）"""
    density = MATERIAL_DENSITY.get(material.upper(), MATERIAL_DENSITY["DEFAULT"])
    r = diameter_mm / 2 / 10  # mm → cm
    cross_section = math.pi * r ** 2  # cm²
    return cross_section * density  # g/m


@dataclass
class Consumable:
    """耗材卷数据模型"""
    id: Optional[int] = None
    name: str = ""
    material: str = "PLA"
    brand: str = ""
    color_name: str = ""
    color_hex: str = "#000000"
    diameter: float = 1.75          # 线径 mm
    weight_net: float = 1000.0       # 净重 g
    weight_spool: float = 220.0     # 卷轴重量 g
    current_weight: Optional[float] = None  # 当前重量 g（传感器读数）
    remaining_g: Optional[float] = None     # 剩余净重 g
    remaining_pct: Optional[float] = None   # 剩余百分比
    purchase_date: str = ""
    expiry_date: Optional[str] = None
    cost: float = 0.0
    supplier: str = ""
    notes: str = ""
    is_active: bool = True           # 当前是否在用
    low_threshold_pct: float = 20.0  # 低库存预警阈值（%）

    # 计算属性（自动更新）
    def update_remaining(self, raw_weight: float) -> None:
        """根据传感器读数更新剩余量"""
        self.current_weight = raw_weight
        net = raw_weight - self.weight_spool
        self.remaining_g = max(net, 0.0)
        self.remaining_pct = round(self.remaining_g / self.weight_net * 100, 1)

    @property
    def is_low(self) -> bool:
        return self.remaining_pct is not None and self.remaining_pct < self.low_threshold_pct

    @property
    def is_empty(self) -> bool:
        return self.remaining_pct is not None and self.remaining_pct < 5.0

    def to_dict(self) -> dict:
        d = asdict(self)
        d["is_low"] = self.is_low
        d["is_empty"] = self.is_empty
        return d


@dataclass
class PrintJob:
    """打印任务记录（用于用量统计）"""
    id: Optional[int] = None
    consumable_id: int = 0
    model_name: str = ""
    material: str = "PLA"
    filament_used_g: float = 0.0
    start_time: str = ""
    end_time: Optional[str] = None
    success: bool = True
    notes: str = ""


# ━━━ 数据库层 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Database:
    DB_PATH = Path(__file__).parent / "data" / "consumables.db"

    def __init__(self):
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consumables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    material TEXT DEFAULT 'PLA',
                    brand TEXT DEFAULT '',
                    color_name TEXT DEFAULT '',
                    color_hex TEXT DEFAULT '#000000',
                    diameter REAL DEFAULT 1.75,
                    weight_net REAL DEFAULT 1000.0,
                    weight_spool REAL DEFAULT 220.0,
                    current_weight REAL,
                    remaining_g REAL,
                    remaining_pct REAL,
                    purchase_date TEXT DEFAULT '',
                    expiry_date TEXT,
                    cost REAL DEFAULT 0.0,
                    supplier TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    is_active INTEGER DEFAULT 1,
                    low_threshold_pct REAL DEFAULT 20.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS print_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consumable_id INTEGER REFERENCES consumables(id),
                    model_name TEXT DEFAULT '',
                    material TEXT DEFAULT 'PLA',
                    filament_used_g REAL DEFAULT 0.0,
                    start_time TEXT DEFAULT '',
                    end_time TEXT,
                    success INTEGER DEFAULT 1,
                    notes TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consumable_id INTEGER REFERENCES consumables(id),
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    remaining_pct REAL,
                    is_acknowledged INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_consumable_active
                ON consumables(is_active)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_printjob_consumable
                ON print_jobs(consumable_id)
            """)

    # ━━━ 耗材 CRUD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def add_consumable(self, c: Consumable) -> int:
        with sqlite3.connect(self.DB_PATH) as conn:
            cur = conn.execute("""
                INSERT INTO consumables
                (name, material, brand, color_name, color_hex, diameter,
                 weight_net, weight_spool, current_weight, remaining_g, remaining_pct,
                 purchase_date, expiry_date, cost, supplier, notes, is_active, low_threshold_pct)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c.name, c.material, c.brand, c.color_name, c.color_hex,
                c.diameter, c.weight_net, c.weight_spool, c.current_weight,
                c.remaining_g, c.remaining_pct, c.purchase_date, c.expiry_date,
                c.cost, c.supplier, c.notes, int(c.is_active), c.low_threshold_pct
            ))
            return cur.lastrowid

    def get_consumable(self, id: int) -> Optional[Consumable]:
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM consumables WHERE id = ?", (id,)
            ).fetchone()
            if row:
                return Consumable(**dict(row))
            return None

    def list_consumables(self, active_only: bool = True) -> list[Consumable]:
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM consumables"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY remaining_pct ASC, name"
            rows = conn.execute(query).fetchall()
            return [Consumable(**dict(r)) for r in rows]

    def update_consumable(self, c: Consumable) -> bool:
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("""
                UPDATE consumables SET
                    name = ?, material = ?, brand = ?, color_name = ?,
                    color_hex = ?, diameter = ?, weight_net = ?, weight_spool = ?,
                    current_weight = ?, remaining_g = ?, remaining_pct = ?,
                    purchase_date = ?, expiry_date = ?, cost = ?, supplier = ?,
                    notes = ?, is_active = ?, low_threshold_pct = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                c.name, c.material, c.brand, c.color_name, c.color_hex,
                c.diameter, c.weight_net, c.weight_spool, c.current_weight,
                c.remaining_g, c.remaining_pct, c.purchase_date, c.expiry_date,
                c.cost, c.supplier, c.notes, int(c.is_active), c.low_threshold_pct, c.id
            ))
            return conn.total_changes > 0

    def update_weight(self, id: int, raw_weight: float) -> Optional[Consumable]:
        """更新指定耗材的称重读数"""
        c = self.get_consumable(id)
        if not c:
            return None
        c.update_remaining(raw_weight)
        self.update_consumable(c)
        return c

    def delete_consumable(self, id: int) -> bool:
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("DELETE FROM consumables WHERE id = ?", (id,))
            return conn.total_changes > 0

    # ━━━ 用量统计 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def add_print_job(self, job: PrintJob) -> int:
        with sqlite3.connect(self.DB_PATH) as conn:
            cur = conn.execute("""
                INSERT INTO print_jobs
                (consumable_id, model_name, material, filament_used_g,
                 start_time, end_time, success, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.consumable_id, job.model_name, job.material,
                job.filament_used_g, job.start_time, job.end_time,
                int(job.success), job.notes
            ))
            # 同步更新耗材剩余量
            c = self.get_consumable(job.consumable_id)
            if c and c.remaining_g is not None:
                c.remaining_g = max(c.remaining_g - job.filament_used_g, 0)
                c.remaining_pct = round(c.remaining_g / c.weight_net * 100, 1)
                self.update_consumable(c)
            return cur.lastrowid

    def get_usage_stats(self, consumable_id: int, days: int = 30) -> dict:
        """获取指定耗材的用量统计"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM print_jobs
                WHERE consumable_id = ? AND start_time >= ? AND success = 1
                ORDER BY start_time DESC
            """, (consumable_id, cutoff)).fetchall()

        if not rows:
            return {"days": days, "total_g": 0, "jobs": 0, "daily_avg_g": 0, "estimated_days_left": None}

        total_g = sum(r["filament_used_g"] for r in rows)
        jobs = len(rows)
        daily_avg = total_g / days if days > 0 else 0

        c = self.get_consumable(consumable_id)
        days_left = None
        if c and c.remaining_g is not None and daily_avg > 0:
            days_left = round(c.remaining_g / daily_avg, 1)

        return {
            "days": days,
            "total_g": round(total_g, 1),
            "jobs": jobs,
            "daily_avg_g": round(daily_avg, 2),
            "estimated_days_left": days_left,
        }

    def get_low_stock_alerts(self) -> list[Consumable]:
        """获取所有低库存耗材"""
        all_c = self.list_consumables(active_only=True)
        return [c for c in all_c if c.is_low]

    def add_alert(self, consumable_id: int, alert_type: str, message: str, remaining_pct: float):
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("""
                INSERT INTO alerts (consumable_id, alert_type, message, remaining_pct)
                VALUES (?, ?, ?, ?)
            """, (consumable_id, alert_type, message, remaining_pct))


# ━━━ Flask API ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def create_app(db: Database, alert_callback=None):
    """
    创建 Flask 应用
    alert_callback: 当触发预警时的回调函数（用于发送飞书通知）
    """
    from flask import Flask, jsonify, request
    import threading

    app = Flask(__name__)

    def _require_json():
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400

    def _check_alerts(c: Consumable):
        """检测并触发预警"""
        if c.is_low:
            msg = (f"⚠️ 低库存预警 [{c.name}]\n"
                   f"材料: {c.material} ({c.brand})\n"
                   f"颜色: {c.color_name}\n"
                   f"剩余: {c.remaining_pct:.1f}% ({c.remaining_g:.0f}g)\n"
                   f"阈值: {c.low_threshold_pct}%\n"
                   f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            db.add_alert(c.id, "LOW_STOCK", msg, c.remaining_pct or 0)
            if alert_callback:
                threading.Thread(target=alert_callback, args=(c, msg), daemon=True).start()

    # ━━ 耗材 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    @app.route("/api/consumables", methods=["GET"])
    def list_consumables():
        items = db.list_consumables(active_only=True)
        return jsonify({"items": [c.to_dict() for c in items], "total": len(items)})

    @app.route("/api/consumables", methods=["POST"])
    def create_consumable():
        _require_json()
        d = request.json
        try:
            c = Consumable(
                name=d.get("name", "未命名耗材"),
                material=d.get("material", "PLA"),
                brand=d.get("brand", ""),
                color_name=d.get("color_name", ""),
                color_hex=d.get("color_hex", "#000000"),
                diameter=float(d.get("diameter", 1.75)),
                weight_net=float(d.get("weight_net", 1000.0)),
                weight_spool=float(d.get("weight_spool", 220.0)),
                current_weight=float(d["current_weight"]) if "current_weight" in d else None,
                purchase_date=d.get("purchase_date", ""),
                expiry_date=d.get("expiry_date"),
                cost=float(d.get("cost", 0.0)),
                supplier=d.get("supplier", ""),
                notes=d.get("notes", ""),
                low_threshold_pct=float(d.get("low_threshold_pct", 20.0)),
            )
            if c.current_weight:
                c.update_remaining(c.current_weight)
            elif c.weight_net:
                c.remaining_g = c.weight_net
                c.remaining_pct = 100.0
            c.id = db.add_consumable(c)
            _check_alerts(c)
            return jsonify(c.to_dict()), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/consumables/<int:id>", methods=["GET"])
    def get_consumable(id: int):
        c = db.get_consumable(id)
        if not c:
            return jsonify({"error": "Not found"}), 404
        return jsonify(c.to_dict())

    @app.route("/api/consumables/<int:id>", methods=["PUT"])
    def update_consumable(id: int):
        _require_json()
        d = request.json
        c = db.get_consumable(id)
        if not c:
            return jsonify({"error": "Not found"}), 404
        for k, v in d.items():
            if hasattr(c, k):
                setattr(c, k, v)
        db.update_consumable(c)
        _check_alerts(c)
        return jsonify(c.to_dict())

    @app.route("/api/consumables/<int:id>", methods=["DELETE"])
    def delete_consumable(id: int):
        ok = db.delete_consumable(id)
        return jsonify({"ok": ok})

    @app.route("/api/consumables/<int:id>/weight", methods=["POST"])
    def update_weight(id: int):
        """
        接收称重传感器读数，更新库存
        Body: {"raw_weight": 1050.0}  # 带卷轴的总重量
        """
        _require_json()
        raw = request.json.get("raw_weight")
        if raw is None:
            return jsonify({"error": "raw_weight required"}), 400
        c = db.update_weight(id, float(raw))
        if not c:
            return jsonify({"error": "Not found"}), 404
        _check_alerts(c)
        return jsonify(c.to_dict())

    # ━━ 用量记录 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    @app.route("/api/consumables/<int:id>/usage", methods=["GET"])
    def get_usage(id: int):
        days = int(request.args.get("days", 30))
        return jsonify(db.get_usage_stats(id, days))

    @app.route("/api/print_jobs", methods=["POST"])
    def create_print_job():
        _require_json()
        d = request.json
        job = PrintJob(
            consumable_id=int(d["consumable_id"]),
            model_name=d.get("model_name", ""),
            material=d.get("material", "PLA"),
            filament_used_g=float(d.get("filament_used_g", 0)),
            start_time=d.get("start_time", datetime.now().isoformat()),
            end_time=d.get("end_time"),
            success=d.get("success", True),
            notes=d.get("notes", ""),
        )
        job.id = db.add_print_job(job)
        # 触发预警检测（打印后可能已低于阈值）
        c = db.get_consumable(job.consumable_id)
        if c:
            _check_alerts(c)
        return jsonify({"id": job.id, "ok": True})

    # ━━ 预警 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    @app.route("/api/alerts", methods=["GET"])
    def get_alerts():
        with sqlite3.connect(db.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT a.*, c.name as consumable_name, c.material, c.color_name
                FROM alerts a
                LEFT JOIN consumables c ON a.consumable_id = c.id
                WHERE a.is_acknowledged = 0
                ORDER BY a.created_at DESC
                LIMIT 20
            """).fetchall()
        return jsonify({"items": [dict(r) for r in rows]})

    @app.route("/api/alerts/<int:id>/ack", methods=["POST"])
    def ack_alert(id: int):
        with sqlite3.connect(db.DB_PATH) as conn:
            conn.execute("UPDATE alerts SET is_acknowledged = 1 WHERE id = ?", (id,))
        return jsonify({"ok": True})

    # ━━ 摘要 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    @app.route("/api/summary", methods=["GET"])
    def summary():
        items = db.list_consumables()
        low = [c for c in items if c.is_low]
        empty = [c for c in items if c.is_empty]
        return jsonify({
            "total": len(items),
            "low_stock": len(low),
            "empty": len(empty),
            "low_stock_items": [c.to_dict() for c in low],
            "warnings": [c.to_dict() for c in empty] if empty else [],
        })

    # ━━ 健康检查 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "db": str(db.DB_PATH)})

    return app


# ━━━ CLI 入口 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    parser = argparse.ArgumentParser(description="大鱼 TT 耗材管理 API 服务")
    parser.add_argument("--port", type=int, default=5011, help="API 端口（默认 5011）")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="监听地址")
    parser.add_argument("--data-dir", type=str, help="数据库目录（可选）")
    args = parser.parse_args()

    db = Database()
    print(f"[ConsumableAPI] 📦 耗材管理 API 启动，端口 {args.port}")
    print(f"[ConsumableAPI] 数据库: {db.DB_PATH}")
    print(f"[ConsumableAPI] 示例: curl -X POST http://localhost:{args.port}/api/consumables "
          f"-H 'Content-Type: application/json' -d '{{\"name\":\"PLA白\",\"material\":\"PLA\","
          f"\"weight_net\":1000,\"current_weight\":1200}}'")

    def alert_callback(c: Consumable, msg: str):
        """飞书通知回调（待接入）"""
        print(f"[ALERT] 🔔 {msg}")

    app = create_app(db, alert_callback)
    app.run(host=args.host, port=args.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
