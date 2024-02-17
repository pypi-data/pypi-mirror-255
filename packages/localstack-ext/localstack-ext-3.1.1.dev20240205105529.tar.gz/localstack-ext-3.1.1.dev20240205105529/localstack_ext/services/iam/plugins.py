from localstack.aws.chain import CompositeHandler
from localstack.http import Router
from localstack.http.dispatcher import Handler as RouteHandler
from localstack_ext.runtime.plugin import ProPlatformPlugin
class IamEnforcementPlugin(ProPlatformPlugin):
	name='iam-enforcement'
	def update_request_handlers(B,handlers):from localstack_ext.services.iam.policy_engine.handler import IamEnforcementHandler as A;handlers.append(A.get())
	def update_gateway_routes(B,router):from localstack_ext.services.iam.router import IAMRouter as A;A(router).register_routes()
	def on_platform_shutdown(B):from localstack_ext.services.iam.policy_generation.policy_generator import PolicyGenerator as A;A.get().shutdown()