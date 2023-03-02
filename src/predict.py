import cv2
import numpy as np
import os
import sys
import time
from PIL import Image
from tqdm import tqdm

sys.path.append(os.path.dirname(sys.path[0]))
from utils.yolo import YOLO

if __name__ == "__main__":
    yolo = YOLO()
    mode = input("Input mode (img, video, fps, heatmap, onnx, dir): ")
    # mode = "img"
    crop = True
    # mode = "video"
    video_save_path = "tmp/416.avi"
    video_fps = 25.0
    # mode = "fps"
    test_interval = 100
    # mode = "heatmap"
    heatmap_save_path = "../tmp/heatmap.png"
    # mode = "onnx"
    onnx_save_path = "../data/model.onnx"
    # mode = "dir"
    dir_path = "../tmp/imgs"
    dir_save_path = "../tmp/imgs_out"
    if mode == "img":
        img = input("Input image path: ")
        try:
            image = Image.open(img)
        except:
            pass
        else:
            r_image, _ = yolo.detect_image(image, crop=crop)
            r_image.show()
    elif mode == "video":
        video_path = input("Input video path, input 0 to call camera: ")
        capture = cv2.VideoCapture(0 if video_path == "0" else video_path)
        if video_save_path != "":
            video_save_path = "../tmp/videos_out/01.avi"
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        out = cv2.VideoWriter(video_save_path, fourcc, video_fps, size)
        ref, frame = capture.read()
        if not ref:
            raise ValueError("Failed to read the camera/video.")
        fps = 0.0
        while True:
            t1 = time.time()
            ref, frame = capture.read()
            if not ref:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(np.uint8(frame))
            image, _ = yolo.detect_image(frame)
            frame = np.array(image)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            fps = (fps + (1. / (time.time() - t1))) / 2
            print("fps=%.2f" % fps)
            frame = cv2.putText(frame, "fps= %.2f" % fps, (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("video", frame)
            c = cv2.waitKey(1) & 0xff
            out.write(frame)
            if c == 27:
                capture.release()
                break
        capture.release()
        print(video_save_path + " saved")
        out.release()
        cv2.destroyAllWindows()
    elif mode == "fps":
        fps_image_path = input("Input image path: ")
        img = Image.open(fps_image_path)
        tact_time = yolo.get_fps(img, test_interval)
        print(str(tact_time) + " seconds, " + str(1 / tact_time) + " fps, @batch_size 1")
    elif mode == "heatmap":
        img = input("Input image path: ")
        try:
            image = Image.open(img)
        except:
            pass
        else:
            yolo.detect_heatmap(image, heatmap_save_path)
    elif mode == "onnx":
        yolo.convert_to_onnx(onnx_save_path)
    elif mode == "dir":
        img_names = os.listdir(dir_path)
        for img_name in tqdm(img_names):
            if img_name.lower().endswith(
                    (".bmp", ".dib", ".png", ".jpg", ".jpeg", ".pbm", ".pgm", ".ppm", ".tif", ".tiff")):
                image_path = os.path.join(dir_path, img_name)
                image = Image.open(image_path)
                r_image, _ = yolo.detect_image(image)
                os.makedirs(dir_save_path, exist_ok=True)
                r_image.save(os.path.join(dir_save_path, img_name.replace(".jpg", ".png")), quality=95, subsampling=0)
    else:
        raise AssertionError("Use mode (img, video, fps, heatmap, onnx, dir).")
