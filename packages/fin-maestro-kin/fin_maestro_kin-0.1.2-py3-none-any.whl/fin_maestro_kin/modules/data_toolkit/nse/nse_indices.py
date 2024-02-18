from fastapi import APIRouter, HTTPException, Query
import requests
import json
import pandas as pd

router = APIRouter()

niftyindices_headers = {
    'Connection': 'keep-alive',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'DNT': '1',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'Content-Type': 'application/json; charset=UTF-8',
    'Origin': 'https://niftyindices.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://niftyindices.com/reports/historical-data',
    'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
}


def index_history(symbol, start_date, end_date):
    data = "{'name':'" + symbol + "','startDate':'" + start_date + "','endDate':'" + end_date + "'}"
    payload = requests.post('https://niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString', headers=niftyindices_headers,  data=data).json()
    payload = json.loads(payload["d"])
    payload = pd.DataFrame.from_records(payload)
    return payload


#Example usage - 127.0.0.1:8000/niftyindices/history?symbol=NIFTY 50&start_date=10-Jan-2024&end_date=12-Jan-2024
@router.get("/niftyindices/history")
def get_niftyindices_history(
    symbol: str = Query(..., title="Symbol", description="Nifty indices symbol"),
    start_date: str = Query(..., title="Start Date", description="Start date for historical data"),
    end_date: str = Query(..., title="End Date", description="End date for historical data")
):
    try:
        history_data = index_history(symbol, start_date, end_date)
        return history_data.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {e}")
    

def index_pe_pb_div(symbol,start_date,end_date):
    data = "{'name':'"+symbol+"','startDate':'"+start_date+"','endDate':'"+end_date+"'}"
    payload = requests.post('https://niftyindices.com/Backpage.aspx/getpepbHistoricaldataDBtoString', headers=niftyindices_headers,  data=data).json()
    payload = json.loads(payload["d"])
    payload=pd.DataFrame.from_records(payload)
    return payload


#Example usage - #Example usage - 127.0.0.1:8000/niftyindices/ratios?symbol=NIFTY 50&start_date=10-Jan-2024&end_date=12-Jan-2024
@router.get("/niftyindices/ratios")
def get_niftyindices_ratios(
    symbol: str = Query(..., title="Symbol", description="Nifty indices symbol"),
    start_date: str = Query(..., title="Start Date", description="Start date for historical data"),
    end_date: str = Query(..., title="End Date", description="End date for historical data")
):
    try:
        historical_ratios_data = index_pe_pb_div(symbol, start_date, end_date)
        return historical_ratios_data.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical ratios data: {e}")
    

def index_total_returns(symbol,start_date,end_date):
    data = "{'name':'"+symbol+"','startDate':'"+start_date+"','endDate':'"+end_date+"'}"
    payload = requests.post('https://niftyindices.com/Backpage.aspx/getTotalReturnIndexString', headers=niftyindices_headers,  data=data).json()
    payload = json.loads(payload["d"])
    payload=pd.DataFrame.from_records(payload)
    return payload


#Example usage - 127.0.0.1:8000/niftyindices/returns?symbol=NIFTY 50&start_date=10-Jan-2024&end_date=12-Jan-2024
@router.get("/niftyindices/returns")
def get_niftyindices_returns(
    symbol: str = Query(..., title="Symbol", description="Nifty indices symbol"),
    start_date: str = Query(..., title="Start Date", description="Start date for historical data"),
    end_date: str = Query(..., title="End Date", description="End date for historical data")
):
    try:
        historical_returns_data = index_total_returns(symbol, start_date, end_date)
        return historical_returns_data.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical ratios data: {e}")