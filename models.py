import datetime
import re


VARIETIES = ("富士", "红星", "黄元帅", "其他")
SPRAY_TYPES = ("杀虫剂", "杀菌剂", "叶面肥", "除草剂")
GRADES = ("特级", "一级", "二级", "等外")

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MONTH_RE = re.compile(r"^\d{4}-\d{2}$")


class ValidationError(Exception):
    pass


def validate_variety(variety):
    if variety not in VARIETIES:
        raise ValidationError(
            f"品种必须是: {', '.join(VARIETIES)} (收到: {variety})"
        )
    return variety


def validate_spray_type(stype):
    if stype not in SPRAY_TYPES:
        raise ValidationError(
            f"喷药类型必须是: {', '.join(SPRAY_TYPES)} (收到: {stype})"
        )
    return stype


def validate_grade(grade):
    if grade not in GRADES:
        raise ValidationError(
            f"收获等级必须是: {', '.join(GRADES)} (收到: {grade})"
        )
    return grade


def validate_date(date_str):
    if not _DATE_RE.match(date_str or ""):
        raise ValidationError(f"日期格式必须为 YYYY-MM-DD (收到: {date_str})")
    try:
        datetime.date.fromisoformat(date_str)
    except ValueError as e:
        raise ValidationError(f"日期无效: {date_str} ({e})")
    return date_str


def validate_month(month_str):
    if not _MONTH_RE.match(month_str or ""):
        raise ValidationError(f"月份格式必须为 YYYY-MM (收到: {month_str})")
    try:
        y, m = month_str.split("-")
        datetime.date(int(y), int(m), 1)
    except (ValueError, IndexError) as e:
        raise ValidationError(f"月份无效: {month_str} ({e})")
    return month_str


def validate_positive_float(value, field="重量"):
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field}必须是数字 (收到: {value})")
    if v <= 0:
        raise ValidationError(f"{field}必须是正数 (收到: {value})")
    return v


def validate_positive_int(value, field="数量"):
    try:
        v = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field}必须是整数 (收到: {value})")
    if v <= 0:
        raise ValidationError(f"{field}必须是正整数 (收到: {value})")
    return v


def validate_year(value):
    try:
        v = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"种植年份必须是整数 (收到: {value})")
    if v < 1900 or v > datetime.date.today().year + 1:
        raise ValidationError(f"种植年份不合理: {value}")
    return v


def validate_tree_id(tree_id):
    if not tree_id or not isinstance(tree_id, str) or not tree_id.strip():
        raise ValidationError("果树编号不能为空")
    return tree_id.strip()


def require_tree(db, tree_id):
    if tree_id not in db["trees"]:
        raise ValidationError(f"果树不存在: {tree_id}")
    return db["trees"][tree_id]


def year_of(date_str):
    return date_str[:4]


def month_of(date_str):
    return date_str[:7]


def remaining_harvest_weight(db, tree_id, year):
    total = 0.0
    for h in db["harvests"]:
        if h["tree_id"] == tree_id and year_of(h["date"]) == year:
            total += h["weight_kg"]
    sold = 0.0
    for s in db["sales"]:
        if s["tree_id"] == tree_id and year_of(s["date"]) == year:
            sold += s["weight_kg"]
    return total - sold
