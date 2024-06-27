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
images = glob.glob(r'C:\python_dev\calibration\calibration_images\*.png')  # 실제 이미지 경로로 수정

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
    np.savez(r"C:\python_dev\calibration\calibration_images\calibration_data.npz", mtx=mtx, dist=dist)
    print("캘리브레이션 데이터를 성공적으로 저장했습니다.")
else:
    print("체커보드 이미지를 찾을 수 없습니다. 캘리브레이션을 수행할 수 없습니다.")


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import cv2
import numpy as np
import urllib.request

# 캘리브레이션 데이터 로드
calibration_data = np.load(r"C:\python_dev\calibration\calibration_images\calibration_data.npz")
mtx = calibration_data['mtx']
dist = calibration_data['dist']

# 스트림 URL 설정
stream_url = 'http://192.168.1.100:8080/?action=stream'

# 스트림 열기
stream = urllib.request.urlopen(stream_url)
bytes_data = b''

while True:
        # 스트림에서 프레임 읽기
        bytes_data += stream.read(1024)
        a = bytes_data.find(b'\xff\xd8')
        b = bytes_data.find(b'\xff\xd9')
        
        if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                
                # 왜곡 보정
                h, w = frame.shape[:2]
                newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
                dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)

                # ROI로 자르기
                x, y, w, h = roi
                dst = dst[y:y+h, x:x+w]
                
                # 결과 출력
                cv2.imshow('Original', frame)
                cv2.imshow('Undistorted', dst)
        
                if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

cv2.destroyAllWindows()
