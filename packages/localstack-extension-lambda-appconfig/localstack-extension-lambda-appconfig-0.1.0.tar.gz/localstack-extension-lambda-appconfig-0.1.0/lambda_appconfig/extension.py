import logging
import os
from ssl import (
    OP_NO_COMPRESSION,
    Purpose,
    SSLContext,
    SSLObject,
    TLSVersion,
    create_default_context,
)

from hypercorn import Config
from localstack import config
from localstack.constants import DEFAULT_VOLUME_DIR
from localstack.extensions.api import Extension
from localstack.http import route
from localstack.services.lambda_ import hooks as lambda_hooks
from localstack.services.lambda_.invocation.docker_runtime_executor import (
    LambdaContainerConfiguration,
)
from localstack.services.lambda_.invocation.lambda_models import FunctionVersion
from localstack.utils.container_utils.container_client import VolumeBind, VolumeMappings
from localstack.utils.docker_utils import get_host_path_for_path_in_docker
from localstack.utils.files import new_tmp_file, rm_rf, save_file

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)


class State:
    enabled: bool = False


# TODO: generate certs instead of hardcoding here!
CA_CERT = """
-----BEGIN CERTIFICATE-----
MIIDRTCCAi2gAwIBAgIUZGWaFAinxfWFT64N0S+oOZON8VEwDQYJKoZIhvcNAQEL
BQAwMjEWMBQGA1UEAwwNYW1hem9uYXdzLmNvbTELMAkGA1UEBhMCVVMxCzAJBgNV
BAcMAlNGMB4XDTIzMTAxODIxMDUxNloXDTI2MDcxMzIxMDUxNlowMjEWMBQGA1UE
AwwNYW1hem9uYXdzLmNvbTELMAkGA1UEBhMCVVMxCzAJBgNVBAcMAlNGMIIBIjAN
BgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvIkOfgrVu4a+NGfKAAVReaBDtcD6
lHAymZPCL0NARNoG/vp1GAxpQxx707qUD3WgLLPOhVX/k/6Eys7vGlRDlbGYts+h
VCm0R7qOc+sD3j0pXuTmlRXaBNzrU53yiFa3KYjhcvTRxSBBz4WJ5Jr5emRtrhLM
jhIGK5/s4oovVDHNmLWndhcoz0iZsKGvBK8NWOElDnxs/hgLLrU4yjArfe8DRxmm
HRbnr8caIGCUtMSxNpeOll1ysQz6bmaGDVeh8fp0uVL8vmxNVYS6ymtO9ygzGqWn
gmMbYdj2giiSEQfFBB8tGGFHjGMMxXGmiqbitsmjO6JOq7qvCQtvKhBQFwIDAQAB
o1MwUTAdBgNVHQ4EFgQU6RHYWeZyJlFvbDMHYL/fP+n/DvAwHwYDVR0jBBgwFoAU
6RHYWeZyJlFvbDMHYL/fP+n/DvAwDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0B
AQsFAAOCAQEALjEIwCGWHrSatuntTNBy6+NLiMXnzqa1f7/goLpL5JilM7EBwSZg
vDITk7CDg1GfYnp/WsD6AntW0eBAs3ODcsR/TPrWsoYfsY768UMtQaP0ybBwXmq1
zz4kMejTYqaH/LcKy5rBhTumD0k/yKqZP9I+aMDz2i+rtVOPMVci2mV40AKLvgJb
UPelsadaWOO1pGjQux0F4CNewB806QJNPoqO5htQSkpnqmjOkAirdcQID09F9ggE
+m7IW3Osd7HT5QCk+ZCDtj8UwB0SjQLU94TjDT/69bi3VBbEJXaOLGohDksGS3lP
N4v3O6c/xevkkDUW+ZEtm4N6sYWCQc0JjA==
-----END CERTIFICATE-----
"""

