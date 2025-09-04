# AWS Image Annotation Application 🚀

This project was built for my **COMP5349 Cloud Computing assignment** at the **University of Sydney**.  
I designed and deployed a **highly available image annotation application** on **AWS**, built from scratch with a focus on **scalability, security, and serverless design**.

---

## 🌐 Architecture Overview

- **Frontend (Web App)**  
  - Flask app hosted on **EC2 Auto Scaling Group (ASG)**.  
  - Traffic distributed via **Application Load Balancer (ALB)** across **2 Availability Zones**.  

- **Serverless Components**  
  - **CreateAnnotation Lambda** → Generates captions via Gemini API, stores results in RDS.  
  - **CreateThumbnail Lambda** → Generates thumbnails, saves to S3.  
  - Both triggered by **S3 → EventBridge → Lambda** event-driven workflow.  

- **Database**  
  - **RDS (MySQL)** deployed in **private subnets**, credentials secured in **AWS Secrets Manager**.  

- **Storage**  
  - **S3 bucket** with prefixes:  
    - `raw/` → original uploads.  
    - `thumbnails/` → generated images.  

- **Networking & Security**  
  - Custom **VPC** with public & private subnets across 2 AZs.  
  - **NAT Gateways**, **Internet Gateway**, and **VPC Endpoints** (S3 & Secrets Manager).  
  - **Bastion host** for controlled SSH access.  
  - Security Groups configured with principle of least privilege.  

---

## 🏗 Architecture Diagrams

### Web Application Architecture
![Web Application Architecture](./diagrams/aws_A2.drawio.png)

### Serverless Workflow
![Serverless Architecture](./diagrams/aw_a2-2.drawio.png)

---

## ⚡ High Availability in Action

- **Load Tested with ApacheBench**:  
  - 40,000 requests with concurrency of 100.  
  - Auto Scaling Group scaled from **1 → 3 instances** under load.  
  - ALB distributed requests evenly, balancing CPU utilisation across instances.  

---

## 🔒 Security Highlights
- Database in **private subnets** (no public access).  
- **Secrets Manager** for DB credentials (retrieved via Interface Endpoint).  
- **IAM roles** (LabRole) to control resource access.  
- Bastion host restricted to **my IP only** for admin access.  

---

## 🎯 Results & Lessons Learned
- Designed a **highly available architecture** with automatic failover.  
- Implemented **serverless, event-driven pipelines** with S3 + EventBridge + Lambda.  
- Learned the importance of **careful Security Group and Route Table setup** (small misconfigs caused errors or security risks).  
- Avoided **infinite Lambda loops** by carefully structuring S3 prefixes.  

---

## ✅ Key AWS Services Used
- **Compute**: EC2, Auto Scaling Groups, Application Load Balancer  
- **Serverless**: Lambda, EventBridge  
- **Database**: RDS (MySQL), Secrets Manager  
- **Storage**: S3  
- **Networking**: VPC, NAT Gateway, Internet Gateway, VPC Endpoints  
- **Security**: Security Groups, IAM Roles  

---

## 📚 About This Project
This project was implemented as part of **COMP5349 – Cloud Computing** at the University of Sydney.  
It demonstrates my ability to:  
- Build AWS architectures **from scratch**.  
- Apply **best practices** in availability, serverless design, and security.  
- Benchmark, test, and validate system performance.  
