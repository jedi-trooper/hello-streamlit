import json
import requests
import pandas as pd
from breeze_connect import BreezeConnect

class apification():
    def __init__(self, creds):    
        self.creds=creds
        try:
            
            self.api = BreezeConnect(api_key=creds['appKey'])
            self.api.generate_session(api_secret=creds['secretKey'],session_token=creds['sessionKey'])

        except Exception as e:
            print(f"Error : {e}")
            self.api = None

            
            
    def get_object(self):
        return self.api
    
    
    def user_details(self):
        
        try:
            response = self.api.get_customer_details(self.creds['sessionKey'])
        
            if response['Status'] == 200:
                userID = response['Success']['idirect_userid']
                username = response['Success']['idirect_user_name']            


                response2 = self.api.get_funds()

                if response2['Status'] == 200:
                    account = response2['Success']['bank_account']
                    balance = response2['Success']['total_bank_balance']

                    output = {
                        'userID':userID,
                        'username':username,
                        'account':account,
                        'balance':balance
                    }


                    return output
                
            else:
                err = response['Error']
                print(f"{err}")

                error = {
                'error' : err
                }

            return error
        
        except Exception as e:
            return f"Error : {e}"
                         
                    
        
    def place_order(self, params):
        
        try:

            self.params = params

            response = self.api.place_order(
                stock_code=self.params['stock_code'],
                exchange_code=params['exchange_code'],
                product=params['product'],
                action=self.params['action'],
                order_type=self.params['order_type'],
                stoploss="",
                quantity=self.params['quantity'],
                price=self.params['price'],
                validity="day",
                validity_date=self.params['validity_date'],
                disclosed_quantity="0",
                expiry_date=self.params['expiry_date'],
                right=self.params['right'],
                strike_price=self.params['strike_price']
           )

            
            return response

#             if response['Status'] == 200:
#                 print(f"{response['Success']}")
#                 orderID = response['Success']['order_id']

#                 msg = f'Order ID: {orderID} !!'            
#                 return response['Success']

#             else:
#                 err = json.dumps({"Error" : response['Error']})
#                 return err                
#                 return f"Error : {response['Error']}"


        
        except Exception as e:
            err = json.dumps({"Error" : e})
            return err


        
        
        
        

    def orderbook(self):        
        try:
            response = self.api.get_order_list(
                exchange_code="NFO",
                from_date="2023-09-10T10:00:00.000Z",
                to_date="2023-09-15T10:00:00.000Z"
            )            

            if response['Status'] == 200:
                df = pd.DataFrame(response['Success'])
                return df
            else:
                print(f"{response['Error']}")
                
        except Exception as e:
            return f"Error : {e}"



    def charts(self, params):        
        try:
            response = self.api.get_historical_data_v2(interval=params['interval'],
                            from_date= params['from_date'],
                            to_date= params['to_date'],
                            stock_code=params['stock_code'],
                            exchange_code=params['exchange_code'],
                            product_type=params['product_type'],
                            expiry_date=params['expiry_date'],
                            right=params['right'],
                            strike_price=params['strike_price']
            )            

            if response['Status'] == 200:
                df = pd.DataFrame(response['Success'])
                df['Date'] = pd.to_datetime(df['datetime'])  # Convert 'datetime' to datetime64
                df['Price'] = df['close'].astype(float)  # Convert 'close' to float

                # Create 'chart_data' DataFrame with 'Price' and 'Date' columns and 'Date' as the index
                chart_data = df[['Price', 'Date']]
                return chart_data

            else:
                print(f"{response['Error']}")

        except Exception as e:
            return f"Error : {e}"
        
        
    def option_chain(self, params):                
        try:
            response_1 = self.api.get_option_chain_quotes(
                            stock_code=params['stock_code'],
                            exchange_code="NFO",
                            product_type="options",
                            expiry_date=params['expiry_date'],
                            right="call"
                       )


            response_2 = self.api.get_option_chain_quotes(
                            stock_code=params['stock_code'],
                            exchange_code="NFO",
                            product_type="options",
                            expiry_date=params['expiry_date'],
                            right="put"
                       )
            
            
            response_3 = self.api.get_quotes(stock_code=params['stock_code'], exchange_code="NSE")
            
            if (response_1['Status']==200) and (response_2['Status'] == 200) and (response_3['Status']==200):
                df1 = pd.DataFrame(response_1['Success'])
                df2 = pd.DataFrame(response_2['Success'])

                merged_df = pd.merge(df1, df2, on='strike_price', how='inner')
                merged_df = merged_df[['strike_price', 'previous_close_x', 'previous_close_y']]
                merged_df.columns = ['strike', 'call', 'put']                
                merged_df = merged_df[(merged_df['call'] != 0) & (merged_df['put'] != 0)]
                
                
                spot = response_3['Success'][0]['ltp']
                strike = int(round(spot/50,0)*50)
                
                merged_df = merged_df[(merged_df.strike > strike - 300 ) & (merged_df.strike < strike + 300)]

                return merged_df

            else:
                print(f"{response['Error']}")

        except Exception as e:
            return f"Error : {e}"


        
    def news(self,params):

        stock = params['stock_code']
        from_date =params['from_date']
        apiKey = "4726e7136e884e55b5bbbf27852ef51e"
        language = "en"
        url = f"https://newsapi.org/v2/everything?q={stock}&from={from_date}&sortBy=publishedAt&apiKey={apiKey}&language={language}"
        response = requests.get(url)

        data = response.json()

        if data['status'] == 'ok':
            data = data['articles']

        table = pd.DataFrame(data)

        table = table[["publishedAt", "author","title"]]
        table['publishedAt'] = pd.to_datetime(table['publishedAt'])
        table['publishedAt'] = table['publishedAt'].dt.strftime('%Y-%m-%d')

        return table            
    
    
       
    def place_basket(self, basket):
        
        orders = {'call' : '', 'put' : ''}

        try:
            for params in basket:


                    response = self.api.place_order(
                        stock_code=params['stock_code'],
                        exchange_code=params['exchange_code'],
                        product=params['product'],
                        action=params['action'],
                        order_type=params['order_type'],
                        stoploss="",
                        quantity=params['quantity'],
                        price=params['price'],
                        validity="day",
                        validity_date=params['validity_date'],
                        disclosed_quantity="0",
                        expiry_date=params['expiry_date'],
                        right=params['right'],
                        strike_price=params['strike_price']
                   )


                    if response['Status'] == 200:
                        print(f"{response['Success']}")
                        orderID = response['Success']['order_id']

                        orders[params['right']] = orderID

                    else:
                        print(f"{response['Error']}")
                        orders[params['right']] = response['Error']

            return json.dumps(orders)


        except Exception as e:
            err = json.dumps({"Error" : e})
            return err

    def calculate_pnl(self):

        total_cost,pnl = 0,0
        response = self.api.get_portfolio_positions()
        if response['Success'] == None:
            # Create an empty DataFrame with columns
            columns = ['stock_code', 'expiry_date', 'strike_price', 'right', 'action', 'quantity', 'average_price', 'ltp']
            positions = pd.DataFrame(columns=columns)
            return positions

            

        else:
            positions = pd.DataFrame(response['Success'])
            positions = positions[['stock_code', 'expiry_date', 'strike_price', 'right', 'action', 'quantity', 'average_price', 'ltp']]                

            return positions