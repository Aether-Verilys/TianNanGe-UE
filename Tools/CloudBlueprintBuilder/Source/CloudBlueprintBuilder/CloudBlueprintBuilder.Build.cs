using UnrealBuildTool;
public class CloudBlueprintBuilder : ModuleRules {
 public CloudBlueprintBuilder(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PrivateDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","UnrealEd","BlueprintGraph","KismetCompiler"});
 }
}
