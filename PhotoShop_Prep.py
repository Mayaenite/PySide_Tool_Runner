import os
from datetime import datetime
from tempfile import mkdtemp
import photoshop.api as ps_api
from photoshop import Session
import glob
file_foulder = os.path.dirname(__file__)
slate_template = os.path.join(file_foulder,"slate_template.psd")
ps_api.action_descriptor

base_image_foulder = os.sys.argv[1]
print(base_image_foulder)
save_foulder = os.path.normpath(os.path.join(os.path.dirname(base_image_foulder),"Slated",os.path.basename(base_image_foulder)))

image_folders = [os.path.normpath(os.path.join(base_image_foulder,pth)) for pth in os.listdir(base_image_foulder)]

for image_foulder in image_folders:
	image_files = glob.glob(image_foulder+"/*.png")
	for image_file_path in image_files:
		image_name = os.path.basename(image_file_path)
		frame_number = image_name.split(".")[1]
		shader_color = os.path.basename(os.path.dirname(image_file_path))
		shader_color = "_".join(shader_color.split("_")[:2])
		save_image_path = os.path.join(save_foulder,os.path.basename(image_foulder),image_name).replace(".png",".jpg")
		if not os.path.exists(os.path.dirname(save_image_path)):
			os.makedirs(os.path.dirname(save_image_path).replace("\\","/"))
			
		with Session(slate_template, action="open", auto_close=True) as ps:
			layer_set = ps.active_document.layerSets.getByName("template")
			
			data = {
				"project name": shader_color,
				"datetime": datetime.today().strftime("%Y-%m-%d"),
				"Frame Number": "Frame Number : {}".format(frame_number)
			}
			
			for layer in layer_set.layers:
				if layer.kind == ps.LayerKind.TextLayer:
					layer.textItem.contents = data[layer.textItem.contents.strip()]
					
			desc = ps.ActionDescriptor
			desc.putPath(ps.app.charIDToTypeID("null"), image_file_path)
			event_id = ps.app.charIDToTypeID("Plc ")  # `Plc` need one space in here.
			ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
			layer1 = ps.active_document.layers.getByName("Layer 1")
			ps.active_document.activeLayer.move(layer1, ps_api.enumerations.ElementPlacement.PlaceAfter)
			ps.active_document.saveAs(save_image_path, ps.JPEGSaveOptions())
			print(f"Save jpg to {save_image_path}")