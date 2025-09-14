# Contributing to AuraFarming

Thank you for your interest in contributing to AuraFarming! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Check existing issues** first to avoid duplicates
2. **Use issue templates** when creating new issues
3. **Provide detailed information** including:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Screenshots/logs if applicable

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/AuraFarming.git
   cd AuraFarming
   ```
3. **Follow the Quick Start guide** in README.md
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Pull Request Process

1. **Ensure your code follows our standards** (see below)
2. **Add tests** for new functionality
3. **Update documentation** as needed
4. **Commit with clear messages** using Conventional Commits
5. **Push to your fork** and create a pull request
6. **Address review feedback** promptly

## 📝 Code Standards

### Python (Backend)

- **Follow PEP 8** style guidelines
- **Use Black** for code formatting:
  ```bash
  black backend/app/
  ```
- **Use type hints** for function parameters and returns
- **Write docstrings** for all functions and classes
- **Keep functions small** and focused on single responsibility

### JavaScript/React (Frontend)

- **Follow Airbnb JavaScript Style Guide**
- **Use Prettier** for code formatting:
  ```bash
  npx prettier --write src/
  ```
- **Use meaningful component and variable names**
- **Write JSDoc comments** for complex functions
- **Prefer functional components** with hooks

### Git Commit Convention

We use **Conventional Commits** format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(ml): add crop yield prediction model
fix(auth): resolve login session timeout issue
docs(api): update endpoint documentation
```

## 🧪 Testing

### Backend Testing

```bash
cd backend
python -m pytest tests/ -v
```

**Test Requirements:**
- Maintain >80% code coverage
- Write unit tests for all new functions
- Include integration tests for API endpoints
- Mock external services in tests

### Frontend Testing

```bash
cd frontend
npm test
```

**Test Requirements:**
- Test all user interactions
- Write component tests using React Testing Library
- Include accessibility tests
- Test responsive design

## 🔒 Security Guidelines

- **Never commit sensitive information** (API keys, passwords, etc.)
- **Use environment variables** for configuration
- **Validate all user inputs** on both frontend and backend
- **Follow OWASP security guidelines**
- **Report security issues privately** to maintainers

## 📚 Documentation

- **Update README.md** for significant changes
- **Add inline code comments** for complex logic
- **Write API documentation** for new endpoints
- **Include examples** in documentation
- **Keep documentation up-to-date** with code changes

## 🌟 Recognition

Contributors will be recognized in:
- **README.md contributors section**
- **GitHub contributors page**
- **Release notes** for significant contributions

## 📞 Getting Help

- **Create an issue** for bugs or feature requests
- **Start a discussion** for questions or ideas
- **Join our community** for real-time chat
- **Check existing documentation** first

## 📋 Contributor Checklist

Before submitting a pull request:

- [ ] Code follows style guidelines
- [ ] Self-review of code completed
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts with main branch

## 🚀 Development Workflow

1. **Pick an issue** from our GitHub issues
2. **Comment on the issue** to get assigned
3. **Create a feature branch** from main
4. **Develop and test** your changes
5. **Submit a pull request** with clear description
6. **Respond to code review** feedback
7. **Celebrate** when your PR is merged! 🎉

Thank you for contributing to AuraFarming and helping farmers worldwide! 🌾