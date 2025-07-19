[app]

# Название приложения
title = LED Control

# Имя пакета
package.name = ledcontrol

# Домен пакета
package.domain = com.example

# Исходная директория
source.dir = .

# Включаемые расширения
source.include_exts = py,png,jpg,kv,atlas

# Версия приложения
version = 1.0.0

# Требуемые зависимости
requirements = python3,kivy,pyjnius

# Ориентация экрана
orientation = portrait

# API Android
android.api = 31

# Минимальный API
android.minapi = 21

# Разрешения
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION

# (str) Android NDK version to use
android.ndk = 23b

# (str) Android SDK version to use
#android.sdk = 28

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (list) Application requirements
#requirements = source/requirements.txt

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2