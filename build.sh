#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$ROOT_DIR/build"
DIST_DIR="$ROOT_DIR/dist"
VENV="$ROOT_DIR/venv"
PYTHON="$VENV/bin/python"
PYINSTALLER="$VENV/bin/pyinstaller"
APP_NAME="TTS-Virtual-Mic"
APP_DIR="$BUILD_DIR/$APP_NAME.AppDir"

echo "=== Step 1: Clean build directories ==="
rm -rf "$BUILD_DIR" "$DIST_DIR"

echo "=== Step 2: Build with PyInstaller ==="
cd "$ROOT_DIR"
"$PYINSTALLER" --onedir \
    --name "$APP_NAME" \
    --add-data "resources:resources" \
    --add-data "voices:voices" \
    --hidden-import "PyQt5.QtCore" \
    --hidden-import "PyQt5.QtGui" \
    --hidden-import "PyQt5.QtWidgets" \
    --hidden-import "piper" \
    --hidden-import "piper.voice" \
    --hidden-import "piper.config" \
    --hidden-import "onnxruntime" \
    --hidden-import "numpy" \
    --collect-all "piper" \
    --collect-all "onnxruntime" \
    --noconfirm \
    main.py

echo "=== Step 3: Create AppDir structure ==="
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

# Copy PyInstaller output
cp -r "$DIST_DIR/$APP_NAME/"* "$APP_DIR/usr/bin/"

# Copy .desktop file
cp "$ROOT_DIR/resources/tts-virtual-mic.desktop" "$APP_DIR/usr/share/applications/"
cp "$ROOT_DIR/resources/tts-virtual-mic.desktop" "$APP_DIR/"

# Copy icon
cp "$ROOT_DIR/resources/icon.png" "$APP_DIR/usr/share/icons/hicolor/256x256/apps/tts-virtual-mic.png"
cp "$ROOT_DIR/resources/icon.png" "$APP_DIR/tts-virtual-mic.png"

# Create AppRun
cat > "$APP_DIR/AppRun" << 'APPRUN'
#!/bin/bash
SELF_DIR="$(dirname "$(readlink -f "$0")")"
export PATH="$SELF_DIR/usr/bin:$PATH"
export LD_LIBRARY_PATH="$SELF_DIR/usr/bin:$LD_LIBRARY_PATH"
export QT_QPA_PLATFORM_PLUGIN_PATH="$SELF_DIR/usr/bin/PyQt5/Qt5/plugins"
export QT_PLUGIN_PATH="$SELF_DIR/usr/bin/PyQt5/Qt5/plugins"
exec "$SELF_DIR/usr/bin/$APP_NAME" "$@"
APPRUN
sed -i "s/\$APP_NAME/$APP_NAME/g" "$APP_DIR/AppRun"
chmod +x "$APP_DIR/AppRun"

echo "=== Build complete ==="
echo "AppDir at: $APP_DIR"
echo ""
echo "To create AppImage, run:"
echo "  appimagetool $APP_DIR $APP_NAME-x86_64.AppImage"
