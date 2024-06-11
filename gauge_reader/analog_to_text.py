
'''  
Copyright (c) 2017 Intel Corporation.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
'''

import cv2
import numpy as np
#import paho.mqtt.client as mqtt
import time
import os
os.chdir('C:/python_dev/gauge_to_text/analog')

def avg_circles(circles, b):
    avg_x=0
    avg_y=0
    avg_r=0
    for i in range(b):
        #optional - average for multiple circles (can happen when a gauge is at a slight angle)
        avg_x = avg_x + circles[0][i][0]
        avg_y = avg_y + circles[0][i][1]
        avg_r = avg_r + circles[0][i][2]
    avg_x = int(avg_x/(b))
    avg_y = int(avg_y/(b))
    avg_r = int(avg_r/(b))
    return avg_x, avg_y, avg_r

def dist_2_pts(x1, y1, x2, y2):
    #print np.sqrt((x2-x1)^2+(y2-y1)^2)
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calibrate_gauge(gauge_number, file_type):
    '''
        This function should be run using a test image in order to calibrate the range available to the dial as well as the
        units.  It works by first finding the center point and radius of the gauge.  Then it draws lines at hard coded intervals
        (separation) in degrees.  It then prompts the user to enter position in degrees of the lowest possible value of the gauge,
        as well as the starting value (which is probably zero in most cases but it won't assume that).  It will then ask for the
        position in degrees of the largest possible value of the gauge. Finally, it will ask for the units.  This assumes that
        the gauge is linear (as most probably are).
        It will return the min value with angle in degrees (as a tuple), the max value with angle in degrees (as a tuple),
        and the units (as a string).

        
        이 함수는 테스트 이미지를 사용하여 다이얼의 가용 범위와 단위를 보정하기 위해 실행되어야 합니다. 
        먼저 게이지의 중심점과 반지름을 찾습니다. 그런 다음 하드 코딩된 간격(각도)으로 선을 그립니다. 
        그런 다음 사용자에게 게이지의 최소값 위치(각도)와 시작 값을 입력하도록 요청합니다. 
        시작 값은 대부분의 경우 아마도 0이지만 이를 가정하지는 않습니다. 
        그런 다음 게이지의 최대값 위치(각도)를 입력하도록 요청합니다. 
        마지막으로 단위를 묻습니다. 이 함수는 게이지가 선형이라고 가정합니다(대부분 그렇겠지만). 
        최종적으로 최소값과 각도(튜플 형태), 최대값과 각도(튜플 형태), 단위(문자열 형태)를 반환합니다.
    '''
    # 이미지 파일 경로를 동적으로 생성
    img = cv2.imread('gauge-%s.%s' %(gauge_number, file_type))
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #convert to gray
    #gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # gray = cv2.medianBlur(gray, 5)

    #for testing, output gray image -> 이미지 회색 변경
    # cv2.imwrite('gauge-%s-bw.%s' %(gauge_number, file_type),gray)

    #detect circles (2ed. 원형 감지)
    #restricting the search from 35-48% of the possible radii gives fairly good results across different samples.  Remember that
    #these are pixel values which correspond to the possible radii search range.
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, np.array([]), 100, 50, int(height*0.31), int(height*0.40))
    # average found circles, found it to be more accurate than trying to tune HoughCircles parameters to get just the right one
    a, b, c = circles.shape
    x,y,r = avg_circles(circles, b)

    print('x,y,r ::::::::::::::::::::::::::::::::::: ', x,y,r)

    #draw center and circle (외곽선(게이지 테두리)과 게이지 중심에 점 그리기)
    cv2.circle(img, (x, y), r, (0, 0, 255), 3, cv2.LINE_AA)  # draw circle
    cv2.circle(img, (x, y), 2, (0, 255, 0), 3, cv2.LINE_AA)  # draw center of circle

    #for testing, output circles on image
    # cv2.imwrite('gauge-%s-circles.%s' % (gauge_number, file_type), img)


