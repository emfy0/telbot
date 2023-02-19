import asyncio
import logging

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions
import csv
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

import re
import psycopg2
import sklearn
import numpy as np


morph = pymorphy2.MorphAnalyzer(lang='ru')

from config import TOKEN

logging.basicConfig(
    format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
    level=logging.INFO
)


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

  
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(
        'Привет!\nИспользуй команду /help, чтобы узнать список доступных команд!'
    )


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    msg = text(
        bold('Я могу ответить на следующие команды:'),
        '/help', '/ask', '/psychologist', '/stop', sep='\n'
    )
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    executor.start_polling(dp)

btn = types.InlineKeyboardButton(text='Нажми на меня', url='')


conn = psycopg2.connect(dbname='energy', user='mao', password='darin', host='localhost')
cursor = conn.cursor()

morph = pymorphy2.MorphAnalyzer(lang='ru')

answer_id=[]
answer = dict()

cursor.execute('SELECT id, answer FROM app.chats_answer;')
records = cursor.fetchall()
for row in records:
    answer[row[1]]=row[1]

questions=[] 

cursor.execute('SELECT question, answer_id FROM app.chats_question;')
records = cursor.fetchall()

transform=0

for row in records:
    if row[1]>0:
        phrases=row[0]
        words=phrases.split(' ')
        phrase=""

        for word in words:
            word = morph.parse(word)[0].normal_form

        phrase = phrase + word + " "

        if (len(phrase) > 0):
            questions.append(phrase.strip())
            answer_id.append(row[1])
            transform = transform + 1

print (questions)
print (answer)
print (answer_id)

cursor.close()
conn.close()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

vectorizer_q = TfidfVectorizer()
vectorizer_q.fit(questions)
matrix_big_q = vectorizer_q.transform(questions)
print("Размер матрицы: ")
print(matrix_big_q.shape)

if transform > 200:
    transform = 200

svd_q = TruncatedSVD(n_components=transform)
svd_q.fit(matrix_big_q)


matrix_small_q = svd_q.transform(matrix_big_q)

print ("Коэффициент уменьшения матрицы: ")
print ( svd_q.explained_variance_ratio_.sum())

from sklearn.neighbors import BallTree
from sklearn.base import BaseEstimator

def softmax(x):
    proba = np.exp(-x)
    return proba / sum(proba)

class NeighborSampler(BaseEstimator):
    def __init__(self, k=5, temperature=10.0):
        self.k=k
        self.temperature = temperature
    def fit(self, X, y):
        self.tree_ = BallTree(X)
        self.y_ = np.array(y)
    def predict(self, X, random_state=None):
        distances, indices = self.tree_.query(X, return_distance=True, k=self.k)
        result = []
        for distance, index in zip(distances, indices):
            result.append(np.random.choice(index, p=softmax(distance * self.temperature)))
        return self.y_[result]

from sklearn.pipeline import make_pipeline

ns_q = NeighborSampler()


ns_q.fit(matrix_small_q, answer_id) 
pipe_q = make_pipeline(vectorizer_q, svd_q, ns_q)
