import maya.standalone
import maya.OpenMaya as OpenMaya
import sys
import subprocess
import time
import os

def main( argv = None ):
	try:
		maya.standalone.initialize(  )
		sys.stdout.write( "initialize standalone application" )
	except:
		sys.stderr.write( "Failed in initialize standalone application" )
		raise

main()

import maya.app.renderSetup.model.override as override
import maya.app.renderSetup.model.selector as selector
import maya.app.renderSetup.model.collection as collection
import maya.app.renderSetup.model.connectionOverride as connectionOverride
import maya.app.renderSetup.model.renderLayer as renderLayer
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm


cmds.loadPlugin( "vrayformaya", quiet=True,)

def remove_old_project(root):
	if os.path.isdir(root):
		for item in os.listdir(root):
			item = os.path.join(root,item)
			remove_old_project(item)
		os.rmdir(root)
	else:
		os.remove(root)
		
#----------------------------------------------------------------------
def get_project_Location():
	""""""
	maya_project_dir = os.path.join(os.environ["MAYA_APP_DIR"],"projects").replace("\\","/")
	new_project_location = os.path.join(maya_project_dir,"DML_Auto_Example").replace("\\","/")
	return new_project_location

#----------------------------------------------------------------------
def createWorkspace():
	maya_project_dir = os.path.join(os.environ["MAYA_APP_DIR"],"projects").replace("\\","/")
	new_project_location = os.path.join(maya_project_dir,"DML_Auto_Example").replace("\\","/")
	if os.path.exists(new_project_location):
		remove_old_project(new_project_location)
	
	cmds.workspace(create=new_project_location)
	cmds.workspace( new_project_location,o=True)
	cmds.workspace(fr=["images","images"])
	cmds.workspace(fr=["V-Ray Scene","data"])
	cmds.workspace(fr=["Presets","data"])
	cmds.workspace(fr=["autoSave","autosave"])
	cmds.workspace(fr=["mayaBinary","scenes"])
	cmds.workspace(fr=["scene","scenes"])
	cmds.workspace(fr=["sourceImages","sourceimages"])
	cmds.workspace( saveWorkspace=True)
	for fr in cmds.workspace( fileRuleList=True ):
		pth = cmds.workspace( fileRuleEntry=fr )
		pth = os.path.join(new_project_location,pth)
		try:
			os.mkdir(pth)
		except:
			pass
	return new_project_location

# Helper function for creating a shader
def createShader(name,color):
	""" Create a shader of the given type"""
	Shader_mat = pm.shadingNode("VRayCarPaintMtl", asShader=True)
	Shader_mat.setName(name)
	Shader_SG = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=(Shader_mat.name() + "_SG"))
	Shader_mat.outColor.connect(Shader_SG.surfaceShader)
	Shader_mat.flake_scale.set(0.8)
	cmds.setAttr("{}.color".format(Shader_mat.name()),color[0],color[1],color[2],type="double3")
	return Shader_mat,Shader_SG


