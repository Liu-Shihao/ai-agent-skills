---
name: feature-query
description: 解析和查询 #05A 和 #05B 格式的 feature 数据。支持查询指定行和组的 feature 状态（enable/disable），返回原始数据和处理后的值。适用于分析设备feature配置、协议数据解析等场景。
---

# Feature Query

解析和查询 #05A、#05B 格式的 feature 数据。

## 数据格式

### #05A
- 每行 16 组，每组 4 位
- 第一位：1 = Enable，0 = Disable
- 后 3 位：feature 值

示例：`1000` → Enable, 值 = `000`

### #05B
- 每行 16 组，每组 5 位
- 包含字母和数字
- 字母（前缀 2 位）可能为空

示例：`FA008` → 前缀 = `FA`, 值 = `008`

## 索引计算

**重要：** 第 N 个 feature 的计算方式：

```
line = (index - 1) // 16 + 1    # 行号 (1-indexed)
group = (index - 1) % 16 + 1    # 组号 (1-16)
```

示例：
- 第1个 → line=1, group=1
- 第16个 → line=1, group=16
- 第17个 → line=2, group=1
- 第32个 → line=2, group=16

## 使用方法

### 命令行调用

```bash
python scripts/parser.py --type 05A --data "<data>" --line <行号> --group <组号>
python scripts/parser.py --type 05B --data "<data>" --line <行号> --group <组号>
```

### 作为模块导入

```python
from parser import query_feature, query_all_by_group, query_enabled_features

# 查询单个 feature
result = query_feature("05A", data, line=1, group=1)
# 返回: {'line': 1, 'group': 1, 'enabled': True, 'value': '000', 'raw': '1000'}

# 查询所有行的同一组
results = query_all_by_group("05A", data, group=1)

# 查询所有 enabled 的 features（仅 05A）
enabled = query_enabled_features("05A", data)
```

## 示例

### 查询 #05A 第 1 行第 1 组
```
输入: 1000101910001000...
结果: Line 1, Group 1: ✓ Enabled, Raw: 1000
```

### 查询 #05B 第 1 行第 1 组
```
输入: FA008VN002...
结果: Line 1, Group 1: Prefix='FA', Value=008, Raw: FA008
```

## 输出格式

查询结果包含：
- `line`: 行号 (1-indexed)
- `group`: 组号 (1-indexed, 1-16)
- `enabled`: 是否启用 (#05A 专有)
- `prefix`: 前缀字母 (#05B 专有)
- `raw`: 原始数据
