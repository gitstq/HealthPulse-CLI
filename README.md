<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version" />
  <img src="https://img.shields.io/badge/python-3.8%2B-green.svg" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License" />
  <img src="https://img.shields.io/badge/dependencies-0-purple.svg" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/rules-61-yellow.svg" alt="61 Rules" />
  <img src="https://img.shields.io/badge/dimensions-8-cyan.svg" alt="8 Dimensions" />
  <img src="https://img.shields.io/badge/languages-14-informational.svg" alt="14 Languages" />
</p>

<p align="center">
  <a href="#-项目介绍">简体中文</a> &nbsp;|&nbsp;
  <a href="#-繁體中文版本">繁體中文</a> &nbsp;|&nbsp;
  <a href="#-english-version">English</a>
</p>

---

# 🩺 HealthPulse-CLI

> 轻量级终端代码仓库健康度智能诊断引擎 | Lightweight Terminal Code Repository Health Diagnosis Engine

---

<a id="-项目介绍"></a>

## 🎉 项目介绍

**HealthPulse-CLI** 是一款零外部依赖的终端代码仓库健康度诊断引擎。它通过 **8 大分析维度** 和 **61 条诊断规则**，对代码仓库进行全面体检，输出 0-100 的健康评分及字母等级（A+ ~ F），帮助开发者快速定位代码质量问题。

无论你是个人开发者还是团队协作，HealthPulse-CLI 都能在几秒内完成对代码仓库的全面诊断，并以 **彩色终端仪表盘、JSON、HTML 网页报告、Markdown** 四种格式呈现结果。

### 一句话概述

```
pip install . && healthpulse scan ./your-project
```

仅需一行命令，即可获得代码仓库的全面健康报告。

<a id="-繁體中文版本"></a>

---

## 🏯 繁體中文版本

### 🎉 專案介紹

**HealthPulse-CLI** 是一款零外部依賴的終端程式碼倉庫健康度診斷引擎。它透過 **8 大分析維度** 和 **61 條診斷規則**，對程式碼倉庫進行全面體檢，輸出 0-100 的健康評分及字母等級（A+ ~ F），幫助開發者快速定位程式碼品質問題。

無論你是個人開發者還是團隊協作，HealthPulse-CLI 都能在幾秒內完成對程式碼倉庫的全面診斷，並以 **彩色終端儀表盤、JSON、HTML 網頁報告、Markdown** 四種格式呈現結果。

### ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🔍 **8 大分析維度** | 複雜度、重複率、命名、安全、架構、文檔、可維護性、效能 |
| 📋 **61 條診斷規則** | 涵蓋 critical / warning / info / hint 四級嚴重度 |
| 🌐 **14 種語言支援** | Python、JavaScript、TypeScript、Go、Rust、Java、Ruby、PHP、Kotlin、Swift、Scala、Shell、C、C++ |
| 📊 **4 種輸出格式** | TUI 彩色儀表盤、JSON、HTML 網頁報告、Markdown |
| 🚫 **零外部依賴** | 純 Python 標準庫實現，無需安裝任何第三方套件 |
| 🏥 **健康評分系統** | 0-100 分 + A+ ~ F 字母等級 |
| 🔄 **CI/CD 整合** | 可配置健康分數閾值，自動判定構建通過/失敗 |
| ⚙️ **靈活配置** | 支援 `.healthpulse.json` 配置檔案，自訂權重與規則 |

### 🚀 快速開始

```bash
# 從原始碼安裝
git clone https://github.com/your-org/healthpulse-cli.git
cd healthpulse-cli
pip install .

# 或不安裝直接運行
PYTHONPATH=src python3 -m healthpulse
```

```bash
# 掃描當前目錄
healthpulse scan .

# 掃描指定目錄
healthpulse scan ./my-project

# 生成 HTML 報告
healthpulse report ./my-project --format html -o health.html

# CI 模式：健康分數低於閾值則退出碼非零
healthpulse scan . --ci --threshold 70
```

### 📖 詳細使用指南

#### CLI 指令一覽

| 指令 | 說明 | 範例 |
|------|------|------|
| `scan` | 掃描倉庫並診斷健康度 | `healthpulse scan ./src` |
| `report` | 生成詳細健康報告 | `healthpulse report . --format html` |
| `rules` | 查看或檢視診斷規則 | `healthpulse rules list` |
| `config` | 查看或修改配置 | `healthpulse config show` |
| `init` | 初始化配置檔案 | `healthpulse init` |

#### 掃描選項

