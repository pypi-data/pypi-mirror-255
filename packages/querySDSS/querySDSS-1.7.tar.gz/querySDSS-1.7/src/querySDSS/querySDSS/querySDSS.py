from astroquery.exceptions import RemoteServiceError
from astroquery.sdss import SDSS
from requests.exceptions import ConnectionError


# Esse é um módulo Python feito por mim @aCosmicDebbuger
# https://github.com/aCosmicDebugger
# Neste módulo uso o astroquery do astropy para fazer uma query
# dos dados do SDSS (release 17)  contendo a natureza do objeto
# o redshift, declinação e acendência e os fluxos nas bandas u,g,r,i


def query_sdss_data():
    try:
        # Query SDSS database and retrieve necessary columns
        query = """SELECT TOP 2500
            p.objid, p.ra, p.dec, p.u, p.g, p.r, p.i, p.z,
            p.run, p.rerun, p.camcol, p.field,
            p.extinction_u, p.extinction_g, p.extinction_r, p.extinction_i, p.extinction_z,
            s.specobjid, s.class, s.z as redshift,
            s.plate, s.mjd, s.fiberid
        FROM PhotoObj AS p
        JOIN SpecObj AS s ON s.bestobjid = p.objid
        WHERE 
            s.z > 0 AND s.zWarning = 0
            AND s.specobjid <> 108
        """

        # Query SDSS database and retrieve data
        result = SDSS.query_sql(query)
        return result
    except RemoteServiceError as e:
        print("Error querying SDSS:", e)
        return None
    except ConnectionError as e:
        print("Connection error:", e)
        return None


if __name__ == "__main__":
    # Query SDSS data
    sdss_data = query_sdss_data()

    if sdss_data is not None:
        # Print the retrieved data
        print(sdss_data)
    else:
        print("Error retrieving SDSS data.")
