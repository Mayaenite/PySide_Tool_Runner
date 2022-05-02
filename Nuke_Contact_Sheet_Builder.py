import nuke
import os
import glob

#base_image_foulder = r"C:\Users\drew.loveridge\Documents\maya\projects\DML_Auto_Example\images\01"
base_image_foulder = os.sys.argv[1]

slated_image_foulder = os.path.join(os.path.dirname( base_image_foulder),"Slated",os.path.basename(base_image_foulder))

save_foulder = os.path.join(os.path.dirname( base_image_foulder),"Merged")

save_image_file_path = os.path.join(save_foulder,"Contact_Sheet.####.jpg")

image_folders = [os.path.normpath(os.path.join(slated_image_foulder,pth)) for pth in os.listdir(base_image_foulder)]

read_nodes = []
for image_foulder in image_folders:
	image_files = glob.glob(image_foulder+"/*.jpg")
	image_name = os.path.basename(image_files[0])
	image_name_parts = image_name.split(".")
	frame_count = len(image_name_parts[1])
	image_name = "{}.{}.{}".format(image_name_parts[0],"#"*frame_count,image_name_parts[-1])
	read_image_path = os.path.join(image_foulder,image_name)
	read_nd = nuke.createNode("Read","file {} last 10".format(read_image_path.replace("\\","/")), inpanel=False)
	read_nodes.append(read_nd)

for rn in read_nodes:
	rn.setSelected(True)
	nuke.autoplace(rn)
ContactSheet_nod = nuke.createNode("ContactSheet","rows 2 columns 2 width 1280 height 960",inpanel=False)
nuke.autoplace(ContactSheet_nod)
write_node = nuke.createNode("Write","file {} create_directories true file_type jpeg".format(save_image_file_path.replace("\\","/")))

root = nuke.root()
format_knb = root.knob("format")
format_knb.fromScript('1280 960 0 0 1280 960 1 Contact_Sheet')
nuke.execute(write_node,1,10)
