```
███████      ███████
████████    ████████
█████████  █████████
█████████  █████████
██████████████
██████████████
█████████  █████████
█████████  █████████
████████    ████████
███████      ███████

K O A H   S K I L L S
```

[![skills.sh](https://www.skills.sh/b/koahlabs/skills)](https://www.skills.sh/koahlabs/skills)

Public agent skills for working with Koah products, plus a few techniques we use
on our own work.

## Available skills

| skill | what it does |
|---|---|
| [koah-integration](skills/koah-integration) | Integrate Koah into your application, either as a publisher (an AI app developer looking to monetize) or an advertiser looking to promote your brand on Koah. |
| [hdr-logo](skills/hdr-logo) | Re-encode a logo as Rec.2100 PQ so its white pixels render brighter than normal white on Apple EDR/XDR displays, without shifting any other colour. macOS only. |

## Get started

### With the skills CLI

Install one skill:

```bash
npx skills add koahlabs/skills --skill koah-integration
```

Install everything in the repo:

```bash
npx skills add koahlabs/skills --all
```

Skills land in your project's `.agents/skills` folder. Pass `--global` to install
at the user level instead, or `--list` to see what a repo offers without
installing anything.

### With Claude Code

1. Run `/plugins` to manage plugins.
2. Add `https://github.com/koahlabs/skills` under "Marketplaces".
3. Reload the available skills with `/reload-plugins`.
4. Invoke a skill by name, for example `/koah-integration`.

## Adding a skill

A skill is a directory under `skills/` holding a `SKILL.md` with `name` and
`description` frontmatter. The description is what an agent matches against, so
list the phrases that should trigger it.

Register it in two places:

- the `skills` array in `.claude-plugin/marketplace.json`, for the Claude plugin
- a group in `skills.sh.json`, which organizes the repo page on skills.sh

Copy follows the Koah voice: plain, concrete, and no em dashes.

## License

MIT
