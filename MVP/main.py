
from ultralytics.models import YOLO

from MVP.camera.camera import Camera
from MVP.show_picture.show_picture import ShowPicture


model_path= r'/my_best-shelf-void-model2026-01-27-16-53.pt'
model = YOLO(model_path)
json_path=r'C:\Users\ryabovva.VOLKOVKMR\PycharmProjects\learn_void_shelf\shot_20260123_193334_shelf_coordinates.json'
camera = Camera(ip_camera='10.142.13.204')
show = ShowPicture(model=model)
show.start(camera=camera, json_path=json_path)