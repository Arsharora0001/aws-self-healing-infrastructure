region  = "ap-south-1"
project = "self-healing"
env     = "dev"

create_ec2    = true
instance_type = "t2.nano"

service_name = "nginx"

# Demo only (not secure). Better: your public IP/32
allowed_ssh_cidr = "0.0.0.0/0"

# Optional: if you have Key Pair name in AWS
key_name = ""

# only needed if create_ec2=false
target_instance_id = "xxxxxxxxx"
admin_email        = "xxxx@gmail.com"


