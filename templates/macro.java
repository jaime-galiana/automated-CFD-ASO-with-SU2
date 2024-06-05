// Simcenter STAR-CCM+ macro: macro.java
// Written by Simcenter STAR-CCM+ 16.04.007
package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;
import star.cadmodeler.*;
import star.meshing.*;
import star.delaunaymesher.*;

public class macro extends StarMacro {

  public void execute() {
    execute0();
  }

  private void execute0() {

    Simulation simulation_0 = 
      getActiveSimulation();

    CadModel cadModel_1 = 
      simulation_0.get(SolidModelManager.class).createSolidModel();

    cadModel_1.resetSystemOptions();

    simulation_0.get(SolidModelManager.class).importFilesInto3DCad(new StringVector(new String[] {resolvePath("/rds/general/user/jg2219/ephemeral/Final-try/bin/domain.STEP")}), cadModel_1, true, false, false, false, false, false, false, true, false, true, NeoProperty.fromString("{\'STEP\': 0, \'NX\': 0, \'CATIAV5\': 0, \'SE\': 0, \'JT\': 0}"));

    UniteBodiesFeature uniteBodiesFeature_1 = 
      cadModel_1.getFeatureManager().createUniteBodies();

    uniteBodiesFeature_1.setAutoPreview(true);

    cadModel_1.allowMakingPartDirty(false);

    uniteBodiesFeature_1.setAutoPreview(true);

    cadModel_1.allowMakingPartDirty(false);

    uniteBodiesFeature_1.setImprintOption(0);

    uniteBodiesFeature_1.getTolerance().setValue(1.0E-5);

    Units units_0 = 
      ((Units) simulation_0.getUnitsManager().getObject("m"));

    uniteBodiesFeature_1.getTolerance().setUnits(units_0);

    uniteBodiesFeature_1.setTransferFaceNames(true);

    uniteBodiesFeature_1.setTransferBodyNames(false);

    star.cadmodeler.Body cadmodelerBody_2 = 
      ((star.cadmodeler.Body) cadModel_1.getBody("Boss-Extrude1"));

    star.cadmodeler.Body cadmodelerBody_3 = 
      ((star.cadmodeler.Body) cadModel_1.getBody("Revolve1"));

    uniteBodiesFeature_1.setBodies(new NeoObjectVector(new Object[] {cadmodelerBody_2, cadmodelerBody_3}));

    uniteBodiesFeature_1.setBodyGroups(new NeoObjectVector(new Object[] {}));

    uniteBodiesFeature_1.setCadFilters(new NeoObjectVector(new Object[] {}));

    uniteBodiesFeature_1.setIsBodyGroupCreation(false);

    cadModel_1.getFeatureManager().markDependentNotUptodate(uniteBodiesFeature_1);

    uniteBodiesFeature_1.markFeatureForEdit();

    cadModel_1.allowMakingPartDirty(true);

    cadModel_1.getFeatureManager().execute(uniteBodiesFeature_1);

    cadModel_1.update();

    simulation_0.get(SolidModelManager.class).endEditCadModel(cadModel_1);

    CadModel cadModel_2 = 
      simulation_0.get(SolidModelManager.class).createSolidModel();

    cadModel_2.resetSystemOptions();

    simulation_0.get(SolidModelManager.class).importFilesInto3DCad(new StringVector(new String[] {resolvePath("./wing.stp")}), cadModel_2, true, false, false, false, false, false, false, true, false, true, NeoProperty.fromString("{\'STEP\': 0, \'NX\': 0, \'CATIAV5\': 0, \'SE\': 0, \'JT\': 0}"));

    cadModel_2.update();

    simulation_0.get(SolidModelManager.class).endEditCadModel(cadModel_2);

    cadModel_1.createParts(new NeoObjectVector(new Object[] {cadmodelerBody_2}), new NeoObjectVector(new Object[] {}), 1, "SharpEdges", 30.0, 4, true, 1.0E-5, false);

    SolidModelPart solidModelPart_0 = 
      ((SolidModelPart) simulation_0.get(SimulationPartManager.class).getPart("Boss-Extrude1"));

    solidModelPart_0.setPresentationName("domain");

    ImportCadFileFeature importCadFileFeature_0 = 
      ((ImportCadFileFeature) cadModel_2.getFeature("ImportCad 1"));

    star.cadmodeler.Body cadmodelerBody_4 = 
      ((star.cadmodeler.Body) importCadFileFeature_0.getBodyByIndex(1));

    cadModel_2.createParts(new NeoObjectVector(new Object[] {cadmodelerBody_4}), new NeoObjectVector(new Object[] {}), 1, "SharpEdges", 30.0, 4, true, 1.0E-5, false);

    SolidModelPart solidModelPart_1 = 
      ((SolidModelPart) simulation_0.get(SimulationPartManager.class).getPart("Body 1"));

    solidModelPart_1.setPresentationName("wing");

    PartSurface partSurface_0 = 
      ((PartSurface) solidModelPart_0.getPartSurfaceManager().getPartSurface("Default"));

    solidModelPart_0.getPartSurfaceManager().splitPartSurfacesByAngle(new NeoObjectVector(new Object[] {partSurface_0}), 89.0);

    partSurface_0.setPresentationName("farfield");

    PartSurface partSurface_1 = 
      ((PartSurface) solidModelPart_0.getPartSurfaceManager().getPartSurface("Default 2"));

    partSurface_1.setPresentationName("sym");

    PartSurface partSurface_2 = 
      ((PartSurface) solidModelPart_0.getPartSurfaceManager().getPartSurface("Default 3"));

    partSurface_2.setPresentationName("outlet");

    MeshActionManager meshActionManager_0 = 
      simulation_0.get(MeshActionManager.class);

    MeshPart meshPart_0 = 
      meshActionManager_0.subtractParts(new NeoObjectVector(new Object[] {solidModelPart_0, solidModelPart_1}), solidModelPart_0, "Discrete");

    Region region_0 = 
      simulation_0.getRegionManager().createEmptyRegion();

    region_0.setPresentationName("Region");

    Boundary boundary_0 = 
      region_0.getBoundaryManager().getBoundary("Default");

    region_0.getBoundaryManager().removeBoundaries(new NeoObjectVector(new Object[] {boundary_0}));

    FeatureCurve featureCurve_0 = 
      ((FeatureCurve) region_0.getFeatureCurveManager().getObject("Default"));

    region_0.getFeatureCurveManager().removeObjects(featureCurve_0);

    FeatureCurve featureCurve_1 = 
      region_0.getFeatureCurveManager().createEmptyFeatureCurveWithName("Feature Curve");

    simulation_0.getRegionManager().newRegionsFromParts(new NeoObjectVector(new Object[] {meshPart_0}), "OneRegion", region_0, "OneBoundaryPerPartSurface", null, "OneFeatureCurve", featureCurve_1, RegionManager.CreateInterfaceMode.BOUNDARY, "OneEdgeBoundaryPerPart", null);

    Boundary boundary_1 = 
      region_0.getBoundaryManager().getBoundary("Subtract.Default");

    boundary_1.setPresentationName("wing");

    Boundary boundary_2 = 
      region_0.getBoundaryManager().getBoundary("Subtract.farfield");

    boundary_2.setPresentationName("farfield");

    Boundary boundary_3 = 
      region_0.getBoundaryManager().getBoundary("Subtract.outlet");

    boundary_3.setPresentationName("outlet");

    Boundary boundary_4 = 
      region_0.getBoundaryManager().getBoundary("Subtract.sym");

    boundary_4.setPresentationName("sym");

    FreeStreamBoundary freeStreamBoundary_0 = 
      ((FreeStreamBoundary) simulation_0.get(ConditionTypeManager.class).get(FreeStreamBoundary.class));

    boundary_2.setBoundaryType(freeStreamBoundary_0);

    OutletBoundary outletBoundary_0 = 
      ((OutletBoundary) simulation_0.get(ConditionTypeManager.class).get(OutletBoundary.class));

    boundary_3.setBoundaryType(outletBoundary_0);

    SymmetryBoundary symmetryBoundary_0 = 
      ((SymmetryBoundary) simulation_0.get(ConditionTypeManager.class).get(SymmetryBoundary.class));

    boundary_4.setBoundaryType(symmetryBoundary_0);

    AutoMeshOperation autoMeshOperation_0 = 
      simulation_0.get(MeshOperationManager.class).createAutoMeshOperation(new StringVector(new String[] {"star.resurfacer.ResurfacerAutoMesher", "star.delaunaymesher.DelaunayAutoMesher"}), new NeoObjectVector(new Object[] {meshPart_0}));

    autoMeshOperation_0.getMesherParallelModeOption().setSelected(MesherParallelModeOption.Type.PARALLEL);

    autoMeshOperation_0.getDefaultValues().get(BaseSize.class).setValue(0.2);

    autoMeshOperation_0.getDefaultValues().get(BaseSize.class).setUnits(units_0);

    PartsMinimumSurfaceSize partsMinimumSurfaceSize_0 = 
      autoMeshOperation_0.getDefaultValues().get(PartsMinimumSurfaceSize.class);

    partsMinimumSurfaceSize_0.getRelativeSizeScalar().setValue(0.5);

    Units units_1 = 
      ((Units) simulation_0.getUnitsManager().getObject(""));

    partsMinimumSurfaceSize_0.getRelativeSizeScalar().setUnits(units_1);

    PartsTargetSurfaceSize partsTargetSurfaceSize_0 = 
      autoMeshOperation_0.getDefaultValues().get(PartsTargetSurfaceSize.class);

    partsTargetSurfaceSize_0.getRelativeSizeScalar().setValue(10000);

    Units units_2 = 
      ((Units) simulation_0.getUnitsManager().getObject(""));

    partsTargetSurfaceSize_0.getRelativeSizeScalar().setUnits(units_2);

    SurfaceCurvature surfaceCurvature_0 = 
      autoMeshOperation_0.getDefaultValues().get(SurfaceCurvature.class);

    surfaceCurvature_0.setEnableCurvatureDeviationDist(true);

    surfaceCurvature_0.setNumPointsAroundCircle(180.0);

    surfaceCurvature_0.setMaxNumPointsAroundCircle(360.0);

    surfaceCurvature_0.getCurvatureDeviationDistance().setValue(1.0E-5);

    surfaceCurvature_0.getCurvatureDeviationDistance().setUnits(units_0);

    PartsResurfacerSurfaceProximity partsResurfacerSurfaceProximity_0 = 
      autoMeshOperation_0.getDefaultValues().get(PartsResurfacerSurfaceProximity.class);

    partsResurfacerSurfaceProximity_0.setEnableCeiling(true); 

    MaximumCellSize maximumCellSize_0 = 
      autoMeshOperation_0.getDefaultValues().get(MaximumCellSize.class);

    maximumCellSize_0.getRelativeSizeScalar().setValue(20000.0);

    maximumCellSize_0.getRelativeSizeScalar().setUnits(units_1);

    PartsCoreMeshOptimizer partsCoreMeshOptimizer_0 = 
      autoMeshOperation_0.getDefaultValues().get(PartsCoreMeshOptimizer.class);

    partsCoreMeshOptimizer_0.setOptimizeCycles(4);

    partsCoreMeshOptimizer_0.setQualityThreshold(0.8);

    PartsDelaunayPostMeshOptimizer partsDelaunayPostMeshOptimizer_0 = 
      autoMeshOperation_0.getDefaultValues().get(PartsDelaunayPostMeshOptimizer.class);

    partsDelaunayPostMeshOptimizer_0.setOptimizeBoundary(true);

    SurfaceCustomMeshControl surfaceCustomMeshControl_0 = 
      autoMeshOperation_0.getCustomMeshControls().createSurfaceControl();

    surfaceCustomMeshControl_0.getCustomConditions().get(PartsTargetSurfaceSizeOption.class).setSelected(PartsTargetSurfaceSizeOption.Type.CUSTOM);

    surfaceCustomMeshControl_0.getCustomConditions().get(PartsMinimumSurfaceSizeOption.class).setSelected(PartsMinimumSurfaceSizeOption.Type.CUSTOM);

    surfaceCustomMeshControl_0.getCustomConditions().get(PartsSurfaceCurvatureOption.class).setSelected(PartsSurfaceCurvatureOption.Type.CUSTOM_VALUES);

    PartsTargetSurfaceSize partsTargetSurfaceSize_1 = 
      surfaceCustomMeshControl_0.getCustomValues().get(PartsTargetSurfaceSize.class);

    partsTargetSurfaceSize_1.getRelativeSizeScalar().setValue(20000.0);

    partsTargetSurfaceSize_1.getRelativeSizeScalar().setUnits(units_1);

    PartsMinimumSurfaceSize partsMinimumSurfaceSize_1 = 
      surfaceCustomMeshControl_0.getCustomValues().get(PartsMinimumSurfaceSize.class);

    partsMinimumSurfaceSize_1.getRelativeSizeScalar().setValue(1.0);

    partsMinimumSurfaceSize_1.getRelativeSizeScalar().setUnits(units_1);

    SurfaceCurvature surfaceCurvature_1 = 
      surfaceCustomMeshControl_0.getCustomValues().get(SurfaceCurvature.class);

    surfaceCurvature_1.setNumPointsAroundCircle(35.0);

    surfaceCustomMeshControl_0.getGeometryObjects().setQuery(null);

    PartSurface partSurface_3 = 
      ((PartSurface) meshPart_0.getPartSurfaceManager().getPartSurface("farfield"));

    PartSurface partSurface_4 = 
      ((PartSurface) meshPart_0.getPartSurfaceManager().getPartSurface("outlet"));

    PartSurface partSurface_5 = 
      ((PartSurface) meshPart_0.getPartSurfaceManager().getPartSurface("sym"));

    surfaceCustomMeshControl_0.getGeometryObjects().setObjects(partSurface_3, partSurface_4, partSurface_5);

    autoMeshOperation_0.execute();

    ImportManager importManager_0 = 
      simulation_0.getImportManager();

    importManager_0.setExportPath("./mesh.cga");

    importManager_0.setFormatType(SolutionExportFormat.Type.CGA);

    importManager_0.setExportParts(new NeoObjectVector(new Object[] {}));

    importManager_0.setExportPartSurfaces(new NeoObjectVector(new Object[] {}));

    importManager_0.setExportBoundaries(new NeoObjectVector(new Object[] {boundary_2, boundary_3, boundary_4, boundary_1}));

    importManager_0.setExportRegions(new NeoObjectVector(new Object[] {region_0}));

    importManager_0.setExportScalars(new NeoObjectVector(new Object[] {}));

    importManager_0.setExportVectors(new NeoObjectVector(new Object[] {}));

    importManager_0.setExportOptionAppendToFile(false);

    importManager_0.setExportOptionDataAtVerts(false);

    importManager_0.setExportOptionSolutionOnly(false);

    importManager_0.export(resolvePath("mesh.cga"), new NeoObjectVector(new Object[] {region_0}), new NeoObjectVector(new Object[] {boundary_2, boundary_3, boundary_4, boundary_1}), new NeoObjectVector(new Object[] {}), new NeoObjectVector(new Object[] {}), new NeoObjectVector(new Object[] {}), NeoProperty.fromString("{\'exportFormatType\': 11, \'appendToFile\': false, \'solutionOnly\': false, \'dataAtVerts\': false, \'triangulatePoly\': false, \'mergeBoundaries\': false, \'fileFormat\': 1}"));
  }
}
