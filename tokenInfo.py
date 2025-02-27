import httpx


class TokenInfo:
    def __init__(self):
        pass

    @staticmethod
    async def get_token_info(token_mint_address):
        data = {}
        """Get Token Info"""

        url = f"https://api.jup.ag/tokens/v1/token/{token_mint_address}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json() 
            else:
                return {}
            price_response = await client.get(f"https://api.jup.ag/price/v2?ids={token_mint_address},So11111111111111111111111111111111111111112&vs_Token=So11111111111111111111111111111111111111112")
            if price_response.status_code == 200:
                price_data = price_response.json()
                price_in_usd = price_data['data'][token_mint_address]['price']
                sol_price = price_data['data']['So11111111111111111111111111111111111111112']['price']
                price_in_sol = float(price_in_usd) / float(sol_price)
                
                data['price_in_usd'] = round(float(price_in_usd), 2)
                data['price_in_sol'] = round(float(price_in_sol), 6)

                print(data, "final data after price")
                return data
            else:
                return {}
            

            
    @staticmethod
    def convert_price_to_string(price):
        # Price is a float number, convert it to a string
        price_str = "{:.10f}".format(price).rstrip('0')
        
        # Find the position of the dot
        dot_position = price_str.find('.')
        zero_count = 0
        for char in price_str[dot_position+1:]:
            if char == '0':
                zero_count += 1
            else:
                break
        
        # If there are more than 2 continuous zeros, convert them to a placeholder
        if zero_count > 2:
            # Convert the price to a string with a placeholder
            converted_price = price_str[:dot_position+2] + "{" + str(zero_count-1) + "}" + price_str[dot_position+1+zero_count:]
        else:
            # Convert the price to a string without a placeholder
            converted_price = price_str
        
        return converted_price
    
    @staticmethod
    def convert_volume_to_string(volume):
        # Covert volume to a string
        if volume > 1000000000:
            volume_str = "{:.2f}".format(volume/1000000000) + "B"
        elif volume > 1000000:
            volume_str = "{:.2f}".format(volume/1000000) + "M"
        else:
            volume_str = "{:.2f}".format(volume/1000) + "K"
        
        return volume_str
    