SERVER_CERT = """
-----BEGIN CERTIFICATE-----
MIIFRjCCBC6gAwIBAgIUZNOeezv52KJHBLK4jKu9dengkdcwDQYJKoZIhvcNAQEL
BQAwMjEWMBQGA1UEAwwNYW1hem9uYXdzLmNvbTELMAkGA1UEBhMCVVMxCzAJBgNV
BAcMAlNGMB4XDTIzMTAxODIxMDUxNloXDTI0MTAxNzIxMDUxNlowZTELMAkGA1UE
BhMCVVMxDTALBgNVBAgMBFRlc3QxDTALBgNVBAcMBFRlc3QxDTALBgNVBAoMBFRl
c3QxETAPBgNVBAsMCFRlc3QgRGV2MRYwFAYDVQQDDA1hbWF6b25hd3MuY29tMIIB
IjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0hrnnbb9cO35Wl1M+4US2WZF
zAD0D4DjQ5hRUY9DsI1D3/veNsdPGmv4ecrY9+BnYDaqnC031XlLHZX8fqFzxaiq
t5l2Lb9RnPt7jSX0hF1umpddAFKwzOYYVUCp8D8oilcI1Mq9FuXbgWmIa73Xgy5P
PbwFJk0Fg/Wogw72wHwbRvwlH1IKrmjEFHmEDRa1MvqiZ2256SR/LnrSFYtLoHWX
Eew86FF84mDO5mkujzil4aVrBapsW2gkkmL8hc2mV6jFuATjjvA+m7foJld9qDc5
rQW0336JlyeBp+DOAwgrRzLoQMWXuD55hl07/p7E/XWNE3nbNxicViVya/35AwID
AQABo4ICHzCCAhswHwYDVR0jBBgwFoAU6RHYWeZyJlFvbDMHYL/fP+n/DvAwCQYD
VR0TBAIwADALBgNVHQ8EBAMCBPAwggG/BgNVHREEggG2MIIBsoINYW1hem9uYXdz
LmNvbYIQczMuYW1hem9uYXdzLmNvbYIXYXBwY29uZmlnLmFtYXpvbmF3cy5jb22C
JGFwcGNvbmZpZy5ldS1jZW50cmFsLTEuYW1hem9uYXdzLmNvbYIhYXBwY29uZmln
LnVzLWVhc3QtMS5hbWF6b25hd3MuY29tgiFhcHBjb25maWcudXMtZWFzdC0yLmFt
YXpvbmF3cy5jb22CIWFwcGNvbmZpZy51cy13ZXN0LTEuYW1hem9uYXdzLmNvbYIh
YXBwY29uZmlnLnVzLXdlc3QtMi5hbWF6b25hd3MuY29tgihhcHBjb25maWdkYXRh
LmV1LWNlbnRyYWwtMS5hbWF6b25hd3MuY29tgiVhcHBjb25maWdkYXRhLnVzLWVh
c3QtMS5hbWF6b25hd3MuY29tgiVhcHBjb25maWdkYXRhLnVzLWVhc3QtMi5hbWF6
b25hd3MuY29tgiVhcHBjb25maWdkYXRhLnVzLXdlc3QtMS5hbWF6b25hd3MuY29t
giVhcHBjb25maWdkYXRhLnVzLXdlc3QtMi5hbWF6b25hd3MuY29tMB0GA1UdDgQW
BBT4IwJFJD4oqkky1W9YrICejRutBDANBgkqhkiG9w0BAQsFAAOCAQEApohDCVcE
5qxREwWAe+7EILEKIEtAbMIWq1MmFH4QWt+AVFjQmP4zxOxSZhS7HFPeT37Ul+da
yWVCFbSRuzbEQ4cmI6vZRlI25HuQCNd08ASxV5QfxpLhibnAV1bJdhPxiMIY2txd
x6G7yyeW2MNh1kH+TX6oNkaWcdZ3KvCtCScZQ2P4JpDc3rpR7cajQFUlWKXnsikl
qCnPADUIK/0yOrpg//2FO1y0VUBUozSJHjFbBdZUzwyFEbMa9Z61nZOF/cFpvig8
bQo/XdB/BftstVBgxvQMSM5CQpXFbg2tNFZGpKeuBFRYzZOktjdtXuEhs40dVGt3
gVtB8giXieCntQ==
-----END CERTIFICATE-----
"""

