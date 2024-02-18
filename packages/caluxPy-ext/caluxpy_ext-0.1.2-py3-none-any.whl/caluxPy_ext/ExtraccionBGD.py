import os, pandas as pd, datetime

class ExtraccionBGD():

    rutas = []
    def __init__(self, estructura, division, mes, año, listado_cuentas, dias, mensuales, columnas, subsector, line_thresh, cwd) -> None:
        
        #Definición de las Variables de la Instancia
        self.estructura = estructura
        self.division = division
        self.mes = mes
        self.año = año
        self.listado_cuentas = listado_cuentas
        self.dias = dias
        self.mensuales = mensuales
        self.columnas = columnas
        self.subsector = subsector
        self.terminal = ['.xlsm', '.xlsx']
        self.errores = 0
        self.errores_prompt = ''
        self.line_thresh = line_thresh
        self.cwd = cwd

        with open(os.path.join(self.cwd, 'extraccion_log.txt'), 'w') as self._f:
            #Ejecución de las Funciones
            self._ruta, self._validacion = self.crear_ruta(
                                                            division = self.division, 
                                                            estructura = self.estructura,
                                                            subsector = self.subsector, 
                                                            año = self.año, 
                                                            mes = self.mes, 
                                                            terminal = self.terminal
                                                            )
            self.generated_df = self.recoleccion_de_datos(
                                                            ruta = self._ruta, 
                                                            listado_cuentas = self.listado_cuentas, 
                                                            dias = self.dias, 
                                                            mensuales = self.mensuales, 
                                                            columnas = self.columnas, 
                                                            subsector = self.subsector,
                                                            mes = self.mes,
                                                            line_thresh = self.line_thresh
                                                            )
            self.limpiar_data(self.generated_df)

    def crear_ruta(self, division, estructura, subsector, año, mes, terminal):
        terminal_seeker = 0
        ruta = ''
        while True:
            if division == 'Division_Banca_Fomento':
                directorio = estructura['estructura_ruta'].format(
                                                                    division = division, 
                                                                    año = año, 
                                                                    subsector = subsector
                                                                 )
                #Se usa terminal seeker para iterar en opciones
                archivo = estructura['estructura_archivo'].format(
                                                                    subsector = subsector, 
                                                                    mes = mes, 
                                                                    año = año[-2:], 
                                                                    terminal = terminal[terminal_seeker]
                                                                 )
            else: 
                directorio = estructura['estructura_ruta'].format(
                                                                    division = division, 
                                                                    año = año
                                                                 )
                archivo = estructura['estructura_archivo'].format(
                                                                    mes = mes, 
                                                                    año = año[-2:], 
                                                                    terminal = terminal[terminal_seeker]
                                                                 )
            ruta = os.path.join(directorio, archivo)
            validacion = self.verificar_ruta(ruta = ruta)
            if validacion == True:
                break
            else: terminal_seeker += 1
        ExtraccionBGD.rutas.append(ruta)
        return ruta, validacion

    def verificar_ruta(self, ruta):
        if os.path.exists(ruta):
            return True
        else: 
            return False

    def recoleccion_de_datos(self, ruta, listado_cuentas, dias, mensuales, columnas, subsector, mes, line_thresh):
        #Abrir Excel y mantener en memoria
        excel = pd.ExcelFile(ruta) 
        #Llama la función y como se manda el DataFrame entonces se concatena la información al usado
        generated_df = self.generar_df(
                                        excel = excel, 
                                        listado_cuentas = listado_cuentas, 
                                        dias = dias, 
                                        mensuales = mensuales,
                                        columnas = columnas,
                                        subsector = subsector,
                                        mes = mes,
                                        line_thresh = line_thresh
                                      )
        del excel
        return generated_df

    def generar_df(self, excel, listado_cuentas, dias, mensuales, columnas, subsector, mes, line_thresh):
        #Genera una base concatenada de los dias y ese DF generado lo devuelve a recolección de datos
        generated_df = pd.DataFrame()
        self.errores_prompt = []
        for dia in excel.sheet_names:
            if dia in dias or dia in mensuales:
                col = 0
                while True:
                    try:
                        data, tipo_cambio, fecha = self.extraer_data(
                                                                     data = pd.read_excel(
                                                                                            excel, 
                                                                                            sheet_name = dia, 
                                                                                            nrows = line_thresh, usecols = columnas[col]
                                                                                         ), 
                                                                     listado_cuentas = listado_cuentas
                                                                    )
                        data = pd.DataFrame(data)
                        #Agrega columnas de constantes
                        if not data.empty:
                            data['Dia'] = dia
                            data['Mes'] = mes
                            data['Subsector'] = subsector
                            data['Tipo Cambio'] = tipo_cambio
                            data['Fecha'] = fecha
                            data = data[['Dia', 'Mes', 'Fecha', 'Subsector', 'Entidad', 'Cuenta', 'Valor', 'Tipo Cambio']]
                            
                        #Concatena las tablas que se van creando
                        generated_df = pd.concat([generated_df, data])
                        break
                    except pd.errors.ParserError as e:
                        col += 1
                    except KeyError as e:
                        message = f'--Error! -> Falta columna {e} || Día: {dia}'
                        self.errores += 1
                        self.errores_prompt.append(f' {message}')
                        break
        return generated_df

    def extraer_data(self, data, listado_cuentas):
        tipo_cambio = data.iloc[0].iloc[1] #Extracción del tipo de cambio
        fecha = data.iloc[0].index[0]
        hoy = datetime.datetime.now().date()
        entidades = data.iloc[2].to_list() #Extracción del nombre de las entidades
        entidades[0] = 'ENTIDADES' #reemplaza el primer valor por esto
        data.rename(columns = data.iloc[2], inplace = True) #Cambia la primera linea del DataFrame para que los índices por columna sean adecuados

        #Definición de Variables
        valores_data = []
        entidades_data = []
        cuentas_data = []
        datos = {}

        if isinstance(fecha, datetime.datetime):
            fecha = fecha.date()
            if fecha <= hoy:
                #Proceso de creado de listas
                for codigo in listado_cuentas:
                    try:
                        linea = data[data['CODIGOS'] == codigo].values[0].tolist()
                        cuenta = linea[0]
                        for item in linea: #itera sobre las cuentas seleccionadas
                            #if type(item) == int or type(item) == float and not pd.isna(item): #itera por cada componente de la línea y si cumple con las condiciones se agrega
                            if item != codigo and item != cuenta:
                                valores_data.append(item) #Se agrega el valor a los datos
                                cuentas_data.append(f'{cuenta.lstrip(' ').rstrip(' ').title()} ({codigo})') #Se agrega la cuenta por cada dato agregado

                        for entidad in entidades:
                            if entidad != 'ENTIDADES' and entidad != 'CODIGOS': #and not pd.isna(entidad) and entidad != 0:
                                entidades_data.append(entidad)

                        #Verifica que las longitudes cuadren y si no devuelve un error
                        if len(entidades_data) == len(valores_data):
                            datos = {
                                    'Entidad': entidades_data,
                                    'Cuenta': cuentas_data,
                                    'Valor': valores_data
                                    }
                    except Exception as e: #Si no encuentra la cuenta
                        print(f'ERROR! --> Cuenta {cuenta} no encontrada!', file = self._f)
        return datos, tipo_cambio, fecha

    def limpiar_data(self, df):
        df.dropna(inplace = True)

