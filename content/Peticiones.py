import requests as rq
from json import loads
from controller.Log import Log
from controller.Impresor import Impresor
from controller.utils.Helpers import Helpers
from controller.utils.Configurations import Configurations

logger = Log()
helper = Helpers()
consola = Impresor()
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
       
        respuesta = []
        try:
            consola.imprimirProceso("Inicio de proceso para Obtener Listado de Facturas")
            res = rq.get(f"{self.__urlAPI}/{self.__dictEndpoints["obtencionFacturas"]}", timeout = 30)
            respuesta = loads(res.text)
            consola.imprimirProceso(f"Fin del proceso para Obtener Listado de Facturas [({len(respuesta)})]")
        except Exception as e:
            consola.imprimirError(f"Error en el proceso para Obtener Listado de Facturas [{e}]")
            logger.registrarLogEror(f"Error al generar la petición de facturas para armado de cuentas, error: {e}", "obtenerListadoFacturas")
        finally:
            print(respuesta)
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
                json = data,
                timeout = 10
            )
            print(actualizacion.text)
        except Exception as e:
            logger.registrarLogEror(f"No se ha podido actualizar los datos de la cuenta con id: {idFactura}, error: {e}", "actualizarEstadoCuenta")
        finally:
            return exito
    
    def crearAlertaSoporteFaltante(self, soporte: str, cuenta: str):
        """
        Se consumirá en la API un endpoint para generar
        una alerta sobre el soporte faltante de la cuenta
        que se esta recorriendo en el armado.
        """