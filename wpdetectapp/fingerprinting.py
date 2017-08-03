import socket
import mysql.connector
from mysql.connector import errorcode
import urllib2
import hashlib
import operator


class FingerPrinting:
    prefix = 'wordpress/'
    request_limit = 10

    def __init__(self):
        # open db connection
        try:
            self.cnx = mysql.connector.connect(user='cms_user', password='Passw0rd',
                                               host='127.0.0.1',
                                               database='cms_files')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            raise Exception('DB Connection failed!')
        else:
            self.cursor = self.cnx.cursor()

    # hashing function
    @staticmethod
    def md5_content(content):
        hash_md5 = hashlib.md5()
        hash_md5.update(content)
        return hash_md5.hexdigest()

    def getSignificantPaths(self):
        sql = '''SELECT
          COUNT(DISTINCT(md5)),
          path
        FROM hashes
        WHERE ext NOT IN (".txt", ".php", ".html", ".htm")
        GROUP BY path
        ORDER BY COUNT(DISTINCT(md5)) DESC
        LIMIT 10;'''

        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
        except mysql.connector.Error as e:
            print e
            return None

        if rows is None or len(rows) == 0:
            return None
        else:
            return [row[1].split(self.prefix)[1] for row in rows]

    def getNextPaths(self, paths, vers):
        vers = [x[0] for x in vers]
        format_strings1 = ','.join(['%s'] * len(vers))
        paths = [self.prefix + path for path in paths]
        format_strings2 = ','.join(['%s'] * len(paths))

        sql = '''SELECT         
          COUNT(DISTINCT(md5)),
          path
        FROM hashes
        WHERE ext NOT IN (".txt", ".php", ".html", ".htm")
        AND cms_ver IN (%s)
        AND path NOT IN (%s)        
        GROUP BY path
        ORDER BY COUNT(DISTINCT(md5)) DESC
        LIMIT 10;''' % (format_strings1, format_strings2)

        try:
            vers.extend(paths)
            self.cursor.execute(sql, tuple(vers))
            rows = self.cursor.fetchall()
        except mysql.connector.Error as e:
            print e
            return None

        if rows is None or len(rows) == 0:
            return None
        else:
            return [row[1].split(self.prefix)[1] for row in rows]

    def getPossibleVers(self, md5, path):
        path = self.prefix + path
        sql = '''SELECT cms_ver FROM hashes 
              WHERE ext NOT IN (".txt", ".php", ".html", ".htm") 
              AND path = %s 
              AND md5 = %s'''

        try:
            self.cursor.execute(sql, (path, md5))
            row = self.cursor.fetchall()
        except mysql.connector.Error as e:
            print e
            return None

        return row

    @staticmethod
    def checkWebDomain(web_url):
        try:
            responseCode = urllib2.urlopen(web_url).getcode()
            if responseCode != 200:
                raise Exception('Invalid Domain')
        except Exception as e:
            print e
            raise Exception(e)

    def getWebContentHash(self, web_domain, urlPath):
        url = web_domain + '/' + urlPath
        try:
            response = urllib2.urlopen(url)
            page_content = response.read()
        except Exception:
            return None
        else:
            return FingerPrinting.md5_content(page_content)

    def detect(self, web_domain):
        webpage = 'http://' + web_domain
        try:
            # control the web adress
            self.checkWebDomain(webpage)
        except Exception as e:
            raise Exception(e)
        else:
            possibleVersions = []
            usedPaths = []
            commonPaths = self.getSignificantPaths()[:]
            foundVers = []
            limitCounter = 0
            # for commonPath in commonPaths:
            while True:
                commonPath = commonPaths[limitCounter]
                limitCounter += 1
                if limitCounter > self.request_limit - 1:
                    break
                # get MD5 of the page
                pageMd5 = self.getWebContentHash(webpage, commonPath)
                if pageMd5 is not None:
                    tempVersions = self.getPossibleVers(pageMd5, commonPath)

                    if tempVersions is None or len(tempVersions) == 0:
                        continue
                    else:
                        temp = [ver[0] for ver in tempVersions]
                        foundVers.append(temp)
                        possibleVersions = tempVersions

                    if len(possibleVersions) > 0:
                        # get new commonPath
                        usedPaths.append(commonPath)
                        newPaths = self.getNextPaths(usedPaths, possibleVersions)
                        if newPaths is None or len(newPaths) == 0:
                            break
                        else:
                            commonPaths = commonPaths[0:limitCounter]
                            commonPaths.extend(newPaths)
            # process the results
            print webpage
            print foundVers
            if len(foundVers) != 0:
                res = list(reduce(set.intersection, [set(item) for item in foundVers]))
                if len(res) != 0:  # if there is an intersection in all results
                    return ', '.join(res)
                else:  # if there is not, calculate an estimation
                    p = {}
                    for vers in foundVers:
                        for ver in vers:
                            if ver in p:
                                p[ver] = p[ver] + 1.0 / len(vers)
                            else:
                                p[ver] = 1.0 / len(vers)

                    sump = reduce(lambda x, y: x + y, p.values())
                    percent = {k: p[k] / sump * 100 for k in p.keys()}
                    sorted_x = sorted(percent.items(), key=operator.itemgetter(1), reverse=True)
                    result = ', '.join([item[0] + ': % ' + ('%.1f' % item[1]) for item in sorted_x])
                    # alternative output format
                    # result = {item[0]: ("%% %.1f" % item[1]) for item in sorted_x}
                    return result
            else:
                return None

    def __del__(self):
        try:
            self.cursor.close()
            self.cnx.close()
        except AttributeError:
            pass
# try it out
obj = FingerPrinting()
print obj.detect('www.google.com')