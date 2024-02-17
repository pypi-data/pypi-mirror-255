import requests
import io

def upload_by_fragments(filepath: str, resumable_session_url: str, chunk_size: int = 1024*1024*32):
    """
    Upload a file to the Hectiq Console using the resumable upload method.

    Do not use this method directly, use `upload_file` instead.

    Args:
        filepath (str): Path to the local file to upload
        resumable_session_url (str): Resumable session url
        chunk_size (int, optional): Chunk size in bytes. Defaults to 32Mb.
    """
    try:
        from tqdm import tqdm
        use_tqdm = True
    except ImportError:
        use_tqdm = False
    from google.resumable_media.requests import ResumableUpload
    upload = ResumableUpload(
        upload_url=resumable_session_url,
        chunk_size=chunk_size
    )
    data = open(filepath, 'rb').read()
    upload._stream = io.BytesIO(data)
    upload._total_bytes = len(data)
    upload._resumable_url = resumable_session_url
    
    transport = requests.Session()
    if use_tqdm:
        progress_bar = tqdm(total=upload.total_bytes, unit='iB', unit_scale=True)

    bytes_uploaded = 0
    while upload.finished==False:
        res = upload.transmit_next_chunk(transport)
        if use_tqdm:
            progress_bar.update(upload.bytes_uploaded-bytes_uploaded)
        bytes_uploaded = upload.bytes_uploaded
        assert res.status_code in [200,308], f'An error occured while uploading the file {filepath}\n{res.status_code}:: {res.text}'
    return 

def upload_with_signed_url(filepath: str, bucket_name: str, url: str, fields: dict):
    """Upload a file to the Hectiq Console using the signed url.

    Do not use this method directly, use `upload_file` instead.

    Args:
        filepath (str): Path to the local file to upload
        bucket_name (str): Bucket name
        url (str): Signed url
        fields (dict): Signed fields
    """
    content_bytes = open(filepath, "rb")
    files = {"file": (bucket_name, content_bytes)}
    requests.post(url, data=fields, files=files)

def upload_file(filepath: str, policy: dict):
    """
    Upload a file to the Hectiq Console using the signed policy.

    Args:
        filepath (str): Path to the local file to upload
        policy (dict): Signed policy with keys: 
            - "policy": dict with keys "url" and "fields"
            - "bucket_name": str
            - "upload_method": str (optional, default "single")
    """

    upload_method = policy.get('upload_method')
    if upload_method=='fragment':
        upload_by_fragments(filepath, 
                            resumable_session_url=policy.get('url'))
    else:
        creds = policy.get('policy')
        upload_with_signed_url(filepath, 
                            bucket_name=policy.get('bucket_name'),
                            url=creds.get('url'),
                            fields=creds.get('fields'))

    return