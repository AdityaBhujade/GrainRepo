# How to Build and Run Grain Android App

## Prerequisites

1. **Android Studio** - Download from https://developer.android.com/studio
2. **Android SDK** - API Level 35 (will be installed via Android Studio)
3. **Java 17** - Android Studio bundles this

## Step 1: Open Project in Android Studio

1. Open Android Studio
2. Click **File** → **Open**
3. Navigate to `D:\GrainRepo\grain-android-app`
4. Click **OK**

Android Studio will automatically:
- Download required SDK components
- Set up Gradle wrapper
- Build the project

## Step 2: Wait for Gradle Sync

Android Studio will ask to "Sync Now" - click it to complete the setup.

## Step 3: Run on Device or Emulator

### Option A: Use Emulator (Easiest)

1. Click **Tools** → **Device Manager** → **Create Device**
2. Select a device (e.g., "Pixel 6")
3. Select API Level 35
4. Click **Finish**
5. In Android Studio, click the **Run** button (green triangle)
6. Select your created device
7. Click **OK**

### Option B: Use Physical Device

1. Connect Android device via USB
2. Enable Developer Mode:
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times
   - Go to Developer Options → Enable USB Debugging
3. Click the **Run** button in Android Studio
4. Select your device
5. Click **OK**

## Step 4: App Should Launch

The app will load `http://13.201.13.214/` automatically.

**Make sure:**
- Your backend is running on EC2
- Your Windows machine has internet access to EC2

## Build Commands (Terminal)

From the `grain-android-app` folder:

```powershell
# Build debug APK
.\gradlew build

# Install on connected device
.\gradlew installDebug

# Build release (for Google Play Store)
.\gradlew bundleRelease

# Clean build
.\gradlew clean
./gradlew build
```

## Troubleshooting

### App crashes immediately
- Check EC2 backend is running: `curl http://13.201.13.214/`
- Check device/emulator has internet access
- View logs in Android Studio: **View** → **Tool Windows** → **Logcat**

### Gradle sync fails
- Click **File** → **Invalidate Caches** → **Invalidate and Restart**
- Or manually download SDK in **Tools** → **SDK Manager**

### APK installation fails
- For emulator: Delete and recreate the emulator
- For device: Uninstall old app: `./gradlew uninstallDebug`

### WebView shows blank page
- Check that `http://13.201.13.214/` loads in your PC browser
- Check network connectivity on device
- Check firewall/security settings on EC2

## App Features

- ✅ Loads Grain web interface
- ✅ Full WebView functionality (JavaScript enabled)
- ✅ Cookie/session support
- ✅ Back button navigation
- ✅ Responsive design

## Next Steps

After building successfully:

1. Test on both emulator and real device
2. To change backend URL: Edit `MainActivity.kt` and change `START_URL`
3. To customize colors: Edit `app/src/main/res/values/colors.xml`
4. To change app name: Edit `app/src/main/res/values/strings.xml`

## Publishing to Google Play Store

1. Create a Google Play Developer account ($25 one-time fee)
2. Generate signed release APK/Bundle:
   ```
   ./gradlew bundleRelease
   ```
3. Upload the `.aab` file to Google Play Console

For detailed instructions, see: https://developer.android.com/studio/publish
