from datetime import datetime
import uuid
from typing import ClassVar, List, Optional, Dict, Any, Type, TypeVar, Generic
from pydantic import BaseModel, Field
from app.services.mongodb.client import async_db
from pymongo import ReturnDocument

T = TypeVar('T', bound='MongoBaseModel')

class MongoBaseModel(BaseModel):
    """MongoDB基础模型类，提供异步操作方法"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # 获取当前东八区时间
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    
    class Config:
        collection: ClassVar[str] = None
        indexes: ClassVar[List[str]] = []
    
    async def save(self) -> 'MongoBaseModel':
        """异步保存文档到MongoDB"""
        self.updated_at = datetime.now().astimezone()
        collection = async_db.get_collection(self.Config.collection)
        data = self.dict(by_alias=True)
        data.pop("id")
        await collection.replace_one({"_id": self.id}, data, upsert=True)
        return self
    
    async def delete(self) -> bool:
        """异步从MongoDB删除文档"""
        collection = async_db.get_collection(self.Config.collection)
        result = await collection.delete_one({"_id": self.id})
        return result.deleted_count > 0
    
    @classmethod
    async def find_by_id(cls: Type[T], id: str) -> Optional[T]:
        """异步根据ID查找文档"""
        collection = async_db.get_collection(cls.Config.collection)
        data = await collection.find_one({"_id": id})
        if data:
            # 确保_id映射到id字段
            if "_id" in data and "id" not in data:
                data["id"] = data["_id"]
            return cls(**data)
        return None
    
    @classmethod
    async def find_one(cls: Type[T], filter: Dict) -> Optional[T]:
        """异步查找单个文档"""
        collection = async_db.get_collection(cls.Config.collection)
        data = await collection.find_one(filter)
        if data:
            # 确保_id映射到id字段
            if "_id" in data and "id" not in data:
                data["id"] = data["_id"]
            return cls(**data)
        return None

    @classmethod
    async def find_one_and_update(cls: Type[T], filter: Dict, update: Dict) -> Optional[T]:
        """异步查找并更新单个文档"""
        collection = async_db.get_collection(cls.Config.collection)
        if '$set' not in update:
            update['$set'] = {}
        update['$set']['updated_at'] = datetime.now().astimezone()
        data = await collection.find_one_and_update(
            filter, 
            update, 
            return_document=ReturnDocument.AFTER
        )
        if data:
            # 确保_id映射到id字段
            if "_id" in data and "id" not in data:
                data["id"] = data["_id"]
            return cls(**data)
        return None
    
    @classmethod
    async def find_many(cls: Type[T], filter: Dict = None, 
                       sort: List = None, 
                       skip: int = 0, 
                       limit: int = 0) -> List[T]:
        """异步查找多个文档"""
        collection = async_db.get_collection(cls.Config.collection)
        cursor = collection.find(filter or {})
        
        if sort:
            cursor = cursor.sort(sort)
        
        if skip:
            cursor = cursor.skip(skip)
            
        if limit:
            cursor = cursor.limit(limit)
            
        result = []
        async for document in cursor:
            # 确保_id映射到id字段
            if "_id" in document and "id" not in document:
                document["id"] = document["_id"]
            result.append(cls(**document))
        
        return result
    
    @classmethod
    async def count(cls, filter: Dict = None) -> int:
        """异步计算文档数量"""
        collection = async_db.get_collection(cls.Config.collection)
        return await collection.count_documents(filter or {})
    
    @classmethod
    async def aggregate(cls, pipeline: List[Dict]) -> List[Dict]:
        """异步执行聚合查询"""
        collection = async_db.get_collection(cls.Config.collection)
        result = []
        async for document in collection.aggregate(pipeline):
            result.append(document)
        return result
    
    @classmethod
    async def update_one(cls, filter: Dict, update: Dict) -> int:
        """异步更新单个文档"""
        collection = async_db.get_collection(cls.Config.collection)
        result = await collection.update_one(filter, update)
        return result.modified_count

    @classmethod
    async def update_many(cls, filter: Dict, update: Dict) -> int:
        """异步更新多个文档"""
        collection = async_db.get_collection(cls.Config.collection)
        result = await collection.update_many(filter, update)
        return result.modified_count
    
    @classmethod
    async def delete_many(cls, filter: Dict) -> int:
        """异步删除多个文档"""
        collection = async_db.get_collection(cls.Config.collection)
        result = await collection.delete_many(filter)
        return result.deleted_count
    
    @classmethod
    async def create_indexes(cls):
        """异步创建索引"""
        if not cls.Config.indexes:
            return
            
        collection = async_db.get_collection(cls.Config.collection)
        for index in cls.Config.indexes:
            if isinstance(index, str):
                await collection.create_index(index)
            elif isinstance(index, tuple) and len(index) == 2:
                field, direction = index
                await collection.create_index([(field, direction)])
            elif isinstance(index, list):
                await collection.create_index(index)