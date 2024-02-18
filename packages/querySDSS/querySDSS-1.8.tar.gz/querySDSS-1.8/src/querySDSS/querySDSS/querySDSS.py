from astroquery.exceptions import RemoteServiceError
from astroquery.sdss import SDSS
from requests.exceptions import ConnectionError


# Esse é um módulo Python feito por mim @aCosmicDebbuger
# https://github.com/aCosmicDebugger
# Neste módulo uso o astroquery do astropy para fazer uma query
# dos dados do SDSS (release 17)  contendo a natureza do objeto
# o redshift, declinação e acendência e os fluxos nas bandas u,g,r,i


from astroquery.exceptions import RemoteServiceError
from astroquery.sdss import SDSS
from requests.exceptions import ConnectionError


def query_sdss_data(variables, num_observations):
    try:
        # Construa a consulta com base nas variáveis fornecidas
        query = f"""SELECT TOP {num_observations}
            {', '.join(variables)}
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

    # Informa ao usuário sobre as variáveis disponíveis
    print("Informações sobre as variáveis disponíveis:")
    print("- Objid, Specobjid - Identificadores de Objeto")
    print("- ra - Ascensão Reta J2000")
    print("- dec - Declinação J2000")
    print("- redshift - Redshift Final do objeto celeste")
    print("- u, g, r, i, e z - magnitude ajustada para u, g, r, i e z (correspondem às cinco bandas fotométricas: banda ultravioleta, banda verde, banda vermelha, banda infravermelha e próximo à infravermelha, respectivamente)")
    print("- run - Número de Execução")
    print("- rerun - Número de Repetição")
    print("- camcol - Coluna da Câmera")
    print("- field - Número de Campo")
    print("- extinction_u - Extinção na banda u")
    print("- extinction_g - Extinção na banda g")
    print("- extinction_r - Extinção na banda r")
    print("- extinction_i - Extinção na banda i")
    print("- extinction_z - Extinção na banda z")
    print("- tds - Inclui todas as variáveis")

    # Solicita ao usuário as variáveis e o número de observações
    variable_input = input("Informe as variáveis separadas por vírgulas ou 'tds' para todas as variáveis: ")

    if variable_input.lower() == 'tds':
        variables = ["objid", "specobjid", "ra", "dec", "redshift", "u", "g", "r", "i", "z",
                     "run", "rerun", "camcol", "field", "extinction_u", "extinction_g", "extinction_r",
                     "extinction_i", "extinction_z"]
    else:
        variables = variable_input.split(',')

    num_observations = int(input("Informe o número total de observações a serem solicitadas: "))

    # Query SDSS data
    sdss_data = query_sdss_data(variables, num_observations)

    if sdss_data is not None:
        # Print the retrieved data
        print(sdss_data)
    else:
        print("Error retrieving SDSS data.")

