from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
from datetime import datetime
import boto3
from config import Config

class FileUpLoadResource(Resource) :
    
    def post(self) :
        # 1. 클라이언트로부터 데이터를 받아온다
        # request.files에 파일이 들어있다

        if 'photo' not in request.files :
            return {'error' : '파일 업로드하세요'}, 400

        file = request.files['photo']
        print(file)

        # 클라이언트가 보낸 파일의 파일명을 변경시켜서 S3에 올려야 유니크하게 파일을 관리할 수 있다
        
        # 파일명을 유니크하게 만드는 방법
        current_time = datetime.now()
        # 콜론은 파일명에 들어갈 수 없음으로 바꿔준다
        new_file_name = current_time.isoformat().replace(':', '_') + '.jpg'
        
        # 파일명을 유니크한 이름으로 변경한다 (클라이언트에서 보낸 파일명을 대체)
        file.filename = new_file_name
        
        # boto3 라이브러리를 이용해서 S3에 파일을 업로드 한다 (S3의 파일 업로드하는 boto3 라이브러리가 필요)
        # 참고 : 라이브러리 설치는 pip install boto3
        client =  boto3.client('s3', aws_access_key_id= Config.ACCESS_KEY, aws_secret_access_key= Config.SECRET_ACCESS)

        try :
            client.upload_fileobj(file, Config.S3_BUCKET, new_file_name, ExtraArgs= {'ACL' : 'public-read', 'ContentType' : file.content_type})
        
        except Exception as e :
            return {"error" : str(e)}, 500

        return {"result" : "success", "imgUrl" : Config.S3_LOCATION + new_file_name}