# Inspecting the Formula 1 Android App

## Prerequisites

* Ubuntu 18.04
* Android Studio 3 (Emulator >= 30.0.0 for ARM binary support)
* Apktool (https://ibotpeaches.github.io/Apktool/)
* mitmproxy (https://mitmproxy.org/)
* Add Android Sdk tools to `PATH`:
  ```bash
  # Android Sdk
  ANDROID_SDK_ROOT=~/Android/Sdk
  export PATH=$PATH:$ANDROID_SDK_ROOT/build-tools/29.0.2
  export PATH=$PATH:$ANDROID_SDK_ROOT/platform-tools
  export PATH=$PATH:$ANDROID_SDK_ROOT/tools
  ```

## Download APK

Install the Formula 1-App on your Android phone.

```bash
# Find APK on phone
adb shell pm list packages | grep f1
adb shell pm path com.softpauer.f1timingapp2014.basic

# Download APK from phone
adb pull /data/app/com.softpauer.f1timingapp2014.basic-5_5xt0A4JQp9O0bhh2I-5A==/base.apk
mv base.apk com.softpauer.f1timingapp2014.basic.apk
```

## Enable debug mode and disable certificate pinning

```bash
# Decompile APK
apktool d com.softpauer.f1timingapp2014.basic.apk

# Add `android:debuggable="true"` to the <application> element
vi com.softpauer.f1timingapp2014.basic/AndroidManifest.xml

# Compile
apktool b com.softpauer.f1timingapp2014.basic

# Sign APK (https://developer.android.com/studio/build/building-cmdline#sign_cmdline)
cd com.softpauer.f1timingapp2014.basic/dist/
keytool -genkey -v -keystore release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias test
zipalign -v -p 4 com.softpauer.f1timingapp2014.basic.apk com.softpauer.f1timingapp2014.basic.aligned.apk
apksigner sign --ks release-key.jks --out com.softpauer.f1timingapp2014.basic.aligned.signed.apk com.softpauer.f1timingapp2014.basic.aligned.apk
```

## Inspect traffic

* Start mitmproxy by running `mitmweb`.
* Open Android Studio and select "Profile or debug APK".
  Select the previously generated file `com.softpauer.f1timingapp2014.basic.aligned.signed.apk`.
* Make sure to have a device in AVD Manager. (You will get a `INSTALL_FAILED_NO_MATCHING_ABIS` 
  error if you try to run the app on non-ARM compatible x86_64 image.)
* Click the "Run" button. Add the proxy config to the emulator settings.
  (Your IP [`ip a`] and port `8080`)
* Install the mitm certificate inside Android by visiting [mitm.it](mitm.it).
* You should now be able to inspect all network traffic.
