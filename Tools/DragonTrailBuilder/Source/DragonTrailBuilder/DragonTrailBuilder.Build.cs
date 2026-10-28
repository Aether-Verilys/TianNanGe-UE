using UnrealBuildTool;
public class DragonTrailBuilder : ModuleRules {
 public DragonTrailBuilder(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PrivateDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","UnrealEd","Niagara","NiagaraCore","NiagaraEditor","AssetRegistry"});
 }
}
