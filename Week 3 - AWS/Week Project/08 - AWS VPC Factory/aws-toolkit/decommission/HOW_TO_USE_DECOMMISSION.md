### **Directory Structure**

```
aws-toolkit/decommission/
├── find_vpc_by_name.py
├── terminate_instances.py
├── delete_nat_gateways.py
├── release_eips.py
├── delete_igw.py
├── delete_subnets.py
├── delete_route_tables.py
├── delete_security_groups.py
├── delete_vpc.py
├── delete_key_pair.py
└── HOW_TO_USE_DECOMMISSION.md
```

---

### **`HOW_TO_USE_DECOMMISSION.md`**

# AWS Toolkit - Decommissioning Guide

This guide explains how to use the individual Python scripts to safely and completely tear down the AWS environment created by the `aws-toolkit`. These scripts should be run from within the `aws-toolkit/decommission/` directory.

## The Correct Destruction Order

To avoid dependency errors, you **must** run these scripts in the following sequence.

---
### **Step 1: Find Your VPC ID**
First, find the ID of the VPC you want to destroy using its "Name" tag.

```bash
python find_vpc_by_name.py --name Boto3-VPC
```
➡️ **Copy the `VPC ID` from the output.** You will need it for almost every other command. Let's assume it's `vpc-12345`.

---
### **Step 2: Terminate All EC2 Instances**
This is the most critical first step, as many resources depend on running instances.

```bash
python terminate_instances.py --vpc-id vpc-12345
```

---
### **Step 3: Delete NAT Gateways**
These must be deleted before their Elastic IPs can be released. This step may take a minute or two.

```bash
python delete_nat_gateways.py --vpc-id vpc-12345
```

---
### **Step 4: Release Elastic IPs**
Now that the NAT Gateways are gone, we can release the public IPs they were using.

```bash
python release_eips.py
```

---
### **Step 5: Delete the Internet Gateway**
With no public-facing resources left, we can now detach and delete the "front door" to the VPC.

```bash
python delete_igw.py --vpc-id vpc-12345
```

---
### **Step 6: Delete Network Infrastructure**
Now we can clean up the internal networking components.

*   **Subnets:**
    ```bash
    python delete_subnets.py --vpc-id vpc-12345
    ```
*   **Custom Route Tables:**
    ```bash
    python delete_route_tables.py --vpc-id vpc-12345
    ```
*   **Custom Security Groups:**
    ```bash
    python delete_security_groups.py --vpc-id vpc-12345
    ```

---
### **Step 7: Delete the VPC**
With all its internal components removed, the VPC container can now be deleted.

```bash
python delete_vpc.py --vpc-id vpc-12345
```

---
### **Step 8: Delete the EC2 Key Pair (Updated)**
Finally, clean up the SSH key from your AWS account and your local machine. This script needs to know where your `.pem` file is stored.

**Important:** The command below assumes your directory structure is:
```
parent_directory/
├── aws-toolkit/
│   ├── commission/
│   │   └── boto3-lab-key.pem  <-- The key file
│   │   └── ... (other creator scripts)
│   ├── decommission/
│   │   └── delete_key_pair.py     <-- The script you are running
```

Run the following command from inside the `decommission/` directory:

```bash
python delete_key_pair.py --key-name boto3-lab-key --key-path ../aws-toolkit/commission
```
*   The `--key-path` argument tells the script to look one directory up (`..`) and then down into `aws-toolkit/commission/` to find the `.pem` file.

---

The environment is now fully decommissioned.
