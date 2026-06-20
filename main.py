import argparse
import sys

import models
import storage
import commands


def build_parser():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="家庭果园果树管理与采摘记录工具",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add-tree", help="添加果树")
    p_add.add_argument("tree_id", help="果树编号，如 T001")
    p_add.add_argument("name", help="果树名称，如 苹果树")
    p_add.add_argument(
        "--variety", required=True,
        choices=models.VARIETIES,
        help=f"品种: {' / '.join(models.VARIETIES)}",
    )
    p_add.add_argument("--location", required=True, help="位置，如 A区3行5号")
    p_add.add_argument("--plant-year", required=True, help="种植年份，如 2015")

    p_spray = sub.add_parser("spray", help="记录喷药")
    p_spray.add_argument("tree_id", help="果树编号")
    p_spray.add_argument("--date", required=True, help="日期 YYYY-MM-DD")
    p_spray.add_argument(
        "--type", required=True,
        choices=models.SPRAY_TYPES,
        help=f"喷药类型: {' / '.join(models.SPRAY_TYPES)}",
    )
    p_spray.add_argument("--operator", required=True, help="操作人")

    p_harvest = sub.add_parser("harvest", help="记录收获")
    p_harvest.add_argument("tree_id", help="果树编号")
    p_harvest.add_argument("--date", required=True, help="日期 YYYY-MM-DD")
    p_harvest.add_argument("--weight-kg", required=True, help="收获重量(kg)，必须正数")
    p_harvest.add_argument(
        "--grade", required=True,
        choices=models.GRADES,
        help=f"等级: {' / '.join(models.GRADES)}",
    )

    p_sell = sub.add_parser("sell-harvest", help="记录销售")
    p_sell.add_argument("tree_id", help="果树编号")
    p_sell.add_argument("--date", required=True, help="日期 YYYY-MM-DD")
    p_sell.add_argument("--weight-kg", required=True, help="销售重量(kg)")
    p_sell.add_argument("--price-per-kg", required=True, help="单价(分/kg)，整数")

    p_month = sub.add_parser("monthly-harvest", help="按月按品种统计")
    p_month.add_argument("--month", required=True, help="月份 YYYY-MM")

    p_stats = sub.add_parser("tree-stats", help="某果树累计统计")
    p_stats.add_argument("tree_id", help="果树编号")

    return parser


def run(args):
    db = storage.load()
    dirty = False

    if args.command == "add-tree":
        msg = commands.add_tree(
            db, args.tree_id, args.name, args.variety,
            args.location, args.plant_year,
        )
        dirty = True
        print(msg)

    elif args.command == "spray":
        msg = commands.spray(
            db, args.tree_id, args.date, args.type, args.operator,
        )
        dirty = True
        print(msg)

    elif args.command == "harvest":
        msg = commands.harvest(
            db, args.tree_id, args.date, args.weight_kg, args.grade,
        )
        dirty = True
        print(msg)

    elif args.command == "sell-harvest":
        msg = commands.sell_harvest(
            db, args.tree_id, args.date, args.weight_kg, args.price_per_kg,
        )
        dirty = True
        print(msg)

    elif args.command == "monthly-harvest":
        print(commands.monthly_harvest(db, args.month))

    elif args.command == "tree-stats":
        print(commands.tree_stats(db, args.tree_id))

    if dirty:
        storage.save(db)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run(args)
    except models.ValidationError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("已取消", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
