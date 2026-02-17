# 幽梦个人助手

![版本](https://img.shields.io/badge/版本-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-orange)
![许可证](https://img.shields.io/badge/许可证-MIT-yellow)

基于 PyQt5 的个人任务管理应用程序，支持日常任务、周常任务和特殊任务的智能管理与自动重置。采用 QQ 风格的现代化界面设计。

## 功能特性

### 任务管理
- **任务分类**：日常任务、周常任务、特殊任务三种类型
- **自动重置**：日常任务每日自动重置，周常任务每周自动重置
- **优先级系统**：四级优先级（紧急/优先/普通/建议），按钮式快速选择
- **标签系统**：多标签支持，灵活筛选和分类
- **任务详情**：支持标题、描述、要求等多字段

### 回收站
- 软删除机制，支持任务恢复
- 永久删除和清空回收站
- 颜色编码：7天内(橙色)、30天内(灰色)、30天以上(深灰)
- 可配置容量限制

### 界面特性
- QQ 风格浅蓝色主题（#12B7F5）
- 流畅的页面切换动画
- 顶部搜索栏（支持模糊/精确搜索）
- 可滑出的右侧详情面板（支持切换收回）
- 卡片式任务展示
- 边缘拖拽调整窗口大小
- 窗口位置和大小记忆

### 日志系统
- 按启动会话隔离日志目录
- 三级日志分离（app.log、error.log、debug.log）
- 7天自动清理旧日志

## 安装

### 方式一：安装包（推荐）

从 [Releases](../../releases) 页面下载最新的安装程序，运行即可完成安装。

### 方式二：从源码运行

**系统要求**：Python 3.7+

```bash
# 创建虚拟环境（推荐）
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

## 项目结构

```
YoumengPersonalAssistant/
├── main.py                     # 应用程序入口
├── requirements.txt            # Python 依赖
├── YoumengAssistant.spec       # PyInstaller 打包配置
├── installer.iss               # Inno Setup 安装脚本
├── build.bat                   # 一键打包脚本
├── config/
│   └── settings.py             # 配置管理模块
├── core/
│   ├── task_manager.py         # 任务管理器（业务逻辑）
│   └── auto_reset_service.py   # 自动重置服务
├── data/
│   ├── models.py               # 数据模型定义
│   ├── database.py             # 数据库连接管理
│   └── repository.py           # 数据仓库实现
├── ui/
│   ├── main_window.py          # 主窗口界面
│   ├── task_card.py            # 任务卡片组件
│   ├── task_dialog.py          # 任务对话框
│   ├── settings_dialog.py      # 设置对话框
│   ├── recycle_bin_dialog.py   # 回收站对话框
│   ├── animations/             # 动画效果
│   │   └── animation_manager.py
│   ├── components/             # 可复用组件
│   │   ├── animated_stacked_widget.py
│   │   ├── search_bar.py
│   │   ├── sliding_panel.py
│   │   ├── task_form_widget.py
│   │   └── settings_widget.py
│   └── styles/                 # 样式主题
│       └── qq_style.py
├── utils/
│   ├── logger.py               # 日志管理（LogManager）
│   ├── common.py               # 通用工具函数
│   ├── exceptions.py           # 自定义异常
│   └── resource.py             # 资源路径管理
└── resources/
    └── icons/                  # 应用图标资源
```

## 架构设计

项目采用分层架构：

| 层级 | 目录 | 职责 |
|------|------|------|
| 数据层 | `data/` | 数据模型、数据库操作、数据访问接口 |
| 业务层 | `core/` | 核心业务逻辑、自动重置服务 |
| 表示层 | `ui/` | 用户界面组件、动画、样式 |
| 工具层 | `utils/`, `config/` | 日志、配置等辅助模块 |

组件间通信使用 PyQt5 信号槽机制。

## 配置说明

配置文件 `config.json` 在首次运行时自动生成，主要配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `task.daily_reset_time` | 日常重置时间 | `06:00` |
| `task.weekly_reset_day` | 周常重置日（0=周一） | `0` |
| `task.auto_reset_enabled` | 启用自动重置 | `true` |
| `task.recycle_bin_capacity` | 回收站最大容量 | `100` |
| `ui.default_section` | 默认分区（0=日常，1=周常，2=特殊） | `0` |
| `ui.show_completed` | 显示已完成任务 | `true` |

## 数据库

使用 SQLite 数据库，主要数据表：

- `tasks` - 任务表（含 requirements、priority 字段）
- `tags` - 标签表
- `task_tags` - 任务-标签关联表
- `app_state` - 应用程序状态表

## 打包发布

### 打包 EXE

```bash
# 使用一键打包脚本
build.bat

# 或手动打包
pyinstaller YoumengAssistant.spec --clean
```

### 创建安装程序

1. 安装 [Inno Setup 6](https://jrsoftware.org/isdl.php)
2. 打开 `installer.iss`
3. 点击编译

输出路径：`installer_output/`

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

Copyright (c) 2026 幽梦工作室
