using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Globalization;

// Runs only in an isolated export project. The source checkout is never upgraded.
public static class TianNanGeExport {
    const string Out = "D:/UnrealProject/TianNanGe_UE58/Transfer";
    [Serializable] public class MaterialInfo { public string id,name,source; public Color color=Color.white; public float metallic,smoothness; public string baseTexture,normalTexture,maskTexture; public bool transparent; }
    [Serializable] public class NodeInfo { public string name,path,mesh; public string[] materials; public Vector3 position,scale,forward,up,sourceBoundsSize,poseBoundsSize; public Quaternion rotation; public bool skinned,collider; }
    [Serializable] public class CameraInfo { public Vector3 position,forward,up; public float fov,aspect; }
    [Serializable] public class LightInfo { public string name; public Vector3 forward; public Color color; public float intensity; }
    [Serializable] public class Manifest { public string unityVersion; public List<NodeInfo> nodes=new List<NodeInfo>(); public List<MaterialInfo> materials=new List<MaterialInfo>(); public List<LightInfo> lights=new List<LightInfo>(); public CameraInfo camera; public List<string> warnings=new List<string>(); }
    static Manifest data=new Manifest();
    static Dictionary<Mesh,string> meshes=new Dictionary<Mesh,string>();
    static Dictionary<Material,string> materials=new Dictionary<Material,string>();
    static Dictionary<Mesh,Bounds> poseBounds=new Dictionary<Mesh,Bounds>();
    static string F(float v) {return v.ToString("R",CultureInfo.InvariantCulture);}
    static Vector3 Convert(Vector3 v) {return new Vector3(v.z,v.x,v.y);}
    static string PathOf(Transform t) {return t.parent==null?t.name:PathOf(t.parent)+"/"+t.name;}
    public static void Run() {
        try {
            Directory.CreateDirectory(Out+"/Meshes");
            var scene=EditorSceneManager.OpenScene("Assets/TianNanGe/Scenes/TianNanGe_Main.unity");
            data.unityVersion=Application.unityVersion;
            if(UnityEngine.Object.FindObjectsByType<ParticleSystem>(FindObjectsSortMode.None).Length>0) data.warnings.Add("Particle systems are not exported; snow requires a Niagara implementation.");
            AnimationMode.StartAnimationMode();
            foreach(var animator in UnityEngine.Object.FindObjectsByType<Animator>(FindObjectsSortMode.None)) {
                try {
                    var clips=animator.runtimeAnimatorController?animator.runtimeAnimatorController.animationClips:new AnimationClip[0];
                    var clip=clips.FirstOrDefault(c=>c.name.ToLowerInvariant().Contains("idle")) ?? clips.FirstOrDefault();
                    if(clip) {AnimationMode.BeginSampling();AnimationMode.SampleAnimationClip(animator.gameObject,clip,0);AnimationMode.EndSampling();}
                } catch(Exception e) {data.warnings.Add("Animator: "+e.Message);}
            }
            foreach(var root in scene.GetRootGameObjects()) foreach(var renderer in root.GetComponentsInChildren<Renderer>(false)) {
                if(!renderer.enabled || !renderer.gameObject.activeInHierarchy || renderer is ParticleSystemRenderer) continue;
                Mesh mesh=null; bool skinned=false;
                if(renderer is SkinnedMeshRenderer skin) {mesh=MakePoseMesh(skin); skinned=true;}
                else {var mf=renderer.GetComponent<MeshFilter>(); if(mf) mesh=mf.sharedMesh;}
                if(!mesh || mesh.vertexCount==0) {data.warnings.Add("Missing/empty mesh: "+PathOf(renderer.transform));continue;}
                try {
                    string id;
                    if(!meshes.TryGetValue(mesh,out id)) {id="SM_"+meshes.Count.ToString("D4"); WriteMesh(mesh,id); meshes.Add(mesh,id);}
                    var t=renderer.transform;
                    data.nodes.Add(new NodeInfo {name=t.name,path=PathOf(t),mesh=id,materials=renderer.sharedMaterials.Select(MaterialId).ToArray(),position=Convert(t.position)*100,scale=Convert(t.lossyScale),rotation=new Quaternion(t.rotation.z,t.rotation.x,t.rotation.y,t.rotation.w),forward=Convert(t.forward),up=Convert(t.up),sourceBoundsSize=Convert(renderer.bounds.size)*100,poseBoundsSize=skinned?Convert(poseBounds[mesh].size)*100:Vector3.zero,skinned=skinned,collider=renderer.GetComponent<Collider>()!=null});
                } catch(Exception e) {data.warnings.Add(PathOf(renderer.transform)+": "+e.Message);}
            }
            var cam=Camera.main ?? UnityEngine.Object.FindFirstObjectByType<Camera>();
            if(cam) data.camera=new CameraInfo {position=Convert(cam.transform.position)*100,forward=Convert(cam.transform.forward),up=Convert(cam.transform.up),fov=cam.fieldOfView,aspect=1280f/620f};
            foreach(var light in UnityEngine.Object.FindObjectsByType<Light>(FindObjectsSortMode.None)) if(light.type==LightType.Directional && light.enabled) data.lights.Add(new LightInfo{name=light.name,forward=Convert(light.transform.forward),color=light.color,intensity=light.intensity});
            File.WriteAllText(Out+"/scene.json",JsonUtility.ToJson(data,true));
            AnimationMode.StopAnimationMode();
            Debug.Log("TIANNANGE_EXPORT_OK nodes="+data.nodes.Count+" meshes="+meshes.Count+" materials="+materials.Count);
            EditorApplication.Exit(0);
        } catch(Exception e) {Debug.LogException(e); File.WriteAllText(Out+"/error.txt",e.ToString()); EditorApplication.Exit(1);}
    }
    static string MaterialId(Material mat) {
        if(!mat) return "";
        if(materials.TryGetValue(mat,out var existing)) return existing;
        string id="M_"+materials.Count.ToString("D3"); materials.Add(mat,id);
        var info=new MaterialInfo{id=id,name=mat.name,source=AssetDatabase.GetAssetPath(mat)};
        // Read saved properties even when HDRP's shader is absent in this export-only project.
        var so=new SerializedObject(mat); var saved=so.FindProperty("m_SavedProperties");
        var colors=saved.FindPropertyRelative("m_Colors");
        for(int i=0;i<colors.arraySize;i++) {var p=colors.GetArrayElementAtIndex(i); var key=p.FindPropertyRelative("first").stringValue; if(key=="_BaseColor" || key=="_Color") info.color=p.FindPropertyRelative("second").colorValue;}
        var floats=saved.FindPropertyRelative("m_Floats");
        for(int i=0;i<floats.arraySize;i++) {var p=floats.GetArrayElementAtIndex(i); var key=p.FindPropertyRelative("first").stringValue; float v=p.FindPropertyRelative("second").floatValue; if(key=="_Metallic") info.metallic=v; if(key=="_Smoothness" || key=="_Glossiness") info.smoothness=v; if(key=="_SurfaceType") info.transparent=v>0;}
        var tex=saved.FindPropertyRelative("m_TexEnvs");
        for(int i=0;i<tex.arraySize;i++) {var p=tex.GetArrayElementAtIndex(i); var key=p.FindPropertyRelative("first").stringValue; var obj=p.FindPropertyRelative("second").FindPropertyRelative("m_Texture").objectReferenceValue; if(!obj)continue; string path=AssetDatabase.GetAssetPath(obj); if(key=="_BaseColorMap" || key=="_MainTex")info.baseTexture=path; if(key=="_NormalMap" || key=="_BumpMap")info.normalTexture=path; if(key=="_MaskMap")info.maskTexture=path;}
        data.materials.Add(info); return id;
    }
    public static Mesh MakePoseMesh(SkinnedMeshRenderer skin) {
        var result=new Mesh();skin.BakeMesh(result,false);
        // Use the skinning matrices as the source of truth for positions. Parent
        // scale in imported FBX rigs can otherwise be baked a second time by BakeMesh.
        var source=skin.sharedMesh;var bones=skin.bones;var binds=source.bindposes;
        var weights=source.boneWeights;var vertices=source.vertices;
        if(weights.Length!=vertices.Length || bones.Length==0) return result;
        var matrices=new Matrix4x4[bones.Length];
        for(int i=0;i<bones.Length;i++) matrices[i]=skin.worldToLocalMatrix*bones[i].localToWorldMatrix*binds[i];
        for(int i=0;i<vertices.Length;i++) {
            var w=weights[i];var v=vertices[i];
            vertices[i]=matrices[w.boneIndex0].MultiplyPoint3x4(v)*w.weight0+matrices[w.boneIndex1].MultiplyPoint3x4(v)*w.weight1+matrices[w.boneIndex2].MultiplyPoint3x4(v)*w.weight2+matrices[w.boneIndex3].MultiplyPoint3x4(v)*w.weight3;
        }
        result.vertices=vertices;result.RecalculateBounds();
        var worldBounds=new Bounds(skin.transform.TransformPoint(vertices[0]),Vector3.zero);
        foreach(var v in vertices)worldBounds.Encapsulate(skin.transform.TransformPoint(v));
        poseBounds[result]=worldBounds;return result;
    }
    static void WriteMesh(Mesh mesh,string id) {
        // OBJ vertices are already in Unreal centimeters/Z-up. Import conversion is disabled.
        using(var w=new StreamWriter(Out+"/Meshes/"+id+".obj")) {
            w.WriteLine("o "+id);
            // FBX SDK's OBJ reader always negates Y, even with convert_scene=false.
            foreach(var p in mesh.vertices) {var v=Convert(p)*100;w.WriteLine("v "+F(v.x)+" "+F(-v.y)+" "+F(v.z));}
            var uv=mesh.uv; var normal=mesh.normals;
            // UE 5.8's OBJ translator asserts on v//vn when the source mesh has no UVs.
            // Untextured procedural meshes receive an explicit zero UV channel.
            if(uv.Length!=mesh.vertexCount) uv=new Vector2[mesh.vertexCount];
            foreach(var v in uv)w.WriteLine("vt "+F(v.x)+" "+F(v.y));
            foreach(var p in normal) {var v=Convert(p);w.WriteLine("vn "+F(v.x)+" "+F(-v.y)+" "+F(v.z));}
            bool hasUV=uv.Length==mesh.vertexCount,hasNormals=normal.Length==mesh.vertexCount;
            for(int s=0;s<mesh.subMeshCount;s++) {
                w.WriteLine("usemtl Slot_"+s); var tri=mesh.GetTriangles(s);
                for(int i=0;i<tri.Length;i+=3) {
                    // Unity and OBJ front-face winding differ.
                    int[] order={tri[i]+1,tri[i+2]+1,tri[i+1]+1};
                    w.Write("f"); foreach(int n in order) w.Write(" "+n+(hasUV?"/"+n:(hasNormals?"/":""))+(hasNormals?"/"+n:"")); w.WriteLine();
                }
            }
        }
    }
}
