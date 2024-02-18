from peewee import CharField, DateTimeField, FloatField, ForeignKeyField, fn
from .core import BaseModel
from datetime import datetime
import csv
from tqdm import tqdm
from io import StringIO
from io import BytesIO


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class Variables(BaseModel):

    name = CharField(unique=True)

    @classmethod
    def create(cls, name:str)-> dict:
        r"""
        You can use Model.create() to create a new model instance. This method accepts keyword arguments, where the keys correspond 
        to the names of the model's fields. A new instance is returned and a row is added to the table.

        ```python
        >>> Variables.create(name='Pressure')
        {
            'message': (str)
            'data': (dict) {
                'name': 'pressure'
            }
        }
        ```
        
        This will INSERT a new row into the database. The primary key will automatically be retrieved and stored on the model instance.

        **Parameters**

        * **name:** (str), Industrial protocol name

        **Returns**

        * **result:** (dict) --> {'message': (str), 'data': (dict) row serialized}

        """
        result = dict()
        data = dict()
        name = name.lower()

        if not cls.name_exist(name):

            query = cls(name=name)
            query.save()
            
            message = f"{name} variable created successfully"
            data.update(query.serialize())

            result.update(
                {
                    'message': message, 
                    'data': data
                }
            )
            return result

        message = f"{name} variable is already into database"
        result.update(
            {
                'message': message, 
                'data': data
            }
        )
        return result

    @classmethod
    def read_by_name(cls, name:str)->bool:
        r"""
        Get instance by its a name

        **Parameters**

        * **name:** (str) Variable name

        **Returns**

        * **bool:** If True, name exist into database 
        """
        query = cls.get_or_none(name=name)
        
        if query is not None:

            return query.serialize()
        
        return None

    @classmethod
    def name_exist(cls, name:str)->bool:
        r"""
        Verify is a name exist into database

        **Parameters**

        * **name:** (str) Variable name

        **Returns**

        * **bool:** If True, name exist into database 
        """
        query = cls.get_or_none(name=name)
        
        if query is not None:

            return True
        
        return False

    def serialize(self)-> dict:
        r"""
        Serialize database record to a jsonable object
        """

        return {
            "id": self.id,
            "name": self.name
        }


class Units(BaseModel):

    name = CharField(unique=True)
    unit = CharField(unique=True)
    variable_id = ForeignKeyField(Variables, backref='units', on_delete='CASCADE')

    @classmethod
    def create(cls, name:str, unit:str, variable:str)-> dict:
        r"""
        You can use Model.create() to create a new model instance. This method accepts keyword arguments, where the keys correspond 
        to the names of the model's fields. A new instance is returned and a row is added to the table.

        ```python
        >>> Variables.create(name='Pa', variable='Pressure')
        {
            'message': (str)
            'data': (dict) {
                'id': 1,
                'name': 'Pa',
                'variable': 'pressure'
            }
        }
        ```
        
        This will INSERT a new row into the database. The primary key will automatically be retrieved and stored on the model instance.

        **Parameters**

        * **name:** (str), Industrial protocol name

        **Returns**

        * **result:** (dict) --> {'message': (str), 'data': (dict) row serialized}

        """
        result = dict()
        data = dict()
        name = name
        variable = variable.lower()

        if not cls.name_exist(name):

            query_variable = Variables.read_by_name(variable)
            
            if query_variable is not None:

                variable_id = query_variable['id']

                query = cls(name=name, unit=unit, variable_id=variable_id)
                query.save()
                
                message = f"{name} unit created successfully"
                data.update(query.serialize())

                result.update(
                    {
                        'message': message, 
                        'data': data
                    }
                )
                return result


            message = f"{variable} variable not exist into database"

            result.update(
                {
                    'message': message, 
                    'data': data
                }
            )
            return result

        message = f"{name} unit is already into database"
        result.update(
            {
                'message': message, 
                'data': data
            }
        )
        return result

    @classmethod
    def read_by_name(cls, name:str)->bool:
        r"""
        Get instance by its a name

        **Parameters**

        * **name:** (str) Variable name

        **Returns**

        * **bool:** If True, name exist into database 
        """
        query = cls.get_or_none(name=name)
        
        if query is not None:

            return query.serialize()
        
        return None

    @classmethod
    def read_by_unit(cls, unit:str)->bool:
        r"""
        Get instance by its a name

        **Parameters**

        * **name:** (str) Variable name

        **Returns**

        * **bool:** If True, name exist into database 
        """
        query = cls.get_or_none(unit=unit)
        
        if query is not None:

            return query.serialize()
        
        return None

    @classmethod
    def name_exist(cls, name:str)->bool:
        r"""
        Verify is a name exist into database

        **Parameters**

        * **name:** (str) Variable name

        **Returns**

        * **bool:** If True, name exist into database 
        """
        query = cls.get_or_none(name=name)
        
        if query is not None:

            return True
        
        return False

    def serialize(self)-> dict:
        r"""
        Serialize database record to a jsonable object
        """

        return {
            "id": self.id,
            "name": self.name,
            "variable": self.variable_id.name,
            "unit": self.unit
        }


