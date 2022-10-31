import cv2
import pickle

if __name__ == '__main__':
    file_path = "../cifar_after_divide/data_class_0"
    with open(file_path, "rb") as f:
        entry = pickle.load(f, encoding="latin1")
        for i in range(5000):
            img = entry['data'][i].reshape(3, 32, 32)
            img = img.transpose(1,2,0)
            # print((img.shape))
            cv2.imshow("img", img)
            cv2.waitKey(1000)