SERVER_KEY = """
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDSGuedtv1w7fla
XUz7hRLZZkXMAPQPgONDmFFRj0OwjUPf+942x08aa/h5ytj34GdgNqqcLTfVeUsd
lfx+oXPFqKq3mXYtv1Gc+3uNJfSEXW6al10AUrDM5hhVQKnwPyiKVwjUyr0W5duB
aYhrvdeDLk89vAUmTQWD9aiDDvbAfBtG/CUfUgquaMQUeYQNFrUy+qJnbbnpJH8u
etIVi0ugdZcR7DzoUXziYM7maS6POKXhpWsFqmxbaCSSYvyFzaZXqMW4BOOO8D6b
t+gmV32oNzmtBbTffomXJ4Gn4M4DCCtHMuhAxZe4PnmGXTv+nsT9dY0Teds3GJxW
JXJr/fkDAgMBAAECggEAAYFh2FHfwrfPgNqtbT42a6XGqWSI7WwU2VojUwWQMQam
qbTlkkYMvXmU23lmLErIm/pM3clRJ8+yh6fhmfmHmYqHsgnuc0Sa8mFtww3a/oKn
ucr6ay6aNWkO7iVyCR+j3ksGx5nSj5a5vp6hq3UZehBt4TSkrDsnC/bb7GELNiKz
U4bxwHF8B3QfRFVVfEy/AGb30HEdQI2BIJzCQdmEKCP0rs81n2t/R7wBYpBs5Y9E
ZSfXg78kE+0ut+ti/WJu4+pOLnzyHE4F3K0s4qFbYrPf88IGysLUoN/hs/FpqiuE
PurWRrvvSdikpsJX5kE1mWK52gN1H9fLEjFCd9yyiQKBgQDvaO6xNqCtwdQpwNGn
gxp0PzysHGh5RcveIVI/W+LjpAn070FUHwm3Y0+8BBLZvso3inx294d1q+93W8/r
g7bXZ6tKCg3NZaPuPYfH0YJimlubGKmpADf6/3amBGmcCxXr1AKolu/QiAvM9CE0
xty1gv4qP4yMCsVlKInEjbjlfwKBgQDgqhz0g/CUaQhBStbEhGhEsAAzNRi787Ku
EnBL1PZc9UWRNQdannUbWjpxM3A/o2deTMARzAvZrSYUvcyX3qfU5nWuVoLy5lL/
sJFASpNdOMj1xks8RnEuGd23DSrFyJKdc4hiUkIFxP2tIXagUgXl4FC0b14p7+7f
Lb1Gm4MWfQKBgQDXsqzLUTJ3GlkyvRynVcFx1r+tOXMPQEkres4Fc536BwNJgH5V
chlo9rsR5IGvWOwMGmOFNAMBi8UWvsuXn3YOoMJ81I4W7mpB7YH2D9bvS68ZD6Fc
OGw3Yg7eCL+17W70qHE0v7iVIt2u7I02ZazYhIrGObdBPTsXpuxpAF8DtQKBgBJ0
BpLS74TRJ7ttMTzM/1988VdDajet6aRAoXapFF9ISiGGMIdx8n5/p8M6jWK8wjXN
qg0MLIEBptoXSOHEiRaEo2/hbToUTwbvcs7MEVSb4G3HjtBxnMRDnaF2dGfwdJJ4
NeCVjxS4PHnnAL5kXlWmWhqn9x0Mtxsfv6c4CMllAoGAOhItQMBSNSbfLAKKVLvf
ppBAyvOlUUHtFlQ8kE+TH2v7WADrNUv8BFtJCVfg5GX/0bae+kMtOV8cDquoYTiD
AMBrqW0gKIK8QpHWrT0spXhZ/5F+vgW/qDAp1sLvzU9SDJIsQMgFzPwRyqMhvkq1
cbrL1olnco29L407tT6F4dM=
-----END PRIVATE KEY-----
"""


