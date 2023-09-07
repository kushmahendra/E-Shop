from django.db import models
from django.utils.text import slugify
# Create your models here.
from base.models import BaseModel


class Category(BaseModel):
    category_name=models.CharField(max_length=100)
    category_image=models.ImageField(upload_to='categories')
    #Important field
    slug=models.SlugField(unique=True,null=True,blank=True)


    def save(self, *args,**kwargs):
        self.slug=slugify(self.category_name)
        super(Category,self).save(*args,**kwargs)
    
    def __str__(self):
        return self.category_name
    
    class Meta:
        verbose_name_plural='Categories'







class ColorVariant(BaseModel):
    color_name=models.CharField(max_length=100)
    
    price=models.IntegerField(default=0)

    def __str__(self):
        return self.color_name

class SizeVariant(BaseModel):
    size_name=models.CharField(max_length=100)
    price=models.IntegerField(default=0)

    def __str__(self):
        return self.size_name


class Product(BaseModel):
    product_name=models.CharField(max_length=100)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products')
    price=models.FloatField()
    product_description=models.TextField()
    #Immportant Field
    slug=models.SlugField(unique=True,null=True,blank=True)
    color_variant=models.ManyToManyField(ColorVariant,blank=True)
    size_variant=models.ManyToManyField(SizeVariant,blank=True)



    def save(self, *args,**kwargs):
        self.slug=slugify(self.product_name)
        super(Product,self).save(*args,**kwargs)
    
    def __str__(self):
        return self.product_name
    
    class Meta:
        verbose_name_plural='Products'

    def get_product_price_by_size(self,size):
        return SizeVariant.objects.get(size_name=size).price
    
    def get_product_price_by_color(self,color):
        return ColorVariant.objects.get(color_name=color).price
    

class ProductImage(BaseModel):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product_images')
    image=models.ImageField(upload_to='products')

    def __str__(self):
        return self.product.product_name

class Coupon(BaseModel):
    coupon_code=models.CharField(max_length=10)
    is_expired=models.BooleanField(default=False)
    discount_price=models.IntegerField(default=100)
    minimum_amount=models.IntegerField(default=500)

    def __str__(self):
        return self.coupon_code