class DataTypes(BaseModel):

    name = CharField(unique=True)

    @classmethod
    def create(cls, name:str)-> dict:
        r"""
        You can use Model.create() to create a new model instance. This method accepts keyword arguments, where the keys correspond 
        to the names of the model's fields. A new instance is returned and a row is added to the table.

        ```python
        >>> Variables.create(name='Pressure')
        {
            'message': (str)
            'data': (dict) {
                'name': 'pressure'
            }
        }
        ```
        
        This will INSERT a new row into the database. The primary key will automatically be retrieved and stored on the model instance.

        **Parameters**

        * **name:** (str), Industrial protocol name

        **Returns**

        * **result:** (dict) --> {'message': (str), 'data': (dict) row serialized}

        """
        result = dict()
        data = dict()
        name = name.lower()

        if not cls.name_exist(name):

            query = cls(name=name)
            query.save()
            
            message = f"{name} DataType created successfully"
            data.update(query.serialize())

            result.update(
                {
                    'message': message, 
                    'data': data
                }
            )
            return result

        message = f"{name} DataType is already into database"
        result.update(
            {
                'message': message, 
                'data': data
            }
        )
        return result

    @classmethod
    def read_by_name(cls, name:str)->bool:
        r"""
        Get instance by its a name

        **Parameters**

        * **name:** (str) Variable name

        **Returns**

        * **bool:** If True, name exist into database 
        """
        query = cls.get_or_none(name=name)
        
        if query is not None:

            return query.serialize()
        
        return None

    @classmethod
    def name_exist(cls, name:str)->bool:
        r"""
        Verify is a name exist into database

        **Parameters**

        * **name:** (str) Variable name

        **Returns**

        * **bool:** If True, name exist into database 
        """
        query = cls.get_or_none(name=name)
        
        if query is not None:

            return True
        
        return False

    def serialize(self)-> dict:
        r"""
        Serialize database record to a jsonable object
        """

        return {
            "id": self.id,
            "name": self.name
        }


