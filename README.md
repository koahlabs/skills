# Koah Skills

Repository of public skills for Koah products that can be added with the [skills NPM package](https://www.npmjs.com/package/skills).

[![skills.sh](https://skills.sh/b/koahlabs/skills)](https://skills.sh/b/koahlabs/skills)

# Skills List

1. [koah-integration](skills/koah-integration): Integrate Koah into your application, either as a publisher (AI app developer looking to monetize) or an advertiser looking to promote your brand on Koah.

# Get Started

1. Install the skills NPM package: `npm install -g skills`
2. Install the desired Koah skill, e.g. `npx skills add https://github.com/koahlabs/skills --skill koah-integration`. This installs the skill to your local project's `.agents/skills` folder.
3. Use the skill with your LLM: for Claude, you'll need to copy `.agent/skills` to `/claude/skills`, then run `/koah-integration` (may need to restart Claude).


# LICENSE

MIT
