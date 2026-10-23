#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "Engine/Blueprint.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "EdGraphSchema_K2.h"
#include "K2Node_CallFunction.h"
#include "K2Node_VariableGet.h"
#include "K2Node_FunctionEntry.h"
#include "K2Node_IfThenElse.h"
#include "K2Node_Event.h"
#include "Components/HeterogeneousVolumeComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/KismetSystemLibrary.h"
#include "GameFramework/Actor.h"
#include "Editor.h"
#include "UnrealClient.h"
#include "ImageUtils.h"
#include "Misc/FileHelper.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, CloudBlueprintBuilder)

// Read the existing render target. No SceneCapture, high-resolution render,
// viewport resize, actor lock, focus change or injected UI input is involved.
extern "C" __declspec(dllexport) int SaveCurrentEditorViewport(const wchar_t* Filename)
{
 if(!IsInGameThread() || !GEditor) return -1;
 FViewport* Viewport=GEditor->GetActiveViewport();
 if(!Viewport) return -2;
 const FIntPoint Size=Viewport->GetSizeXY();
 if(Size.X<=0 || Size.Y<=0) return -3;
 // Background editor viewports may retain their last presented frame. Render
 // the current state explicitly, without presenting or activating the window.
 Viewport->Draw(false);
 TArray<FColor> Pixels;
 if(!GetViewportScreenShot(Viewport,Pixels)) return -4;
 for(FColor& Pixel:Pixels) Pixel.A=255;
 TArray64<uint8> Png;
 FImageUtils::PNGCompressImageArray(Size.X,Size.Y,MakeArrayView(Pixels),Png);
 return FFileHelper::SaveArrayToFile(Png,Filename)?0:-5;
}

