"""Module for KumpeApps API Functions"""
from datetime import date
import datetime
import random
import string
from flask import request
import pymysql
import requests

class KAPI:
    """KumpeApps API Functions"""
    def __init__(
        self,
        apikey: str,
        mysql_creds=None
    ):
        self.apikey = apikey
        self.mysql_creds = mysql_creds

    def create_user(
        self,
        username,
        password,
        email,
        first_name,
        last_name,
        comment="Added via API"
    ):
        """Creates new user on the KumpeApps System"""
        data = {
            "_key": self.apikey,
            "login": username,
            "pass": password,
            "email": email,
            "name_f": first_name,
            "name_l": last_name,
            "comment": comment
            }
        response = requests.post(
            'https://www.kumpeapps.com/api/users',
            data=data,
            timeout=10
            )
        return response.json()

    def create_subuser(
        self,
        username,
        password,
        email,
        first_name,
        last_name,
        master_id,
        comment="Added via API"
    ):
        """Create new sub/child user on the KumpeApps System"""
        data = {
            "_key": self.apikey,
            "login": username,
            "pass": password,
            "email": email,
            "name_f": first_name,
            "name_l": last_name,
            "comment": comment,
            "subusers_parent_id": master_id}
        response = requests.post(
            'https://www.kumpeapps.com/api/users',
            data=data,
            timeout=10
            )
        return response.json()

    def authenticate_user(self, username, password):
        """Authenticate user credentials on KumpeApps"""
        data = {
            "_key": self.apikey,
            "login": username,
            "pass": password
            }
        response = requests.get(
            'https://www.kumpeapps.com/api/check-access/by-login-pass',
            params=data,
            timeout=10
            )
        return response.json()

    def add_access(
        self,
        user_id,
        product_id,
        begin_date=date.today(),
        expire_date='2037-12-31',
        comment='Added via API'
    ):
        """Add product/access to user on KumpeApps"""
        data = {
            "_key": self.apikey,
            "user_id": user_id,
            "product_id": product_id,
            "begin_date": begin_date,
            "expire_date": expire_date,
            "comment": comment
            }
        response = requests.post(
            'https://www.kumpeapps.com/api/access',
            data=data,
            timeout=10
            )
        return response.json()

    def get_user_info(self, username):
        """Get user info from KumpeApps"""
        if self.mysql_creds is not None:
            database = self.mysql_connect()
            cursor = database.cursor(
                pymysql.cursors.DictCursor
                )
            sql = "SELECT * FROM vw_am_user WHERE 1=1 AND login = %s;"
            cursor.execute(sql, (username,))
            results = cursor.fetchone()
            cursor.close()
            database.close()
            return results
        else:
            raise PermissionError("MySQL Creds required for this function")

    def get_authkey_info(self, auth_key):
        """Get info from auth_key"""
        if self.mysql_creds is not None:
            database = self.mysql_connect()
            cursor = database.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM %s WHERE 1=1 AND auth_key = %s;"
            cursor.execute(sql, ('Core_RESTAPI.v5__vw_Auth_Keys', auth_key,))
            results = cursor.fetchone()
            cursor.close()
            database.close()
            return results
        else:
            raise PermissionError("MySQL Creds required for this function")

    def get_user_info_byid(self, user_id):
        """Get User Info by user_id"""
        if self.mysql_creds is not None:
            database = self.mysql_connect()
            cursor = database.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM vw_am_user WHERE 1=1 AND user_id = %s;"
            cursor.execute(sql, (user_id,))
            results = cursor.fetchone()
            cursor.close()
            database.close()
            return results
        else:
            raise PermissionError("MySQL Creds required for this function")

    def delete_user(self, user_id):
        """Delete User from KumpeApps"""
        data = {
            "_key": self.apikey,
            "_method": "DELETE"
            }
        response = requests.post(
            f'https://www.kumpeapps.com/api/users/{user_id}',
            data=data,
            timeout=10
            )
        return response.json()

    def expire_access(self, user_id, product_id, comment="Expired via API"):
        """Set access/product expiration date to yesterday"""
        if self.mysql_creds is not None:
            today = date.today()
            yesterday = today - datetime.timedelta(days=1)
            database = self.mysql_connect()
            cursor = database.cursor(pymysql.cursors.DictCursor)
            sql = """SELECT access_id, expire_date FROM
            Core_KumpeApps.am_access WHERE 1=1
            AND user_id = %s AND product_id = %s AND
            expire_date > now();"""
            cursor.execute(sql, (user_id, product_id))
            results = cursor.fetchall()
            cursor.close()
            database.close()
            if not results:
                return
            for access in results:
                access_id = access['access_id']
                data = {
                    "_key": self.apikey,
                    "expire_date": yesterday,
                    "comment": comment
                    }
                requests.put(
                    f'https://www.kumpeapps.com/api/access/{access_id}',
                    data=data,
                    timeout=10
                    )
            return
        else:
            raise PermissionError("MySQL Creds required for this function")

    def update_user(
        self,
        user_id,
        username,
        email,
        first_name,
        last_name,
        comment="Updated via API"
    ):
        """Update User on KumpeApps"""
        data = {
            "_key": self.apikey,
            "_method": "PUT",
            "login": username,
            "email": email,
            "name_f": first_name,
            "name_l": last_name,
            "comment": comment
            }
        response = requests.post(
            f'https://www.kumpeapps.com/api/users/{user_id}',
            data=data,
            timeout=10
            )
        return response

    def access_log_insert(self, user_id, referrer, url):
        """Insert into KumpeApps access log"""
        if self.mysql_creds is not None:
            ip_address = request.environ['HTTP_X_FORWARDED_FOR']
            database = self.mysql_connect()
            cursor = database.cursor(pymysql.cursors.DictCursor)
            sql = """INSERT INTO
            `am_access_log`(`user_id`, `time`, `url`, `remote_addr`,
            `referrer`) VALUES (%s,now(),%s,%s,%s)"""
            cursor.execute(sql, (user_id, url, ip_address, referrer, ))
            database.commit()
            cursor.close()
            return
        else:
            raise PermissionError("MySQL Creds required for this function")

    def create_auth_link(
        self,
        master_id,
        auth_user_id,
        link_user_id,
        link="https://khome.kumpeapps.com/portal/wish-list.php",
        scope="WishList",
        scope2="none",
        scope3="none",
        scope4="none",
        kiosk=0
    ):
        """Create Auth Link for KHome"""
        if self.mysql_creds is not None:
            randomstring = string.ascii_letters + string.digits
            auth_token = ''.join(random.choice(randomstring) for i in range(10))
            database = pymysql.connect(
                db='Web_KumpeHome',
                user=self.mysql_creds['username'],
                passwd=self.mysql_creds['password'],
                host='sql.kumpedns.us',
                port=3306
                )
            cursor = database.cursor(pymysql.cursors.DictCursor)
            sql = """INSERT INTO `Web_KumpeHome`.`AuthenticatedLinks`
            (`master_id`,`authenticated_user_id`,`link_user_id`,`link`,
            `expiration`,`token`,`scope`,`scope2`,`scope3`,`scope4`,
            `is_kiosk`) VALUES (%s,%s,%s,%s,NOW() + INTERVAL 365 DAY,
            %s,%s,%s,%s,%s,%s);"""
            cursor.execute(
                sql,
                (
                    master_id,
                    auth_user_id,
                    link_user_id,
                    link,
                    auth_token,
                    scope,
                    scope2,
                    scope3,
                    scope4,
                    kiosk,
                    )
                )
            database.commit()
            cursor.close()
            database.close()
            return link+'?token='+auth_token
        else:
            raise PermissionError("MySQL Creds required for this function")

    def mysql_connect(self):
        """Connect to MySQL"""
        database = pymysql.connect(
            db='Core_KumpeApps',
            user=self.mysql_creds['username'],
            passwd=self.mysql_creds['password'],
            host='sql.kumpedns.us',
            port=3306
            )
        return database
