# workbuddy-experts

WorkBuddy 专家包（Expert / Expert Team）开源集合。仓库本身就是一个可加载的专家市场源，每个专家包独立放在 `plugins/<包名>/`，新增专家只需加目录并在清单里登记。

## 专家列表

| 包名 | 名称 | 类型 | 分类 | 版本 |
|---|---|---|---|---|
| [`mcp-dev-assistant`](plugins/mcp-dev-assistant) | MCP开发助手 | Team（4 角色） | 技术工程 | 1.0.0 |
| [`stm32-fw-codegen`](plugins/stm32-fw-codegen) | STM32 固件代码生成专家团 | Team（6 角色） | 技术工程 | 1.3.0 |

### mcp-dev-assistant · MCP开发助手

四角色专家团，覆盖 MCP 桥梁建设全流程：选型、Server 封装、Client 接入、协议联调排障。

| 角色 | 职责 |
|---|---|
| MCP 架构协调者（主理人） | 判断问题属于 Client、Server 还是协议层，编排协作，输出单一结论 |
| MCP Client 开发专家 | 握手与能力协商、`tools/call` 与结果解析、Sampling / Roots / Elicitation、三类客户端传输 |
| MCP Server 开发专家 | 工具 / 资源 / 提示定义、`inputSchema` 设计、三种传输的服务端实现、鉴权与安全硬化 |
| MCP 协议与调试专家 | JSON-RPC 消息层、版本协商、错误码语义、Inspector 与帧级取证、端到端验证 |

预设流程五条：E 选型与边界 / A 连不上调不通 / B 从零搭建 / C 上线前审查 / D 传输迁移与版本升级。详见 [该包 README](plugins/mcp-dev-assistant/README.md)。

### stm32-fw-codegen · STM32 固件代码生成专家团

六角色专家团，把原理图 / 网表变成可编译的 STM32 + FreeRTOS 固件工程：

| 角色 | 职责 |
|---|---|
| Eva（主理人） | 判型、拆解、编排、裁决，并在交付前过「事故 → 闸门」清单 |
| 文工 | 网表 / BOM 解析、引脚防冲突三层校验、`hardware.yaml` 草案 |
| 模板匠 | 器件模型 YAML、Jinja2 驱动模板、CMake / 链接脚本模板 |
| 凯 | FreeRTOS 任务划分、事件队列、状态机 DSL、初始化排序 |
| 薇拉 | 失效安全、ISR 并发、时序预算、MISRA C:2012 审查（P0/P1/P2） |
| 博 | 构建、主机单测、pyOCD 烧录取证、Bootloader A/B 与差分 FOTA 验证 |

内置两个技能：`ub-mode`（上游工程纪律基线 + 嵌入式适配层）与 `fw-lessons`（把真实事故提炼成 E0–E4 证据分级与交付判据）。详见 [该包 README](plugins/stm32-fw-codegen/README.md)。

领域知识提炼自开源项目 [hw2c](https://github.com/jinliangliu/hw2c) 与 [hw2c-web](https://github.com/jinliangliu/hw2c-web)。

## 安装

### 方式一：作为市场源

在 WorkBuddy 的专家市场设置中添加本仓库地址，清单见 [`.codebuddy-plugin/marketplace.json`](.codebuddy-plugin/marketplace.json)，安装其中任一专家。

### 方式二：本地复制 + 注册（推荐用于本机调试）

```bash
# 1. 复制某个专家包到本机市场
cp -r plugins/mcp-dev-assistant ~/.workbuddy/plugins/marketplaces/my-experts/plugins/

# 2. 注册到市场清单
python <WorkBuddy>/resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills/expert-manager/scripts/register_expert.py \
  ~/.workbuddy/plugins/marketplaces/my-experts/plugins/mcp-dev-assistant
```

注册后可在【专家中心 - 我的专家】看到该专家。

## 目录结构

```
workbuddy-experts/
├── .codebuddy-plugin/
│   └── marketplace.json          # 市场清单，每个专家在此登记一条
├── plugins/
│   ├── mcp-dev-assistant/        # 一个专家包 = 一个目录
│   └── stm32-fw-codegen/
│       ├── .codebuddy-plugin/plugin.json
│       ├── agents/               # 每角色一个 MD，文件名 = agentName / members[].id
│       ├── avatars/              # 512×512 PNG，≤500KB
│       ├── skills/               # 内置技能（ub-mode / fw-lessons）及其 references/
│       ├── settings.json         # Team 型必需，agent = 主理人 id
│       ├── LICENSE
│       └── README.md
├── scripts/
│   └── lint_expert.py            # 深度校验：字段、头像、市场死链
├── CONTRIBUTING.md               # 新增专家的规范与骨架
├── LICENSE
└── README.md
```

## 新增专家

1. 在 `plugins/` 下新建 kebab-case 目录
2. 按 [CONTRIBUTING.md](CONTRIBUTING.md) 填写 `plugin.json`、`agents/*.md`、`avatars/*.png`
3. 在 `.codebuddy-plugin/marketplace.json` 的 `plugins` 数组追加条目
4. 跑 `python scripts/lint_expert.py plugins/<包名> --marketplace .`，零错误再提交

## 许可

本仓库整体为 [MIT](LICENSE)，Copyright (c) 2026 jinliang.liu。

第三方组件署名：

| 组件 | 许可 | 说明 |
|---|---|---|
| `plugins/stm32-fw-codegen/skills/ub-mode/SKILL.md` | MIT © 2026 Robert C. Martin | 上游 [unclebob/ub-mode](https://github.com/unclebob/ub-mode) 逐字副本；许可全文见同目录 `LICENSE`。嵌入式适配层 `references/embedded-adaptation.md` 为本仓库原创 |
| `hw2c` / `hw2c-web` | MIT | 领域知识来源，代码未随本仓库分发 |
| `plugins/*/avatars/*.png` | 同仓库 MIT | 为各角色生成的头像 |

`fw-lessons` 为本仓库原创，方法借鉴通用工程事故复盘实践，不含第三方受版权保护的内容。
