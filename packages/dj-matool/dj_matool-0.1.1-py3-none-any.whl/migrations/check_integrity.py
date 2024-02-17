from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_details import PackDetails
from src.model.model_patient_master import PatientMaster
from src.model.model_facility_master import FacilityMaster
from src.model.model_file_header import FileHeader
from dosepack.base_model.base_model import db
from src.model.model_drug_master import DrugMaster
from src.model.model_pack_grid import PackGrid
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_patient_rx import PatientRx


def compare_packs(old_database, new_database, pack_id):
    """
        Get the total number of packs present in new database generated
    """
    old_drug_name_set, old_ndc_set, old_rx_no_set, old_drug_dict, old_pack_data, invalid = get_current_pack_data(old_database, pack_id)
    new_drug_name_set, new_ndc_set, new_rx_no_set, new_drug_dict = get_inserted_pack_data(new_database, pack_id)

    if invalid:
        return True

    # print("sorted ndc old", sorted(old_ndc_set))
    # print("sorted ndc new", sorted(new_ndc_set))
    # print("sorted rx old", sorted(old_rx_no_set))
    # print("sorted rx new", sorted(new_rx_no_set))

    if sorted(old_ndc_set) == sorted(new_ndc_set) and sorted(old_rx_no_set) == sorted(new_rx_no_set):
        return True
    else:
        return False


def compare_total_packs(old_database, new_database):
    total_inserted_packs = get_total_packs_generated(new_database)
    total_packs_present = total_packs(old_database)

    return total_inserted_packs == total_packs_present


def total_packs(database):
    """
        Get the total number of packs present in the current database.
    """
    db.init(database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    total_packs_present = 0
    cursor = db.execute_sql('select count(1) from pack_header')
    for row in cursor.fetchall():
        total_packs_present = int(row[0])

    return total_packs_present


def get_current_pack_data(old_database, pack_id):
    """
        Get the pack and slot details for the given pack_id from the current database running.
    """
    db.init(old_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    old_pack_data = []
    old_ndc_set = set()
    old_rx_no_set = set()
    old_drug_name_set = set()
    old_drug_dict = {}
    total_packs_old = 0
    cursor = db.execute_sql('select pack_id, pack_display_id, pack_header.robot_id_id, rfid, pack_no, '
                            'pack_plate_location, filecheck_id, slot_id, canister_number,drug_name, ndc, '
                            'admin_date, admin_time, slot_row, slot_column, rx_no, drug_sig, quantity, '
                            'filename, lastname, firstname, patient_checked_id, allergy, dob, facility_name, '
                            'pack_header.created_date, pack_status from pack_header  '
                            'join slot_details on pack_header.pack_id = slot_details.pack_id_id '
                            'join file_header on file_header.file_id = pack_header.file_id_id '
                            'join patient_master on patient_master.patient_id = pack_header.patient_id_id '
                            'join facility_master on facility_master.facility_id = pack_header.facility_id_id '
                            'where pack_id =' + str(pack_id))

    invalid = False
    for row in cursor.fetchall():
        total_packs_old += 1
        pack_id = row[0]
        pack_display_id = row[1]
        robot_id = row[2]
        rfid = row[3]
        pack_no = row[4]
        pack_plate_location = row[5]
        fill_id = row[6]
        drug_name = row[9]
        ndc = row[10]
        admin_date = row[11]
        admin_time = row[12]
        slot_row = row[13]
        slot_col = row[14]
        rx_no = row[15]
        sig = row[16]
        quantity = row[17]
        filename = row[18]
        lastname = row[19]
        firstname = row[20]
        group_no = row[21]
        dob = row[23]
        facility_name = row[24]
        created_date = row[25]
        pack_status = row[26]

        if pack_status == "invalid" or pack_status == "dropped" or pack_status == "manual":
            invalid = True
        else:
            invalid = False

        old_drug_name_set.add(drug_name)
        old_ndc_set.add(ndc)
        old_rx_no_set.add(rx_no)
        old_drug_dict[ndc] = drug_name
        old_pack_data.append({"pack_id": pack_id, "pack_display_id": pack_display_id, "robot_id": robot_id,
                              "rfid": rfid, "pack_no": pack_no, "pack_plate_location": pack_plate_location,
                              "pharmacy_fill_id": fill_id, "drug_name": drug_name, "ndc": ndc, "admin_date": admin_date,
                              "admin_time": admin_time, "slot_row": slot_row, "slot_col": slot_col, "pharmacy_rx_no":
                                  rx_no, "sig": sig, "quantity": quantity, "filename": filename,
                              "patient_name": lastname + "," + firstname, "patient_no": group_no, "dob": dob,
                              "facility_name": facility_name, "created_date": created_date})

    return old_drug_name_set, old_ndc_set, old_rx_no_set, old_drug_dict, old_pack_data, invalid


def get_total_packs_generated(database):
    db.init(database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    no_of_packs = PackDetails.select(PackDetails.id).wrapped_count()
    return no_of_packs


def get_inserted_pack_data(database, pack_id):
    new_ndc_set = set()
    new_rx_no_set = set()
    new_drug_name_set = set()
    new_drug_dict = {}

    db.init(database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    for record in PackHeader.select(PackDetails.id.alias('pack_id'), PackDetails.pack_display_id,
                                    PackDetails.rfid, PackDetails.pack_no, PackDetails.pack_plate_location,
                                    PackHeader.pharmacy_fill_id, DrugMaster.drug_name, DrugMaster.ndc,DrugMaster.strength, DrugMaster.strength_value,
                                    SlotHeader.hoa_date, SlotHeader.hoa_time, PackGrid.slot_row, PackGrid.slot_column,
                                    PatientRx.sig, PatientRx.pharmacy_rx_no, SlotDetails.quantity, PatientMaster.patient_name,
                                    PatientMaster.dob, PatientMaster.patient_no, FacilityMaster.facility_name, PackDetails.created_date).dicts().join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id) \
        .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
        .join(FacilityMaster, on=PatientMaster.facility_id == FacilityMaster.id) \
        .join(FileHeader, on=PackHeader.file_id == FileHeader.id) \
        .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
        .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
        .join(DrugMaster, on=PatientRx.drug_id == DrugMaster.id) \
        .join(SlotHeader, on=SlotHeader.pack_id == PackDetails.id) \
        .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id)\
        .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
        .where(PackDetails.id == pack_id):
        new_drug_name_set.add(record["drug_name"] + " " + record["strength"] + " " + record["strength_value"])
        new_ndc_set.add(record["ndc"])
        new_rx_no_set.add(record["pharmacy_rx_no"])
        new_drug_dict[record["ndc"]] = record["drug_name"]

    return new_drug_name_set, new_ndc_set, new_rx_no_set, new_drug_dict


