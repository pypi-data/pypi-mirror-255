from dosepack.base_model.base_model import db
from migrations.check_integrity import compare_packs, compare_total_packs
import random


def start_tests(old_database, new_database, sample_size=100):
    """
        Randomly sample sample size packs randomly from the total packs present and
        check the integrity of those packs after they are migrated.
    """
    db.init(old_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    packs = []
    cursor = db.execute_sql('select pack_id from pack_header')
    for row in cursor.fetchall():
        packs.append(int(row[0]))

    sampled_packs = random.sample(packs, sample_size)
    success_tests = 0
    failure_tests = 0
    failure_pack_ids = []

    if not compare_total_packs(old_database, new_database):
        failure_tests += 1
    else:
        success_tests += 1

    for pack_id in sampled_packs:
        if compare_packs(old_database, new_database, pack_id):
            success_tests += 1
        else:
            failure_tests += 1
            failure_pack_ids.append(pack_id)

    print("Total Tests Run: ", success_tests + failure_tests)
    print("Total Tests Successful: ", success_tests)
    print("Total Tests Failure: ", failure_tests, failure_pack_ids)



