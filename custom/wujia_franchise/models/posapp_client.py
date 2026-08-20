from datetime import datetime
import logging
import requests

_logger = logging.getLogger(__name__)

class PosAppClient:

    _account_id = None
    _shops = []

    data_groups = [] # dữ liệu đã được group lại theo gòm các thuojc tin {"date": "YYYY-MM", total_receipt: number, total_amount: number, total_amount_app: number,}
    """
    Client for interacting with the PosApp Admin and Manage APIs.
    This class is a utility class and does not link to the database.
    """

    def __init__(self, token=None, session_cookie=None, base_url="https://admin-api.posapp.vn"):
        """
        Initialize the PosApp Client.
        :param token: The API token for authentication.
        :param session_cookie: The value of the posapp_session cookie.
        :param base_url: The base URL of the PosApp API.
        """
        self.base_url = base_url.rstrip('/')
        self.token = token or 'f48e656477b064b12575'
        self.session_cookie = session_cookie or 'eF2We3YQdG6SQRHCmf51zsUBG8mB8UCOSBQT1XVn'
        
        self.session = requests.Session()
        if self.session_cookie:
            self.session.headers.update({
                'Cookie': f'posapp_session={self.session_cookie}'
            })
    def set_data_group_by_date(self):
        self.data_groups = []

    def get_orders_by_payment_status(self, date_start, date_end, shop_code, page=1, limit=10, payment_status=-1):
        """
        Retrieve orders from PosApp by payment status.
        
        :param date_start: Start date in YYYY-MM-DD format.
        :param date_end: End date in YYYY-MM-DD format.
        :param account_id: Account ID.
        :param shop_id: Shop ID.
        :param page: Page number (default: 1).
        :param limit: Number of records per page (default: 10).
        :param payment_status: Payment status filter (default: -1).
        :param token: Override the API token (optional).
        :return: JSON response or dict containing the response details.
        """
        
        url = f"{self.base_url}/api/getOrdersByPaymentStatus"
        shop_id = ""
        token = ""
        
        for shop in self._shops:
            if shop['shop_name'] == shop_code:
                shop_id = shop['shop_id']
                token = shop['token']
                break
        
        payload = {
            'date_start': str(date_start),
            'date_end': str(date_end),
            'account_id': str(self._account_id),
            'shop_id': str(shop_id),
            'page': str(page),
            'limit': str(limit),
            'token': token or self.token,
            'payment_status': str(payment_status)
        }
        print("payload", payload)
        try:
            _logger.info("Sending POST request to PosApp API: %s with payload: %s", url, payload)
            response = self.session.post(url, data=payload, timeout=30)
            
            # Raise an HTTPError if the HTTP request returned an unsuccessful status code
            response.raise_for_status()
            
            try:
                json_data = response.json()
                data = json_data.get('data')
                orders =json_data.get('orders')

                date_obj = datetime.strptime(date_end, "%Y-%m-%d")
                date = date_obj.strftime("%Y-%m")
                count_receipt = 0
                count_amount = 0
                count_amount_app = 0
                for order in orders.get('data'):
                    count_receipt += 1
                    count_amount += order.get('total_final', 0)
                    count_amount_app += order.get('total_app', 0)
                self.data_groups.append({
                    'date': date,
                    'count_receipt': count_receipt,
                    'count_amount': count_amount,
                    'count_amount_app': count_amount_app
                })
                

                # lấy kêt dữ liệu
                current_page = orders.get('current_page')
                last_page = orders.get('last_page')
                if current_page < last_page:
                    data.extend(self.get_orders_by_payment_status(date_start, date_end, shop_code, current_page + 1, limit, payment_status))
                return { "orders": data }
            except ValueError:
                _logger.warning("PosApp API response is not a valid JSON: %s", response.text)
                return {
                    'success': False,
                    'error': 'Invalid JSON response',
                    'raw_response': response.text
                }
                
        except requests.exceptions.RequestException as e:
            _logger.error("Failed to connect to PosApp API: %s", e)
            return {
                'success': False,
                'error': str(e)
            }

    def system_login(self, user="vanhanhhtng", password="HtNg@2026", jwt_token=None):
        """
        Authenticate with the PosApp Manage system login API.
        
        :param user: Username (default: "vanhanhhtng").
        :param password: Password (default: "HtNg@2026").
        :param jwt_token: Optional jwt_token cookie value.
        :return: JSON response or dict containing the response details.
        """
        url = "https://manage-api.posapp.vn/api/system/login"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        token = jwt_token or '597052%7CaJV9tnAlCqPcrftGUwvyYRhPBsIPRS5V92lvrwMK6989d442'
        if token:
            headers['Cookie'] = f'jwt_token={token}'
            
        payload = {
            'user': user,
            'pass': password
        }
        
        try:
            _logger.info("Sending POST request to PosApp Login API: %s", url)
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            try:
                json_data = response.json()
                data = json_data.get('data')
                self._account_id = data.get('id')
                
                self._shops = [{ "shop_id": shop['shop_id'], "shop_name": shop['shop_name'][0:4], "token": shop['token']} for shop in data.get('account_shops', [])]
                return { "account_id": self._account_id }

            except ValueError:
                _logger.warning("PosApp Login API response is not a valid JSON: %s", response.text)
                return {
                    'success': False,
                    'error': 'Invalid JSON response',
                    'raw_response': response.text
                }
                
        except requests.exceptions.RequestException as e:
            _logger.error("Failed to connect to PosApp Login API: %s", e)
            return {
                'success': False,
                'error': str(e)
            }
