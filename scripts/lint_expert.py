#!/usr/bin/env python3
"""Deep lint for WorkBuddy expert / expert-team packages.

Complements validate_expert.py, which does not check members[].name,
avatar existence, settings/agent consistency, or marketplace dead links.

Usage:
    lint_expert.py <expert-dir> [--marketplace <marketplace-dir>]
    lint_expert.py --zip <package.zip>

Exit code 0 = no errors (warnings allowed), 1 = errors found.
"""

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

KEBAB = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def _norm(rel):
    rel = str(rel)
    if rel.startswith('./'):
        rel = rel[2:]
    return rel.lstrip('/')


class Source:
    """Abstracts a directory or a zip archive."""

    def __init__(self, root=None, zip_path=None):
        self.root = Path(root).resolve() if root else None
        self.zip = zipfile.ZipFile(zip_path) if zip_path else None
        self.prefix = ''
        self._names = None
        if self.zip:
            names = self.zip.namelist()
            pj = [n for n in names if n.endswith('.codebuddy-plugin/plugin.json')]
            if not pj:
                raise SystemExit('zip 内未找到 .codebuddy-plugin/plugin.json')
            self.prefix = pj[0][: -len('.codebuddy-plugin/plugin.json')]
            self._names = set(names)

    def exists(self, rel):
        rel = _norm(rel)
        if self.zip:
            return (self.prefix + rel) in self._names
        return (self.root / rel).exists()

    def read_json(self, rel):
        rel = _norm(rel)
        if self.zip:
            return json.loads(self.zip.read(self.prefix + rel).decode('utf-8'))
        return json.loads((self.root / rel).read_text(encoding='utf-8'))

    def size(self, rel):
        rel = _norm(rel)
        if self.zip:
            return self.zip.getinfo(self.prefix + rel).file_size
        return (self.root / rel).stat().st_size


def i18n(pj, key, level=err):
    v = pj.get(key)
    if not isinstance(v, dict):
        level(f'plugin.json: 缺少 {key} 或其不是对象')
        return
    for lang in ('en', 'zh'):
        if not str(v.get(lang) or '').strip():
            level(f'plugin.json: {key}.{lang} 为空')


def lint(src):
    try:
        pj = src.read_json('.codebuddy-plugin/plugin.json')
    except FileNotFoundError:
        try:
            pj = src.read_json('.workbuddy-plugin/plugin.json')
        except FileNotFoundError:
            err('找不到 .codebuddy-plugin/plugin.json')
            return

    name = pj.get('name', '')
    if not KEBAB.match(name or ''):
        err(f"plugin.json: name '{name}' 不是 kebab-case")
    if not pj.get('version'):
        warn('plugin.json: 缺少 version')
    if pj.get('plugin') and pj['plugin'] != name:
        err(f"plugin.json: plugin '{pj['plugin']}' 与 name '{name}' 不一致")

    expert_type = pj.get('expertType')
    if expert_type not in ('agent', 'team'):
        err(f"plugin.json: expertType '{expert_type}' 应为 agent 或 team")

    for key in ('displayName', 'profession', 'displayDescription'):
        i18n(pj, key)

    desc_zh = (pj.get('displayDescription') or {}).get('zh', '')
    if desc_zh and not 40 <= len(desc_zh) <= 50:
        err(f'plugin.json: displayDescription.zh {len(desc_zh)} 字，要求 40-50')

    agent_name = pj.get('agentName', '')
    if not agent_name:
        err("plugin.json: 缺少 agentName")
    else:
        if agent_name == 'team-lead':
            err("plugin.json: agentName 不能是通用 'team-lead'，要带包名前缀")
        if not agent_name.startswith(name):
            warn(f"plugin.json: agentName '{agent_name}' 未以包名 '{name}' 开头（主理人建议 <pkg>-team-lead）")
        if not src.exists(f'agents/{agent_name}.md'):
            err(f"plugin.json: agentName '{agent_name}' 找不到对应文件 agents/{agent_name}.md")

    agents = pj.get('agents') or []
    if not agents:
        err("plugin.json: agents 不能为空")
    for a in agents:
        if not src.exists(a):
            err(f'plugin.json: agents 路径不存在 {a}')

    tags = pj.get('tags') or []
    if len(tags) != 3:
        err(f'plugin.json: tags 必须正好 3 个，当前 {len(tags)}')
    for t in tags:
        if not (t.get('en') and t.get('zh')):
            err(f'plugin.json: tag 缺少 en/zh → {t}')

    qps = pj.get('quickPrompts') or []
    if len(qps) != 3:
        err(f'plugin.json: quickPrompts 必须正好 3 个，当前 {len(qps)}')
    dip = pj.get('defaultInitPrompt') or {}
    if qps and dip and (qps[0].get('zh') != dip.get('zh')):
        err('plugin.json: quickPrompts[0] 必须等于 defaultInitPrompt')

    if not pj.get('categoryId'):
        warn('plugin.json: 缺少 categoryId')

    avatar = pj.get('avatar')
    if not avatar:
        err('plugin.json: 缺少 avatar')
    elif not src.exists(avatar):
        err(f'plugin.json: avatar 文件不存在 {avatar}')

    if expert_type == 'team':
        lint_team(src, pj, name, agent_name)
    else:
        lint_agent_avatars(src, [pj.get('avatar')] if avatar else [])


def lint_agent_avatars(src, paths):
    for p in paths:
        if not p or not src.exists(p):
            continue
        size = src.size(p)
        if size > 500 * 1024:
            warn(f'{p}: {size / 1024:.0f} KB，超过 500KB 建议压缩')


