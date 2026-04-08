# Contributing

本文档面向仓库维护者和贡献者。

## 发布说明

当前仓库已经包含基于 OpenID Connect 的 GitHub Actions 发布流程：

- 正式 PyPI：`.github/workflows/publish.yml`
- TestPyPI：`.github/workflows/publish-testpypi.yml`

两者都使用 PyPI Trusted Publishing，不需要保存长期 `PYPI_API_TOKEN`。

### 正式 PyPI 配置

需要在网页上完成两步：

1. 在 PyPI 项目里添加 Trusted Publisher
2. 在 GitHub 仓库里创建 `pypi` environment

推荐配置：

- PyPI project name: `dida365-openapi`
- GitHub owner: `hktkzyx`
- GitHub repository: `dida365-openapi`
- Workflow file: `publish.yml`
- Environment name: `pypi`

### TestPyPI 配置

需要在网页上完成两步：

1. 在 TestPyPI 项目里添加 Trusted Publisher
2. 在 GitHub 仓库里创建 `testpypi` environment

推荐配置：

- TestPyPI project name: `dida365-openapi`
- GitHub owner: `hktkzyx`
- GitHub repository: `dida365-openapi`
- Workflow file: `publish-testpypi.yml`
- Environment name: `testpypi`

### 测试发布

TestPyPI workflow 通过 `test-v*` tag 触发。

例如：

```bash
git tag test-v0.1.1
git push origin test-v0.1.1
```

### 正式发布

正式 PyPI workflow 通过 `v*` tag 触发。

发版步骤：

1. 修改 [pyproject.toml](./pyproject.toml) 里的版本号
2. 提交代码
3. 打 tag 并推送

例如：

```bash
git tag v0.1.1
git push origin v0.1.1
```

推送后，GitHub Actions 会自动构建并发布到 PyPI。
