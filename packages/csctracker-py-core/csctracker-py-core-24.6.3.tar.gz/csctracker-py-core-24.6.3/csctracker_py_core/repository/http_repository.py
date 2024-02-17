from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from flask import request
from flask_cors import cross_origin

from csctracker_py_core.models.emuns.config import Config
from csctracker_py_core.repository.remote_repository import RemoteRepository
from csctracker_py_core.utils.configs import Configs
from csctracker_py_core.utils.request_info import RequestInfo

headers_sti = {
    'Cookie': Configs.get_env_variable(Config.STI_COOKIE),
    'User-Agent': 'PostmanRuntime/7.26.8'
}


class HttpRepository:
    def __init__(self, remote_repository: RemoteRepository):
        self.remote_repository = remote_repository
        pass

    def get_stock_type(self, ticker, headers=None):
        response = requests.get('https://statusinvest.com.br/home/mainsearchquery', params={"q": ticker},
                                headers=headers_sti)
        return response.json()

    def get_firt_stock_type(self, ticker, headers=None):
        return self.get_stock_type(ticker, headers)[0]

    # FIXME: importar o remote_repository.py
    def get_page_text(self, ticker, headers=None):
        stock = self.remote_repository.get_object("stocks", ["ticker"], {"ticker": ticker}, headers)
        page = requests.get(f"https://statusinvest.com.br{stock['url_infos']}", headers=headers_sti)
        return page.text

    def get_page_text_by_url(self, url, headers=None):
        page = requests.get(f"{url}", headers=headers_sti)
        return page.text

    def get_values_by_ticker(self, stock, force=False, headers=None, time_multiply=1):
        try:
            last_update = datetime.strptime(stock['last_update'], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)
            astimezone = datetime.now().astimezone(timezone.utc)
            time = astimezone.timestamp() * 1000 - last_update.timestamp() * 1000
            queue = time > (1000 * 60 * 15 * time_multiply) or time < 0
        except Exception as e:
            queue = True
        if queue or force:
            try:
                text = self.get_page_text(stock['ticker'], headers)
                soup = BeautifulSoup(text, "html5lib")
                self.get_values(soup, stock)
                try:
                    if stock["investment_type_id"] <= 4:
                        stock['pvp'] = self.get_info(stock, "vp", headers)
                except Exception as e:
                    print(e, stock['ticker'], "pvp")
                    pass
                self.remote_repository.update("stocks", ['ticker'], stock, headers)
            except Exception as e:
                print(e)
                pass
        investment_type = self.remote_repository.get_object("investment_types",
                                                            data={"id": stock['investment_type_id']},
                                                            headers=headers)
        return stock, investment_type, queue

    def get_soup(self, url, headers=None):
        text = self.get_page_text_by_url(url, headers)
        soup = BeautifulSoup(text, "html5lib")
        return soup

    def get_values(self, soup, stock):
        try:
            stock["segment"] = self.find_value(soup, "Segmento", "text", 2, 0)
        except:
            try:
                stock["segment"] = self.find_value(soup, "Segmento de Atuação", "text", 2, 0)
            except:
                try:
                    stock["segment"] = self.find_value(soup, "\nClasse anbima\n", "text", 2, 0)
                except:
                    pass

        try:
            price_text = self.find_value(soup, "Valor atual do ativo", "title", 2, 0)
        except:
            try:
                price_text = self.find_value(soup, "Valor atual", "title", 2, 0)
            except:
                price_text = self.find_value(soup, "Preço da cota", "title", 2, 0)

        stock["price"] = float(price_text.replace(".", "").replace(",", "."))

        try:
            txt = self.find_value(soup, "P/L", "text", 3, 0)
            stock["pl"] = float(txt.replace(".", "").replace(",", "."))
        except Exception as e:
            stock["pl"] = 0

        if stock["investment_type_id"] > 4:
            try:
                txt = self.find_value(soup, "P/VP", "text", 3, 0)
                stock["pvp"] = float(txt.replace(".", "").replace(",", "."))
            except Exception as e:
                stock["pvp"] = 0

        try:
            txt = self.find_value(soup, "Liquidez média diária", "text", 3, 0)
            stock["avg_liquidity"] = float(txt.replace(".", "").replace(",", "."))
        except Exception as e:
            stock["avg_liquidity"] = 0

        return stock

    def get_info(self, stock_, atributo, headers=None, tag="span", is_number=True):
        url_ = 'https://investidor10.com.br/fiis/' + stock_['ticker']
        if stock_['investment_type_id'] == 1:
            url_ = 'https://investidor10.com.br/acoes/' + stock_['ticker']
        elif stock_['investment_type_id'] == 4:
            url_ = 'https://investidor10.com.br/bdrs/' + stock_['ticker']
        elif stock_['investment_type_id'] == 1001:
            ticker_ = ''.join([i for i in stock_['ticker'] if not i.isdigit()])
            url_ = 'https://investidor10.com.br/indices/' + ticker_
        soup_ = self.get_soup(url_, headers)
        value_ = self.find_value(soup_, '_card ' + atributo, "class")[0]
        value_ = self.find_value(value_, '_card-body', "class")[0].find_all(tag)[0].text
        if is_number:
            value_ = float(value_.replace(".", "").replace(",", "."))
        return value_

    def find_value(self, soup, text, type, parents=0, children=None, child_Type="strong", value="text"):
        if type == "text":
            obj = soup.find_all(text=f"{text}")
        elif type == "class":
            obj = soup.find_all(class_=f"{text}")
        elif type == "title":
            obj = soup.find_all(title=f"{text}")
        elif type == "id":
            obj = soup.find_all(id=f"{text}")
        else:
            obj = soup.find_all(tag=f"{text}")

        if children is None:
            return obj
        else:
            obj = obj[children]

        for i in range(parents):
            obj = obj.parent
        if value == "text":
            strong__text = obj.find_all(child_Type)[0].text
        else:
            strong__text = obj.find_all(child_Type)[0][value]
        return strong__text

    def get_prices(self, ticker, type, daily=False, price_type="4"):
        if daily:
            response = requests.get(f'https://statusinvest.com.br/{type}/tickerprice?type=-1&currences%5B%5D=1',
                                    params={"ticker": ticker}, headers=headers_sti)
        else:
            response = requests.get(
                f'https://statusinvest.com.br/{type}/tickerprice?type={price_type}&currences%5B%5D=1',
                params={"ticker": ticker}, headers=headers_sti)
        return response.json()

    def get_prices_fundos(self, ticker, month=False):
        if month:
            response = requests.get(f'https://statusinvest.com.br/fundoinvestimento/profitabilitymainresult?'
                                    f'nome_clean={ticker}'
                                    f'&time=1', headers=headers_sti)
        else:
            response = requests.get(f'https://statusinvest.com.br/fundoinvestimento/profitabilitymainresult?'
                                    f'nome_clean={ticker}'
                                    f'&time=6', headers=headers_sti)
        return response.json()

    def get(self, url, params={}, headers=None, body=None):
        if body is not None:
            return requests.get(url, params=params, headers=headers, json=body)
        return requests.get(url, params=params, headers=headers)

    def post(self, url, body={}, headers=None, args=None):
        return requests.post(url, json=body, headers=headers, params=args)

    def get_api_token(self):
        return Configs.get_env_variable(Config.API_TOKEN)

    def get_json_body(self):
        return request.json

    def get_args(self):
        return request.args

    def get_headers(self):
        headers = request.headers
        headers_ = {}
        for key in headers.keys():
            headers_[key] = headers.get(key)
        if 'x-correlation-id' not in headers_:
            headers_['x-correlation-id'] = RequestInfo.get_request_id(True)
        return headers

    def get_request(self):
        return request

    def get_cross_origin(self):
        return cross_origin
