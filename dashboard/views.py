from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomLoginForm, CustomRegisterForm, ProfileUpdateForm
from .models import UserProfile, FavoriteCompany
import csv
from django.http import HttpResponse
from django.db.models import Avg, Count
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Companies, Profitandloss, Balancesheet, Cashflow, Documents, FactMlScores
from django.db.models import Avg 



def company_list(request):

    # ========== FIX: TOP ROE — Python mein filter ==========
    all_companies = list(Companies.objects.all())
    top_roe_list = []
    for c in all_companies:
        try:
            roe = float(c.roe_percentage or 0)
            if roe > 0:
                top_roe_list.append((roe, c))
        except (ValueError, TypeError):
            pass
    
    top_roe_list.sort(reverse=True, key=lambda x: x[0])
    top_roe = [c for _, c in top_roe_list[:5]]
    
        # ========== FIX: TOP PROFIT — Python mein filter + Company Name ==========
    all_profits = list(Profitandloss.objects.all())
    top_profit_list = []
    for p in all_profits:
        try:
            profit = float(p.net_profit or 0)
            if profit > 0:
                # Company name fetch kar
                company = Companies.objects.filter(id=p.company_id).first()
                p.company_name = company.company_name if company else "Unknown"
                p.year_display = p.year if p.year else "TTM"
                top_profit_list.append((profit, p))
        except (ValueError, TypeError):
            pass
    
    top_profit_list.sort(reverse=True, key=lambda x: x[0])
    top_profit = [p for _, p in top_profit_list[:5]]
    
    query = request.GET.get('q')
    sector = request.GET.get('sector')

    companies = Companies.objects.all()

    if query:
        companies = companies.filter(
            Q(company_name__icontains=query) |
            Q(id__icontains=query)
        )

    if sector:
        companies = companies.filter(sector=sector)

    sectors = Companies.objects.exclude(sector__isnull=True).values_list('sector', flat=True).distinct()

    top_scores = FactMlScores.objects.all().order_by('-overall_score')[:5]

    context = {
        'companies': companies,
        'query': query,
        'sector': sector,
        'sectors': sectors,
        'top_scores': top_scores,
        'top_roe': top_roe,
        'top_profit': top_profit,
    }

    return render(request, 'dashboard/company_list.html', context)


def company_detail(request, company_id):
    company = get_object_or_404(Companies, id=company_id)

    profits = Profitandloss.objects.filter(company_id=company_id).order_by('year')
    balances = Balancesheet.objects.filter(company_id=company_id).order_by('year')
    cashflows = Cashflow.objects.filter(company_id=company_id).order_by('year')
    documents = Documents.objects.filter(company_id=company_id)

    # ========== CHART DATA ==========
    chart_years = []
    chart_sales = []
    chart_net_profits = []
    chart_operating_profits = []
    chart_eps = []

    for row in profits:
        chart_years.append(str(row.year))
        chart_sales.append(float(row.sales or 0))
        chart_net_profits.append(float(row.net_profit or 0))
        chart_operating_profits.append(float(row.operating_profit or 0))
        chart_eps.append(float(row.eps or 0))

    chart_operating_cf = []
    chart_investing_cf = []
    chart_financing_cf = []
    chart_net_cf = []

    for row in cashflows:
        chart_operating_cf.append(float(row.operating_activity or 0))
        chart_investing_cf.append(float(row.investing_activity or 0))
        chart_financing_cf.append(float(row.financing_activity or 0))
        chart_net_cf.append(float(row.net_cash_flow or 0))

    latest_balance = balances.last()
    latest_total_assets = 0
    latest_total_liabilities = 0
    latest_borrowings = 0
    latest_net_worth = 0

    if latest_balance:
        latest_total_assets = float(latest_balance.total_assets or 0)
        latest_total_liabilities = float(latest_balance.total_liabilities or 0)
        latest_borrowings = float(latest_balance.borrowings or 0)
        latest_net_worth = latest_total_assets - latest_total_liabilities

    context = {
        'company': company,
        'profits': profits,
        'balances': balances,
        'cashflows': cashflows,
        'documents': documents,
        'chart_years': chart_years,
        'chart_sales': chart_sales,
        'chart_net_profits': chart_net_profits,
        'chart_operating_profits': chart_operating_profits,
        'chart_eps': chart_eps,
        'chart_operating_cf': chart_operating_cf,
        'chart_investing_cf': chart_investing_cf,
        'chart_financing_cf': chart_financing_cf,
        'chart_net_cf': chart_net_cf,
        'latest_total_assets': latest_total_assets,
        'latest_total_liabilities': latest_total_liabilities,
        'latest_borrowings': latest_borrowings,
        'latest_net_worth': latest_net_worth,
        'years': chart_years,
        'sales': chart_sales,
        'profits_data': chart_net_profits,
    }

    return render(request, 'dashboard/company_detail.html', context)

