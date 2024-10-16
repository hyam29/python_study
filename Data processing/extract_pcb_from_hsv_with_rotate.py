import cv2
import numpy as np
import os

# hsv 필터
def filter_image_by_hsv_color(img: np.ndarray, lower_color: tuple, upper_color: tuple):
    # BGR 이미지를 HSV 이미지로 변환
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    result_img = cv2.inRange(hsv_img, lower_color, upper_color)
    return result_img

def rotate_image(img, cropped_img, mask=None):
    """
    이미지를 수평/수직으로 맞추기 위한 함수
    
    Parameters:
    img (numpy.ndarray): 원본 이미지
    mask (numpy.ndarray, optional): 처리할 마스크 이미지. 필요시 함께 회전

    Returns:
    rotated_img (numpy.ndarray): 수평/수직이 맞춰진 이미지
    rotated_mask (numpy.ndarray, optional): 회전된 마스크 이미지. 마스크를 입력한 경우 반환
    """
    # 윤곽선 찾기
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 가장 큰 윤곽선 찾기 (PCB의 외곽선으로 가정)
    largest_contour = max(contours, key=cv2.contourArea)
    
    # 사각형 계산
    rect = cv2.minAreaRect(largest_contour)
    angle = rect[2]
    
    # 각도 조정 (OpenCV에서 각도가 -90도에서 0도로 반환되기 때문에 90도보다 작은 값만 회전)
    if angle < -45:
        angle += 90
    elif angle > 45:
        angle -= 90  # 45도보다 크게 기울어졌을 때는 반대 방향으로 회전
    
    # 자른 이미지의 중심 좌표 계산
    (h, w) = cropped_img.shape[:2]
    center = (w // 2, h // 2)
    
    # 회전 행렬 계산
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # 자른 이미지 회전
    rotated_img = cv2.warpAffine(cropped_img, rotation_matrix, (w, h))
    
    return rotated_img



# hsv 적용 후 영역 잘라내기
def extract_pcb_from_hsv_mask(image_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    # 원본 이미지 읽기
    img = cv2.imread(image_path)
    
    # HSV 필터링
    hsv_mask = filter_image_by_hsv_color(img, (35, 50, 50), (85, 255, 255))
    # cv2.imwrite(os.path.join(output_dir, "1_hsv_mask.png"), hsv_mask)
    
    # 노이즈 제거
    kernel = np.ones((5, 5), np.uint8)
    cleaned_mask = cv2.morphologyEx(hsv_mask, cv2.MORPH_OPEN, kernel)
    # cv2.imwrite(os.path.join(output_dir, "2_cleaned_mask.png"), cleaned_mask)
    
    # 윤곽선 찾기
    contours, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 가장 큰 윤곽선 찾기 (PCB의 외곽선으로 가정)
    largest_contour = max(contours, key=cv2.contourArea)
    
    # 바운딩 박스를 찾고 PCB 영역만 잘라내기
    x, y, w, h = cv2.boundingRect(largest_contour)
    cropped_pcb = img[y:y+h, x:x+w]
    # cv2.imwrite(os.path.join(output_dir, "3_cropped_pcb.png"), cropped_pcb)
    
    # 마스크 영역도 동일하게 잘라내기
    cropped_mask = cleaned_mask[y:y+h, x:x+w]

    # 자른 후 기울어진 기판을 수평으로 맞추기
    rotated_cropped_pcb = rotate_image(img, cropped_pcb, cropped_mask)
    cv2.imwrite(os.path.join(output_dir, "4_rotated_cropped_pcb.png"), rotated_cropped_pcb )
    
    return rotated_cropped_pcb 

result = extract_pcb_from_hsv_mask(r"C:\python_dev\smt\pcb_detect\test_img_3.jpg", r"C:\python_dev\smt\pcb_detect\extract_hsv_rotate_res")

