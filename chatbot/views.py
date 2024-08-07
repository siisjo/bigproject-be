import os
import json
import openai
import time
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA, ConversationChain
from langchain.memory import ConversationBufferMemory
from django.http import StreamingHttpResponse

from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer, ChatSessionDetailSerializer

with open('secrets.json') as f:
    keys = json.load(f)

OPENAI_API_KEY = keys['openai_api_key']
translation_api_key = keys['google_api_key']

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

chat = ChatOpenAI(model="gpt-3.5-turbo")
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

class OpenAIChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        query = request.data.get('query')
        nation = request.data.get('nation')

        if not session_id:
            return Response({'error': 'Session ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not query:
            return Response({'error': 'Query is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not nation:
            return Response({'error': 'Nation is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 벡터 데이터베이스 로드
        directory = f"./DB/{nation}db"
        database = Chroma(persist_directory=directory, embedding_function=embeddings)

        try:
            session = ChatSession.objects.prefetch_related('chatmessage_set').get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found or access denied.'}, status=status.HTTP_404_NOT_FOUND)

        # 검색기 설정
        k = 3
        retriever = database.as_retriever(search_kwargs={"k": k})

        # ConversationChain 설정
        memory = ConversationBufferMemory()
        conversation = ConversationChain(llm=chat, memory=memory)

        # 이전 대화 불러오기
        previous_messages = session.chatmessage_set.order_by('sent_at')
        for message in previous_messages:
            if message.sender == 1:
                memory.chat_memory.add_user_message(message.message)
            else:
                memory.chat_memory.add_ai_message(message.message)

        # target_language 설정 >> 일 할 국가 nation 설정
        target_language = 'ko' if nation == 'korea' else 'en'

        # 입력 메시지 번역 (얻은 답변을 처음 질문받았을 때의 언어로 번역)
        translated_query, detected_language = self.translate_text(query, target_language)

        result = conversation.predict(input=translated_query)
        translated_result, _ = self.translate_text(result, detected_language)
        
        # 새 메시지 저장
        new_message = ChatMessage(session=session, message=query, sender=1)  # 1 for user
        new_message.save()

        bot_response = ChatMessage(session=session, message=translated_result, sender=0)  # 0 for AI
        bot_response.save()

        # 세션 요약 업데이트 (첫 번째 메시지를 요약으로 사용, 12글자 초과 시 ...로 대체)
        first_message = previous_messages.first().message if previous_messages.exists() else query
        session.summary = first_message if len(first_message) <= 12 else first_message[:9] + '...'
        session.save()

        return Response({"response": translated_result}, status=status.HTTP_200_OK)

    def translate_text(self, text, target_language):
        url = f"https://translation.googleapis.com/language/translate/v2?key={translation_api_key}"
        params = {
            'q': text,
            'target': target_language
        }
        response = requests.post(url, data=params)
        if response.status_code == 200:
            result = response.json()
            translated_text = result['data']['translations'][0]['translatedText']
            detected_language = result['data']['translations'][0]['detectedSourceLanguage']
            return translated_text, detected_language
        else:
            raise Exception(f"Error in translation: {response.status_code}, {response.text}")

# 전체 채팅 세션 나열
class ChatSessionListView(generics.ListAPIView):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).prefetch_related('chatmessage_set')

# 특정 채팅 세션 ID의 정보 및 메시지 나열, 세션 삭제
class ChatSessionDetailView(generics.RetrieveDestroyAPIView):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).prefetch_related('chatmessage_set')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        session = ChatSession.objects.prefetch_related('chatmessage_set').filter(id=instance.id, user=request.user).first()
        if not session:
            return Response({'error': 'Session not found or access denied.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        messages = ChatMessage.objects.filter(session=session).select_related('session')
        messages_serializer = ChatMessageSerializer(messages, many=True)
        data = serializer.data
        data['messages'] = messages_serializer.data
        return Response(data)

# 새 대화 세션 생성
class CreateNewSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session = ChatSession.objects.create(user=request.user)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
