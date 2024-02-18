from .BaseMicrosoftAPI import BaseMicrosoftAPI
import requests

class GraphAPI(BaseMicrosoftAPI):
    def connect(self, tenant_ID, app_ID, secret_key):
       super().connect(tenant_ID, app_ID, secret_key,
                        'https://graph.microsoft.com/.default')

    def list_users(self, properties=None):
        if properties:
            parameters = ','.join(properties)
            url = f'https://graph.microsoft.com/v1.0/users?$top=999&$select={parameters}'
        else:
            url = 'https://graph.microsoft.com/v1.0/users'
        response = self.call_api(url)
        return response

    def list_subscribed_skus(self):
        url = 'https://graph.microsoft.com/v1.0/subscribedSkus'
        response = self.call_api(url)
        return response

    def list_organizations(self):
        url = 'https://graph.microsoft.com/v1.0/organization'
        response = self.call_api(url)
        return response

    def get_details(self, listParamsExtract=[
                'getOneDriveUsageAccountDetail',
                'getOneDriveActivityUserDetail',
                'getTeamsDeviceUsageUserDetail',
                'getTeamsUserActivityUserDetail',
                'getEmailActivityUserDetail',
                'getEmailAppUsageUserDetail',
                'getSharePointActivityUserDetail',
                'getSharePointSiteUsageDetail',
                'getSkypeForBusinessActivityUserDetail',
                'getSkypeForBusinessDeviceUsageUserDetail',
                'getYammerActivityUserDetail',
                'getYammerDeviceUsageUserDetail',
                'getOffice365ActiveUserDetail',
                'getSkypeForBusinessOrganizerActivityUserCounts',
                'getMailboxUsageDetail','getMailboxUsageStorage'
            ], paramsData=('period', '7')):
        
        results = []

        supported_paramsExtract = [
            'getOneDriveUsageAccountDetail',
            'getOneDriveActivityUserDetail',
            'getTeamsDeviceUsageUserDetail',
            'getTeamsUserActivityUserDetail',
            'getEmailActivityUserDetail',
            'getEmailAppUsageUserDetail',
            'getSharePointActivityUserDetail',
            'getSharePointSiteUsageDetail',
            'getSkypeForBusinessActivityUserDetail',
            'getSkypeForBusinessDeviceUsageUserDetail',
            'getYammerActivityUserDetail',
            'getYammerDeviceUsageUserDetail',
            'getOffice365ActiveUserDetail'
        ]

        if paramsData[0] == 'period':
            supported_paramsExtract+=['getSkypeForBusinessOrganizerActivityUserCounts',\
                'getMailboxUsageDetail','getMailboxUsageStorage']

        for item in listParamsExtract:

            if item not in supported_paramsExtract:
                print(f'Parameter not supported {item} \n'\
                    f'Supported parameters: {supported_paramsExtract}')
                return None

            else:
                urls = {
                'period': f"https://graph.microsoft.com/v1.0/reports/"\
                            f"{item}(period='D{paramsData[1]}')",
                'date': f"https://graph.microsoft.com/v1.0/reports/"\
                        f"{item}(date={paramsData[1]})"
                }

                url = urls.get(paramsData[0])
                response = self.call_api_stream(url)
                results.append((item, response))

        return results

    def office365_active_user_detail(self, params=('period', '7')):
        urls = {
            'period': f"https://graph.microsoft.com/v1.0/reports/"\
                      f"getOffice365ActiveUserDetail(period='D{params[1]}')",
            'date': f"http://graph.microsoft.com/v1.0/reports/"\
                    f"getOffice365ActiveUserDetail(date={params[1]})"
        }

        url = urls.get(params[0])
        response = self.call_api_stream(url)
        return response

    def office365_mailbox_usage_detail(self, period=7):
        supported_periods = [7, 30, 90, 180]
        if period not in supported_periods:
            print(f'office_365_mailbox_usage_detail: please use one of'\
                  f'supported periods: {period}')
            # raise error
            return None
        else:
            url = f"https://graph.microsoft.com/v1.0/reports/"\
                  f"getMailboxUsageDetail(period='D{period}')"
            response = self.call_api_stream(url)
            return response

    def methods(self):
        methods = [
            {
                'method_name': 'list_users',
                'method': self.list_users,
                'format': 'json'
            },
            {
                'method_name': 'list_subscribed_skus',
                'method': self.list_subscribed_skus,
                'format': 'json'
            },
            {
                'method_name': 'list_organizations',
                'method': self.list_organizations,
                'format': 'json'
            },
            {
                'method_name': 'get_details',
                'method': self.get_details,
                'format': 'list_csv'
            }
        ]
        return methods
