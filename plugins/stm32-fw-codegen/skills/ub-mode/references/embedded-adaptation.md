# ub-mode 在 STM32 固件生成团队中的适配说明

## 0. 定位与效力

- `../SKILL.md` 是上游 [unclebob/ub-mode](https://github.com/unclebob/ub-mode) 的**逐字副本**，未作任何改动。MIT 许可证见 `../LICENSE`，版权归 Robert C. Martin（2026）。
- 本文件是**适配层**，不是对上游的改写。ub-mode 面向通用软件工程；本团队面向 Cortex-M / FreeRTOS / MISRA C:2012 的**模板生成固件**，两者有真实冲突。
- **效力顺序**：目标平台可编译性与安全性 > MISRA C:2012 Mandatory > 团队既有工程铁律 > 本适配层 > ub-mode 原文。冲突时按下表消解，并把消解理由写进交付日志。
- **适用范围**：本专家团内，`ub-mode` 是**所有代码、模板、配置与测试改动的默认工程纪律基线**，不只在用户显式输入 `/ub-mode` 时才生效。

## 1. 逐条映射与冲突消解

| ub-mode 条目 | 在本团队中的落地 | 冲突/限制 |
|---|---|---|
| **Fix Root Causes** | 缺陷必须回溯到 `templates/*.j2` 的生成位置；**修生成产物是错的**，修复落在上游模板 | 与团队既有铁律完全一致，优先级最高 |
| **TDD** | 主机侧 Unity + Mock-HAL 先写失败用例，看到**预期原因**的失败再改模板 | ISR / 中断使能 / 备份域 / 标志清除在 `TEST` 构建中是空桩，主机侧**结构上覆盖不到** → 必须声明"需上板验证"，**不得伪造绿灯** |
| **If an honest test is impractical, do not write a bad one** | mock 必须复刻生产语义（含大小写敏感的 `strcmp` 总线名匹配） | 曾经踩过：mock 按名字动态创建总线、不区分大小写 → 单测全绿但目标板确定性失败。宁可标注"未覆盖"，不写假测试 |
| **Crapper（CRAP < 10）** | 映射到 cppcheck / lizard 圈复杂度 + gcov 覆盖率；需求基准 NFR-3：单函数 ≤ 100 行、圈复杂度 ≤ 10 | `unclebob/crapper` 是独立仓库，**本包不内置、不假设已安装**。工具不可用时如实写"未执行"，不得报数 |
| **Dryer（重复 ≥ 0.8）** | 检查 `templates/*.j2` 之间的重复块，合并前先确认渲染上下文等价 | `unclebob/dryer` 未内置；手工查重即可，不谎报排名 |
| **Mutator（变异测试）** | 主机侧 C 代码可用；目标板裸机/RTOS 路径**不适用** | `unclebob/mutator` 未内置。不适用于 ISR 与硬件寄存器访问路径，明确声明 |
| **Test Behavior, Not Implementation** | 测组件对外行为（总线读写结果、状态机迁移结果），不测内部静态函数 | 与"取证诚实性"一致 |
| **Separate Before Serializing Shared State / 单写者** | ISR 与任务不共享可变 GPIO 状态；读-改-写必须有唯一写者并在结构上强制 | 直接对应团队 ISR 并发铁律；ISR 必须清掉负责的**全部**标志 |
| **Make Operations Idempotent** | 组件 `init` 可重复调用；双槽 Bootloader A/B 与差分 FOTA 中途断电后状态可恢复 | 与 OTA 验证职责一致 |
| **Model the Domain / Boundary Discipline / Get the data shape right** | 六层 YAML（hardware/task/components/bind/params/pubsub）在入口校验；业务状态机保持纯迁移函数 | 配置解析**不得静默退出**：不夹取值、不 `except: pass`，派生值必须可在管线中段观测 |
| **Type System Discipline / Do not silence the compiler** | 用 `-Wall -Wextra` 严格告警集；`-std=c99` 与默认标准**分别编译并比对** | 但不得为"让非法值写不出来"引入语言扩展 → 违反 MISRA Dir 4.1 / Rule 1.2。MISRA 优先 |
| **Subtract Before You Add / Laziness Protocol** | 优先减模板分支，不为单个器件扩分支 | Cortex-M0+ 无 FPU、无硬件除法加速、不支持非对齐访问；**禁止**为抽象引入堆分配、动态分发、浮点格式化 |
| **Attack the Premise** | 多个修复反复卡在同一道门时，先写出共同前提再动手 | 历史教训：FreeRTOS ARMv6-M `ulCriticalNesting` 的毒值 `0xAAAAAAAA` 必须靠**初始化顺序**修，不是逐处打补丁 |
| **Keep a Log / Sequence into verifiable units** | 主理人每阶段向用户通报，最终交付动作日志与理由；每个 SOP Phase 独立验收 | 与团队 SOP 一致 |
| **Guard the Context Window** | 大段源码/网表交给成员分析，主理人只留摘要与结论 | 与 Team 编排一致 |

## 2. 三条硬约束（覆盖 ub-mode 原文）

ub-mode 原文里有三条在本团队**不适用或被收紧**，必须按下述执行：

1. **Commit and Push → 只提交，不推送。** 原文「Push to the main line at the end」改为：提交到本地主线并在日志里报告 commit；**未经用户明确确认，不得 `git push`、不得向任何远端或平台执行发布动作**。仓库可能没有 remote，此时只报告「未配置远端」。
2. **Worktree Cleanup → 只报告，不删除。** 原文「then reclaim the disk」改为：列出可清理项与判断依据，**不删除、不移动、不重命名任何文件**。任何删除须用户逐项明确确认。
3. **质量门工具 → 不谎报。** crapper / dryer / mutator / uml-viewer 均为上游独立仓库，本包未内置。未安装就写「工具不可用，该项未执行」；**禁止编造 CRAP 分数、重复率、变异得分**。

## 3. 排除范围

- **vendor 源码只读**：芯片 HAL / CMSIS / FreeRTOS-Kernel / Unity / lwrb 等第三方代码不参与 ub-mode 的重构、去重、TDD 与合规判定。`static/stm32g0/` 下内容不得改动。
- **硬件事实不得用"减法"消掉**：引脚、电源域、时钟、寄存器约束来自原理图与数据手册，不是可重构的抽象。ub-mode 的 "Subtract Before You Add" 不适用于硬件能力模型。
- **上板验证不可替代**：任何涉及真实时序、中断、模拟量、功耗的结论，主机侧结果只是证据之一，最终结论必须标注上板状态。

## 4. 成员分工对应

| 成员 | 主要承接的 ub-mode 原则 |
|---|---|
| `hw-schematic-analyst` | Get the data shape right / Boundary Discipline / Maintain a glossary |
| `fw-template-engineer` | Laziness Protocol / Build the Lever / Fix Root Causes（模板层）/ TDD |
| `rtos-architect` | Separate Before Serializing Shared State / 单写者 / Idempotent init |
| `fw-safety-reviewer` | Crapper / Dryer / Mutator 的替代判据 / Test Behavior / 取证诚实性 |
| `build-ota-verifier` | Sequence into verifiable units / 可复现证据 / 不谎报质量门 |
| `stm32-fw-codegen-team-lead` | Keep a Log / Guard the Context Window / 全阶段纪律裁决 |

## 5. 交付日志模板

每次任务结束，主理人在报告末尾附：

```
## ub-mode 执行日志
- 变更单元：（逐个可验证单元，含验收方式）
- TDD：写了哪些失败用例 / 失败原因是否符合预期 / 哪些因硬件依赖标为「需上板验证」
- 质量门：cppcheck / MISRA / 覆盖率 —— 实际执行命令与结果；不可用的工具明确列出
- 根因回溯：改了哪些 templates/*.j2，未改哪些生成产物
- 冲突消解：ub-mode 与本适配层/ MISRA / 平台约束冲突处及理由
- 提交：commit 列表（why / what / how proved）；是否 push（默认：否）
```
