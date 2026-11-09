# MCP开发助手

覆盖 MCP Client、Server 与协议调试的四角色技术团队，先判断问题归属，再给可落地的代码与排查路径。

## 类型

Team 型（多角色协作团队）

## 成员

| Agent ID | 名字 | 角色 | 职责 |
|---|---|---|---|
| `mcp-dev-assistant-team-lead` | Emmet Ward | MCP 架构协调者 | 判断问题归属 Client / Server / 协议层，编排协作，汇编最终方案 |
| `mcp-client-dev` | Anton Bridges | MCP Client 开发专家 | 连接生命周期、能力协商、工具调用、Sampling / Roots / Elicitation、三类传输的客户端实现 |
| `mcp-server-dev` | Forman Steele | MCP Server 开发专家 | 工具 / 资源 / 提示定义、JSON Schema 设计、三种传输的服务端实现、安全硬化 |
| `mcp-protocol-debug` | Anthea Tracey | MCP 协议与调试专家 | JSON-RPC 消息层、版本协商、错误码语义、Inspector 与日志取证、端到端验证 |

花名统一为英文，取「名含蚂蚁、姓含职能」的构造：Emmet（古英语「蚂蚁」）Ward（分区守护，对应归属判定），Anton（ant）Bridges（桥接连接），Forman（formica 蚁属／foreman 工头）Steele（钢构基座），Anthea（ant）Tracey（谐 trace，逐帧追踪取证）。

## 功能

- **接通前选型**：判定桥该做在 Server 侧、Client 侧还是两端，划清 Host / Client / Server 职责，给出能力暴露清单与「不做什么」
- **双向归因诊断**：连不上、调不通、偶发超时时，先从协议层判断故障层级，再分头查 Client 与 Server，最后由协议专家交叉比对出单一结论，避免两头乱改
- **从零搭建**：Server 侧给能力暴露判定、Schema、最小骨架、鉴权 / 限流 / 幂等约束与安全清单；Client 侧给接入配置与调用示例；协议侧给联调验证用例
- **上线前审查**：工具权限最小化、输入校验、越权与 SSRF / 命令注入 / 路径穿越、容器与沙箱隔离、调用审计、协议合规性与错误码规范
- **传输迁移**：SSE → Streamable HTTP、protocolVersion 升级的改造成本、双栈共存、灰度顺序与回滚预案
- **版本与规范辨析**：明确区分「MCP 规范强制要求」与「某 SDK 的约定」，标注 stdio / SSE / Streamable HTTP 的演进差异

## 适用与不适用

**适合**

- 需要把内部业务系统安全、可控地暴露给智能体，但先要定「桥做在哪一侧」
- 需要为智能体接入多个 MCP Server，并统一鉴权与传输方式
- 需要设计工具 Schema、能力暴露清单、传输选型与鉴权模型
- 需要排查 MCP 端到端联调问题（握手、能力协商、会话过期、事件丢失、调用超时）
- 需要在明确安全边界内推进 MCP 桥梁落地的团队

**不适合**

- 指望它替你做业务决策：该暴露哪些接口、哪些字段可给模型看、权限口径怎么定，必须由你拍板
- 指望一键生成可上线的系统：产出是方案、代码片段与排查路径，接入你们 CI/CD、监控、密钥管理仍由团队完成
- 不提供业务上下文却要求精准集成方案：没有对象模型与权限体系，任何 Schema 设计都是猜的
- 与 MCP 无关的问题：LLM 应用自身的 prompt 工程、非 MCP 的 RPC 框架、前端框架选型

## 使用示例

- 「我们有个内部工单系统，想接进 Agent，该包 Server 还是写 Client 适配」
- 「这些接口该怎么暴露？哪些做成 Tool，哪些留业务侧」
- 「我的 MCP Client 连不上 SSE Server，帮我判断问题在哪一侧」
- 「用 TypeScript SDK 写一个带参数校验和错误处理的 MCP Server 工具」
- 「Streamable HTTP 和 SSE 该怎么选？给我选型依据和部署注意事项」
- 「tools/call 一直 pending，日志里什么都没有」
- 「这套 MCP 服务能上生产吗？帮我审一下工具权限和安全边界」
- 「现有 SSE Server 要迁到 Streamable HTTP，存量客户端怎么平滑过渡」

## 工作方式

主理人先做归属判断：单点问题直调对应成员，跨端问题走五条预设 Workflow——A 连不上 / 调不通、B 从零搭建、C 上线前审查、D 传输迁移与版本升级、E 接通前的选型与边界划定；三阶段串并行编排后统一输出「结论 → 步骤 → 代码 → 注意事项」。

**Workflow E 是新建桥梁的入口**：选型未定时不会直接给 Server 骨架，避免默认了「只做 Server」这个答案。

## 使用建议

两条建议本质是同一件事：**主动减少可选分支**。MCP 的答案空间很大（三种传输 × 两套 SDK × 多个协议版本 × 多种部署形态），不收敛就会答得面面俱到但不可用。

### 建议一：场景偏某一侧时，压缩角色

如果你的场景明显偏一侧（例如内部只做 Server，不自己维护 Client），不必保留完整四人配置：

- **保留主理人**（Emmet Ward）作为唯一入口，负责归属判定与汇编
- **把用不上的角色降级为「必要时咨询」**：在 `agents/mcp-dev-assistant-team-lead.md` 的 SOP 中，把对应 Phase 改成条件调度，例如「仅当结论需要客户端侧取证时才调度 `mcp-client-dev`」；路由表里对应行也标注为可选
- **或直接移除**：同步删除 `plugin.json` 的 `agents` 数组项、`teamInfo.memberAgents`、`members` 数组项、`settings.json` 不受影响

效果：主理人 prompt 中的成员清单、路由表、SOP 阶段全部变短，模型注意力集中到真正会用到的一部分能力上，减少无关分支。**注意 `members` 至少保留一条 `role: "lead"`**，改完必须重新校验并注册：

```bash
python scripts/validate_expert.py <expert-dir>
python scripts/register_expert.py <expert-dir>
```

### 建议二：固定技术栈时，钉死版本与传输

如果团队有固定技术栈（如 TypeScript SDK + Streamable HTTP），把这层约束写进角色描述，而不是每轮对话口头交代：

- **钉在四份 MD 的「参考实现要点」开头**，例如：「本项目固定使用 `@modelcontextprotocol/sdk` 1.x + Streamable HTTP，不得建议 SSE 方案或切换传输」
- **一并钉死**：SDK 与版本、传输方式、部署形态（单机进程 / 容器 / 多副本）、运行时版本（Node LTS / Python 3.x）
- **效果**：省掉每轮「你用的是哪个 SDK、哪种传输」的追问；成员不再输出三传输横向对比，只给一条可执行路径；主理人也不再把多选题当结论

钉得越死，回答越准；代价是这套专家只适用于该技术栈。

### 建议三：长期维持偏侧配置时，另存一份

不要直接改原包。复制一份目录、改 `plugin.json` 的 `name` 与 `plugin` 字段、重命名主理人 MD 并同步 `agentName` / `settings.json`，作为团队专用版本；原包保留完整四人配置，供跨端问题使用。

## 头像

头像已自动生成在 `avatars/` 目录下，同一团队统一画风。如需替换：
- 格式：PNG（推荐）或 JPG
- 尺寸：512×512 px
- 大小：单张不超过 500KB

## 注册

```bash
python scripts/register_expert.py <expert-dir>
```

## 打包分享

```bash
python scripts/package_expert.py <expert-dir>
```
