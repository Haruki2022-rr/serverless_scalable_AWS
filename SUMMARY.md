# AWS Image Annotation Application – Quick Summary

✅ Built AWS architecture from scratch (VPC, subnets, NAT, SGs).  
✅ Flask app deployed with Auto Scaling + ALB across 2 AZs → **high availability**.  
✅ Event-driven **serverless pipeline**: S3 → EventBridge → Lambda.  
✅ **Annotation Lambda** stores results in RDS (MySQL).  
✅ **Thumbnail Lambda** saves generated images to S3.  
✅ Secured DB with **Secrets Manager + private subnets**.  
✅ Benchmarked scaling: **1 → 3 EC2 instances** under 40k requests.  

**Tech Stack**: AWS (EC2, ALB, ASG, Lambda, RDS, S3, EventBridge, Secrets Manager, VPC), Flask, Python.  
