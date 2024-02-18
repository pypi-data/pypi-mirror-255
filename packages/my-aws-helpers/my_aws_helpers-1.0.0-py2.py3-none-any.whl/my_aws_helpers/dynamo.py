from typing import List, Any, Optional
from datetime import datetime, date
import boto3
from abc import ABC, abstractclassmethod, abstractmethod

class MetaData:
    """
    This class is a convenience class, 
    each of its attributes will be attached to objects that inherit from `BaseTableObject`
    """
    created_by: Optional[str]
    created_on: Optional[datetime]
    updated_by: Optional[str]
    updated_on: Optional[datetime]

    def set_timestamp(self, ts: Any) -> datetime:
        """Be absolutely sure timestamps are datetimes"""
        if isinstance(ts, datetime):
            return ts
        else:
            return datetime.now()

    def __init__(self, **kwargs) -> None:
        self.created_by = kwargs["created_by"] if kwargs.get("created_by") else self._get_user()
        self.updated_by = kwargs["updated_by"] if kwargs.get("updated_by") else self._get_user()
        self.created_on = self.set_timestamp(ts=kwargs.get("created_on"))
        self.updated_on = self.set_timestamp(ts=kwargs.get("updated_on"))

    def _get_user(self):
        """This should probably do some clever thing to get the actual user details from the token or something"""
        return ""


class BaseTableObject(MetaData):
    """
    An Abstract class that helps ensure your objects
    conform to the AssetTable schema and
    implement serialisation/deserialisation for Dynamo
    """
    pk: str
    sk: str

    def _get_pk(self):
        pass

    def _get_sk(self):
        pass

    @abstractclassmethod
    def _from_dynamo_representation():
        """
        Deserialises this object from Dynamo Representation
        """
        pass

    @abstractmethod
    def _to_dynamo_representation():
        """
        Serialises this object to Dynamo Representation
        """        
        pass

    def _optional_get(self, kwargs: dict, key: str, default: Any):
        return kwargs.get(key) if kwargs.get(key) else default
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.pk = self._optional_get(kwargs=kwargs, key='pk', default=self._get_pk())
        self.sk = self._optional_get(kwargs=kwargs, key='sk', default=self._get_sk())

class BaseQueries(ABC):
    table_name: str

    def __init__(self, table_name: str) -> None:
        self.table_name = table_name

class Dynamo:
    def __init__(self, table_name: str) -> None:
        ddb = boto3.resource('dynamodb')
        self.table = ddb.Table(table_name)
    
    def put_item(self, item: dict):
        return self.table.put_item(Item=item)
    
    def get_item(self, item: dict):
        return self.table.get_item(Item=item)
    
    def delete_item(self, item: dict):
        return self.table.delete_item(Item=item)
    
    def batch_put(self, items: List[dict]) -> None:
        with self.table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        return 
    
    def batch_delete(self, items: List[dict]) -> None:
        with self.table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Item=item)
        return

    def to_dynamo_representation(obj: dict):
        """
        Attempts to put common datatype transformations in one spot
        """
        new_obj = dict()
        for key, value in obj.items():
            new_obj[key] = _datatype_map(value=value)
        return new_obj
    
def _datatype_map(value: Any):
    if (isinstance(value, date)) or (isinstance(value, datetime)):
        return value.isoformat()
    if (isinstance(value, list)):
        return [_datatype_map(value = item) for item in value]
    if (isinstance(value, dict)):
        new_obj = dict()
        for k, v in value.items():
            new_obj[k] = _datatype_map(value=v)
        return new_obj
    return value