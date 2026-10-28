#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "NiagaraSystem.h"
#include "NiagaraEmitter.h"
#include "NiagaraEmitterHandle.h"
#include "NiagaraScript.h"
#include "NiagaraSystemFactoryNew.h"
#include "NiagaraEditorUtilities.h"
#include "NiagaraRibbonRendererProperties.h"
#include "Materials/MaterialInterface.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/FileHelper.h"
#include "NiagaraScriptSource.h"
#include "NiagaraGraph.h"
#include "NiagaraNodeFunctionCall.h"
#include "NiagaraNodeAssignment.h"
#include "ViewModels/Stack/NiagaraStackGraphUtilities.h"
#include "ViewModels/Stack/NiagaraParameterHandle.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, DragonTrailBuilder)
static const TCHAR* AssetPath=TEXT("/Game/TianNanGe/Dragon_X/EyeGlow/NS_DragonEyeTrail");
static UNiagaraSystem* FindSystem(){return LoadObject<UNiagaraSystem>(nullptr,AssetPath);}
extern "C" __declspec(dllexport) int BuildDragonEyeTrail()
{
 if(!IsInGameThread())return -1;
 auto* System=FindSystem();
 if(!System){
  auto* Source=LoadObject<UNiagaraEmitter>(nullptr,TEXT("/Niagara/DefaultAssets/Templates/Emitters/Minimal"));
  if(!Source)return -2;
  auto* Package=CreatePackage(AssetPath);
  System=NewObject<UNiagaraSystem>(Package,TEXT("NS_DragonEyeTrail"),RF_Public|RF_Standalone|RF_Transactional);
  UNiagaraSystemFactoryNew::InitializeSystem(System,true);
  FNiagaraEditorUtilities::AddEmitterToSystem(*System,*Source,Source->GetExposedVersion().VersionGuid);
  auto Instance=System->GetEmitterHandles()[0].GetInstance();auto* Data=Instance.GetEmitterData();
  TArray<UNiagaraRendererProperties*> OldRenderers=Data->GetRenderers();
  for(auto* Renderer:OldRenderers)Instance.Emitter->RemoveRenderer(Renderer,Instance.Version);
  auto* Ribbon=NewObject<UNiagaraRibbonRendererProperties>(Instance.Emitter,NAME_None,RF_Transactional);
  Instance.Emitter->AddRenderer(Ribbon,Instance.Version);
  auto* Graph=CastChecked<UNiagaraScriptSource>(Data->EmitterUpdateScriptProps.Script->GetLatestSource())->NodeGraph.Get();
  auto* Output=Graph->FindEquivalentOutputNode(ENiagaraScriptUsage::EmitterUpdateScript);
  auto* Spawn=LoadObject<UNiagaraScript>(nullptr,TEXT("/Niagara/Modules/Emitter/SpawnRate"));
  auto* RateModule=FNiagaraStackGraphUtilities::AddScriptModuleToStack(Spawn,*Output);
  auto& RatePin=FNiagaraStackGraphUtilities::GetOrCreateStackFunctionInputOverridePin(*RateModule,FNiagaraParameterHandle(*(RateModule->GetFunctionName()+TEXT(".SpawnRate"))),FNiagaraTypeDefinition::GetFloatDef(),FGuid(),FGuid());
  RatePin.DefaultValue=TEXT("90.0");
  auto* SpawnOutput=Graph->FindEquivalentOutputNode(ENiagaraScriptUsage::ParticleSpawnScript);
  TArray<FNiagaraVariable> Vars={FNiagaraVariable(FNiagaraTypeDefinition::GetFloatDef(),TEXT("Particles.RibbonWidth")),FNiagaraVariable(FNiagaraTypeDefinition::GetFloatDef(),TEXT("Particles.Lifetime"))};
  TArray<FString> Values={TEXT("2.0"),TEXT("0.8")};
  FNiagaraStackGraphUtilities::AddParameterModuleToStack(Vars,*SpawnOutput,INDEX_NONE,Values);
  FAssetRegistryModule::AssetCreated(System);
 }
 System->Modify();
 for(auto& Handle:System->GetEmitterHandles()){
  auto* Data=Handle.GetInstance().GetEmitterData();
  Data->bLocalSpace=false;
  for(auto* Renderer:Data->GetRenderers())if(auto* Ribbon=Cast<UNiagaraRibbonRendererProperties>(Renderer)){
   if(auto* Material=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/TianNanGe/Dragon_X/EyeGlow/M_DragonEyeTrail")))Ribbon->Material=Material;
  }
 }
 System->RequestCompile(false);System->MarkPackageDirty();return 0;
}
extern "C" __declspec(dllexport) int DumpDragonEyeTrail(const wchar_t* Filename)
{
 auto* System=FindSystem();if(!System)return -1;
 System->WaitForCompilationComplete(false,false);
 FString Output;
 for(auto& Handle:System->GetEmitterHandles()){
  auto* Data=Handle.GetInstance().GetEmitterData();
  Output+=FString::Printf(TEXT("Emitter %s Local=%d\n"),*Handle.GetName().ToString(),Data->bLocalSpace);
  TArray<UNiagaraScript*> Scripts;Data->GetScripts(Scripts);
  for(auto* Script:Scripts){
   Output+=FString::Printf(TEXT("SCRIPT %s\n"),*Script->GetName());
   for(auto& Var:Script->RapidIterationParameters.ReadParameterVariables()){
    Output+=Var.GetName().ToString()+TEXT(" | ")+Var.GetType().GetName();
    if(Var.GetType()==FNiagaraTypeDefinition::GetFloatDef())Output+=FString::Printf(TEXT(" = %g"),Script->RapidIterationParameters.GetParameterValue<float>(Var));
    if(Var.GetType()==FNiagaraTypeDefinition::GetVec3Def()){auto V=Script->RapidIterationParameters.GetParameterValue<FVector3f>(Var);Output+=FString::Printf(TEXT(" = %g,%g,%g"),V.X,V.Y,V.Z);}
    Output+=TEXT("\n");
   }
  }
 }
 return FFileHelper::SaveStringToFile(Output,Filename)?0:-2;
}
extern "C" __declspec(dllexport) int SetDragonTrailFloat(const wchar_t* Suffix,float Value)
{
 auto* System=FindSystem();if(!System)return -1;int Count=0;
 System->Modify();
 for(auto& Handle:System->GetEmitterHandles()){
  TArray<UNiagaraScript*> Scripts;Handle.GetInstance().GetEmitterData()->GetScripts(Scripts);
  for(auto* Script:Scripts){
   TArray<FNiagaraVariable> Vars;Script->RapidIterationParameters.GetParameters(Vars);
   for(auto& Var:Vars)if(Var.GetType()==FNiagaraTypeDefinition::GetFloatDef() && Var.GetName().ToString().EndsWith(Suffix)){
    Script->Modify();Script->RapidIterationParameters.SetParameterValue<float>(Value,Var);Count++;
   }
  }
 }
 System->MarkPackageDirty();return Count;
}
extern "C" __declspec(dllexport) int CompileDragonEyeTrail()
{
 auto* System=FindSystem();if(!System)return -1;
 System->RequestCompile(false);return 0;
}
extern "C" __declspec(dllexport) int StrengthenDragonEyeTrail()
{
 if(!IsInGameThread())return -1;
 auto* System=FindSystem();if(!System)return -2;
 System->Modify();
 FNiagaraVariable Drift(FNiagaraTypeDefinition::GetVec3Def(),TEXT("User.TrailDrift"));
 System->GetExposedParameters().SetParameterValue<FVector3f>(FVector3f(0,0,100),Drift,true);
 for(auto& Handle:System->GetEmitterHandles()){
  auto* Data=Handle.GetInstance().GetEmitterData();Data->bLocalSpace=false;
  auto* Graph=CastChecked<UNiagaraScriptSource>(Data->EmitterUpdateScriptProps.Script->GetLatestSource())->NodeGraph.Get();
  auto* SpawnOutput=Graph->FindEquivalentOutputNode(ENiagaraScriptUsage::ParticleSpawnScript);
  auto* UpdateOutput=Graph->FindEquivalentOutputNode(ENiagaraScriptUsage::ParticleUpdateScript);
  bool HasVelocity=false,HasSolver=false;
  for(auto& NodeRef:Graph->Nodes){
   auto* Node=NodeRef.Get();
   if(auto* A=Cast<UNiagaraNodeAssignment>(Node))HasVelocity|=A->FindAssignmentTarget(TEXT("Particles.Velocity"))!=INDEX_NONE;
   if(auto* F=Cast<UNiagaraNodeFunctionCall>(Node))HasSolver|=F->FunctionScript && F->FunctionScript->GetPathName().Contains(TEXT("SolveForcesAndVelocity"));
  }
  if(!HasVelocity){
   TArray<FNiagaraVariable> Vars={FNiagaraVariable(FNiagaraTypeDefinition::GetColorDef(),TEXT("Particles.Color")),FNiagaraVariable(FNiagaraTypeDefinition::GetVec3Def(),TEXT("Particles.Velocity"))};
   auto* Assignment=FNiagaraStackGraphUtilities::AddParameterModuleToStack(Vars,*SpawnOutput,INDEX_NONE,{TEXT("(R=1.0,G=1.0,B=1.0,A=1.0)"),TEXT("(X=0.0,Y=0.0,Z=100.0)")});
   auto& Pin=FNiagaraStackGraphUtilities::GetOrCreateStackFunctionInputOverridePin(*Assignment,FNiagaraParameterHandle(*(Assignment->GetFunctionName()+TEXT(".Particles.Velocity"))),FNiagaraTypeDefinition::GetVec3Def(),FGuid(),FGuid());
   TSet<FNiagaraVariableBase> Known;Known.Add(Drift);
   FNiagaraStackGraphUtilities::SetLinkedParameterValueForFunctionInput(Pin,Drift,Known);
  }
  if(!HasSolver){
   auto* Solver=LoadObject<UNiagaraScript>(nullptr,TEXT("/Niagara/Modules/Solvers/SolveForcesAndVelocity"));
   if(!Solver)return -3;
   FNiagaraStackGraphUtilities::AddScriptModuleToStack(Solver,*UpdateOutput);
  }
 }
 System->RequestCompile(false);System->MarkPackageDirty();return 0;
}
