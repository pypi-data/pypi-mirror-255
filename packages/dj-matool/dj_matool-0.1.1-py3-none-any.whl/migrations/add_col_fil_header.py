from dosepack.base_model.base_model import db, BaseModel
from src.model.model_file_header import FileHeader


def add_col_file_header(database):
    db.init(database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    #   remove if the column exists.
    # sql = 'ALTER TABLE fileheader Drop column manual_upload'
    # db.execute_sql((sql))

    # add column
    sql = 'ALTER TABLE fileheader ADD manual_upload bool'
    db.execute_sql((sql))

def main():
    print (add_col_file_header("alia"))

if __name__ == "__main__":
    # execute only if run as a script
    main()