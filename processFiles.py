import zipfile
import glob
import hashlib
import mysql.connector
import os


# hashing function
def md5_zip_file(f_name, zip_file_obj):
    hash_md5 = hashlib.md5()
    zip_file_obj.read(f_name)
    hash_md5.update(zip_file_obj.read(f_name))
    return hash_md5.hexdigest()


# open db connection
cnx = mysql.connector.connect(user='cms_user', password='Passw0rd',
                              host='127.0.0.1',
                              database='cms_files')
cursor = cnx.cursor()
create_table = '''CREATE TABLE IF NOT EXIST hashes
(
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    cms_name TEXT(30) NOT NULL,
    cms_ver TEXT(10) NOT NULL,
    path TEXT NOT NULL,
    ext TEXT(10),
    md5 TEXT(40) NOT NULL,
    size INT NOT NULL
)'''

try:
    cursor.execute(create_table)
except mysql.connector.Error as err:
    print("Failed creating database: {}".format(err))

add_file = ("INSERT INTO hashes "
            "(cms_name, cms_ver, path, ext, md5, size) "
            "VALUES (%s, %s, %s, %s, %s, %s)")
# list wordpress zip files
zipFilesList = glob.glob("wordpress/*.zip")
cms_name = 'wordpress'

try:
    for zipFileName in zipFilesList:
        print zipFileName
        # get wordpress version
        cms_ver = zipFileName[20:].split('.zip')[0]
        with zipfile.ZipFile(zipFileName, 'r') as archive:
            for tempfile in archive.filelist:
                if tempfile.file_size > 0:
                    data_file = (
                        cms_name, cms_ver, tempfile.filename, os.path.splitext(tempfile.filename)[1],
                        md5_zip_file(tempfile.filename, archive), tempfile.file_size)
                    # Insert new file
                    cursor.execute(add_file, data_file)
    cnx.commit()
finally:
    cursor.close()
    cnx.close()