class Tags(BaseModel):

    name = CharField(unique=True)
    unit = ForeignKeyField(Units, backref='tags', on_delete='CASCADE')
    data_type = ForeignKeyField(DataTypes, backref='tags', on_delete='CASCADE')
    description = CharField(max_length=250)
    display_name = CharField()
    min_value = FloatField(null=True)
    max_value = FloatField(null=True)
    tcp_source_address = CharField(null=True)
    node_namespace = CharField(null=True)
    start = DateTimeField(default=datetime.now())

    @classmethod
    def create(
        cls, 
        name:str, 
        unit:str,
        data_type:str,
        description:str,
        display_name:str,
        min_value:float=None,
        max_value:float=None,
        tcp_source_address:str=None,
        node_namespace:str=None
        ):

        result = dict()
        message = f"{name} already exist into database"
        data = dict()
        
        if not cls.name_exist(name):

            _unit = Units.read_by_unit(unit=unit)

            _data_type = DataTypes.read_by_name(name=data_type.lower())

            if _unit is not None:

                if _data_type is not None:
            
                    query = cls(
                        name=name, 
                        unit=_unit['id'],
                        data_type=_data_type['id'],
                        description=description,
                        display_name=display_name,
                        min_value=min_value,
                        max_value=max_value,
                        tcp_source_address=tcp_source_address,
                        node_namespace=node_namespace
                        )
                    query.save()

                    message = f"{name} tag created successfully"
                    data.update(query.serialize())

                    result.update(
                        {
                            'message': message, 
                            'data': data
                        }
                    )

                    return result

                message = f"{data_type} data type not exist into database"
                result.update(
                    {
                        'message': message, 
                        'data': data
                    }
                )
                return result

            message = f"{unit} unit not exist into database"
            result.update(
                {
                    'message': message, 
                    'data': data
                }
            )
            return result

        result.update(
            {
                'message': message, 
                'data': data
            }
        )
        return result

    @classmethod
    def read_by_name(cls, name):
        query = cls.get_or_none(name=name)
        return query

    @classmethod
    def read_by_names(cls, names):
        query = cls.select().where(cls.name in names)
        return query

    @classmethod
    def name_exist(cls, name):
        r"""
        Documentation here
        """
        tag = cls.get_or_none(name=name)
        if tag is not None:

            return True
        
        return False

    @classmethod
    def get_export_to_csv(cls):
        r"""
        Documentation here
        """
        return [tag.serialize() for tag in cls.select()]

    def serialize(self):
        r"""
        Documentation here
        """
        return {
            'id': self.id,
            'name': self.name,
            'unit': self.unit.unit,
            'data_type': self.data_type.name,
            'description': self.description,
            'display_name': self.display_name,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'tcp_source_address': self.tcp_source_address,
            'node_namespace': self.node_namespace
        }


