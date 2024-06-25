import cv2
import numpy as np
import glob

# 체커보드 패턴의 내부 코너 수 (업로드한 이미지 기준)
CHECKERBOARD = (6, 9)

# 3D 포인트의 실제 좌표 설정
objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp = objp*25 # real size of the pattern is multiplied. (25mm)

objpoints = []  # 3D 포인트 저장할 배열
imgpoints = []  # 2D 포인트 저장할 배열

# 체커보드 이미지가 저장된 폴더 경로 설정
images = glob.glob(r'C:\python_dev\gauge_to_text\bizAnalog\calibration_images\*.png')  # 실제 이미지 경로로 수정

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 체커보드 코너 찾기
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, 
                                                cv2.CALIB_CB_ADAPTIVE_THRESH + 
                                                cv2.CALIB_CB_NORMALIZE_IMAGE + 
                                                cv2.CALIB_CB_FAST_CHECK)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

        # 코너를 그려서 확인
        img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners, ret)
        cv2.imshow('img', img)
        cv2.waitKey(500)
    else:
        print(f"체커보드 코너를 찾지 못했습니다: {fname}")

cv2.destroyAllWindows()

if objpoints and imgpoints:
    # 카메라 캘리브레이션
    # ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (1885, 880), None, None) # (해상도 가로, 세로)

    # 캘리브레이션 결과 저장
    np.savez("calibration_data", mtx=mtx, dist=dist) # 매트릭스, 왜곡 계수
    np.savez(r"C:\python_dev\gauge_to_text\bizAnalog\calibration_images\calibration_data.npz", mtx=mtx, dist=dist)
    print("캘리브레이션 데이터를 성공적으로 저장했습니다.")
else:
    print("체커보드 이미지를 찾을 수 없습니다. 캘리브레이션을 수행할 수 없습니다.")
