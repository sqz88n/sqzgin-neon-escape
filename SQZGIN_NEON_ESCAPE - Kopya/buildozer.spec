[app]

title = Neon Escape
package.name = sqspace
package.domain = org.sqzgin
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,pygame
orientation = portrait
fullscreen = 1

android.permissions = INTERNET, FOREGROUND_SERVICE
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
build_dir = ./.buildozer
# p4a sürümünü AAB destekleyen master dala sabitleyelim:
p4a.branch = master