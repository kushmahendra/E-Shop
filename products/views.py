
from django.shortcuts import render
from products.models import Product,Category
from django.db.models import Q

# Create your views here.



def get_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        context = {'product': product}
        total_price = product.price
        
        if request.GET.get('size'):
            size = request.GET.get('size')
            price = product.get_product_price_by_size(size)
            context['selected_size'] = size
            total_price += price
        
        if request.GET.get('color'):
            color = request.GET.get('color')
            price = product.get_product_price_by_color(color)
            context['selected_color'] = color
            total_price += price
        
        context['updated_price'] = total_price
        return render(request, 'product/product.html', context)
    
    except Exception as e:
        print(e)

def products(request):
    query = request.GET.get('query', '')
    category_slug = request.GET.get('category')
    categories = Category.objects.all()
    products = Product.objects.all()

    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug)
            products = products.filter(category=category)
        except Category.DoesNotExist:
            # Handle the case where category_slug does not match any category
            pass

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(product_description__icontains=query) |
            Q(category__category_name__icontains=query)
        )

        if not products:
            return render(request,'base/noitem.html')

    return render(request, 'product/browse.html', {
        'products': products,
        'query': query,
        'categories': categories,
        'category_slug': category_slug
    })