def lint_team(src, pj, name, agent_name):
    members = pj.get('members') or []
    if not members:
        err("plugin.json: Team 型必须有 members 数组")
        return

    ids = []
    leads = []
    avatars = []
    for i, m in enumerate(members):
        where = f'members[{i}]'
        if not isinstance(m, dict):
            err(f'{where}: 不是对象')
            continue
        mid = m.get('id')
        if not mid:
            err(f'{where}: 缺少 id')
        ids.append(mid)
        if 'displayName' in m:
            err(f'{where}: 成员姓名字段应叫 name 而不是 displayName（平台解析会报 name 必填）')
        nm = m.get('name')
        if not isinstance(nm, dict):
            err(f'{where}.name: 缺失或不是对象')
        else:
            for lang in ('en', 'zh'):
                if not str(nm.get(lang) or '').strip():
                    err(f'{where}.name.{lang}: 为空')
        for lang in ('en', 'zh'):
            if not str((m.get('profession') or {}).get(lang) or '').strip():
                err(f'{where}.profession.{lang}: 为空')
        role = m.get('role')
        if role not in ('lead', 'member'):
            err(f"{where}.role: '{role}' 应为 lead 或 member")
        if role == 'lead':
            leads.append(mid)
        extra = set(m) - {'id', 'name', 'profession', 'avatar', 'role'}
        if extra:
            warn(f'{where}: 多余字段 {sorted(extra)}（官方包只有 id/name/profession/avatar/role）')
        if not m.get('avatar'):
            err(f'{where}: 缺少 avatar')
        else:
            avatars.append(m['avatar'])
            if not src.exists(m['avatar']):
                err(f'{where}.avatar: 文件不存在 {m["avatar"]}')
        if mid and not src.exists(f'agents/{mid}.md'):
            err(f'{where}: id {mid} 没有对应 agents/{mid}.md')

    if len(set(ids)) != len(ids):
        err(f'members: id 重复 → {ids}')
    if len(leads) != 1:
        err(f'members: role=lead 必须正好 1 个，当前 {leads}')

    ti = pj.get('teamInfo') or {}
    lead_agent = ti.get('leadAgent')
    if leads and lead_agent != leads[0]:
        err(f"teamInfo.leadAgent '{lead_agent}' 与 members 中 lead '{leads[0]}' 不一致")
    if lead_agent and lead_agent != agent_name:
        err(f"teamInfo.leadAgent '{lead_agent}' 与 agentName '{agent_name}' 不一致")
    member_agents = ti.get('memberAgents') or []
    if lead_agent and lead_agent in member_agents:
        err('teamInfo.memberAgents 不应包含主理人')
    expected = [i for i in ids if i and i != lead_agent]
    if sorted(member_agents) != sorted(expected):
        err(f'teamInfo.memberAgents {member_agents} 与 members 非主理人 {expected} 不一致')

    if pj.get('profession') != pj.get('displayName'):
        warn('Team 型 profession 与 displayName 不一致（本地 validate 会拦，官方包有反例）')

    if not src.exists('settings.json'):
        warn('Team 型无 settings.json（官方包不带，但本地 validate 要求，打包前需有）')
    else:
        s = src.read_json('settings.json')
        if s.get('agent') != agent_name:
            err(f"settings.json.agent '{s.get('agent')}' 应等于 agentName '{agent_name}'")

    lint_agent_avatars(src, avatars + ([pj['avatar']] if pj.get('avatar') else []))


def lint_marketplace(mp_dir, name, version):
    mp_file = Path(mp_dir) / '.codebuddy-plugin' / 'marketplace.json'
    if not mp_file.exists():
        err(f'marketplace.json 不存在：{mp_file}')
        return
    mp = json.loads(mp_file.read_text(encoding='utf-8'))
    entries = [e for e in mp.get('plugins', []) if e.get('name') == name]
    if not entries:
        err(f"marketplace.json 中没有 '{name}' 条目（需要跑 register_expert.py）")
        return
    e = entries[0]
    src_path = (mp_file.parent.parent / e.get('source', '')).resolve()
    if not src_path.exists():
        err(f"marketplace.json 条目 source 指向不存在的目录：{e.get('source')}")
    if e.get('version') and version and e['version'] != version:
        warn(f"marketplace.json version {e['version']} 与 plugin.json {version} 不一致")
    stale = [
        x['name'] for x in mp.get('plugins', [])
        if x.get('source') and not (mp_file.parent.parent / x['source']).resolve().exists()
    ]
    if stale:
        warn(f'marketplace.json 存在死链条目：{stale}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('expert_dir', nargs='?')
    ap.add_argument('--zip', dest='zip_path')
    ap.add_argument('--marketplace', dest='marketplace')
    args = ap.parse_args()

    if not args.expert_dir and not args.zip_path:
        ap.error('需要 expert_dir 或 --zip')

    if args.zip_path:
        src = Source(zip_path=args.zip_path)
        target = args.zip_path
    else:
        src = Source(root=args.expert_dir)
        target = args.expert_dir

    print(f'🔍 Lint: {target}')
    lint(src)

    if args.marketplace and not args.zip_path:
        pj = src.read_json('.codebuddy-plugin/plugin.json')
        lint_marketplace(args.marketplace, pj.get('name'), pj.get('version'))

    for w in warnings:
        print(f'  ⚠️  {w}')
    for e in errors:
        print(f'  ❌ {e}')

    print()
    if errors:
        print(f'❌ {len(errors)} 个错误，{len(warnings)} 个警告')
        return 1
    print(f'✅ 通过（{len(warnings)} 个警告）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
