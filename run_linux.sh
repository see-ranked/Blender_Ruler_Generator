#!/bin/bash

BLENDER_PATH="{Enter your Blender Python path.}"

# bpyモジュールがインストールされているか確認
if ! $BLENDER_PATH -c "import bpy" 2>/dev/null; then
    echo "bpy module not found. Installing..."
    $BLENDER_PATH -m pip install bpy
else
    echo "bpy module is already installed."
fi

$BLENDER_PATH Blender_Ruler_Generator.py
