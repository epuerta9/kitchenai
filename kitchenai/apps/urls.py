from django.urls import path
from kitchenai.apps.views.playground import home, chat_send, clear_chat_history, evaluate_response


app_name = "apps"

urlpatterns = [
    path("playground/", home, name="playground_home"),
    path("playground/chat_send", chat_send, name="playground_chat_send"),
    path("playground/chat/clear/", clear_chat_history, name="playground_clear_chat"),
    path("playground/evaluations/", evaluate_response, name="playground_evaluate"),
]
