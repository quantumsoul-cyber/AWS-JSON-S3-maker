#!/usr/bin/env python3
"""
JSON Generator and S3 Uploader
Creates 3000 unique JSON files (~4GB total) and uploads them to a new S3 bucket.
"""

import os
import json
import random
import string
import time
import boto3
import base64
from cryptography.fernet import Fernet
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

class JSONS3Generator:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = None
        self.output_dir = "generated_json"
        self.total_files = 3000
        self.target_total_size_gb = 0.5  # Changed to 500MB (0.5GB)
        # Generate encryption key
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
    def setup_aws_credentials(self):
        """Setup AWS credentials and S3 client using CLI user role."""
        try:
            # Use default credentials from AWS CLI
            self.s3_client = boto3.client('s3')
            # Test credentials by listing buckets
            self.s3_client.list_buckets()
            print("✅ AWS credentials configured successfully (using CLI user role)")
            return True
        except NoCredentialsError:
            print("❌ AWS credentials not found!")
            print("Please ensure you are logged in to AWS CLI:")
            print("1. Run: aws configure")
            print("2. Or use: aws sso login (if using SSO)")
            print("3. Or ensure you have appropriate IAM role assigned")
            return False
        except ClientError as e:
            print(f"❌ AWS authentication error: {e}")
            return False
    
    def generate_bucket_name(self):
        """Generate a unique bucket name with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.bucket_name = f"cursor-json-bucket-{timestamp}"
        return self.bucket_name
    
    def create_s3_bucket(self):
        """Create a new S3 bucket."""
        try:
            print(f"🪣 Creating S3 bucket: {self.bucket_name}")
            self.s3_client.create_bucket(Bucket=self.bucket_name)
            print(f"✅ S3 bucket '{self.bucket_name}' created successfully")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyExists':
                print(f"⚠️  Bucket '{self.bucket_name}' already exists, using existing bucket")
                return True
            else:
                print(f"❌ Error creating bucket: {e}")
                return False
    
    def generate_funny_filename(self):
        """Generate a funny and unique filename."""
        adjectives = [
            "fluffy", "sparkly", "bouncy", "silly", "wobbly", "giggly", "squishy",
            "twinkly", "bubbly", "fuzzy", "wacky", "zippy", "snuggly", "dizzy",
            "jumpy", "wiggly", "sparkly", "bouncy", "silly", "wobbly", "giggly"
        ]
        
        nouns = [
            "toaster", "penguin", "banana", "robot", "unicorn", "taco", "ninja",
            "dragon", "pizza", "wizard", "kitten", "rainbow", "spaghetti", "vampire",
            "turtle", "rocket", "butterfly", "sushi", "ghost", "mermaid", "taco"
        ]
        
        # Generate random components
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        number = random.randint(1, 999)
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        return f"{adj}-{noun}-{number}-{suffix}.json"
    
    def generate_random_json_content(self, target_size_bytes):
        """Generate random JSON content with target size."""
        # Base structure
        data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "file_id": ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
                "version": "1.0"
            },
            "data": {}
        }
        
        # Calculate how much content we need to add
        current_size = len(json.dumps(data))
        remaining_bytes = target_size_bytes - current_size
        
        if remaining_bytes <= 0:
            return data
        
        # Generate random key-value pairs to reach target size
        keys_generated = 0
        while len(json.dumps(data)) < target_size_bytes and keys_generated < 1000:
            key = f"field_{keys_generated}_{''.join(random.choices(string.ascii_lowercase, k=8))}"
            
            # Randomly choose data type
            data_type = random.choice(['string', 'number', 'array', 'object', 'boolean'])
            
            if data_type == 'string':
                # Generate random string
                str_length = random.randint(10, 500)
                value = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=str_length))
            elif data_type == 'number':
                value = random.uniform(-1000000, 1000000)
            elif data_type == 'array':
                array_length = random.randint(1, 50)
                value = [random.randint(1, 1000) for _ in range(array_length)]
            elif data_type == 'object':
                obj_length = random.randint(1, 10)
                value = {f"nested_{i}": random.randint(1, 100) for i in range(obj_length)}
            else:  # boolean
                value = random.choice([True, False])
            
            data["data"][key] = value
            keys_generated += 1
        
        return data
    
    def encrypt_json_content(self, json_content):
        """Encrypt JSON content using Fernet encryption."""
        # Convert JSON to string
        json_string = json.dumps(json_content, indent=2)
        # Encrypt the JSON string
        encrypted_data = self.cipher.encrypt(json_string.encode('utf-8'))
        return encrypted_data
    
    def create_output_directory(self):
        """Create the output directory for JSON files."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Created output directory: {self.output_dir}")
    
    def generate_json_files(self):
        """Generate all JSON files locally."""
        print(f"\n📝 Generating {self.total_files} encrypted JSON files...")
        
        # Calculate target size per file (500MB / 3000 files ≈ 167KB per file)
        target_size_per_file = (self.target_total_size_gb * 1024 * 1024 * 1024) // self.total_files
        
        total_generated_size = 0
        files_created = []
        
        for i in range(self.total_files):
            # Generate filename
            filename = self.generate_funny_filename()
            filepath = os.path.join(self.output_dir, filename)
            
            # Generate content with some size variation (±20%)
            size_variation = random.uniform(0.8, 1.2)
            target_size = int(target_size_per_file * size_variation)
            
            # Generate JSON content
            json_content = self.generate_random_json_content(target_size)
            
            # Encrypt the JSON content
            encrypted_content = self.encrypt_json_content(json_content)
            
            # Write encrypted content to file
            with open(filepath, 'wb') as f:
                f.write(encrypted_content)
            
            # Get actual file size
            actual_size = os.path.getsize(filepath)
            total_generated_size += actual_size
            
            files_created.append({
                'filename': filename,
                'filepath': filepath,
                'size': actual_size
            })
            
            # Progress update every 100 files
            if (i + 1) % 100 == 0:
                progress = ((i + 1) / self.total_files) * 100
                size_mb = total_generated_size / (1024 * 1024)
                print(f"📊 Progress: {i + 1}/{self.total_files} ({progress:.1f}%) - {size_mb:.1f} MB generated")
        
        print(f"✅ Generated {len(files_created)} encrypted JSON files")
        print(f"📊 Total size: {total_generated_size / (1024 * 1024 * 1024):.2f} GB")
        print(f"🔐 Encryption key (AES-256): {base64.b64encode(self.encryption_key).decode('utf-8')}")
        
        return files_created
    
    def upload_to_s3(self, files_created):
        """Upload all generated files to S3."""
        print(f"\n☁️  Uploading encrypted files to S3 bucket: {self.bucket_name}")
        
        total_uploaded = 0
        total_upload_size = 0
        
        for i, file_info in enumerate(files_created):
            try:
                # Upload file to S3
                self.s3_client.upload_file(
                    file_info['filepath'],
                    self.bucket_name,
                    file_info['filename']
                )
                
                total_uploaded += 1
                total_upload_size += file_info['size']
                
                # Progress update every 100 files
                if (i + 1) % 100 == 0:
                    progress = ((i + 1) / len(files_created)) * 100
                    size_mb = total_upload_size / (1024 * 1024)
                    print(f"📤 Upload progress: {i + 1}/{len(files_created)} ({progress:.1f}%) - {size_mb:.1f} MB uploaded")
                
            except ClientError as e:
                print(f"❌ Error uploading {file_info['filename']}: {e}")
        
        print(f"✅ Successfully uploaded {total_uploaded}/{len(files_created)} encrypted files to S3")
        print(f"📊 Total uploaded size: {total_upload_size / (1024 * 1024 * 1024):.2f} GB")
        
        return total_uploaded
    
    def cleanup_local_files(self):
        """Clean up local JSON files after upload."""
        try:
            import shutil
            shutil.rmtree(self.output_dir)
            print(f"🧹 Cleaned up local directory: {self.output_dir}")
        except Exception as e:
            print(f"⚠️  Could not clean up local files: {e}")
    
    def run(self):
        """Main execution method."""
        print("🚀 JSON Generator and S3 Uploader (Encrypted)")
        print("=" * 50)
        
        # Setup AWS
        if not self.setup_aws_credentials():
            return False
        
        # Generate bucket name and create bucket
        self.generate_bucket_name()
        if not self.create_s3_bucket():
            return False
        
        # Create output directory
        self.create_output_directory()
        
        # Generate JSON files
        start_time = time.time()
        files_created = self.generate_json_files()
        
        # Upload to S3
        upload_start_time = time.time()
        uploaded_count = self.upload_to_s3(files_created)
        upload_end_time = time.time()
        
        # Calculate timing
        total_time = time.time() - start_time
        upload_time = upload_end_time - upload_start_time
        
        # Final summary
        print("\n" + "=" * 50)
        print("📋 FINAL SUMMARY")
        print("=" * 50)
        print(f"🪣 S3 Bucket: {self.bucket_name}")
        print(f"📁 Files generated: {len(files_created)}")
        print(f"📤 Files uploaded: {uploaded_count}")
        print(f"🔐 Encryption: Fernet (AES-256)")
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        print(f"📤 Upload time: {upload_time:.2f} seconds")
        print(f"📊 Average upload speed: {len(files_created) / upload_time:.2f} files/second")
        
        # Ask about cleanup
        cleanup = input("\n🧹 Clean up local JSON files? (y/n): ").lower().strip()
        if cleanup == 'y':
            self.cleanup_local_files()
        
        return True

def main():
    """Main function."""
    generator = JSONS3Generator()
    success = generator.run()
    
    if success:
        print("\n🎉 Process completed successfully!")
    else:
        print("\n❌ Process failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 