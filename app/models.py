from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


# ── 常量 ──────────────────────────────────────────────────

VALID_ROLES = ('admin', 'sales', 'designer', 'warehouse',
               'external_modeler', 'craftsman', 'finance')


# ══════════════════════════════════════════════════════════
# 1. StockUser  库存系统用户（权限表）
# ══════════════════════════════════════════════════════════

class StockUser(UserMixin, db.Model):
    """库存系统权限表 — 用户名对应大系统用户，role='admin' 可看成本"""
    __tablename__ = 'stock_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(30), nullable=False, default='staff')  # admin / staff
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def role_display(self):
        _map = {'admin': '管理员', 'staff': '店员'}
        return _map.get(self.role, self.role)

    def __repr__(self):
        return f'<StockUser {self.username} role={self.role}>'


# ══════════════════════════════════════════════════════════
# 2. Supplier  供应商
# ══════════════════════════════════════════════════════════

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(40), nullable=False, default='stone')  # gold/stone/accessory/outsource/other
    contact_name = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(40), nullable=True)
    wechat = db.Column(db.String(80), nullable=True)
    address = db.Column(db.String(300), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # 关系
    raw_materials = db.relationship('RawMaterial', back_populates='supplier', lazy='dynamic')

    @property
    def type_display(self):
        _map = {
            'gold': '金料供应商', 'stone': '石料供应商',
            'accessory': '配件供应商', 'outsource': '外包合作',
            'other': '其他',
        }
        return _map.get(self.type, self.type)

    def __repr__(self):
        return f'<Supplier {self.name}>'


# ══════════════════════════════════════════════════════════
# 3. RawMaterial  原材料
# ══════════════════════════════════════════════════════════

class RawMaterial(db.Model):
    __tablename__ = 'raw_materials'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(60), unique=True, nullable=True)  # 物料编号
    category = db.Column(db.String(30), nullable=False, default='stone')  # gold/silver/platinum/diamond/gemstone/accessory
    name = db.Column(db.String(200), nullable=False)
    spec = db.Column(db.String(200), nullable=True)  # 规格描述

    # 重量相关
    weight = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(10), nullable=True, default='ct')  # g / ct / 颗

    # 石料专用字段
    shape = db.Column(db.String(60), nullable=True)
    color = db.Column(db.String(60), nullable=True)
    clarity = db.Column(db.String(60), nullable=True)
    cert_number = db.Column(db.String(120), nullable=True)
    cert_org = db.Column(db.String(80), nullable=True)

    # 金料专用字段
    purity = db.Column(db.String(20), nullable=True)  # 999 / 916 / 750 等

    # 成本（管理员可见）
    cost_price = db.Column(db.Float, nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)

    # 关联
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(30), nullable=False, default='in_stock')  # in_stock/locked/out/returned
    lot_number = db.Column(db.String(60), nullable=True)  # 采购批次号

    # 图片
    photos = db.Column(db.Text, nullable=True)  # JSON 数组存文件名

    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(80), nullable=True)  # 录入人 username
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # 关系
    supplier = db.relationship('Supplier', back_populates='raw_materials')

    @property
    def category_display(self):
        _map = {
            'gold': '金料', 'silver': '银料', 'platinum': '铂金',
            'diamond': '钻石', 'gemstone': '彩色宝石',
            'pearl': '珍珠', 'jade': '翡翠/玉石',
            'accessory': '配件', 'other': '其他',
        }
        return _map.get(self.category, self.category)

    @property
    def status_display(self):
        _map = {
            'in_stock': '在库', 'locked': '已锁定',
            'out': '已出库', 'returned': '已退货',
        }
        return _map.get(self.status, self.status)

    @property
    def weight_display(self):
        if self.weight is None:
            return '—'
        unit_label = self.unit or 'ct'
        return f'{self.weight} {unit_label}'

    @property
    def first_photo(self):
        if self.photos:
            import json
            try:
                arr = json.loads(self.photos)
                return arr[0] if arr else None
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    @property
    def photo_count(self):
        if self.photos:
            import json
            try:
                return len(json.loads(self.photos))
            except (json.JSONDecodeError, TypeError):
                return 0
        return 0

    def __repr__(self):
        return f'<RawMaterial {self.code or self.id} {self.name}>'


# ══════════════════════════════════════════════════════════
# 4. SemiFinished  半成品
# ══════════════════════════════════════════════════════════

