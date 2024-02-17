_J='version'
_I='versions'
_H='services'
_G='status'
_F='service'
_E='message'
_D='event'
_C=True
_B=False
_A=None
import io,json,logging,os,zipfile
from abc import ABC,abstractmethod
from functools import singledispatch
from pathlib import Path
from typing import Dict,List,Optional,Tuple,TypedDict,Union
from urllib.parse import urlparse
import click,requests,yaml
from click import ClickException
from localstack import config,constants
from localstack.cli import console
from localstack.constants import APPLICATION_JSON,HEADER_CONTENT_TYPE
from localstack.utils.bootstrap import in_ci
from localstack.utils.files import load_file,save_file
from localstack.utils.http import safe_requests
from localstack.utils.strings import to_str
from packaging import version
from requests.structures import CaseInsensitiveDict
from rich.progress import Progress
from localstack_ext.bootstrap import auth
from localstack_ext.bootstrap.auth import get_platform_auth_headers
from localstack_ext.bootstrap.pods.constants import INTERNAL_REQUEST_PARAMS_HEADER
from localstack_ext.bootstrap.pods.remotes.api import CloudPodsRemotesClient
from localstack_ext.bootstrap.pods.remotes.configs import RemoteConfig,RemoteConfigParams
from localstack_ext.bootstrap.pods.remotes.params import get_remote_params_callable
from localstack_ext.config import POD_LOAD_CLI_TIMEOUT
from localstack_ext.constants import API_PATH_PODS,CLOUDPODS_METADATA_FILE
LOG=logging.getLogger(__name__)
HEADER_LS_API_KEY='ls-api-key'
HEADER_LS_VERSION='ls-version'
HEADER_AUTHORIZATION='Authorization'
class PodInfo(TypedDict,total=_B):name:str;pod_id:str;version:int;services:List[str];description:str;size:int;remote:str;localstack_version:str
def get_state_zip_from_instance(services=_A):
	C=services;G=f"{get_pods_endpoint()}/state";H=','.join(C)if C else'';I={INTERNAL_REQUEST_PARAMS_HEADER:'{}'};D=in_ci();A=requests.get(G,params={_H:H},headers=I,stream=not D);J=int(A.headers.get('Content-Length',0));B=A.content if D else b''
	with Progress()as E:
		K=E.add_task('Retrieving state from the container',total=J)
		for F in A.iter_content(chunk_size=100000):B+=F;E.update(K,advance=len(F))
	L=PodInfo(services=A.headers.get('x-localstack-pod-services','').split(','),size=int(A.headers.get('x-localstack-pod-size',0)))
	if not A.ok:raise Exception(f"An error occurred while retrieving the LocalStack state (code {A.status_code}): {B})")
	return B,L
class CloudPodRemoteAttributes(TypedDict,total=_B):is_public:bool;description:Optional[str];services:Optional[List[str]]
class PodSaveRequest(TypedDict,total=_B):remote:Optional[Dict[str,Union[str,Dict]]];attributes:Optional[CloudPodRemoteAttributes]
class CloudPodsService(ABC):
	@abstractmethod
	def save(self,pod_name,attributes=_A,remote=_A,local=_B,version=_A):0
	@abstractmethod
	def delete(self,pod_name,remote=_A,delete_from_remote=_C):0
	@abstractmethod
	def load(self,pod_name,remote=_A,version=_A,merge_strategy=_A,ignore_version_mismatches=_C):0
	@abstractmethod
	def list(self,remote=_A):0
	@abstractmethod
	def get_versions(self,pod_name,remote=_A):0
	def _get_cloud_pods_info(C,pod_name):
		B=pod_name;A=requests.get(create_platform_url(B),headers=get_platform_auth_headers())
		if not A.ok:_raise_exception_with_formatted_message(f"Unable to get into for pod: {B}",A)
		return json.loads(A.content)
	def _get_localstack_pod_version(G,pod_name,version=_A,cloud_pods_dict=_A):
		C=pod_name;B=cloud_pods_dict;A=version
		if not B:B=G._get_cloud_pods_info(C)
		D=B[_I];E=int(B['max_version'])
		if A and A>E:raise Exception(f"Unable to load pod {C} with version {A}. The maximum version available in the remote storage is {E}")
		F=list(filter(lambda v:v[_J]==A,D));H=F[0]if F else D[-1];I=H['localstack_version'];return I
	def get_metamodel(B,pod_name,version):
		A=requests.get(url=f"{get_pods_endpoint()}/state/metamodel",headers=_get_headers())
		if not A.ok:_raise_exception_with_formatted_message(f"Unable to get metamodel for pod {pod_name}",A)
		return json.loads(A.content)
	def set_remote_attributes(G,pod_name,attributes,remote=_A):
		D='is_public';C=remote;B=pod_name
		if C:LOG.debug(f"Trying to set attributes for remote '{C}'. Currently we support attributes only for the default remote");return
		E=create_platform_url(B);F=auth.get_auth_headers();A=safe_requests.patch(E,headers=F,json={D:attributes[D]})
		if not A.ok:raise Exception(f"Error setting remote attributes for Cloud Pod {B} (code {A.status_code}): {A.text}")