```bash
healthpulse scan <path> [options]

選項：
  -l, --language <lang>      目標語言 (auto/python/js/ts/go/rust/java)
  -f, --format <format>      輸出格式 (tui/json/html/markdown)
  -o, --output <path>        將輸出儲存至檔案
  -r, --rules <rules>        啟用特定規則（逗號分隔）
  -x, --exclude <patterns>   排除模式（逗號分隔）
  -v, --verbose              顯示詳細輸出
  -q, --quiet                僅顯示健康分數
  --no-color                 停用顏色
  --ci                       CI 模式（退出碼 = 健康狀態）
  --threshold <score>        最低健康分數（預設：60）
```

#### 8 大分析維度

| 維度 | 權重 | 說明 |
|------|------|------|
| 🔴 Security | 1.2 | 安全漏洞檢測（eval、硬編碼密碼、注入風險等） |
| 🟡 Complexity | 1.0 | 代碼複雜度分析（深層嵌套、圈複雜度、長函數等） |
| 🟡 Duplication | 1.0 | 代碼重複檢測（重複區塊、相似模式等） |
| 🟡 Maintainability | 1.0 | 可維護性評估（TODO/FIXME/HACK、長行等） |
| 🟠 Architecture | 0.9 | 架構品質評估（大檔案、扁平目錄、高耦合等） |
| 🔵 Naming | 0.8 | 命名規範檢查（命名約定、命名品質等） |
| 🔵 Performance | 0.8 | 效能問題檢測（字串拼接、低效迭代等） |
| 🟢 Documentation | 0.7 | 文檔覆蓋率評估（README、LICENSE、註釋等） |

#### 健康評分等級

| 分數區間 | 等級 | 含義 |
|----------|------|------|
| 90-100 | A+ | 優秀 |
| 85-89 | A | 優良 |
| 80-84 | A- | 良好 |
| 75-79 | B+ | 中上 |
| 70-74 | B | 中等偏上 |
| 65-69 | B- | 中等 |
| 60-64 | C+ | 及格 |
| 55-59 | C | 需要改進 |
| 50-54 | C- | 較差 |
| 40-49 | D | 不及格 |
| 0-39 | F | 極差 |

#### CI/CD 整合

```yaml
# GitHub Actions 範例
- name: Health Check
  run: |
    pip install .
    healthpulse scan . --ci --threshold 70 --format json -o report.json
```

```yaml
# GitLab CI 範例
health_check:
  script:
    - pip install .
    - PYTHONPATH=src python3 -m healthpulse scan . --ci --threshold 65
```

#### 配置檔案

執行 `healthpulse init` 將在當前目錄生成 `.healthpulse.json` 配置檔案：

```json
{
  "version": "1.0",
  "language": "auto",
  "threshold": 60,
  "exclude": [
    "node_modules", ".git", "__pycache__", ".venv",
    "dist", "build", ".next", ".cache", "coverage"
  ],
  "rules": {
    "enabled": "all",
    "disabled": []
  },
  "dimensions": {
    "complexity": { "weight": 1.0 },
    "duplication": { "weight": 1.0 },
    "naming": { "weight": 0.8 },
    "security": { "weight": 1.2 },
    "architecture": { "weight": 0.9 },
    "documentation": { "weight": 0.7 },
    "maintainability": { "weight": 1.0 },
    "performance": { "weight": 0.8 }
  },
  "ci": {
    "enabled": false,
    "threshold": 60
  }
}
```

### 💡 設計思路與迭代規劃

#### 設計理念

- **零依賴原則**：純 Python 標準庫實現，降低使用門檻，避免依賴衝突
- **多維度評估**：不僅僅關注某一個方面，而是從 8 個維度全面評估代碼健康度
- **多語言支援**：一套引擎支援 14 種主流程式語言，統一的健康評估標準
- **CI 友好**：原生支援 CI/CD 整合，退出碼反映健康狀態
- **可擴展架構**：分析器、規則註冊表、報告器均採用模組化設計，易於擴展

#### 迭代規劃

- **v1.1**：增加 Git 歷史分析（提交頻率、代碼變更趨勢）
- **v1.2**：增加自訂規則支援（YAML/JSON 規則定義）
- **v2.0**：增加 SARIF 格式輸出，支援 VS Code 擴展整合
- **v2.1**：增加基線比對功能，追蹤健康度變化趨勢

### 📦 安裝與部署

#### 系統要求

- Python 3.8 或更高版本
- pip（Python 套件管理器）

#### 安裝方式

```bash
# 方式一：從原始碼安裝（推薦）
git clone https://github.com/your-org/healthpulse-cli.git
cd healthpulse-cli
pip install .

# 方式二：不安裝，直接運行
cd healthpulse-cli
PYTHONPATH=src python3 -m healthpulse scan ./my-project

# 方式三：開發模式安裝
pip install -e .
```

#### 驗證安裝

```bash
healthpulse --version
# 輸出：HealthPulse-CLI v1.0.0

healthpulse help
# 顯示完整幫助資訊
```

### 🤝 貢獻指南