class LambdaAppConfigExtension(Extension):
    name = "lambda-appconfig"

    def on_extension_load(self):
        State.enabled = True
        patch_ssl_context()

    def update_gateway_routes(self, router):
        router.add(RequestHandler())


class RequestHandler:
    # @route("/", host="appconﬁgdata.<regex('.+'):region>.amazonaws.com<regex('(?::\d+)?'):port>")
    # def appconfig_root(self, request, region: str, port: str):
    #     print("!!appconfig_root1")
    #     return {}

    @route("/<path:path>", host="appconﬁgdata.<region>.amazonaws.com")
    def appconfig_root1(self, request, region: str):
        return {}

    # Note: seems like the regex host matching above doesn't work, so we need to
    #   match on the more specific hostname including the region
    @route("/", host="appconfigdata.us-east-1.amazonaws.com")
    def appconfig_root2(self, request):
        return {}


@lambda_hooks.start_docker_executor()
def lambda_appconfig_docker_hook(
    container_config: LambdaContainerConfiguration, function_version: FunctionVersion
) -> None:
    try:
        if not State.enabled:
            return

        LOG.debug(
            "Executing Lambda Docker executor hook for function %s",
            function_version.id.qualified_arn(),
        )
        layers = function_version.config.layers
        matching = [lyr for lyr in layers if "layer:AWS-AppConfig-Extension" in lyr.layer_arn]
        if not matching:
            return

        # set CA bundle file in container
        ca_bundle_file = "/tmp/certs/ls.aws.ca.bundle"
        container_config.env_vars["AWS_CA_BUNDLE"] = ca_bundle_file

        ca_bundle_file_local = os.path.join(DEFAULT_VOLUME_DIR + "/certs")
        save_file(ca_bundle_file_local + "/ls.aws.ca.bundle", CA_CERT)

        # determine mountable host path
        ca_bundle_from_host = get_host_path_for_path_in_docker(ca_bundle_file_local)

        # add volume mappings
        if container_config.volumes is None:
            container_config.volumes = VolumeMappings()
        container_config.volumes.add(VolumeBind(ca_bundle_from_host, "/tmp/certs"))
    except Exception as e:
        # TODO fix
        LOG.exception("Extension Lambda hook error: %s", e)


def patch_ssl_context():
    def create_ssl_context(self, *args, **kwargs):
        result: SSLContext = create_ssl_context_orig(self, *args, **kwargs)

        # load additional SSL cert file for *.amazonaws.com domains
        # note: SSL context creation taken from hypercorn.config.Config.create_ssl_context
        new_context = create_default_context(Purpose.CLIENT_AUTH)
        new_context.set_ciphers(self.ciphers)
        new_context.minimum_version = TLSVersion.TLSv1_2  # RFC 7540 Section 9.2: MUST be TLS >=1.2
        new_context.options = OP_NO_COMPRESSION  # RFC 7540 Section 9.2.1: MUST disable compression
        new_context.set_alpn_protocols(self.alpn_protocols)
        # add certfile/keyfile for the SSL cert
        certfile = new_tmp_file()
        keyfile = new_tmp_file()
        save_file(certfile, SERVER_CERT)
        save_file(keyfile, SERVER_KEY)
        new_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        rm_rf(certfile)
        rm_rf(keyfile)

        def sni_callback(sock: SSLObject, req_hostname: str, *args, **kwargs):
            if not req_hostname:
                # Should we unset AWS_CA_BUNDLE here?
                # del os.environ["AWS_CA_BUNDLE"]
                return
            if "amazonaws.com" in req_hostname:
                sock.context = new_context

        result.sni_callback = sni_callback

        return result

    # Note: deliberately not using @patch decorator here, as this function is also patched elsewhere
    create_ssl_context_orig = Config.create_ssl_context
    Config.create_ssl_context = create_ssl_context

    # set AWS_CA_BUNDLE for trusted CA in main container environment
    ca_bundle = new_tmp_file()
    save_file(ca_bundle, SERVER_CERT)
    os.environ["AWS_CA_BUNDLE"] = ca_bundle
