import bpy

# get the list of scenes
scn = bpy.data.scenes['Scene']

# 4 views 
views = ["top", "side", "front", "aux"]

# translation values
tranValues = {
				"top"   :   [0.25, 0.25],
				"side"  :   [-0.25, 0.25],
				"front" :   [0.25, -0.25],
				"aux"   :   [-0.25, -0.25]
				}

for view in views:

	# clone the scene
	bpy.ops.scene.new(type="LINK_OBJECTS")
	bpy.context.scene.name = view + "Scn"
	curScn = bpy.data.scenes[view+"Scn"]

	# cretae the camera 
	cam_data = bpy.data.cameras.new(view+"Cam")
	cam_ob = bpy.data.objects.new(name=view+"Cam", object_data=cam_data)
	
	# link the camera to that particular scene 
	curScn.objects.link(cam_ob)  # instance the camera object in the scene
	curScn.camera = cam_ob  # set the active camera

	# scale the cam for differentiation	
	cam_ob.scale = 5.0, 5.0, 5.0

	# define the locations and rotations...	
	if view == "top":
		cam_ob.location = 0.0, 0.0, 40.0
		cam_ob.location = 0.0, 0.0, 0.0

	elif view == "side":
		cam_ob.location = 40.0, 0.0, 0.0
		cam_ob.rotation_euler = -90.0 * 0.0174532925, 180.0 * 0.0174532925, -90.0 * 0.0174532925

	elif view == "front":
		cam_ob.location = 0.0, 0.0, 10.0
		cam_ob.rotation_euler = 90.0*0.0174532925, 0.0, 180.0 * 0.0174532925

	elif view == "aux":
		cam_ob.location = 0.0, 0.0, 10.0
		cam_ob.rotation_euler = 0.0, 0.0, 10.0 * 0.0174532925


# set the "Scene" as the current active scene
bpy.context.window.screen.scene = bpy.data.scenes['Scene']

# enable the compositing nodes.
bpy.context.scene.use_nodes = True
#bpy.context.space_data.tree_type = 'CompositorNodeTree'

# create the node network.
nodes = bpy.data.scenes['Scene'].node_tree.nodes
links = bpy.data.scenes['Scene'].node_tree.links

# create 3 mix nodes
mixNodes = []
for i in range(1, 4):
	mixNode = nodes.new("CompositorNodeMixRGB")
	mixNode.blend_type = "ADD"
	
	mixNode.location.y = -300 * i
	mixNode.location.x = 600

	if i == 3:
		mixNode.location.y = -500
		mixNode.location.x = 1000
	
	mixNodes.append( mixNode )

outputSocket = mixNodes[0].outputs[0]
inputSocket = mixNodes[2].inputs[1]
links.new(outputSocket, inputSocket)

outputSocket = mixNodes[1].outputs[0]
inputSocket = mixNodes[2].inputs[2]
links.new(outputSocket, inputSocket)

# link to composite node
#for node in nodes:
#	if node.type == "COMPOSITE":
#		compositeNode = node

# create output node
compositeNode = nodes.new('CompositorNodeComposite')   
compositeNode.use_alpha = False
compositeNode.location = 1200, -500

# connect to composite nodea
outputSocket = mixNodes[2].outputs[0]
inputSocket = compositeNode.inputs[0]
links.new(outputSocket, inputSocket)

for index, view in enumerate(views):
	#render layer node 
	rLayerNode = nodes.new("CompositorNodeRLayers")
	rLayerNode.name = view+"RLayer"
	rLayerNode.scene = bpy.data.scenes[view+"Scn"]
	
	rLayerNode.location.y = -300 * index
	
	# scale node
	scaleNode = nodes.new("CompositorNodeScale")
	scaleNode.inputs[1].default_value = 0.48
	scaleNode.inputs[2].default_value = 0.48

	scaleNode.location.y = -300 * index
	scaleNode.location.x = 200 
	
	# translate node
	
	translateNode = nodes.new("CompositorNodeTranslate")
	translateNode.inputs[1].default_value = tranValues[view][0]
	translateNode.inputs[2].default_value = tranValues[view][1]
	translateNode.use_relative = True
	
	translateNode.location.y = -300 * index
	translateNode.location.x = 400
	
	# connect render layer to scale
	outputSocket = rLayerNode.outputs[0]
	inputSocket = scaleNode.inputs[0]
	links.new(outputSocket, inputSocket)
	
	# connect scale to translate
	outputSocket = scaleNode.outputs[0]
	inputSocket = translateNode.inputs[0]
	links.new(outputSocket, inputSocket)
	
	outputSocket = translateNode.outputs[0]

	# connect to mix nodes
	if view == "top":
		inputSocket = mixNodes[0].inputs[1]
	if view == "side":
		inputSocket = mixNodes[0].inputs[2]		
	if view == "front":
		inputSocket = mixNodes[1].inputs[1]	
	if view == "aux":
		inputSocket = mixNodes[1].inputs[2]

	links.new(outputSocket, inputSocket)
