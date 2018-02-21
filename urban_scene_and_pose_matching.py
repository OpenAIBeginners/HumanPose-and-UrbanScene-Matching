# https://docs.opencv.org/master/d1/de0/tutorial_py_feature_homography.html

import cv2
import numpy as np
from matplotlib import pyplot as plt
import clustering
import affine_transformation
import matplotlib.patches as mpatches
import util
import feature_operations

MIN_MATCH_COUNT = 10

model_name = 'trap7'   # goeie : "pisa9"  taj3  # trap1     trap1
input_name = 'trap8'  # goeie : "pisa10"  taj4  # trap2     trap3
img_tag = 'jpg'

# goeie voorbeelden zijn pisa9 en pisa10
model_image = cv2.imread('img/' + model_name + '.' + img_tag ,0)
input_image = cv2.imread('img/' + input_name + '.' + img_tag ,0)
# Resize
# TODO: optimize + altijd noodzakelijk om te resizen?
model_image, input_image = util.resize_img(model_image, input_image)

list_poses = {
    # 1: linkerpols   2:rechterpols
    "trap1": np.array([[113, 290], [179, 290]]),  #np.array([[113, 290], [179, 290]], np.float32)  # trap1
    "trap2": np.array([[127, 237], [206, 234]]),  # np.array([[127, 237], [206, 234]], np.float32)  # trap1
    "trap3": np.array([[218, 299], [280, 300]]),
    "trap4": np.array([[254, 248], [293, 253]]),
    "trap7": np.array([[254, 248], [293, 253]]),
    "trap8": np.array([[150, 230],[319, 570]]),  #trap8   rpols, renkel, lenkel
    "trap9": np.array([[136, 230], [297, 536], [343, 542]]),  #trap9  rpols, renkel, lenkel
    "taj3": np.array([[391, 92], [429, 126]]),  # taj3  enkel recher pols + r elbow     #np.array([[391, 92], [517, 148]])  # taj3  enkel recher pols + nek
    "taj4": np.array([[303, 37], [347, 70]]),   # taj4 enkel rechter pols + r elbow     #np.array([[303, 37], [412, 90]])  # taj4 enkel rechter pols + nek
    "pisa9": np.array([[152, 334], [153, 425]]),  #  np.array([[256, 362], [247, 400]], np.float32)
    "pisa10" : np.array([[256, 362], [247, 400]])
    }

model_pose_features = list_poses[model_name]
input_pose_features = list_poses[input_name]

assert model_pose_features.shape == input_pose_features.shape

# --------- SIFT FEATURE DETETCION & DESCRIPTION ------------------------
kp_model, des_model = feature_operations.sift_detect_and_compute(model_image)
kp_input, des_input = feature_operations.sift_detect_and_compute(input_image)

# --------- FEATURE MATCHING : FLANN MATCHER -------------------
#(matchesMask, model_image_homo, good, model_pts, input_pts) = feature_operations.flann_matching(des_model, des_input, kp_model, kp_input, model_image, input_image)
(matchesMask, input_image_homo, good, model_pts, input_pts) = feature_operations.flann_matching(des_model, des_input, kp_model, kp_input, model_image, input_image)

# ---------------- DRAW MATCHES  -------------------------------
draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)
plt.figure()
img3 = cv2.drawMatches(model_image,kp_model,input_image_homo,kp_input,good,None,**draw_params)
plt.imshow(img3) # Draw greyvalue images
plt.show(block=False)


# ------- APPLY MASK AND ONLY KEEP THE FEATURES OF THE FIRST FOUND HOMOGRAPHY -----
# Convert mask array to an array of boolean type [ False True True False ... ]
my_mask = np.asarray(matchesMask).astype(bool)
# Apply mask to feature points of destination img, so only the features of homography remain
my_model_pts = model_pts[np.array(my_mask)]
my_input_pts = input_pts[np.array(my_mask)]

# Reshape to simple 2D array [ [x,y] , [x',y'], ... ]
model_pts_2D = np.squeeze(my_model_pts[:])
input_pts_2D = np.squeeze(my_input_pts[:])

print("Total good matches: ", len(good))
print("Total matches for bouding box des: ", len(my_model_pts))
print("Total matches for bouding box source: ", len(my_input_pts))

# ------------- Kmeans - CLUSTERING THE FEATURES -------------
# --> If more than one building is detected ie pisa9.jpg & pisa10.jpg => cluster & seperate in individual buildings
# define criteria and apply kmeans()
clustered_features, one_building = clustering.kmean(model_pts_2D, input_pts_2D)

# Reduce dimensions
clustered_model_features = np.squeeze(clustered_features[0])  # first elements in array are model features
clustered_input_features = np.squeeze(clustered_features[1])  # second elements in array are model features

feature_operations.plot_features(clustered_model_features, clustered_input_features, one_building, model_image, input_image)

feature_operations.affine_transform_urban_scene_and_pose(one_building, model_pose_features, input_pose_features,
                                                         clustered_input_features, clustered_model_features,model_image, input_image)


plt.show()










