from flask import Flask, url_for, send_from_directory, request
import logging, os
from werkzeug import secure_filename
import speech_recognition as sr
import subprocess
import os.path
import json
import re
from difflib import SequenceMatcher
import diff_match_patch as dmp_module
import nltk
from nltk import word_tokenize
from ftfy import fix_encoding
from flaskext.mysql import MySQL
import codecs
import time
import random
import string


app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
mysql2 = MySQL()

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#real database
app.config['MYSQL_DATABASE_USER'] = ''
app.config['MYSQL_DATABASE_PASSWORD'] = 'D'
app.config['MYSQL_DATABASE_DB'] = 'moodle'
app.config['MYSQL_DATABASE_HOST'] = ''
mysql2.init_app(app)


def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

def randomString(stringLength=4):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

@app.route('/', methods=['POST'])
def api_root():
    app.logger.info(PROJECT_HOME)
    if request.method == 'POST' and request.files['file']:
        localtime = time.asctime(time.localtime(time.time()))
        app.logger.info(app.config['UPLOAD_FOLDER'])
        img = request.files['file']
        type = request.form['type']
        questionid = request.form['questionid']
        img_name = secure_filename(img.filename)
        create_new_folder(app.config['UPLOAD_FOLDER'])
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
        app.logger.info("saving {}".format(saved_path))
        img.save(saved_path)

        subprocess.call(['ffmpeg', '-i', saved_path, img_name + '.wav', '-y'])
        # convert file to wav
        statbuf = os.stat(img_name + '.wav')
        mbytes = statbuf.st_size / 1024
        duration = (mbytes / 128)
        r = sr.Recognizer()

        audio = img_name + '.wav'
        with sr.AudioFile(audio) as source:
            audio = r.record(source)
            print('Done!')

        try:
            text = r.recognize_google(audio)
            speech_text = text.lower()
            print(speech_text)

            if (type not in ['P1', 'P2', 'P3', 'P4']):
                return json.dumps(
                    {'status': 400, 'speech_result': speech_text, 'message': 'Body truyền sai type câu hỏi', 'time_created':localtime},
                    ensure_ascii=False)
            if (type == "P1"):

                cursor = mysql2.connect().cursor()
                query_test = "SELECT graderinfo from top_qtype_poodllrecording_opts WHERE questionid = " + questionid
                cursor.execute(query_test)
                data = cursor.fetchone()
                if data is None:
                    return json.dumps(
                        {'status': 400, 'speech_result': speech_text, 'message': 'API truyền sai questionid', 'time_created':localtime},
                        ensure_ascii=False)
                myresult = data[0]

                convert_to_string = str(myresult)

                answer = convert_to_string.lower()

                print(answer)

                right_word = ""
                wrong_word = ""

                print(speech_text, "texxtttt")

                if (speech_text == answer):
                    p_result = "right"
                    ratio = 1
                    right_word = answer
                else:
                    p_result = "wrong"
                    ratio = 0
                    wrong_word = answer
                result = {'status': 200,'speech_result': speech_text, 'answer': answer, 'result': p_result, 'ratio': ratio,
                          'right_word': right_word, 'wrong_word': wrong_word, 'time_created': localtime}
            if (type == "P2"):

                cursor = mysql2.connect().cursor()
                query_test = "SELECT graderinfo from top_qtype_poodllrecording_opts WHERE questionid = " + questionid
                cursor.execute(query_test)
                data = cursor.fetchone()

                print("dataa", data)
                if data is None:
                    return json.dumps(
                        {'status': 400, 'speech_result': speech_text, 'message': 'API truyền sai questionid', 'time_created':localtime},
                        ensure_ascii=False)
                myresult = data[0]

                print(myresult)

                convert_to_string = str(myresult)

                answer = convert_to_string.lower()
                answer_from_database = convert_to_string.lower()

                print(answer_from_database)

                if "," in answer_from_database:
                    print("right database")
                else:
                    return json.dumps({'status': 204,'speech_result': speech_text, 'message': 'trường graderinfo thiếu dấu ,', 'time_created': localtime},
                                      ensure_ascii=False)

                answer_array = answer_from_database.split(",")

                compare_text = fix_encoding(answer_array[0])

                answer = answer_array[1]

                document_1_words = speech_text.split()
                document_2_words = answer.split()

                common = set(document_1_words).intersection(set(document_2_words))
                right_words = list(common)

                speech_list = re.findall(r'\w+', speech_text)

                answer_list = re.findall(r'\w+', answer)

                wrong_words = list(set(answer_list) - set(speech_list))

                if len(wrong_words) == 0:
                    ratio = 100
                else:
                    ratio = round(((len(right_words) / len(answer.split())) * 100), 0)

                num_of_word = len(speech_text.split())

                if (ratio < 100):
                    p_result = 'wrong'
                else:
                    p_result = 'right'
                word_per_min = round((num_of_word / duration) * 60, 0)

                if (word_per_min < 130):
                    speed = 'chậm'
                if (word_per_min >= 130 and word_per_min < 160):
                    speed = 'khá chậm'
                if (word_per_min < 190 and word_per_min >= 160):
                    speed = 'trung bình'
                if (word_per_min < 220 and word_per_min >= 190):
                    speed = 'khá nhanh'
                if (word_per_min > 220):
                    speed = 'nhanh'

                result = {'status': 200,'speech_result': speech_text, 'answer': answer, 'result': p_result, 'wpm': word_per_min,
                          'speed': speed, 'ratio': ratio, 'wrong_word': wrong_words, 'right_word': right_words,
                          'compare_text': compare_text, 'time_created': localtime}
            if (type == "P3"):
                cursor = mysql2.connect().cursor()
                query_test = "SELECT graderinfo from top_qtype_poodllrecording_opts WHERE questionid = " + questionid
                cursor.execute(query_test)
                data = cursor.fetchone()
                if data is None:
                    return json.dumps(
                        {'status': 400, 'speech_result': speech_text, 'message': 'API truyền sai questionid', 'time_created':localtime},
                        ensure_ascii=False)
                myresult = data[0]

                convert_to_string = str(myresult)

                answer = convert_to_string.lower()

                document_1_words = speech_text.split()
                document_2_words = answer.split()

                common = set(document_1_words).intersection(set(document_2_words))
                right_words = list(common)

                speech_list = re.findall(r'\w+', speech_text)

                answer_list = re.findall(r'\w+', answer)

                wrong_words = list(set(answer_list) - set(speech_list))

                if len(wrong_words) == 0:
                    ratio = 100
                else:
                    ratio = round(((len(right_words) / len(answer.split())) * 100), 0)

                num_of_word = len(speech_text.split())

                if (ratio < 100):
                    p_result = 'wrong'
                else:
                    p_result = 'right'
                word_per_min = round((num_of_word / duration) * 60, 0)

                if (word_per_min < 130):
                    speed = 'chậm'
                if (word_per_min >= 130 and word_per_min < 160):
                    speed = 'khá chậm'
                if (word_per_min < 190 and word_per_min >= 160):
                    speed = 'trung bình'
                if (word_per_min < 220 and word_per_min >= 190):
                    speed = 'khá nhanh'
                if (word_per_min > 220):
                    speed = 'nhanh'
                result = {'status': 200,'speech_result': speech_text, 'answer': answer, 'result': p_result, 'wpm': word_per_min,
                          'speed': speed, 'ratio': ratio, 'wrong_word': wrong_words, 'right_word': right_words, 'time_created': localtime}
            if (type == "P4"):
                cursor = mysql2.connect().cursor()
                query_test = "SELECT graderinfo from top_qtype_poodllrecording_opts WHERE questionid = " + questionid
                cursor.execute(query_test)
                data = cursor.fetchone()
                if data is None:
                    return json.dumps(
                        {'status': 400, 'speech_result': speech_text, 'message': 'API truyền sai questionid', 'time_created':localtime},
                        ensure_ascii=False)
                myresult = data[0]

                convert_to_string = str(myresult)

                answer_from_database = convert_to_string.lower()

                print(answer_from_database)

                if "," in answer_from_database:
                    print("right database")
                else:
                    return json.dumps({'status': 204,'speech_result': speech_text, 'message': 'trường graderinfo thiếu dấu ,', 'time_created':localtime},
                                      ensure_ascii=False)

                answer_array = answer_from_database.split(",")

                compare_text = answer_array[0]

                answer = answer_array[1]

                document_1_words = speech_text.split()
                document_2_words = answer.split()

                common = set(document_1_words).intersection(set(document_2_words))
                right_words = list(common)

                speech_list = re.findall(r'\w+', speech_text)

                answer_list = re.findall(r'\w+', answer)

                wrong_words = list(set(answer_list) - set(speech_list))

                if len(wrong_words) == 0:
                    ratio = 100
                else:
                    ratio = round(((len(right_words) / len(answer.split())) * 100), 0)

                num_of_word = len(speech_text.split())

                if (ratio < 100):
                    p_result = 'wrong'
                else:
                    p_result = 'right'
                word_per_min = round((num_of_word / duration) * 60, 0)

                if (word_per_min < 130):
                    speed = 'chậm'
                if (word_per_min >= 130 and word_per_min < 160):
                    speed = 'khá chậm'
                if (word_per_min < 190 and word_per_min >= 160):
                    speed = 'trung bình'
                if (word_per_min < 220 and word_per_min >= 190):
                    speed = 'khá nhanh'
                if (word_per_min > 220):
                    speed = 'nhanh'

                # using nltk to analysis sentence structure
                student_sentence = word_tokenize(speech_text)
                sentence_struct = nltk.pos_tag(student_sentence)
                predicted_tense = ""
                tense = {}
                tense["future"] = len([word for word in sentence_struct if word[1] in ["VBC", "VBF"]])
                tense["present"] = len([word for word in sentence_struct if word[1] in ["VBP", "VBZ", "VBG"]])
                tense["past"] = len([word for word in sentence_struct if word[1] in ["VBD"]])
                tense["present_con"] = len([word for word in sentence_struct if word[1] in ["VBG"]])
                tense["present_per"] = len([word for word in sentence_struct if word[1] in ["VBN"]])

                if tense["future"] == 1:
                    predicted_tense = "thì tương lai đơn"
                if tense["present"] == 1:
                    predicted_tense = "thì hiện tại đơn"
                if tense["past"] == 1:
                    predicted_tense = "thì quá khứ đơn"
                if tense["present_con"] == 1:
                    predicted_tense = "thì hiện tại tiếp diễn"
                if tense["present_per"] == 1:
                    predicted_tense = "thì hiện tại hoàn thành"


                if predicted_tense == "":
                    if "can't" in speech_text:
                        predicted_tense = "thì hiện tại đơn"
                    if "will" in speech_text:
                        predicted_tense = "thì tương lai đơn"
                    if "won't" in speech_text:
                        predicted_tense = "thì tương lai đơn"
                    if "can" in speech_text:
                        predicted_tense = "thì hiện tại đơn"
                    if "could" in speech_text:
                        predicted_tense = "thì quá khứ đơn"
                    if "would" in speech_text:
                        predicted_tense = "thì quá khứ đơn"


                if predicted_tense == compare_text:
                    student_tense = "Dùng đúng thời"
                else:
                    student_tense = "Dùng sai thời"

                result = {'status': 200,'speech_result': speech_text, 'answer': answer, 'result': p_result, 'wpm': word_per_min,
                          'speed': speed, 'ratio': ratio, 'wrong_word': wrong_words, 'right_word': right_words,
                          "predicted_tense": predicted_tense, "student_tense": student_tense,
                          "right_tense": compare_text, 'time_created': localtime}
            return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            print(e)
            # cursor = mysql2.connect().cursor()
            # query_test = "SELECT graderinfo from top_qtype_poodllrecording_opts WHERE questionid = " + questionid
            # cursor.execute(query_test)
            # data = cursor.fetchone()
            # if data is None:
            #     return json.dumps(
            #         {'status': 400, 'speech_result': "bạn nói không rõ từ", 'message': 'API truyền sai questionid',
            #          'time_created': localtime},
            #         ensure_ascii=False)
            # myresult = data[0]
            #
            # convert_to_string = str(myresult)
            #
            # answer = convert_to_string.lower()
            # return json.dumps(
            #     {'status': 200,'speech_result': answer + randomString(4),'answer': answer, 'result': 'wrong', 'ratio': 0,
            #         'time_created': localtime},
            #     ensure_ascii=False)

            if(type == "P1"):
                cursor = mysql2.connect().cursor()
                query_test = "SELECT graderinfo from top_qtype_poodllrecording_opts WHERE questionid = " + questionid
                cursor.execute(query_test)
                data = cursor.fetchone()
                if data is None:
                    return json.dumps(
                        {'status': 400, 'speech_result': "bạn nói không rõ từ", 'message': 'API truyền sai questionid',
                         'time_created': localtime},
                        ensure_ascii=False)
                myresult = data[0]

                convert_to_string = str(myresult)

                answer = convert_to_string.lower()
                return json.dumps(
                    {'status': 200,'speech_result': answer + randomString(4),'answer': answer, 'wrong_word': answer, 'result': 'wrong', 'ratio': 0,
                        'time_created': localtime},
                    ensure_ascii=False)
            else:
                cursor = mysql2.connect().cursor()
                query_test = "SELECT graderinfo from top_qtype_poodllrecording_opts WHERE questionid = " + questionid
                cursor.execute(query_test)
                data = cursor.fetchone()
                if data is None:
                    return json.dumps(
                        {'status': 400, 'speech_result': "bạn nói không rõ từ", 'message': 'API truyền sai questionid',
                         'time_created': localtime},
                        ensure_ascii=False)
                myresult = data[0]

                convert_to_string = str(myresult)

                answer = convert_to_string.lower()
                return json.dumps(
                    {'status': 200,'speech_result': 'bạn nói không rõ tiếng','answer': answer, 'result': 'wrong', 'ratio': 0,
                        'time_created': localtime},
                    ensure_ascii=False)
    else:
        return "upload failed"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='1234', debug=False)
