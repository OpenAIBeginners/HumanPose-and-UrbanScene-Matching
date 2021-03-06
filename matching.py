from urbanscene.urban_scene import match_scene_multi
import posematching.multi_person as multi_person
import logging
import thresholds
import plot_vars
from matplotlib import pyplot as plt
import cv2
import numpy as np
logger = logging.getLogger("match_whole")

import time

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        logger.critical('%s function took %0.3f ms' % (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap

# Performs the whole matching
# First multi pose matching, followed by urbanscene matching
@timing
def match_whole(model_pose_features, input_pose_features, detector, matcher, model_image, input_image, plot_us=False, plot_mp=False):

    result_pose_matching = multi_person.match(model_pose_features, input_pose_features,normalise=True, plot=plot_mp, input_image = input_image, model_image=model_image)
    #logger.debug("---Result pose matching: --")
    #logger.debug(result_pose_matching)

    if result_pose_matching.match_bool:
        #logger.debug(result_pose_matching.matching_permutations)
        logger.info("===> Pose matching succes!")

    else:
        logger.info("No matching poses found, so quit URBAN SCENE MATCHING")
        if plot_us or plot_mp:
            f = plt.figure(figsize=(10, 8))
            fs = 10 #fontsize
            markersize = 3
            f.suptitle("No matching poses found, so quit URBAN SCENE MATCHING", fontsize=10)
            plt.subplot(1, 2, 1)
            plt.imshow(np.asarray(input_image), cmap='gray')
            for i in range(0, len(input_pose_features)):
                plt.plot(*zip(*input_pose_features[i]), marker='o', color='blue', label='pose', ls='', ms=markersize - 1)
            plt.title("input: " + plot_vars.input_name + " (" + str(plot_vars.amount_input_persons) + " pers)", fontsize=fs)

            plt.subplot(1, 2, 2)
            plt.imshow(np.asarray(model_image), cmap='gray')
            for i in range(0, len(model_pose_features)):
                plt.plot(*zip(*model_pose_features[i]), marker='o', color='blue', label='pose', ls='', ms=markersize - 1)
            plt.title("model: " + plot_vars.model_name + " (" + str(plot_vars.amount_model_persons) + " pers)", fontsize=fs)

            plot_name = plot_vars.model_name.split(".")[0] + "_" + plot_vars.input_name.split(".")[0] + "_FALSE"
            plt.savefig('./plots/' + plot_name + '.png')
        return (False,False)
        #exit()

    logger.debug("--- Starting urbanscene matching ---")
    # Loop over all found matching comnbinations
    # And order input poses according to matching model poses
    for matching_permuations, result in result_pose_matching.matching_permutations.items():
        model_poses = result['model']
        input_poses = result['input']
        #logger.debug(model_poses)
        #logger.debug(input_poses)

        model_image_copy = model_image  #TODO make hard copy ??
        input_image_copy = input_image

        error = match_scene_multi(detector, matcher,
                                            model_image_copy, input_image_copy,
                                            model_poses,input_poses,
                                            plot_us)
        if error <= thresholds.AFFINE_TRANS_WHOLE_DISTANCE:
            logger.info("===> MATCH! permutation %s  score:%0.4f (thresh ca %0.4f)",
                        matching_permuations, round(error, 4), thresholds.AFFINE_TRANS_WHOLE_DISTANCE)
            return (True,True)
        else:
            logger.info("===> NO-MATCH! permutation %s  score:%0.4f (thresh ca %0.4f)",
                        matching_permuations, round(error, 4), thresholds.AFFINE_TRANS_WHOLE_DISTANCE)
            return (True,False)