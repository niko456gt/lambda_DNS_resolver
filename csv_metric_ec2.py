import json
import boto3
import io
import csv
import datetime

cloudwatch = boto3.client('cloudwatch')
s3 = boto3.client('s3')

INSTANCE_ID = 'i-0'  # replace with your instance ID
BUCKET = ''

def lambda_handler(event, context):
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(hours=24)

    # Define both CPU and Memory metrics
    metric_queries = [
        {
            'Id': 'cpu',
            'MetricStat': {
                'Metric': {
                    'Namespace': 'AWS/EC2',
                    'MetricName': 'CPUUtilization',
                    'Dimensions': [{'Name': 'InstanceId', 'Value': INSTANCE_ID}]
                },
                'Period': 60,
                'Stat': 'Average'
            },
            'ReturnData': True,
        },
        {
            'Id': 'mem',
            'MetricStat': {
                'Metric': {
                    'Namespace': 'CWAgent',
                    'MetricName': 'MemoryUsedPercent',
                    'Dimensions': [{'Name': 'InstanceId', 'Value': INSTANCE_ID}]
                },
                'Period': 60,
                'Stat': 'Average'
            },
            'ReturnData': True,
        }
    ]

    response = cloudwatch.get_metric_data(
        MetricDataQueries=metric_queries,
        StartTime=start,
        EndTime=end
    )

    # Parse results
    cpu_results = next((r for r in response['MetricDataResults'] if r['Id'] == 'cpu'), None)
    mem_results = next((r for r in response['MetricDataResults'] if r['Id'] == 'mem'), None)

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'CPUUtilization', 'MemoryUsedPercent'])

    # Align timestamps and values (CPU & Memory)
    if cpu_results and mem_results:
        # Sort both by timestamp to align
        cpu_data = sorted(zip(cpu_results['Timestamps'], cpu_results['Values']))
        mem_data = sorted(zip(mem_results['Timestamps'], mem_results['Values']))

        # Convert to dict for timestamp alignment
        mem_dict = {t.isoformat(): v for t, v in mem_data}

        for ts, cpu_val in cpu_data:
            ts_str = ts.isoformat()
            mem_val = mem_dict.get(ts_str, '')  # blank if not available
            writer.writerow([ts_str, cpu_val, mem_val])

    # Upload to S3
    s3.put_object(
        Bucket=BUCKET,
        Key=f"reports/ec2_metrics_{end.strftime('%Y%m%d%H')}.csv",
        Body=output.getvalue()
    )

    return {
        'status': 'ok',
        'cpu_points': len(cpu_results['Timestamps']) if cpu_results else 0,
        'mem_points': len(mem_results['Timestamps']) if mem_results else 0
    }
