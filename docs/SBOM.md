# Software Bill of Materials (SBOM) - Runic Lands

## 📋 Overview

This document provides a comprehensive inventory of all software packages, dependencies, and components used in the Runic Lands project. This SBOM is maintained for security purposes and compliance requirements.

**Generated**: December 2024  
**Project Version**: 0.1.0  
**Python Version**: 3.13.1  

## 🐍 Core Dependencies

### Primary Game Engine
| Package | Version | License | Purpose | Security Status |
|---------|---------|---------|---------|-----------------|
| pygame | >=2.5.0 | LGPL | Game engine and multimedia | ✅ Current |
| python | 3.13.1 | PSF | Runtime environment | ✅ Latest |

### Graphics & Rendering
| Package | Version | License | Purpose | Security Status |
|---------|---------|---------|---------|-----------------|
| pillow | 11.1.0 | HPND | Image processing | ✅ Current |
| pytmx | 3.32 | LGPL | TMX map format support | ✅ Current |
| pyscroll | 2.31 | LGPL | Scrolling map engine | ✅ Current |

### Scientific Computing
| Package | Version | License | Purpose | Security Status |
|---------|---------|---------|---------|-----------------|
| numpy | 2.2.4 | BSD | Numerical computing | ✅ Current |
| scipy | 1.15.2 | BSD | Scientific computing | ✅ Current |

### World Generation
| Package | Version | License | Purpose | Security Status |
|---------|---------|---------|---------|-----------------|
| opensimplex | >=0.4.5 | MIT | Noise generation | ✅ Current |

## 🔧 Development Dependencies

### Build & Packaging
| Package | Version | License | Purpose | Security Status |
|---------|---------|---------|---------|-----------------|
| setuptools | Latest | MIT | Package building | ✅ Current |
| wheel | Latest | MIT | Package distribution | ✅ Current |

### Code Quality (Recommended)
| Package | Version | License | Purpose | Security Status |
|---------|---------|---------|---------|-----------------|
| black | Latest | MIT | Code formatting | 🔄 To Add |
| flake8 | Latest | MIT | Linting | 🔄 To Add |
| mypy | Latest | MIT | Type checking | 🔄 To Add |
| pytest | Latest | MIT | Testing framework | 🔄 To Add |

## 🎵 Audio Dependencies

### Audio Processing
| Package | Version | License | Purpose | Security Status |
|---------|---------|---------|---------|-----------------|
| pygame.mixer | Built-in | LGPL | Audio playback | ✅ Current |

### Audio Generation Tools (Development)
| Tool | Purpose | Dependencies | Security Status |
|------|---------|--------------|-----------------|
| generate_menu_music.py | Menu music generation | pygame | ✅ Safe |
| generate_game_music.py | Game music generation | pygame | ✅ Safe |
| audio_manager.py | Audio management | pygame | ✅ Safe |

## 🎨 Asset Dependencies

### Image Assets
| Asset Type | Format | Count | Size | Purpose |
|------------|--------|-------|------|---------|
| Character Sprites | PNG | 6 | ~50KB | Player animations |
| Audio Files | WAV | 20+ | ~2MB | Music and sound effects |
| Map Data | JSON | 1 | ~5KB | Level configuration |

### Generated Assets
| Asset Type | Generator | Dependencies | Security Status |
|------------|-----------|--------------|-----------------|
| Music Files | Custom tools | pygame | ✅ Safe |
| Sprite Variations | generate_*.py | pillow | ✅ Safe |

## 🔒 Security Analysis

### Vulnerability Assessment
- **pygame**: No known critical vulnerabilities
- **pillow**: Regular security updates, current version secure
- **numpy**: Well-maintained, no critical issues
- **scipy**: Scientific computing library, secure
- **opensimplex**: MIT licensed, minimal attack surface

### Security Recommendations
1. **Regular Updates**: Monitor for security updates monthly
2. **Dependency Scanning**: Implement automated vulnerability scanning
3. **License Compliance**: All dependencies use permissive licenses
4. **Asset Validation**: Implement checksum validation for game assets

## 📊 Dependency Tree

```
Runic Lands
├── pygame (>=2.5.0)
│   ├── SDL2 (system dependency)
│   └── SDL2_mixer (system dependency)
├── pillow (11.1.0)
│   ├── zlib (system dependency)
│   └── libjpeg (system dependency)
├── pytmx (3.32)
│   └── xml.etree.ElementTree (built-in)
├── pyscroll (2.31)
│   └── pygame (dependency)
├── numpy (2.2.4)
│   └── BLAS/LAPACK (system dependency)
├── scipy (1.15.2)
│   ├── numpy (dependency)
│   └── BLAS/LAPACK (system dependency)
└── opensimplex (>=0.4.5)
    └── No dependencies
```

## 🔄 Update Schedule

### Monthly Reviews
- Check for security updates
- Review dependency versions
- Update SBOM with new packages

### Quarterly Reviews
- Major version updates
- License compliance check
- Performance impact assessment

## 📋 Compliance Notes

### License Compatibility
- **Primary License**: MIT (compatible with all dependencies)
- **GPL Dependencies**: None (pygame uses LGPL, compatible)
- **Commercial Use**: All dependencies allow commercial use

### Export Control
- No cryptographic libraries
- No restricted algorithms
- No export-controlled components

## 🛠️ Installation Commands

### Basic Installation
```bash
pip install -r docs/requirements.txt
```

### Development Installation
```bash
pip install -r docs/requirements.txt
pip install black flake8 mypy pytest
```

### Security Scan
```bash
pip install safety
safety check
```

## 📞 Security Contact

For security-related issues or questions about this SBOM:
- **Project**: Runic Lands
- **Maintainer**: Development Team
- **Last Updated**: December 2024

---

*This SBOM is maintained for security and compliance purposes. Regular updates ensure accurate dependency tracking.*
