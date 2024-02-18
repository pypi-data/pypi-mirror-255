import boto3
from .base import Base


s3 = boto3.client("s3")

class S3(Base):
    pass


def get_s3_file_size(bucket: str, key: str) -> int:
    file_size = 0
    response = s3.head_object(Bucket=bucket, Key=key)
    if response:
        file_size = int(response.get('ContentLength'))
    return file_size


MB = 1024 * 1024 * 1024
def stream_s3_file(bucket: str, key: str, chunk_bytes=50 * MB):
    file_size = get_s3_file_size(bucket, key)
    input_serialization = {}
    if key.endswith("csv"):
        input_serialization["CSV"] = {
            'FileHeaderInfo': 'USE',
            'FieldDelimiter': ',',
            'RecordDelimiter': '\n'
        }

    for start in range(0, file_size, chunk_bytes):
        end = min(chunk_bytes, file_size)
        response = s3.select_object_content(
            Bucket=bucket,
            Key=key,
            ExpressionType='SQL',
            Expression='SELECT * FROM S3Object',
            InputSerialization=input_serialization,
            OutputSerialization={
                'JSON': {
                    'RecordDelimiter': ','
                }
            },
            ScanRange={
                'Start': start,
                'End': end
            },
        )
        result = b""
        for event in response['Payload']:
            if records := event.get('Records'):
                result += records['Payload']
        yield from eval(result.decode('utf-8'))