我們歡迎並感謝所有形式的貢獻！

#### 貢獻流程

1. **Fork** 本倉庫
2. 建立功能分支：`git checkout -b feature/your-feature`
3. 提交變更：`git commit -m 'feat: add your feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

#### 新增分析規則

在 `src/healthpulse/rules/registry.py` 中註冊新規則：

```python
Rule(
    rule_id='HP1XX',           # 規則 ID
    name='Rule Name',          # 規則名稱
    category='category',       # 所屬維度
    severity='warning',        # 嚴重度：critical/warning/info/hint
    description='描述',         # 規則描述
    languages=['python'],      # 適用語言
    suggestion='建議',          # 修復建議
)
```

#### 新增分析器

1. 在 `src/healthpulse/analyzers/` 下建立新的分析器模組
2. 實現 `analyze()` 和 `calculate_score()` 方法
3. 在 `engine.py` 中註冊分析器

### 📄 開源協議

本項目基於 [MIT License](LICENSE) 開源。

```
MIT License
Copyright (c) 2026 HealthPulse Team
```

---

<a id="-english-version"></a>

## 🇬🇧 English Version

### 🎉 Project Introduction

**HealthPulse-CLI** is a zero-dependency terminal code repository health diagnosis engine. It performs comprehensive health checks through **8 analysis dimensions** and **61 diagnosis rules**, outputting a 0-100 health score with letter grades (A+ ~ F), helping developers quickly identify code quality issues.

Whether you are an individual developer or part of a team, HealthPulse-CLI can complete a full diagnosis of your codebase in seconds, presenting results in **4 output formats**: colored TUI dashboard, JSON, HTML web report, and Markdown.

### One-liner

```bash
pip install . && healthpulse scan ./your-project
```

A single command to get a comprehensive health report for your codebase.

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔍 **8 Analysis Dimensions** | Complexity, Duplication, Naming, Security, Architecture, Documentation, Maintainability, Performance |
| 📋 **61 Diagnosis Rules** | Covering 4 severity levels: critical / warning / info / hint |
| 🌐 **14 Language Support** | Python, JavaScript, TypeScript, Go, Rust, Java, Ruby, PHP, Kotlin, Swift, Scala, Shell, C, C++ |
| 📊 **4 Output Formats** | Colored TUI Dashboard, JSON, HTML Web Report, Markdown |
| 🚫 **Zero Dependencies** | Pure Python standard library, no third-party packages needed |
| 🏥 **Health Score System** | 0-100 score + A+ ~ F letter grade |
| 🔄 **CI/CD Integration** | Configurable health score threshold with automatic pass/fail |
| ⚙️ **Flexible Configuration** | `.healthpulse.json` config file with custom weights and rules |

### 🚀 Quick Start

```bash
# Install from source
git clone https://github.com/your-org/healthpulse-cli.git
cd healthpulse-cli
pip install .

# Or run without installing
PYTHONPATH=src python3 -m healthpulse
```

```bash
# Scan current directory
healthpulse scan .

# Scan a specific directory
healthpulse scan ./my-project

# Generate HTML report
healthpulse report ./my-project --format html -o health.html

# CI mode: non-zero exit code if health score below threshold
healthpulse scan . --ci --threshold 70
```

### 📖 Detailed Usage Guide

#### CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `scan` | Scan repository and diagnose health | `healthpulse scan ./src` |
| `report` | Generate detailed health report | `healthpulse report . --format html` |
| `rules` | List or inspect diagnosis rules | `healthpulse rules list` |
| `config` | View or modify configuration | `healthpulse config show` |
| `init` | Initialize configuration file | `healthpulse init` |

#### Scan Options

```bash
healthpulse scan <path> [options]

Options:
  -l, --language <lang>      Target language (auto/python/js/ts/go/rust/java)
  -f, --format <format>      Output format (tui/json/html/markdown)
  -o, --output <path>        Save output to file
  -r, --rules <rules>        Enable specific rules (comma-separated)
  -x, --exclude <patterns>   Exclude patterns (comma-separated)
  -v, --verbose              Show verbose output
  -q, --quiet                Only show health score
  --no-color                 Disable colors
  --ci                       CI mode (exit code = health status)
  --threshold <score>        Min health score (default: 60)
