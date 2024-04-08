# import sys
# import math
# import random
# import yfinance as yf
# from datetime import date, timedelta

# # import json

# # Get the input parameters from the command line arguments
# h = 101  # int(sys.argv[1])
# d = 10000  # int(sys.argv[2])
# t = "sell"  # sys.argv[3]
# p = 7  # int(sys.argv[4])

# # h = int(sys.argv[1])
# # d = int(sys.argv[2])
# # t = sys.argv[3]
# # p = int(sys.argv[4])


# # Initialize the results
# # results = {"var95": [], "var99": [], "profit_loss": []}


# # Get stock data from Yahoo Finance
# def risk_analysis(h, d, t, p):
#     # Get stock data from Yahoo Finance

#     today = date.today()
#     timePast = today - timedelta(days=h)
#     data = yf.download("NVDA", start=timePast, end=today)
#     results = {"var95": [], "var99": [], "profit_loss": []}

#     # Convert the data to a list of lists
#     data_list = [list(row) for row in data.values]

#     count = 0

#     # Perform the risk analysis for each signal
#     for i in range(2, len(data_list)):
#         body = 0.01
#         # Three Soldiers
#         if (
#             (data_list[i][3] - data_list[i][0]) >= body
#             and data_list[i][3] > data_list[i - 1][3]
#             and (data_list[i - 1][3] - data_list[i - 1][0]) >= body
#             and data_list[i - 1][3] > data_list[i - 2][3]
#             and (data_list[i - 2][3] - data_list[i - 2][0]) >= body
#         ):
#             signal = 1
#         # Three Crows
#         elif (
#             (data_list[i][0] - data_list[i][3]) >= body
#             and data_list[i][3] < data_list[i - 1][3]
#             and (data_list[i - 1][0] - data_list[i - 1][3]) >= body
#             and data_list[i - 1][3] < data_list[i - 2][3]
#             and (data_list[i - 2][0] - data_list[i - 2][3]) >= body
#         ):
#             signal = -1
#         else:
#             signal = 0

#         if (signal == 1 and t == "buy") or (signal == -1 and t == "sell"):
#             # Generate d simulated returns
#             mean = sum([row[3] for row in data_list[i - h : i]]) / h
#             std = math.sqrt(
#                 sum([(row[3] - mean) ** 2 for row in data_list[i - h : i]]) / h
#             )
#             simulated = [random.gauss(mean, std) for _ in range(d)]
#             # print(simulated)

#             # Calculate the 95% and 99% VaR
#             simulated.sort(reverse=True)
#             var95 = simulated[int(len(simulated) * 0.95)]
#             var99 = simulated[int(len(simulated) * 0.99)]
#             count += 1
#             results["var95"].append(var95)
#             results["var99"].append(var99)

#             # Calculate the profit or loss
#             if i + p < len(data_list):
#                 if t == "buy":
#                     profit_loss = data_list[i + p][3] - data_list[i][3]
#                 else:  # t == "sell"
#                     profit_loss = data_list[i][3] - data_list[i + p][3]
#                 results["profit_loss"].append(profit_loss)
#     # return json.dumps(results)
#     return results


# # Output the results as JSON
# # print(risk_analysis(h, d, t, p))
# # print(json.dumps(results))
