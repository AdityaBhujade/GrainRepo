# Grain Android App

A native Android app wrapper for the Grain Customer Management System. This app provides a mobile interface to access the Grain application by wrapping the web interface in a WebView.

## Features

- Native Android app using Kotlin
- WebView-based interface  
- Connects to Grain backend at `http://13.201.13.214/`
- Supports JavaScript and cookies
- Back navigation support
- Cleartext traffic enabled for local development

## Requirements

- Android Studio Arctic Fox or later
- Android SDK 35 (compileSdk)
- Minimum Android API 24 (minSdk)
- Java 17
- Gradle 8.11.1

## Setup & Build

### 1. Open in Android Studio

Open the `grain-android-app` folder as an Android Studio project.

### 2. Build the Project

```bash
./gradlew build
```

### 3. Run on Emulator/Device

```bash
./gradlew installDebug
```

Or use Android Studio's Run button.

## Project Structure

```
grain-android-app/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/grain/app/
│   │       │   └── MainActivity.kt
│   │       ├── res/
│   │       │   ├── values/
│   │       │   │   ├── strings.xml
│   │       │   │   ├── colors.xml
│   │       │   │   └── styles.xml
│   │       │   ├── drawable/
│   │       │   ├── mipmap-anydpi-v26/
│   │       │   └── xml/
│   │       │       └── network_security_config.xml
│   │       └── AndroidManifest.xml
│   └── build.gradle.kts
├── gradle/
│   └── wrapper/
├── build.gradle.kts
├── settings.gradle.kts
└── gradle.properties
```

## Configuration

### Changing the Backend URL

Edit `MainActivity.kt` and update the `START_URL` constant:

```kotlin
private const val START_URL = "http://13.201.13.214/"
```

### Network Security

The app allows cleartext (HTTP) traffic to `13.201.13.214` and `localhost`. This is configured in `app/src/main/res/xml/network_security_config.xml`.

## Debugging

### Enable Logging

WebView debugging is available through Chrome DevTools:

1. Navigate to `chrome://inspect` in Chrome desktop browser
2. Select your app from the list
3. View console and network requests

## App Permissions

- `INTERNET` - Required to fetch content from the Grain backend

## Development Notes

- The app uses Kotlin for best practices and concise code
- Extensions and lambda syntax are used for cleaner code structure
- Cookie management is enabled for session handling
- JavaScript is enabled in WebView settings for interactive features

## Building & Distributing

### Create Release Build

```bash
./gradlew bundleRelease
```

This generates an App Bundle (`.aab`) file that can be uploaded to Google Play Store.

### Sign APK

Configure signing in `app/build.gradle.kts` and build:

```bash
./gradlew assembleRelease
```

## Troubleshooting

### App crashes on startup
- Ensure backend is running at `http://13.201.13.214/`
- Check that the device/emulator has internet access
- View logs in Android Studio's Logcat window

### WebView shows blank page
- Check network connectivity
- Verify backend is accessible
- Enable verbose logging in MainActivity

### SSL Certificate Errors
- Network security config is set to allow cleartext for development
- For production, use HTTPS and update the security config

## License

This project is part of the Grain application suite.
