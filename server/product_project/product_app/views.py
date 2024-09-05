from django.shortcuts import render
from .serializers import ProductSerializer
from .models import Product
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework.filters import OrderingFilter
import pandas as pd

# Create your views here.
class ProductAPI(ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [OrderingFilter]
    ordering = 'product_category'

    def post(self, request):
        print(request.data)

        if request.data.get('file'):
            if request.data.get('file').name.endswith('xlsx') or request.data.get('file').name.endwith('xls'):
                df = pd.read_excel(request.data.get('file'))
                columns = { 'product_id' , 'product_name', 'product_category', 'product_price', 
                           'product_expiry_date', 'product_manufacturing_date', 'product_HSN_no', 'product_quantity' }
                
                if columns.issubset(df.columns):
                    data = []
                    for index, series in df.iterrows():
                        d = { "product_id" : series['product_id'],
                             "product_name" : series['product_name'],
                             "product_category" : series['product_category'],
                             "product_price" : series['product_price'],
                             "product_expiry_date" : series['product_expiry_date'].date(),
                             "product_manufacturing_date" : series['product_manufacturing_date'].date(),
                             "product_HSN_no" : series['product_HSN_no'],
                             "product_quantity" : series['product_quantity'] }
                        
                        if d not in data and not Product.objects.filter(product_id=d['product_id']).exists():
                            data.append(d)
                    print(data)

                    serializer = ProductSerializer(data=data, many=True)

                    if serializer.is_valid():
                        serializer.save()
                        return Response(data=serializer.data, status=201)
                    return Response(data=serializer.errors, status=400)
                return Response(data={"error": f'Missing columns - {columns-set(df.columns)}'}, status=400)
            return Response(data={"error": "must provide xlsx/xls file"}, status=400)

                        

