import os
import unreal

def CreateBaseImportTask(importTask):
    importTask = unreal.AssetImportTask()
    importTask.filename = importTask

    fileName = os.path.basename(importTask).split('.')[0]
    importTask.destination_path = '/Game/'  + fileName

    importTask.automated = True
    importTask.save = True
    importTask.replace_existing = True

    return importTask

def ImportSkeletalMesh(meshPath):
    importTask = CreateBaseImportTask(meshPath)

    importOption = unreal.FbxImportUI()
    importOption.import_mesh = True
    importOption.skeletal_mesh_import_data.set_editor_property("import_morph_targets", True)
    importOption.skeletal_mesh_import_data.set_editor_property("use_t0_as_ref_pose", True)

    importTask.options = [importOption]

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([importTask])
    return importTask.get_objects()[-1]

def ImportAnimation(mesh, animPath):
    importTask = CreateBaseImportTask(animPath)
    meshDir = os.path.dirname(mesh.get_path_name())
    importTask.destination_path = meshDir + "animations"

    importOptions = unreal.FbxImportUI()
    importOptions.import_mesh = False
    importOptions.import_as_skeletal = True
    importOptions.import_animations = True
    importOptions.skeleton = mesh.skeleton

    importOptions.set_editor_property('automated_import_should_detect_type', False)
    importOptions.set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    importOptions.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_ANIMATION)

    importTask.options = importOptions

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([importTask])


def ImportMeshAndAnimations(meshPath, animDir):
    mesh = ImportSkeletalMesh(meshPath)
    print(mesh)

    for file in os.listdir(animDir):
        animPath = os.path.join(animDir, file)
        ImportAnimation(mesh, animPath)
    
ImportMeshAndAnimations("D:/MayaToUETemp/Alex.fbx", "D:/MayaToUETemp/animations/")

