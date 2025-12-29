"""
我的第一个 MCP 服务
学习目的：理解 MCP 的基本结构
"""

import os
import platform
from datetime import datetime
from mcp.server.fastmcp import FastMCP
import sqlite3
import re

# 1. 创建 MCP 服务实例
#    "我的学习服务" 是服务名称，会显示在客户端中
mcp = FastMCP("我的学习服务")

# ============ Skill 发现器配置 ============
SKILLS_BASE_PATH = r'D:\桌面\mcp\.claude\skills'
AGENTS_MD_PATH = r'D:\桌面\mcp\AGENTS.md'


# ============ Resources（资源）============
# Resource 让 AI 可以读取数据

# 静态资源：固定 URI
@mcp.resource("config://app-settings")
def get_app_settings() -> str:
    """
    获取应用配置信息
    URI: config://app-settings
    """
    return """
    应用名称: 我的学习服务
    版本: 0.1.0
    作者: MCP学习者
    创建时间: 2024
    """


# 动态资源：返回实时数据
@mcp.resource("system://info")
def get_system_info() -> str:
    """
    获取系统信息
    URI: system://info
    """
    return f"""
    操作系统: {platform.system()} {platform.release()}
    Python版本: {platform.python_version()}
    当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    当前目录: {os.getcwd()}
    """


# 带参数的资源模板
@mcp.resource("file:///{path}")
def read_file_resource(path: str) -> str:
    """
    读取指定路径的文件内容
    URI: file:///路径 (例如 file:///readme.txt)
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"错误：文件 '{path}' 不存在"
    except Exception as e:
        return f"错误：{str(e)}"


# 2. 定义一个简单的 Tool（工具）
#    Tool 让 AI 可以执行操作
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    计算两个数字的和
    
    Args:
        a: 第一个数字
        b: 第二个数字
    
    Returns:
        两数之和
    """
    return a + b


@mcp.tool()
def greet(name: str) -> str:
    """
    向用户打招呼
    
    Args:
        name: 用户的名字
    
    Returns:
        问候语
    """
    return f"你好，{name}！欢迎学习 MCP 开发！"

