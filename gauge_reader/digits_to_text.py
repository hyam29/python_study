from imutils.perspective import four_point_transform
from imutils import contours
import imutils
import cv2

import numpy as np
from skimage import filters

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
	(1, 1, 1, 1, 1, 1, 1): 8,
	(1, 1, 1, 1, 0, 1, 1): 9
}

# 이미지 로드
image = cv2.imread(r"C:\python_dev\gauge_to_text_baeksuk\digital_99999\src\output\001.01.png")


# 이미지 전처리 -> 윤곽선 추출
image = imutils.resize(image, height=500)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(blurred, 50, 200, 255)

# cv2.imshow("edged image", edged)

##################################################################################################

# LCD 영역 찾기
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
displayCnt = None

for c in cnts:
    # 윤곽선 근사치 적용
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)

    # contour 4각형이면, display
    if len(approx) == 4:
        displayCnt = approx
        break

displayCnt = None
# loop over the contours
for c in cnts:
	# approximate the contour
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	# if the contour has four vertices, then we have found
	# the thermostat display
	if len(approx) == 4:
		displayCnt = approx
		break

# 모듈 이용하여 정점 4개 -> LCD 추출
warped = four_point_transform(gray, displayCnt.reshape(4, 2))
output = four_point_transform(image, displayCnt.reshape(4, 2))

# cv2.imshow("Warped Output Image", output)

##################################################################################################

# 숫자 추출
thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU) [1]
# 소수점 제거
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel) # 작은 객체(=노이즈) 제거

# 작은 세그먼트를 병합하기 위한 팽창 연산 (1 인식이 안되는 해결을 위함)
kernel = np.ones((2, 2), np.uint8)
thresh = cv2.dilate(thresh, kernel, iterations=1)

# 작은 객체를 제거하여 더 잘린 숫자 찾기
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
digitCnts = []

cv2.imshow('thresh', thresh);


##################################################################################################

# 정확한 숫자 찾기
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
digitCnts = [] # 숫자 윤곽선 저장

for c in cnts:
	# compute the bounding box of the contour
	(x, y, w, h) = cv2.boundingRect(c)
	# if the contour is sufficiently large, it must be a digit

	# if w >= 10 and (h >= 15 and h <= 70):
	# 	digitCnts.append(c)
	# 종횡비 추가
	aspectRatio = w / float(h)
	if 0.1 < aspectRatio < 1.0 and w >= 3 and h >= 20:  # 비율과 크기 조건을 조정
		digitCnts.append(c)

# x,y 좌표를 기준으로 왼쪽에서 오른쪽으로 자릿수 윤곽선 분류
digitCnts = contours.sort_contours(digitCnts, method="left-to-right")[0]
digits = []

for c in digitCnts:
	# digit ROI 추출
	(x,y,w,h) = cv2.boundingRect(c)

	# 숫자 1을 위한 조건
	is_digit_one = w < 15
	if w < 15:
		x = max(0, x - w)  # 왼쪽으로 너비의 2배만큼 확장
		w = w * 2  # 너비를 3배로 확장 (1 배는 원래 크기, 2배는 확장한 부분)

	roi = thresh[y:y + h, x:x + w]
	
    # 7-세그먼트의 대략적인 높이, 폭 계산
	(roiH, roiW) = roi.shape
	(dW, dH) = (int (roiW * 0.25), int(roiH * 0.15))
	dHC = int(roiH * 0.05)

	print('출력내용출력내용출력내용출력내용출력내용출력내용 : ', (roiH, roiW))
	
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
		if total / float(area) > 0.4:
			on[i]= 1

	print('인식내용인식내용 : ', on)

    # lookup the digit and draw it on the image
	# digit = DIGITS_LOOKUP[tuple(on)]
	digit = DIGITS_LOOKUP.get(tuple(on), -1)  # 인식되지 않는 숫자는 -1로 표시
	digits.append(digit)

	if is_digit_one:
		# 숫자 '1'에 대해서만 바운딩 박스 위치 이동
		x_shift = 3  # 이동시킬 픽셀 수
		y_shift = 1  # y 좌표 이동시킬 픽셀 수
		cv2.rectangle(output, (x - x_shift, y - y_shift), (x + w - x_shift, y + h - y_shift), (0, 255, 0), 1)
		cv2.putText(output, str(digit), (x - 10 - x_shift, y - 10 - y_shift), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
	else:
		cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 1)
		cv2.putText(output, str(digit), (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

# display the digits
print(u"{}{}{}{}{}".format(*digits))
# cv2.imshow("Input", image)
cv2.imshow("Output", output)


cv2.waitKey(0)
cv2.destroyAllWindows()