```

#### 8 Analysis Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| 🔴 Security | 1.2 | Security vulnerability detection (eval, hardcoded passwords, injection risks, etc.) |
| 🟡 Complexity | 1.0 | Code complexity analysis (deep nesting, cyclomatic complexity, long functions, etc.) |
| 🟡 Duplication | 1.0 | Code duplication detection (duplicate blocks, similar patterns, etc.) |
| 🟡 Maintainability | 1.0 | Maintainability assessment (TODO/FIXME/HACK, long lines, etc.) |
| 🟠 Architecture | 0.9 | Architecture quality assessment (large files, flat directories, high coupling, etc.) |
| 🔵 Naming | 0.8 | Naming convention checks (naming conventions, name quality, etc.) |
| 🔵 Performance | 0.8 | Performance issue detection (string concatenation, inefficient iteration, etc.) |
| 🟢 Documentation | 0.7 | Documentation coverage assessment (README, LICENSE, comments, etc.) |

#### Health Score Grades

| Score Range | Grade | Meaning |
|-------------|-------|---------|
| 90-100 | A+ | Excellent |
| 85-89 | A | Great |
| 80-84 | A- | Good |
| 75-79 | B+ | Above Average |
| 70-74 | B | Above Average |
| 65-69 | B- | Average |
| 60-64 | C+ | Passing |
| 55-59 | C | Needs Improvement |
| 50-54 | C- | Below Average |
| 40-49 | D | Failing |
| 0-39 | F | Critical |

#### CI/CD Integration

```yaml
# GitHub Actions example
- name: Health Check
  run: |
    pip install .
    healthpulse scan . --ci --threshold 70 --format json -o report.json
```

```yaml
# GitLab CI example
health_check:
  script:
    - pip install .
    - PYTHONPATH=src python3 -m healthpulse scan . --ci --threshold 65
```

#### Configuration File

Run `healthpulse init` to generate a `.healthpulse.json` configuration file:

```json
{
  "version": "1.0",
  "language": "auto",
  "threshold": 60,
  "exclude": [
    "node_modules", ".git", "__pycache__", ".venv",
    "dist", "build", ".next", ".cache", "coverage"
  ],
  "rules": {
    "enabled": "all",
    "disabled": []
  },
  "dimensions": {
    "complexity": { "weight": 1.0 },
    "duplication": { "weight": 1.0 },
    "naming": { "weight": 0.8 },
    "security": { "weight": 1.2 },
    "architecture": { "weight": 0.9 },
    "documentation": { "weight": 0.7 },
    "maintainability": { "weight": 1.0 },
    "performance": { "weight": 0.8 }
  },
  "ci": {
    "enabled": false,
    "threshold": 60
  }
}
```

### 💡 Design Philosophy & Roadmap

#### Design Philosophy

- **Zero Dependency Principle**: Pure Python standard library implementation, lowering the barrier to entry and avoiding dependency conflicts
- **Multi-dimensional Assessment**: Not limited to a single aspect; evaluates code health from 8 comprehensive dimensions
- **Multi-language Support**: A single engine supporting 14 mainstream programming languages with a unified health assessment standard
- **CI-Friendly**: Native CI/CD integration with exit codes reflecting health status
- **Extensible Architecture**: Modular design for analyzers, rule registry, and reporters, making it easy to extend

#### Roadmap

- **v1.1**: Git history analysis (commit frequency, code change trends)
- **v1.2**: Custom rule support (YAML/JSON rule definitions)
- **v2.0**: SARIF format output, VS Code extension integration
- **v2.1**: Baseline comparison feature, health score trend tracking

### 📦 Installation & Deployment

#### System Requirements

- Python 3.8 or higher
- pip (Python package manager)

#### Installation Methods

```bash
# Method 1: Install from source (recommended)
git clone https://github.com/your-org/healthpulse-cli.git
cd healthpulse-cli
pip install .

# Method 2: Run without installing
cd healthpulse-cli
PYTHONPATH=src python3 -m healthpulse scan ./my-project

# Method 3: Development mode installation
pip install -e .
```

#### Verify Installation

```bash
healthpulse --version
# Output: HealthPulse-CLI v1.0.0

healthpulse help
# Display full help information
```

### 🤝 Contributing

We welcome and appreciate contributions of all forms!

#### Contribution Workflow

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push the branch: `git push origin feature/your-feature`
5. Submit a **Pull Request**

#### Adding a New Rule

Register a new rule in `src/healthpulse/rules/registry.py`:

```python
Rule(
    rule_id='HP1XX',           # Rule ID
    name='Rule Name',          # Rule name
    category='category',       # Dimension category
    severity='warning',        # Severity: critical/warning/info/hint
    description='Description',  # Rule description
    languages=['python'],      # Applicable languages
    suggestion='Suggestion',   # Fix suggestion
)
```

#### Adding a New Analyzer

1. Create a new analyzer module in `src/healthpulse/analyzers/`
2. Implement `analyze()` and `calculate_score()` methods
3. Register the analyzer in `engine.py`

### 📄 License

This project is licensed under the [MIT License](LICENSE).

```
MIT License
Copyright (c) 2026 HealthPulse Team
```

---

<p align="center">
  <sub>Built with ❤️ by HealthPulse Team | Powered by Python Standard Library</sub>
</p>
