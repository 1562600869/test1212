from collections import defaultdict

import models


def add_tree(db, tree_id, name, variety, location, plant_year):
    tree_id = models.validate_tree_id(tree_id)
    variety = models.validate_variety(variety)
    plant_year = models.validate_year(plant_year)
    if not name or not isinstance(name, str) or not name.strip():
        raise models.ValidationError("果树名称不能为空")
    if tree_id in db["trees"]:
        raise models.ValidationError(f"果树编号已存在: {tree_id}")
    db["trees"][tree_id] = {
        "id": tree_id,
        "name": name.strip(),
        "variety": variety,
        "location": location.strip() if location else "",
        "plant_year": plant_year,
    }
    tree = db["trees"][tree_id]
    return (
        f"已添加果树: {tree['id']} {tree['name']} | 品种: {tree['variety']} "
        f"| 位置: {tree['location'] or '-'} | 种植年份: {tree['plant_year']}"
    )


def spray(db, tree_id, date, stype, operator):
    tree_id = models.validate_tree_id(tree_id)
    models.require_tree(db, tree_id)
    date = models.validate_date(date)
    stype = models.validate_spray_type(stype)
    if not operator or not isinstance(operator, str) or not operator.strip():
        raise models.ValidationError("操作人不能为空")
    record = {
        "tree_id": tree_id,
        "date": date,
        "type": stype,
        "operator": operator.strip(),
    }
    db["sprays"].append(record)
    return (
        f"已记录喷药: {record['date']} | {tree_id} | "
        f"类型: {record['type']} | 操作人: {record['operator']}"
    )


def harvest(db, tree_id, date, weight_kg, grade):
    tree_id = models.validate_tree_id(tree_id)
    models.require_tree(db, tree_id)
    date = models.validate_date(date)
    weight_kg = models.validate_positive_float(weight_kg, "收获重量")
    grade = models.validate_grade(grade)
    record = {
        "tree_id": tree_id,
        "date": date,
        "weight_kg": round(weight_kg, 3),
        "grade": grade,
    }
    db["harvests"].append(record)
    return (
        f"已记录收获: {record['date']} | {tree_id} | "
        f"{record['weight_kg']} kg | 等级: {record['grade']}"
    )


def sell_harvest(db, tree_id, date, weight_kg, price_per_kg):
    tree_id = models.validate_tree_id(tree_id)
    models.require_tree(db, tree_id)
    date = models.validate_date(date)
    weight_kg = models.validate_positive_float(weight_kg, "销售重量")
    price_per_kg = models.validate_positive_int(price_per_kg, "单价")

    year = models.year_of(date)
    remaining = models.remaining_harvest_weight(db, tree_id, year)
    if weight_kg > remaining + 1e-9:
        raise models.ValidationError(
            f"{year} 年该果树未售重量仅剩 {remaining:.3f} kg，"
            f"无法销售 {weight_kg:.3f} kg"
        )

    income = round(weight_kg * price_per_kg, 2)
    record = {
        "tree_id": tree_id,
        "date": date,
        "weight_kg": round(weight_kg, 3),
        "price_per_kg": price_per_kg,
        "income": income,
    }
    db["sales"].append(record)
    return (
        f"已记录销售: {record['date']} | {tree_id} | "
        f"{record['weight_kg']} kg × {record['price_per_kg']} 分/kg = "
        f"{record['income']:.2f} 分 ({record['income']/100:.2f} 元)"
    )


def monthly_harvest(db, month):
    month = models.validate_month(month)
    by_variety = defaultdict(lambda: {"weight_kg": 0.0, "income": 0.0})

    variety_of = {tid: t["variety"] for tid, t in db["trees"].items()}

    for h in db["harvests"]:
        if models.month_of(h["date"]) == month:
            v = variety_of.get(h["tree_id"], "未知")
            by_variety[v]["weight_kg"] += h["weight_kg"]

    for s in db["sales"]:
        if models.month_of(s["date"]) == month:
            v = variety_of.get(s["tree_id"], "未知")
            by_variety[v]["weight_kg"] += 0
            by_variety[v]["income"] += s["income"]

    if not by_variety:
        return f"{month} 月没有任何记录。"

    lines = [f"=== {month} 月 各品种统计 ==="]
    lines.append(
        f"{'品种':<8}{'收获重量(kg)':>16}{'销售收入(元)':>16}"
    )
    total_w = 0.0
    total_i = 0.0
    for variety in sorted(by_variety):
        w = round(by_variety[variety]["weight_kg"], 3)
        i = by_variety[variety]["income"]
        total_w += w
        total_i += i
        lines.append(
            f"{variety:<8}{w:>16.3f}{i/100:>16.2f}"
        )
    lines.append("-" * 40)
    lines.append(
        f"{'合计':<8}{total_w:>16.3f}{total_i/100:>16.2f}"
    )
    return "\n".join(lines)


def tree_stats(db, tree_id):
    tree_id = models.validate_tree_id(tree_id)
    tree = models.require_tree(db, tree_id)

    total_weight = 0.0
    total_income = 0.0
    harvest_count = 0
    sale_count = 0

    for h in db["harvests"]:
        if h["tree_id"] == tree_id:
            total_weight += h["weight_kg"]
            harvest_count += 1

    for s in db["sales"]:
        if s["tree_id"] == tree_id:
            total_income += s["income"]
            sale_count += 1

    lines = [f"=== 果树统计: {tree_id} ==="]
    lines.append(f"名称: {tree['name']}")
    lines.append(f"品种: {tree['variety']}")
    lines.append(f"位置: {tree['location'] or '-'}")
    lines.append(f"种植年份: {tree['plant_year']}")
    lines.append(f"累计收获次数: {harvest_count}")
    lines.append(f"累计收获重量: {total_weight:.3f} kg")
    lines.append(f"累计销售次数: {sale_count}")
    lines.append(f"累计销售收入: {total_income/100:.2f} 元 ({total_income:.0f} 分)")
    return "\n".join(lines)