@mcp.tool()
def query_users() -> str:
    """
    查询用户列表

    Returns:
        用户列表
    """
    conn = sqlite3.connect(r'D:\桌面\mcp\test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    conn.close()
    output = "ID | 姓名 | 年龄 | 城市\n"
    for row in results:
        output += f"{row[0]} | {row[1]} | {row[2]} | {row[3]}\n"
    return output

@mcp.tool()
def query_users_by_city(city: str) -> str:
    """
    根据城市查询用户列表

    Returns:
        用户列表
    """
    conn = sqlite3.connect(r'D:\桌面\mcp\test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE city = ?", (city,))
    results = cursor.fetchall()
    conn.close()
    if not results:
        return f"没有找到城市为 {city} 的用户"
    output = "ID | 姓名 | 年龄 | 城市\n"
    for row in results:
        output += f"{row[0]} | {row[1]} | {row[2]} | {row[3]}\n"
    return output

@mcp.tool()
def add_user(name: str, age: int, city: str) -> str:
    """
    添加用户

    Args:
        name: 用户姓名
        age: 用户年龄
        city: 所在城市
    
    Returns:
        用户列表
    """
    conn = sqlite3.connect(r'D:\桌面\mcp\test.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, age, city) VALUES (?, ?, ?)", (name, age, city))
    conn.commit()
    conn.close()
    if  not cursor.rowcount:
        return f"添加用户 {name} 失败"
    return f"添加用户 {name} 成功,{age}岁,来自{city}"

@mcp.tool()
def connect_db(path:str) -> str:
    """
    连接数据库

    Returns:
        数据库连接
    """
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    conn.close()
    return "数据库连接成功"

@mcp.prompt()
def code_review(code: str) -> str:
    """
    代码审查

    Args:
        code: 待审查的代码

    Returns:
        审查结果
    """
    return f"""请审查以下代码，指出潜在的问题和改进建议：
     
    ```{code}```
    请从以下方面进行审查：
1. 代码逻辑是否正确
2. 是否有潜在的 bug
3. 代码风格和可读性
4. 性能优化建议
    """

@mcp.prompt()
def frontend_design(requirements: str) -> str:
    """
    前端设计提示词模板

    Args:
        requirements: 前端设计需求

    Returns:
        前端设计提示词
    """
    return f"""你是一个专业的前端设计师。请根据以下需求创建独特、生产级的前端界面。

## 用户需求
{requirements}

## 设计思维
在编码之前，理解上下文并确定一个大胆的美学方向：

- 目的：这个界面解决什么问题？谁在使用它？
- 风格：选择一个极端风格：
    极简主义、极繁混乱、复古未来、有机自然、奢华精致
    俏皮玩具风、杂志编辑风、粗野主义、装饰艺术几何风
    柔和粉彩、工业实用风等
- 约束：技术要求（框架、性能、可访问性）
- 差异化：什么让这个设计令人难忘？用户会记住什么？

### 关键：选择一个清晰的概念方向并精确执行。大胆的极繁主义和精致的极简主义都可以——关键是意图性，而不是强度。

然后实现可运行的代码（HTML/CSS/JS、React、Vue 等），要求：

- 生产级且功能完整
- 视觉上引人注目且令人难忘
- 具有清晰美学观点的连贯性
- 每个细节都精心打磨

## 前端美学指南
- 字体：选择美观、独特、有趣的字体。避免 Arial、Inter 等通用字体；选择能提升美感的独特字体。将独特的展示字体与精致的正文字体搭配。

- 颜色与主题：坚持连贯的美学。使用 CSS 变量保持一致性。主色配锐利的强调色，优于胆怯的、均匀分布的调色板。

- 动效：使用动画增强效果和微交互。HTML 优先使用纯 CSS 方案。React 可用 Motion 库。专注于高影响力时刻：一个精心编排的页面加载（带交错显示）比分散的微交互更令人愉悦。使用滚动触发和令人惊喜的悬停状态。

- 空间构图：意想不到的布局。不对称。重叠。对角线流动。打破网格的元素。慷慨的负空间或受控的密度。

- 背景与视觉细节：创造氛围和深度，而不是默认使用纯色。添加与整体美学匹配的上下文效果和纹理。应用创意形式如渐变网格、噪点纹理、几何图案、分层透明度、戏剧性阴影、装饰边框、自定义光标和颗粒叠加。

## 禁止事项
永远不要使用通用的 AI 生成美学：

过度使用的字体（Inter、Roboto、Arial、系统字体）
陈词滥调的配色方案（特别是白底紫色渐变）
可预测的布局和组件模式
缺乏上下文特色的千篇一律设计
每个设计都应该独特。在明暗主题、不同字体、不同美学之间变化。永远不要在多次生成中收敛到常见选择（如 Space Grotesk）。

重要：实现复杂度要匹配美学愿景。极繁设计需要精心的代码、大量动画和效果。极简或精致设计需要克制、精确，以及对间距、字体和微妙细节的仔细关注。

请生成完整可运行的前端代码（HTML/CSS/JS 或 React/Vue）。

注意，如果已经存在前端界面，你需要先阅读背景前端，确定用户需求的上下文
    """


@mcp.tool()
def get_algorithmic_art_guide(user_request: str) -> str:
    """
    获取算法艺术/生成艺术创作完整指南和模板
    
    使用场景：
    - 用户想创建算法艺术、生成艺术、代码艺术
    - 用户想用 p5.js 创建流场、粒子系统、噪声图案
    - 用户想创建可交互的艺术作品
    - 用户提到 generative art、algorithmic art、creative coding
    
    Args:
        user_request: 用户的艺术创作需求描述（如"创建一个流动的粒子系统"）
    
    Returns:
        包含创作哲学指南、HTML查看器模板、JS生成器模板的完整内容，
        AI 可以根据这些内容为用户生成完整的算法艺术作品代码
    """
    base_path = r'D:\桌面\mcp\.claude\skills\algorithmic-art'
    # 读取 SKILL.md
    with open(f'{base_path}/SKILL.md', 'r', encoding='utf-8') as f:
        skill_guide = f.read()
    # 读取模板
    with open(f'{base_path}/templates/viewer.html', 'r', encoding='utf-8') as f:
        viewer_html = f.read()
    with open(f'{base_path}/templates/generator_template.js', 'r', encoding='utf-8') as f:
        generator_js = f.read()
    return f"""

## 用户需求
{user_request}

## 创作指南
{skill_guide}

## HTML 查看器模板
```html
{viewer_html}

## JS 生成器模板
{generator_js}
请根据以上指南和模板，为用户创建算法艺术作品。 

"""

@mcp.tool()
def get_canvas_design_guide(design_request: str) -> str:
    """
    获取 Canvas 视觉设计/艺术创作完整指南和字体资源
    
    使用场景：
    - 用户想创建海报、艺术作品、视觉设计、静态图片
    - 用户需要生成 PNG 或 PDF 格式的设计作品
    - 用户想要博物馆/杂志级别的高质量视觉输出
    - 用户提到 poster、art、design、视觉设计、平面设计
    - 用户想创建咖啡桌书籍风格的艺术页面
    
    注意：此工具用于静态视觉设计，不是网页前端设计
    
    Args:
        design_request: 用户的设计需求描述（如"创建一张极简主义风格的音乐节海报"）
    
    Returns:
        包含设计哲学指南（两步流程）、可用字体列表的完整内容，
        AI 可以根据这些内容为用户生成 PNG/PDF 格式的视觉艺术作品
    """
    base_path = r'D:\桌面\mcp\.claude\skills\canvas-design'
    
    # 读取 SKILL.md
    with open(f'{base_path}/SKILL.md', 'r', encoding='utf-8') as f:
        skill_guide = f.read()
    
    # 获取可用字体列表
    import os
    fonts_path = f'{base_path}/canvas-fonts'
    fonts = [f for f in os.listdir(fonts_path) if f.endswith('.ttf')]
    fonts_list = '\n'.join(f'- {font}' for font in sorted(fonts))
    
    return f"""## 用户设计需求
{design_request}

## 设计哲学指南
{skill_guide}

## 可用字体资源
字体目录：{fonts_path}
共 {len(fonts)} 个字体文件：

{fonts_list}

## 创作要求
1. 先构思设计哲学 - 命名美学运动，确定 4-6 段哲学方向
2. 再表达为视觉作品（.png 或 .pdf 文件）- 90% 视觉设计，10% 必要文字
3. 文字必须极简，作为视觉元素而非说明文字
4. 追求博物馆/杂志级别的精致工艺
5. 所有元素必须在画布边界内，有适当边距和呼吸空间
6. 使用上述字体目录中的字体文件


请根据以上指南，为用户创建「{design_request}」的视觉艺术作品。
"""

def load_skills_from_agents_md():
    """
    从 AGENTS.md 解析 skill 列表
    返回: [{name, description}, ...]
    """
    with open(AGENTS_MD_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    skills = []
    # 使用正则匹配 <skill>...</skill> 块
    pattern = r'<skill>\s*<name>(.*?)</name>\s*<description>(.*?)</description>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for name, description in matches:
        skills.append({
            'name': name.strip(),
            'description': description.strip().strip('"')
        })
    
    return skills

@mcp.tool()
def list_all_skills() -> str:
    """
    列出所有可用的 Claude Skills 及其描述
    
    使用场景：
    - 用户想知道有哪些工具/技能可用
    - 需要选择合适的 skill 来完成任务
    - 查看所有能力列表
    
    Returns:
        所有 skill 的名称和描述列表
    """
    skills = load_skills_from_agents_md()
    
    result = "## 可用的 Skills 列表\n\n"
    for skill in skills:
        result += f"### {skill['name']}\n{skill['description']}\n\n"
    
    result += "\n使用 `get_skill_guide(skill_name)` 获取具体 skill 的完整使用指南。"
    return result


@mcp.tool()
def get_skill_guide(skill_name: str) -> str:
    """
    获取指定 skill 的完整使用指南（SKILL.md 内容）
    
    Args:
        skill_name: skill 名称（如 "docx", "frontend-design", "canvas-design"）
    
    Returns:
        该 skill 的完整 SKILL.md 指南内容
    """
    skill_md_path = os.path.join(SKILLS_BASE_PATH, skill_name, 'SKILL.md')
    
    if not os.path.exists(skill_md_path):
        # 列出可用的 skill 名称
        available = [d for d in os.listdir(SKILLS_BASE_PATH) 
                     if os.path.isdir(os.path.join(SKILLS_BASE_PATH, d))]
        return f"错误：skill '{skill_name}' 不存在。\n\n可用的 skills: {', '.join(available)}"
    
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return f"## {skill_name} 使用指南\n\n{content}"


# 3. 启动服务的入口
if __name__ == "__main__":
    # 以 stdio 模式运行（标准输入输出，用于与 AI 客户端通信）
    mcp.run()