def _get_headers():
	B={HEADER_CONTENT_TYPE:APPLICATION_JSON};C=CaseInsensitiveDict(auth.get_auth_headers())
	for A in(HEADER_AUTHORIZATION,HEADER_LS_API_KEY,HEADER_LS_VERSION):
		if C.get(A):B[A]=C[A]
	return B
def _raise_exception_with_formatted_message(message,response):raise Exception(f"{message}: {response.text}")
def _get_remote_params_payload(remote):
	A=remote
	if not A:return{}
	C=_get_remote_configuration(A,render_params=_B);B=get_remote_params_callable(C.remote_url)
	if not B:return{}
	A.remote_params=B();return{'remote':A.to_dict()}
class CloudPodsClient(CloudPodsService):
	def __init__(A,interactive=_B):A.interactive=interactive
	def _process_response(J,response,message):
		F='operation';C=message;B=console.status(C);B.start()
		for G in response.iter_lines():
			A=json.loads(G)
			if A[_D]=='log':B.update(A[_E])
			if A[_D]==_F:D,H,E=A[_F],A[_G],A[F];C=f"{D}: {E} succeeded"if H=='ok'else f"{D}: {E} failed";B.update(C)
			elif A[_D]=='completion':
				B.stop()
				if A[_G]=='error':raise Exception(A.get(_E))
				if A[F]=='save':I=PodInfo(**A['info']);return I
		B.stop()
	def save(F,pod_name,attributes=_A,remote=_A,local=_B,version=_A):
		G=version;C=pod_name;D=f"{get_pods_endpoint()}/{C}?"
		if local:D+='&local=true'
		if G:D+=f"&version={G}"
		H=_get_remote_params_payload(remote);H.update({'attributes':attributes});B=requests.post(url=D,json=H,headers=_get_headers(),stream=_C)
		if not B.ok:_raise_exception_with_formatted_message(f"Unable to save pod {C}",B)
		E={}
		if F.interactive:E=F._process_response(B,message=f"Saving Cloud Pod {C}")
		else:
			for A in B.iter_lines():
				A=json.loads(A)
				if A[_D]=='pod_info':E=PodInfo(**A['extra'])
				elif A[_D]=='exception':raise Exception(A[_E])
		return E
	def delete(E,pod_name,remote=_A,delete_from_remote=_C):
		A=pod_name;B=f"{get_pods_endpoint()}/{A}"
		if not delete_from_remote:B+='?local=true'
		D=_get_remote_params_payload(remote);C=requests.delete(url=B,json=D,headers=_get_headers())
		if not C.ok:_raise_exception_with_formatted_message(f"Unable to delete Cloud Pod '{A}'",C)
	def load(B,pod_name,remote=_A,version=_A,merge_strategy=_A,ignore_version_mismatches=_B):
		E=ignore_version_mismatches;C=version;A=pod_name
		if in_ci():E=_C
		if not E:
			F=B._get_localstack_pod_version(pod_name=A,version=C);G=get_ls_version_from_health()
			if not is_compatible_version(F,G)and not click.confirm(f"This Cloud Pod was created with LocalStack {F} but you are running LocalStack {G}. Cloud Pods might be incompatible across different LocalStack versions.\nLoading a Cloud Pod with mismatching version might lead to a corrupted state of the emulator. Do you want to continue?"):raise click.Abort('LocalStack version mismatch')
		H=f"{get_pods_endpoint()}/{A}"
		if C:H+=f"?version={C}"
		I=_get_remote_params_payload(remote);D=requests.put(url=H,json=I,headers=_get_headers(),stream=_C)
		if not D.ok:_raise_exception_with_formatted_message(f"Unable to load pod {A}",D)
		if B.interactive:B._process_response(D,message=f"Loading Cloud Pod {A}")
	def list(C,remote=_A):
		B=_get_remote_params_payload(remote);A=requests.get(url=get_pods_endpoint(),json=B,headers=_get_headers())
		if not A.ok:_raise_exception_with_formatted_message('Unable to list Cloud Pods',A)
		return json.loads(A.content).get('cloudpods',[])
	def get_versions(D,pod_name,remote=_A):
		B=pod_name;C=_get_remote_params_payload(remote);A=requests.get(url=f"{get_pods_endpoint()}/{B}/versions",json=C,headers=_get_headers())
		if A.status_code==404:raise Exception(f"Cloud Pod {B} not found")
		if not A.ok:_raise_exception_with_formatted_message(f"Unable to get versions for pod {B}",A)
		return json.loads(A.content).get(_I,[])
def _get_remote_configuration(params,render_params=_C):
	A=params;D=CloudPodsRemotesClient()
	try:C=D.get_remote(name=A.remote_name)
	except Exception as E:raise ClickException(f"Error getting configuration for the remote {A.remote_name}")from E
	B=C['remote_url']
	if render_params:B=A.render_url(B)
	LOG.debug('Remote configuration: %s',C);return RemoteConfig(remote_url=B)
