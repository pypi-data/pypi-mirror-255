from enum import Enum

from runhouse.rns.secrets_old.aws_secrets import AWSSecrets
from runhouse.rns.secrets_old.azure_secrets import AzureSecrets
from runhouse.rns.secrets_old.gcp_secrets import GCPSecrets
from runhouse.rns.secrets_old.github_secrets import GitHubSecrets
from runhouse.rns.secrets_old.huggingface_secrets import HuggingFaceSecrets
from runhouse.rns.secrets_old.lambda_secrets import LambdaSecrets
from runhouse.rns.secrets_old.sky_secrets import SkySecrets
from runhouse.rns.secrets_old.ssh_secrets import SSHSecrets


class Providers(Enum):
    AWS = AWSSecrets()
    AZURE = AzureSecrets()
    GCP = GCPSecrets()
    HUGGINGFACE = HuggingFaceSecrets()
    LAMBDA = LambdaSecrets()
    SKY = SkySecrets()
    SSH = SSHSecrets()
    GITHUB = GitHubSecrets()
