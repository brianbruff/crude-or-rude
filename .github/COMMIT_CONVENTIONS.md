# Conventional Commits Guide

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature for the user
- **fix**: A bug fix for the user
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies (Poetry, pyproject.toml)
- **ci**: Changes to CI configuration files and scripts (GitHub Actions)
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

### Scopes (Optional)

Use scopes to indicate which part of the codebase is affected:

- **claude**: AWS Bedrock Claude integration (`nodes/claude.py`)
- **sentiment**: Sentiment analysis node (`nodes/sentiment.py`)
- **rudeness**: Rudeness detection node (`nodes/rudeness.py`)
- **workflow**: LangGraph workflow orchestration (`workflow.py`)
- **models**: Pydantic models and schemas (`models/`)
- **services**: External service integrations (`services/`)
- **cli**: Command-line interface (`main.py`)
- **deps**: Dependencies and package management
- **config**: Configuration files
- **tests**: Test files and test infrastructure

### Subject

- Use imperative mood: "Add feature" not "Added feature"
- Don't capitalize the first letter
- No period at the end
- Maximum 50 characters

### Body (Optional)

- Explain the motivation for the change
- Contrast with previous behavior
- Wrap at 72 characters per line

### Footer (Optional)

- Reference GitHub issues: `Closes #123`
- Note breaking changes: `BREAKING CHANGE: <description>`

## Examples

### Simple Changes
```
feat(claude): add cross-region inference profile support
fix(workflow): handle AWS Bedrock service timeout
docs: update README with AWS CLI setup instructions
test(sentiment): add mock FastMCP service tests
chore(deps): update langchain-aws to v0.1.15
```

### With Body
```
feat(claude): add temperature configuration option

Allow users to configure Claude model temperature through
environment variable CLAUDE_TEMPERATURE. Default remains 0.7
for consistent witty commentary generation.

Closes #45
```

### Breaking Change
```
feat(models)!: restructure MarketSentiment response format

BREAKING CHANGE: MarketSentiment.response field renamed to
MarketSentiment.commentary for better semantic clarity.
Update any code that accesses the response field.

Closes #67
```

### Revert
```
revert: feat(claude): add temperature configuration

This reverts commit 1234567890abcdef due to compatibility
issues with AWS Bedrock cross-region profiles.
```

## Git Configuration

To use the commit message template:

```bash
git config commit.template .gitmessage
```

## Tools

Consider using tools like:
- [commitizen](https://github.com/commitizen/cz-cli) for interactive commit creation
- GitHub CLI with conventional commit templates
- VS Code extensions for conventional commits

## Enforcement

This project may use:
- GitHub Actions to validate commit message format
- Pre-commit hooks for local validation
- Branch protection rules requiring conventional commits