// Extend the existing graph in place. Existing references, variables and MID
// reuse are retained; the saved Blueprint uses only native Engine nodes.
extern "C" __declspec(dllexport) int AddCloudOpacityControls()
{
 auto* BP=LoadObject<UBlueprint>(nullptr,TEXT("/Game/TianNanGe/CloudSea/Blueprints/BP_CloudSeaController"));
 if(!BP) return -1;
 UEdGraph* Graph=nullptr;
 for(UEdGraph* G:BP->FunctionGraphs) if(G->GetFName()==TEXT("ApplyCloudParameters")) Graph=G;
 if(!Graph) return -2;
 UK2Node_CallFunction* Create=nullptr; UK2Node_CallFunction* Color=nullptr;
 int Found=0;
 for(UEdGraphNode* Node:Graph->Nodes) if(auto* Call=Cast<UK2Node_CallFunction>(Node))
 {
  auto Name=Call->FunctionReference.GetMemberName();
  if(Name==TEXT("CreateDynamicMaterialInstance")) Create=Call;
  if(Name==TEXT("SetVectorParameterValue") && Call->FindPin(TEXT("ParameterName"))->DefaultValue==TEXT("CloudAlbedo")) Color=Call;
  if(Name==TEXT("SetScalarParameterValue"))
  {
   auto* Pin=Call->FindPin(TEXT("ParameterName"));
   if(Pin && (Pin->DefaultValue==TEXT("DensityMultiplier") || Pin->DefaultValue==TEXT("InteriorDensityBoost"))) ++Found;
  }
 }
 if(Found==2) return 1;
 if(Found || !Create || !Color || Color->GetExecPin()->LinkedTo.Num()!=1) return -3;
 const auto* Schema=GetDefault<UEdGraphSchema_K2>();
 BP->Modify();Graph->Modify();
 FEdGraphPinType Real;Real.PinCategory=UEdGraphSchema_K2::PC_Real;Real.PinSubCategory=UEdGraphSchema_K2::PC_Float;
 const TCHAR* Names[]={TEXT("DensityMultiplier"),TEXT("InteriorDensityBoost")};
 UEdGraphPin* Previous=Color->GetExecPin()->LinkedTo[0];
 Previous->BreakLinkTo(Color->GetExecPin());
 for(int I=0;I<2;++I)
 {
  FName Name=Names[I];
  if(!FBlueprintEditorUtils::AddMemberVariable(BP,Name,Real,I==0?TEXT("1.0"):TEXT("4.0"))) return -4;
  FBlueprintEditorUtils::SetBlueprintOnlyEditableFlag(BP,Name,false);
  FBlueprintEditorUtils::SetBlueprintVariableCategory(BP,Name,nullptr,FText::FromString(TEXT("Cloud Sea|01 高度与密度")));
  FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,Name,nullptr,TEXT("DisplayName"),I==0?TEXT("整体密度倍率"):TEXT("内部厚实度"));
  FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,Name,nullptr,TEXT("ToolTip"),I==0?TEXT("0关闭云，1为原有整体密度，2为两倍。配合内部厚实度控制近处遮挡，不改变云形起伏。"):TEXT("1为原有内部密度，4为四倍。仅在云顶以下平滑增强，减少近处看穿云体；不增加云顶起伏。"));
  FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,Name,nullptr,TEXT("UIMin"),I==0?TEXT("0"):TEXT("1"));
  FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,Name,nullptr,TEXT("UIMax"),I==0?TEXT("20"):TEXT("8"));
  FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,Name,nullptr,TEXT("ClampMin"),I==0?TEXT("0"):TEXT("1"));
  FGraphNodeCreator<UK2Node_VariableGet> GetCreator(*Graph);auto* Get=GetCreator.CreateNode();
  Get->VariableReference.SetSelfMember(Name);Get->NodePosX=1800;Get->NodePosY=1600+I*300;GetCreator.Finalize();
  FGraphNodeCreator<UK2Node_CallFunction> SetCreator(*Graph);auto* Set=SetCreator.CreateNode();
  Set->SetFromFunction(UMaterialInstanceDynamic::StaticClass()->FindFunctionByName(TEXT("SetScalarParameterValue")));
  Set->NodePosX=2150;Set->NodePosY=1600+I*300;SetCreator.Finalize();
  Schema->TrySetDefaultValue(*Set->FindPinChecked(TEXT("ParameterName")),Names[I]);
  if(!Schema->TryCreateConnection(Previous,Set->GetExecPin()) ||
     !Schema->TryCreateConnection(Create->GetReturnValuePin(),Set->FindPinChecked(UEdGraphSchema_K2::PN_Self)) ||
     !Schema->TryCreateConnection(Get->GetValuePin(),Set->FindPinChecked(TEXT("Value")))) return -5;
  Previous=Set->GetThenPin();
 }
 if(!Schema->TryCreateConnection(Previous,Color->GetExecPin())) return -6;
 FBlueprintEditorUtils::SetBlueprintVariableCategory(BP,TEXT("Extinction"),nullptr,FText::FromString(TEXT("Cloud Sea|90 高级范围")));
 FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,TEXT("Extinction"),nullptr,TEXT("DisplayName"),TEXT("基础消光系数（高级）"));
 FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,TEXT("Extinction"),nullptr,TEXT("UIMax"),TEXT("3"));
 FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,TEXT("Extinction"),nullptr,TEXT("ToolTip"),TEXT("保留原始消光系数和外部蓝图兼容性。日常请调整体密度倍率与内部厚实度。"));
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
 FKismetEditorUtilities::CompileBlueprint(BP);
 return BP->Status==BS_Error ? -7:0;
}

// Preserve the existing editable graph and controls. Reuse the volume's MID
// instead of replacing it whenever Construction Script applies a slider value.
extern "C" __declspec(dllexport) int RepairCloudControllerMaterialReuse()
{
 auto* BP=LoadObject<UBlueprint>(nullptr,TEXT("/Game/TianNanGe/CloudSea/Blueprints/BP_CloudSeaController"));
 if(!BP) return -1;
 int Changed=0;
 for(UEdGraph* Graph:BP->FunctionGraphs)
 {
  if(Graph->GetFName()!=TEXT("ApplyCloudParameters")) continue;
  for(UEdGraphNode* Node:Graph->Nodes)
  {
   auto* Call=Cast<UK2Node_CallFunction>(Node);
   if(!Call || Call->FunctionReference.GetMemberName()!=TEXT("CreateDynamicMaterialInstance")) continue;
   auto* Source=Call->FindPin(TEXT("SourceMaterial"));
   if(!Source || !Source->LinkedTo.IsEmpty()) return -2;
   BP->Modify();Graph->Modify();Call->Modify();
   Source->DefaultObject=nullptr;
   Source->DefaultValue.Reset();
   Source->AutogeneratedDefaultValue.Reset();
   ++Changed;
  }
 }
 if(Changed!=1) return -3;
 FBlueprintEditorUtils::MarkBlueprintAsModified(BP);
 FKismetEditorUtilities::CompileBlueprint(BP);
 return BP->Status==BS_Error ? -4:0;
}

