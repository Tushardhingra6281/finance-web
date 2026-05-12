from rest_framework import serializers
from .models import Companies, Profitandloss, Balancesheet, Cashflow


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Companies
        fields = "__all__"


class ProfitLossSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profitandloss
        fields = "__all__"


class BalanceSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balancesheet
        fields = "__all__"


class CashFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cashflow
        fields = "__all__"