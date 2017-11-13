import boto3

config = dict(
    region_name='us-west-2',
)


def get_job(transcoder_job_id: str):
    et = boto3.client(
        'elastictranscoder',
        region_name=config['region_name']
    )
    return et.read_job(Id=transcoder_job_id)


def get_job_status(transcoder_job_id: str):
    return get_job(transcoder_job_id)['Job']['Status']


def extract_errors(transcoder_job: dict):
    from funcy import merge, where, lpluck
    job = transcoder_job['Job']
    outputs = merge(job['Outputs'], job['Playlists'])
    return lpluck('StatusDetail', where(outputs, Status='Error'))
