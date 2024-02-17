#
# def temp_test():
#     pack_quadrant_canister_dict = {1: {1: 1, 2: 1, 3: 1, 4: 1},
#                                2: {1: 2, 2: 2, 3: 0, 4: 0},
#                                3: {1: 3, 2: 3, 3: 3, 4: 3},
#                                4: {1: 3, 2: 3, 3: 3, 4: 3},
#                                5: {1: 2, 2: 2, 3: 2, 4: 2},
#                                6: {1: 0, 2: 0, 3: 3, 4: 3},
#                                7: {1: 2, 2: 2, 3: 2, 4: 2},
#                                8: {1: 1, 2: 1, 3: 1, 4: 1},
#                                9: {1: 3, 2: 0, 3: 0, 4: 3},
#                                10: {1: 2, 2: 2, 3: 2, 4: 2},
#                                11: {1: 0, 2: 3, 3: 0, 4: 3},
#                                12: {1: 2, 2: 2, 3: 2, 4: 2}}
#
#     pack_device_dict = {1: 1,
#                         2: 1,
#                         3: 1,
#                         4: 1,
#                         5: 1,
#                         6: 1,
#                         7: 1,
#                         8: 1,
#                         9: 1,
#                         10: 1,
#                         11: 1,
#                         12: 1
#                         }
#
#     canister_pack_dict = dict()
#     pack_order_no_date_dict = {1: {"order_no": 1, "delivery_date": '2020-11-10'},
#                                2: {"order_no": 2, "delivery_date": '2020-11-10'},
#                                3: {"order_no": 3, "delivery_date": '2020-11-10'},
#                                4: {"order_no": 4, "delivery_date": '2020-11-12'},
#                                5: {"order_no": 5, "delivery_date": '2020-11-12'},
#                                6: {"order_no": 6, "delivery_date": '2020-11-12'},
#                                7: {"order_no": 7, "delivery_date": '2020-11-12'},
#                                8: {"order_no": 8, "delivery_date": '2020-11-13'},
#                                9: {"order_no": 9, "delivery_date": '2020-11-13'},
#                                10: {"order_no": 10, "delivery_date": '2020-11-13'},
#                                11: {"order_no": 11, "delivery_date": '2020-11-13'},
#                                12: {"order_no": 12, "delivery_date": '2020-11-14'},
#                                }
#
#     pack_ids = list(pack_order_no_date_dict.keys())
#     per_quad_capacity = 8
#     temp_trolley_list = [i for i in range(1, len(pack_ids) + 1)]
#     trolley_mini_batch = dict()
#     mini_batch_pack_list = dict()
#     device_trolley_date_dict = dict()
#     pack_travelled_dict = {1: False,
#                            2: False,
#                            3: False,
#                            4: False,
#                            5: False,
#                            6: False,
#                            7: False,
#                            8: False,
#                            9: False,
#                            10: False,
#                            11: False,
#                            12: False
#                            }
#
#     for pack in pack_ids:
#         pack_delivery_date = list()
#         if not pack_travelled_dict[pack]:
#             trolley_id = temp_trolley_list[0]
#             device = pack_device_dict[pack]
#
#             if device not in trolley_mini_batch.keys():
#                 trolley_mini_batch[device] = dict()
#
#             if trolley_id not in trolley_mini_batch[device].keys():
#                 trolley_mini_batch[device][trolley_id] = {1: 0, 2: 0, 3: 0, 4: 0}
#                 mini_batch_pack_list[device][trolley_id] = list()
#                 device_trolley_date_dict[device][trolley_id] = list()
#
#             similar_packs = get_same_canister_packs(pack_quadrant_canister_dict, canister_pack_dict, {pack})
#             quad_canister, quad_canister_length = get_merged_quad_canister_data(similar_packs, pack_quadrant_canister_dict)
#
#             for pack in similar_packs:
#                 pack_delivery_date.append(pack_order_no_date_dict[pack]["delivery_date"])
#
#             existing_quad_can = tuple(quad_canister_length.values())
#
#             for each_trolley, quad_can_used in trolley_mini_batch[device].items():
#                 current_trolley_can = tuple(trolley_mini_batch[device][each_trolley].values())
#                 sum_of_current_and_existing = tuple(map(sum,zip(current_trolley_can, existing_quad_can)))
#
#                 if any(i > per_quad_capacity for i in sum_of_current_and_existing):
#                     continue
#
#                 else:
#                     max_delivery_date = device_trolley_date_dict[device][each_trolley]
#                     min_delivery_date = device_trolley_date_dict[device][each_trolley]
#                     if pack_delivery_date in range(min_delivery_date, max_delivery_date):
#                         quad1, quad2, quad3, quad4 = sum_of_current_and_existing
#                         trolley_mini_batch[device][each_trolley] = {1: quad1, 2: quad2, 3: quad3, 4: quad4}
#                         for each_pack in similar_packs:
#                             pack_travelled_dict[each_pack] = True
#                         mini_batch_pack_list[device][each_trolley].update(similar_packs)
#                         device_trolley_date_dict[device][each_trolley].update(pack_delivery_date)
#                         break
#
#                     else:
#                         continue
#
#             if not pack_travelled_dict[pack]:
#                 new_trolley = temp_trolley_list[1]
#                 temp_trolley_list.pop(0)
#                 quad1, quad2, quad3, quad4 = existing_quad_can
#                 trolley_mini_batch[device][new_trolley] = {1: quad1, 2: quad2, 3: quad3, 4: quad4}
#                 for each_pack in similar_packs:
#                     pack_travelled_dict[each_pack] = True
#                 mini_batch_pack_list[device][new_trolley].update(similar_packs)
#                 device_trolley_date_dict[device][new_trolley].update(pack_delivery_date)
#
#
# def get_merged_quad_canister_data(similar_packs, pack_quadrant_canister_dict):
#     """
#
#     @param similar_packs:
#     @param pack_quadrant_canister_dict:
#     @return:
#     """
#     quad_canister = dict()
#     quad_canister_length = dict()
#     for pack in similar_packs:
#         temp_quad_canister = pack_quadrant_canister_dict[pack]
#         for quad, canister_set in temp_quad_canister.items():
#             if quad not in quad_canister:
#                 quad_canister[quad] = set()
#                 quad_canister_length[quad] = 0
#             quad_canister[quad].update(canister_set)
#             quad_canister_length[quad] += len(canister_set)
#
#     return quad_canister, quad_canister_length
#
#
# def get_same_canister_packs(pack_quadrant_canister_dict, canister_pack_dict, pack):
#     """
#
#     @param canister_pack_dict:
#     @return:
#     """
#     try:
#         canister_list = list()
#         for each_pack in pack:
#             canister_list.extend(list(pack_quadrant_canister_dict[each_pack].values()))
#         packs = set()
#         for canister_set in canister_list:
#             for canister in canister_set:
#                 packs.update(canister_pack_dict[canister])
#
#         if len(packs) > len(pack):
#             return get_same_canister_packs(pack_quadrant_canister_dict, canister_pack_dict, packs)
#         else:
#             return packs
#
#     except Exception as e:
#         return e
#
#
#
#
#

string = "((((("
opening = "("
closing = ")"
count = 0
list = string.replace(")(", ") (")
list = list.split(" ")
for i in list:
    count_o = 0
    count_c = 0
    for e_s in i:
        if e_s == opening:
            count_o += 1
        else:
            count_c += 1
    req = abs(count_o - count_c)
    count += req
print(count)

# -------------------------------------------------------------

string = ")))((()"
opening = "("
closing = ")"

o_list = list()
c_list = list()

for i in string:
    if i == opening:
        o_list.append(i)
    if i == closing:
        if len(o_list):
            o_list.remove(opening)
        else:
            c_list.append(i)

print(len(o_list) + len(c_list))








