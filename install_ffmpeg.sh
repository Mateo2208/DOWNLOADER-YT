#!/bin/bash
set -e

# Descargar y extraer ffmpeg
FFMPEG_VERSION="4.3.1"
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-${FFMPEG_VERSION}-static.tar.xz -o ffmpeg.tar.xz
tar -xf ffmpeg.tar.xz
rm ffmpeg.tar.xz
mv ffmpeg-*-static/ffmpeg /app/bin/
mv ffmpeg-*-static/ffprobe /app/bin/
chmod +x /app/bin/ffmpeg
chmod +x /app/bin/ffprobe
