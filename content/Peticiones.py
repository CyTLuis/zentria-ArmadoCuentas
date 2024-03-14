import requests as rq
from json import loads
from controller.Log import Log
from controller.utils.Helpers import Helpers
from controller.utils.Configurations import Configurations

logger = Log()
helper = Helpers()
config = Configurations()

class Peticiones:
    """
    Peticiones
    ==========
    Esta clase se encargará de realizar las peticiones
    correspondientes a la API de Zentria, de manera
    que pueda obtener la info con la que trabajará el
    armado de cuenta, y a la vez, reportar información
    del mismo armado.
    - `Metodos disponibles:`
        - `obtenerListadoFacturas` -> Dict: Obtención de cuentas para armado.
    """

    def __init__(self) -> None:
        """Contructor de la clase"""

        self.__urlAPI = config.getConfigValue("variables", "urlAPI")
        self.__dictEndpoints = {
            "obtencionFacturas": "postgres/itemsActividadesConSportes",
            "actualizacionEstado": "postgres/actualizarEstadoProceso"
        }
    
    def obtenerListadoFacturas(self):
        """
        Este metodo hará una petición a la API para obtener el
        listado de facturas que se pueden armar su cuenta.
        """
        x = [
                {
                    "id_pdf": 12,
                    "numero_factura": "CASM-484058",
                    "no_atencion": "1005805",
                    "fecha_ingreso": "2023-09-27",
                    "ambito": "Urgencias",
                },
                {
                    "id_pdf": 13,
                    "numero_factura": "CASM-485138",
                    "no_atencion": "878308",
                    "fecha_ingreso": "2023-05-26",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 14,
                    "numero_factura": "CASM-485168",
                    "no_atencion": "879528",
                    "fecha_ingreso": "2023-05-27",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 12,
                    "numero_factura": "CASM-485191",
                    "no_atencion": "1005805",
                    "fecha_ingreso": "2023-09-27",
                    "ambito": "Urgencias",
                },
                {
                    "id_pdf": 13,
                    "numero_factura": "CASM-485198",
                    "no_atencion": "878308",
                    "fecha_ingreso": "2023-05-26",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 14,
                    "numero_factura": "CASM-485203",
                    "no_atencion": "879528",
                    "fecha_ingreso": "2023-05-27",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 12,
                    "numero_factura": "CASM-485214",
                    "no_atencion": "1005805",
                    "fecha_ingreso": "2023-09-27",
                    "ambito": "Urgencias",
                },
                {
                    "id_pdf": 13,
                    "numero_factura": "CASM-485221",
                    "no_atencion": "878308",
                    "fecha_ingreso": "2023-05-26",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 14,
                    "numero_factura": "CASM-485227",
                    "no_atencion": "879528",
                    "fecha_ingreso": "2023-05-27",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 12,
                    "numero_factura": "CASM-485235",
                    "no_atencion": "1005805",
                    "fecha_ingreso": "2023-09-27",
                    "ambito": "Urgencias",
                },
                {
                    "id_pdf": 13,
                    "numero_factura": "CASM-485238",
                    "no_atencion": "878308",
                    "fecha_ingreso": "2023-05-26",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 14,
                    "numero_factura": "CASM-485255",
                    "no_atencion": "879528",
                    "fecha_ingreso": "2023-05-27",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 12,
                    "numero_factura": "CASM-485340",
                    "no_atencion": "1005805",
                    "fecha_ingreso": "2023-09-27",
                    "ambito": "Urgencias",
                },
                {
                    "id_pdf": 13,
                    "numero_factura": "CASM-485370",
                    "no_atencion": "878308",
                    "fecha_ingreso": "2023-05-26",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 14,
                    "numero_factura": "CASM-485396",
                    "no_atencion": "879528",
                    "fecha_ingreso": "2023-05-27",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 12,
                    "numero_factura": "CASM-485404",
                    "no_atencion": "1005805",
                    "fecha_ingreso": "2023-09-27",
                    "ambito": "Urgencias",
                },
                {
                    "id_pdf": 13,
                    "numero_factura": "CASM-485408",
                    "no_atencion": "878308",
                    "fecha_ingreso": "2023-05-26",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 14,
                    "numero_factura": "CASM-485413",
                    "no_atencion": "879528",
                    "fecha_ingreso": "2023-05-27",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 12,
                    "numero_factura": "CASM-485430",
                    "no_atencion": "1005805",
                    "fecha_ingreso": "2023-09-27",
                    "ambito": "Urgencias",
                },
                {
                    "id_pdf": 13,
                    "numero_factura": "CASM-485445",
                    "no_atencion": "878308",
                    "fecha_ingreso": "2023-05-26",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 14,
                    "numero_factura": "CASM-485458",
                    "no_atencion": "879528",
                    "fecha_ingreso": "2023-05-27",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 12,
                    "numero_factura": "CASM-485468",
                    "no_atencion": "1005805",
                    "fecha_ingreso": "2023-09-27",
                    "ambito": "Urgencias",
                },
                {
                    "id_pdf": 13,
                    "numero_factura": "CASM-485473",
                    "no_atencion": "878308",
                    "fecha_ingreso": "2023-05-26",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 14,
                    "numero_factura": "CASM-485494",
                    "no_atencion": "879528",
                    "fecha_ingreso": "2023-05-27",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 12,
                    "numero_factura": "CASM-485503",
                    "no_atencion": "1005805",
                    "fecha_ingreso": "2023-09-27",
                    "ambito": "Urgencias",
                },
                {
                    "id_pdf": 13,
                    "numero_factura": "CASM-485533",
                    "no_atencion": "878308",
                    "fecha_ingreso": "2023-05-26",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 14,
                    "numero_factura": "CASM-485534",
                    "no_atencion": "879528",
                    "fecha_ingreso": "2023-05-27",
                    "ambito": "Apoyo Diagnostico",
                },
                {
                    "id_pdf": 12,
                    "numero_factura": "CASM-485538",
                    "no_atencion": "1005805",
                    "fecha_ingreso": "2023-09-27",
                    "ambito": "Urgencias",
                },
                {
                    "id_pdf": 13,
                    "numero_factura": "CASM-485540",
                    "no_atencion": "878308",
                    "fecha_ingreso": "2023-05-26",
                    "ambito": "Apoyo Diagnostico",
                }
            ]
        return x

        respuesta = []
        try:
            res = rq.get(f"{self.__urlAPI}/{self.__dictEndpoints["obtencionFacturas"]}")
            respuesta = loads(res.text)
        except Exception as e:
            logger.registrarLogEror(f"Error al generar la petición de facturas para armado de cuentas, error: {e}", "obtenerListadoFacturas")
        finally:
            return respuesta
    
    def actualizarEstadoCuenta(self, idFactura: int, estado: str):
        """
        Actualización del estado de la factura en la tabla de items_facturas
        a su nuevo estado, según culminación de proceso x factura.
        - `Args:`
            - idFactura (int): Id de la factura en la tabla.
            - estado (str): Estado que se le asignará.
        """
        exito = False
        try:
            data = {
                "id_pdf_factura": idFactura,
                "estado_proceso": estado
            }
            actualizacion = rq.post(
                f"{self.__urlAPI}/{self.__dictEndpoints["actualizacionEstado"]}",
                json = data
            )
            print(actualizacion.text)
        except Exception as e:
            logger.registrarLogEror(f"No se ha podido actualizar los datos de la cuenta con id: {idFactura}, error: {e}", "actualizarEstadoCuenta")
        finally:
            return exito