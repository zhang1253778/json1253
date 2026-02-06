# JSON 修复与格式处理工具

`json_tool.py` 提供以下能力：

- 解析标准 JSON
- 尝试修复常见非标准 JSON 问题：
  - `//` 与 `/* */` 注释
  - 单引号字符串
  - 未加引号的对象键
  - 结尾多余逗号
- 支持两种输出模式：
  - 格式化（默认）
  - 压缩（minify）

## 用法

```bash
# 读取文件并格式化
python3 json_tool.py data.json

# 压缩输出
python3 json_tool.py data.json --mode minify

# 从标准输入读取
cat data.json | python3 json_tool.py -m format -i 4
```