def create_Maya_Scene():

	cmds.file( force=True, newFile=True,)
	
	new_workspace = createWorkspace()
	
	
	# Build The Sphere
	sphere_tras,sphere_poly = pm.polySphere(r=1,sx=20,sy=20,ax=[0,1,0])
	# Move it up so resting on ground
	sphere_tras.ty.set(1)
	# Build Floor
	plan_trans,plan_poly = pm.polyPlane(w=30,h=30,sx=10,sy=10,ax=[0,1,0])
	
	# create camera
	cam_tras,cam_shape = pm.camera()
	# make the camera aim constrant
	mel.eval('cameraMakeNode 2 ""')
	# Get the constrat group
	cam_group = cam_tras.getParent()
	# get the camera aim target
	cam_aim = cam_group.child(1)
	# parent the target to the world
	cam_aim.setParent(world=True)
	
	#cam_group.t.set(0,3,6)
	# center the camera target to the middle of thee sphere
	cam_aim.setTranslation(sphere_tras.getPivots(ws=True)[0])
	
	#create a circle to attach camera to
	cir_tras,cir_shape = pm.circle( radius=8, normal=[0,1,0], sweep =45)
	cir_tras.ty.set(3)
	cir_tras.rz.set(-13)
	
	#create a light
	recLight_tras = pm.shadingNode("VRayLightRectShape",asLight=True)
	recLight_tras.t.set([-1, 4.5, -10])
	pm.aimConstraint([sphere_tras,recLight_tras],weight=1, aimVector=[0,0,-1] ,upVector=[0 ,1 ,0],worldUpType="vector",worldUpVector=[0,1,0])
	
	#Attach The Camera to the path animation
	pm.pathAnimation([cam_group,cir_tras],fractionMode=True,  follow=True,followAxis="x",upAxis="y",worldUpType="vector",worldUpVector=[0,1,0],inverseUp=False,inverseFront=False,bank=False,startTimeU=1,endTimeU=10)
	
	#Camera A Light
	recLight_tras.setRotation([-41, 195, 0.0])
	recLight_shap = recLight_tras.child(0)
	recLight_shap.intensityMult.set(100)
	
	# List of new Material Names
	material_names = ["White_Shader","Red_Shader","Yellow_Shader","Green_Shader"]
	# List of new Material Color Values
	material_colors = [[1.0,1.0,1.0],[1.0,0.0,0.0],[0.375595,0.380288,0.0503627],[0.157469,0.425018,0.0508247]]
	
	rs = renderSetup.instance()
	
	render_layers = []
	for name,color in zip(material_names,material_colors):
		mat,sg = createShader(name,color)
		rl = rs.createRenderLayer(mat.name()+"_Switcher")
		render_layers.append(rl)
		
		cl_1 = rl.createCollection("All_Transfroms")
		cl_1.getSelector().setPattern("*")
		cl_2 = cl_1.createCollection("Sphere")
		cl_2.getSelector().setStaticSelection(sphere_tras.name())
		
		Mat_Override = cl_2.createOverride(mat.name().split("_")[0]+"_Color",connectionOverride.MaterialOverride.kTypeId)
		Mat_Override.setMaterial(sg.name())
		
	save_file_location = os.path.join(new_workspace,"scenes/Colored_Spheres.mb".replace("\\",'/'))
	cmds.file(rename=save_file_location)
	cmds.file(options="v=0",  save=True)
	
	
	defaultRenderGlobals = pm.ls("defaultRenderGlobals")[0]
	defaultResolution = pm.ls("defaultResolution")[0]
	defaultRenderGlobals.currentRenderer.set("vray")
	defaultResolution.deviceAspectRatio.set(1.333)
	
	vraySettings = pm.ls("vraySettings")[0]
	vraySettings.width.set(640)
	vraySettings.height.set(480)
	vraySettings.aspectRatio.set(1.333)
	vraySettings.fileNamePrefix.set("<Version>/<Layer>/Sphere")
	defaultRenderGlobals.renderVersion.set("01")
	vraySettings.animType.set(1)
	cam_shape.renderable.set(1)
	pm.ls("perspShape")[0].renderable.set(0)
	defaultRenderGlobals.endFrame.set(2)
	
	cmds.evalDeferred("renderLayer.DefaultRenderLayer().setRenderable(False)")
	cmds.evalDeferred('cmds.file(options="v=0",  save=True)')
	return save_file_location

save_file_location = create_Maya_Scene()
prj_location       = get_project_Location()
next_Line = 0
with open(os.path.join(prj_location,"renderLog.txt"), mode='w+') as f:
	proc = subprocess.Popen('"C:/Program Files/Autodesk/Maya2020/bin/Render.exe" -r vray -s 1 -e 10 -proj {} "{}"'.format(prj_location.replace("\\","/"), save_file_location), stdout=f, shell=False)
	while proc.returncode == None:
		proc.poll()
		f.seek(0)
		lines = f.readlines()
		if len(lines) > next_Line:
			for l in lines[next_Line:]:
				next_Line += 1
				if len(l.strip()):
					if "completed" in l or "Successfully" in l:
						sys.stdout.write( l.strip().replace(r"\n","").replace(r"\r",""))
		time.sleep(1)