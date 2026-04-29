import bpy

def create_ruler(
    length=10.0, 
    tick_interval=0.1, 
    label_interval=1.0, 
    font_path=None, 
    font_size=0.2
):
    """
    Blenderで定規を作成する関数
    :param length: 定規の全長
    :param tick_interval: 小さな目盛の間隔
    :param label_interval: 数字が入る目盛の間隔
    :param font_path: フォントファイルのパス (Noneの場合はデフォルト)
    :param font_size: 文字サイズ
    """
    
    # --- 設定 ---
    ruler_width = 0.5  # 定規の幅（奥行き）
    ruler_thickness = 0.05 # 定規の厚み
    tick_length_small = 0.1 # 小さな目盛の長さ
    tick_length_large = 0.2 # 数字がある目盛の長さ
    label_offset = -0.3 # 文字の位置オフセット（Y方向）

    # コレクションを作成して整理する
    collection_name = "Ruler_Collection"
    if collection_name in bpy.data.collections:
        bpy.data.collections.remove(bpy.data.collections[collection_name], do_unlink=True)
    
    ruler_coll = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(ruler_coll)

    # 1. 定規の本体（ベース板）を作成
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    body = bpy.context.active_object
    body.name = "Ruler_Body"
    body.scale = (length, ruler_width, ruler_thickness)
    body.location = (length / 2, 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ruler_coll.objects.link(body)
    bpy.context.scene.collection.objects.unlink(body)

    # 目盛線を格納するためのリスト（後で結合して軽量化するため）
    tick_objects = []

    # 2. 目盛線とラベルの作成
    current_pos = 0.0
    while current_pos <= length + 0.001: # 浮動小数点の誤差対策
        is_label_tick = (round(current_pos / label_interval, 5) % 1 == 0)
        t_len = tick_length_large if is_label_tick else tick_length_small
        
        # 目盛線の作成
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        tick = bpy.context.active_object
        tick.name = f"Tick_{current_pos:.2f}"
        tick.scale = (0.01, t_len, ruler_thickness) 
        # 位置調整: 本体の上に配置し、Y軸方向に伸ばす
        tick.location = (current_pos, -ruler_width/2 + t_len/2, 0)
        
        ruler_coll.objects.link(tick)
        bpy.context.scene.collection.objects.unlink(tick)
        tick_objects.append(tick)

        # ラベル（テキスト）の作成
        if is_label_tick:
            bpy.ops.object.text_add(location=(current_pos, label_offset, 0))
            txt = bpy.context.active_object
            txt.name = f"Label_{current_pos:.2f}"
            txt.data.body = str(int(round(current_pos)))
            
            # フォント設定
            txt.data.size = font_size
            txt.data.align_x = 'CENTER'
            txt.data.align_y = 'CENTER'
            if font_path:
                try:
                    font_data = bpy.data.fonts.load(font_path)
                    txt.data.font = font_data
                except:
                    print(f"Font not found at {font_path}")

            ruler_coll.objects.link(txt)
            bpy.context.scene.collection.objects.unlink(txt)

        current_pos += tick_interval

    # 目盛線を一つに結合してオブジェクト数を減らす（最適化）
    bpy.ops.object.select_all(action='DESELECT')
    for obj in tick_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = tick_objects[0]
    bpy.ops.object.join()
    bpy.context.active_object.name = "Ruler_Ticks"

# ==========================================
# 実行パラメータの設定
# ==========================================
create_ruler(
    length=20.0,            # 全長
    tick_interval=0.1,      # 小目盛の間隔 (0.1 = 10cmごと)
    label_interval=1.0,     # 数字の間隔 (1.0 = 1mごと)
    font_path="C:/Windows/Fonts/arial.ttf", # Windowsの例。Macなら /Library/Fonts/... 等に変更してください
    font_size=0.3          # フォントサイズ
)
