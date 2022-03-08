from cfg import CLIENT_ID, CLIENT_SECRET, SPOTIPY_REDIRECT_URI, DB_CONNSTR
import spotipy
from spotipy.Oauth import SpotifyOAuth
from datetime import datetime, timedelta
from spoty_etl.models import TABLENAME, TAB
import pandas as pandas
from sqlalchemy import create_engine

scope = "user-read-recently-played" #Dame tu ultima playlist escuchada


#Para conectarse a spotify:

sp = spotipy.Spotify(auth_manager=SpotifyOAuth( client_id=CLIENT_ID,
                                                client_secret=CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                scope=scope)) #permiso para ver la playlist


def extract(date, limit=50):

    """Traer elementos limitados de la playlist


    args:
        ds(datetime): date to query
        limit (int): limite del elemento a consultar
    """
    ds = int(date.timestamp()) * 1000 #transformo a formato unix
    return sp.current_user_recently_played(limit=limit, after=ds)

def transform(raw_data, date):
    data = []
    for r in raw_data["items"]:
        data.append(
            {
                "played_at": r["played_at"],
                "artist": r["track"]["artists"][0]["name"],
                "track": r["track"]["name"]
            }
        )
    df = pd.DataFrame(data)

    # filtrar fechas que quiero que se muestren
    clean_df = df[pd.to_datetime(df["played_at"]).dt.date == date.date()]

    # validacion de que no se este escuchando mas de un elemento a la vez
    if not df["played_at"].is_unique:
        raise Exception("A value from played_at is not unique")

    if df.isnull().values.any():
        raise Exception("A value in df is null")

    return clean_df

def load(df):
    print(f'Uploading {df.shape[0]} to pg')
    engine = create_engine(DB_CONNSTR)
    #metodo to_sql a un postgresql
    df.to_sql(TABLENAME, con=engine, index=False, if_exists='append')



if __name__ == "__main__":
    date = datetime.today() - timedelta(days=1)

    #extract
    data_raw = extract(date)
    print(f"Extracted {(data_raw['items'])} registers")

    #transform
    clean_df = transform(data_raw, date)
    print(f'{clean_df.shape[0]} registers after transform')

    #load
    load(clean_df)
    print("Done")