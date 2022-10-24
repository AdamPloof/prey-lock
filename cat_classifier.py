import cv2
from PIL import Image
from datetime import datetime
from pathlib import Path

class CatClassifier():
    MAX_IMAGES = 5
    CAPTURE_PATH = './captured_images'

    def __init__(self) -> None:
        self.frame = None
        self.cascade = cv2.CascadeClassifier('./haarcascade_frontalcatface_extended.xml')

    def load_frame(self, frame):
        self.frame = frame

    def test_classify(self):
        img = Image.open('./training_images/cat_training_img_1.jpg')
        img = img.resize((600, 600))
        img = img.convert('L')

        processed_path = './training_images/test_processed.jpg'
        img.save(processed_path)

        processed_img = cv2.imread(processed_path)
        cat_faces = self.cascade.detectMultiScale(processed_img, scaleFactor=1.3, minNeighbors=5, minSize=(75, 75))
        print(cat_faces)
        for (i, (x, y, w, h)) in enumerate(cat_faces):
            cv2.rectangle(processed_img, (x, y), (x+w, y+h), (0,255, 0), 3)
            cv2.putText(processed_img, "Cat Faces - #{}".format(i + 1), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

        cv2.imwrite('./training_images/cat_detected.jpg', processed_img)

    def is_cat(self) -> bool:
        pass

    def save_img(self):
        if self.img_folder_full() or self.frame is None:
            return

        cap_file = Path(CatClassifier.CAPTURE_PATH).joinpath(datetime.now().strftime('%Y%m%d%H%M%S') + 'capture.jpg')
        cv2.imwrite(filename=str(cap_file), img=self.frame)

    def img_folder_full(self) -> bool:
        # Rather than checking the total size of the image folder, which could be expensive,
        # just check number of images in there.
        files = [item for item in Path(CatClassifier.CAPTURE_PATH).iterdir() if item.is_file() and item.suffix == '.jpg' ]

        return len(files) >= CatClassifier.MAX_IMAGES