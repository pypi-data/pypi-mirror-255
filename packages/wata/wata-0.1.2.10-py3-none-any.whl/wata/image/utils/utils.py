import cv2
def show_img(path):
    img = cv2.imread(path)
    cv2.imshow('show_img', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()