from imutils.perspective import four_point_transform
from imutils import contours
import imutils
import cv2
import numpy as np

import glob
import os
os.chdir("C:/python_dev/calibration/undistort_video_capture")

'''
7세그먼트가 이어지지 않으면( ㅡ 이렇게 이어져야하는데 -- 이렇게 되면) 인식을 제대로 못함
-> 영역확장처리 -> 숫자 외 LCD 영역과 겹쳐서 숫자인식을 제대로 못함
-> 추후 무조건 LCD만 인식해서 크롭해야 할 것

* 24.07.11
LCD 영역 추출이 힘들어 숫자영역만 크롭하는 방법으로 진행

'''

"""
7 segments indexes are:
0: top,
1: top left,
2: top right,
3: middle,
4: bottom left
5: bottom right
6: bottom
"""

DIGITS_LOOKUP = {
	(1, 1, 1, 0, 1, 1, 1): 0,
	(0, 0, 1, 0, 0, 1, 0): 1,
	(1, 0, 1, 1, 1, 0, 1): 2,
	(1, 0, 1, 1, 0, 1, 1): 3,
	(0, 1, 1, 1, 0, 1, 0): 4,
	(1, 1, 0, 1, 0, 1, 1): 5,
	(1, 1, 0, 1, 1, 1, 1): 6,
	(1, 0, 1, 0, 0, 1, 0): 7,
	(1, 1, 1, 0, 0, 1, 0): 7,
	(1, 1, 1, 1, 1, 1, 1): 8,
	(1, 1, 1, 1, 0, 1, 1): 9,
	(1, 1, 1, 1, 0, 1, 0): 9
}

# 이미지 로드
list_of_files = glob.glob('*.jpg')  # 현재 디렉토리의 모든 .jpg 파일 가져오기
latest_file = max(list_of_files, key=os.path.getctime)  # 가장 최신 파일 가져오기
image_path = latest_file
image = cv2.imread(image_path)
height, width = image.shape[:2]


# 특정 영역으로 이미지 자르기
x, y, w, h = 590, 50, 150, 150  # 자르기 시작할 x, y 좌표 및 폭(w), 높이(h)
image = image[y:y+h, x:x+w]
# cv2.imshow("Cropped Image", image) # 결과


# 이미지 전처리
image = imutils.resize(image, height=500)
rotated = imutils.rotate(image, 2) # 이미지 2도 반시계 회전
# cv2.imshow('rotated', rotated)
gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)

##################################################################################################

# 디지털 숫자 추출
# thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU) [1]
thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV) [1]
blurred = cv2.GaussianBlur(thresh, (5, 5), 0)

# 이진화 적용
_, binary = cv2.threshold(blurred, 180, 255, cv2.THRESH_BINARY_INV)

# 소수점 제거
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
thresh = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel) # 작은 객체(=노이즈) 제거

# 작은 세그먼트를 병합하기 위한 추가 팽창 연산 (1 인식이 안되는 해결을 위함)
kernel = np.ones((3, 3), np.uint8)
thresh = cv2.dilate(thresh, kernel, iterations=1)

# 작은 객체를 제거하여 더 잘린 숫자 찾기
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

cv2.imshow('thresh', thresh);


##################################################################################################

'''
숫자영역 찾기
'''
output = image.copy()

# 정확한 숫자 찾기
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
digitCnts = [] # 숫자 윤곽선 저장

for c in cnts:
	(x, y, w, h) = cv2.boundingRect(c)
	if (w > 20 and w < 100) and (h >= 80 and h <= 140):
		# if (w < 19):  # 숫자 1을 위한 조건
		# 	x = max(0, x - 30)  # 왼쪽으로 10픽셀 확장
		# 	w += 40  # 너비를 20픽셀 확장
		digitCnts.append(c)
		

'''
# 조건에 맞는 윤곽선만 추가
if (w >= 30 and w <= 50) and (h >= 35 and h <= 80):
	digitCnts.append(c)
'''


# x,y 좌표를 기준으로 왼쪽에서 오른쪽으로 자릿수 윤곽선 분류
digitCnts = contours.sort_contours(digitCnts, method="left-to-right")[0]
digits = []

for c in digitCnts:
	# digit ROI 추출
	(x,y,w,h) = cv2.boundingRect(c)

	# 숫자 1을 위한 조건
	is_digit_one = w < 35
	if w < 35:
		x = max(0, x - w - 5)  # 왼쪽으로 너비의 2배만큼 확장
		w = w * 2  # 너비를 3배로 확장 (1 배는 원래 크기, 2배는 확장한 부분)

	roi = thresh[y:y + h, x:x + w]
	
    # 7-세그먼트의 대략적인 높이, 폭 계산
	(roiH, roiW) = roi.shape
	(dW, dH) = (int (roiW * 0.25), int(roiH * 0.15))
	dHC = int(roiH * 0.05)

	print('(너비, 높이) 출력 : ', (roiW, roiH))
	
    # 7-세그먼트 정의
	segments = [
		((0, 0), (w, dH)),  # 상단
		((0, 0), (dW, h // 2)),  # 좌상
		((w - dW, 0), (w, h // 2)),  # 우상
		((0, (h // 2) - dHC), (w, (h // 2) + dHC)),  # 중앙
		((0, h // 2), (dW, h)),  # 좌하
		((w - dW, h // 2), (w, h)),  # 우하
		((0, h - dH), (w, h))  # 하단
	]
	on = [0] * len(segments)

	# loop over the segments
	for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
		# extract the segment ROI, count the total number of
		# thresholded pixels in the segment, and then compute
		# the area of the segment
		segROI = roi[yA:yB, xA:xB]
		total = cv2.countNonZero(segROI)
		area = (xB - xA) * (yB - yA)
		# if the total number of non-zero pixels is greater than
		# 40% of the area, mark the segment as "on"
		# if total / float(area) > 0.4:
		# 	on[i]= 1
		if area > 0 and total / float(area) > 0.45:
			on[i] = 1

	print('7 segment 인식내용 : ', on)

    # lookup the digit and draw it on the image
	# digit = DIGITS_LOOKUP[tuple(on)]
	digit = DIGITS_LOOKUP.get(tuple(on), -1)  # 인식되지 않는 숫자는 -1로 표시
	digits.append(digit)

	# if is_digit_one:
	# 	# 숫자 '1'에 대해서만 바운딩 박스 위치 이동
	# 	x_shift = 3  # 이동시킬 픽셀 수
	# 	y_shift = 1  # y 좌표 이동시킬 픽셀 수
	# 	cv2.rectangle(output, (x - x_shift, y - y_shift), (x + w - x_shift, y + h - y_shift), (0, 255, 0), 1)
	# 	cv2.putText(output, str(digit), (x - 10 - x_shift, y - 10 - y_shift), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
	# else:

	# 인식 영역 바운딩 박스 그리기 및 인식 숫자 값 표시
	cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 1)
	cv2.putText(output, str(digit), (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)




# display the digits
print("인식된 숫자: {}".format("".join(map(str, digits))))
# cv2.imshow("Input", image)
cv2.imshow("Output", output)

cv2.waitKey(0)
cv2.destroyAllWindows()
