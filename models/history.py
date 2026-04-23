from extensions import mongo
from bson.objectid import ObjectId
from datetime import datetime, UTC


class History:
    @staticmethod
    def save(user_id, question, answer, mode):
        doc = {
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "mode": mode,
            "created_at": datetime.now(UTC)
        }
        mongo.db.history.insert_one(doc)

    @staticmethod
    def get_by_user(user_id, limit=20):
        items = list(
            mongo.db.history
            .find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(limit)
        )
        for it in items:
            it["_id"] = str(it["_id"])
            it["created_at"] = it["created_at"].isoformat()
        return items

    @staticmethod
    def delete(user_id, item_id):
        try:
            result = mongo.db.history.delete_one({
                "_id": ObjectId(item_id),
                "user_id": user_id
            })
            return result.deleted_count == 1
        except Exception:
            return False