# ========== API VIEWS ==========

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import (
    CompanySerializer, 
    ProfitLossSerializer, 
    BalanceSheetSerializer, 
    CashFlowSerializer
)


@api_view(["GET"])
def api_companies(request):
    companies = Companies.objects.all()[:20]
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def api_company_detail(request, company_id):
    company = get_object_or_404(Companies, id=company_id)
    serializer = CompanySerializer(company)
    return Response(serializer.data)


@api_view(["GET"])
def api_profit_loss(request, company_id):
    data = Profitandloss.objects.filter(company_id=company_id)
    serializer = ProfitLossSerializer(data, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def api_balance_sheet(request, company_id):
    data = Balancesheet.objects.filter(company_id=company_id)
    serializer = BalanceSheetSerializer(data, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def api_cash_flow(request, company_id):
    data = Cashflow.objects.filter(company_id=company_id)
    serializer = CashFlowSerializer(data, many=True)
    return Response(serializer.data)


def api_docs(request):
    return render(request, 'dashboard/api_docs.html')


def ml_scores(request):
    scores = FactMlScores.objects.all().order_by('-overall_score')
    context = {
        'scores': scores
    }
    return render(request, 'dashboard/ml_scores.html', context)

def compare_companies(request):

    company1 = request.GET.get('c1')
    company2 = request.GET.get('c2')

    data1 = None
    data2 = None

    if company1:
        data1 = Companies.objects.filter(id=company1).first()

    if company2:
        data2 = Companies.objects.filter(id=company2).first()

    companies = Companies.objects.all()

    context = {
        'companies': companies,
        'data1': data1,
        'data2': data2,
    }

    return render(request, 'dashboard/compare.html', context)

def sector_dashboard(request):

    sector_data = (
        Companies.objects
        .values('sector')
        .annotate(
            total_companies=Count('id'),
            avg_roe=Avg('roe_percentage'),
            avg_roce=Avg('roce_percentage')
        )
        .order_by('-avg_roe')
    )

    context = {
        'sector_data': sector_data
    }

    return render(
        request,
        'dashboard/sector_dashboard.html',
        context
    )

def download_report(request, company_id):
    company = Companies.objects.get(id=company_id)
    profits = Profitandloss.objects.filter(company_id=company_id).order_by('-year')
    balance_sheets = Balancesheet.objects.filter(company_id=company_id).order_by('-year')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{company.company_name.replace(" ", "_")}_Financial_Report.csv"'

    writer = csv.writer(response)

    # ============================================================
    writer.writerow([''])
    writer.writerow([company.company_name.upper()])
    writer.writerow(['FINANCIAL ANALYTICS REPORT'])
    writer.writerow([''])
    
    # COMPANY OVERVIEW
    writer.writerow(['COMPANY OVERVIEW'])
    writer.writerow(['-' * 50])
    writer.writerow(['Sector', getattr(company, 'sector', 'N/A')])
    writer.writerow(['ROE', f'{company.roe_percentage}%' if company.roe_percentage else 'N/A'])
    writer.writerow(['ROCE', f'{company.roce_percentage}%' if company.roce_percentage else 'N/A'])
    writer.writerow(['Book Value', f'Rs.{company.book_value}' if company.book_value else 'N/A'])
    writer.writerow(['Face Value', f'Rs.{company.face_value}' if company.face_value else 'N/A'])
    writer.writerow(['Website', company.website or 'N/A'])
    writer.writerow(['Report Generated', '12-05-2026'])
    writer.writerow([''])
    
    # PROFIT & LOSS
    writer.writerow(['PROFIT & LOSS STATEMENT'])
    writer.writerow(['-' * 50])
    writer.writerow(['Year', 'Sales (Rs. Cr)', 'Operating Profit (Rs. Cr)', 'Net Profit (Rs. Cr)', 'EPS (Rs.)', 'OPM (%)'])
    
    total_sales = 0
    total_profit = 0
    count = 0
    
    for p in profits:
        opm = round((p.operating_profit / p.sales * 100), 2) if p.sales and p.operating_profit else 0
        
        writer.writerow([
            p.year,
            f'Rs.{p.sales:,}' if p.sales else 'Rs.0',
            f'Rs.{p.operating_profit:,}' if p.operating_profit else 'Rs.0',
            f'Rs.{p.net_profit:,}' if p.net_profit else 'Rs.0',
            f'Rs.{p.eps}' if p.eps else 'Rs.0',
            f'{opm}%' if opm else '0%'
        ])
        
        if p.sales:
            total_sales += p.sales
            total_profit += p.net_profit if p.net_profit else 0
            count += 1
    
    if count > 0:
        writer.writerow([''])
        writer.writerow(['SUMMARY'])
        writer.writerow(['-' * 50])
        writer.writerow(['Total Sales (All Years)', f'Rs.{total_sales:,}'])
        writer.writerow(['Total Net Profit', f'Rs.{total_profit:,}'])
        writer.writerow(['Average Sales/Year', f'Rs.{round(total_sales/count):,}'])
        writer.writerow(['Profit Margin', f'{round((total_profit/total_sales)*100, 2)}%'])
    
    writer.writerow([''])
    
    # BALANCE SHEET
    writer.writerow(['BALANCE SHEET'])
    writer.writerow(['-' * 50])
    writer.writerow(['Year', 'Total Assets (Rs. Cr)', 'Total Liabilities (Rs. Cr)', 'Borrowings (Rs. Cr)', 'Debt to Equity', 'Equity Ratio'])
    
    for b in balance_sheets:
        equity_ratio = round((b.total_assets - b.total_liabilities) / b.total_assets * 100, 2) if b.total_assets else 0
        
        writer.writerow([
            b.year,
            f'Rs.{b.total_assets:,}' if b.total_assets else 'Rs.0',
            f'Rs.{b.total_liabilities:,}' if b.total_liabilities else 'Rs.0',
            f'Rs.{b.borrowings:,}' if b.borrowings else 'Rs.0',
            f'{b.debt_to_equity}' if b.debt_to_equity else '0',
            f'{equity_ratio}%'
        ])
    
    writer.writerow([''])
    writer.writerow(['-' * 50])
    writer.writerow(['END OF REPORT'])
    writer.writerow(['-' * 50])
    writer.writerow(['Generated by Stock Analytics Pro | Copyright 2026'])
    writer.writerow([''])

    return response

def recommendation_engine(request):
    """
    ML-based Recommendation Engine
    """
    
    companies = Companies.objects.all()
    recommendations = []
    
    for company in companies:
        # Get latest financial data
        latest_pl = Profitandloss.objects.filter(company_id=company.id).order_by('-year').first()
        latest_bs = Balancesheet.objects.filter(company_id=company.id).order_by('-year').first()
        
        # SKIP if no financial data
        if not latest_pl or not latest_bs:
            continue
        
        # SAFE NUMBER CONVERSION
        roe = float(company.roe_percentage) if company.roe_percentage not in [None, ''] else 0
        roce = float(company.roce_percentage) if company.roce_percentage not in [None, ''] else 0
        
        sales = float(latest_pl.sales) if latest_pl.sales is not None else 0
        net_profit = float(latest_pl.net_profit) if latest_pl.net_profit is not None else 0
        operating_profit = float(latest_pl.operating_profit) if latest_pl.operating_profit is not None else 0
        eps = float(latest_pl.eps) if latest_pl.eps is not None else 0
        
        total_assets = float(latest_bs.total_assets) if latest_bs.total_assets is not None else 0
        total_liabilities = float(latest_bs.total_liabilities) if latest_bs.total_liabilities is not None else 0
        
        dte_raw = latest_bs.debt_to_equity
        dte = float(dte_raw) if dte_raw not in [None, ''] else 0
        
        # ===== ML SCORING =====
        factors = {}
        
        # ROE Score
        if roe > 20: factors['roe_score'] = 25
        elif roe > 15: factors['roe_score'] = 20
        elif roe > 10: factors['roe_score'] = 15
        elif roe > 5: factors['roe_score'] = 10
        else: factors['roe_score'] = max(0, roe * 2)
            
        # ROCE Score
        if roce > 25: factors['roce_score'] = 25
        elif roce > 18: factors['roce_score'] = 20
        elif roce > 12: factors['roce_score'] = 15
        elif roce > 8: factors['roce_score'] = 10
        else: factors['roce_score'] = max(0, roce)
            
        # NPM Score
        npm = (net_profit / sales * 100) if sales > 0 else 0
        if npm > 15: factors['npm_score'] = 20
        elif npm > 10: factors['npm_score'] = 15
        elif npm > 5: factors['npm_score'] = 10
        else: factors['npm_score'] = max(0, npm)
            
        # Growth Score
        prev_pl = Profitandloss.objects.filter(company_id=company.id).order_by('-year')[1:2].first()
        if prev_pl and prev_pl.sales:
            try:
                prev_sales = float(prev_pl.sales)
                sales_growth = ((sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
            except:
                sales_growth = 0
            if sales_growth > 20: factors['growth_score'] = 25
            elif sales_growth > 10: factors['growth_score'] = 20
            elif sales_growth > 5: factors['growth_score'] = 15
            elif sales_growth > 0: factors['growth_score'] = 10
            else: factors['growth_score'] = max(0, 10 + sales_growth)
        else:
            factors['growth_score'] = 10
            
        # Debt Score
        if dte < 0.5: factors['debt_score'] = 25
        elif dte < 1.0: factors['debt_score'] = 20
        elif dte < 1.5: factors['debt_score'] = 15
        elif dte < 2.0: factors['debt_score'] = 10
        else: factors['debt_score'] = max(0, 25 - (dte * 10))
            
        # Asset Score
        prev_bs = Balancesheet.objects.filter(company_id=company.id).order_by('-year')[1:2].first()
        if prev_bs and prev_bs.total_assets:
            try:
                prev_assets = float(prev_bs.total_assets)
                asset_growth = ((total_assets - prev_assets) / prev_assets * 100) if prev_assets > 0 else 0
            except:
                asset_growth = 0
            if asset_growth > 15: factors['asset_score'] = 20
            elif asset_growth > 10: factors['asset_score'] = 15
            elif asset_growth > 5: factors['asset_score'] = 10
            else: factors['asset_score'] = max(0, asset_growth)
        else:
            factors['asset_score'] = 10
            
        # OPM Score
        opm = (operating_profit / sales * 100) if sales > 0 else 0
        if opm > 20: factors['opm_score'] = 25
        elif opm > 15: factors['opm_score'] = 20
        elif opm > 10: factors['opm_score'] = 15
        elif opm > 5: factors['opm_score'] = 10
        else: factors['opm_score'] = max(0, opm)
            
        # EPS Score
        if prev_pl and prev_pl.eps:
            try:
                prev_eps = float(prev_pl.eps)
                eps_growth = ((eps - prev_eps) / prev_eps * 100) if prev_eps > 0 else 0
            except:
                eps_growth = 0
            if eps_growth > 20: factors['eps_score'] = 20
            elif eps_growth > 10: factors['eps_score'] = 15
            elif eps_growth > 5: factors['eps_score'] = 10
            else: factors['eps_score'] = max(0, eps_growth)
        else:
            factors['eps_score'] = 10
        
        # FINAL SCORE
        total_score = (
            factors['roe_score'] * 0.20 +
            factors['roce_score'] * 0.15 +
            factors['npm_score'] * 0.10 +
            factors['growth_score'] * 0.20 +
            factors['debt_score'] * 0.15 +
            factors['asset_score'] * 0.05 +
            factors['opm_score'] * 0.10 +
            factors['eps_score'] * 0.05
        )
        
        total_score = max(0, min(100, total_score))
        
        if total_score >= 80: category = "STRONG BUY"
        elif total_score >= 65: category = "BUY"
        elif total_score >= 50: category = "HOLD"
        elif total_score >= 35: category = "WEAK HOLD"
        else: category = "AVOID"
        
        recommendations.append({
            'company': company,
            'score': round(total_score, 2),
            'category': category,
            'factors': factors,
            'latest_pl': latest_pl,
            'latest_bs': latest_bs
        })
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    context = {
        'recommendations': recommendations[:10],
        'total_companies': len(recommendations),
        'avg_score': round(sum(r['score'] for r in recommendations) / len(recommendations), 2) if recommendations else 0,
    }
    
    return render(request, 'recommendations.html', context)

def sector_recommendations(request, sector_name):
    """
    Get recommendations for a specific sector
    """
    companies = Companies.objects.filter(sector__icontains=sector_name)
    
    recommendations = []
    
    for company in companies:
        latest_pl = Profitandloss.objects.filter(company_id=company.id).order_by('-year').first()
        latest_bs = Balancesheet.objects.filter(company_id=company.id).order_by('-year').first()
        
        if not latest_pl or not latest_bs:
            continue
            
        roe = float(company.roe_percentage) if company.roe_percentage else 0
        roce = float(company.roce_percentage) if company.roce_percentage else 0
        npm = (latest_pl.net_profit / latest_pl.sales * 100) if latest_pl.sales else 0
        dte = float(latest_bs.debt_to_equity) if latest_bs.debt_to_equity else 0
        
        score = (roe * 0.3) + (roce * 0.25) + (npm * 0.2) + ((2 - dte) * 10 * 0.25)
        score = min(100, max(0, score))
        
        if score >= 75:
            category = "TOP PICK"
        elif score >= 60:
            category = "RECOMMENDED"
        elif score >= 45:
            category = "MODERATE"
        else:
            category = "AVOID"
        
        recommendations.append({
            'company': company,
            'score': round(score, 2),
            'category': category,
            'roe': roe,
            'roce': roce,
            'npm': round(npm, 2),
            'dte': dte
        })
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    context = {
        'sector': sector_name.upper(),
        'recommendations': recommendations[:5],
        'total': len(recommendations)
    }
    
    return render(request, 'sector_recommendations.html', context)

def recommendation_engine(request):
    """
    ML-based Recommendation Engine
    """
    
    companies = Companies.objects.all()
    recommendations = []
    
    for company in companies:
        # Get latest financial data
        latest_pl = Profitandloss.objects.filter(company_id=company.id).order_by('-year').first()
        latest_bs = Balancesheet.objects.filter(company_id=company.id).order_by('-year').first()
        
        # SKIP if no financial data
        if not latest_pl or not latest_bs:
            continue
        
        # SAFE NUMBER CONVERSION
        roe = float(company.roe_percentage) if company.roe_percentage not in [None, ''] else 0
        roce = float(company.roce_percentage) if company.roce_percentage not in [None, ''] else 0
        
        sales = float(latest_pl.sales) if latest_pl.sales is not None else 0
        net_profit = float(latest_pl.net_profit) if latest_pl.net_profit is not None else 0
        operating_profit = float(latest_pl.operating_profit) if latest_pl.operating_profit is not None else 0
        eps = float(latest_pl.eps) if latest_pl.eps is not None else 0
        
        total_assets = float(latest_bs.total_assets) if latest_bs.total_assets is not None else 0
        total_liabilities = float(latest_bs.total_liabilities) if latest_bs.total_liabilities is not None else 0
        
        dte_raw = latest_bs.debt_to_equity
        dte = float(dte_raw) if dte_raw not in [None, ''] else 0
        
        # ===== ML SCORING =====
        factors = {}
        
        # ROE Score
        if roe > 20: factors['roe_score'] = 25
        elif roe > 15: factors['roe_score'] = 20
        elif roe > 10: factors['roe_score'] = 15
        elif roe > 5: factors['roe_score'] = 10
        else: factors['roe_score'] = max(0, roe * 2)
            
        # ROCE Score
        if roce > 25: factors['roce_score'] = 25
        elif roce > 18: factors['roce_score'] = 20
        elif roce > 12: factors['roce_score'] = 15
        elif roce > 8: factors['roce_score'] = 10
        else: factors['roce_score'] = max(0, roce)
            
        # NPM Score
        npm = (net_profit / sales * 100) if sales > 0 else 0
        if npm > 15: factors['npm_score'] = 20
        elif npm > 10: factors['npm_score'] = 15
        elif npm > 5: factors['npm_score'] = 10
        else: factors['npm_score'] = max(0, npm)
            
        # Growth Score
        prev_pl = Profitandloss.objects.filter(company_id=company.id).order_by('-year')[1:2].first()
        if prev_pl and prev_pl.sales:
            try:
                prev_sales = float(prev_pl.sales)
                sales_growth = ((sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
            except:
                sales_growth = 0
            if sales_growth > 20: factors['growth_score'] = 25
            elif sales_growth > 10: factors['growth_score'] = 20
            elif sales_growth > 5: factors['growth_score'] = 15
            elif sales_growth > 0: factors['growth_score'] = 10
            else: factors['growth_score'] = max(0, 10 + sales_growth)
        else:
            factors['growth_score'] = 10
            
        # Debt Score
        if dte < 0.5: factors['debt_score'] = 25
        elif dte < 1.0: factors['debt_score'] = 20
        elif dte < 1.5: factors['debt_score'] = 15
        elif dte < 2.0: factors['debt_score'] = 10
        else: factors['debt_score'] = max(0, 25 - (dte * 10))
            
        # Asset Score
        prev_bs = Balancesheet.objects.filter(company_id=company.id).order_by('-year')[1:2].first()
        if prev_bs and prev_bs.total_assets:
            try:
                prev_assets = float(prev_bs.total_assets)
                asset_growth = ((total_assets - prev_assets) / prev_assets * 100) if prev_assets > 0 else 0
            except:
                asset_growth = 0
            if asset_growth > 15: factors['asset_score'] = 20
            elif asset_growth > 10: factors['asset_score'] = 15
            elif asset_growth > 5: factors['asset_score'] = 10
            else: factors['asset_score'] = max(0, asset_growth)
        else:
            factors['asset_score'] = 10
            
        # OPM Score
        opm = (operating_profit / sales * 100) if sales > 0 else 0
        if opm > 20: factors['opm_score'] = 25
        elif opm > 15: factors['opm_score'] = 20
        elif opm > 10: factors['opm_score'] = 15
        elif opm > 5: factors['opm_score'] = 10
        else: factors['opm_score'] = max(0, opm)
            
        # EPS Score
        if prev_pl and prev_pl.eps:
            try:
                prev_eps = float(prev_pl.eps)
                eps_growth = ((eps - prev_eps) / prev_eps * 100) if prev_eps > 0 else 0
            except:
                eps_growth = 0
            if eps_growth > 20: factors['eps_score'] = 20
            elif eps_growth > 10: factors['eps_score'] = 15
            elif eps_growth > 5: factors['eps_score'] = 10
            else: factors['eps_score'] = max(0, eps_growth)
        else:
            factors['eps_score'] = 10
        
        # FINAL SCORE
        total_score = (
            factors['roe_score'] * 0.20 +
            factors['roce_score'] * 0.15 +
            factors['npm_score'] * 0.10 +
            factors['growth_score'] * 0.20 +
            factors['debt_score'] * 0.15 +
            factors['asset_score'] * 0.05 +
            factors['opm_score'] * 0.10 +
            factors['eps_score'] * 0.05
        )
        
        total_score = max(0, min(100, total_score))
        
        if total_score >= 80: category = "STRONG BUY"
        elif total_score >= 65: category = "BUY"
        elif total_score >= 50: category = "HOLD"
        elif total_score >= 35: category = "WEAK HOLD"
        else: category = "AVOID"
        
        recommendations.append({
            'company': company,
            'score': round(total_score, 2),
            'category': category,
            'factors': factors,
            'latest_pl': latest_pl,
            'latest_bs': latest_bs
        })
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    context = {
        'recommendations': recommendations[:10],
        'total_companies': len(recommendations),
        'avg_score': round(sum(r['score'] for r in recommendations) / len(recommendations), 2) if recommendations else 0,
    }
    
    return render(request, 'recommendations.html', context)

# views.py mein add karein (line ~459 ke aas paas ya end mein):

def ai_recommendations(request):
    """AI Recommendation Engine - Full analysis page"""
    from django.db.models import Avg
    
    companies = Company.objects.all()
    total_companies = companies.count()
    
    recommendations = []
    
    for company in companies:
        latest_pl = ProfitLoss.objects.filter(company=company).order_by('-year').first()
        prev_pl = ProfitLoss.objects.filter(company=company).order_by('-year')[1:2].first()
        
        if not latest_pl:
            continue
            
        # Safe EPS growth calculation
        if latest_pl.eps is not None and prev_pl and prev_pl.eps is not None and prev_pl.eps != 0:
            eps_growth = ((latest_pl.eps - prev_pl.eps) / prev_pl.eps) * 100
        else:
            eps_growth = 0
            
        # Safe ROE
        roe = company.roe_percentage or 0
        
        # Safe ROCE  
        roce = company.roce_percentage or 0
        
        # Safe OPM
        opm = latest_pl.opm_percentage or 0 if hasattr(latest_pl, 'opm_percentage') else 0
        
        # Safe Debt (lower is better)
        debt = latest_pl.debt_to_equity or 0 if hasattr(latest_pl, 'debt_to_equity') else 0
        
        # Scoring (0-100)
        roe_score = min(roe * 2, 100)
        roce_score = min(roce * 2, 100)
        growth_score = min(max(eps_growth, 0), 100)
        debt_score = max(0, 100 - debt * 10)
        opm_score = min(opm * 3, 100)
        
        overall_score = (roe_score + roce_score + growth_score + debt_score + opm_score) / 5
        
        # Category
        if overall_score >= 60:
            category = "STRONG BUY"
        elif overall_score >= 40:
            category = "BUY"
        elif overall_score >= 25:
            category = "HOLD"
        else:
            category = "AVOID"
            
        recommendations.append({
            'company': company,
            'score': round(overall_score, 2),
            'category': category,
            'factors': {
                'roe_score': round(roe_score, 1),
                'roce_score': round(roce_score, 1),
                'growth_score': round(growth_score, 1),
                'debt_score': round(debt_score, 1),
                'opm_score': round(opm_score, 1),
            },
            'latest_pl': latest_pl,
        })
    
    # Sort by score descending
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    top_10 = recommendations[:10]
    
    # Calculate average score
    avg_score = round(sum(r['score'] for r in recommendations) / len(recommendations), 2) if recommendations else 0
    
    return render(request, 'dashboard/ai_recommendation_engine.html', {
        'recommendations': top_10,
        'total_companies': total_companies,
        'avg_score': avg_score,
    })

# ========== AUTHENTICATION VIEWS ==========

def user_login(request):
    if request.user.is_authenticated:
        return redirect('personal_dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('personal_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'dashboard/login.html', {'form': form})

def user_register(request):
    if request.user.is_authenticated:
        return redirect('personal_dashboard')
    
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', '')
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('personal_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomRegisterForm()
    
    return render(request, 'dashboard/register.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('company_list')

@login_required
def personal_dashboard(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    favorites = FavoriteCompany.objects.filter(user=user).select_related('company')
    recent_favorites = favorites.order_by('-added_at')[:5]
    
    top_favorites = []
    for fav in favorites:
        try:
            score = FactMlScores.objects.filter(company_id=fav.company.id).first()
            if score:
                top_favorites.append({
                    'company': fav.company,
                    'score': score.overall_score,
                    'health_label': score.health_label
                })
        except:
            pass
    
    top_favorites.sort(key=lambda x: x['score'], reverse=True)
    
    context = {
        'user': user,
        'profile': profile,
        'favorites': favorites,
        'recent_favorites': recent_favorites,
        'top_favorites': top_favorites[:5],
        'total_favorites': favorites.count(),
    }
    
    return render(request, 'dashboard/personal_dashboard.html', context)

@login_required
def add_favorite(request, company_id):
    if request.method == 'POST':
        company = get_object_or_404(Companies, id=company_id)
        favorite, created = FavoriteCompany.objects.get_or_create(
            user=request.user,
            company=company
        )
        
        if created:
            return JsonResponse({'status': 'added', 'message': 'Added to favorites'})
        else:
            favorite.delete()
            return JsonResponse({'status': 'removed', 'message': 'Removed from favorites'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def remove_favorite(request, company_id):
    if request.method == 'POST':
        favorite = FavoriteCompany.objects.filter(
            user=request.user,
            company_id=company_id
        ).first()
        
        if favorite:
            favorite.delete()
            messages.success(request, 'Company removed from favorites.')
        
        return redirect('personal_dashboard')
    return redirect('personal_dashboard')

@login_required
def update_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('personal_dashboard')
    else:
        form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'dashboard/update_profile.html', {'form': form})