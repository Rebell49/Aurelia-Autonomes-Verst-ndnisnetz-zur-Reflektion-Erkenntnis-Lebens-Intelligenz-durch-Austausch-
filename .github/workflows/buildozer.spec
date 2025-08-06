[app]
title = Aurelia
package.name = aurelia
package.domain = org.aurelia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
requirements = python3,kivy,packaging
orientation = portrait
fullscreen = 1
osx.python_version = 3
osx.kivy_version = 2.2.1
icon.filename = assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_path = 
android.sdk_path = 
android.private_storage = True
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,FOREGROUND_SERVICE
android.arch = arm64-v8a
android.gradle_dependencies = 
android.accept_sdk_license = true
android.build_tools_version = 34.0.0


[android]
android.manifest.intent_filters = 
