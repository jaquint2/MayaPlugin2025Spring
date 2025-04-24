import os
import unreal 

def importMeshAndAnimations(meshPath, animDir):
    importTask = unreal.AssetImportTask()
    importTask.filename = meshPath

    filename = os.path.basename(meshPath).split('.')[0]
    importTask.destination_path = '/Game/' = filename

    importTask.automated = True
    importTask.save = True
    importTask.replace.existing = True

    importOption = unreal.FbxImportUI()
    importOption.import_mesh = True
    importOption.import_as_skeletal = True
    importOption.skeletal_mesh.import_data.set_editor_property('import_morph_targets', True)
    importOption.skeletal_mesh.import_data.set_editor_property('use_t0_as_ref_pose', True)

    importTask.options = importOption

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([importTask])

importMeshAndAnimations("D:/MayaToUETemp/Alex.fbx", "D:/MayaToUETemp/animations/")