def get_pods_endpoint():A=config.external_service_url();return f"{A}{API_PATH_PODS}"
class StateService:
	def export_pod(I,target,services=_A):
		C=target;D=urlparse(C);A=os.path.abspath(os.path.join(D.netloc,D.path));E=Path(A).parent.absolute()
		if not os.path.exists(E):raise Exception(f"{E} is not a valid path")
		G,F=get_state_zip_from_instance(services=services);save_file(file=A,content=G);B=get_environment_metadata();B['name']=os.path.basename(C);B.update(F)
		with zipfile.ZipFile(file=A,mode='a')as H:H.writestr(CLOUDPODS_METADATA_FILE,yaml.dump(B))
		return F
	def import_pod(I,source,show_progress=_C):
		E='pro';B=urlparse(source);A=os.path.abspath(os.path.join(B.netloc,B.path))
		if not os.path.exists(A):raise Exception(f"Path {A} does not exist")
		if not os.path.isfile(A):raise Exception(f"Path {A} is not a file")
		C=load_file(A,mode='rb');F=zipfile.ZipFile(io.BytesIO(C),'r');D=read_metadata_from_pod(F)or{};G=D.get(_H,[]);H=get_environment_metadata().get(E)
		if D.get(E,_B)and not H:console.print('Warning: You are trying to load a Cloud Pod generated with a Pro license.The loaded state might be incomplete.')
		load_local_state(content=C,number_services=len(G),show_progress=show_progress)
def list_public_pods():
	B=create_platform_url('public');C=auth.get_auth_headers();A=safe_requests.get(B,headers=C)
	if not A.ok:raise Exception(to_str(A.content))
	D=json.loads(A.content);return[A['pod_name']for A in D]
@singledispatch
def read_metadata_from_pod(zip_file):
	try:A=yaml.safe_load(zip_file.read(CLOUDPODS_METADATA_FILE));return A
	except KeyError:LOG.debug('No %s file in the archive',CLOUDPODS_METADATA_FILE)
@read_metadata_from_pod.register(bytes)
def _(zip_file):A=zip_file;A=zipfile.ZipFile(io.BytesIO(A),'r');return read_metadata_from_pod(A)
@read_metadata_from_pod.register(str)
def _(zip_file):
	with zipfile.ZipFile(zip_file)as A:return read_metadata_from_pod(A)
def call_post_load_endpoint(content,stream):
	B=stream;C=get_pods_endpoint()
	try:
		A=requests.post(C,data=content,timeout=POD_LOAD_CLI_TIMEOUT,stream=B)
		if not B:LOG.debug('Loaded services from local state file: %s',A.content)
	except requests.exceptions.Timeout as D:raise Exception('Timeout exceed for the pod load operation. To avoid this issue, try to increase thevalue of the POD_LOAD_CLI_TIMEOUT configuration variable.')from D
	if not A.ok:raise Exception(f"Unable to load LocalStack state via {C}")
	return A
def load_state_with_progress_bar(content,number_services=0):
	A=content;D=call_post_load_endpoint(A,stream=_C);C=0
	with Progress()as B:
		E=B.add_task('Loading state',total=number_services)
		for F in D.iter_lines():A=json.loads(F);LOG.debug('Loaded service: %s',A);G,H=A[_F],'✅'if A[_G]else'❌';B.log(f"{G}: {H}");C+=1;B.update(E,completed=C)
def load_local_state(content,number_services=0,show_progress=_C):
	A=content
	if show_progress:load_state_with_progress_bar(content=A,number_services=number_services)
	else:call_post_load_endpoint(content=A,stream=_B)
def get_environment_metadata():
	C=get_pods_endpoint();A=f"{C}/environment";B=requests.get(A)
	if not B.ok:raise Exception(f"Unable to retrieve environment metadata from {A}")
	return json.loads(B.content)
def reset_state(services=_A):
	B=services
	def C(_url):
		A=requests.post(_url)
		if not A.ok:LOG.debug('Reset call to %s failed: status code %s',_url,A.status_code);raise Exception('Failed to reset LocalStack')
	if not B:A=f"{config.external_service_url()}/_localstack/state/reset";C(A);return
	for D in B:A=f"{config.external_service_url()}/_localstack/state/{D}/reset";C(A)
def get_ls_version_from_health():
	try:A=f"{config.external_service_url()}/_localstack/health";B=requests.get(A).json();return B[_J]
	except Exception:return''
def create_platform_url(path=_A,api_endpoint=_A):
	B=api_endpoint;A=path;B=B or constants.API_ENDPOINT;C=f"{B}/cloudpods"
	if not A:return C
	A=A if A.startswith('/')else f"/{A}";return f"{C}{A}"
def is_compatible_version(version_one,version_two):
	B=version_two;A=version_one
	if not A or not B:return _B
	C=version.parse(A);D=version.parse(B);return C.base_version==D.base_version