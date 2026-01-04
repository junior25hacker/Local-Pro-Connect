from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from requests.models import PriceRange, ServiceRequest

u,_=User.objects.get_or_create(username='req_quick', defaults={'email':'req_quick@example.com'})
u.set_password('pass12345'); u.save()
client=Client(); assert client.login(username='req_quick', password='pass12345')
pr,_=PriceRange.objects.get_or_create(label='$50-$100', defaults={'min_price':50,'max_price':100})
url=reverse('requests:create_request')
post={
  'provider_choice':'',
  'provider_name':'Wirna Email Co',
  'description':'Hanging submit fix test',
  'urgent':'on',
  'price_range':str(pr.id),
}
resp=client.post(url, post, follow=False)
print('Status:', resp.status_code)
last=ServiceRequest.objects.order_by('-id').first()
print('Last request:', last.id if last else None, last.provider_name if last else None)
