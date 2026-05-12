# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.models import User
from django.db import models


class Companies(models.Model):
    id = models.TextField(primary_key=True)
    company_logo = models.TextField(blank=True, null=True)
    company_name = models.TextField(blank=True, null=True)
    sector = models.TextField(blank=True, null=True)
    chart_link = models.TextField(blank=True, null=True)
    about_company = models.TextField(blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    nse_profile = models.TextField(blank=True, null=True)
    bse_profile = models.TextField(blank=True, null=True)
    face_value = models.FloatField(blank=True, null=True)
    book_value = models.FloatField(blank=True, null=True)
    roce_percentage = models.FloatField(blank=True, null=True)
    roe_percentage = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'companies'


class Profitandloss(models.Model):
    id = models.IntegerField(primary_key=True)
    company_id = models.TextField(blank=True, null=True)
    year = models.TextField(blank=True, null=True)
    sales = models.BigIntegerField(blank=True, null=True)
    expenses = models.BigIntegerField(blank=True, null=True)
    operating_profit = models.FloatField(blank=True, null=True)
    opm_percentage = models.FloatField(blank=True, null=True)
    other_income = models.BigIntegerField(blank=True, null=True)
    interest = models.BigIntegerField(blank=True, null=True)
    depreciation = models.BigIntegerField(blank=True, null=True)
    profit_before_tax = models.BigIntegerField(blank=True, null=True)
    tax_percentage = models.FloatField(blank=True, null=True)
    net_profit = models.BigIntegerField(blank=True, null=True)
    eps = models.FloatField(blank=True, null=True)
    dividend_payout = models.FloatField(blank=True, null=True)
    net_profit_margin = models.FloatField(blank=True, null=True)
    expense_ratio = models.FloatField(blank=True, null=True)
    interest_coverage = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profitandloss'


class Balancesheet(models.Model):
    id = models.IntegerField(primary_key=True)
    company_id = models.TextField(blank=True, null=True)
    year = models.TextField(blank=True, null=True)
    equity_capital = models.FloatField(blank=True, null=True)
    reserves = models.BigIntegerField(blank=True, null=True)
    borrowings = models.BigIntegerField(blank=True, null=True)
    other_liabilities = models.BigIntegerField(blank=True, null=True)
    total_liabilities = models.BigIntegerField(blank=True, null=True)
    fixed_assets = models.BigIntegerField(blank=True, null=True)
    cwip = models.BigIntegerField(blank=True, null=True)
    investments = models.BigIntegerField(blank=True, null=True)
    other_asset = models.BigIntegerField(blank=True, null=True)
    total_assets = models.BigIntegerField(blank=True, null=True)
    debt_to_equity = models.FloatField(blank=True, null=True)
    equity_ratio = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'balancesheet'


class Cashflow(models.Model):
    id = models.IntegerField(primary_key=True)
    company_id = models.TextField(blank=True, null=True)
    year = models.TextField(blank=True, null=True)
    operating_activity = models.FloatField(blank=True, null=True)
    investing_activity = models.FloatField(blank=True, null=True)
    financing_activity = models.FloatField(blank=True, null=True)
    net_cash_flow = models.FloatField(blank=True, null=True)
    free_cash_flow = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cashflow'


class Analysis(models.Model):
    id = models.IntegerField(primary_key=True)
    company_id = models.TextField(blank=True, null=True)
    compounded_sales_growth = models.TextField(blank=True, null=True)
    compounded_profit_growth = models.TextField(blank=True, null=True)
    stock_price_cagr = models.TextField(blank=True, null=True)
    roe = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'analysis'


class Documents(models.Model):
    id = models.IntegerField(primary_key=True)
    company_id = models.TextField(blank=True, null=True)
    year = models.BigIntegerField(blank=True, null=True)
    annual_report = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documents'


class Prosandcons(models.Model):
    id = models.IntegerField(primary_key=True)
    company_id = models.TextField(blank=True, null=True)
    pros = models.TextField(blank=True, null=True)
    cons = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prosandcons'


class FactMlScores(models.Model):
    company_id = models.TextField(primary_key=True)
    company_name = models.TextField(blank=True, null=True)
    computed_at = models.DateTimeField(blank=True, null=True)

    overall_score = models.FloatField(blank=True, null=True)
    profitability_score = models.FloatField(blank=True, null=True)
    growth_score = models.FloatField(blank=True, null=True)
    leverage_score = models.FloatField(blank=True, null=True)
    cashflow_score = models.FloatField(blank=True, null=True)
    stability_score = models.FloatField(blank=True, null=True)

    health_label = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fact_ml_scores'


# ============================================================
# AUTHENTICATION MODELS (Managed by Django)
# ============================================================

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True  # Django manages this table

    def __str__(self):
        return f"{self.user.username}'s Profile"


class FavoriteCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    company_id = models.CharField(max_length=255, default='')  # ✅ YE HONA CHAHIYE
    company_name = models.CharField(max_length=255, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = True
        unique_together = ('user', 'company_id')