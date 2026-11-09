# STM32 固件代码生成专家团（stm32-fw-codegen）

从原理图网表到可编译的 STM32 + FreeRTOS 固件工程：外设模型、Jinja2 驱动模板、RTOS 与状态机架构、MISRA-C 安全审查、上板 OTA 验证。

**面向对象**：嵌入式软件工程师、硬件工程师、固件原型验证与教学场景。

## 类型

Team 型（多角色协作团队）

## 团队构成

| 成员 | Agent ID | 职责 |
|------|----------|------|
| Eva（主理人） | `stm32-fw-codegen-team-lead` | 判型、拆解、编排、裁决与汇编 |
| 文工 | `hw-schematic-analyst` | 网表/BOM 解析、引脚防冲突三层校验、hardware.yaml 草案 |
| 模板匠 | `fw-template-engineer` | 器件模型 YAML、Jinja2 驱动模板、CMake/链接脚本模板、USER CODE 保真 |
| 凯 | `rtos-architect` | FreeRTOS 任务划分、事件队列、状态机 DSL、低功耗策略、初始化排序 |
| 薇拉 | `fw-safety-reviewer` | 失效安全、ISR 并发正确性、时序预算、MISRA C:2012 / C99 审查（P0/P1/P2 分级） |
| 博 | `build-ota-verifier` | arm-none-eabi-gcc 构建、Unity+Mock HAL 单测、SIL、pyOCD 烧录取证、Bootloader A/B 与 FOTA 验证 |

## 领域来源

团队专业设定提炼自开源项目（MIT）：

- **hw2c**：https://github.com/jinliangliu/hw2c —— 从 EDA 设计文件（Netlist/BOM）自动生成可编译嵌入式固件的代码生成平台（六层 YAML、123+ Jinja2 模板、FreeRTOS 组件框架、双槽 Bootloader + 差分 FOTA）
- **hw2c-web**：https://github.com/jinliangliu/hw2c-web —— hw2c 的可视化配置前端（Vue 3 + FastAPI，拖拽任务编排、引脚封装预览、时钟树配置）

## 内置技能：ub-mode（工程纪律基线）

本专家团内置 [unclebob/ub-mode](https://github.com/unclebob/ub-mode) —— Robert C. Martin 发布的 agent 技能，用于约束「写代码 / 改代码」时的工程纪律。

- **位置**：`skills/ub-mode/SKILL.md`（上游逐字副本，未改动）
- **许可证**：MIT，Copyright (c) 2026 Robert C. Martin，全文见 `skills/ub-mode/LICENSE`
- **适配层**：`skills/ub-mode/references/embedded-adaptation.md` —— Cortex-M / MISRA C:2012 环境下的冲突消解
- **生效方式**：`plugin.json` 的 `skills` 声明 + 6 个 Agent 的 frontmatter `skills: [ub-mode]` 预加载。所有代码、模板、配置与测试改动默认遵循，**不只在用户显式输入 `/ub-mode` 时生效**

原则主线：First Make it Work → Then Make it Right → Practice（TDD、根因修复、CRAP < 10、去重、变异测试、动作日志、小步提交）。

### 三条覆盖原文的硬约束

| ub-mode 原文 | 本团队 |
|---|---|
| Commit and **Push** | 只提交不推送；未经用户明确确认不得 push |
| Worktree Cleanup / reclaim the disk | 只报告可清理项，不删除任何文件 |
| 使用 crapper / dryer / mutator | 这些是上游独立仓库、本包未内置；不可用时写「未执行」，**禁止编造分数** |

上游质量门工具在本包中由 cppcheck + MISRA + gcov + 圈复杂度检查替代，逐条映射见适配层。

## 内置技能：fw-lessons（事故 → 闸门）

把真实付过代价的失败，变成下次交付前能逐条勾选的闸门。方法借鉴一份工程事故复盘文档的「现象 → 根因 → 处置 → 怎么提前发现」四段式与其判据清单，移植到固件生成链路。

| 文件 | 内容 |
|---|---|
| `skills/fw-lessons/SKILL.md` | 四段式归因法、E0–E4 证据分级、闸门流程、新失败闭环回写、反模式 |
| `skills/fw-lessons/references/LESSONS.md` | 本团队真实事故档案，**按根因归类不按时间**；含「验证类假象」对照表、可复用验证手段、已知欠账、代价盘点 |
| `skills/fw-lessons/references/CRITERIA.md` | 编号判据清单，`Lxx` ↔ `Cxx` 互指，每条对应至少一次事故；附闸门结果表模板 |

**关键机制**

- **证据分级**：E0 推断 / E1 静态 / E2 主机执行 / E3 上板实测 / E4 独立回读。外部执行的返回值不能自证；E3+E4 为 0 时不得写「已上板验证」。
- **验证类假象**（最高优先级知识）：编译通过 ≠ 引脚配置正确、主机单测绿 ≠ 目标板正确、串口有输出 ≠ 调度正确、OTA success ≠ 双槽生效、本地 lint 全绿 ≠ 平台接受。
- **交付闸门**：主理人在 Phase 6 逐条标 PASS / FAIL / N/A；PASS 需证据路径，FAIL 不交付，N/A 进欠账表。已修复项**从欠账表删掉**，不做历史陈列。
- **闭环**：出现清单没拦住的新失败 → 追加 `Lxx` + 新增 `Cxx` + 编号互指。判断闭环是否完成的标准是：下次遇到同类现象，能否在清单里找到一条能提前拦住它的勾选框。

生效方式与 `ub-mode` 相同：`plugin.json` 的 `skills` 声明 + 6 个 Agent 的 frontmatter `skills: [ub-mode, fw-lessons]` 预加载。两者的分工是：**`ub-mode` 管代码怎么写，`fw-lessons` 管结果怎么证明、错了之后团队怎么变聪明**；冲突时以事实性约束优先。

## 作者

jinliang.liu — [GitHub @jinliangliu](https://github.com/jinliangliu)

## 许可证

MIT License，详见 [LICENSE](./LICENSE)。

## 使用示例

- 我有一个 STM32 板子（附原理图/网表），帮我生成一版可编译的 FreeRTOS 固件工程骨架，并把引脚、外设和任务都配置好。
- 帮我为一块新的 SPI Flash（或 IMU、温压传感器）写一套驱动模板 + 器件模型 + 主机侧单元测试，接入代码生成管线。
- 审查这份生成的固件源码：RTOS 任务划分、ISR 共享数据、中断标志清除、失效安全路径与 MISRA C:2012 合规性。

## 头像

头像已自动生成在 `avatars/` 目录下（512×512，均 <500KB）。如需替换为自定义头像，要求：
- 格式：PNG（推荐）或 JPG
- 尺寸：512×512 px
- 大小：单张不超过 500KB

## 安装

将专家包目录放到 WorkBuddy 专家目录下（默认 `~/.workbuddy/plugins/marketplaces/my-experts/plugins/`；若设置了 `WORKBUDDY_CONFIG_DIR`，则在其下）：

```
<WORKBUDDY_CONFIG_DIR>/plugins/marketplaces/my-experts/plugins/stm32-fw-codegen/
```

然后运行注册命令使其可见：

```bash
python3 scripts/register_expert.py <expert-dir>
```

## 打包分享

```bash
python3 scripts/package_expert.py <expert-dir>
```
