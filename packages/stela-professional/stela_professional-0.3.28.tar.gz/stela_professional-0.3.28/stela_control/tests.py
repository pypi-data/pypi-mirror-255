from django.conf import settings

# Create your tests here.
import boto3

# Configura tus credenciales y la región
client = boto3.client('product_advertising_api', 
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, 
                      region_name='us-west-2')

# Hacer una llamada al API
response = client.item_search(
    Query='Harry Potter books',
    SearchIndex='All'
)

print(response)