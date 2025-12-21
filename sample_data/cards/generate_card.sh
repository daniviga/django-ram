#!/bin/bash
mkdir -p output

for img in input/*.{jpg,png}; do
  [ -e "$img" ] || continue  # skip if no files
  name=$(basename "${img%.*}").jpg
  magick convert background.png \
    \( "$img" -resize x820 \) \
    -gravity center -composite \
    -quality 85 -sampling-factor 4:4:4 \
    "output/$name"
done
