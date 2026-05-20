#!/usr/bin/env python3
"""
中国地级市行政区划地图绘制工具

用法:
    python plot_city_map.py                          # 列出可用指标
    python plot_city_map.py --indicator "GDP(亿元)"  # 列出该指标可用年份
    python plot_city_map.py --indicator "GDP(亿元)" --year 2020  # 绘制地图

依赖: geopandas, matplotlib, pandas
"""

import json
import sys
import argparse

DATA_FILE = "data.json"
GEOJSON_FILE = "中国_市.geojson"


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_geojson():
    with open(GEOJSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_geo_city_names():
    """获取 GeoJSON 中所有地级市面要素的名称"""
    geojson = load_geojson()
    return {
        f["properties"]["name"]
        for f in geojson["features"]
        if f["geometry"]["type"] == "MultiPolygon"
    }


def filter_city_data(data, indicator, geo_cities):
    """过滤掉 GeoJSON 中不存在的城市（如省级记录）"""
    return {
        city: years
        for city, years in data[indicator].items()
        if city in geo_cities
    }


def list_indicators(data):
    """列出所有可用指标及年份范围"""
    geo_cities = get_geo_city_names()
    print(f"共 {len(data)} 个指标：\n")
    for name in sorted(data.keys()):
        city_data = filter_city_data(data, name, geo_cities)
        all_years = set()
        for city, years in city_data.items():
            all_years.update(years.keys())
        sorted_years = sorted(all_years)
        yr_range = f"{sorted_years[0]}-{sorted_years[-1]}" if sorted_years else "无数据"
        print(f"  {name}")
        print(f"    年份: {yr_range} (共 {len(sorted_years)} 年)")
        print(f"    城市: {len(city_data)} 个")


def list_years(data, indicator):
    """列出指定指标的可用年份"""
    geo_cities = get_geo_city_names()

    if indicator not in data:
        print(f"错误: 指标 '{indicator}' 不存在")
        print("可用指标可通过不加参数运行本脚本查看")
        return None

    city_data = filter_city_data(data, indicator, geo_cities)

    all_years = set()
    for city, years in city_data.items():
        all_years.update(years.keys())
    sorted_years = sorted(all_years)

    print(f"指标: {indicator}")
    print(f"年份列表 ({len(sorted_years)} 年):")
    for y in sorted_years:
        cities_with_data = sum(1 for c, ys in city_data.items() if y in ys)
        print(f"  {y} — {cities_with_data} 个城市有数据")
    return sorted_years


def validate_inputs(data, indicator, year):
    """验证指标和年份是否存在，返回错误信息或 None"""
    if indicator not in data:
        return f"指标 '{indicator}' 不存在。使用 --list 查看所有可用指标。"

    year_key = f"{year}年"
    has_year = any(year_key in years for years in data[indicator].values())
    if not has_year:
        return f"指标 '{indicator}' 没有 {year} 年的数据。使用 --list-years --indicator \"{indicator}\" 查看可用年份。"

    return None


def draw_map(data, indicator, year):
    """绘制 choropleth 地图"""
    import geopandas as gpd
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import pandas as pd
    import numpy as np

    year_key = f"{year}年"

    # 准备数据 DataFrame
    indicator_data = data[indicator]
    records = []
    for city, years in indicator_data.items():
        val = years.get(year_key, None)
        records.append({"name": city, "value": float(val) if val is not None else None})

    df_data = pd.DataFrame(records)

    # 加载 GeoJSON
    gdf = gpd.read_file(GEOJSON_FILE)
    # 只保留面要素（剔除境界线）
    gdf = gdf[gdf.geometry.type == "MultiPolygon"].copy()

    # 合并数据
    gdf = gdf.merge(df_data, on="name", how="left")

    # 分类：有数据 / 无数据
    has_data = gdf["value"].notna()
    no_data_count = (~has_data).sum()

    # 创建图形
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))

    # 绘制无数据区域（灰色）
    if no_data_count > 0:
        gdf[~has_data].plot(
            ax=ax,
            color="#e0e0e0",
            edgecolor="white",
            linewidth=0.3,
            label="无数据",
        )

    # 绘制有数据区域（连续色阶）
    if has_data.any():
        values = gdf.loc[has_data, "value"]
        vmin, vmax = values.min(), values.max()

        gdf[has_data].plot(
            ax=ax,
            column="value",
            cmap="YlOrRd",
            legend=True,
            edgecolor="white",
            linewidth=0.3,
            vmin=vmin,
            vmax=vmax,
            legend_kwds={
                "label": f"{indicator}",
                "shrink": 0.6,
                "pad": 0.02,
            },
        )

    # 设置地图范围（中国范围）
    ax.set_xlim(73, 136)
    ax.set_ylim(3, 54)

    ax.set_title(
        f"{indicator} — {year}年",
        fontsize=16,
        fontweight="bold",
        pad=12,
    )
    ax.axis("off")

    # 添加图例说明
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor="#e0e0e0", edgecolor="white", label="无数据")]
    if no_data_count > 0:
        legend1 = ax.legend(
            handles=legend_elements,
            loc="lower left",
            framealpha=0.8,
            fontsize=10,
        )
        ax.add_artist(legend1)

    # 右下角文字标注
    ax.text(
        0.98, 0.02,
        f"共 {len(gdf)} 个区域    有数据: {has_data.sum()}    无数据: {no_data_count}",
        transform=ax.transAxes,
        fontsize=9,
        ha="right",
        va="bottom",
        color="gray",
        fontstyle="italic",
    )

    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="中国地级市行政区划地图绘制工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    %(prog)s                              # 列出所有指标
    %(prog)s --indicator "GDP(亿元)"       # 查看该指标可用年份
    %(prog)s -i "GDP(亿元)" -y 2020        # 绘制2020年GDP地图
    %(prog)s -i "常住人口数(万人)" -y 2020  # 绘制2020年常住人口地图
        """,
    )
    parser.add_argument("-i", "--indicator", help="指标名称")
    parser.add_argument("-y", "--year", type=int, help="年份（如 2020）")
    parser.add_argument(
        "-l", "--list", action="store_true",
        help="列出所有可用指标及年份范围",
    )

    args = parser.parse_args()

    # 加载数据
    try:
        data = load_data()
    except FileNotFoundError:
        print(f"错误: 找不到数据文件 {DATA_FILE}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误: {DATA_FILE} 格式错误")
        sys.exit(1)

    # 列出所有指标
    if args.list or (args.indicator is None and args.year is None):
        list_indicators(data)
        return

    # 列出指定指标的可用年份
    if args.indicator and args.year is None:
        list_years(data, args.indicator)
        return

    # 绘制地图需要 indicator 和 year
    if args.indicator and args.year is not None:
        error = validate_inputs(data, args.indicator, args.year)
        if error:
            print(f"错误: {error}")
            sys.exit(1)

        try:
            draw_map(data, args.indicator, args.year)
        except ImportError as e:
            missing_lib = str(e).split("'")[1] if "'" in str(e) else str(e)
            print(f"缺少依赖库: {missing_lib}")
            print("请安装: pip install geopandas matplotlib pandas")
            sys.exit(1)
        except Exception as e:
            print(f"绘图出错: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()