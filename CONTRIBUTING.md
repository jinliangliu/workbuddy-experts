# 贡献指南

本仓库是专家包集合，一个专家包 = `plugins/` 下一个目录。新增或修改专家请按本文执行。

## 一、命名规范

| 对象 | 规则 | 示例 |
|---|---|---|
| 包目录 / `name` / `plugin` | kebab-case，三者一致 | `mcp-dev-assistant` |
| 主理人 Agent | `<包名>-team-lead` | `mcp-dev-assistant-team-lead` |
| 成员 Agent | 表达职责的 kebab-case，不必带包名前缀 | `mcp-client-dev` |
| MD 文件名 | 必须等于该 Agent 的 `id` / `agentName` | `agents/mcp-client-dev.md` |
| 头像文件 | 与 Agent 同名，团队头像用包名 | `avatars/mcp-dev-assistant.png` |

`agentName` 不允许是通用的 `team-lead`，会造成多团队冲突。

## 二、目录要求

```
plugins/<包名>/
├── .codebuddy-plugin/plugin.json
├── agents/<agentName>.md            # 主理人 + 每个成员各一份
├── avatars/<agentName>.png          # 512×512 PNG，≤500KB
├── settings.json                    # 仅 Team 型，{"agent": "<主理人 id>"}
└── README.md                        # 该专家自己的说明
```

## 三、plugin.json 骨架

### Team 型

```json
{
  "name": "<包名>",
  "version": "1.0.0",
  "description": "<English one-liner>",
  "author": { "name": "<name>", "email": "<email>" },
  "agents": [
    "./agents/<包名>-team-lead.md",
    "./agents/<成员1>.md"
  ],
  "expertType": "team",
  "agentName": "<包名>-team-lead",
  "teamInfo": {
    "leadAgent": "<包名>-team-lead",
    "memberAgents": ["<成员1>"]
  },
  "displayName": { "en": "<EN>", "zh": "<中文名>" },
  "profession": { "en": "<EN>", "zh": "<中文名>" },
  "displayDescription": { "en": "<EN>", "zh": "<40-50 字>" },
  "avatar": "avatars/<包名>.png",
  "categoryId": "02-Engineering",
  "defaultInitPrompt": { "zh": "<首条示例问题>", "en": "<EN>" },
  "plugin": "<包名>",
  "tags": [
    { "en": "<EN>", "zh": "<中文>" },
    { "en": "<EN>", "zh": "<中文>" },
    { "en": "<EN>", "zh": "<中文>" }
  ],
  "quickPrompts": [
    { "zh": "<同 defaultInitPrompt>", "en": "<EN>" },
    { "zh": "<示例2>", "en": "<EN>" },
    { "zh": "<示例3>", "en": "<EN>" }
  ],
  "members": [
    {
      "id": "<包名>-team-lead",
      "name": { "en": "<EN>", "zh": "<中文名>" },
      "profession": { "en": "<EN>", "zh": "<中文头衔>" },
      "avatar": "avatars/<包名>-team-lead.png",
      "role": "lead"
    },
    {
      "id": "<成员1>",
      "name": { "en": "<EN>", "zh": "<中文名>" },
      "profession": { "en": "<EN>", "zh": "<中文头衔>" },
      "avatar": "avatars/<成员1>.png",
      "role": "member"
    }
  ]
}
```

### Agent 型

去掉 `teamInfo`、`members`、`settings.json`，`agents` 只留主理人一项，`agentName` 为该 Agent 名。

## 四、Agent MD 骨架

```markdown
---
name: <agentName>
description: "<一句话职责，英文或中文均可>"
displayName:
  en: "<EN>"
  zh: "<中文名>"
profession:
  en: "<EN>"
  zh: "<中文头衔>"
maxTurns: 80
---

# <角色名>

<角色定位，一句话说清不做什么>

## 职责

- ...

## 输出规范

- 结论先行，再给依据
- ...
```

禁止在 frontmatter 声明 `tools` 字段。

## 五、字段硬约束

这些规则来自实际被平台驳回的案例，逐条核对：

