import bpy
import os

def move_to_collection(obj, target_coll):
    """オブジェクトを現在の全コレクションから外し、指定のコレクションのみに所属させる"""
    for coll in obj.users_collection:
        coll.objects.unlink(obj)
    target_coll.objects.link(obj)

def create_material(name, color):
    """指定した名前と色のマテリアルを作成して返す"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    # Principled BSDFノードを探してベースカラーを設定
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
    return mat

def create_ruler(
    length=10.0, 
    tick_interval=0.1, 
    label_interval=1.0, 
    font_path=None, 
    font_size=0.2,
    body_color=(0.8, 0.8, 0.8, 1.0),  # デフォルト: 薄いグレー (RGBA)
    tick_color=(0.1, 0.1, 0.1, 1.0)   # デフォルト: 濃いグレー (RGBA)
):
    # シーン内の既存のオブジェクトをすべて削除（初期化）
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # --- 設定 ---
    ruler_width = 0.5
    ruler_thickness = 0.05
    tick_length_small = 0.1
    tick_length_large = 0.2
    label_offset = 0.1

    collection_name = "Ruler_Collection"
    if collection_name in bpy.data.collections:
        bpy.data.collections.remove(bpy.data.collections[collection_name], do_unlink=True)
    
    ruler_coll = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(ruler_coll)

    # 1. 定規の本体を作成
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    body = bpy.context.active_object
    body.name = "Ruler_Body"
    body.scale = (length, ruler_width, ruler_thickness)
    body.location = (length / 2, 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # 本体にマテリアルを適用
    body_mat = create_material("Mat_RulerBody", body_color)
    body.data.materials.append(body_mat)

    move_to_collection(body, ruler_coll)

    tick_objects = []

    # 2. 目盛線とラベルの作成
    current_pos = 0.0
    while current_pos <= length + 0.001:
        is_label_tick = (round(current_pos / label_interval, 5) % 1 == 0)
        t_len = tick_length_large if is_label_tick else tick_length_small
        
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        tick = bpy.context.active_object
        tick.name = f"Tick_{current_pos:.2f}"
        tick.scale = (0.01, t_len, ruler_thickness) 
        tick.location = (current_pos, -ruler_width/2 + t_len/2, 0.0001)
        
        ruler_coll.objects.link(tick)
        tick_objects.append(tick)

        # ラベル（テキスト）の作成
        if is_label_tick:
            bpy.ops.object.text_add(location=(current_pos, label_offset, ruler_thickness/2+0.0001))
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

            # 結合した目盛線にマテリアルを適用
            label_mat = create_material("Mat_LabelTicks", tick_color)
            txt.data.materials.append(label_mat)

            ruler_coll.objects.link(txt)

        current_pos += tick_interval

    # 目盛線を一つに結合してオブジェクト数を減らす（最適化）
    bpy.ops.object.select_all(action='DESELECT')
    for obj in tick_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = tick_objects[0]
    bpy.ops.object.join()
    
    ticks_combined = bpy.context.active_object
    ticks_combined.name = "Ruler_Ticks"

    # 結合した目盛線にマテリアルを適用
    tick_mat = create_material("Mat_RulerTicks", tick_color)
    ticks_combined.data.materials.append(tick_mat)

def save_blender_file(filepath):
    try:
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
        print(f"ファイルが正常に保存されました: {filepath}")
    except Exception as e:
        print(f"保存中にエラーが発生しました: {e}")

# ==========================================
# 実行パラメータの設定
# ==========================================
if __name__ == "__main__":
    # 例: 本体を黄色(1, 1, 0)、目盛りを黒色(0, 0, 0)で作成する場合
    create_ruler(
        length=10.0, 
        body_color=(1.0, 0.8, 0.0, 1.0), # Yellowish
        tick_color=(0.0, 0.0, 0.0, 1.0)  # Black
    )
  
    save_path = os.path.join(os.path.expanduser("./"), "simple_model.blend") 
    save_blender_file(save_path)

