from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config
from resources.image import FileUpLoadResource
from resources.posting import PostingResource
from resources.rekognition import ObjectDetectionResource, PhotoRekognitionResource

app = Flask(__name__)

app.config.from_object(Config)

jwt = JWTManager(app)

api = Api(app)
api.add_resource(FileUpLoadResource, '/upload')
api.add_resource(ObjectDetectionResource, '/object_detection')
api.add_resource(PhotoRekognitionResource, '/get_photo_labels')
api.add_resource(PostingResource, '/posting')

if __name__ == '__main__' :
    app.run()   