##################################################################################################
    # 사용자 입력값(설정된 간격)을 참조하여 x,y 값 설정 후 이미지에 선과 레이블 추가


    #for calibration, plot lines from center going out at every 10 degrees and add marker
    #for i from 0 to 36 (every 10 deg)

    '''
    goes through the motion of a circle and sets x and y values based on the set separation spacing.  Also adds text to each
    line.  These lines and text labels serve as the reference point for the user to enter
    NOTE: by default this approach sets 0/360 to be the +x axis (if the image has a cartesian grid in the middle), the addition
    (i+9) in the text offset rotates the labels by 90 degrees so 0/360 is at the bottom (-y in cartesian).  So this assumes the
    gauge is aligned in the image, but it can be adjusted by changing the value of 9 to something else.
    '''
    separation = 10.0 #in degrees
    interval = int(360 / separation)
    p1 = np.zeros((interval,2))  #set empty arrays
    p2 = np.zeros((interval,2))
    p_text = np.zeros((interval,2))
    for i in range(0,interval):
        for j in range(0,2):
            if (j%2==0):
                p1[i][j] = x + 0.9 * r * np.cos(separation * i * 3.14 / 180) #point for lines
            else:
                p1[i][j] = y + 0.9 * r * np.sin(separation * i * 3.14 / 180)
    text_offset_x = 10
    text_offset_y = 5
    for i in range(0, interval):
        for j in range(0, 2):
            if (j % 2 == 0):
                p2[i][j] = x + r * np.cos(separation * i * 3.14 / 180)
                p_text[i][j] = x - text_offset_x + 1.2 * r * np.cos((separation) * (i+9) * 3.14 / 180) #point for text labels, i+9 rotates the labels by 90 degrees
            else:
                p2[i][j] = y + r * np.sin(separation * i * 3.14 / 180)
                p_text[i][j] = y + text_offset_y + 1.2* r * np.sin((separation) * (i+9) * 3.14 / 180)  # point for text labels, i+9 rotates the labels by 90 degrees

    #add the lines and labels to the image (이미지에 선과 라벨 추가)
    for i in range(0,interval):
        cv2.line(img, (int(p1[i][0]), int(p1[i][1])), (int(p2[i][0]), int(p2[i][1])),(0, 255, 0), 2)
        cv2.putText(img, '%s' %(int(i*separation)), (int(p_text[i][0]), int(p_text[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(0,0,0),1,cv2.LINE_AA)

    cv2.imwrite('gauge-%s-calibration.%s' % (gauge_number, file_type), img)

##################################################################################################

    # 3th. 게이지 최대최소값, 각도 입력
    #get user input on min, max, values, and units (사용자 입력값 입력)
    print ('gauge number: %s' %gauge_number)
    min_angle = 45 # 90-45 = 45
    max_angle = 310 # 360-45 = 315
    min_value = 0
    max_value = 1000
    units = "inHg"

    #for testing purposes: hardcode and comment out raw_inputs above
    # min_angle = 45
    # max_angle = 320
    # min_value = 0
    # max_value = 200
    # units = "PSI"

    return min_angle, max_angle, min_value, max_value, units, x, y, r

##################################################################################################

def get_current_value(img, min_angle, max_angle, min_value, max_value, x, y, r, gauge_number, file_type):

    #for testing purposes
    #img = cv2.imread('gauge-%s.%s' % (gauge_number, file_type))

    gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Set threshold and maxValue
    thresh = 175
    maxValue = 255

    # for testing purposes, found cv2.THRESH_BINARY_INV to perform the best
    # th, dst1 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY);
    # th, dst2 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY_INV);
    # th, dst3 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_TRUNC);
    # th, dst4 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_TOZERO);
    # th, dst5 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_TOZERO_INV);
    # cv2.imwrite('gauge-%s-dst1.%s' % (gauge_number, file_type), dst1)
    # cv2.imwrite('gauge-%s-dst2.%s' % (gauge_number, file_type), dst2)
    # cv2.imwrite('gauge-%s-dst3.%s' % (gauge_number, file_type), dst3)
    # cv2.imwrite('gauge-%s-dst4.%s' % (gauge_number, file_type), dst4)
    # cv2.imwrite('gauge-%s-dst5.%s' % (gauge_number, file_type), dst5)

    # apply thresholding which helps for finding lines
    th, dst2 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY_INV);

    # found Hough Lines generally performs better without Canny / blurring, though there were a couple exceptions where it would only work with Canny / blurring
    #dst2 = cv2.medianBlur(dst2, 5)
    #dst2 = cv2.Canny(dst2, 50, 150)
    #dst2 = cv2.GaussianBlur(dst2, (5, 5), 0)

    # for testing, show image after thresholding
    # cv2.imwrite('gauge-%s-tempdst2.%s' % (gauge_number, file_type), dst2)

    # find lines
    minLineLength = 10
    maxLineGap = 0
    lines = cv2.HoughLinesP(image=dst2, rho=1, theta=np.pi / 180, threshold=100,minLineLength=minLineLength, maxLineGap=0)  
    # rho is set to 3 to detect more lines, easier to get more then filter them out later -> 숫자가 작을수록 라인이 많이 생성

    #for testing purposes, show all found lines
    # for i in range(0, len(lines)):
    #     for x1, y1, x2, y2 in lines[i]:
    #         cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #         cv2.imwrite('gauge-%s-lines-test.%s' %(gauge_number, file_type), img)

    # remove all lines outside a given radius
    final_line_list = []
    #print "radius: %s" %r

    # 4th. 게이지 바늘 조정
    #diff1LowerBound and diff1UpperBound determine how close the line should be from the center
    #(중심에서 얼마나 가까워야하는 지 결정)
    diff1LowerBound = 0.1
    diff1UpperBound = 0.45
    #diff2LowerBound and diff2UpperBound determine how close the other point of the line should be to the outside of the gauge
    #(선의 다른 지점이 게이지 외부에 얼마나 가까워야하는 지 결정)
    diff2LowerBound = 0.5
    diff2UpperBound = 1.0
    for i in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            diff1 = dist_2_pts(x, y, x1, y1)  # x, y is center of circle
            diff2 = dist_2_pts(x, y, x2, y2)  # x, y is center of circle
            #set diff1 to be the smaller (closest to the center) of the two), makes the math easier = diff1을 중앙에 가장 가까운 것으로 설정해야 연산이 쉬워짐
            if (diff1 > diff2):
                temp = diff1
                diff1 = diff2
                diff2 = temp
            # check if line is within an acceptable range (라인이 허용 가능한 범위 내에 존재하는 지 확인)
            if (((diff1<diff1UpperBound*r) and (diff1>diff1LowerBound*r) and (diff2<diff2UpperBound*r)) and (diff2>diff2LowerBound*r)):
                line_length = dist_2_pts(x1, y1, x2, y2)
                # add to final list
                final_line_list.append([x1, y1, x2, y2])

    #testing only, show all lines after filtering
    for i in range(0,len(final_line_list)):
        x1 = final_line_list[i][0]
        y1 = final_line_list[i][1]
        x2 = final_line_list[i][2]
        y2 = final_line_list[i][3]
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # assumes the first line is the best one
    x1 = final_line_list[0][0]
    y1 = final_line_list[0][1]
    x2 = final_line_list[0][2]
    y2 = final_line_list[0][3]
    cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    #for testing purposes, show the line overlayed on the original image
    #cv2.imwrite('gauge-1-test.jpg', img)
    cv2.imwrite('gauge-%s-lines-2.%s' % (gauge_number, file_type), img)

    #find the farthest point from the center to be what is used to determine the angle
    dist_pt_0 = dist_2_pts(x, y, x1, y1)
    dist_pt_1 = dist_2_pts(x, y, x2, y2)
    if (dist_pt_0 > dist_pt_1):
        x_angle = x1 - x
        y_angle = y - y1
    else:
        x_angle = x2 - x
        y_angle = y - y2
    # take the arc tan of y/x to find the angle
    res = np.arctan(np.divide(float(y_angle), float(x_angle)))
    #np.rad2deg(res) #coverts to degrees

    # print x_angle
    # print y_angle
    # print res
    # print np.rad2deg(res)

    #these were determined by trial and error
    res = np.rad2deg(res)
    if x_angle > 0 and y_angle > 0:  #in quadrant I
        final_angle = 270 - res
    if x_angle < 0 and y_angle > 0:  #in quadrant II
        final_angle = 90 - res
    if x_angle < 0 and y_angle < 0:  #in quadrant III
        final_angle = 90 - res
    if x_angle > 0 and y_angle < 0:  #in quadrant IV
        final_angle = 270 - res

    #print final_angle

    old_min = float(min_angle)
    old_max = float(max_angle)

    new_min = float(min_value)
    new_max = float(max_value)

    old_value = final_angle

    old_range = (old_max - old_min)
    new_range = (new_max - new_min)
    new_value = (((old_value - old_min) * new_range) / old_range) + new_min

    return new_value

##################################################################################################

# 1st. gauge 이미지 파일명 입력 (파일명 형식 : gauge-?.jpg)

def main():
    gauge_number = 2
    file_type='jpg'
    # name the calibration image of your gauge 'gauge-#.jpg', for example 'gauge-5.jpg'.  It's written this way so you can easily try multiple images
    min_angle, max_angle, min_value, max_value, units, x, y, r = calibrate_gauge(gauge_number, file_type)

    #feed an image (or frame) to get the current value, based on the calibration, by default uses same image as calibration
    img = cv2.imread('gauge-%s.%s' % (gauge_number, file_type))
    val = get_current_value(img, min_angle, max_angle, min_value, max_value, x, y, r, gauge_number, file_type)
    print ("Current reading: %s %s" %(val, units))

if __name__=='__main__':
    main()

