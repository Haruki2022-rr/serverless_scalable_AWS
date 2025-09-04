# AWS Image Annotation Application – Configuration Details

This document provides **technical details** of how the project was deployed on AWS.  
It complements the [README.md](./README.md), which provides a high-level overview.

---

## 🌐 VPC & Networking

**VPC**
- CIDR: `10.0.0.0/16`
- DNS resolution & hostnames: Enabled (for interface endpoints)

**Subnets**
- **Public Subnets** (for ALB, NAT, Bastion)  
  - `10.0.1.0/24` (ap-southeast-2a)  
  - `10.0.2.0/24` (ap-southeast-2b)  
- **Private Web Subnets** (for EC2 in Auto Scaling Group)  
  - `10.0.11.0/24` (ap-southeast-2a)  
  - `10.0.12.0/24` (ap-southeast-2b)  
- **Private DB Subnets** (for RDS)  
  - `10.0.21.0/24` (ap-southeast-2a)  
  - `10.0.22.0/24` (ap-southeast-2b)  

**Routing**
- Internet Gateway (A2-IGW) attached to VPC.  
- **Public Route Table** → `0.0.0.0/0` → IGW.  
- **Private Route Tables** → `0.0.0.0/0` → NAT Gateway (per AZ).  

**NAT Gateways**
- NAT-A in `Public-A` subnet.  
- NAT-B in `Public-B` subnet.  

**VPC Endpoints**
- **S3 Gateway Endpoint** → allows private subnet access to S3.  
- **Secrets Manager Interface Endpoint** → allows private subnet access to DB secrets without internet traffic.  

---

## 🔒 Security Groups

1. **db-SG**
   - Inbound: MySQL (3306) from `web-app-SG`, `bastion-SG`, `lambda-annotation-SG`.

2. **lambda-annotation-SG**
   - Outbound: All (to reach RDS, Secrets Manager, and Gemini API).  

3. **web-app-SG**
   - Inbound:  
     - HTTP (80) from `alb-SG`.  
     - SSH (22) from `bastion-SG`.  

4. **alb-SG**
   - Inbound: HTTP (80) from `0.0.0.0/0`.  
   - Outbound: All (default).  

5. **bastion-SG**
   - Inbound: SSH (22) from **my IP only**.  

6. **secrets-endpoint-SG**
   - Inbound: HTTPS (443) from `lambda-annotation-SG` and `web-app-SG`.  

---

## 🖥 Compute Environment

**EC2 Web App (Flask)**
- Custom AMI created with:
  - Flask app  
  - MySQL client & dependencies (`mysql-connector-python`, `boto3`, `werkzeug`, `gunicorn`)  
- Instances launched via **Auto Scaling Group**.  

**Bastion Host**
- Deployed in public subnet.  
- Used for SSH into private EC2 and RDS access.  

---

## ⚡ Auto Scaling Group (ASG)

**Launch Template**
- Instance type: `t2.micro`  
- AMI: Custom Flask app image  
- Security group: `web-app-SG`  
- IAM instance profile: `LabRole`  
- User data: Starts Flask app with Gunicorn  

**Scaling Settings**
- Min capacity: 1  
- Desired capacity: 1  
- Max capacity: 3  
- Scaling policy: Target average CPU = 50%  

**Load Balancer (ALB)**
- Type: Application Load Balancer  
- Subnets: Spans both public subnets  
- Security Group: `alb-SG`  
- Listener: HTTP 80 → Target Group (EC2 instances)  
- Health check: `/` path, interval 10s, threshold 2  

---

## 🗄 Database

**RDS MySQL**
- Instance type: `db.t3.micro`  
- Storage: 20 GiB GP3 SSD  
- Multi-AZ enabled with subnet group (db-private-subnet1 & 2).  
- Public access: Disabled.  
- Credentials: Stored in **Secrets Manager**.  

**Secret Manager**
- RDS credentials stored as a secret.  
- Access restricted to `lambda-annotation-SG` and `web-app-SG`.  

---

## 📦 Storage

**S3 Bucket**
- Name: `a2-<studentid>-images`  
- Folders (prefixes):  
  - `raw/` → uploaded images.  
  - `thumbnails/` → generated thumbnails.  
- EventBridge notifications enabled for object-level events.  

---

## 🛠 Serverless Components

**CreateAnnotation Lambda**
- Language: Python 3.12  
- Runs in **private subnet** with NAT access.  
- Permissions: S3, RDS (via Secret Manager).  
- Dependencies packaged as Lambda Layer (`mysql-connector-python`, `google-generativeai`).  
- Workflow:  
  - Reads from S3 → calls Gemini API → stores caption in RDS.  

**CreateThumbnail Lambda**
- Language: Python 3.12  
- Runs **outside VPC** (only needs S3).  
- Workflow:  
  - Reads from S3 → generates thumbnail → writes to `thumbnails/`.  

**EventBridge**
- Rule: Trigger both Lambdas when object created in `raw/` prefix.  

---

## 🧪 Testing & Benchmarking

**Load Testing**
- Tool: ApacheBench (macOS).  
- Command: `ab -n 40000 -c 100 http://a2-ALB.../gallery`  
- Result:  
  - ASG scaled from 1 → 3 instances.  
  - ALB evenly distributed requests.  
  - CPU utilisation balanced across instances.  

**Database Testing**
- SSH into Bastion → connect to RDS via MySQL client.  
- Verified inserts from `CreateAnnotationLambda`.  

---

## 🔑 IAM Roles

- **LabRole (LabInstanceProfile)** assigned to:  
  - EC2 instances  
  - Lambdas  
  - Bastion  
- Permissions:  
  - Access to S3  
  - Access to Secrets Manager  

---

## 📌 Key Config Notes
- Placed `CreateAnnotationLambda` **inside VPC** to access RDS securely.  
- Placed `CreateThumbnailLambda` **outside VPC** (faster, no DB access).  
- Used **VPC Endpoints** for S3 & Secrets Manager → secure, no internet traffic.  
- Security Groups follow **least-privilege principle**.  
- Used **prefix-based S3 events** to prevent infinite Lambda invocation loops.  