- `members[]` 用 `name:{en,zh}`，**不是 `displayName`**。平台报错原文：「members[0].name 的 en/zh 均为必填」
- Team 型 `profession` 必须与 `displayName` **完全相等**
- `tags`、`quickPrompts` 各 3 个；`quickPrompts[0]` 必须等于 `defaultInitPrompt`
- `displayDescription.zh` 40–50 字
- `settings.json.agent` = `agentName`；`teamInfo.leadAgent` = `role=lead` 的 `id`；`teamInfo.memberAgents` 不含主理人且覆盖其余成员
- `avatar` 与 `members[].avatar` 指向的文件必须真实存在
- 头像 512×512、PNG、≤500KB

## 六、校验

```bash
# 深度校验（字段、头像、id↔MD 对应、市场清单死链）
python scripts/lint_expert.py plugins/<包名> --marketplace .

# 官方浅校验（需要本机 WorkBuddy 安装目录）
python <WorkBuddy>/resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills/expert-manager/scripts/validate_expert.py plugins/<包名>
```

`lint_expert.py` 的检查项多于官方 `validate_expert.py`，后者不校验 `members[].name`、头像存在性、市场死链。

> ⚠️ 官方 `validate_expert.py` 还会强制校验「专家包必须位于 WorkBuddy 专家目录」，对本仓库 `plugins/` 下的副本会直接报「专家不在专家目录下，将无法被检测到」。**在本仓库内以 `scripts/lint_expert.py` 为准**；确需跑官方校验时，先把包复制到 `$WORKBUDDY_CONFIG_DIR/plugins/marketplaces/my-experts/plugins/` 下再执行。

## 七、清单登记

新增专家时在 `.codebuddy-plugin/marketplace.json` 的 `plugins` 追加：

```json
{
  "name": "<包名>",
  "source": "./plugins/<包名>",
  "description": "<English one-liner>",
  "version": "1.0.0",
  "license": "MIT"
}
```

改包名时必须同时修改 `source`，否则市场里会出现死链条目。

## 八、发布前脱敏检查

**首次 `git push` 之前必须过一遍。** 公开仓库的内容不可撤回：邮箱、路径一旦进入 commit 历史，即使后续删除文件也仍然可被检索。

- [ ] **身份信息**：全仓（含 `.codebuddy-plugin/` 等**隐藏目录**）扫邮箱；私有邮箱改用 `用户名@users.noreply.github.com`，作者联系方式改用 GitHub 主页链接。内部域邮箱（如 `*.local`）一律替换。
- [ ] **git 提交作者**：`git log --format='%an <%ae>'` 确认提交作者不含私人邮箱。未 push 时用 `git commit --amend --reset-author` 修正；已 push 则需改写历史并强推，代价高得多。
- [ ] **本机绝对路径**：扫 `C:/Users/...`、`/Users/<name>/...`、用户名、内部文档名；工具路径用环境变量或占位符，安装路径用 `$WORKBUDDY_CONFIG_DIR`。
- [ ] **凭据**：扫 `ghp_` / `github_pat_` / `sk-` / `-----BEGIN` / `password=` / `api_key=`，以及 `.env`、`*.pem`、`id_rsa*` 文件是否已忽略。
- [ ] **二进制元数据**：头像 PNG 检查 `tEXt` / `iTXt` / `eXIf` 块，生成工具可能写入本机路径或提示词。
- [ ] **外链**：确认所有 `http(s)://` 都是公开可访问地址，无内部域名、`localhost` 之外的私有地址。
- [ ] **复扫范围**：必须用能进入隐藏目录的方式扫描（`grep -r` 默认会跳过点目录），扫描目标排除 `.git/`，但**要包含 `.git` 历史里的作者字段**。

> 本仓库的 `.gitignore` 已忽略凭据类文件，但那是防误提交，不替代上面的人工复核。

## 八、提交前清单

- [ ] `python scripts/lint_expert.py plugins/<包名> --marketplace .` 零错误
- [ ] 所有头像存在且 ≤500KB
- [ ] `agents/` 下文件名与 `agentName`、`members[].id` 全部对应
- [ ] `marketplace.json` 已登记，`source` 路径正确
- [ ] 未提交 `.created-by-session`、`.pending-preview-session`、`dist/`、`*.zip`（`.gitignore` 已覆盖）
- [ ] `version` 已按变更幅度递增（破坏性改动升 minor 以上）
