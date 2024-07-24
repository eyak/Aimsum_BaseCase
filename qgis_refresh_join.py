# remove join from layer names 'sections' and recreate the join
# this refreshs data from the join layer, if used to join data from an external data source

dataLayer = QgsProject.instance().mapLayersByName('data')[0]
dataLayer.dataProvider().forceReload()

sectionsLayer = QgsProject.instance().mapLayersByName('sections')[0]
sectionsLayer.dataProvider().forceReload()


joins = sectionsLayer.vectorJoins()
for join in joins:
    # Get layer as part of the join
    join_target = join.joinLayer()
    joinFieldName = join.joinFieldName()
    targetFieldName = join.targetFieldName()
    # Remove existing join
    sectionsLayer.removeJoin(join.joinLayerId())
    # Create new join
    joinObject = QgsVectorLayerJoinInfo()
    joinObject.setUsingMemoryCache(True)
    joinObject.setJoinLayer(join_target)
    joinObject.setJoinFieldName(joinFieldName)
    joinObject.setTargetFieldName(targetFieldName)
    # Recreate the join
    sectionsLayer.addJoin(joinObject)
sectionsLayer.triggerRepaint()