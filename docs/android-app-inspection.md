# Inspecting the Formula 1 Android App

## Prerequisites

* Ubuntu 18.04
* Android Studio 4
* mitmproxy (https://mitmproxy.org/)
* Add Android Sdk tools to `PATH`:
  ```bash
  # Android Sdk
  ANDROID_SDK_ROOT=~/Android/Sdk
  export PATH=$PATH:$ANDROID_SDK_ROOT/build-tools/29.0.2
  export PATH=$PATH:$ANDROID_SDK_ROOT/platform-tools
  export PATH=$PATH:$ANDROID_SDK_ROOT/tools
  ```

## Download and patch APK

* Open Android Virtual Device Manager and start a device (ARM64) with Play Store.
* Install the Formula 1-App from the Play Store.
* Install [Split APKs Installer (SAI)](https://play.google.com/store/apps/details?id=com.aefyr.sai)
  and backup (export) the Formula 1 app to the `Downloads` folder.
* Download the exported `*.apks` file:
```bash
adb pull /sdcard/Download/Formula\ 1_com,softpauer,f1timingapp2014,basic_11,0,1395.apks
mv Formula\ 1_com,softpauer,f1timingapp2014,basic_11,0,1395.apks com.softpauer.f1timingapp2014.apks
```
* Patch the APK:
```bash
npx apk-mitm com.softpauer.f1timingapp2014.apks
```
* Push the patched APK file back to the virtual device:
```shell
adb push com.softpauer.f1timingapp2014-patched.apks /sdcard/Download/
```
* Uninstall the original Formula 1 app.
* Install the patched APK with SAI.

## Inspect traffic

* Start mitmproxy by running `mitmweb`.
* Start the app on your virtual device. Add the proxy config to the emulator settings.
  (Your IP [`ip a`] and port `8080`)
* Install the mitm certificate inside Android by visiting [mitm.it](mitm.it).
* You should now be able to inspect all network traffic.
