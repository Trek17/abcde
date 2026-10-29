import requests
import pandas as pd
import numpy as np
from datetime import datetime
import os

def run_pipeline():
    BASE_URL1 = 'https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream'
    params1 = {
        "publishDateTimeFrom": "2026-01-01T00:00:00Z",
        "publishDateTimeTo": "2026-02-01T23:59:59Z",
        "fuelType": "WIND",
        }
    columns1 =['startTime','generation','settlementDate','settlementPeriod']

    BASE_URL2 = 'https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream'


    params2 = {
        # Include forecasts published on 31 December for 1 January delivery
         "publishDateTimeFrom": "2025-12-31T00:00:00Z",
           "publishDateTimeTo": "2026-01-31T23:59:59Z",
           }
    columns2 =['publishTime','startTime','generation']



    # -- Step 1: Make the request with error handling --
    def fetch_api_data(BASE_URL,params,columns):
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()  # Raises an error for 4xx and 5xx codes
        except requests.exceptions.Timeout:
            print('The request timed out. The server took too long to respond.')
            exit()
        except requests.exceptions.HTTPError as e:
            print(f'HTTP error: {e}')
            exit()
        except requests.exceptions.RequestException as e:
            print(f'Something went wrong: {e}')
            exit()
        data = response.json()
        df = pd.DataFrame(data, columns =columns)
        return df

    df_actual = fetch_api_data(BASE_URL1,params1,columns1)
    df_forecast = fetch_api_data(BASE_URL2,params2,columns2)

    df_actual = df_actual[
    (df_actual['settlementDate'] >= '2026-01-01') &
    (df_actual['settlementDate'] <= '2026-01-31')
]
    # 1. Parse timestamps in UTC
    df_forecast['publishTime'] = pd.to_datetime(
        df_forecast['publishTime'], utc=True
    )
    df_forecast['startTime'] = pd.to_datetime(
        df_forecast['startTime'], utc=True
    )
    df_actual['startTime'] = pd.to_datetime(
        df_actual['startTime'], utc=True
    )

    # 2. Define the assumed bidding deadline:
    # 06:00 UTC on the day before delivery
    df_forecast['target_date'] = df_forecast['startTime'].dt.normalize()
    df_forecast['bidding_deadline'] = (
        df_forecast['target_date']
        - pd.Timedelta(days=1)
        + pd.Timedelta(hours=6)
    )

    # 3. Keep only forecasts published before the deadline
    valid_forecasts = df_forecast[
        df_forecast['publishTime'] <= df_forecast['bidding_deadline']
    ].copy()

    # 4. Select the latest eligible forecast for each delivery hour
    latest_hourly_forecast = (
        valid_forecasts
        .sort_values(['startTime', 'publishTime'])
        .drop_duplicates(subset=['startTime'], keep='last')
        [['startTime', 'publishTime', 'generation']]
        .rename(columns={'generation': 'forecast_gen'})
    )

    # 5. Aggregate half-hourly actuals into hourly averages
    # Keep only hours containing exactly two actual readings
    actual_hourly = (
        df_actual
        .set_index('startTime')
        .resample('1h')
        .agg(
            actual_gen=('generation', 'mean'),
            actual_count=('generation', 'count')
        )
        .reset_index()
    )

    actual_hourly = actual_hourly[
        actual_hourly['actual_count'] == 2
    ].drop(columns='actual_count')
    
    # print("Raw actual start:", df_actual["startTime"].min())
    # print("Raw actual end:", df_actual["startTime"].max())

    # print(
    # actual_hourly[
    #     actual_hourly["startTime"] < "2026-01-03"
    # ].to_string(index=False)
# )
    
    # target = pd.Timestamp("2026-01-31 23:00:00", tz="UTC")

    # print("Actual hourly record:")
    # print(actual_hourly[actual_hourly["startTime"] == target])

    # print("\nEligible forecast record:")
    # print(valid_forecasts[valid_forecasts["startTime"] == target])

    # target = pd.Timestamp("2026-01-31 23:00:00", tz="UTC")

    # print(actual_hourly[actual_hourly["startTime"] == target])

    # target = pd.Timestamp("2026-01-31 23:00:00", tz="UTC")

    # print(
    # df_actual[
    #     (df_actual["startTime"] >= target) &
    #     (df_actual["startTime"] < target + pd.Timedelta(hours=1))
    # ][["startTime", "generation"]]

    # )
    # print(
    # df_actual[
    #     df_actual["startTime"] >= "2026-01-31 23:00:00+00:00"
    # ][["startTime", "generation"]].tail(10))

    # 6. Compare forecasts and actuals for matching hours
    evaluation_df = pd.merge(
        actual_hourly,
        latest_hourly_forecast,
        on='startTime',
        how='inner'
    )
    evaluation_df = evaluation_df[
    (evaluation_df["startTime"] >= "2026-01-01T00:00:00Z")
    & (evaluation_df["startTime"] < "2026-02-01T00:00:00Z")
    ].copy()


    # print(evaluation_df["startTime"].head(5))

    # 7. Calculate forecast errors (actual - forecast)
    evaluation_df['error_mw'] = (
        evaluation_df['actual_gen'] - evaluation_df['forecast_gen']
    )
    evaluation_df['abs_error_mw'] = evaluation_df['error_mw'].abs()

    # 8. Calculate overall accuracy metrics
    mae = evaluation_df['abs_error_mw'].mean()
    rmse = np.sqrt((evaluation_df['error_mw'] ** 2).mean())

    # print(f"Evaluated hours: {len(evaluation_df)}")
    # print(f"MAE: {mae:.2f} MW")
    # print(f"RMSE: {rmse:.2f} MW")

    # 9. Summarise performance by settlement period
    # Use the hourly start time to identify the corresponding settlement period.
    evaluation_df['settlementPeriod'] = (
        evaluation_df['startTime'].dt.hour * 2 + 1
    )

    period_perf = (
        evaluation_df
        .groupby('settlementPeriod')
        .agg(
            Avg_Actual_MW=('actual_gen', 'mean'),
            Avg_Forecast_MW=('forecast_gen', 'mean'),
            Period_MAE_MW=('abs_error_mw', 'mean')
        )
        .reset_index()
    )


#     expected_hours = pd.date_range(
#     "2026-01-01 00:00",
#     "2026-02-01 00:00",
#     freq="1h",
#     inclusive="left",
#     tz="UTC"
# )

#     evaluated_hours = pd.DatetimeIndex(
#         evaluation_df["startTime"].drop_duplicates()
#     )

#     missing_hours = expected_hours.difference(evaluated_hours)

#     print("Missing hours:", missing_hours)

#     print("Evaluated hours:", evaluation_df["startTime"].nunique())
#     print("Expected hours:", len(expected_hours))

    return {
    "summary": {
        "evaluated_hours": int(len(evaluation_df)),
        "mae_mw": round(float(mae), 2),
        "rmse_mw": round(float(rmse), 2)
    },
    "hourly": (
        evaluation_df[
            [
                "startTime",
                "actual_gen",
                "forecast_gen",
                "error_mw"
            ]
        ]
        .assign(
            startTime=lambda df:
                df["startTime"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        .to_dict(orient="records")
    ),
    "period_performance": period_perf.to_dict(orient="records")
    }



# results = run_pipeline()

# df_merged = pd.DataFrame(results["hourly"])

# print(df_merged[df_merged["startTime"] >= "2026-01-31 22:00:00+00:00"])