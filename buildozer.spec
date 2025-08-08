[app]
title = Aurelia
package.name = aurelia
package.domain = org.aurelia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
requirements = python3,kivy,packaging,colorama,openssl,pyopenssl,requests,cython
orientation = portrait
fullscreen = 1
osx.python_version = 3
osx.kivy_version = 2.2.1
icon.filename = assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 25b
android.ndk_path =
android.sdk_path =
android.private_storage = False  # auf False, damit wir Zugriff auf externe Storage haben
android.package_format = apk
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,FOREGROUND_SERVICE,MANAGE_EXTERNAL_STORAGE  # MANAGE_EXTERNAL_STORAGE für neuere Android-Versionen
android.arch = arm64-v8a
android.gradle_dependencies =
android.accept_sdk_license = true
android.build_tools_version = 34.0.0

[android]
# Intent Filter kannst du so lassen oder aktivieren, wenn nötig
# android.manifest.intent_filters = <intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter>
