import cv2
from datetime import datetime
from pathlib import Path

class CatClassifier():
    MAX_IMAGES = 5
    CAPTURE_PATH = './captured_images'

    def __init__(self) -> None:
        self.frame = None
        self.cascade = cv2.CascadeClassifier('./cascades/haarcascade_frontalcatface_extended.xml')

    def load_frame(self, frame):
        self.frame = frame

    def test_classify(self):
        # img = cv2.imread('./training_images/cat_training_img_2.jpg')
        img = cv2.imread('./training_images/daisy_2.jpg')
        processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed_img = cv2.resize(processed_img, (600, 600))

        cat_faces = self.cascade.detectMultiScale(processed_img, scaleFactor=1.01, minNeighbors=3, minSize=(75, 75))
        # cat_faces = self.cascade.detectMultiScale(processed_img, scaleFactor=1.01, minNeighbors=1)
        # cat_faces = self.cascade.detectMultiScale(processed_img)
        print(cat_faces)
        processed_img = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2BGR)
        for (i, (x, y, w, h)) in enumerate(cat_faces):
            cv2.rectangle(processed_img, (x, y), (x+w, y+h), (0,255, 0), 3)
            cv2.putText(processed_img, "Daisy - #{}".format(i + 1), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

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