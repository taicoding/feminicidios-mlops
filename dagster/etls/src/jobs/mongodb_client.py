import logging
from pymongo import MongoClient, errors
import pandas as pd

logger = logging.getLogger(__name__)


class MongoDBClient:
    def __init__(self, uri, db_name, collection_name):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        """Conectar a la base de datos de MongoDB y obtener la colección."""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info(f"Conectado a {self.db_name}.{self.collection_name}")
        except errors.ConnectionFailure as e:
            logger.error(f"No se pudo conectar a MongoDB: {e}")

    def create_unique_index(self, field):
        """Crear un índice único en un campo especificado si no existe ya."""
        try:
            self.collection.create_index([(field, 1)], unique=True)
            logger.info(f"Índice único en '{field}' creado exitosamente.")
        except Exception as e:
            logger.error(f"Error al crear el índice: {e}")

    def insert_new_document(self, document, field):
        """Insertar un documento en la colección si no existe un documento con el valor del campo especificado."""
        if self.collection.find_one({field: document.get(field)}) is None:
            try:
                self.collection.insert_one(document)
                logger.info("Documento insertado exitosamente.")
            except errors.DuplicateKeyError:
                logger.warning("Error de clave duplicada. Documento no insertado.")
        else:
            logger.info(
                f"El documento con {field}={document.get(field)} ya existe. No se insertó ningún documento."
            )

    def aggregate_documents(self, pipeline=[]):
        """Agregar documentos en la colección."""
        result = self.collection.aggregate(pipeline, allowDiskUse=True)
        df_result = pd.json_normalize(result)
        return df_result

    def insert_many_documents(self, documents):
        """Insertar múltiples documentos en la colección."""
        try:
            self.collection.insert_many(documents)
            logger.info("Documentos insertados exitosamente.")
        except errors.DuplicateKeyError:
            logger.warning("Error de clave duplicada. Documentos no insertados.")

    def find_document(self, query={}):
        """Encontrar un documento en la colección."""
        result = self.collection.find_one(query)
        df_result = pd.json_normalize(result)
        return df_result

    def find_documents(self, query={}):
        """Encontrar documentos en la colección."""
        result = self.collection.find(query)
        df_result = pd.json_normalize(result)
        return df_result

    def update_document(self, query={}, update={}):
        """Actualizar un documento en la colección."""
        self.collection.update_one(query, update)
        logger.info("Documento actualizado exitosamente.")

    def close(self):
        """Cerrar la conexión a la base de datos de MongoDB."""
        self.client.close()
        logger.info("Conexión cerrada.")
