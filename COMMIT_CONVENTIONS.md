# Commit Message Conventions

This project follows [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages.

## Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types

| Type | Description |
|------|-------------|
| `feat` | A new feature for the user |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc) |
| `refactor` | A code change that neither fixes a bug nor adds a feature |
| `perf` | A code change that improves performance |
| `test` | Adding missing tests or correcting existing tests |
| `build` | Changes that affect the build system or external dependencies (poetry, pyproject.toml) |
| `ci` | Changes to CI configuration files and scripts (GitHub Actions, etc.) |
| `chore` | Other changes that don't modify src or test files |
| `revert` | Reverts a previous commit |

## Scopes

Common scopes for this project:

- `claude` - AWS Bedrock Claude integration
- `workflow` - LangGraph workflow orchestration
- `sentiment` - Sentiment analysis functionality
- `rudeness` - Rudeness detection functionality
- `nodes` - Analysis node implementations
- `models` - Pydantic models and data structures
- `services` - External service integrations
- `cli` - Command line interface
- `api` - API endpoints (if applicable)
- `config` - Configuration files
- `deps` - Dependencies

## Examples

### Features
```
feat(claude): add cross-region inference profile support

- Implement fallback regions for improved availability
- Add model configuration with temperature and max tokens
- Include proper error handling for ValidationException

Closes #123
```

### Bug Fixes
```
fix(workflow): handle AWS Bedrock service unavailability

When AWS Bedrock is unavailable, the workflow now falls back to
mock sentiment analysis instead of crashing.

Fixes #456
```

### Documentation
```
docs: update README with AWS CLI configuration steps

Add detailed instructions for setting up AWS credentials
and region configuration for Bedrock access.
```

### Breaking Changes
```
feat(api): redesign sentiment analysis response format

BREAKING CHANGE: The sentiment analysis endpoint now returns
a structured response with `category`, `reasoning`, and `response`
fields instead of a simple string classification.

Before:
{
  "sentiment": "positive"
}

After:
{
  "category": "Professional",
  "reasoning": "Market shows measured optimism",
  "response": "This market is cautiously optimistic..."
}
```

### Chores
```
chore(deps): update langchain-aws to v0.2.1

- Includes performance improvements for Bedrock integration
- Fixes compatibility with latest boto3 version
```

## Setup

To use the commit message template automatically:

```bash
git config commit.template .gitmessage
```

This will open the template in your editor whenever you run `git commit` without the `-m` flag.

## Guidelines

1. **Subject line (first line)**:
   - Use imperative mood ("add" not "added" or "adds")
   - Don't capitalize the first letter after the colon
   - No period at the end
   - Keep under 50 characters

2. **Body**:
   - Separate from subject with blank line
   - Wrap at 72 characters
   - Explain what and why, not how
   - Use imperative mood

3. **Footer**:
   - Reference issues and pull requests
   - Note breaking changes
   - Use "Closes #123" or "Fixes #456" for automatic issue closing

## Tools

You can use tools like [commitizen](https://commitizen-tools.github.io/commitizen/) to help format commits:

```bash
pip install commitizen
cz commit
```

Or use VS Code extensions like "Conventional Commits" for guided commit message creation.
