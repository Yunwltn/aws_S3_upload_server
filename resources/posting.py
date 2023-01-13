from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
from datetime import datetime
import boto3
from config import Config

class PostingResource(Resource) :

    def post(slef) :
        # 1. 클라이언트로부터 데이터를 받아온다
        # from=data
        # photo : file
        # content : text

        # 사진과 내용은 필수항목이다 세이프코딩
        if 'photo' not in request.files or 'content' not in request.form :
            return {'error' : '데이터를 정확히 보내세요'}, 400
        
        file = request.files['photo']
        content = request.form['content']

        # 이미지가 아닐때 세이프코딩
        if 'image' not in file.content_type :
            return {'error' : '이미지 파일이 아닙니다.'}

        # 2. 사진을 먼저 S3에 저장한다
        current_time = datetime.now()
        # 콜론은 파일명에 들어갈 수 없음으로 바꿔준다
        new_file_name = current_time.isoformat().replace(':', '_') + '.' + file.content_type.split('/')[-1]
        # 파일명을 유니크한 이름으로 변경한다 (클라이언트에서 보낸 파일명을 대체)
        file.filename = new_file_name
        
        # boto3 라이브러리를 이용해서 S3에 파일을 업로드 한다
        client =  boto3.client('s3', aws_access_key_id= Config.ACCESS_KEY, aws_secret_access_key= Config.SECRET_ACCESS)

        try :
            client.upload_fileobj(file, Config.S3_BUCKET, new_file_name, ExtraArgs= {'ACL' : 'public-read', 'ContentType' : file.content_type})
        
        except Exception as e :
            return {"error" : str(e)}, 500

        # 3. 저장된 사진의 imgUrl을 만든다
        imgUrl = Config.S3_LOCATION + new_file_name

        # 4. DB에 저장한다
        try :
            connection = get_connection()

            query = '''insert into
                    posting(content, imgUrl)
                    values (%s, %s);'''

            record = (content, imgUrl)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success"}, 200

