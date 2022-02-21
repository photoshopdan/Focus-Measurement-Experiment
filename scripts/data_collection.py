import glob
import os
import csv
import json
from time import perf_counter

import boto3
import cv2
from skimage import measure
import pywt


def downscale(image, long_edge):
    # Proportionally downscale image based on long edge.
    img_h, img_w = image.shape[:2]
    if img_h >= img_w:
        img = cv2.resize(
            image,
            (int(long_edge / (img_h / img_w)), long_edge),
            cv2.INTER_LINEAR)
    else:
        img = cv2.resize(
            image,
            (long_edge, int(long_edge / (img_w / img_h))),
            cv2.INTER_LINEAR)
    
    return img

def describe(file):
    # Start client and send jpg to AWS for face detection and analysis.
    client = boto3.client('rekognition', region_name='eu-west-2')
    with open(file, 'rb') as image:
        response = client.detect_faces(Image={'Bytes': image.read()},
                                       Attributes=['DEFAULT'])

        # Fail on zero or multiple face detection, otherwise return response.
        if not response['FaceDetails']:
            return None
        elif len(response['FaceDetails']) > 1:
            return None
        else:
            return response['FaceDetails'][0]

def variance_of_laplacian(image):
    # Compute the Laplacian and return the variance.
    return cv2.Laplacian(image, cv2.CV_64F).var()

def perceptual_blur_metric(image):
    # Apply Scikit-images's no-reference perceptual blur metric.
    return measure.blur_effect(image, h_size=11)

def tenengrad_variance(image):
    # Apply the Tenengrad method by computing the x and y image gradients, then
    # return the variance of the gradient magnitudes for each pixel.
    gx = cv2.Sobel(image, cv2.CV_64F, 1, 0, 3, borderType=cv2.BORDER_REFLECT)
    gy = cv2.Sobel(image, cv2.CV_64F, 0, 1, 3, borderType=cv2.BORDER_REFLECT)
    return ((gx**2 + gy**2)**0.5).var()

def wavelet_coefficients_variance(image):
    coeffs = pywt.dwt2(image, 'db6', 'reflect')
    cA, (cH, cV, cD) = coeffs
    return cH.var() + cV.var() + cD.var()
    
    
def main():
    # User parameters.
    downscale_long_edge = 1200
    eye_radius = 48
    blur_stdev = [0, 1, 2, 3, 4, 5]
    
    # List files in the input image folder.
    files = glob.glob('D:\\Downloads\\Sharpness Test\\Images_test\\*.jpg')

    # Create directory for downsized images.
    temp_dir = 'Downsized'
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    # Create CSV to store data.
    with open('results_test.csv', 'w', newline='\n') as csvfile:
        results = csv.writer(csvfile, delimiter=',', quotechar='"',
                             quoting=csv.QUOTE_NONNUMERIC)
        results.writerow(['File', 'Gaussian kernel standard deviation',
                          'AWS Sharpness',
                          'VoL Left', 'VoL Right', 'VoL Mean', 'VoL Time',
                          'PBM Left', 'PBM Right', 'PBM Mean', 'PBM Time',
                          'TV Left', 'TV Right', 'TV Mean', 'TV Time',
                          'WCV Left', 'WCV Right', 'WCV Mean', 'WCV Time'])

        # Iterate over images.
        for file in files:
            print(f'Processing {os.path.basename(file)}')
            # Downsize image.
            img = cv2.imread(file, cv2.IMREAD_COLOR)
            img = downscale(img, downscale_long_edge)
            temp_file = os.path.join(temp_dir, os.path.basename(file))
            
            # Iterate over blurs.
            eyes = []
            write_data = []
            for blur in blur_stdev:
                if blur != 0:
                    img_b = cv2.GaussianBlur(img, (0, 0), blur, blur,
                                             borderType=cv2.BORDER_REFLECT)
                else:
                    img_b = img
                cv2.imwrite(temp_file, img_b, [cv2.IMWRITE_JPEG_QUALITY, 90])

                # Get face data from AWS.
                face_data = describe(temp_file)
                if face_data == None:
                    print('    Face detection error. Image not processed.')
                    os.remove(temp_file)
                    break
                
                # Get coordinates of both eyes if this is the initial image.
                if not eyes:
                    for i in face_data['Landmarks']:
                        if i['Type'] == 'eyeLeft':
                            eyes.append((int(img.shape[1] * i['X']),
                                         int(img.shape[0] * i['Y'])))
                        elif i['Type'] == 'eyeRight':
                            eyes.append((int(img.shape[1] * i['X']),
                                         int(img.shape[0] * i['Y'])))

                # Create ROI for each eye.
                eye_img_l = img_b[eyes[0][1] - eye_radius:eyes[0][1]
                                  + eye_radius,
                                  eyes[0][0] - eye_radius:eyes[0][0]
                                  + eye_radius]
                eye_img_r = img_b[eyes[1][1] - eye_radius:eyes[1][1]
                                  + eye_radius,
                                  eyes[1][0] - eye_radius:eyes[1][0]
                                  + eye_radius]
                
                # A single channel image is required so we discard the blue and
                # red channels.
                eye_img_l, eye_img_r = eye_img_l[:,:,1], eye_img_r[:,:,1]

                # Gather and time blur values.
                start = perf_counter()
                vol_l = variance_of_laplacian(eye_img_l)
                vol_r = variance_of_laplacian(eye_img_r)
                stop = perf_counter()
                vol_t = stop - start

                start = perf_counter()
                pbm_l = perceptual_blur_metric(eye_img_l)
                pbm_r = perceptual_blur_metric(eye_img_r)
                stop = perf_counter()
                pbm_t = stop - start

                start = perf_counter()
                ten_l = tenengrad_variance(eye_img_l)
                ten_r = tenengrad_variance(eye_img_r)
                stop = perf_counter()
                ten_t = stop - start

                start = perf_counter()
                wcv_l = wavelet_coefficients_variance(eye_img_l)
                wcv_r = wavelet_coefficients_variance(eye_img_r)
                stop = perf_counter()
                wcv_t = stop - start

                # Write results to CSV.
                write_data.append([os.path.basename(file),
                                   blur,
                                   face_data['Quality']['Sharpness'],
                                   vol_l, vol_r, (vol_l + vol_r) / 2, vol_t,
                                   pbm_l, pbm_r, (pbm_l + pbm_r) / 2, pbm_t,
                                   ten_l, ten_r, (ten_l + ten_r) / 2, ten_t,
                                   wcv_l, wcv_r, (wcv_l + wcv_r) / 2, wcv_t])

                # Clean up temp folder.
                os.remove(temp_file)

            # If one of the blur images failed, don't write any of the blur
            # images. Otherwise write all of them.
            if len(write_data) == len(blur_stdev):
                for line in write_data:
                    results.writerow(line)

if __name__ == '__main__':
    main()