class SemiFinished(db.Model):
    __tablename__ = 'semi_finished'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(60), unique=True, nullable=True)
    name = db.Column(db.String(200), nullable=False)

    type = db.Column(db.String(30), nullable=False, default='wax_model')  # wax_model/casting/setting/polishing/outsource/craftsman
    workflow_order_id = db.Column(db.String(60), nullable=True)  # 关联大系统订单号
    craftsman = db.Column(db.String(80), nullable=True)  # 当前工匠
    current_location = db.Column(db.String(200), nullable=True)

    materials_snapshot = db.Column(db.Text, nullable=True)  # JSON: 用了哪些料
    estimated_complete_date = db.Column(db.Date, nullable=True)

    cost_summary = db.Column(db.Float, nullable=True)  # 成本汇总，管理员可见

    status = db.Column(db.String(30), nullable=False, default='in_progress')
    photos = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    @property
    def type_display(self):
        _map = {
            'wax_model': '精膜', 'casting': '铸件',
            'setting': '镶石中', 'polishing': '抛光中',
            'outsource': '在外包', 'craftsman': '在工匠',
            'other': '其他',
        }
        return _map.get(self.type, self.type)

    @property
    def status_display(self):
        _map = {
            'in_progress': '制作中', 'completed': '已完成',
            'pending_check': '待验收', 'returned': '已退回',
        }
        return _map.get(self.status, self.status)

    @property
    def first_photo(self):
        if self.photos:
            import json
            try:
                arr = json.loads(self.photos)
                return arr[0] if arr else None
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    @property
    def photo_count(self):
        if self.photos:
            import json
            try:
                return len(json.loads(self.photos))
            except (json.JSONDecodeError, TypeError):
                return 0
        return 0

    def __repr__(self):
        return f'<SemiFinished {self.code or self.id} {self.name}>'


# ══════════════════════════════════════════════════════════
# 5. FinishedProduct  成品
# ══════════════════════════════════════════════════════════

class FinishedProduct(db.Model):
    __tablename__ = 'finished_products_stock'

    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(60), unique=True, nullable=True)
    name = db.Column(db.String(200), nullable=False)

    type = db.Column(db.String(40), nullable=True)  # ring/necklace/bracelet/earrings/bangle/other
    material_desc = db.Column(db.String(200), nullable=True)

    gold_weight = db.Column(db.Float, nullable=True)
    stone_weight = db.Column(db.Float, nullable=True)

    main_stone = db.Column(db.String(200), nullable=True)
    side_stones = db.Column(db.Text, nullable=True)

    # 成本/售价（管理员可见）
    total_cost = db.Column(db.Float, nullable=True)
    sale_price = db.Column(db.Float, nullable=True)

    location = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(30), nullable=False, default='in_stock')  # in_stock/display/locked/out
    workflow_order_id = db.Column(db.String(60), nullable=True)  # 关联大系统订单

    photos = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    @property
    def type_display(self):
        _map = {
            'ring': '戒指', 'necklace': '项链', 'bracelet': '手链',
            'earrings': '耳饰', 'bangle': '手镯', 'pendant': '吊坠',
            'brooch': '胸针', 'set': '套装', 'other': '其他',
        }
        return _map.get(self.type, self.type)

    @property
    def status_display(self):
        _map = {
            'in_stock': '在库', 'display': '展示中',
            'locked': '已锁定', 'out': '已出库',
        }
        return _map.get(self.status, self.status)

    @property
    def first_photo(self):
        """返回第一张照片的文件名，没有则返回 None"""
        if self.photos:
            import json
            try:
                arr = json.loads(self.photos)
                return arr[0] if arr else None
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    @property
    def photo_count(self):
        if self.photos:
            import json
            try:
                return len(json.loads(self.photos))
            except (json.JSONDecodeError, TypeError):
                return 0
        return 0

    def __repr__(self):
        return f'<FinishedProduct {self.product_code or self.id}>'


# ══════════════════════════════════════════════════════════
# 6. Transaction  出入库流水
# ══════════════════════════════════════════════════════════

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), nullable=False)  # in/out/transfer/check_adjust/return
    target_type = db.Column(db.String(20), nullable=False)  # raw/semi/finished
    target_id = db.Column(db.Integer, nullable=False)
    target_name = db.Column(db.String(200), nullable=True)  # 物料名称快照

    quantity = db.Column(db.Integer, nullable=True, default=1)
    weight = db.Column(db.Float, nullable=True)

    from_location = db.Column(db.String(200), nullable=True)
    to_location = db.Column(db.String(200), nullable=True)

    related_order_id = db.Column(db.String(60), nullable=True)

    # 操作时的成本记录（管理员可见）
    cost_recorded = db.Column(db.Float, nullable=True)

    operator = db.Column(db.String(80), nullable=True)  # username
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    @property
    def type_display(self):
        _map = {
            'in': '入库', 'out': '出库',
            'transfer': '调拨', 'check_adjust': '盘点调整',
            'return': '退货',
        }
        return _map.get(self.type, self.type)

    def __repr__(self):
        return f'<Transaction {self.type} {self.target_type}:{self.target_id}>'
