# 🚀 Quick Start Guide - Grain Android App (पहिली बायको)

## What We Created

A **native Android app** that wraps your Grain web application, following the same structure as your Portfolio Android app. The app automatically loads your backend at `http://13.201.13.214/`.

### App Features
- ✅ Native Android app (Kotlin)
- ✅ WebView wrapper around Grain web interface
- ✅ Connects to: `http://13.201.13.214/`
- ✅ Full web functionality (JavaScript, cookies)
- ✅ Back button support
- ✅ App name: **पहिली बायको**

---

## 📱 Option 1: Quick Test (5 minutes)

### Windows/Laptop Terminal:

```powershell
# 1. Navigate to the app folder
cd D:\GrainRepo\grain-android-app

# 2. List all files to confirm structure
ls -Recurse | Where-Object {$_.PSIsContainer -eq $false} | Select Name
```

---

## 🎯 Option 2: Build & Run in Android Studio (15 minutes)

### Step-by-Step:

**1. Download & Install Android Studio**
   - Go to https://developer.android.com/studio
   - Install latest version

**2. Open the Project**
   - Launch Android Studio
   - File → Open
   - Select: `D:\GrainRepo\grain-android-app`
   - Click OK

**3. Let Gradle Sync**
   - Android Studio will show "Sync Now" → Click it
   - Wait for build to complete (~2-5 minutes)

**4. Create Virtual Device (or connect real phone)**
   - Click: Tools → Device Manager
   - Click: Create Device
   - Select: Pixel 6 (or any device)
   - Select: API 35
   - Click: Finish

**5. Run the App**
   - Click green ▶ Run button
   - Select your device
   - Click OK
   - **App will launch and load your Grain website!**

---

## 📁 Project Structure (Reference)

```
grain-android-app/
├── README.md              ← Detailed documentation
├── SETUP.md              ← Build instructions
├── STRUCTURE.md          ← Folder explanation
│
├── app/
│   ├── build.gradle.kts  ← App configuration
│   │
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/com/grain/app/
│       │   └── MainActivity.kt  ← Main web wrapper
│       │
│       └── res/
│           ├── values/
│           │   ├── strings.xml  ← App name (पहिली बायको)
│           │   ├── colors.xml   ← Theme colors
│           │   └── styles.xml   ← Theme styles
│           │
│           ├── xml/
│           │   └── network_security_config.xml
│           │
│           └── mipmap-anydpi-v26/
│               └── ic_launcher.xml
│
├── gradle/wrapper/
│   └── gradle-wrapper.properties  ← Gradle 8.11.1
│
├── build.gradle.kts      ← Project build config
├── settings.gradle.kts   ← Gradle settings
└── gradle.properties     ← Gradle properties
```

---

## 🔧 Customization

### Change Backend URL
Edit `app/src/main/java/com/grain/app/MainActivity.kt`, line 14:
```kotlin
private const val START_URL = "http://YOUR_NEW_URL/"
```

### Change App Name
Edit `app/src/main/res/values/strings.xml`:
```xml
<string name="app_name">Your New App Name</string>
```

### Change Theme Colors
Edit `app/src/main/res/values/colors.xml`:
```xml
<color name="grain_primary">#YOURCOLOR</color>
```

---

## ⚠️ Important Notes

1. **Backend Must Be Running**
   - App loads: `http://13.201.13.214/`
   - Make sure your EC2 backend is running
   - Test in browser: http://13.201.13.214

2. **Network Access**
   - Device/Emulator must have internet access
   - No VPN unless allowed in network security config

3. **API 35 Required**
   - Minimum SDK: 24 (Android 7.0)
   - Target SDK: 35 (Android 15)
   - Java 17

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Gradle sync failed" | File → Invalidate Caches → Restart |
| "App won't start" | Check EC2 backend is running |
| "Blank white page" | Check device has internet access |
| "APK won't install" | `gradle uninstallDebug` then retry |

---

## 📦 Next Steps

1. ✅ **Build & Run** in Android Studio (above)
2. 📝 **Test on device** - Use a real phone or emulator
3. 🔄 **Customize** - Update app name, colors, backend URL
4. 🚀 **Publish** - Release on Google Play Store (add Google Play Developer account)

---

## 📚 Resources

- **Android Studio Docs**: https://developer.android.com/studio/intro
- **WebView Guide**: https://developer.android.com/reference/android/webkit/WebView
- **Material Design**: https://material.io/design
- **Google Play Publishing**: https://developer.android.com/studio/publish

---

## ✨ You're All Set!

Your Grain Android App (**पहिली बायको**) is ready to build and distribute.

**Next Action**: Open `D:\GrainRepo\grain-android-app` in Android Studio and click Run! 🚀
