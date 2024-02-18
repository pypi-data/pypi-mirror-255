from pytdx.tdx import Tdx
import os
from dotenv import load_dotenv
import json

load_dotenv()

conn_info = json.loads(os.getenv("TDX_CONN"))


tdx_client = Tdx(
    username=conn_info[0],
    password=conn_info[1],
    hostname=conn_info[2],
    environment=conn_info[3],
    asset_app_id=conn_info[4],
    client_portal_app_id=conn_info[5],
    ticketing_app_id=conn_info[6],
    is_admin=conn_info[7],
)


print(tdx_client.get_asset(asset_id=1145451))
