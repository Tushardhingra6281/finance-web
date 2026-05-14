from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_list, name='company_list'),
    path('company/<str:company_id>/', views.company_detail, name='company_detail'),

    path('api/companies/', views.api_companies, name='api_companies'),
    path('api/company/<str:company_id>/', views.api_company_detail, name='api_company_detail'),
    path('api/profit/<str:company_id>/', views.api_profit_loss, name='api_profit_loss'),
    path('api/balance/<str:company_id>/', views.api_balance_sheet, name='api_balance_sheet'),
    path('api/cashflow/<str:company_id>/', views.api_cash_flow, name='api_cash_flow'),
    path('api-docs/', views.api_docs, name='api_docs'),
    path('ml-scores/', views.ml_scores, name='ml_scores'),
    path('compare/', views.compare_companies, name='compare_companies'),
    path('sectors/', views.sector_dashboard, name='sector_dashboard'),
    path('download/<str:company_id>/', views.download_report, name='download_report'),
    path('recommendations/', views.recommendation_engine, name='recommendations'),
    path('recommendations/<str:sector_name>/', views.sector_recommendations, name='sector_recommendations'),
    path('ai-recommendations/', views.recommendation_engine, name='ai_recommendations'),
    path('', views.company_list, name='company_list'),
    path('company/<int:company_id>/', views.company_detail, name='company_detail'),
    path('ml-scores/', views.ml_scores, name='ml_scores'),
    path('compare/', views.compare_companies, name='compare_companies'),
    path('sector/', views.sector_dashboard, name='sector_dashboard'),
    path('download/<int:company_id>/', views.download_report, name='download_report'),
    path('recommendations/', views.recommendation_engine, name='recommendation_engine'),
    path('api/docs/', views.api_docs, name='api_docs'),
    
    # 
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.personal_dashboard, name='personal_dashboard'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('favorite/add/<int:company_id>/', views.add_favorite, name='add_favorite'),
    path('favorite/remove/<int:company_id>/', views.remove_favorite, name='remove_favorite'),
]
