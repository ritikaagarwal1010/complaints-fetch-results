import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    print(event)
    
    # Initialize a session using Amazon DynamoDB
    dynamodb = boto3.resource('dynamodb')
    
    # Replace 'your_table_name' with your DynamoDB table name
    table_crl = dynamodb.Table('mq-qms-inference-results')
    table_priority = dynamodb.Table('mq-qms-priority-results')
    
    # Replace 'primary_key_value' with the value of your primary key
    content = json.loads(event["body"])
    
    try:
        response = table_crl.get_item(
            Key={
                'uuid': content['uuid']
            }
        )
        item_crl = response.get('Item')
        response_priority = table_priority.get_item(
            Key={
                'uuid': content['uuid']
            }
        )
        item_priority = response_priority.get('Item')
        print(item_priority)
        item_priority = eval(item_priority['results'])
        item_crl = eval(item_crl['results'])
        
        # Merge the results dictionaries
        combined_results = {**item_priority, **item_crl}
        
        # Create the combined dictionary
        
        ''' Should be dynamic; Author: Pratik '''
        shap_key = "model/shap_img_tmp/temp.html"
        
        ''' End '''
        
        shap_url = create_presigned_urls(shap_key)
        print(shap_url)
        combined = {
            'uuid': content['uuid'],  # Both x and y have the same uuid
            'results': combined_results,
            'shap_url': shap_url
        }
        
        # Print the combined dictionary
        print(combined)
        
       
        if item_crl:
            print("Item found:")
            print(item_crl)
            return {
                'statusCode': 200,
                'body': json.dumps(combined)
            }
        else:
            print("Item not found")
    except ClientError as e:
        print(f"Error querying item: {e.response['Error']['Message']}")
        
        
def create_presigned_urls(file_key):
    ''' Shap Presigned generation : Pratik '''
    
    bucket_name =  "qms-complaints-file-storage"
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': file_key}, ExpiresIn=300)
    
    # Code to send entire HTML #
    
    # s3 = boto3.resource('s3')
    # obj = s3.Object(bucket_name, file_key)
    # body = obj.get()['Body'].read().decode('utf-8') 
    # print(body)
    return url