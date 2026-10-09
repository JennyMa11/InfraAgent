#!/bin/zsh
set -euo pipefail

project_root="$(cd "$(dirname "$0")/../.." && pwd)"
bundle="$project_root/dist/InfraLens.app"
backend="${INFRA_DESKTOP_BACKEND:-bge}"
rerank="${INFRA_DESKTOP_RERANK:-1}"
index_directory="${INFRA_DESKTOP_INDEX:-$project_root/data/desktop-bge}"
port="${INFRA_DESKTOP_PORT:-18774}"

if [[ "$backend" != "demo" && "$backend" != "bge" ]]; then
    print -u2 "INFRA_DESKTOP_BACKEND must be demo or bge"
    exit 2
fi
if [[ "$rerank" != "0" && "$rerank" != "1" ]]; then
    print -u2 "INFRA_DESKTOP_RERANK must be 0 or 1"
    exit 2
fi
if ! [[ "$port" =~ '^[0-9]+$' ]] || (( port < 1 || port > 65535 )); then
    print -u2 "INFRA_DESKTOP_PORT must be between 1 and 65535"
    exit 2
fi

mkdir -p "$bundle/Contents/MacOS" "$bundle/Contents/Resources"
swiftc -O -parse-as-library "$project_root/desktop/macos/InfraLens.swift" \
    -o "$bundle/Contents/MacOS/InfraLens" \
    -framework AppKit -framework SwiftUI -framework Carbon

cat > "$bundle/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleIdentifier</key><string>dev.infrarag.InfraLens</string>
  <key>CFBundleName</key><string>Infra Lens</string>
  <key>CFBundleExecutable</key><string>InfraLens</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>0.1.0</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST

/usr/bin/python3 - "$bundle/Contents/Resources/desktop.json" \
    "$project_root" "$index_directory" "$backend" "$rerank" "$port" <<'PY'
import json
import sys

path, root, index, backend, rerank, port = sys.argv[1:]
with open(path, "w", encoding="utf-8") as output:
    json.dump(
        {
            "projectRoot": root,
            "indexDirectory": index,
            "backend": backend,
            "rerank": rerank == "1",
            "port": int(port),
        },
        output,
        ensure_ascii=False,
        indent=2,
    )
PY

print "Built $bundle"
