#!/usr/bin/env python3
"""
Feature Query Parser

解析 #05A 和 #05B 数据，查询特定组的 feature 状态

#05A: 4位一组，第一位1表示enable，0表示disable，每行16组
#05B: 5位一组，包含字母和数字，字母可能为空，每行16组
"""

import re
import sys
from typing import Optional


def parse_05a(data: str) -> list[dict]:
    """
    解析 #05A 数据
    每行16组，每组4位，第一位1=enable, 0=disable
    """
    results = []
    lines = [l.strip() for l in data.strip().split('\n') if l.strip()]
    
    for line_idx, line in enumerate(lines):
        # 去除空格
        line = line.replace(' ', '')
        
        if len(line) < 16 * 4:
            print(f"Warning: Line {line_idx + 1} has insufficient length ({len(line)}), expected {16 * 4}", file=sys.stderr)
            continue
            
        for group_idx in range(16):
            start = group_idx * 4
            end = start + 4
            group = line[start:end]
            
            # 提取第一位作为 enable 标志
            is_enabled = group[0] == '1'
            # 提取后3位作为 feature 值
            feature_value = group[1:] if len(group) >= 4 else ''
            
            results.append({
                'line': line_idx + 1,
                'group': group_idx + 1,
                'enabled': is_enabled,
                'value': feature_value,
                'raw': group
            })
    
    return results


def parse_05b(data: str) -> list[dict]:
    """
    解析 #05B 数据
    每行16组，每组4-5位（前缀0-2个字母 + 3位数字），字母可能为空
    """
    import re
    results = []
    lines = data.strip().split('\n')
    
    for line_idx, line in enumerate(lines):
        # 去掉所有空格
        clean = line.replace(' ', '')
        
        # 使用正则匹配: 2字母+3数字 | 1字母+3数字 | 3数字
        pattern = r'([A-Z]{2}\d{3}|[A-Z]\d{3}|\d{3})'
        groups = re.findall(pattern, clean)
        
        # 如果超过16组，取最后16组
        if len(groups) > 16:
            groups = groups[-16:]
        
        if len(groups) < 16:
            print(f"Warning: Line {line_idx + 1} has {len(groups)} groups, expected 16", file=sys.stderr)
        
        for group_idx, group in enumerate(groups):
            # 提取字母部分（前两位）
            prefix = group[:2] if len(group) >= 2 else ''
            # 提取数字部分（后3位）
            suffix = group[2:] if len(group) >= 3 else ''
            
            results.append({
                'line': line_idx + 1,
                'group': group_idx + 1,
                'prefix': prefix.strip(),
                'value': suffix,
                'raw': group
            })
    
    return results


def query_feature(data_type: str, data: str, line: int, group: int) -> Optional[dict]:
    """
    查询指定行和组的 feature
    
    Args:
        data_type: "05A" 或 "05B"
        data: 数据内容
        line: 行号 (1-indexed)
        group: 组号 (1-indexed, 1-16)
    
    Returns:
        feature 信息字典，如果不存在则返回 None
    """
    if data_type == "05A":
        parsed = parse_05a(data)
    elif data_type == "05B":
        parsed = parse_05b(data)
    else:
        raise ValueError(f"Unknown data type: {data_type}")
    
    # 过滤指定行
    filtered = [f for f in parsed if f['line'] == line and f['group'] == group]
    
    return filtered[0] if filtered else None


def query_all_by_group(data_type: str, data: str, group: int) -> list[dict]:
    """
    查询所有行中指定组的 feature
    
    Args:
        data_type: "05A" 或 "05B"
        data: 数据内容
        group: 组号 (1-indexed, 1-16)
    
    Returns:
        所有匹配的行
    """
    if data_type == "05A":
        parsed = parse_05a(data)
    elif data_type == "05B":
        parsed = parse_05b(data)
    else:
        raise ValueError(f"Unknown data type: {data_type}")
    
    return [f for f in parsed if f['group'] == group]


def query_enabled_features(data_type: str, data: str) -> list[dict]:
    """
    查询所有 enable 的 features（仅适用于 #05A）
    """
    if data_type != "05A":
        raise ValueError("query_enabled_features only works with #05A data")
    
    parsed = parse_05a(data)
    return [f for f in parsed if f['enabled']]


def format_result(result: dict, data_type: str) -> str:
    """格式化查询结果"""
    if data_type == "05A":
        status = "✓ Enabled" if result['enabled'] else "✗ Disabled"
        return f"Line {result['line']}, Group {result['group']}: {status}\n  Raw: {result['raw']}"
    elif data_type == "05B":
        return f"Line {result['line']}, Group {result['group']}: Prefix='{result['prefix']}', Value={result['value']}\n  Raw: {result['raw']}"
    return str(result)


if __name__ == "__main__":
    # 测试示例
    sample_05a = """1000101910001000100010001000000010001000100010001000100010001000
0000100000001000000010001000100010001000000010000000000000001011
10110000103700001000100010000000010001000100010251076000000001999
1000100010001000000011201255103700000000000010601026110010120000
0000100000000000000010000000000010001000100010001000100010001000
1000100010001000100010001000100010001000100010000000000010001000
1000000010111011101710281028000019991999000019990000000000000000
0000000000000000199919990000199910111999000012990000000000000000"""
    
    sample_05b = """FA008VN002FN006FN012FN012FN012FN010FN008FN008FN008FN006FN006FN004FN004FN004FN004
FN004FN004FN003FN003FN003FN003FN003FN003FN004FN002FN001FX009FX009FX009FX009VN002
VN002VA002VA002VA003FA012FA006FA002FA003FA008FA015FA040VA002VA002VA003VA003VA003
FN003FN003FN003FA008FN016VA003VA003VA003 000 000 000VA003VA003VA003VA003FA008
FA008FN001FN002FN003FN003FN003FN004FN004FN006FN010FN010FN010FN010FN010FN010FN010
FN010FN012FN012FN012FN012FN016FN016FN016FN016FN042FA001FA002FA005FA007FN042FA008
FX017FA025VN002VN002VA002VA002VA002VA003VA003VA003 000VA003 000 000 000VA003
 000 000 000 000VA003VA003VA003VA003VA003VA003VA003 000VA003 000VA003VA003FA008"""
    
    # 测试查询第1行第1组
    print("=== #05A Line 1, Group 1 ===")
    result = query_feature("05A", sample_05a, 1, 1)
    print(format_result(result, "05A") if result else "Not found")
    
    print("\n=== #05A Line 1, Group 2 ===")
    result = query_feature("05A", sample_05a, 1, 2)
    print(format_result(result, "05A") if result else "Not found")
    
    print("\n=== #05B Line 1, Group 1 ===")
    result = query_feature("05B", sample_05b, 1, 1)
    print(format_result(result, "05B") if result else "Not found")
    
    print("\n=== All #05A Group 1 ===")
    results = query_all_by_group("05A", sample_05a, 1)
    for r in results:
        print(format_result(r, "05A"))
