import functools
import urllib
from sqlalchemy import (
    create_engine,
    select,
    insert,
    Table,
    Column,
    Float,
    Integer,
    String,
    MetaData,
    DateTime,
    Boolean,
)
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
import pytz
from datetime import datetime


class SqlDB:

    def __init__(self, esquema="dbo"):
        self.esquema = esquema
        params = urllib.parse.quote_plus(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=morant.database.windows.net;"
            "DATABASE=GASTOSDB;"
            "UID=emorones;"
            "PWD=Mor@nt2024;"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=30;"
        )

        self.engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        self.metadata = MetaData(schema=self.esquema)
        self.definir_tablas()

    def definir_tablas(self):

        self.tabla_registro = Table(
            'Registro', self.metadata,
            Column('Id', Integer, primary_key=True),
            Column('ProyectoId', String),
            Column('OpenAIApiKey', String),
            Column('NombreFuncion', String),
            Column('TokensEntrada', Float),
            Column('TokensSalida', Float),
            Column('Costo', Float),
            Column('ModeloId', String),
            Column('UserAlt', Integer),
            Column('FechaAlt', DateTime),
            Column('UserUpd', Integer),
            Column('FechaUpd', DateTime),
            Column('Activo', Boolean),
            schema=self.esquema
        )

        self.tabla_modelo = Table(
            'Modelo', self.metadata,
            Column('Id', Integer, primary_key=True),
            Column('Modelo', String),
            Column('PrecioTokenEntrada', Float),
            Column('PrecioTokenSalida', Float),
            Column('UserAlt', Integer),
            Column('FechaAlt', DateTime),
            Column('UserUpd', Integer),
            Column('FechaUpd', DateTime),
            Column('Activo', Boolean),
            schema=self.esquema
        )

        self.tabla_proyecto = Table(
            'Proyecto', self.metadata,
            Column('Id', Integer, primary_key=True),
            Column('Nombre', String),
            Column('FechaInicio', DateTime),
            Column('UserAlt', Integer),
            Column('FechaAlt', DateTime),
            Column('UserUpd', Integer),
            Column('FechaUpd', DateTime),
            Column('Activo', Boolean),
            schema=self.esquema
        )

    def agregar_modelo(self, modelo, precio_token_entrada, precio_token_salida): # noqa
        try:
            # Ajustar la fecha actual a la zona horaria de la Ciudad de México
            zona_horaria_cdmx = pytz.timezone('America/Mexico_City')
            fecha_actual = datetime.now(zona_horaria_cdmx)

            stmt = insert(self.tabla_modelo).values(
                Modelo=modelo,
                PrecioTokenEntrada=precio_token_entrada,
                PrecioTokenSalida=precio_token_salida,
                FechaAlt=fecha_actual,
                FechaUpd=fecha_actual,
                Activo=True
            )

            with self.engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()

            print("Modelo agregado con éxito.")
        except SQLAlchemyError as e:
            # Manejar el error específico de SQLAlchemy
            print(f"Error al agregar el modelo: {e}")
        except Exception as e:
            # Manejar cualquier otro error no específico de SQLAlchemy
            print(f"Error inesperado: {e}")

    def obtener_datos_modelo(self, nombre_modelo):
        try:
            # Construir la consulta para buscar el modelo por su nombre
            stmt = select(
                self.tabla_modelo.c.Id,
                self.tabla_modelo.c.Modelo,
                self.tabla_modelo.c.PrecioTokenEntrada,
                self.tabla_modelo.c.PrecioTokenSalida
            ).where(self.tabla_modelo.c.Modelo == nombre_modelo)

            with self.engine.connect() as conn:
                resultado = conn.execute(stmt).fetchone()

            if resultado:
                # Convertir el resultado en un diccionario para facilitar su uso # noqa
                datos_modelo = {
                    "Id": resultado[0],
                    "Modelo": resultado[1],
                    "PrecioTokenEntrada": resultado[2],
                    "PrecioTokenSalida": resultado[3]
                }
                return datos_modelo
            else:
                print("No se encontró el modelo especificado.")
                return None
        except SQLAlchemyError as e:
            print(f"Error al buscar el modelo: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None

    def crear_proyecto(self, nombre, fecha_inicio):
        try:
            nombre = nombre.lower()
            # Ajustar la fecha de inicio a la zona horaria de la Ciudad de México, si es necesario # noqa
            zona_horaria_cdmx = pytz.timezone('America/Mexico_City')
            if fecha_inicio.tzinfo is None:
                fecha_inicio = zona_horaria_cdmx.localize(fecha_inicio)
            else:
                fecha_inicio = fecha_inicio.astimezone(zona_horaria_cdmx)

            # Fecha actual para los campos de fecha de alta y actualización
            fecha_actual = datetime.now(zona_horaria_cdmx)

            stmt = insert(self.tabla_proyecto).values(
                Nombre=nombre,
                FechaInicio=fecha_inicio,
                FechaAlt=fecha_actual,
                FechaUpd=fecha_actual,
                Activo=True
            )

            with self.engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()

            print("Proyecto agregado con éxito.")
        except SQLAlchemyError as e:
            print(f"Error al agregar el proyecto: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")

    def obtener_datos_proyecto(self, nombre_proyecto):
        try:
            # Asegurar que el nombre del proyecto se busca en minúsculas
            nombre_proyecto_minusculas = nombre_proyecto.lower()

            # Construir la consulta para buscar el proyecto por su nombre
            stmt = select(
                self.tabla_proyecto.c.Id,
                self.tabla_proyecto.c.Nombre
            ).where(self.tabla_proyecto.c.Nombre == nombre_proyecto_minusculas)

            with self.engine.connect() as conn:
                resultado = conn.execute(stmt).fetchone()

            if resultado:
                datos_proyecto = {
                    "Id": resultado[0],
                    "Nombre": resultado[1]
                }
                return datos_proyecto
            else:
                print("No se encontró el proyecto especificado.")
                return None
        except SQLAlchemyError as e:
            print(f"Error al buscar el proyecto: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None

    def agregar_registro(self, proyecto_id, openai_api_key, nombre_funcion, tokens_entrada, tokens_salida, costo, modelo_id): # noqa
        try:
            # Ajustar la fecha actual a la zona horaria de la Ciudad de México
            zona_horaria_cdmx = pytz.timezone('America/Mexico_City')
            fecha_actual = datetime.now(zona_horaria_cdmx)

            stmt = insert(self.tabla_registro).values(
                ProyectoId=proyecto_id,
                OpenAIApiKey=openai_api_key,
                NombreFuncion=nombre_funcion,
                TokensEntrada=tokens_entrada,
                TokensSalida=tokens_salida,
                Costo=costo,
                ModeloId=modelo_id,
                FechaAlt=fecha_actual,
                Activo=True
            )

            with self.engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()

            print("Registro agregado con éxito.")
        except SQLAlchemyError as e:
            print(f"Error al agregar el registro: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None


def costos_morant(proyecto, openai_api_key, modelo):
    def decorador(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            nombre_funcion = func.__name__

            # Intentar crear la instancia de la base de datos
            try:
                db = SqlDB()
            except DBAPIError as e:
                print(f"No se pudo conectar a la base de datos debido a un problema con ODBC: {e}") # noqa
                return func(*args, **kwargs)["anwser"]
            except Exception as e:
                print(f"Error inesperado al crear la instancia de la base de datos: {e}") # noqa
                return func(*args, **kwargs)["anwer"]

            data = func(*args, **kwargs)

            tokens_entrada = data.get("input_tokens", 0)
            tokens_salida = data.get("output_tokens", 0)

            # Intentar obtener los datos del modelo
            try:
                datos_modelo = db.obtener_datos_modelo(modelo)
                if datos_modelo is None:
                    raise ValueError("No se encontraron datos para el modelo especificado.") # noqa
            except Exception as e:
                print(f"Error al obtener datos del modelo: {e}")
                return data["answer"]

            # Intentar obtener los datos del proyecto
            try:
                datos_proyecto = db.obtener_datos_proyecto(proyecto)
                if datos_proyecto is None:
                    raise ValueError("No se encontraron datos para el proyecto especificado.") # noqa
            except Exception as e:
                print(f"Error al obtener datos del proyecto: {e}")
                return data["answer"]

            # Calcular el costo
            costo_entrada = tokens_entrada * datos_modelo["PrecioTokenEntrada"] / 1000 # noqa
            costo_salida = tokens_salida * datos_modelo["PrecioTokenSalida"] / 1000 # noqa
            costo = costo_entrada + costo_salida

            # Intentar crear el registro
            try:
                resultado = db.agregar_registro(
                    proyecto_id=datos_proyecto['Id'],
                    openai_api_key=openai_api_key,
                    nombre_funcion=nombre_funcion,
                    tokens_entrada=tokens_entrada,
                    tokens_salida=tokens_salida,
                    costo=costo,
                    modelo_id=datos_modelo['Id']
                )

                if resultado is None:
                    print("No se pudo agregar el resultado")

            except Exception as e:
                print(f"Error al agregar el registro: {e}")

            return data["answer"]
        return wrapper
    return decorador
