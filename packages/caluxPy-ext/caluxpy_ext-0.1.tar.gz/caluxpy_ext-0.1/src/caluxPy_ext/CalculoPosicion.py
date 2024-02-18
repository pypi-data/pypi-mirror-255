import os, pandas as pd, datetime, logging
class CalculoPosicion:

    def __init__(self, df, include, type) -> None:

        logFormatter = logging.Formatter("%(asctime)s: [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        fileHandler = logging.FileHandler("{0}/{1}.log".format(os.getcwd(), 'posicion'), mode = 'w', encoding = 'utf-8')
        fileHandler.setFormatter(logFormatter)
        self.logger.addHandler(fileHandler)
        self.include = include
        self.type = type

        self._df = df
        #Proceso Inicial para preparar las cosas
        df2 = self._df #Crea copia del DataFrame
        df2['Fecha'] = pd.to_datetime(df2['Fecha'], format = '%Y-%m-%d') #Convierte las fechas del dataframe en fechas
        grouped = df2.groupby(['Codigos'][0]) #agrupa por nombre de entidad
        df_entidades = {x[0]: x[1] for x in grouped} #saca las entidades para una lista de indices
        entidades = list(df_entidades.keys())
        cantidad_entidades = len(entidades)

        #Informaciones Entidades
        self.datos_entidades = pd.DataFrame()
        self.capital_subsectores = pd.DataFrame()
        i = 0
        for entidad in entidades:
            if not entidad in ['BM SUBSECTOR', 'AP SUBSECTOR', 'BAC SUBSECTOR', 'CC SUBSECTOR', 'SP SUBSECTOR']:
                i += 1
                self.logger.info(f'Trabajando entidad {i} de {cantidad_entidades} -> {entidad}..')
                df_entidad = df_entidades[entidad]
                datos_entidad, capital_subsector = self.crear_df(df_entidad, entidad)
                self.datos_entidades = pd.concat([self.datos_entidades, datos_entidad])
                self.datos_entidades.reset_index(drop = True, inplace = True)
                
                self.capital_subsectores = pd.concat([self.capital_subsectores, capital_subsector]) if not self.capital_subsectores.empty else capital_subsector
                self.capital_subsectores.reset_index(drop = True, inplace = True)
                #capital_df['Fecha'] = capital_df['Fecha'].dt.date

        self.datos_entidades.replace(['BHD LEON'], ['BHD'], inplace = True)
        self.datos = self.calculo_subsector_sistema(self.datos_entidades)
        if self.include == 'var':
            self.datos = self.calcular_variacion(self.datos)

        self.exportar_datos(self.datos)   
        self.logger.removeHandler(fileHandler)
        fileHandler.close()

    def exportar_datos(self, datos_entidades):
        
        if self.type == 'update':
            df_read = pd.read_excel(os.path.join(os.getcwd(), 'resultados_pnme.xlsx'))
            df_export = pd.concat([df_read, datos_entidades])
            df_export.to_excel(os.path.join(os.getcwd(), 'resultados_pnme.xlsx'))
        elif self.type == 'new':
            datos_entidades.to_excel(os.path.join(os.getcwd(),'resultados_pnme.xlsx'))
        self.logger.info(f'Tabla de Resultados exportada con exito en ruta: {os.getcwd()}')

    def forma_calculo_posicion(self, datos, fecha, entidad):

        fecha_cambio_citi = datetime.datetime.strptime('2023-08-18', '%Y-%m-%d') #Cambio del cálculo fue el 25 de agosto del 2023 pero se usan los 5 días anteriores
        fecha_cambio = datetime.datetime.strptime('2023-04-10', '%Y-%m-%d') #Cambio del cálculo fue el 17 de abril del 2023 pero se usan los 5 días anteriores
        fecha_cambio_posicion = datetime.datetime.strptime('2024-01-01', '%Y-%m-%d')

        #region --> Pasar Valor a Variables y Verificar que un Valor pase
        try:
            activos = datos['Total De Activos (ME-1)']
        except Exception:
            activos = 0
        try:
            compra_forwards = datos['Contratos De Compra A Plazo Forward Y A Futuro De Divisas (ME-4-7)']
        except Exception:
            compra_forwards = 0
        try:
            a_cont_sin_cont = datos['Cuentas Contingentes Deudoras Sin Contratos (ME-4-16)']
        except Exception:
            a_cont_sin_cont = 0

        try:
            provisiones = datos['Provisión Para Diferencias En Cambios De Créditos D Y E (ME-4-5)'] + datos['Provisión Por Diferencias De Cambios De Los Créditos D Y E (ME-4-5)']
        except Exception:
            try:
                provisiones = datos['Provisión Para Diferencias En Cambios De Créditos D Y E (ME-4-5)']
            except Exception:
                try:
                    provisiones = datos['Provisión Por Diferencias De Cambios De Los Créditos D Y E (ME-4-5)']
                except Exception:
                    provisiones = 0

        try:
            a_cont = datos['Cuentas Contingentes Deudoras (ME-4-2)']
        except Exception:
            a_cont = 0

        try:
            pasivos = datos['Total De Pasivos (ME-2)']
        except Exception:
            pasivos = 0

        try:
            venta_forwards = datos['Contratos De Venta A Plazo Forward Y A Futuro De Divisas (ME-4-8)']
        except Exception:
            venta_forwards = 0

        if entidad == 'BM CITIBANK' and (fecha_cambio_citi <= fecha < fecha_cambio_posicion):
            try:
                derechos_derivados = datos['Derechos En Derivados (IF-1)']
            except Exception:
                derechos_derivados = 0
            try:
                obligaciones_derivados = datos['Obligaciones De Derivados (IF-2)']
            except Exception:
                obligaciones_derivados = 0
            #print(f'{True} -> {fecha} Derechos: {derechos_derivados} Obligaciones: {obligaciones_derivados}')
        else:
            try:
                derechos_derivados = datos['Derechos En Derivados (ME-4-7)'] + (datos['Contratos De Compra/Venta Al Contado (Spot) (ME-4-19)'] if fecha >= fecha_cambio_posicion else 0)
            except Exception:
                derechos_derivados = 0
            try:
                obligaciones_derivados = datos['Obligaciones En Derivados (ME-4-8)'] + datos['Obligaciones De Derivados (ME-4-8)']
            except Exception:
                try: 
                    obligaciones_derivados = datos['Obligaciones En Derivados (ME-4-8)']
                except Exception:
                    try:
                        obligaciones_derivados = datos['Obligaciones De Derivados (ME-4-8)']
                    except Exception:
                        obligaciones_derivados = 0
        

        try:    
            p_cont_sin_cont = datos['Cuentas Contingentes Acreedoras Sin Contratos (ME-4-17)']
        except Exception:
            p_cont_sin_cont = 0

        try:
            p_cont = datos['Cuentas Contingentes Acreedoras (ME-4-3)']
        except Exception:
            p_cont = 0

        try:
            capital_pagado = datos['Capital Pagado (BG-3-1)']
        except Exception:
            capital_pagado = 0
        try:
            adicional_pagado = datos['Capital Adicional Pagado (BG-3-2)']
        except Exception:
            adicional_pagado = 0
        try:
            reservas = datos['Reservas Obligatoria\\ (ME-4-6)']
        except Exception:
            reservas = 0

        try:
            tipo_cambio = datos['tipo_cambio']
        except Exception:
            tipo_cambio = 0 
        #endregion --> Pasar Valor a Variables y Verificar que un Valor pase
        
        #Capital
        capital = capital_pagado + reservas
        capital_mas_adicional = capital + adicional_pagado
        
        #Calculo Actual
        parte_activa_actual = activos + derechos_derivados + a_cont_sin_cont - provisiones #Se suman las provisiones porque son negativas
        parte_pasiva_actual = pasivos + obligaciones_derivados + p_cont_sin_cont

        #Calculo Anterior
        parte_activa_antes = activos + (a_cont - compra_forwards - venta_forwards) + compra_forwards - provisiones
        parte_pasiva_antes = pasivos + (p_cont - compra_forwards - venta_forwards) + venta_forwards

        parte_activa = parte_activa_antes if fecha < fecha_cambio else parte_activa_actual
        parte_pasiva = parte_pasiva_antes if fecha < fecha_cambio else parte_pasiva_actual

        #np.seterr(divide = 'raise')
        try:
            posicion = (parte_activa - parte_pasiva) / tipo_cambio
        except Exception as e:
            self.logger.error(f'Error! Calculando Posición -> {fecha}')
            posicion = 0
        
        try:
            if tipo_cambio == 0 or capital == 0:
                self.logger.error(f'Error! Calculando Posición entre Capital -> {fecha} {'|| Tipo Cambio en 0' if tipo_cambio == 0 else '|| Capital en 0' if capital == 0 else ""}')
                posicion_capital = 0
            else:
                posicion_capital = posicion / (capital / tipo_cambio)
        except Exception as e:
            self.logger.error(f'Error! Calculando Posición entre Capital -> {fecha}')
            posicion_capital = 0
        try:     
            if tipo_cambio == 0 or capital_mas_adicional == 0:
                self.logger.error(f'Error! Calculando Posición entre Capital más Adicional -> {fecha} {'|| Tipo Cambio en 0' if tipo_cambio == 0 else '|| Capital más Adicional en 0' if capital_mas_adicional == 0 else ""}')
                posicion_capital_adicional = 0
            else:
                posicion_capital_adicional = posicion / (capital_mas_adicional / tipo_cambio)
        except Exception as e:
            self.logger.error(f'Error! Calculando Posición entre Capital más Adicional -> {fecha}')
            posicion_capital_adicional = 0
        
        capital_list = []
        capitaladd_list = []
        fecha_list = []
        df_capital = {}
        if entidad in ['BM SUBSECTOR', 'AP SUBSECTOR', 'BAC SUBSECTOR', 'CC SUBSECTOR', 'SP SUBSECTOR']:
            capital_list.append(capital)
            capitaladd_list.append(capital_mas_adicional)
            fecha_list.append(fecha)
        df_capital['Fecha'] = fecha_list  
        df_capital['Capital'] = capital_list
        df_capital['Capital Mas Add'] = capitaladd_list
        df_capital = pd.DataFrame.from_dict(df_capital)

        return posicion, posicion_capital, posicion_capital_adicional, tipo_cambio, df_capital, capital, capital_mas_adicional

    def sacar_valores(self, datos, cuentas, parametros, **kwargs):
        valores = {}
        par1 = kwargs['par1']
        #par2 = kwargs['par2']
        for cuenta in cuentas:
            try:
                valores[cuenta] = datos[(datos[parametros[0]] == cuenta) & (datos[parametros[1]] == par1)]['Valor'].values[0] # & (df[parametros[2]] == par2) #no se necesita entidad porque se esta dividiendo ya por entidades
            except IndexError:
                self.logger.warning(f'WARNING! -> Cuenta {cuenta} no encontrada!')

        i = 0
        while True:
            if i <= len(cuentas):
                try:
                    valores['tipo_cambio'] = datos[(datos[parametros[1]] == par1)]['Tipo Cambio'].values[i] #& (df[parametros[2]] == par2)
                    if valores['tipo_cambio'] == 0:
                        i += 1
                    else:
                        break
                except Exception as e:
                    i += 1
            else:
                valores['tipo_cambio'] = 0
                break
            
        return valores

    def calculador_posicion_fecha(self, datos, fechas_sacadas, cuentas_sacadas, parametros, entidad):
        dat, pos, pos_cap, pos_cap_add, tasa_cambio, capital, capital_mas_ad = [], [], [], [], [], [], []
        dict_posicion = {}
        capital_df = pd.DataFrame()
        for fecha in fechas_sacadas:
            dat.append(fecha.date())
            self.logger.info(f'Fecha: {fecha.date()}')
            posicion = self.forma_calculo_posicion(datos = self.sacar_valores(datos = datos,
                                                                              cuentas = cuentas_sacadas, 
                                                                              parametros = parametros, 
                                                                              par1 = fecha), 
                                                   fecha = fecha,
                                                   entidad = entidad)
            pos.append(posicion[0])
            pos_cap.append(posicion[1])
            pos_cap_add.append(posicion[2])
            tasa_cambio.append(posicion[3])
            capital.append(posicion[5])
            capital_mas_ad.append(posicion[6])

            capital_df = pd.concat([capital_df, posicion[4]])

        self.logger.info(f'{dat} - {entidad} - {tasa_cambio}')
        dict_posicion = {'Fecha': dat,
                        'Posicion': pos,
                        'Capital': capital,
                        'Capital + Add': capital_mas_ad,
                        '%Capital': pos_cap,
                        '%Capital + Add': pos_cap_add,
                        'Tipo Cambio': tasa_cambio
                        }

        return dict_posicion, capital_df

    def generar_diccionario_posicion_entidad(self, datos, entidad):
        cuentas_sacadas = datos['Cuenta'].unique()
        fechas_sacadas = datos['Fecha'].unique()
        parametros = ['Cuenta', 'Fecha', 'Codigos', 'Valor']
        dic_resultados_posicion_fecha, capital = self.calculador_posicion_fecha(datos = datos, 
                                                                                fechas_sacadas = fechas_sacadas, 
                                                                                cuentas_sacadas = cuentas_sacadas, 
                                                                                parametros = parametros,
                                                                                entidad = entidad)
        return dic_resultados_posicion_fecha, capital

    def crear_df(self, datos, entidad):

        #Definir las informaciones por Periodicidad
        diarias = datos[datos['Dia'].str.startswith('DIA')] #Informaciones Diarias
        mensuales = datos[~datos['Dia'].astype(str).str.startswith('DIA')] #Informaciones Mensuales

        #Sacar las informaciones por periodicidad y luego juntarlas y retornar df compilado
        informaciones_diarias_entidad, capital_diario = self.generar_diccionario_posicion_entidad(datos = diarias, entidad = entidad)
        informaciones_diarias_entidad = pd.DataFrame(informaciones_diarias_entidad)
        informaciones_diarias_entidad['Periodicidad'] = 'Diaria'
        informaciones_diarias_entidad.sort_values(by = ['Fecha'], inplace = True)
        #informaciones_diarias_entidad['Variacion'] = informaciones_diarias_entidad['Posicion'] - informaciones_diarias_entidad['Posicion'].shift(1)
        capital_diario = pd.DataFrame(capital_diario)
        capital_diario['Periodicidad'] = 'Diaria'
        capital_diario['Entidad'] = entidad

        informaciones_mensuales_entidad, capital_mensual = self.generar_diccionario_posicion_entidad(datos = mensuales, entidad = entidad)
        informaciones_mensuales_entidad = pd.DataFrame(informaciones_mensuales_entidad)
        informaciones_mensuales_entidad['Periodicidad'] = 'Mensual'
        informaciones_mensuales_entidad.sort_values(by = ['Fecha'], inplace = True)
        #informaciones_mensuales_entidad['Variacion'] = informaciones_mensuales_entidad['Posicion'] - informaciones_mensuales_entidad['Posicion'].shift(1)
        capital_mensual = pd.DataFrame(capital_mensual)
        capital_mensual['Periodicidad'] = 'Mensual'
        capital_mensual['Entidad'] = entidad

        informaciones_entidad = pd.concat([informaciones_diarias_entidad, informaciones_mensuales_entidad])
        capital_subsector = pd.concat([capital_diario, capital_mensual])
        informaciones_entidad['Entidad'] = entidad
        informaciones_entidad[['Subsector', 'Entidad']] = informaciones_entidad['Entidad'].str.split(' ', n = 1, expand = True)
        informaciones_entidad = informaciones_entidad[['Fecha', 'Periodicidad', 'Entidad', 'Subsector', 'Posicion', 'Capital', 'Capital + Add','%Capital', '%Capital + Add', 'Tipo Cambio']]#, 'Variacion']]

        return informaciones_entidad, capital_subsector

    def calculo_subsector_sistema(self, df_entidades):
        df_total = pd.DataFrame()

        def calculo(df: pd.DataFrame, type: str):
            #Crea un df vacio
            df_results = pd.DataFrame()
            
            #toma porcion del df parametro y saca la suma 
            dfs = df[['Posicion', 'Capital', 'Capital + Add']]
            suma = dfs.sum()

            #Se llena el df vacio con las nuevas informaciones
            fecha = df['Fecha'].unique()
            df_results['Fecha'] = fecha
            df_results['Periodicidad'] = df['Periodicidad'].unique()
            df_results['Entidad'] = 'SUBSECTOR' if type == 'sub' else 'SISTEMA'
            df_results['Subsector'] = df['Subsector'].unique() if type == 'sub' else 'SIS'
            df_results['Posicion'] = suma['Posicion']
            df_results['Capital'] = suma['Capital']
            df_results['Capital + Add'] = suma['Capital + Add']

            #Informaciones que requieren el ripo de cambio
            tipo_cambio = df['Tipo Cambio'].unique()
            self.logger.info(f'Fecha {fecha} | Tipo Cambio -> {tipo_cambio}')
            df_results['%Capital'] = (suma['Posicion'] * tipo_cambio) / suma['Capital']
            df_results['%Capital + Add'] = (suma['Posicion'] * tipo_cambio) / suma['Capital + Add']
            df_results['Tipo Cambio'] = tipo_cambio
            return df_results
        
        #Para determinar los valores de los subsectores
        grouped = df_entidades.groupby(['Periodicidad', 'Subsector', 'Fecha'])
        for key, df in grouped:
            df_results = calculo(df, 'sub')
            df_total = df_results if df_total.empty else pd.concat([df_total, df_results])

        #Para determinar los valores del sistema
        grouped = df_total.groupby(['Periodicidad', 'Fecha'])
        for key, df in grouped:
            df_results = calculo(df, 'sis')
            df_total = df_results if df_total.empty else pd.concat([df_total, df_results])

        #Para sacar las variaciones del df que contiene las infos de subsectores y sistema
        #subsector_df = pd.DataFrame()
        #grouped = df_total.groupby(['Periodicidad', 'Subsector'])
        #for key, df in grouped:
        #    df.sort_values(by = ['Fecha'], inplace = True)
        #    df['Variacion'] = df['Posicion'] - df['Posicion'].shift(1)
        #    subsector_df = df if df.empty else pd.concat([subsector_df, df])
        #df_total = subsector_df

        #Se junta el df original con el que resulta de este proceso
        df_final = pd.concat([df_entidades, df_total])

        return df_final
    
    def calcular_variacion(df):

        return df