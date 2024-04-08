# import requests
# import re
# import json


# def get_ec2_price(region_name="us-east-1", instance_type="t2.micro"):
#     url = "https://a0.awsstatic.com/pricing/1/ec2/linux-od.min.js"
#     response = requests.get(url)

#     pattern = re.compile(r"callback\((.*)\);", re.DOTALL)
#     match = pattern.search(response.text)
#     if match:
#         json_text = match.group(1)
#         data = json.loads(json_text)

#         for region in data["config"]["regions"]:
#             if region["region"] == region_name:
#                 for instanceType in region["instanceTypes"]:
#                     for size in instanceType["sizes"]:
#                         if size["size"] == instance_type:
#                             return float(size["valueColumns"][0]["prices"]["USD"])

#     return None


# price = get_ec2_price()
# if price is not None:
#     print(f"The price for t2.micro in us-east-1 is: ${price}")
# else:
#     print("Could not find the price.")