class TagValue(BaseModel):

    tag = ForeignKeyField(Tags, backref='values')
    value = FloatField()
    timestamp = DateTimeField(default=datetime.now)


    @classmethod
    def export_to_csv(cls, start:datetime, end:datetime):
        r"""
        Documentation here
        """

        tag_names_query = cls.select(fn.DISTINCT(cls.tag_id))
        
        tag_info = dict()
        tag_info['timestamp'] = None
        for tag in tag_names_query:

            tag_info[tag.tag.name] = None

        del tag_names_query

        previous_timestamp = datetime.now().strftime(DATETIME_FORMAT)[:-5]
        tags = cls.select().where((cls.timestamp >=start) & (cls.timestamp <= end))
        row = 0
        with open(f'daq_tag_value_from_{start}_to_{end}.csv', 'w', newline='') as f:
            
            for tag in tqdm(tags, desc="Downloading csv", unit="records"):               

                timestamp = tag.timestamp.strftime(DATETIME_FORMAT)[:-5]
                if previous_timestamp!=timestamp:
                    
                    if tag_info:

                        if row==0:
                    
                            dict_writer = csv.DictWriter(f, tag_info.keys(), delimiter=",")
                            dict_writer.writeheader()

                        dict_writer.writerow(tag_info)
                        row += 1

                    tag_info = dict()
                    previous_timestamp = timestamp
                    tag_info['timestamp'] = timestamp
                    tag_info[tag.tag.name] = tag.value

                else:

                    tag_info[f'{tag.tag.name}'] = tag.value


    ##
    @classmethod
    def get_exported_csv(cls, start:datetime, end:datetime):
        r"""
        Documentation here
        """

        tag_names_query = cls.select(fn.DISTINCT(cls.tag_id))
        
        tag_info = dict()
        tag_info['timestamp'] = None
        for tag in tag_names_query:

            tag_info[tag.tag.name] = None

        del tag_names_query

        previous_timestamp = datetime.now().strftime(DATETIME_FORMAT)[:-5]
        tags = cls.select().where((cls.timestamp >=start) & (cls.timestamp <= end))
        row = 0
        
        with StringIO() as f:
            writer = csv.writer(f)
            
            for tag in tqdm(tags, desc="Downloading csv", unit="records"):               

                timestamp = tag.timestamp.strftime(DATETIME_FORMAT)[:-5]
                if previous_timestamp!=timestamp:

                    if tag_info:

                        if row==0:

                            writer.writerow(tag_info.keys())

                        writer.writerow(tag_info.values())
                        row += 1

                    tag_info = dict()
                    previous_timestamp = timestamp
                    tag_info['timestamp'] = timestamp
                    tag_info[tag.tag.name] = tag.value

                else:

                    tag_info[f'{tag.tag.name}'] = tag.value
            
            return f.getvalue()
        
    #########
    @classmethod
    def export_tags_to_csv(cls, start:datetime, end:datetime, tags:list):
        r"""
        Documentation here
        """
        # Select tags
        tag_names_query = cls.select(fn.DISTINCT(cls.tag_id))        
        tag_info = dict()
        tag_info['timestamp'] = None
        _query = ""
        _tags = list()
        for tag in tag_names_query:

            if tag.tag.name in tags:

                tag_info[tag.tag.name] = None
                
                _tags.append(tag.tag.id)
            
        del tag_names_query

        _query = f"cls.tag_id.in_(_tags)"


        previous_timestamp = datetime.now().strftime(DATETIME_FORMAT)[:-5]

        # Creating query
        _query += f" & (cls.timestamp >=start) & (cls.timestamp <= end)"

        tags = cls.select().where(eval(_query)).order_by(cls.timestamp.asc())
        row = 0
        with open(f'daq_tag_value_from_{start}_to_{end}.csv', 'w', newline='') as f:
            
            for tag in tqdm(tags, desc="Downloading csv", unit="records"):               

                timestamp = tag.timestamp.strftime(DATETIME_FORMAT)[:-5]
                if previous_timestamp!=timestamp:
                    
                    if tag_info:

                        if row==0:
                    
                            dict_writer = csv.DictWriter(f, tag_info.keys(), delimiter=",")
                            dict_writer.writeheader()

                        dict_writer.writerow(tag_info)
                        row += 1

                    tag_info = dict()
                    previous_timestamp = timestamp
                    tag_info['timestamp'] = timestamp
                    tag_info[tag.tag.name] = tag.value

                else:

                    tag_info[f'{tag.tag.name}'] = tag.value


    @classmethod
    def get_exported_tags_csv(cls, start:datetime, end:datetime, tags:list):
        r"""
        Documentation here
        """
        # Select tags
        tag_names_query = cls.select(fn.DISTINCT(cls.tag_id))        
        tag_info = dict()
        tag_info['timestamp'] = None
        _query = ""
        _tags = list()
        for tag in tag_names_query:

            if tag.tag.name in tags:

                tag_info[tag.tag.name] = None
                    
                _tags.append(tag.tag.id)
                
        del tag_names_query

        _query = f"cls.tag_id.in_(_tags)"


        previous_timestamp = datetime.now().strftime(DATETIME_FORMAT)[:-5]

        # Creating query
        _query += f" & (cls.timestamp >=start) & (cls.timestamp <= end)"

        tags = cls.select().where(eval(_query)).order_by(cls.timestamp.asc())
        
        with StringIO() as f:
            writer = csv.writer(f)
            writer.writerow(tag_info.keys())

            for tag in tqdm(tags, desc="Downloading csv", unit="records"):               

                timestamp = tag.timestamp.strftime(DATETIME_FORMAT)[:-5]
                if previous_timestamp!=timestamp:

                    if tag_info:

                        writer.writerow(tag_info.values())

                    tag_info = dict()
                    previous_timestamp = timestamp
                    tag_info['timestamp'] = timestamp
                    tag_info[tag.tag.name] = tag.value

                else:
                    tag_info[f'{tag.tag.name}'] = tag.value
            
            return f.getvalue()