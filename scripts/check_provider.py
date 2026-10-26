from utils.AndroidSmsOtpProvider import AndroidSmsOtpProvider

provider = AndroidSmsOtpProvider.from_environment()
count = len(provider.snapshot_ids())
print("SMS provider is ready (cached SMS identities available:", count, ")")
