import settings
import datetime
from typing import Dict, Any
from peewee import InternalError, IntegrityError, JOIN_LEFT_OUTER, DataError, DoesNotExist, fn
from dosepack.utilities.utils import log_args_and_response, convert_date_from_sql_to_display_date
from src.model.model_code_master import CodeMaster
from src.model.model_consumable_sent_data import ConsumableSentData
from src.model.model_consumable_tracker import ConsumableTracker
from src.model.model_consumable_type_master import ConsumableTypeMaster
from src.model.model_consumable_used import ConsumableUsed
from src.model.model_courier_master import CourierMaster
from src.model.model_order_details import OrderDetails
from src.model.model_order_document import OrderDocument
from src.model.model_order_status_tracker import OrderStatusTracker
from src.model.model_orders import Orders
from src.model.model_shipment_tracker import ShipmentTracker

logger = settings.logger


@log_args_and_response
def get_orders_by_company_id(company_id, from_date, to_date):
    """
        Function is used to get order list by company id and date
        @param to_date:
        @param from_date:
        @param company_id:
    """
    order_data: dict = dict()
    try:
        query = Orders.select(Orders.id.alias("order_id"),
                              Orders.inquiry_no,
                              Orders.company_id,
                              Orders.status,
                              Orders.created_by.alias("inquired_by"),
                              Orders.lead_time,
                              Orders.payment_link,
                              Orders.approval_date,
                              Orders.created_date,
                              Orders.modified_date,
                              OrderDocument.id.alias("doc_code"),
                              OrderDocument.document_type,
                              OrderDocument.file_name,
                              ShipmentTracker.tracking_number,
                              ShipmentTracker.created_time.alias('shipment_added_date'),
                              ShipmentTracker.created_by.alias('shipment_info_by'),
                              CourierMaster.name.alias('courier_name'),
                              CourierMaster.website.alias('courier_website')).dicts() \
            .join(OrderDocument, JOIN_LEFT_OUTER, on=OrderDocument.order_id == Orders.id) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=OrderDocument.document_type == CodeMaster.id) \
            .join(ShipmentTracker, JOIN_LEFT_OUTER, on=Orders.id == ShipmentTracker.order_id) \
            .join(CourierMaster, JOIN_LEFT_OUTER, on=CourierMaster.id == ShipmentTracker.courier_id) \
            .where(Orders.created_date.between(from_date, to_date),
                   Orders.company_id == company_id) \
            .order_by(Orders.created_date)
        for record in query:
            if record["order_id"] not in order_data:
                if record["status"] == settings.ORDER_IN_TRANSIT:
                    record["expected_delivery"] = record["modified_date"] + datetime.timedelta(
                        days=settings.FIX_SHIPPING_DAYS)
                    record["expected_delivery"] = convert_date_from_sql_to_display_date(record["expected_delivery"])
                if record["approval_date"] is not None:
                    record["approval_date"] = convert_date_from_sql_to_display_date(record["approval_date"])
                record["document"] = {"order_summary": "order_summary"}  # to handle options in front-end
                order_data[record["order_id"]] = record
            if record["doc_code"] is not None:
                document_type = settings.ORDER_DOCS_CODE[record["document_type"]]
                order_data[record["order_id"]]["document"][document_type] = record["file_name"]

        logger.info("In get_orders_by_company_id: order_data: {}".format(order_data))
        order_list = order_data.values()

        return order_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_orders_by_company_id {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_orders_by_company_id {}".format(e))
        raise e


@log_args_and_response
def get_orders_by_date(from_date, to_date):
    """
        Function is used to get order list by date
        @param to_date:
        @param from_date:
    """
    order_data: dict = dict()
    try:
        query = Orders.select(Orders.id.alias("order_id"),
                              Orders.inquiry_no,
                              Orders.company_id,
                              Orders.status,
                              Orders.created_by.alias("inquired_by"),
                              Orders.lead_time,
                              Orders.payment_link,
                              Orders.approval_date,
                              Orders.created_date,
                              Orders.modified_date,
                              OrderDocument.id.alias("doc_code"),
                              OrderDocument.document_type,
                              OrderDocument.file_name,
                              ShipmentTracker.tracking_number,
                              ShipmentTracker.created_time.alias('shipment_added_date'),
                              ShipmentTracker.created_by.alias('shipment_info_by'),
                              CourierMaster.name.alias('courier_name'),
                              CourierMaster.website.alias('courier_website')).dicts() \
            .join(OrderDocument, JOIN_LEFT_OUTER, on=OrderDocument.order_id == Orders.id) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=OrderDocument.document_type == CodeMaster.id) \
            .join(ShipmentTracker, JOIN_LEFT_OUTER, on=Orders.id == ShipmentTracker.order_id) \
            .join(CourierMaster, JOIN_LEFT_OUTER, on=CourierMaster.id == ShipmentTracker.courier_id) \
            .where(Orders.created_date.between(from_date, to_date)) \
            .order_by(Orders.created_date)

        for record in query:
            if record["order_id"] not in order_data:
                if record["status"] == settings.ORDER_IN_TRANSIT:
                    record["expected_delivery"] = record["modified_date"] + datetime.timedelta(
                        days=settings.FIX_SHIPPING_DAYS)
                    record["expected_delivery"] = convert_date_from_sql_to_display_date(record["expected_delivery"])
                if record["approval_date"] is not None:
                    record["approval_date"] = convert_date_from_sql_to_display_date(record["approval_date"])
                record["document"] = {"order_summary": "order_summary"}  # to handle options in front-end
                order_data[record["order_id"]] = record
            if record["doc_code"] is not None:
                document_type = settings.ORDER_DOCS_CODE[record["document_type"]]
                order_data[record["order_id"]]["document"][document_type] = record["file_name"]

        logger.info("In get_orders_by_date: order_data: {}".format(order_data))
        order_list = order_data.values()

        return order_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_orders_by_date {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_orders_by_date {}".format(e))
        raise e


@log_args_and_response
def create_order_record(order_insert_dict: dict):
    try:
        return Orders.db_create_record(order_insert_dict, Orders, get_or_create=False)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in create_order_record:  {}".format(e))
        raise e


@log_args_and_response
def create_order_details_multiple_record(order_details_insert_dict: list):
    try:
        return OrderDetails.db_create_multi_record(order_details_insert_dict, OrderDetails)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in create_order_details_multiple_record:  {}".format(e))
        raise e


@log_args_and_response
def create_order_status_track(order_id, status, user_id):
    """
    Makes entry in OrderStatusTracker
    :param order_id: Order id
    :param status: New status of order
    :param user_id: User id
    :return:
    """
    try:
        return OrderStatusTracker.db_create_record({"order_id": order_id,
                                                    "status": status,
                                                    "created_by": user_id},
                                                   OrderStatusTracker, get_or_create=False)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in keep_order_status_track:  {}".format(e))
        raise e


@log_args_and_response
def update_orders(dict_order_info: Dict[str, Any], order_id: int) -> bool:
    """
    Update orders by id order id
    """
    try:
        return Orders.db_update_orders(dict_order_info=dict_order_info, order_id=order_id)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_orders:  {}".format(e))
        raise e


@log_args_and_response
def track_consumable_quantity(order_id):
    """
    Updates ConsumableTracker with quantity that was ordered
    :param order_id: Order id
    :return:
    """
    try:
        for record in get_by_order_id(order_id=order_id):
            ConsumableTracker.db_update_or_create(record["order_id"], record["consumable_id"], record)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in track_consumable_quantity:  {}".format(e))
        raise e


@log_args_and_response
def get_by_order_id(order_id: int):
    """
        get order details and order id
        :param order_id: Order id
        :return:
    """
    try:
        for record in OrderDetails.select(OrderDetails.consumable_id,
                                          OrderDetails.quantity,
                                          Orders.company_id,
                                          Orders.id.alias('order_id')).dicts() \
                .join(Orders, on=Orders.id == OrderDetails.order_id) \
                .where(OrderDetails.order_id == order_id):
            yield record
    except (IntegrityError, InternalError) as e:
        logger.error("error in get_by_order_id:  {}".format(e))
        raise e


@log_args_and_response
def get_order_summary_data(order_id: int, company_id: int):
    """
            get order summary
            @param order_id:
            @param company_id:
    """
    summary_data: dict = dict()
    try:
        if company_id is None:
            company_id = Orders.get(id=order_id).company_id

        logger.info("In get_order_summary_data: company_id:{}".format(company_id))
        query = OrderDetails.select(ConsumableTypeMaster.name.alias("consumables_type"),
                                    OrderDetails.quantity,
                                    Orders.inquiry_no,
                                    ConsumableTracker.quantity.alias("consumables_available"),
                                    Orders.created_by,
                                    Orders.created_date,
                                    Orders.company_id).dicts() \
            .join(ConsumableTypeMaster, on=OrderDetails.consumable_id == ConsumableTypeMaster.id) \
            .join(Orders, on=OrderDetails.order_id == Orders.id) \
            .join(ConsumableTracker, JOIN_LEFT_OUTER,
                  on=(ConsumableTracker.consumable_id == ConsumableTypeMaster.id & ConsumableTracker.company_id == company_id)) \
            .where(OrderDetails.order_id == order_id)
        for record in query:
            summary_data["inquired_by"] = record["created_by"]
            summary_data["inquiry_no"] = record["inquiry_no"]
            summary_data["company_id"] = record["company_id"]
            summary_data["created_date"] = convert_date_from_sql_to_display_date(record["created_date"])
            if record["consumables_available"] is None:
                record["consumables_available"] = 0
            summary_data.setdefault("consumables", []).append(record)

        return summary_data

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_order_summary_data:  {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_order_summary_data {}".format(e))
        raise e


@log_args_and_response
def get_active_consumables(company_id: int, active: bool = True):
    """
            get active consumable
            @param active:
            @param company_id:
    """
    consumables = list()
    try:
        join_condition = ((ConsumableTracker.consumable_id == ConsumableTypeMaster.id) & (
                    ConsumableTracker.company_id == company_id))
        for record in ConsumableTypeMaster.select(ConsumableTypeMaster.name,
                                                  ConsumableTypeMaster.id,
                                                  ConsumableTypeMaster.description,
                                                  ConsumableTypeMaster.active,
                                                  ConsumableTracker.quantity.alias("consumables_available")).dicts() \
                .join(ConsumableTracker, JOIN_LEFT_OUTER, on=join_condition) \
                .where(ConsumableTypeMaster.active == active):
            if record["consumables_available"] is None:
                record["consumables_available"] = 0
            consumables.append(record)

        return consumables

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_active_consumables:  {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_active_consumables {}".format(e))
        raise e


@log_args_and_response
def get_couriers_data():
    """
        get couriers data
    """
    try:
        return CourierMaster.db_get_couriers_data()
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_couriers_data:  {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_couriers_data {}".format(e))
        raise e


@log_args_and_response
def create_shipment_tracker_record(dict_tracking_info):
    """
    Makes entry in ShipmentTracker
    :param dict_tracking_info: dict_tracking_info
    :return:
    """
    try:
        return ShipmentTracker.db_create_record(dict_tracking_info, ShipmentTracker, get_or_create=False)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in create_shipment_tracker_record:  {}".format(e))
        raise e


@log_args_and_response
def create_order_document(file_info):
    """
    Makes entry in OrderDocument for invoice file
    :param file_info: file_info
    :return:
    """
    try:
        return OrderDocument.db_create_record(file_info, OrderDocument)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in create_order_document:  {}".format(e))
        raise e


@log_args_and_response
def get_consumables_types():
    """
        get all consumable types
    """
    try:
        return ConsumableTypeMaster.db_get_consumables_types()
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_consumables_types:  {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_consumables_types {}".format(e))
        raise e


@log_args_and_response
def get_monthly_stats(company_id, month, year):
    """
        Returns consumables used of company on monthly base.
        Data will be filtered from given month and year to current month and year
        :param company_id:
        :param month:
        :param year:
        :return: generator
    """
    try:
        for record in ConsumableUsed.select(ConsumableUsed.consumable_id,
                                            ConsumableTypeMaster.name,
                                            fn.SUM(ConsumableUsed.used_quantity).alias('quantity'),
                                            fn.MONTHNAME(ConsumableUsed.created_date).alias('month_name'),
                                            fn.MONTH(ConsumableUsed.created_date).alias('month'),
                                            fn.YEAR(ConsumableUsed.created_date).alias('year')).dicts() \
                .join(ConsumableTypeMaster, on=ConsumableUsed.consumable_id == ConsumableTypeMaster.id) \
                .where(ConsumableUsed.company_id == company_id,
                       fn.YEAR(ConsumableUsed.created_date) >= year) \
                .group_by(ConsumableUsed.consumable_id,
                          fn.YEAR(ConsumableUsed.created_date).desc(),
                          fn.MONTH(ConsumableUsed.created_date).desc()) \
                .order_by(ConsumableUsed.created_date.desc()):
            record["quantity"] = int(record["quantity"])
            if record['month'] < month and record["year"] <= year:
                return
            yield record
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_monthly_stats:  {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_monthly_stats {}".format(e))
        raise e


@log_args_and_response
def get_date_of_last_sent_consumable_data(company_id):
    try:
        last_sent_date = ConsumableSentData.db_get_date_of_last_sent_consumable_data(company_id)
        return last_sent_date
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_date_of_last_sent_consumable_data:  {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_date_of_last_sent_consumable_data {}".format(e))
        raise e


@log_args_and_response
def insert_into_consumable_sent_data_dao(consumable_sent_data):
    try:
        status = ConsumableSentData.db_create_multi_record(consumable_sent_data, ConsumableSentData)
        return status
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in insert_into_consumable_sent_data_dao:  {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in insert_into_consumable_sent_data_dao {}".format(e))
        raise e