import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya


def setupPoleVectorConstraintWithNodes(ikHandle, poleVector):
	if not cmds.nodeType(ikHandle)=='ikHandle':
		return OpenMaya.MGlobal.displayError('defined node is not ikHandle')
	startJoint = cmds.ikHandle(ikHandle, q=True, startJoint=True)
	
	# first creating all necesary nodes needed for pole vetor math calculation
	pos = cmds.createNode('pointMatrixMult', name='{node}_wpos_pmm'.format(node=startJoint))
	cm  = cmds.createNode('composeMatrix', name='{node}_wpos_cm'.format(node=startJoint))
	im  = cmds.createNode('inverseMatrix', name='{node}_wpos_im'.format(node=startJoint)) 
	mm  = cmds.createNode('multMatrix', name='{node}_pole_position_mm'.format(node=ikHandle)) 
	pole= cmds.createNode('pointMatrixMult', name='{node}_pole_position_pmm'.format(node=ikHandle)) 
	
	# compose world space position for start joint
	# since ikHandle is setting rotation value on startJoint
	# I cant connect worldMatrix right away, it will create cycle
	# Connecting postion attribute and parentMatrix will give us worldSpace position
	cmds.connectAttr('{node}.translate'.format(node=startJoint), '{node}.inPoint'.format(node=pos))
	cmds.connectAttr('{node}.parentMatrix[0]'.format(node=startJoint), '{node}.inMatrix'.format(node=pos))

	# Now composeMatrix from output so we can inverse and find local position from startJoint to pole control
	cmds.connectAttr('{node}.output'.format(node=pos), '{node}.inputTranslate'.format(node=cm))
	cmds.connectAttr('{node}.outputMatrix'.format(node=cm), '{node}.inputMatrix'.format(node=im))
	cmds.connectAttr('{node}.worldMatrix[0]'.format(node=poleVector), '{node}.matrixIn[0]'.format(node=mm))
	cmds.connectAttr('{node}.outputMatrix'.format(node=im), '{node}.matrixIn[1]'.format(node=mm))

	# Now connect outputs
	cmds.connectAttr('{node}.matrixSum'.format(node=mm), '{node}.inMatrix'.format(node=pole))
	cmds.connectAttr('{node}.output'.format(node=pole), '{node}.poleVector'.format(node=ikHandle))
