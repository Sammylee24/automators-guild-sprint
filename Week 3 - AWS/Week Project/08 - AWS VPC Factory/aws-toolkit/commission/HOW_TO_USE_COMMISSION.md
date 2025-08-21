### **Directory Structure**

```
aws-toolkit/commission/
├── create_vpc.py
├── create_subnet.py
├── create_igw.py
├── create_route_table.py
├── create_nat_gateway.py
├── create_security_group.py
├── create_ec2_instance.py
└── HOW_TO_USE_COMMISSION.md

---

### `HOW_TO_USE_COMMISSION.md`

# AWS Two-Tier Network Toolkit - Usage Guide

This guide will walk you through the process of deploying a complete, secure, two-tier web architecture in AWS using this suite of individual Python command-line tools.

## 1. Prerequisites (Do This First!)

Before running any scripts, you need to set up your local environment to securely communicate with AWS.

1.  **Install AWS CLI:** If you haven't already, [install the AWS Command Line Interface](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
2.  **Create an IAM User:** Log in to your AWS account and create a new IAM User with `AdministratorAccess` permissions. **Do not use your root account.**
3.  **Generate Access Keys:** For your new IAM user, create a new Access Key and Secret Access Key. **Save these credentials in a secure place.**
4.  **Configure AWS CLI:** Open your terminal or command prompt and run the following command. Enter the credentials you just saved.
    ```bash
    aws configure
    ```
    *   **AWS Access Key ID:** `YOUR_ACCESS_KEY`
    *   **AWS Secret Access Key:** `YOUR_SECRET_KEY`
    *   **Default region name:** `eu-west-1` (or your preferred region)
    *   **Default output format:** `json`

5.  **Install Python Libraries:** Make sure you have a Python virtual environment set up and activated, then run:
    ```bash
    pip install boto3
    ```

You are now ready to build!

## 2. The Deployment Workflow (The Correct Sequence)

The following commands must be run in order. Each script will print out an **ID** for the resource it creates. You will need to **copy that ID** and use it as an input for the next command.

---
### **Step 1: Create the SSH Key Pair**
This key will be used to access your servers. It will be saved as `boto3-lab-key.pem` in your current directory.

```bash
python create_key_pair.py --key-name boto3-lab-key
```

---
### **Step 2: Create the VPC (The Foundation)**
This creates the main virtual network container.

```bash
python create_vpc.py --cidr 10.0.0.0/16 --name Boto3-VPC
```
➡️ **Copy the `VPC ID` from the output.** Let's assume it's `vpc-12345`.

---
### **Step 3: Create the Subnets**
Now, we create the public and private network segments inside our VPC.

*   **Public Subnet:**
    ```bash
    python create_subnet.py --vpc-id vpc-12345 --cidr 10.0.1.0/24 --name Boto3-Public-Subnet
    ```
    ➡️ **Copy the `Public Subnet ID` from the output.** Let's assume it's `subnet-pub-abc`.

*   **Private Subnet:**
    ```bash
    python create_subnet.py --vpc-id vpc-12345 --cidr 10.0.2.0/24 --name Boto3-Private-Subnet
    ```
    ➡️ **Copy the `Private Subnet ID` from the output.** Let's assume it's `subnet-priv-xyz`.

---
### **Step 4: Create the Internet Gateway**
This provides internet access for the public subnet.

```bash
python create_igw.py --vpc-id vpc-12345 --name Boto3-IGW
```
➡️ **Copy the `Internet Gateway ID` from the output.** Let's assume it's `igw-67890`.

---
### **Step 5: Create the NAT Gateway**
This provides secure, outbound-only internet access for the private subnet.

```bash
python create_nat_gateway.py --subnet-id subnet-pub-abc --name Boto3-NAT-GW
```
➡️ **Copy the `NAT Gateway ID` from the output.** Let's assume it's `nat-abcde`.

---
### **Step 6: Create and Configure the Route Tables**
This step defines the traffic flow for our subnets.

*   **Public Route Table:** (Routes internet traffic to the Internet Gateway)
    ```bash
    python create_route_table.py --vpc-id vpc-12345 --name Boto3-Public-RT --subnet-id subnet-pub-abc --gateway-id igw-67890
    ```

*   **Private Route Table:** (Routes internet traffic to the NAT Gateway)
    ```bash
    python create_route_table.py --vpc-id vpc-12345 --name Boto3-Private-RT --subnet-id subnet-priv-xyz --nat-gateway-id nat-abcde
    ```

---
### **Step 7: Create the Security Groups (Firewalls)**
These control what traffic is allowed to reach our servers.

*   **Web Server Security Group:**
    ```bash
    python create_security_group.py --vpc-id vpc-12345 --name Boto3-Web-SG --desc "Web Server SG" --allow-http --allow-ssh
    ```
    ➡️ **Copy the `Web Server SG ID` from the output.** Let's assume it's `sg-web123`.

*   **Database Security Group:**
    ```bash
    python create_security_group.py --vpc-id vpc-12345 --name Boto3-DB-SG --desc "Database SG" --allow-mysql-from sg-web123
    ```
    ➡️ **Copy the `Database SG ID` from the output.** Let's assume it's `sg-db456`.

---
### **Step 8: Launch the EC2 Instances (The Servers)**
Finally, we launch our servers into the network we've built.

*   **Web Server (Public):**
    ```bash
    python create_ec2_instance.py --name Boto3-Web-Server --subnet-id subnet-pub-abc --key-name boto3-lab-key --sg-id sg-web123 --public
    ```
    *This will print the final SSH command you can use to connect to your web server.*

*   **Database Server (Private):**
    ```bash
    python create_ec2_instance.py --name Boto3-Database-Server --subnet-id subnet-priv-xyz --key-name boto3-lab-key --sg-id sg-db456
    ```

---

Congratulations! You have successfully deployed a full two-tier architecture using the command-line toolkit.

## 3. How to Decommission the Environment

To avoid unnecessary AWS charges, run the single `decommission.py` script. It is designed to automatically find all the resources you created with the name "Boto3-VPC" and delete them in the correct order.

```bash
python decommission.py
```