extern "C" __declspec(dllexport) void SetCloudControlMeta(const wchar_t* Name,const wchar_t* Group,const wchar_t* Tip,const wchar_t* Lo,const wchar_t* Hi)
{
 auto* BP=LoadObject<UBlueprint>(nullptr,TEXT("/Game/TianNanGe/CloudSea/Blueprints/BP_CloudSeaController"));
 if(!BP) return;
 FBlueprintEditorUtils::SetBlueprintVariableCategory(BP,Name,nullptr,FText::FromString(Group));
 FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,Name,nullptr,TEXT("ToolTip"),Tip);
 FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,Name,nullptr,TEXT("UIMin"),Lo);
 FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,Name,nullptr,TEXT("UIMax"),Hi);
}

// One-time editor generator. The resulting asset uses only Engine classes.
extern "C" __declspec(dllexport) int BuildCloudController()
{
 const TCHAR* Path=TEXT("/Game/TianNanGe/CloudSea/Blueprints/BP_CloudSeaController");
 if(LoadObject<UBlueprint>(nullptr,Path)) return 2; // Never overwrite an edited controller.
 auto* Package=CreatePackage(Path);
 auto* BP=FKismetEditorUtilities::CreateBlueprint(AActor::StaticClass(),Package,TEXT("BP_CloudSeaController"),BPTYPE_Normal,UBlueprint::StaticClass(),UBlueprintGeneratedClass::StaticClass());
 const auto* Schema=GetDefault<UEdGraphSchema_K2>();
 auto Var=[&](FName Name,FEdGraphPinType Type,const FString& Category,const FString& Tip){
  FBlueprintEditorUtils::AddMemberVariable(BP,Name,Type);
  FBlueprintEditorUtils::SetBlueprintOnlyEditableFlag(BP,Name,false);
  FBlueprintEditorUtils::SetBlueprintVariableCategory(BP,Name,nullptr,FText::FromString(Category));
  FBlueprintEditorUtils::SetBlueprintVariableMetaData(BP,Name,nullptr,TEXT("ToolTip"),Tip);
 };
 FEdGraphPinType Obj;Obj.PinCategory=UEdGraphSchema_K2::PC_Object;Obj.PinSubCategoryObject=UHeterogeneousVolumeComponent::StaticClass();
 Var(TEXT("TargetVolume"),Obj,TEXT("Cloud Sea|00 Target"),TEXT("Existing cloud volume component controlled by this actor."));
 FEdGraphPinType Real;Real.PinCategory=UEdGraphSchema_K2::PC_Real;Real.PinSubCategory=UEdGraphSchema_K2::PC_Float;
 const TCHAR* Names[]={TEXT("SeaLevel"),TEXT("Extinction"),TEXT("SurfaceSoftness"),TEXT("WaveHeight"),TEXT("WavePeriod"),TEXT("BillowPeriod"),TEXT("BillowStrength"),TEXT("ErosionDepth"),TEXT("DetailPeriod"),TEXT("WindSpeed"),TEXT("WindRotationDegrees"),TEXT("BridgeClearanceStrength"),TEXT("BridgeClearanceWidth"),TEXT("EdgeFade")};
 for(auto Name:Names) Var(Name,Real,TEXT("Cloud Sea"),Name);
 FEdGraphPinType Color;Color.PinCategory=UEdGraphSchema_K2::PC_Struct;Color.PinSubCategoryObject=TBaseStructure<FLinearColor>::Get();
 Var(TEXT("CloudAlbedo"),Color,TEXT("Cloud Sea|06 Color"),TEXT("Scattering albedo, still receives scene lighting."));
 auto* Graph=FBlueprintEditorUtils::CreateNewGraph(BP,TEXT("ApplyCloudParameters"),UEdGraph::StaticClass(),UEdGraphSchema_K2::StaticClass());
 FBlueprintEditorUtils::AddFunctionGraph(BP,Graph,true,static_cast<UClass*>(nullptr));
 UK2Node_FunctionEntry* Entry=nullptr;
 for(UEdGraphNode* N:Graph->Nodes) if(auto* E=Cast<UK2Node_FunctionEntry>(N)) Entry=E;
 if(!Entry) return -1;
 Entry->AddExtraFlags(FUNC_Public|FUNC_BlueprintCallable);
 Entry->MetaData.bCallInEditor=true;
 auto Get=[&](FName Name,int Y){FGraphNodeCreator<UK2Node_VariableGet> C(*Graph);auto* N=C.CreateNode();N->VariableReference.SetSelfMember(Name);N->NodePosX=-400;N->NodePosY=Y;C.Finalize();return N;};
 auto Call=[&](UClass* Class,FName Name,int X,int Y){FGraphNodeCreator<UK2Node_CallFunction> C(*Graph);auto* N=C.CreateNode();N->SetFromFunction(Class->FindFunctionByName(Name));N->NodePosX=X;N->NodePosY=Y;C.Finalize();return N;};
 auto Link=[&](UEdGraphPin* A,UEdGraphPin* B){check(A&&B);check(Schema->TryCreateConnection(A,B));};
 auto* Target=Get(TEXT("TargetVolume"),-150);
 auto* Valid=Call(UKismetSystemLibrary::StaticClass(),TEXT("IsValid"),0,-150);
 Link(Target->GetValuePin(),Valid->FindPinChecked(TEXT("Object")));
 FGraphNodeCreator<UK2Node_IfThenElse> BC(*Graph);auto* Branch=BC.CreateNode();BC.Finalize();
 Link(Entry->FindPinChecked(UEdGraphSchema_K2::PN_Then),Branch->GetExecPin());
 Link(Valid->GetReturnValuePin(),Branch->GetConditionPin());
 auto* Create=Call(UPrimitiveComponent::StaticClass(),TEXT("CreateDynamicMaterialInstance"),300,0);
 Link(Branch->GetThenPin(),Create->GetExecPin());Link(Target->GetValuePin(),Create->FindPinChecked(UEdGraphSchema_K2::PN_Self));
 // No SourceMaterial override: CreateDynamicMaterialInstance reuses the
 // component's current MID, or initializes it from the assigned material.
 UEdGraphPin* Last=Create->GetThenPin();int Index=0;
 for(auto Name:Names){
  auto* Set=Call(UMaterialInstanceDynamic::StaticClass(),TEXT("SetScalarParameterValue"),650+(Index%4)*350,(Index/4)*300);
  Link(Last,Set->GetExecPin());Last=Set->GetThenPin();
  Link(Create->GetReturnValuePin(),Set->FindPinChecked(UEdGraphSchema_K2::PN_Self));
  Schema->TrySetDefaultValue(*Set->FindPinChecked(TEXT("ParameterName")),Name);
  Link(Get(Name,300+Index*100)->GetValuePin(),Set->FindPinChecked(TEXT("Value")));++Index;
 }
 auto* Set=Call(UMaterialInstanceDynamic::StaticClass(),TEXT("SetVectorParameterValue"),1800,1200);
 Link(Last,Set->GetExecPin());Link(Create->GetReturnValuePin(),Set->FindPinChecked(UEdGraphSchema_K2::PN_Self));
 Schema->TrySetDefaultValue(*Set->FindPinChecked(TEXT("ParameterName")),TEXT("CloudAlbedo"));
 Link(Get(TEXT("CloudAlbedo"),1800)->GetValuePin(),Set->FindPinChecked(TEXT("Value")));
 FKismetEditorUtilities::CompileBlueprint(BP);
 auto AddApply=[&](UEdGraph* G,UEdGraphPin* Exec){
  FGraphNodeCreator<UK2Node_CallFunction> C(*G);auto* N=C.CreateNode();N->FunctionReference.SetSelfMember(TEXT("ApplyCloudParameters"));N->NodePosX=300;C.Finalize();Link(Exec,N->GetExecPin());
 };
 auto* UCS=FBlueprintEditorUtils::FindUserConstructionScript(BP);
 for(UEdGraphNode* N:UCS->Nodes) if(auto* E=Cast<UK2Node_FunctionEntry>(N)){AddApply(UCS,E->FindPinChecked(UEdGraphSchema_K2::PN_Then));break;}
 UEdGraph* EG=BP->UbergraphPages[0];
 UK2Node_Event* Begin=nullptr;
 for(UEdGraphNode* N:EG->Nodes) if(auto* E=Cast<UK2Node_Event>(N)) if(E->EventReference.GetMemberName()==TEXT("ReceiveBeginPlay")) Begin=E;
 if(!Begin){FGraphNodeCreator<UK2Node_Event> C(*EG);Begin=C.CreateNode();Begin->EventReference.SetExternalMember(TEXT("ReceiveBeginPlay"),AActor::StaticClass());Begin->bOverrideFunction=true;C.Finalize();}
 AddApply(EG,Begin->FindPinChecked(UEdGraphSchema_K2::PN_Then));
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);
 return BP->Status==BS_Error ? -2:AddCloudOpacityControls();
}
