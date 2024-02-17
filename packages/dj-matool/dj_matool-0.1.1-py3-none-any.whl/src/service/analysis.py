# -*- coding: utf-8 -*-
"""
    src.analysis
    ~~~~~~~~~~~~~~~~
    This module defines all the self declared exceptions.

    Todo:

    :copyright: (c) 2015 by Dose pack LLC.

"""

import settings
from dosepack.base_model.base_model import db
from src.dao.alternate_drug_dao import save_alternate_drug_option

logger = settings.logger

if __name__ == "__main__":
    from model.model_init import init_db

    init_db(db, 'database_migration')
    save_alternate_drug_option({
        'pack_ids': [68749, 68649],
        'company_id': 3,
        'save_alternate_drug_option': True
    })
    # save_alternate_drug_option({
    #     'pack_ids': [68650],
    #     'company_id': 3,
    #     'save_alternate_drug_option': True
    # })
