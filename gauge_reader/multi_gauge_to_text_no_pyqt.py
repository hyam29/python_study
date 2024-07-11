import cv2
import numpy as np
import os
import glob
os.chdir("C:/python_dev/calibration/undistort_video_capture")

list_of_files = glob.glob('*.jpg')  # 현재 디렉토리의 모든 .jpg 파일 가져오기
latest_file = max(list_of_files, key=os.path.getctime)  # 가장 최신 파일 가져오기

# 게이지별 변수 설정 (반시계도 추후에 추가 필요)
gauges = [
    {"name": "온도계_1 : ", "start_angle": 45, "end_angle": 315, "start_value": 0, "end_value": 100, "needle_size": 0.9, "convention": "CW"},
    {"name": "온도계_2 : ", "start_angle": 45, "end_angle": 315, "start_value": 0, "end_value": 300, "needle_size": 0.9, "convention": "CW"}
]

# 이미지 로드
# image_path = 'gauge_11.jpg'
image_path = latest_file
image = cv2.imread(image_path)
height, width = image.shape[:2]

# 이미지 자르기
x, y, w, h = 450, 130, 500, 500  # 자르기 시작할 x, y 좌표 및 폭(w), 높이(h)
image = image[y:y+h, x:x+w]
# cv2.imshow("Cropped Image", image) # 결과

'''
# 이미지 로드 및 전처리
image_path = 'pre_gauge.jpg'

def load_and_preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image at path '{image_path}' not found.")
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    gray = cv2.GaussianBlur(gray, (5, 5), 1.0)
    return image, gray
'''


# 게이지 원 찾기
# def find_circles(image):
def find_circles(image):
    # 이미지 전처리
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 1)
    edged = cv2.Canny(blurred, 150, 250)
    # cv2.imshow('edged', edged) # 원 찾기 디버깅용

    circles = cv2.HoughCircles(edged, cv2.HOUGH_GRADIENT, dp=1.1, minDist=20, param1=10, param2=20, minRadius=20, maxRadius=100)
    # cv2.HoughCircles(image, method, dp(입력 영상과 축적 배열의 크기 비율, 1=동일해상도), minDist(검출 원 중심점들의 최소 거리), 
    # circles=None, param1=None(Canny에지 검출기의 높은 임계값), param2=None(축적배열에서 원 검출을 위한 임계값), minRadius=None(검출 원 최소 반지름), maxRadius=None) -> circles
    
    #  +  (나중에...) 반원 게이지 추가하기!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        return circles
    return None

# 게이지 바늘 찾기
'''
find_needle (원본이미지, 원형 게이지의 중심좌표(cx, cy), 반지름, 회색조 이미지)
'''
def find_needle(original_image, cx, cy, radius, needle_size):
    # 이미지 전처리
    gray2 = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    blurred2 = cv2.GaussianBlur(gray2, (7, 7), 1)
    edged2 = cv2.Canny(blurred2, 50, 250)
    # cv2.imshow('processed_needle', edged2) # 이미지 전처리 결과 확인용

    size = radius * needle_size # 바늘길이로 추정되는 값
    slices = 360 # 360도에서 몇 분할할지 결정
    factor = 360 / slices
    # center = tuple([cx, cy])
    center = [cx, cy]

    longest_dark = 0
    best_angle = 0

    for i in range(slices):
        angle = i * factor
        # converted_angle = (450 - angle) % 360 # 3시 방향을 0도
        x2 = cx + int(size * np.cos(angle * np.pi / 180.0))
        y2 = cy + int(size * np.sin(angle * np.pi / 180.0))
        # cv2.line(image, center, (x2, y2), 255, thickness=1) # slices 변수 값에 대한  시각화 (디버깅용)

        line_mask = np.zeros_like(edged2)
        cv2.line(line_mask, center, (x2, y2), 255, 1)
        masked = cv2.bitwise_and(edged2, edged2, mask=line_mask)
        # dark_length = np.mean(masked)
        dark_length = np.sum(masked)  # 어두운 픽셀의 합계로 변경

        if dark_length > longest_dark:
            longest_dark = dark_length
            best_angle = angle

    return best_angle


# 게이지 값 인식 (추후 value 값 범위 아닌 경우 처리도 해둬야 함)
def angle_to_value(angle, start_angle, end_angle, start_value, end_value, convention="CW"):
    # 6시를 0도로 변환
    angle = (angle - 90) % 360

    # start_angle을 0도로 설정
    adjusted_angle = (angle - start_angle) % 360  # start_angle을 기준으로 각도 조정
    if adjusted_angle < 0:
        adjusted_angle += 360
    
    angle_range = (end_angle - start_angle) % 360
    if angle_range == 0:
        angle_range = 360  # (error) Prevent division by zero

    value_range = end_value - start_value
    value = (adjusted_angle / angle_range) * value_range + start_value
    return value, adjusted_angle

    '''
    if convention == "CW":  # 시계 방향
        total_angle = (end_angle - start_angle) % 360
        relative_angle = (angle - start_angle) % 360
    else:  # 반시계 방향
        total_angle = (start_angle - end_angle) % 360
        relative_angle = (start_angle - angle) % 360

    value_range = end_value - start_value
    value = (relative_angle / total_angle) * value_range + start_value

    return value, relative_angle
    '''
    

# 인식된 원의 중심을 기준으로 다른 원을 제외하는 함수
def exclude_circle(circles, exclude_center, exclude_radius):
    filtered_circles = []
    for (x, y, r) in circles:
        distance = np.sqrt((x - exclude_center[0]) ** 2 + (y - exclude_center[1]) ** 2)
        if distance > exclude_radius:
            filtered_circles.append((x, y, r))
    return np.array(filtered_circles)


########################################################################################################

# 이미지 전체에서 원을 찾기
all_circles = find_circles(image)
if all_circles is None:
    print("No circles found")
else:
    print(f"Found {len(all_circles)} circles in total")

    original_image = image.copy()

    # 각 게이지에 대해 원과 바늘 찾기 및 값 계산
    for gauge in gauges:
        print(f"{gauge['name']}")
        if all_circles is None or len(all_circles) == 0:
            print(f"No more circles left to process for {gauge['name']}")
            break

        (x, y, r) = all_circles[0]  # 첫 번째 원을 선택

        # 바늘 찾기
        # cv2.imshow('prev_find_needle', original_image)
        best_angle = find_needle(original_image, x, y, r, gauge["needle_size"])
        print('best_angle ::::::::::::: ', best_angle)

        # 바늘을 이미지에 그림
        x2 = x + int(r * gauge["needle_size"] * np.cos(best_angle * np.pi / 180.0))
        y2 = y + int(r * gauge["needle_size"] * np.sin(best_angle * np.pi / 180.0))
        cv2.line(image, (x, y), (x2, y2), (0, 0, 255), thickness=2)
        # 원과 원의 중심점 그림
        cv2.circle(image, (x, y), r, (0, 255, 0), 4)
        cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        # 인식된 값 출력
        value, adjusted_angle = angle_to_value(best_angle, gauge["start_angle"], gauge["end_angle"], gauge["start_value"], gauge["end_value"])
        print(f'각도 ::: {adjusted_angle}도 ////////////////// 값 ::: {value:.2f}˚C')

        # 현재 원을 제외한 나머지 원들로 업데이트
        all_circles = exclude_circle(all_circles, (x, y), r * 1.5)


########################################################################################################

# 이미지 데이터 타입 변환 (8비트로 변환)
image_8bit = cv2.convertScaleAbs(image)
cv2.imshow("output", image_8bit)
cv2.waitKey(0)
cv2.destroyAllWindows()

