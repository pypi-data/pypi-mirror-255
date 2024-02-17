import settings
import numpy as np

from src.utils import generate_big_stick_possible_combinations
import math
from itertools import product
from copy import deepcopy
from more_itertools import unique_everseen
import builtins


logger = settings.logger

class StickRecommender1:

    def __init__(self, big_stick_id_size_mapping_dict, big_stick_id_dimension_tuple_mapping,
                 big_stick_dimension_tuple_id_mapping, all_big_stick_mold_dimension_tuple_mapping,
                 all_big_stick_dimension_tuple_mold_id_mapping, stock_pill_dict):
        self.small_stick_required_length = None
        self.mft_3D_flag = 0
        self.big_stick_id_size_mapping_dict = big_stick_id_size_mapping_dict
        self.big_stick_possible_combinations, self.big_stick_width_combinations, self.big_stick_depth_combinations = \
            generate_big_stick_possible_combinations(
                lower_range_width=settings.BIG_STICK_WIDTH_LOWER_RANGE,
                upper_range_width=settings.BIG_STICK_WIDTH_UPPER_RANGE,
                lower_range_depth=settings.BIG_STICK_DEPTH_LOWER_RANGE,
                upper_range_depth=settings.BIG_STICK_DEPTH_UPPER_RANGE,
                width_step_size=settings.BIG_STICK_WIDTH_STEP_SIZE, depth_step_size=settings.BIG_STICK_DEPTH_STEP_SIZE)
        self.big_stick_width_combinations = np.array(self.big_stick_width_combinations)
        self.big_stick_depth_combinations = np.array(self.big_stick_depth_combinations)
        self.big_stick_id_dimension_tuple_mapping = big_stick_id_dimension_tuple_mapping
        self.big_stick_dimension_tuple_id_mapping = big_stick_dimension_tuple_id_mapping
        self.all_big_stick_mold_dimension_tuple_mapping = all_big_stick_mold_dimension_tuple_mapping
        self.all_big_stick_dimension_tuple_mold_id_mapping = all_big_stick_dimension_tuple_mold_id_mapping
        self.stock_pill_dict = stock_pill_dict
        self.dct = {}
        self.drum_width1_3D = 0
        self.drum_width2_3D = 0
        self.drum_depth1_3D = 0
        self.drum_depth2_3D = 0
        self.small_stick_3D = 0
        self.drum_length_3D = 0
        self.depth_brush_3D = 0

    def measure_big_stick_depth_dimension(self, depth, width, length, shape, fillet):
        """
            This function measure the possible upper big stick and possible lower big stick for Depth
            This function is for some common percentage tolerance value
        """
        big_stick_required_depth = []
        depth_tolerance = 0
        depth = float(depth)
        width = float(width)
        length = float(length)
        fillet = float(fillet)

        if shape == "Oval":
            if abs(width - depth) < 1.3:
                self.mft_3D_flag = 1
                return big_stick_required_depth, depth_tolerance
            elif 1.3 <= abs(width - depth) < 2:
                for value in range(settings.OVAL_DEPTH_RANGE_LOWER1, settings.OVAL_DEPTH_RANGE_UPPER1,
                                   settings.OVAL_STEP_SIZE):
                    depth_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT <= depth + depth_tolerance <= settings.DEPTH_STICK_UPPER_LIMIT:
                        big_stick_depth_index1 = \
                        np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
                        big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
                        big_stick_required_depth.append(big_stick_temp_depth1)
            elif 2 <= abs(width - depth) < 3:
                for value in range(settings.OVAL_DEPTH_RANGE_LOWER2, settings.OVAL_DEPTH_RANGE_UPPER2,
                                   settings.OVAL_STEP_SIZE):
                    depth_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT <= depth + depth_tolerance <= settings.DEPTH_STICK_UPPER_LIMIT:
                        big_stick_depth_index1 = \
                            np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
                        big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
                        big_stick_required_depth.append(big_stick_temp_depth1)
            elif abs(width - depth) >= 3:
                for value in range(settings.OVAL_DEPTH_RANGE_LOWER3, settings.OVAL_DEPTH_RANGE_UPPER3,
                                   settings.OVAL_STEP_SIZE):
                    depth_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT <= depth + depth_tolerance <= settings.DEPTH_STICK_UPPER_LIMIT:
                        big_stick_depth_index1 = \
                            np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
                        big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
                        big_stick_required_depth.append(big_stick_temp_depth1)
            if not big_stick_required_depth:
                self.mft_3D_flag = 2
                return big_stick_required_depth, depth_tolerance

        elif shape == "Elliptical":
            if abs(width - depth) < 1.3:
                self.mft_3D_flag = 1
                return big_stick_required_depth, depth_tolerance
            elif 1.3 <= abs(width - depth) < 2:
                for value in range(settings.ELLIPTICAL_DEPTH_RANGE_LOWER1, settings.ELLIPTICAL_DEPTH_RANGE_UPPER1,
                                   settings.ELLIPTICAL_STEP_SIZE):
                    depth_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT <= depth + depth_tolerance <= settings.DEPTH_STICK_UPPER_LIMIT:
                        big_stick_depth_index1 = \
                            np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
                        big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
                        big_stick_required_depth.append(big_stick_temp_depth1)
            elif 2 <= abs(width - depth) < 3:
                for value in range(settings.ELLIPTICAL_DEPTH_RANGE_LOWER2, settings.ELLIPTICAL_DEPTH_RANGE_UPPER2,
                                   settings.ELLIPTICAL_STEP_SIZE):
                    depth_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT <= depth + depth_tolerance <= settings.DEPTH_STICK_UPPER_LIMIT:
                        big_stick_depth_index1 = \
                            np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
                        big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
                        big_stick_required_depth.append(big_stick_temp_depth1)
            elif abs(width - depth) >= 3:
                for value in range(settings.ELLIPTICAL_DEPTH_RANGE_LOWER3, settings.ELLIPTICAL_DEPTH_RANGE_UPPER3,
                                   settings.ELLIPTICAL_STEP_SIZE):
                    depth_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT <= depth + depth_tolerance <= settings.DEPTH_STICK_UPPER_LIMIT:
                        big_stick_depth_index1 = \
                            np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
                        big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
                        big_stick_required_depth.append(big_stick_temp_depth1)
            if not big_stick_required_depth:
                self.mft_3D_flag = 2
                return big_stick_required_depth, depth_tolerance

        elif shape == "Round Curved":
            if (fillet / depth) >= 0.7:
                for value in range(settings.ROUND_CURVED_DEPTH_RANGE_LOWER, settings.ROUND_CURVED_DEPTH_RANGE_UPPER,
                                   settings.ROUND_CURVED_STEP_SIZE):
                    depth_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT <= depth + depth_tolerance <= settings.DEPTH_STICK_UPPER_LIMIT:
                        big_stick_depth_index1 = \
                            np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
                        big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
                        big_stick_required_depth.append(big_stick_temp_depth1)
            elif (fillet / depth) < 0.7 or not big_stick_required_depth:
                """
                For mft_3D
                """
                self.mft_3D_flag = 2
                return big_stick_required_depth, depth_tolerance

        # elif shape == "Round Flat":
        #     if 2.25 < depth <= 3.5:
        #         for value in range(settings.ROUND_FLAT_DEPTH_RANGE_LOWER1, settings.ROUND_FLAT_DEPTH_RANGE_UPPER1,
        #                            settings.ROUND_FLAT_STEP_SIZE):
        #             depth_tolerance = 0.01 * value
        #             if settings.BOTH_STICK_LOWER_LIMIT < depth + depth_tolerance < settings.DEPTH_STICK_UPPER_LIMIT:
        #                 big_stick_depth_index1 = \
        #                     np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
        #                 big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
        #                 big_stick_required_depth.append(big_stick_temp_depth1)
        #     elif depth > 3.5:
        #         for value in range(settings.ROUND_FLAT_DEPTH_RANGE_LOWER2, settings.ROUND_FLAT_DEPTH_RANGE_UPPER2,
        #                            settings.ROUND_FLAT_STEP_SIZE):
        #             depth_tolerance = 0.01 * value
        #             if settings.BOTH_STICK_LOWER_LIMIT < depth + depth_tolerance < settings.DEPTH_STICK_UPPER_LIMIT:
        #                 big_stick_depth_index1 = \
        #                     np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
        #                 big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
        #                 big_stick_required_depth.append(big_stick_temp_depth1)
        #     if not big_stick_required_depth:
        #         self.mft_3D_flag = 2
        #         return big_stick_required_depth, depth_tolerance

        elif shape == "Round Flat":
            t1 = depth * settings.ROUND_FLAT_DEPTH_LOWER_RANGE
            t2 = depth * settings.ROUND_FLAT_DEPTH_UPPER_RANGE
            for value in range(int(t2), int(t1), settings.ROUND_FLAT_STEP_SIZE):
                depth_tolerance = 0.01 * value
                if settings.BOTH_STICK_LOWER_LIMIT <= depth + depth_tolerance <= settings.DEPTH_STICK_UPPER_LIMIT:
                    big_stick_depth_index1 = \
                        np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
                    big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
                    big_stick_required_depth.append(big_stick_temp_depth1)
            if not big_stick_required_depth:
                self.mft_3D_flag = 2
                return big_stick_required_depth, depth_tolerance

        elif shape == "Capsule":
            t1 = depth * settings.CAPSULE_LOWER_RANGE
            t2 = depth * settings.CAPSULE_UPPER_RANGE
            if length < 23.8 and width < 9.5:
                for value in range(int(t2), int(t1), settings.CAPSULE_STEP_SIZE):
                    depth_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT <= depth + depth_tolerance <= settings.DEPTH_STICK_UPPER_LIMIT:
                        big_stick_depth_index1 = \
                            np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
                        big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
                        big_stick_required_depth.append(big_stick_temp_depth1)
            if 23.8 <= length <= 26.2 or width > 9.5 or not big_stick_required_depth:
                self.mft_3D_flag = 2
                return big_stick_required_depth, depth_tolerance
            if length > 26.2:
                self.mft_3D_flag = 1
                return big_stick_required_depth, depth_tolerance

        elif shape == "Softgel":
            t1 = depth * settings.SOFTGEL_LOWER_RANGE
            t2 = depth * settings.SOFTGEL_UPPER_RANGE
            if length < 23.8 and width < 9.5:
                for value in range(int(t2), int(t1), settings.SOFTGEL_STEP_SIZE):
                    depth_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT <= depth + depth_tolerance <= settings.DEPTH_STICK_UPPER_LIMIT:
                        big_stick_depth_index1 = \
                            np.where(self.big_stick_depth_combinations >= (depth + depth_tolerance))[0][0]
                        big_stick_temp_depth1 = round(self.big_stick_depth_combinations[big_stick_depth_index1], 2)
                        big_stick_required_depth.append(big_stick_temp_depth1)
            if 23.8 <= length <= 26.2 or width > 9.5 or not big_stick_required_depth:
                self.mft_3D_flag = 2
                return big_stick_required_depth, depth_tolerance
            if length > 26.2:
                self.mft_3D_flag = 1
                return big_stick_required_depth, depth_tolerance

        if depth_tolerance != 0:
            depth_tolerance = depth + depth_tolerance
            depth_tolerance = round(depth_tolerance, 2)

        return big_stick_required_depth, depth_tolerance

    def measure_big_stick_width_dimension(self, width, length, shape, fillet):
        """
        This function measure the upper big stick and lower big stick for Width for every drugs

        """
        width = float(width)
        length = float(length)
        fillet = float(fillet)

        big_stick_required_width = []
        width_tolerance = 0

        if shape == "Oval":
            diagonal = math.sqrt(width ** 2 + fillet ** 2)
            diagonal1 = int(diagonal) + 0.5
            if settings.BOTH_STICK_LOWER_LIMIT <= diagonal1 <= settings.WIDTH_STICK_UPPER_LIMIT:
                big_stick_width_index1 = \
                    np.where(self.big_stick_width_combinations >= diagonal1)[0][0]
                big_stick_temp_width1 = round(self.big_stick_width_combinations[big_stick_width_index1], 2)
                if settings.BOTH_STICK_LOWER_LIMIT <= big_stick_temp_width1 <= settings.WIDTH_STICK_UPPER_LIMIT:
                    big_stick_required_width.append(big_stick_temp_width1)

            temp = diagonal - int(diagonal)
            if temp < 0.5:
                diagonal = int(diagonal)
                if settings.BOTH_STICK_LOWER_LIMIT <= diagonal <= settings.WIDTH_STICK_UPPER_LIMIT:
                    big_stick_width_index1 = \
                        np.where(self.big_stick_width_combinations >= diagonal)[0][0]
                    big_stick_temp_width1 = round(self.big_stick_width_combinations[big_stick_width_index1], 2)
                    if settings.BOTH_STICK_LOWER_LIMIT <= big_stick_temp_width1 <= settings.WIDTH_STICK_UPPER_LIMIT:
                        big_stick_required_width.append(big_stick_temp_width1)
            else:
                diagonal2 = int(diagonal) + 1
                if settings.BOTH_STICK_LOWER_LIMIT <= diagonal2 <= settings.WIDTH_STICK_UPPER_LIMIT:
                    big_stick_width_index1 = \
                        np.where(self.big_stick_width_combinations >= diagonal2)[0][0]
                    big_stick_temp_width1 = round(self.big_stick_width_combinations[big_stick_width_index1], 2)
                    if settings.BOTH_STICK_LOWER_LIMIT <= big_stick_temp_width1 <= settings.WIDTH_STICK_UPPER_LIMIT:
                        big_stick_required_width.append(big_stick_temp_width1)

            if not big_stick_required_width:
                self.mft_3D_flag = 2
                return big_stick_required_width, width_tolerance

        elif shape == "Elliptical":
            temp = (width * width) + (fillet * fillet)
            diagonal = math.sqrt(temp)
            diagonal1 = int(diagonal) + 0.5
            if settings.BOTH_STICK_LOWER_LIMIT <= diagonal1 <= settings.WIDTH_STICK_UPPER_LIMIT:
                big_stick_width_index1 = \
                    np.where(self.big_stick_width_combinations >= diagonal1)[0][0]
                big_stick_temp_width1 = round(self.big_stick_width_combinations[big_stick_width_index1], 2)
                if settings.BOTH_STICK_LOWER_LIMIT <= big_stick_temp_width1 <= settings.WIDTH_STICK_UPPER_LIMIT:
                    big_stick_required_width.append(big_stick_temp_width1)

            temp = diagonal - int(diagonal)
            if temp < 0.5:
                diagonal = int(diagonal)
                if settings.BOTH_STICK_LOWER_LIMIT <= diagonal <= settings.WIDTH_STICK_UPPER_LIMIT:
                    big_stick_width_index1 = \
                        np.where(self.big_stick_width_combinations >= diagonal)[0][0]
                    big_stick_temp_width1 = round(self.big_stick_width_combinations[big_stick_width_index1], 2)
                    if settings.BOTH_STICK_LOWER_LIMIT <= big_stick_temp_width1 <= settings.WIDTH_STICK_UPPER_LIMIT:
                        big_stick_required_width.append(big_stick_temp_width1)
            else:
                diagonal2 = int(diagonal) + 1
                if settings.BOTH_STICK_LOWER_LIMIT <= diagonal2 <= settings.WIDTH_STICK_UPPER_LIMIT:
                    big_stick_width_index1 = \
                        np.where(self.big_stick_width_combinations >= diagonal2)[0][0]
                    big_stick_temp_width1 = round(self.big_stick_width_combinations[big_stick_width_index1], 2)
                    if settings.BOTH_STICK_LOWER_LIMIT <= big_stick_temp_width1 <= settings.WIDTH_STICK_UPPER_LIMIT:
                        big_stick_required_width.append(big_stick_temp_width1)

            if not big_stick_required_width:
                self.mft_3D_flag = 2
                return big_stick_required_width, width_tolerance

        elif shape == "Round Curved":
            if width <= 7:
                for value in range(settings.ROUND_CURVED_WIDTH_RANGE_LOWER1, settings.ROUND_CURVED_WIDTH_RANGE_UPPER1,
                                   settings.ROUND_CURVED_STEP_SIZE):
                    width_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT <= width + width_tolerance <= settings.WIDTH_STICK_UPPER_LIMIT:
                        big_stick_width_index1 = \
                            np.where(self.big_stick_width_combinations >= (width + width_tolerance))[0][0]
                        big_stick_temp_width1 = round(self.big_stick_depth_combinations[big_stick_width_index1], 2)
                        big_stick_required_width.append(big_stick_temp_width1)

            else:
                for value in range(settings.ROUND_CURVED_WIDTH_RANGE_LOWER2, settings.ROUND_CURVED_WIDTH_RANGE_UPPER2,
                                   settings.ROUND_CURVED_STEP_SIZE):
                    width_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT <= width + width_tolerance <= settings.WIDTH_STICK_UPPER_LIMIT:
                        big_stick_width_index1 = \
                            np.where(self.big_stick_width_combinations >= (width + width_tolerance))[0][0]
                        big_stick_temp_width1 = round(self.big_stick_width_combinations[big_stick_width_index1], 2)
                        big_stick_required_width.append(big_stick_temp_width1)

            if not big_stick_required_width:
                self.mft_3D_flag = 2
                return big_stick_required_width, width_tolerance

        elif shape == "Round Flat":
            # t1 = width * settings.ROUND_FLAT_WIDTH_LOWER_RANGE
            # t2 = width * settings.ROUND_FLAT_WIDTH_UPPER_RANGE
            # for value in range(int(t2), int(t1), settings.ROUND_FLAT_STEP_SIZE):
            #     width_tolerance = 0.01 * value
            #     if settings.BOTH_STICK_LOWER_LIMIT < width + width_tolerance < settings.WIDTH_STICK_UPPER_LIMIT:
            #         big_stick_width_index1 = \
            #             np.where(self.big_stick_width_combinations >= (width + width_tolerance))[0][0]
            #         big_stick_temp_width1 = round(self.big_stick_width_combinations[big_stick_width_index1], 2)
            #         big_stick_required_width.append(big_stick_temp_width1)
            # if not big_stick_required_width:
            #     self.mft_3D_flag = 2
            #     return big_stick_required_width, width_tolerance

            if width < 7:
                for value in range(settings.ROUND_FLAT_WIDTH_RANGE_LOWER1, settings.ROUND_FLAT_WIDTH_RANGE_UPPER1,
                                   settings.ROUND_FLAT_STEP_SIZE2):
                    width_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT < width + width_tolerance < settings.WIDTH_STICK_UPPER_LIMIT:
                        big_stick_width_index1 = \
                            np.where(self.big_stick_width_combinations >= (width + width_tolerance))[0][0]
                        big_stick_temp_width1 = round(self.big_stick_depth_combinations[big_stick_width_index1], 2)
                        big_stick_required_width.append(big_stick_temp_width1)

            else:
                for value in range(settings.ROUND_FLAT_WIDTH_RANGE_LOWER2, settings.ROUND_FLAT_WIDTH_RANGE_UPPER2,
                                   settings.ROUND_FLAT_STEP_SIZE2):
                    width_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT < width + width_tolerance < settings.WIDTH_STICK_UPPER_LIMIT:
                        big_stick_width_index1 = \
                            np.where(self.big_stick_width_combinations >= (width + width_tolerance))[0][0]
                        big_stick_temp_width1 = round(self.big_stick_width_combinations[big_stick_width_index1], 2)
                        big_stick_required_width.append(big_stick_temp_width1)

            if not big_stick_required_width:
                self.mft_3D_flag = 2
                return big_stick_required_width, width_tolerance

        elif shape == "Capsule":
            t1 = width * settings.CAPSULE_LOWER_RANGE
            t2 = width * settings.CAPSULE_UPPER_RANGE
            if length < 23.8 and width < 9.5:
                for value in range(int(t2), int(t1), settings.CAPSULE_STEP_SIZE):
                    width_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT < width + width_tolerance < settings.WIDTH_STICK_UPPER_LIMIT:
                        big_stick_width_index1 = \
                            np.where(self.big_stick_width_combinations >= (width + width_tolerance))[0][0]
                        big_stick_temp_width1 = round(self.big_stick_width_combinations[big_stick_width_index1], 2)
                        big_stick_required_width.append(big_stick_temp_width1)
            if 23.8 <= length <= 26.2 or width > 9.5 or not big_stick_required_width:
                self.mft_3D_flag = 2
                return big_stick_required_width, width_tolerance
            if length > 26.2:
                self.mft_3D_flag = 1
                return big_stick_required_width, width_tolerance

        elif shape == "Softgel":
            t1 = width * settings.SOFTGEL_LOWER_RANGE
            t2 = width * settings.SOFTGEL_UPPER_RANGE
            if length < 23.8 and width < 9.5:
                for value in range(int(t2), int(t1), settings.SOFTGEL_STEP_SIZE):
                    width_tolerance = 0.01 * value
                    if settings.BOTH_STICK_LOWER_LIMIT < width + width_tolerance < settings.WIDTH_STICK_UPPER_LIMIT:
                        big_stick_width_index1 = \
                            np.where(self.big_stick_width_combinations >= (width + width_tolerance))[0][0]
                        big_stick_temp_width1 = round(self.big_stick_width_combinations[big_stick_width_index1], 2)
                        big_stick_required_width.append(big_stick_temp_width1)
            if 23.8 <= length <= 26.2 or width > 9.5 or not big_stick_required_width:
                self.mft_3D_flag = 2
                return big_stick_required_width, width_tolerance
            if length > 26.2:
                self.mft_3D_flag = 1
                return big_stick_required_width, width_tolerance

        if width_tolerance != 0:
            width_tolerance = width + width_tolerance
            width_tolerance = round(width_tolerance, 2)

        return big_stick_required_width, width_tolerance


    def recommend_3D_printer(self, width, depth, length, shape, fillet):
        """
        This function measure the upper big stick and lower big stick for Width for every drugs

        """
        depth = float(depth)
        width = float(width)
        length = float(length)
        fillet = float(fillet)

        if shape == "Oval":
            diagonal = math.sqrt(width ** 2 + fillet ** 2)
            diagonal1 = int(diagonal) + 0.5
            self.drum_width1_3D = diagonal1
            temp = diagonal - int(diagonal)
            if temp < 0.5:
                diagonal = int(diagonal)
                self.drum_width2_3D = diagonal
            else:
                diagonal2 = int(diagonal) + 1
                self.drum_width2_3D = diagonal2
            self.drum_depth1_3D = depth + 0.4
            self.small_stick_3D = length - 1.2
            self.drum_length_3D = min((2*length + 12), 52)
            self.depth_brush_3D = depth - 2

        elif shape == "Elliptical":
            diagonal = math.sqrt(width ** 2 + fillet ** 2)
            diagonal1 = int(diagonal) + 0.5
            self.drum_width1_3D = diagonal1
            temp = diagonal - int(diagonal)
            if temp < 0.5:
                diagonal = int(diagonal)
                self.drum_width2_3D = diagonal
            else:
                diagonal2 = int(diagonal) + 1
                self.drum_width2_3D = diagonal2
            self.drum_depth1_3D = depth + 0.4
            self.small_stick_3D = length - 1.2
            self.drum_length_3D = min((2 * length + 12), 52)
            self.depth_brush_3D = depth - 2

        elif shape == "Round Curved":
            self.drum_width1_3D = width + 1.3
            self.drum_depth1_3D = depth + 0.1
            self.depth_brush_3D = depth - 1
            self.drum_length_3D = min((1 * length + 15.5), 52)
            self.small_stick_3D = length - 1.2

        elif shape == "Round Flat":
            self.drum_width1_3D = width + 1.3
            self.drum_depth1_3D = depth + 0.1
            self.depth_brush_3D = depth - 1
            self.drum_length_3D = min((1 * length + 15.5), 52)
            self.small_stick_3D = length - 1.2

        elif shape == "Capsule":
            self.drum_width1_3D = math.ceil(width * 1.2 * 10) / 10.0
            self.drum_depth1_3D = math.ceil(width * 1.2 * 10) / 10.0
            self.depth_brush_3D = depth - 2
            self.drum_length_3D = 52
            self.small_stick_3D = math.floor((length - 1) * 10) / 10.0

        elif shape == "Softgel":
            drum_width_3D = 1.5 * max(depth, width)
            self.drum_width1_3D = math.floor(drum_width_3D * 10) / 10.0
            self.drum_width2_3D = math.ceil(drum_width_3D * 10) / 10.0
            self.drum_depth1_3D = self.drum_width1_3D
            self.drum_depth2_3D = self.drum_width2_3D
            self.depth_brush_3D = depth - 2
            self.drum_length_3D = 52
            self.small_stick_3D = math.floor((length - 1.2) * 10) / 10.0

    def recommend_big_stick(self, depth, width, length, fillet, shape):
        """
        This Function wiil give the possible big stick dimension tuple
        :param depth:
        :param width:
        :param fillet:
        :param shape:
        :return:
        """
        depth = float(depth)
        width = float(width)
        length = float(length)
        fillet = float(fillet)

        big_stick_required_depth, depth_tolerance = self \
            .measure_big_stick_depth_dimension(depth, width, length, shape, fillet)
        width_depth_possible_combination_tuple = list()
        if self.mft_3D_flag != 1 and self.mft_3D_flag != 2:
            big_stick_required_width, width_tolerance = self \
                .measure_big_stick_width_dimension(width, length, shape, fillet)

            # big_stick_required_width_min = list(set(big_stick_required_width_min))
            big_stick_required_width = list(set(big_stick_required_width))
            # big_stick_required_depth_min = list(set(big_stick_required_depth_min))
            big_stick_required_depth = list(set(big_stick_required_depth))
            big_stick_dimensions_min_max = list(product(big_stick_required_width, big_stick_required_depth))
            # big_stick_dimensions_min_max.extend(
            #     list(product(big_stick_required_width_min, big_stick_required_depth)))
            # big_stick_dimensions_min_max.extend(
            #     list(product(big_stick_required_width, big_stick_required_depth_min)))
            # big_stick_dimensions_min_max.extend(
            #     list(product(big_stick_required_width, big_stick_required_depth)))
            temp_width_depth_possible_combination_tuple = big_stick_dimensions_min_max

            if shape == "Capsule":
                for tuple in temp_width_depth_possible_combination_tuple:
                    if tuple[0] == tuple[1]:
                        width_depth_possible_combination_tuple.append(tuple)
            else:
                width_depth_possible_combination_tuple = deepcopy(temp_width_depth_possible_combination_tuple)

            if width_depth_possible_combination_tuple:
                self.mft_3D_flag = 0

        return list(unique_everseen(width_depth_possible_combination_tuple))

    def recommend_small_stick(self, length, shape, stick_tuple):
        # Calculate required small stick length
        if shape == "Elliptical":
            for tpl in stick_tuple:
                drug_required_stick_length = math.sqrt((float(length)) ** 2 - float(tpl[1]) ** 2)
                if drug_required_stick_length - math.floor(drug_required_stick_length) <= 0.7:
                    drug_required_stick_length = math.floor(drug_required_stick_length)
                else:
                    drug_required_stick_length = math.ceil(drug_required_stick_length)
                return drug_required_stick_length

        length = float(length)
        drug_required_stick_length = math.floor(length - 1)
        if drug_required_stick_length < 4 or drug_required_stick_length > 24:
            drug_required_stick_length = 0
            self.mft_3D_flag = 1
        return drug_required_stick_length

    def get_dummy_pills(self, width, depth, length, shape, fillet):

        dummy_pill_id_in_stock_list = []
        if shape == "Round Curved" or shape == "Round Flat":
            for dummy_pill_stock_tuple in self.stock_pill_dict:
                if -0.2 < (float(dummy_pill_stock_tuple[1]) - float(depth)) < 0.2 and -0.2 < (
                        float(dummy_pill_stock_tuple[2]) - float(width)) < 0.2 and math.floor(
                    float(dummy_pill_stock_tuple[3])) - 1 == self.small_stick_required_length and -0.6 < (
                        float(dummy_pill_stock_tuple[4]) - float(fillet)) < 0.6:
                    dummy_pill_id_in_stock_list.append(dummy_pill_stock_tuple[0])
        elif shape == "Capsule":
            for dummy_pill_stock_tuple in self.stock_pill_dict:
                if -0.3 < (float(dummy_pill_stock_tuple[1]) - float(depth)) < 0.3 and -0.3 < (
                        float(dummy_pill_stock_tuple[2]) - float(width)) < 0.3 and math.floor(
                    float(dummy_pill_stock_tuple[3])) - 1 == self.small_stick_required_length and -0.6 < (
                        float(dummy_pill_stock_tuple[4]) - float(fillet)) < 0.6:
                    dummy_pill_id_in_stock_list.append(dummy_pill_stock_tuple[0])
        elif shape == "Oval":
            for dummy_pill_stock_tuple in self.stock_pill_dict:
                if abs(width - depth) > 1.2:
                    if -0.1 < (float(dummy_pill_stock_tuple[1]) - float(depth)) < 0.2 and -0.25 < (
                            float(dummy_pill_stock_tuple[2]) - float(width)) < 0 and math.floor(
                        float(dummy_pill_stock_tuple[3])) - 1 == self.small_stick_required_length and -0.6 < (
                            float(dummy_pill_stock_tuple[4]) - float(fillet)) < 0.6 and dummy_pill_stock_tuple[5] == \
                            'Oval' and abs(float(dummy_pill_stock_tuple[2]) - float(dummy_pill_stock_tuple[1])) > 1.2:
                        dummy_pill_id_in_stock_list.append(dummy_pill_stock_tuple[0])
                else:
                    if -0.1 < (float(dummy_pill_stock_tuple[1]) - float(depth)) < 0.2 and -0.25 < (
                            float(dummy_pill_stock_tuple[2]) - float(width)) < 0 and math.floor(
                        float(dummy_pill_stock_tuple[3])) - 1 == self.small_stick_required_length and -0.6 < (
                            float(dummy_pill_stock_tuple[4]) - float(fillet)) < 0.6 and dummy_pill_stock_tuple[
                        5] == 'Oval' and abs(float(dummy_pill_stock_tuple[2]) - float(dummy_pill_stock_tuple[1])) <= \
                            1.2:
                        dummy_pill_id_in_stock_list.append(dummy_pill_stock_tuple[0])
        elif shape == "Elliptical":
            for dummy_pill_stock_tuple in self.stock_pill_dict:
                if abs(width - depth) < 1.15:
                    if (float(dummy_pill_stock_tuple[1]) - float(depth)) > -0.15 and (
                            float(dummy_pill_stock_tuple[1]) - float(depth)) < 0.15 and -0.2 < (
                            float(dummy_pill_stock_tuple[2]) - float(width)) < 0.1 and math.floor(
                        float(dummy_pill_stock_tuple[3])) - 1 == self.small_stick_required_length and \
                            dummy_pill_stock_tuple[5] == 'Elliptical' and abs(float(dummy_pill_stock_tuple[2]) -
                                                                              float(dummy_pill_stock_tuple[1])) < 1.15:
                        dummy_pill_id_in_stock_list.append(dummy_pill_stock_tuple[0])
                else:
                    if -0.15 < (float(dummy_pill_stock_tuple[1]) - float(depth)) < 0.15 and -0.2 < (
                            float(dummy_pill_stock_tuple[2]) - float(width)) < 0.1 and math.floor(
                        float(dummy_pill_stock_tuple[3])) - 1 == self.small_stick_required_length and \
                            dummy_pill_stock_tuple[5] == 'Elliptical' and abs(float(dummy_pill_stock_tuple[2]) -
                                                                              float(dummy_pill_stock_tuple[1])) >= 1.15:
                        dummy_pill_id_in_stock_list.append(dummy_pill_stock_tuple[0])
        return dummy_pill_id_in_stock_list

    def make_required_data_dict(self, width, depth, length, shape, fillet, strength_value, strength,
                                big_stick_width_depth_possible_combination_tuple, drug, priority,
                                drug_name, drug_count, pack_count):  # priority

        available_big_stick_id_list = []
        big_stick_mold_in_inventory_list = []
        all_big_stick_mold_list = []
        mold_not_available_list = []
        alternate_available_dimensions = []
        alternate_available_big_stick_id_list = []
        alternate_available_mold_id_list = []
        alternate_available_all_mold_id_list = []
        big_stick_sent_list = []
        alternate_available_big_stick_sent_id_list = []
        width = float(width)
        depth = float(depth)
        length = float(length)

        count = 0
        big_stick_width_depth_possible_combination_tuple1 = []
        big_stick_width_depth_possible_combination_tuple_updated = []

        if shape == "Capsule":
            big_stick_width_depth_possible_combination_tuple_copy = []
            for i in big_stick_width_depth_possible_combination_tuple:
                if i[0] in [8.0] and i[1] in [8.0]:
                    x = 8.2
                    y = 8.2
                    big_stick_width_depth_possible_combination_tuple_copy.append((x, y))
                elif i[0] in [7.0] and i[1] in [7.0]:
                    x = 7.2
                    y = 7.2
                    big_stick_width_depth_possible_combination_tuple_copy.append((x, y))
            if len(big_stick_width_depth_possible_combination_tuple_copy) > 0:
                big_stick_width_depth_possible_combination_tuple.extend(
                    big_stick_width_depth_possible_combination_tuple_copy)
                big_stick_width_depth_possible_combination_tuple = list(
                    set(big_stick_width_depth_possible_combination_tuple))

        for i in big_stick_width_depth_possible_combination_tuple:
            if int(i[0]) == 12:
                x1, x2 = i
                i = (11.9, x2)
                big_stick_width_depth_possible_combination_tuple.append(i)
            big_stick_width_depth_possible_combination_tuple1.append(str(i[0]) + "x" + str(i[1]))
        for tuple in big_stick_width_depth_possible_combination_tuple:
            tuple = (str(tuple[0]), str(tuple[1]))
            tpl_list = list(tuple)
            lst = tpl_list[0].split('.')
            lst1 = tpl_list[1].split('.')
            if len(lst) > 1:
                if int(lst[1]) == 0:
                    tpl_list[0] = lst[0]
            if len(lst1) > 1:
                if int(lst1[1]) == 0:
                    tpl_list[1] = lst1[0]
            tuple = builtins.tuple(tpl_list)
            big_stick_width_depth_possible_combination_tuple_updated.append(tuple)

            if tuple in self.big_stick_dimension_tuple_id_mapping.keys():
                available_big_stick_id_list.append({tuple, self.big_stick_dimension_tuple_id_mapping[tuple]})
                count += 1
            if tuple in self.all_big_stick_dimension_tuple_mold_id_mapping.keys():
                all_big_stick_mold_list.append({tuple,self.all_big_stick_dimension_tuple_mold_id_mapping[tuple]})
                # all_big_stick_mold_list.append(self.all_big_stick_dimension_tuple_mold_id_mapping[tuple])
        """
        Find perfect tolerance dimension big stick ids only for round curved shape
        """
        # if shape == "Round Curved":
        #     alternate_width_min = width + 0.7
        #     alternate_depth_min = depth + 0.7
        #     if width < 6:
        #         alternate_width_max = width + 1.5
        #     else:
        #         alternate_width_max = width + 2
        #
        #     if depth < 6:
        #         alternate_depth_max = depth + 1.25
        #     else:
        #         alternate_depth_max = depth + 1.5
        #
        #     for tuple, id in self.big_stick_dimension_tuple_id_mapping.items():
        #         if alternate_width_min < float(tuple[0]) < alternate_width_max:
        #             if alternate_depth_min < float(tuple[1]) < alternate_depth_max:
        #                 alternate_available_dimensions.append(tuple)
        #                 alternate_available_big_stick_id_list.append(self.big_stick_dimension_tuple_id_mapping[tuple])
        #                 self.mft_3D_flag = 0
        #
        #     for tuple, id in self.all_big_stick_dimension_tuple_mold_id_mapping.items():
        #         if alternate_width_min < float(tuple[0]) < alternate_width_max:
        #             if alternate_depth_min < float(tuple[1]) < alternate_depth_max:
        #                 alternate_available_dimensions.append(tuple)
        #                 alternate_available_all_mold_id_list.append(
        #                     self.all_big_stick_dimension_tuple_mold_id_mapping[tuple])
        #
        #     for i in alternate_available_dimensions:
        #         big_stick_width_depth_possible_combination_tuple1.append(str(i[0]) + 'x' + str(i[1]))

        dummy_pill_id_in_stock_list = self.get_dummy_pills(width, depth, length, shape, fillet)

        ratio = float(fillet) / float(depth)

        # for i in available_big_stick_id_list:
        #     if "available_big_stick_inventory" not in self.dct:
        #         self.dct["available_big_stick_inventory"] = {}
        #     if i not in self.dct["available_big_stick_inventory"]:
        #         self.dct["available_big_stick_inventory"][i] = 0
        #     self.dct["available_big_stick_inventory"][i] += 1
        #
        # for i in big_stick_mold_in_inventory_list:
        #     if "mold_in_inventory_list" not in self.dct:
        #         self.dct["mold_in_inventory_list"] = {}
        #     if i not in self.dct["mold_in_inventory_list"]:
        #         self.dct["mold_in_inventory_list"][i] = 0
        #     self.dct["mold_in_inventory_list"][i] += 1
        #
        # for i in all_big_stick_mold_list:
        #     if "all_big_stick_mold_list" not in self.dct:
        #         self.dct["all_big_stick_mold_list"] = {}
        #     if i not in self.dct["all_big_stick_mold_list"]:
        #         self.dct["all_big_stick_mold_list"][i] = 0
        #     self.dct["all_big_stick_mold_list"][i] += 1
        #
        # for i in big_stick_sent_list:
        #     if "big_stick_sent_list" not in self.dct:
        #         self.dct["big_stick_sent_list"] = {}
        #     if i not in self.dct["big_stick_sent_list"]:
        #         self.dct["big_stick_sent_list"][i] = 0
        #     self.dct["big_stick_sent_list"][i] += 1
        #
        # for i in mold_not_available_list:
        #     if "mold_not_available_list" not in self.dct:
        #         self.dct["mold_not_available_list"] = {}
        #     if i not in self.dct["mold_not_available_list"]:
        #         self.dct["mold_not_available_list"][i] = 0
        #     self.dct["mold_not_available_list"][i] += 1
        #
        # for i in alternate_available_big_stick_id_list:
        #     if "alternate_available_big_stick_id_list" not in self.dct:
        #         self.dct["alternate_available_big_stick_id_list"] = {}
        #     if i not in self.dct["alternate_available_big_stick_id_list"]:
        #         self.dct["alternate_available_big_stick_id_list"][i] = 0
        #     self.dct["alternate_available_big_stick_id_list"][i] += 1
        #
        # for i in alternate_available_mold_id_list:
        #     if "alternate_available_mold_id_list" not in self.dct:
        #         self.dct["alternate_available_mold_id_list"] = {}
        #     if i not in self.dct["alternate_available_mold_id_list"]:
        #         self.dct["alternate_available_mold_id_list"][i] = 0
        #     self.dct["alternate_available_mold_id_list"][i] += 1
        #
        # for i in alternate_available_all_mold_id_list:
        #     if "alternate_available_all_mold_id_list" not in self.dct:
        #         self.dct["alternate_available_all_mold_id_list"] = {}
        #     if i not in self.dct["alternate_available_all_mold_id_list"]:
        #         self.dct["alternate_available_all_mold_id_list"][i] = 0
        #     self.dct["alternate_available_all_mold_id_list"][i] += 1
        #
        # for i in alternate_available_big_stick_sent_id_list:
        #     if "alternate_available_big_stick_sent_id_list" not in self.dct:
        #         self.dct["alternate_available_big_stick_sent_id_list"] = {}
        #     if i not in self.dct["alternate_available_big_stick_sent_id_list"]:
        #         self.dct["alternate_available_big_stick_sent_id_list"][i] = 0
        #     self.dct["alternate_available_big_stick_sent_id_list"][i] += 1

        if width >= 12 or depth >= 12:
            self.mft_3D_flag = 2

        # available_big_stick_inventory = list(
        #     set(available_big_stick_id_list + alternate_available_big_stick_id_list))
        available_big_stick_inventory = list(available_big_stick_id_list)
        # if not available_big_stick_inventory:
        #     big_stick_width_depth_possible_combination_tuple1 = {}
            # self.mft_3D_flag =

        if self.mft_3D_flag != 2:
            self.drum_width1_3D = 0
            self.drum_width2_3D = 0
            self.drum_depth1_3D = 0
            self.drum_depth2_3D = 0
            self.small_stick_3D = 0
            self.drum_length_3D = 0
            self.depth_brush_3D = 0

        global_data = {"NDC##TXR": drug, "Width": width, "Depth": depth, "Length": length,
                       "Strength Value": strength_value, "Strength": strength, "Drug Name": drug_name,
                       "Custom Shape": shape, "Fillet": fillet, "Ratio": ratio, "Priority": priority,
                       "Big Stick": set(big_stick_width_depth_possible_combination_tuple1),
                       "available_big_stick_inventory": available_big_stick_id_list,
                       "available_mold_id_list": all_big_stick_mold_list,
                       "Dummy Pill ID": dummy_pill_id_in_stock_list, "Small Stick": self.small_stick_required_length,
                       "mft": self.mft_3D_flag, "drum_width1_3D": self.drum_width1_3D,
                       "drum_width2_3D": self.drum_width2_3D, "drum_depth1_3D": self.drum_depth1_3D,
                       "drum_depth2_3D": self.drum_depth2_3D,"small_stick_3D": self.small_stick_3D,
                       "drum_length_3D": self.drum_length_3D, "depth_brush_3D": self.depth_brush_3D,
                       "drug_count": drug_count, "pack_count": pack_count}

        return global_data

    def recommend_stick_dimensions(self, drugndc_dimensions_dict):
        """
         Big and small stick width combination
        """
        logger.info("in recommend stick dimensions")
        logger.info("2")
        required_data = list()
        count = 0
        for drug, dimensions in drugndc_dimensions_dict.items():
            count += 1
            # pill_shape = "Round Flat"
            # pill_width = 6.48
            # pill_depth = 2.72
            # pill_length = 6.48
            # pill_fillet = 2

            pill_length = float(dimensions["length"])
            pill_depth = float(dimensions["depth"])
            pill_width = float(dimensions["width"])
            pill_fillet = float(dimensions["fillet"])
            pill_length = math.ceil(pill_length * 10) / 10.0
            pill_depth = math.ceil(pill_depth * 10) / 10.0
            pill_width = math.ceil(pill_width * 10) / 10.0
            pill_fillet = math.ceil(pill_fillet * 10) / 10.0
            pill_shape = dimensions["shape"]
            pill_name = dimensions["drug_name"]
            strength_value = dimensions["strength_value"]
            strength = dimensions["strength"]
            priority = dimensions["priority"]
            drug_count = dimensions["drug_count"]
            pack_count = dimensions["pack_count"]

            self.mft_3D_flag = 0

            # if pill_width < 2.5 or pill_depth < 2.25:
            # TODO: Decide whether mft drugs should recommend or not.
            # print("P")
            if not (4.5 < float(pill_length) < 26.2):
                self.mft_3D_flag = 1
            if 23.8 < float(pill_length) < 26.2 or float(pill_depth) < 2.25 or float(pill_width) < 2.8:
                self.mft_3D_flag = 2

            if drug == '654987321##274':
                print("P")
            print(drug)

            if self.mft_3D_flag != 1 or self.mft_3D_flag != 2:
                big_stick_width_depth_possible_combination_tuple = self.recommend_big_stick(pill_depth, pill_width,
                                                                                            pill_length, pill_fillet,
                                                                                            pill_shape)
            else:
                big_stick_width_depth_possible_combination_tuple = []

            big_stick_width_depth_possible_combination_tuple_copy = big_stick_width_depth_possible_combination_tuple.copy()

            for item in big_stick_width_depth_possible_combination_tuple_copy:
                if item[0] < pill_width:
                    big_stick_width_depth_possible_combination_tuple.remove(item)


            if self.mft_3D_flag != 1 or self.mft_3D_flag != 2:
                self.small_stick_required_length = self.recommend_small_stick(pill_length, pill_shape,
                                                                              big_stick_width_depth_possible_combination_tuple)

            if not self.small_stick_required_length:
                big_stick_width_depth_possible_combination_tuple = []

            if self.mft_3D_flag == 2:
                self.recommend_3D_printer(pill_width, pill_depth, pill_length, pill_shape, pill_fillet)

            required_data_dict = self.make_required_data_dict(pill_width, pill_depth, pill_length, pill_shape,
                                                              pill_fillet, strength_value, strength,
                                                              big_stick_width_depth_possible_combination_tuple,
                                                              drug, priority, pill_name, drug_count, pack_count)  # priority
            required_data.append(required_data_dict)
        return required_data
