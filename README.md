## Master's project
### Midterm price prediction for S&P 500 stocks

The work is focused on the problem of predicting the price of shares in the period from one to seven days. Data pool includes stocks that are in the S&P 500 index, as well as the dynamics of the index itself.
Stock prices refer to time series data where the sequence of values is important. Special mechanisms and models are used to process and predict data of this type. The paper presents a study of time series models, classical machine learning models and neural networks. Depending on the algorithm used, different preprocessing methods are used: price scaling, categorical variable coding, additional feature creation, and sequence transformation using sliding windows. The metrics RMSE, MAE, MAPE are used to measure the quality of the forecast.
Based on the considered algorithms, the Telegram bot was developed, which sends the user upon request a graph of the dynamics or forecast of stock prices for the week ahead.
