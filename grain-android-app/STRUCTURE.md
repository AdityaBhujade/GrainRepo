# Grain Android App - Complete Folder Structure

```
grain-android-app/
│
├── 📄 build.gradle.kts                    # Project-level Gradle config
├── 📄 settings.gradle.kts                 # Gradle settings (defines modules)
├── 📄 gradle.properties                   # Gradle configuration properties
├── 📄 local.properties                    # Local SDK path (auto-generated)
├── 📄 .gitignore                         # Git ignore rules
├── 📄 README.md                          # Project documentation
├── 📄 SETUP.md                           # Build and run instructions
│
├── 📁 gradle/
│   └── 📁 wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties      # Gradle version: 8.11.1
│
├── 📁 app/                                # Main app module
│   ├── build.gradle.kts                   # App-level Gradle config
│   ├── proguard-rules.pro                 # ProGuard configuration
│   │
│   └── 📁 src/
│       └── 📁 main/
│           ├── 📄 AndroidManifest.xml     # App manifest
│           │
│           ├── 📁 java/                   # Source code
│           │   └── 📁 com/
│           │       └── 📁 grain/
│           │           └── 📁 app/
│           │               └── MainActivity.kt        # Main activity (WebView wrapper)
│           │
│           └── 📁 res/                    # Resources
│               ├── 📁 drawable/           # App drawables (images)
│               │   └── ic_launcher_foreground.xml (placeholder)
│               │
│               ├── 📁 values/             # Value resources
│               │   ├── strings.xml        # App strings (app name: पहिली बायको)
│               │   ├── colors.xml         # Color definitions
│               │   └── styles.xml         # App theme styles
│               │
│               ├── 📁 mipmap-anydpi-v26/  # Adaptive icons
│               │   ├── ic_launcher.xml
│               │   └── ic_launcher_round.xml
│               │
│               └── 📁 xml/                # XML resources
│                   └── network_security_config.xml   # Network security settings
│
└── ✅ Ready for Android Studio import!
```

## Key Files Explained

### `MainActivity.kt`
- WebView-based activity that loads `http://13.201.13.214/`
- Handles JavaScript, cookies, and back navigation
- No database - pure web wrapper

### `AndroidManifest.xml`
- App configuration and permissions
- Declares MainActivity as launcher
- Requires INTERNET permission for web access

### `build.gradle.kts` (app level)
- Target API 35, Min API 24, Java 17
- Dependencies: androidx.core, androidx.appcompat
- Debug and release build configurations

### `strings.xml`
- App name: "पहिली बायको" (Nepali name)

### `network_security_config.xml`
- Allows cleartext (HTTP) traffic to EC2 IP
- Configured for development

### `colors.xml` & `styles.xml`
- Theme colors (grain-themed brown/gold palette)
- Modern Material Design theme

## Ready to Open in Android Studio! 🚀
