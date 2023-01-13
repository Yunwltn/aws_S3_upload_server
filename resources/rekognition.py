from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
from datetime import datetime
import boto3
from config import Config

class ObjectDetectionResource(Resource) :

    # S3에 저장되어 있는 이미지를 객체 탐지하는 API만들기
    def get(self) :

        # 클라이언트로부터 파일명을 받아온다
        filename = request.args.get('filename')

        # 위의 파일은 이미 S3에 있다는 상황
        # 따라서 aws의 Rekognition 인공지능 서비스를 이용해서 object detection 한다

        # 리코그니션 서비스를 이용할 수 있는지 IAM의 유저 권한 확인하고 설정해준다
        client = boto3.client('rekognition', 'ap-northeast-2', aws_access_key_id= Config.ACCESS_KEY, aws_secret_access_key= Config.SECRET_ACCESS)

        # 메뉴얼 확인
        response = client.detect_labels(Image= {'S3Object' : {'Bucket' : Config.S3_BUCKET, 'Name' : filename}}, MaxLabels= 10)

        print(response)

        for label in response['Labels']:
            print ("Label: " + label['Name'])
            print ("Confidence: " + str(label['Confidence']))
            print ("Instances:")
            for instance in label['Instances']:
                print ("  Bounding box")
                print ("    Top: " + str(instance['BoundingBox']['Top']))
                print ("    Left: " + str(instance['BoundingBox']['Left']))
                print ("    Width: " +  str(instance['BoundingBox']['Width']))
                print ("    Height: " +  str(instance['BoundingBox']['Height']))
                print ("  Confidence: " + str(instance['Confidence']))
                print()

            print ("Parents:")
            for parent in label['Parents']:
                print ("   " + parent['Name'])
            print ("----------")
            print ()

        return {"result" : "success", "Labels" : response['Labels']}, 200

class PhotoRekognitionResource(Resource) :

    def post(self) :

        if 'photo' not in request.files :
            return {'error' : '파일 업로드하세요'}, 400

        file = request.files['photo']

        current_time = datetime.now()
        new_file_name = current_time.isoformat().replace(':', '_') + '.jpg'
        file.filename = new_file_name
        
        client =  boto3.client('s3', aws_access_key_id= Config.ACCESS_KEY, aws_secret_access_key= Config.SECRET_ACCESS)

        try :
            client.upload_fileobj(file, Config.S3_BUCKET, new_file_name, ExtraArgs= {'ACL' : 'public-read', 'ContentType' : file.content_type})
        
        except Exception as e :
            return {"error" : str(e)}, 500

        client = boto3.client('rekognition', 'ap-northeast-2', aws_access_key_id= Config.ACCESS_KEY, aws_secret_access_key= Config.SECRET_ACCESS)

        response = client.detect_labels(Image= {'S3Object' : {'Bucket' : Config.S3_BUCKET, 'Name' : new_file_name}}, MaxLabels= 10)

        print(response)

        # 위의 response에서 필요한 데이터만 가져와서 클라이언트에게 보내준다
        # Labels : ['cat', 'dog', ..]
        name_list = []
        for i in response['Labels'] :
            name_list.append(i['Name'])

        return {"result" : "success", "Labels" : name_list}, 200