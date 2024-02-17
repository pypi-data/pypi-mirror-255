rows = 'ABCDEFGHIJ'
container_dict = {}
container_list = []
location_list = []
location_dict = {}
location_number = 0
container_id = 498
serial_number = 'CRD00'
serial_count = 0
BIG_TYPE = 1
SLOW_USAGE = 4
FAST_USAGE = 3
MEDIUM_FAST_USAGE = 5
MEDIUM_SLOW_USAGE = 6
SMALL_TYPE = 2
for r in rows:
    if r == 'A' or r == 'B':
        for c in range(1, 27):
            if 9 <= c <= 18:
                container_dict['drawer_number'] = r + str(c)
                container_dict['drawer_type'] = BIG_TYPE
                container_dict['drawer_usage'] = FAST_USAGE
                #      if len(str(serial_count))==1:
                #      	serial_count+=1
                # container_dict['serial_number'] = serial_number + '00' + str(serial_count)
                #   if len(str(serial_count))==2:
                #   	container_dict['serial_number'] = serial_number + '0' + str(serial_count)
                #   	serial_count+=1
                #   if len(str(serial_count))==3:
                #   	container_dict['serial_number'] = serial_number + str(serial_count)
                #   	serial_count+=1

                container_list.append(container_dict.copy())

                for i in range(1, 21):
                    location_dict['location_number'] = location_number + 1
                    location_number += 1
                    location_dict['display_location'] = r + str(c) + '-' + str(i)
                    location_dict['container_id'] = container_id + 1
                    container_id += 1
                    location_list.append(location_dict.copy())
            else:
                container_dict['drawer_number'] = r + str(c)
                container_dict['drawer_type'] = BIG_TYPE
                container_dict['drawer_usage'] = MEDIUM_FAST_USAGE
                #      if len(str(serial_count))==1:
                # container_dict['serial_number'] = serial_number + '00' + str(serial_count)
                # serial_count+=1
                #   elif len(str(serial_count))==2:
                #   	container_dict['serial_number'] = serial_number + '0' + str(serial_count)
                #   	serial_count+=1
                #   else:
                #   	container_dict['serial_number'] = serial_number + str(serial_count)
                #   	serial_count+=1
                container_list.append(container_dict.copy())

                for i in range(1, 21):
                    location_dict['location_number'] = location_number + 1
                    location_number += 1
                    location_dict['display_location'] = r + str(c) + '-' + str(i)
                    location_dict['container_id'] = container_id + 1
                    container_id += 1
                    location_list.append(location_dict.copy())

    if r == 'C' or r == 'D' or r == 'E':
        for c in range(1, 27):
            if 9 <= c <= 18:
                container_dict['drawer_number'] = r + str(c)
                container_dict['drawer_type'] = SMALL_TYPE
                container_dict['drawer_usage'] = FAST_USAGE
                #      if len(str(serial_count))==1:
                # container_dict['serial_number'] = serial_number + '00' + str(serial_count)
                # serial_count+=1
                #   elif len(str(serial_count))==2:
                #   	container_dict['serial_number'] = serial_number + '0' + str(serial_count)
                #   	serial_count+=1
                #   else:
                #   	container_dict['serial_number'] = serial_number + str(serial_count)
                #   	serial_count+=1
                container_list.append(container_dict.copy())
                for i in range(1, 21):
                    location_dict['location_number'] = location_number + 1
                    location_number += 1
                    location_dict['display_location'] = r + str(c) + '-' + str(i)
                    location_dict['container_id'] = container_id + 1
                    container_id += 1
                    location_list.append(location_dict.copy())
            else:
                container_dict['drawer_number'] = r + str(c)
                container_dict['drawer_type'] = SMALL_TYPE
                container_dict['drawer_usage'] = MEDIUM_FAST_USAGE
                #      if len(str(serial_count))==1:
                # container_dict['serial_number'] = serial_number + '00' + str(serial_count)
                # serial_count+=1
                #   elif len(str(serial_count))==2:
                #   	container_dict['serial_number'] = serial_number + '0' + str(serial_count)
                #   	serial_count+=1
                #   else:
                #   	container_dict['serial_number'] = serial_number + str(serial_count)
                #   	serial_count+=1
                container_list.append(container_dict.copy())
                for i in range(1, 21):
                    location_dict['location_number'] = location_number + 1
                    location_number += 1
                    location_dict['display_location'] = r + str(c) + '-' + str(i)
                    location_dict['container_id'] = container_id + 1
                    container_id += 1
                    location_list.append(location_dict.copy())

    if r == 'F':
        for c in range(1, 27):
            if 9 <= c <= 18:
                container_dict['drawer_number'] = r + str(c)
                container_dict['drawer_type'] = SMALL_TYPE
                container_dict['drawer_usage'] = FAST_USAGE
                #      if len(str(serial_count))==1:
                # container_dict['serial_number'] = serial_number + '00' + str(serial_count)
                # serial_count+=1
                #   elif len(str(serial_count))==2:
                #   	container_dict['serial_number'] = serial_number + '0' + str(serial_count)
                #   	serial_count+=1
                #   else:
                #   	container_dict['serial_number'] = serial_number + str(serial_count)
                #   	serial_count+=1
                container_list.append(container_dict.copy())
                for i in range(1, 21):
                    location_dict['location_number'] = location_number + 1
                    location_number += 1
                    location_dict['display_location'] = r + str(c) + '-' + str(i)
                    location_dict['container_id'] = container_id + 1
                    container_id += 1
                    location_list.append(location_dict.copy())
            else:
                container_dict['drawer_number'] = r + str(c)
                container_dict['drawer_type'] = SMALL_TYPE
                container_dict['drawer_usage'] = MEDIUM_SLOW_USAGE
                #      if len(str(serial_count))==1:
                # container_dict['serial_number'] = serial_number + '00' + str(serial_count)
                # serial_count+=1
                #   elif len(str(serial_count))==2:
                #   	container_dict['serial_number'] = serial_number + '0' + str(serial_count)
                #   	serial_count+=1
                #   else:
                #   	container_dict['serial_number'] = serial_number + str(serial_count)
                #   	serial_count+=1
                container_list.append(container_dict.copy())
                for i in range(1, 21):
                    location_dict['location_number'] = location_number + 1
                    location_number += 1
                    location_dict['display_location'] = r + str(c) + '-' + str(i)
                    location_dict['container_id'] = container_id + 1
                    container_id += 1
                    location_list.append(location_dict.copy())
    if r == 'G':
        for c in range(1, 27):
            container_dict['drawer_number'] = r + str(c)
            container_dict['drawer_type'] = SMALL_TYPE
            container_dict['drawer_usage'] = MEDIUM_SLOW_USAGE
            #  if len(str(serial_count))==1:
            # container_dict['serial_number'] = serial_number + '00' + str(serial_count)
            # serial_count+=1
            #  elif len(str(serial_count))==2:
            #  	container_dict['serial_number'] = serial_number + '0' + str(serial_count)
            #  	serial_count+=1
            #  else:
            #  	container_dict['serial_number'] = serial_number + str(serial_count)
            #  	serial_count+=1
            container_list.append(container_dict.copy())
            for i in range(1, 21):
                location_dict['location_number'] = location_number + 1
                location_number += 1
                location_dict['display_location'] = r + str(c) + '-' + str(i)
                location_dict['container_id'] = container_id + 1
                container_id += 1
                location_list.append(location_dict.copy())
    if r == 'H' or r == 'I' or r == 'J':
        for c in range(1, 27):
            container_dict['drawer_number'] = r + str(c)
            container_dict['drawer_type'] = SMALL_TYPE
            container_dict['drawer_usage'] = SLOW_USAGE
            #  if len(str(serial_count))==1:
            # container_dict['serial_number'] = serial_number + '00' + str(serial_count)
            # serial_count+=1
            #  elif len(str(serial_count))==2:
            #  	container_dict['serial_number'] = serial_number + '0' + str(serial_count)
            #  	serial_count+=1
            #  else:
            #  	container_dict['serial_number'] = serial_number + str(serial_count)
            #   	serial_count+=1
            container_list.append(container_dict.copy())
            for i in range(1, 21):
                location_dict['location_number'] = location_number + 1
                location_number += 1
                location_dict['display_location'] = r + str(c) + '-' + str(i)
                location_dict['container_id'] = container_id + 1
                container_id += 1
                location_list.append(location_dict.copy())

# print(container_list)
# print(location_list)

# for data in container_list:
# 	for i in range(1,261):
# 		if len(str(i))==1:
# 			data['serial_number'] = serial_number+ '00' + str(i)
# 		if len(str(i))==2:
# 			data['serial_number'] = serial_number+ '0' + str(i)
# 		if len(str(i))==3:
# 			data['serial_number'] = serial_number+ str(i)

# # print(container_list)
li = []
for i in range(1, 261):
    if len(str(i)) == 1:
        li.append(serial_number + '00' + str(i))
    if len(str(i)) == 2:
        li.append(serial_number + '0' + str(i))
    if len(str(i)) == 3:
        li.append(serial_number + str(i))

# for data in container_list:
# 	for i in li:
# 		data['serial_number'] = i
# print(container_list)

for each_data in container_list:
    each_data['serial_number'] = li.pop(0)

# for i,j in zip(container_list,li):
# 	container_list[i]['serial_number'] = li[j]


print(container_list)