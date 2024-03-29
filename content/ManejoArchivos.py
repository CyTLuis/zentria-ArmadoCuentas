# ===========================================================================
# Importaciones de clases y librerias necesarias en este archivo main
# ===========================================================================
# Region -  Importaciones de archivos o librerias
from typing import Dict, List
from pypdf import PdfWriter, PdfReader
from shutil import copytree, copy2, move
from os import listdir, path, rename, remove, system

from controller.Log import Log
from controller.Impresor import Impresor
from controller.utils.Configurations import Configurations
# Endregion - Importaciones de archivos o librerias

# ===========================================================================
# VARIABLES GLOBALES - LOCALES - INICIALIZACION DE OBJETOS
# ===========================================================================

# Region - Instancia de clases de archivos importado
logger = Log()
consola = Impresor()
config= Configurations()
# Endregion - Instancia de clases de archivos importado

class ManejoArchivos:
    """
        ManejoArchivos
        ======= 
        La clase ManejoArchivos solo se encargará de gestionar los
        parametros para el renombre y movimiento de los archivos
        que pertenecen a la entidad Nueva EPS.
    """
    
    def __init__(self):
        """
        Metodo constructor de la clase ManejoArchivos.
        - `Descripción de variables:`
            - `public` dataNomenclatura (str) : Almacenado del JSON de la nomenclatura de renombre.
            - `private` __nitEntidad (str): NIT de la entidad desde el archivo de configuración.
            - `private` __rutaArmado (str): Ruta de la carpeta donde se crea el armado.
            - `private` __pacientesConErrores (list): Lista de cuentas que tuvieron errores.
            - `private` __pacientesSinSoportes (list): Lista de cuentas que no tienen archivos en su carpeta.
            - `private` __pacientesSinFacturas (list): Listado de pacientes que no tienen archivo tipo Factura de la cuenta.
            - `public` soportes (Dict|List) : Dict de listas de archivos con tratamiento de unión de archivos.
        """
        self.dataNomenclatura = ""
        self.__nitEntidad = config.getConfigValue("variables", "entidadNIT")
        self.__rutaArmado = config.getConfigValue("variables", "pathCarpetaArmados")

        self.__pacientesConErrores = []
        self.__pacientesSinSoportes = []
        self.__pacientesSinFacturas = []

        self.soportes: Dict[str, List[str]] = {
            "PDX": [],
            "HAM": [],
            "HAU": [],
            "OPF": [],
            "HUV": [],
            "TRIAGE": []
        }
    
    def copiadoSop(self, ruta: str, cuenta: str, eps: str):
        """
        Este metodo se encarga de copiar todos los archivos
        encontrados en la carpeta de la ruta dada, y dejarlos
        en la misma carpeta del folder de Soportes
        - `Args:`
            - `ruta:` (str) Ruta de la carpeta de la factura en Soportes Descargados.
            - `cuenta:` (str) Cuenta o factura que se esta iterando y se copiarán sus archivos.
            - `eps:` (str) Abreviatura de la EPS que se esta haciendo el renombre.
        """
        try:
            rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta) # Se busca la cuenta en la carpeta de soportes descargados.
            if(path.isdir(ruta) == False or len(listdir(ruta)) == 0): # En caso de no existir o no tener soportes, se reportará
                self.__pacientesSinSoportes(cuenta) # Si la cuenta no existe, se reporta en las cuentas sin soportes
                consola.imprimirWarnColor(f"Cuenta: {cuenta}" f"La cuenta no tiene archivos para copiar, o no existe en la carpeta de descargas.")
            else:
                copytree(ruta, rutaCarpetaPacienteArmado, dirs_exist_ok = True) # Copia del arbol completo de la carpeta de soportes, a la de armado
                consola.imprimirComentario("copiadoSop", f"Se ha hecho el copiado del arbol para la cuenta: {cuenta}, con {len(listdir(ruta))} datos de carpetas.")
        except Exception as e:
            consola.imprimirErrorColor(f"Cuenta: {cuenta}", f"Error en la cuenta: {cuenta}, en el copiado del arbol, con error: {e}")
            logger.registrarLogEror(f"Error reportado en el armado de cuentas, y copia de archivos, error: {e}", "copiadoSoportes")

    def copiadoFactura(self, ruta: str, rutaSecundaria: str, cuenta: str, eps: str):
        """
        Este metodo se encargará de que en cada iteración en
        que sea llamado, busque la factura de la cuenta en
        PDF y la copie a la ruta de armado de cuenta.
        - `Args:`
            - `ruta` (str): Ruta contenedora de las cuentas de facturas
            - `rutaSecundaria` (str): Otra posible ruta contenedora de facturas.
            - `cuenta` (str): Cuenta que se esta iterando
            - `eps` (str): EPS que se esta tratando.
        """
        try:
            rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta) # Ruta en la carpeta de cuentas armadas, por paciente
            rutaFacturaPaciente = path.join(ruta, f"{cuenta}.pdf") # Ruta total donde se descargo la factura del paciente.
            rutaFacturaPacienteSecundaria = path.join(rutaSecundaria, f"{cuenta}.pdf") # Ruta de facturas con fecha anterior.
            if(path.isfile(rutaFacturaPaciente) == False and path.isfile(rutaFacturaPacienteSecundaria) == False): # Valida si existe la factura correctamente.
                consola.imprimirWarnColor(f"Cuenta: {cuenta}", f"No se ha encontrado la FACTURA para la cuenta.")
                self.__pacientesSinFacturas.append(cuenta)
                return
            try:
                copy2(rutaFacturaPaciente, rutaCarpetaPacienteArmado) # Copia la factura de donde se descargo, a la ruta del armado.
                consola.imprimirComentario(f"Cuenta: {cuenta}", f"La factura se ha copiado de la ruta: Facturas de hoy.")
            except Exception as e:
                copy2(rutaFacturaPacienteSecundaria, rutaCarpetaPacienteArmado) # Copia la factura de la 2 opción, a la ruta del armado.
                consola.imprimirComentario(f"Cuenta: {cuenta}", f"La factura se ha copiado de la ruta: Facturas con fecha de ayer.")
            rutaFacturaCopiada = path.join(rutaCarpetaPacienteArmado, f"{cuenta}.pdf") # Ruta de la factura copiada en la carpeta del armado.
            cuenta = cuenta.replace("CASM-", "CASM") # Reemplazo para renombre de la factura
            strNomenSoporte = self.dataNomenclatura["renombreFactura"] # Nomenclatura para renombre de factura.
            strRenombreFactura = strNomenSoporte.replace("$soporte", "FVS").replace("$nit", self.__nitEntidad).replace("$factura", cuenta) # Formateo de str de nuevo nombre
            rename(rutaFacturaCopiada, path.join(rutaCarpetaPacienteArmado, strRenombreFactura))
            consola.imprimirComentario(f"Cuenta: [{cuenta}]", f"Se ha RENOMBRADO correctamente la factura de la cuenta: {cuenta}")
        except Exception as e:
            self.__pacientesSinFacturas.append(cuenta)
            consola.imprimirErrorColor(f"Tratado factura - Cuenta: {cuenta}", f"Imposible hacer el tratado de la factura, error: {e}")
            logger.registrarLogEror(f"Fallo con factura de cuenta: {cuenta}, para copiar o renombrar la factura, error: {e}", "copiadoSoportes")
    
    def _manejarError(self, error: Exception, cuenta: str, tipoSoporte: str):
        consola.imprimirErrorColor(f"Archivos Cargue de Archivos - Cuenta: {cuenta}", f"Error reportado desde la unión de los archivos {tipoSoporte}, con error: {error}")
        logger.registrarLogEror(f"Error haciendo el tratado de soporte de tipo [{tipoSoporte}] de la cuenta: {cuenta}, error: {error}", "renombrarArchivos")

    def validarSoportesTratadoDiferente(self, soporte: str, rutaCarpPacArmado: str, cuenta: str, momento: int, strNombreSoporte: str = None):
        """
        En caso de tener soportes que se unan desde el inicio del
        proceso, se deberán identificar y ordenar en una lista
        para hacer su tratado.
        - `Args:`
            - `soporte (str)`: Nombre del soporte
            - `rutaCarpPacArmado (str)`: Ruta del soporte completo.
            - `cuenta (str)`: Cuenta o factura que se esta armando.
            - `momento (int)`: Identificador del momento del metodo.
            - `strNombreSoporte (str)`: Variable de renombre desde el JSON para soporte.
        """
        if momento == 1:
            if "PDX" in soporte or "PDX50" in soporte:
                self.soportes["PDX"].append(path.join(rutaCarpPacArmado, soporte))
            elif "HAM" in soporte:
                self.soportes["HAM"].append(path.join(rutaCarpPacArmado, soporte))
            elif "HAU" in soporte:
                self.soportes["HAU"].append(path.join(rutaCarpPacArmado, soporte))
            elif "OPF" in soporte:
                self.soportes["OPF"].append(path.join(rutaCarpPacArmado, soporte))
            elif "HUV" in soporte:
                self.soportes["HUV"].append(path.join(rutaCarpPacArmado, soporte))
            elif "TRIAGE" in soporte:
                self.soportes["TRIAGE"].append(path.join(rutaCarpPacArmado, soporte))
        elif momento == 2:
            try:
                if len(self.soportes["PDX"]) > 0:
                    consola.imprimirComentario("validarSoportesTratadoDiferente", f"PDX - Encontró ({len(self.soportes["PDX"])}) PDX, que procederá a unir en uno solo.")
                    self.unirArchivos(self.soportes["PDX"], rutaCarpPacArmado, "PDX")
                    strRenombreSoporte = strNombreSoporte.replace("$soporte", "PDX").replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                    nombrePDX = "PDX.pdf" if path.isfile(path.join(rutaCarpPacArmado, "PDX.pdf")) else "PDX50.pdf"
                    rename(path.join(rutaCarpPacArmado, nombrePDX), path.join(rutaCarpPacArmado, strRenombreSoporte))
            except Exception as e:
                self._manejarError(e, cuenta, "PDX")
            try:
                if len(self.soportes["HAM"]) > 0:
                    consola.imprimirComentario("validarSoportesTratadoDiferente", f"HAM - Encontró ({len(self.soportes["HAM"])}) HAM, que procederá a unir en uno solo.")
                    self.unirArchivos(self.soportes["HAM"], rutaCarpPacArmado, "HAM")
                    nombreHAM = strNombreSoporte.replace("$soporte", "HAM").replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                    rename(path.join(rutaCarpPacArmado, "HAM.pdf"), path.join(rutaCarpPacArmado, nombreHAM))
            except Exception as e:
                self._manejarError(e, cuenta, "HAM")
            try:
                if len(self.soportes["OPF"]) > 0:
                    consola.imprimirComentario("validarSoportesTratadoDiferente", f"OPF - Encontró ({len(self.soportes["OPF"])}) OPF, que procederá a unir en uno solo.")
                    self.unirArchivos(reversed(self.soportes["OPF"]), rutaCarpPacArmado, "OPF")
                    nombreOPF = strNombreSoporte.replace("$soporte", "OPF").replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                    rename(path.join(rutaCarpPacArmado, "OPF.pdf"), path.join(rutaCarpPacArmado, nombreOPF))
            except Exception as e:
                self._manejarError(e, cuenta, "OPF")
            try:
                if len(self.soportes["HUV"]) > 0:
                    consola.imprimirComentario("validarSoportesTratadoDiferente", f"HUV - Encontró ({len(self.soportes["HUV"])}) HUV, que procederá a unir en uno solo.")
                    self.unirArchivos(self.soportes["HUV"], rutaCarpPacArmado, "HUV")
                    nombreHUV = strNombreSoporte.replace("$soporte", "HUV").replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                    rename(path.join(rutaCarpPacArmado, "HUV.pdf"), path.join(rutaCarpPacArmado, nombreHUV))
            except Exception as e:
                self._manejarError(e, cuenta, "HUV")
            try:
                if len(self.soportes["HAU"]) > 0 or len(self.soportes["TRIAGE"]) > 0:
                    consola.imprimirComentario("validarSoportesTratadoDiferente", f"HAU - Encontró ({len(self.soportes["HAU"])}) HAU, y buscará si existen TRIAGES.")
                    if len(self.soportes["TRIAGE"]) > 0:
                        consola.imprimirComentario("validarSoportesTratadoDiferente", f"TRIAGE - Encontró ({len(self.soportes["TRIAGE"])}) TRIAGE, para unir con los HAU.")
                        self.soportes["HAU"].insert(0, self.soportes["TRIAGE"][0])
                    self.unirArchivos(self.soportes["HAU"], rutaCarpPacArmado, "HAU")
                    strRenombreSoporte = strNombreSoporte.replace("$soporte", "HAU").replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                    rename(path.join(rutaCarpPacArmado, "HAU.pdf"), path.join(rutaCarpPacArmado, strRenombreSoporte))
            except Exception as e:
                self._manejarError(e, cuenta, "HAU")

    def renombrarArchivos(self, eps: str, cuenta: str):
        """
        Este metodo se encargará de recorrer la lista de
        los archivos de la cuenta que se obtiene, para hacer
        el tratado de los mismos, sea solo renombrar, o unirlos.
        - `Argumentos:`
            - `eps:` (str) Abreviatura de la EPS que se esta procesando.
            - `cuenta:` (str) Cuenta o factura que se esta iterando y se hará renombre de archivos.
        """
        self.soportes["PDX"].clear(), self.soportes["HAM"].clear(), self.soportes["HAU"].clear(), self.soportes["OPF"].clear(), self.soportes["HUV"].clear(), self.soportes["TRIAGE"].clear()
        rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta)
        cuenta = cuenta.replace("CASM-", "CASM")
        strNomenSoporte = self.dataNomenclatura["renombreSoporte"]
        try:
            if(len(listdir(rutaCarpetaPacienteArmado)) > 0): # Si hay archivos en la carpeta, se inicia proceso
                consola.imprimirComentario("renombrarArchivos", f"Inicio de renombrado para la cuenta: {cuenta}, que cuenta con ({len(listdir(rutaCarpetaPacienteArmado))}) archivos.")
                for soporte in listdir(rutaCarpetaPacienteArmado):
                    try: # Primero se valida los soportes de tratado especial.
                        if any(subcadena in soporte for subcadena in ["PDX", "PDX50", "HAM", "HAU", "TRIAGE", "OPF", "HUV"]):
                            self.validarSoportesTratadoDiferente(soporte, rutaCarpetaPacienteArmado, cuenta, 1)
                        else:
                            soporteRecorrido = path.splitext(soporte)
                            nombreSoporte = soporteRecorrido[0] if "Admision" not in soporteRecorrido[0] else "CRC" # En caso de ser admisión se llamará CRC
                            strRenombreSoporte = strNomenSoporte.replace("$soporte", nombreSoporte).replace("$nit", self.__nitEntidad).replace("$factura", cuenta)
                            if(path.isfile(path.join(rutaCarpetaPacienteArmado, soporte))):
                                rename(path.join(rutaCarpetaPacienteArmado, soporte), path.join(rutaCarpetaPacienteArmado, strRenombreSoporte))
                                consola.imprimirComentario("renombrarArchivos", f"Se ha hecho el renombrado correcto del archivo: {soporte}, ahora es: {strRenombreSoporte}.")
                                if(path.isfile(path.join(rutaCarpetaPacienteArmado, soporte))):
                                    remove(path.join(rutaCarpetaPacienteArmado, soporte))
                                    consola.imprimirComentario("renombrarArchivos", f"Se finaliza removiendo el soporte: {soporte} de la cuenta de la carpeta, SOLO EN CASO DE EXISTIR.")
                    except Exception as e:
                        consola.imprimirErrorColor(f"Renombre archivos - Cuenta: {cuenta}", f"Se ha generado un fallo renombrado los archivos, error: {e}")
                        logger.registrarLogEror(f"Error en el renombre del soporte: {soporte} de la cuenta: {cuenta}, error: {e}", "renombrarArchivos")
                self.validarSoportesTratadoDiferente(soporte, rutaCarpetaPacienteArmado, cuenta, 2, strNomenSoporte)
            else:
                self.__pacientesSinSoportes.append(cuenta)
        except Exception as e:
            self.__pacientesConErrores.append(cuenta)
    
    def tratadoArchivosCargueSoportes(self, eps: str, cuenta: str):
        """
        Este metodo se encargará de tratar aquellos archivos que
        están dentro de la carpeta, cargue de soportes.

        Se validará el nombre de los archivos contra unos listados
        definidos, pertenecientes a un tipo de soporte, de tal forma
        que se pueda unir los archivos en uno solo.
        """
        exito = False
        try:
            rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta)
            rutaCarpetaPacienteCargue = path.join(rutaCarpetaPacienteArmado, "Cargue de Archivos")
            if(path.isdir(rutaCarpetaPacienteCargue)):
                consola.imprimirInfoColor(f"Tratado Cargue de Archivos - Cuenta: {cuenta}", f"Se iniciará el tratado de los archivos de la carpeta Cargue de Archivos.")
                archivosCargados = listdir(rutaCarpetaPacienteCargue)
                listadoPDE = [], listadoTAP = [], listadoPDX = []
                for cargue in archivosCargados:
                    rutaSoporteCargue = path.join(rutaCarpetaPacienteCargue, cargue)
                    if any(subcadena in cargue for subcadena in ["AUTO", "SOPORTES CIRUGIA", "DOCUMENTO DE I", "DE DERECHOS", "PDX", "PDXCA", "COTIZACIONES", "VIRAL"]):
                        listadoPDE.append(rutaSoporteCargue)
                    if any(subcadena in cargue for subcadena in ["TRASLADO"]):
                        listadoTAP.append(rutaSoporteCargue)
                    if any(subcadena in cargue for subcadena in ["ELECTRO", "AYUDAS", "CARDIO"]):
                        listadoPDX.append(rutaSoporteCargue)
                    
                if(len(listadoPDE) > 0):
                    consola.imprimirComentario("tratadoArchivosCargueSoportes", f"PDE - Se encontraron ({len(listadoPDE)}) archivos de PDE, de la cuenta: {cuenta}, en la carpeta de cargue de archivos.")
                    self.unirArchivos(listadoPDE, rutaCarpetaPacienteCargue, "PDE")
                    if(path.isfile(path.join(rutaCarpetaPacienteArmado, "PDE.pdf"))):
                        listaMultiplesPDE = [path.join(rutaCarpetaPacienteCargue, "PDE.pdf"), path.join(rutaCarpetaPacienteArmado, "PDE.pdf")]
                        self.unirArchivos(listaMultiplesPDE, rutaCarpetaPacienteCargue, "PDE")
                    move(path.join(rutaCarpetaPacienteCargue, "PDE.pdf"), path.join(rutaCarpetaPacienteArmado, "PDE.pdf"))

                if(len(listadoTAP) > 0):
                    consola.imprimirComentario("tratadoArchivosCargueSoportes", f"TAP - Se encontraron ({len(listadoTAP)}) archivos de TAP, de la cuenta: {cuenta}, en la carpeta de cargue de archivos.")
                    self.unirArchivos(listadoTAP, rutaCarpetaPacienteCargue, "TAP")
                    move(path.join(rutaCarpetaPacienteCargue, "TAP.pdf"), path.join(rutaCarpetaPacienteArmado, "TAP.pdf"))

                if(len(listadoPDX) > 0):
                    consola.imprimirComentario("tratadoArchivosCargueSoportes", f"PDX - Se encontraron ({len(listadoPDX)}) archivos de PDX, de la cuenta: {cuenta}, en la carpeta de cargue de archivos.")
                    self.unirArchivos(listadoPDX, rutaCarpetaPacienteCargue, "PDX")
                    move(path.join(rutaCarpetaPacienteCargue, "PDX.pdf"), path.join(rutaCarpetaPacienteArmado, "PDX50.pdf"))
                exito = True
        except Exception as e:
            consola.imprimirErrorColor(f"Tratado Cargue de Archivos - Cuenta: {cuenta}", f"Falló el tratado de cargue de archivos, error: {e}")
        finally:
            return exito

    def unirArchivos(self, listadoSoportesUnir: list, rutaCarpetaGuardar: str, soporte: str):
        """
        A través de la libreria `pypdf` se hará la unión
        de los PDF, que se encuentran en una lista de rutas
        donde cada ruta representa un PDF distinto, se deberá
        validar cada PDF antes de intentar hacer la unión con
        los demás, buscando así, en caso de que el PDF sea invalido.
        - `Args:`
            - `listadoSoportesUnir (list):` Listado de rutas de PDFs.
            - `rutaCarpetaGuardar (str):` Ruta donde guardar el PDF resultante.
            - `soporte (str):` Nombre con el cual guardar el PDF.
        """
        try:
            merger = PdfWriter() # Se instancia el escritor de PDF
            for pdf in listadoSoportesUnir:
                try:
                    with open(pdf, 'rb') as file: # Se intenta leer el archivo
                        reader = PdfReader(file) # Se lee el archivo PDF
                        _ = reader.numPages # Si el archivo es leído, no es corrupto, y podrá ser procesado.
                    merger.append(pdf) # Se agrega cada full path al merger.
                    remove(pdf) # Se elimina el PDF de la ruta
                except Exception as e:
                    consola.imprimirWarnColor("Archivo PDF corrupto", f"El archivo en la ruta: {pdf}, está corrupto, y no será procesado para el archivo: {soporte}")
                    next # Si el archivo es corrupto, se mostrará en consola, y se pasará al siguiente archivo.
            merger.write(f"{rutaCarpetaGuardar}\\{soporte}.pdf") # Se unen todos los PDF en uno
            merger.close() # Se cierra la instancia del escritor.
        except Exception as e:
            consola.imprimirErrorColor("Falló en unión de archivos.", f"No ha podido hacer la unión del soporte: [{soporte}], con error: {e}")
    
    def moverSegunRegimen(self, eps: str, regimen: str, cuenta: str):
        """
        Este metodo será el final del tratado de la cuenta
        pues se encargará de mover la carpeta de armado, a
        la carpeta perteneciente al regimen que trae asignado.
        `Args:`
            `regimen (str):` Regimen de la cuenta que se esta iterando
            `cuenta (str):` Cuenta que se itera
        """
        exito = False
        try:
            rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, cuenta)
            rutaCarpetaPacientePorRegimen = path.join(self.__rutaArmado, eps, regimen, cuenta)
            move(rutaCarpetaPacienteArmado, rutaCarpetaPacientePorRegimen)
            exito = True
        except Exception as e:
            consola.imprimirError(f"Error en mover la carpeta según su regimen, error: {e}")
        finally:
            return exito

    def controlFinal(self):
        """
        Este metodo se encargará de gestionar los datos
        de las listas que se tienen con datos erroneos,
        o sin soportes, o que han sido erroneos.
        """
        logger.registrarComentario("Pacientes sin facturas", f"{self.__pacientesSinFacturas}")
        consola.imprimirInfoColor("Pacientes sin facturas", f"{self.__pacientesSinFacturas}")

        logger.registrarComentario("Pacientes sin soportes", f"{self.__pacientesSinSoportes}")
        consola.imprimirInfoColor("Pacientes sin soportes", f"{self.__pacientesSinSoportes}")
        
        logger.registrarComentario("Pacientes con errores", f"{self.__pacientesConErrores}")
        consola.imprimirInfoColor("Pacientes con errores", f"{self.__pacientesConErrores}")

    def renombrarPDEconOTRO(self, eps: str, regimen: str, cuenta: str, archivoNombreInicial: str, nombreFinal: str):
        """
        ! Este metodo es TEMPORAL a fecha (18/03/2024) 
        Valida si en la cuenta armada, existe el archivo llamado
        con el archivoNombreInicial, y lo renombra por el nombreFinal.
        `Args:`
            `eps (str):` EPS que se esta armando.
            `regimen (str):` Regimen de la cuenta que se esta armando
            `cuenta (str):` Cuenta que se ha armado.
            `archivoNombreInicial (str):` Nombre o contenido del nombre inicialmente.
            `nombreFinal (str):` Nombre nuevo que se estaría por mostrar.
        """
        try:
            rutaCarpetaPacienteArmado = path.join(self.__rutaArmado, eps, regimen, cuenta)
            cuenta = cuenta.replace("CASM-", "CASM")
            nombreArchivo = f"{archivoNombreInicial}_{self.__nitEntidad}_{cuenta}.pdf"
            replaceArchivo = nombreArchivo.replace(archivoNombreInicial, nombreFinal)
            nombreArchivoFinal = path.join(rutaCarpetaPacienteArmado, replaceArchivo)
            if(path.isfile(path.join(rutaCarpetaPacienteArmado, nombreArchivo))):
                rename(path.join(rutaCarpetaPacienteArmado, nombreArchivo), nombreArchivoFinal)
                try:
                    remove(path.join(rutaCarpetaPacienteArmado, nombreArchivo))
                except Exception as e:
                    pass
        except Exception as e:
            logger.registrarLogEror(f"Ocurrió un error tratando de renombrar el archivo: {archivoNombreInicial} de la cuenta: {cuenta}, error: {e}", "renombrarPDEconOTRO")
            consola.imprimirError(f"Ocurrió un error tratando de renombrar el archivo: {archivoNombreInicial} de la cuenta: {cuenta}, error: {e}")
