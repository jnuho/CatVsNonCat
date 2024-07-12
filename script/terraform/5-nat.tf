
// EIP for NAT gw
// 출발지 Private Subnet EC2 <--> NAT Gateway(EIP) ----  인터넷 ---- 목적지 타사 도메인 또는 Public IP <--> 타사 서버

# NAT (Network Address Translation) Gateway allows instances in private subnets to initiate outbound traffic to the internet or other AWS services.

# An Elastic IP address is a static IPv4 address designed for dynamic cloud computing. By using an Elastic IP address, you can 
# associate it with an instance in a VPC and have the address remain fixed even if the instance is stopped or terminated.
# This is useful for applications that require a static IP address for outbound connections.

# Two NAT gateways and Eips in case of 1 of the availability zone is down for high availability!

# Suppose you have an EKS cluster with worker nodes deployed in private subnets.
# Pods running on these worker nodes need to pull container images from Docker Hub or push logs to an external logging service.
# When a pod initiates outbound traffic, the traffic goes through the Kubernetes networking layers and then through the AWS VPC networking layers.
# The traffic destined for the internet is routed to the NAT Gateway, which performs the necessary address translation (from private IP to public IP) before forwarding it to the destination.

resource "aws_eip" "nat_eip" {
  # Indicates if this EIP is for use in VPC (vpc).
  domain = "vpc"

  # EIP may require IGW to be created first
  # Use depends_on to set an explicit dependency on the IGW.
  depends_on = [aws_internet_gateway.igw]

  tags = {
    Name = "${var.env}-nat-eip"
  }
}


// NAT gateway
resource "aws_nat_gateway" "nat_gw" {
  # allocation id of the EIP address for the gateway
  allocation_id = aws_eip.nat_eip.id

  # subnet id of the public subnet in which to place the gateway
  subnet_id = aws_subnet.public_zone1.id

  tags = {
    Name = "${var.env}-nat-gw"
  }

  depends_on = [
    aws_internet_gateway.igw,
  ]
}
