# Contributing to Runic Lands

Thank you for your interest in contributing to Runic Lands! This document provides guidelines and information for contributors.

## 🚨 **Important Notice**

This project is **PROPRIETARY** and **CONFIDENTIAL**. All contributions are subject to our proprietary license terms. By contributing, you agree to transfer all rights to your contributions to the Runic Lands Development Team.

## 📋 **Contribution Guidelines**

### **Before You Start**
1. **Read the License**: Ensure you understand our proprietary license terms
2. **Check Issues**: Look for existing issues or feature requests
3. **Contact Us**: Reach out before starting major contributions
4. **Sign Agreement**: Complete our contributor agreement

### **Types of Contributions**
- 🐛 **Bug Fixes**: Fix existing issues and improve stability
- ✨ **Features**: Add new functionality (with approval)
- 📚 **Documentation**: Improve docs, comments, and guides
- 🎨 **Assets**: Create sprites, audio, or other game assets
- 🧪 **Testing**: Add tests and improve test coverage

## 🛠️ **Development Setup**

### **Prerequisites**
- Python 3.13.1+
- Git
- Your preferred IDE/editor
- Windows 10/11 (primary platform)

### **Setup Steps**
1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/runiclands.git
   cd runiclands
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Tests**
   ```bash
   python -m pytest tests/
   ```

## 📝 **Code Standards**

### **Python Style**
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions under 50 lines when possible

### **Naming Conventions**
- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Files**: `snake_case.py`

### **Documentation**
- Use clear, concise docstrings
- Include examples for complex functions
- Update README.md for new features
- Add inline comments for complex logic

## 🧪 **Testing**

### **Test Requirements**
- All new features must have tests
- Maintain 80%+ code coverage
- Test both success and failure cases
- Include integration tests for major features

### **Running Tests**
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_combat.py
```

## 📤 **Submitting Changes**

### **Pull Request Process**
1. **Create PR**: Submit a pull request with clear description
2. **Link Issues**: Reference any related issues
3. **Add Tests**: Include tests for new functionality
4. **Update Docs**: Update documentation as needed
5. **Wait for Review**: Address feedback promptly

### **PR Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Asset addition
- [ ] Other

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🎨 **Asset Contributions**

### **Sprite Guidelines**
- **Format**: PNG with transparency
- **Size**: Power of 2 dimensions (32x32, 64x64, etc.)
- **Style**: Pixel art, consistent with game aesthetic
- **Naming**: Descriptive, snake_case

### **Audio Guidelines**
- **Format**: WAV for effects, OGG for music
- **Quality**: 44.1kHz, 16-bit minimum
- **Length**: Keep effects short (< 2 seconds)
- **Naming**: Descriptive, snake_case

## 🐛 **Bug Reports**

### **Before Reporting**
1. Check existing issues
2. Try latest version
3. Reproduce the bug
4. Gather system information

### **Bug Report Template**
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**System Information**
- OS: Windows 10/11
- Python Version: 3.13.1
- Game Version: 0.8.0

**Screenshots/Logs**
Include relevant screenshots or log files
```

## 💡 **Feature Requests**

### **Before Requesting**
1. Check existing feature requests
2. Consider if it fits the game's vision
3. Think about implementation complexity
4. Provide detailed description

### **Feature Request Template**
```markdown
**Feature Description**
Clear description of the requested feature

**Use Case**
Why this feature would be useful

**Proposed Implementation**
How you think it could be implemented

**Alternatives Considered**
Other ways to achieve the same goal

**Additional Context**
Any other relevant information
```

## 📞 **Getting Help**

### **Communication Channels**
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For general questions
- **Email**: dev@runiclands.com for sensitive matters

### **Response Times**
- **Bug Reports**: 24-48 hours
- **Feature Requests**: 1-2 weeks
- **General Questions**: 2-3 days

## 🏆 **Recognition**

### **Contributor Recognition**
- Contributors listed in README.md
- Special thanks in release notes
- Access to beta features
- Contributor badge on GitHub

### **Types of Recognition**
- **Code Contributors**: Code, tests, documentation
- **Asset Contributors**: Sprites, audio, music
- **Community Contributors**: Bug reports, feedback, testing
- **Documentation Contributors**: Guides, tutorials, translations

## ⚖️ **Legal**

### **Contributor Agreement**
By contributing to Runic Lands, you agree to:
- Transfer all rights to your contributions
- Maintain confidentiality of proprietary information
- Not use contributions for competing projects
- Follow all applicable laws and regulations

### **Intellectual Property**
- All contributions become property of Runic Lands Development Team
- No reverse engineering or decompilation
- Confidentiality of source code and assets
- No distribution without permission

## 📚 **Resources**

### **Documentation**
- [Game Design Document](docs/game_design.md)
- [Technical Architecture](docs/technical_architecture.md)
- [API Reference](docs/api_reference.md)
- [Asset Guidelines](docs/asset_guidelines.md)

### **Development Tools**
- [Asset Generator](tools/gui/asset_gui.py)
- [Audio Manager](tools/audio_manager.py)
- [Sprite Generator](tools/sprite_generation/)

---

**Thank you for contributing to Runic Lands! Together, we're building something amazing.** 🎮✨
